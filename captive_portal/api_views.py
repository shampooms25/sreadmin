"""
API Views para integração com Appliances POPPFIRE
Permite que os Appliances POPPFIRE verifiquem e baixem atualizações do portal captive
"""

from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.contrib.auth.models import User
from painel.models import EldGerenciarPortal, EldPortalSemVideo
import os
import json
import hashlib
from datetime import datetime
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Modelo simples para tokens de API (você pode usar o Token do DRF se estiver instalado)
try:
    from rest_framework.authtoken.models import Token
    HAS_DRF = True
except ImportError:
    HAS_DRF = False
    # Implementação simples sem DRF
    class SimpleToken:
        @staticmethod
        def get_or_create_for_user(username):
            """
            Cria um token simples baseado no username
            Para produção, use uma implementação mais segura
            """
            import hashlib
            token = hashlib.sha256(f"poppfire-{username}-api-token".encode()).hexdigest()[:32]
            return token

class ApplianceAPIAuthentication:
    """
    Autenticação customizada para Appliances POPPFIRE
    """
    @staticmethod
    def verify_token(request):
        """
        Verifica se o token fornecido é válido
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return False, "Token não fornecido ou formato inválido"
        
        token = auth_header.replace('Bearer ', '')
        
        # Primeiro tentar buscar no modelo Django
        try:
            from .models import ApplianceToken
            token_obj = ApplianceToken.objects.get(token=token, is_active=True)
            
            # Atualizar último uso
            client_ip = request.META.get('REMOTE_ADDR')
            token_obj.mark_as_used(ip_address=client_ip)
            
            # Criar usuário fictício para o appliance
            class ApplianceUser:
                def __init__(self, appliance_id, appliance_name):
                    self.username = appliance_id
                    self.appliance_name = appliance_name
                    self.is_authenticated = True
            
            return True, ApplianceUser(token_obj.appliance_id, token_obj.appliance_name)
            
        except Exception as e:
            logger.warning(f"Erro ao verificar token no banco de dados: {e}")
        
        # Fallback: carregar tokens do arquivo JSON
        try:
            tokens_file = os.path.join(settings.BASE_DIR, 'appliance_tokens.json')
            with open(tokens_file, 'r', encoding='utf-8') as f:
                tokens_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Erro ao carregar tokens: {e}")
            return False, "Erro interno de autenticação"
        
        # Verificar se o token existe no JSON
        if token not in tokens_data.get('tokens', {}):
            return False, "Token inválido"
        
        token_info = tokens_data['tokens'][token]
        
        # Atualizar último uso do token no JSON
        try:
            token_info['last_used'] = datetime.now().isoformat()
            with open(tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Erro ao atualizar último uso do token: {e}")
        
        # Criar usuário fictício para o appliance
        class ApplianceUser:
            def __init__(self, appliance_id, appliance_name):
                self.username = appliance_id
                self.appliance_name = appliance_name
                self.is_authenticated = True
        
        return True, ApplianceUser(token_info['appliance_id'], token_info['appliance_name'])

def appliance_auth_required(view_func):
    """
    Decorator para verificar autenticação de appliances
    """
    def wrapper(request, *args, **kwargs):
        is_valid, result = ApplianceAPIAuthentication.verify_token(request)
        if not is_valid:
            return JsonResponse({
                'error': 'Não autorizado',
                'message': result,
                'timestamp': datetime.now().isoformat()
            }, status=401)
        
        request.appliance_user = result
        return view_func(request, *args, **kwargs)
    
    return wrapper


@csrf_exempt
@require_http_methods(["GET"])
@appliance_auth_required
def portal_status(request):
    """
    Endpoint para verificar o status do portal ativo
    
    URL: GET /api/appliances/portal/status/
    Headers: Authorization: Bearer <token>
    
    Response:
    {
        "status": "active",
        "portal_type": "with_video" | "without_video",
        "portal_hash": "abc123...",
        "last_updated": "2025-08-06T10:30:00Z",
        "download_url": "/api/appliances/portal/download/",
        "video_url": "/media/videos/video.mp4" (se aplicável)
    }
    """
    try:
        # Buscar configuração ativa do portal
        portal_config = EldGerenciarPortal.get_configuracao_ativa()
        
        if not portal_config or not portal_config.ativo:
            # Não há portal ativo, retornar portal sem vídeo padrão
            portal_sem_video = EldPortalSemVideo.objects.filter(ativo=True).first()
            
            if not portal_sem_video:
                return JsonResponse({
                    'error': 'Nenhum portal disponível',
                    'message': 'Não há portal com vídeo ativo nem portal sem vídeo disponível',
                    'timestamp': datetime.now().isoformat()
                }, status=404)
            
            # Calcular hash do arquivo
            file_hash = _calculate_file_hash(portal_sem_video.arquivo_zip.path)
            
            return JsonResponse({
                'status': 'active',
                'portal_type': 'without_video',
                'portal_hash': file_hash,
                'portal_name': portal_sem_video.nome,
                'portal_version': portal_sem_video.versao,
                'last_updated': portal_sem_video.data_atualizacao.isoformat(),
                'download_url': f'/api/appliances/portal/download/?type=without_video',
                'file_size_mb': portal_sem_video.tamanho_mb,
                'timestamp': datetime.now().isoformat()
            })
        
        # Portal com vídeo está ativo
        if portal_config.captive_portal_zip:
            file_hash = _calculate_file_hash(portal_config.captive_portal_zip.path)
            
            response_data = {
                'status': 'active',
                'portal_type': 'with_video',
                'portal_hash': file_hash,
                'last_updated': portal_config.data_atualizacao.isoformat(),
                'download_url': f'/api/appliances/portal/download/?type=with_video',
                'timestamp': datetime.now().isoformat()
            }
            
            # Adicionar informações do vídeo se disponível
            if portal_config.nome_video:
                response_data.update({
                    'video_name': os.path.basename(portal_config.nome_video.video.name),
                    'video_url': request.build_absolute_uri(portal_config.nome_video.video.url),
                    'video_size_mb': portal_config.nome_video.tamanho,
                    'using_custom_video': True
                })
            else:
                response_data['using_custom_video'] = False
                response_data['video_info'] = 'Usando vídeo padrão incluído no ZIP'
            
            return JsonResponse(response_data)
        
        else:
            return JsonResponse({
                'error': 'Portal mal configurado',
                'message': 'Portal ativo sem arquivo ZIP',
                'timestamp': datetime.now().isoformat()
            }, status=500)
            
    except Exception as e:
        logger.error(f"Erro em portal_status: {str(e)}")
        return JsonResponse({
            'error': 'Erro interno do servidor',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@appliance_auth_required
def portal_download(request):
    """
    Endpoint para download do arquivo ZIP do portal
    
    URL: GET /api/appliances/portal/download/?type=with_video|without_video
    Headers: Authorization: Bearer <token>
    
    Response: Arquivo ZIP binário
    """
    try:
        portal_type = request.GET.get('type', 'auto')
        
        if portal_type == 'auto':
            # Determinar automaticamente o tipo
            portal_config = EldGerenciarPortal.get_configuracao_ativa()
            if portal_config and portal_config.ativo:
                portal_type = 'with_video'
            else:
                portal_type = 'without_video'
        
        if portal_type == 'with_video':
            # Download do portal com vídeo
            portal_config = EldGerenciarPortal.get_configuracao_ativa()
            
            if not portal_config or not portal_config.ativo or not portal_config.captive_portal_zip:
                return JsonResponse({
                    'error': 'Portal com vídeo não disponível',
                    'message': 'Não há portal com vídeo ativo ou arquivo ZIP não encontrado',
                    'timestamp': datetime.now().isoformat()
                }, status=404)
            
            file_path = portal_config.captive_portal_zip.path
            filename = portal_config.get_portal_zip_name()  # sempre "src.zip"
            
        elif portal_type == 'without_video':
            # Download do portal sem vídeo
            portal_sem_video = EldPortalSemVideo.objects.filter(ativo=True).first()
            
            if not portal_sem_video or not portal_sem_video.arquivo_zip:
                return JsonResponse({
                    'error': 'Portal sem vídeo não disponível',
                    'message': 'Não há portal sem vídeo ativo ou arquivo ZIP não encontrado',
                    'timestamp': datetime.now().isoformat()
                }, status=404)
            
            file_path = portal_sem_video.arquivo_zip.path
            filename = "scripts_poppnet_sre.zip"
            
        else:
            return JsonResponse({
                'error': 'Tipo de portal inválido',
                'message': 'Tipo deve ser "with_video", "without_video" ou "auto"',
                'timestamp': datetime.now().isoformat()
            }, status=400)
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            return JsonResponse({
                'error': 'Arquivo não encontrado',
                'message': f'Arquivo ZIP não existe no servidor: {file_path}',
                'timestamp': datetime.now().isoformat()
            }, status=404)
        
        # Log do download
        logger.info(f"Appliance {request.appliance_user.username} baixando {portal_type}: {filename}")
        
        # Preparar resposta com arquivo
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = os.path.getsize(file_path)
            response['X-Portal-Type'] = portal_type
            response['X-Portal-Hash'] = _calculate_file_hash(file_path)
            response['X-Download-Timestamp'] = datetime.now().isoformat()
            
            return response
            
    except Exception as e:
        logger.error(f"Erro em portal_download: {str(e)}")
        return JsonResponse({
            'error': 'Erro interno do servidor',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@appliance_auth_required
def portal_update_status(request):
    """
    Endpoint para appliances reportarem status de atualização
    
    URL: POST /api/appliances/portal/update-status/
    Headers: Authorization: Bearer <token>
    Content-Type: application/json
    
    Body:
    {
        "appliance_id": "appliance-001",
        "appliance_ip": "192.168.1.1",
        "update_status": "success" | "failed",
        "portal_hash": "abc123...",
        "portal_type": "with_video" | "without_video",
        "error_message": "..." (se failed),
        "update_timestamp": "2025-08-06T10:30:00Z"
    }
    """
    try:
        # Parse do JSON
        data = json.loads(request.body.decode('utf-8'))
        
        required_fields = ['appliance_id', 'update_status', 'portal_hash', 'portal_type']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'error': 'Campo obrigatório ausente',
                    'message': f'Campo "{field}" é obrigatório',
                    'timestamp': datetime.now().isoformat()
                }, status=400)
        
        # Log do status de atualização
        logger.info(f"Status de atualização do appliance {data['appliance_id']}: {data['update_status']}")
        
        # Aqui você pode implementar lógica para salvar o status em banco de dados se necessário
        # Por exemplo, criar um modelo AplianceUpdateLog para rastrear atualizações
        
        return JsonResponse({
            'status': 'success',
            'message': 'Status de atualização recebido com sucesso',
            'received_data': {
                'appliance_id': data['appliance_id'],
                'status': data['update_status'],
                'portal_type': data['portal_type']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON inválido',
            'message': 'Corpo da requisição deve ser um JSON válido',
            'timestamp': datetime.now().isoformat()
        }, status=400)
    except Exception as e:
        logger.error(f"Erro em portal_update_status: {str(e)}")
        return JsonResponse({
            'error': 'Erro interno do servidor',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@appliance_auth_required
def api_info(request):
    """
    Endpoint de informações da API
    
    URL: GET /api/appliances/info/
    Headers: Authorization: Bearer <token>
    """
    return JsonResponse({
        'api_name': 'POPPFIRE Appliance API',
        'version': '1.0',
        'description': 'API para integração com Appliances POPPFIRE',
        'endpoints': {
            'portal_status': '/api/appliances/portal/status/',
            'portal_download': '/api/appliances/portal/download/',
            'update_status': '/api/appliances/portal/update-status/',
            'api_info': '/api/appliances/info/'
        },
        'authentication': 'Bearer Token',
        'server_time': datetime.now().isoformat(),
        'server_ip': '172.18.25.253'
    })


def _calculate_file_hash(file_path):
    """
    Calcula hash SHA256 de um arquivo
    """
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logger.error(f"Erro ao calcular hash do arquivo {file_path}: {str(e)}")
        return "error"

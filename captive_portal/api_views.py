"""
Views API para integração com OpenSense
Permite que o OpenSense verifique e baixe atualizações do portal captive
"""
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from painel.models import EldGerenciarPortal, EldUploadVideo
from django.conf import settings
import os
import hashlib
import json
from datetime import datetime


class CaptivePortalAPIView(View):
    """
    API para verificar configuração ativa do portal captive
    """
    
    def get(self, request):
        """
        Retorna a configuração ativa do portal captive
        """
        try:
            config = EldGerenciarPortal.get_configuracao_ativa()
            
            if not config:
                return JsonResponse({
                    'status': 'no_config',
                    'message': 'Nenhuma configuração ativa encontrada',
                    'data': None
                })
            
            # Dados básicos da configuração
            response_data = {
                'status': 'success',
                'config_id': config.id,
                'ativo': config.ativo,
                'ativar_video': config.ativar_video,
                'data_atualizacao': config.data_atualizacao.isoformat(),
                'video': None,
                'portal_zip': None
            }
            
            # Informações do vídeo se ativo
            if config.ativar_video and config.nome_video:
                video = config.nome_video
                video_path = video.video.path if video.video else None
                video_hash = None
                video_size = None
                
                if video_path and os.path.exists(video_path):
                    # Calcular hash do arquivo para verificar mudanças
                    video_hash = self.calculate_file_hash(video_path)
                    video_size = os.path.getsize(video_path)
                
                response_data['video'] = {
                    'id': video.id,
                    'name': video.video.name if video.video else None,
                    'url': f"/api/captive-portal/download/video/{video.id}/",
                    'size': video_size,
                    'hash': video_hash,
                    'upload_date': video.data.isoformat() if video.data else None
                }
            
            # Informações do ZIP se disponível
            if config.captive_portal_zip:
                zip_path = config.captive_portal_zip.path
                zip_hash = None
                zip_size = None
                
                if os.path.exists(zip_path):
                    zip_hash = self.calculate_file_hash(zip_path)
                    zip_size = os.path.getsize(zip_path)
                
                response_data['portal_zip'] = {
                    'name': config.captive_portal_zip.name,
                    'url': f"/api/captive-portal/download/zip/{config.id}/",
                    'size': zip_size,
                    'hash': zip_hash
                }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erro interno: {str(e)}',
                'data': None
            }, status=500)
    
    def calculate_file_hash(self, file_path):
        """
        Calcula hash SHA256 do arquivo para verificar integridade
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


class VideoDownloadAPIView(View):
    """
    API para download de vídeos
    """
    
    def get(self, request, video_id):
        """
        Download do arquivo de vídeo
        """
        try:
            video = EldUploadVideo.objects.get(id=video_id)
            
            if not video.video or not os.path.exists(video.video.path):
                raise Http404("Arquivo de vídeo não encontrado")
            
            response = FileResponse(
                open(video.video.path, 'rb'),
                content_type='application/octet-stream'
            )
            
            # Nome do arquivo para download
            filename = os.path.basename(video.video.name)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = os.path.getsize(video.video.path)
            
            return response
            
        except EldUploadVideo.DoesNotExist:
            raise Http404("Vídeo não encontrado")
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao baixar vídeo: {str(e)}'
            }, status=500)


class PortalZipDownloadAPIView(View):
    """
    API para download do ZIP do portal
    """
    
    def get(self, request, config_id):
        """
        Download do arquivo ZIP do portal
        """
        try:
            config = EldGerenciarPortal.objects.get(id=config_id)
            
            if not config.captive_portal_zip or not os.path.exists(config.captive_portal_zip.path):
                raise Http404("Arquivo ZIP do portal não encontrado")
            
            response = FileResponse(
                open(config.captive_portal_zip.path, 'rb'),
                content_type='application/zip'
            )
            
            # Nome do arquivo para download
            filename = os.path.basename(config.captive_portal_zip.name)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = os.path.getsize(config.captive_portal_zip.path)
            
            return response
            
        except EldGerenciarPortal.DoesNotExist:
            raise Http404("Configuração não encontrada")
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao baixar ZIP: {str(e)}'
            }, status=500)


class StatusAPIView(View):
    """
    API para verificar status do servidor
    """
    
    def get(self, request):
        """
        Retorna status do servidor e estatísticas
        """
        try:
            # Estatísticas básicas
            total_configs = EldGerenciarPortal.objects.count()
            active_configs = EldGerenciarPortal.objects.filter(ativo=True).count()
            total_videos = EldUploadVideo.objects.count()
            
            return JsonResponse({
                'status': 'online',
                'server_time': datetime.now().isoformat(),
                'django_version': '5.2.3',
                'statistics': {
                    'total_configurations': total_configs,
                    'active_configurations': active_configs,
                    'total_videos': total_videos
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao obter status: {str(e)}'
            }, status=500)

"""
Views administrativas para gerenciamento de ZIP e notificações
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import site
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import redirect
from .models import EldGerenciarPortal, EldUploadVideo
from .services import NotificationService, ZipManagerService
import json
import logging

logger = logging.getLogger(__name__)

def get_admin_context(request):
    """Função auxiliar para obter contexto do admin"""
    context = {
        'available_apps': site.get_app_list(request),
        'has_permission': request.user.is_active and request.user.is_staff,
        'site_header': site.site_header,
        'site_title': site.site_title,
        'index_title': site.index_title,
        'site_url': site.site_url,
    }
    return context

@staff_member_required
def zip_manager_view(request):
    """View principal do gerenciador de ZIP"""
    # Buscar todas as configurações do portal
    configs = EldGerenciarPortal.objects.all().order_by('-data_criacao')
    
    # Adicionar informações do ZIP para cada configuração
    for config in configs:
        if config.captive_portal_zip:
            try:
                zip_info = ZipManagerService.get_zip_info(config.captive_portal_zip.path)
                config.zip_info = zip_info
            except Exception as e:
                logger.error(f"Erro ao obter info do ZIP: {str(e)}")
                config.zip_info = None
        else:
            config.zip_info = None
    
    # Obter contexto do admin
    context = get_admin_context(request)
    context.update({
        'title': 'Gerenciador de ZIP - Portal Captive',
        'configs': configs,
    })
    
    return render(request, 'admin/painel/zip_manager.html', context)

@staff_member_required
def zip_info_ajax(request, config_id):
    """Retorna informações do ZIP via AJAX"""
    try:
        config = get_object_or_404(EldGerenciarPortal, id=config_id)
        
        if not config.captive_portal_zip:
            return JsonResponse({
                'success': False,
                'error': 'Nenhum arquivo ZIP configurado'
            })
        
        zip_info = ZipManagerService.get_zip_info(config.captive_portal_zip.path)
        
        if zip_info:
            return JsonResponse({
                'success': True,
                'data': zip_info
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Erro ao obter informações do ZIP'
            })
            
    except Exception as e:
        logger.error(f"Erro em zip_info_ajax: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@staff_member_required
@csrf_exempt
def update_zip_with_video_ajax(request):
    """Atualiza ZIP com vídeo via AJAX"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método não permitido'
        })
    
    try:
        data = json.loads(request.body)
        config_id = data.get('config_id')
        video_id = data.get('video_id')
        
        config = get_object_or_404(EldGerenciarPortal, id=config_id)
        video = get_object_or_404(EldUploadVideo, id=video_id)
        
        if not config.captive_portal_zip:
            return JsonResponse({
                'success': False,
                'error': 'Nenhum arquivo ZIP configurado'
            })
        
        success = ZipManagerService.update_zip_with_video(
            config.captive_portal_zip.path,
            video.video
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'ZIP atualizado com sucesso com o vídeo {video.video.name}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Erro ao atualizar ZIP'
            })
            
    except Exception as e:
        logger.error(f"Erro em update_zip_with_video_ajax: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@staff_member_required
def test_notifications_view(request):
    """Testa o sistema de notificações"""
    if request.method == 'POST':
        try:
            # Simular um arquivo de vídeo para teste
            class MockVideoFile:
                def __init__(self):
                    self.name = "teste_notificacao.mp4"
                    self.size = 25 * 1024 * 1024  # 25MB
            
            mock_video = MockVideoFile()
            
            # Tentar enviar notificações
            email_success = NotificationService.send_email_notification(mock_video, request.user)
            telegram_success = NotificationService.send_telegram_notification(mock_video, request.user)
            
            if email_success and telegram_success:
                messages.success(request, '✅ Notificações de teste enviadas com sucesso (Email + Telegram)!')
            elif telegram_success:
                messages.success(request, '✅ Notificação Telegram enviada com sucesso!')
                messages.warning(request, '⚠️ Email não enviado - verifique as configurações')
            elif email_success:
                messages.success(request, '✅ Notificação Email enviada com sucesso!')
                messages.warning(request, '⚠️ Telegram não enviado - verifique as configurações')
            else:
                messages.error(request, '❌ Falha ao enviar notificações - verifique as configurações')
                
        except Exception as e:
            logger.error(f"Erro ao testar notificações: {str(e)}")
            messages.error(request, f'❌ Erro ao testar notificações: {str(e)}')
    
    return redirect('painel_admin:zip_manager')

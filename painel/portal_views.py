# Views para gerenciar Portais sem Vídeo

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
import os
import zipfile

def get_admin_context(request):
    """Obter contexto padrão do admin"""
    return {
        'title': 'Portal sem Vídeo',
        'site_title': 'SRE Admin',
        'site_header': 'SRE Administration',
        'has_permission': True,
        'available_apps': [],
        'is_popup': False,
        'to_field': None,
        'cl': None,
        'opts': None,
        'original': None,
        'change': False,
        'add': False,
        'save_as': False,
        'show_save_and_continue': False,
        'show_save_and_add_another': False,
        'show_delete_link': False,
    }

@staff_member_required
def portal_sem_video_list(request):
    """Lista todos os portais sem vídeo"""
    from .models import EldPortalSemVideo
    
    context = get_admin_context(request)
    portais = EldPortalSemVideo.objects.all().order_by('-data_atualizacao')
    
    # Estatísticas
    total_portais = portais.count()
    portal_ativo = EldPortalSemVideo.get_portal_ativo()
    total_size = sum(portal.tamanho_mb for portal in portais)
    
    context.update({
        'title': 'Gerenciar Portais sem Vídeo',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Captive Portal', 'url': '/admin/captive_portal/'},
            {'name': 'Portais sem Vídeo', 'url': None}
        ],
        'portais': portais,
        'total_portais': total_portais,
        'portal_ativo': portal_ativo,
        'total_size': round(total_size, 2),
    })
    
    return render(request, 'admin/painel/portal_sem_video/list.html', context)

@staff_member_required
def portal_sem_video_upload(request):
    """Upload de novo portal sem vídeo"""
    from .models import EldPortalSemVideo
    
    context = get_admin_context(request)
    
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            versao = request.POST.get('versao')
            descricao = request.POST.get('descricao', '')
            arquivo_zip = request.FILES.get('arquivo_zip')
            ativo = request.POST.get('ativo') == 'on'
            
            # Validações
            if not nome or not versao or not arquivo_zip:
                messages.error(request, '❌ Nome, versão e arquivo ZIP são obrigatórios.')
                return render(request, 'admin/painel/portal_sem_video/upload.html', context)
            
            # Validar arquivo ZIP
            if not arquivo_zip.name.lower().endswith('.zip'):
                messages.error(request, '❌ O arquivo deve ter extensão .zip')
                return render(request, 'admin/painel/portal_sem_video/upload.html', context)
            
            # Validar tamanho (máximo 50MB)
            max_size = 50 * 1024 * 1024  # 50MB
            if arquivo_zip.size > max_size:
                messages.error(request, f'❌ Arquivo muito grande. Máximo: 50MB. Atual: {round(arquivo_zip.size / (1024 * 1024), 2)}MB')
                return render(request, 'admin/painel/portal_sem_video/upload.html', context)
            
            # Criar portal
            portal = EldPortalSemVideo(
                nome=nome,
                versao=versao,
                descricao=descricao,
                arquivo_zip=arquivo_zip,
                ativo=ativo
            )
            portal.save()
            
            messages.success(request, f'✅ Portal "{nome}" v{versao} criado com sucesso! ({portal.tamanho_mb}MB)')
            return redirect('painel:portal_sem_video_list')
            
        except Exception as e:
            messages.error(request, f'❌ Erro ao criar portal: {str(e)}')
    
    context.update({
        'title': 'Novo Portal sem Vídeo',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Captive Portal', 'url': '/admin/captive_portal/'},
            {'name': 'Portais sem Vídeo', 'url': '/admin/painel/portal-sem-video/'},
            {'name': 'Novo Portal', 'url': None}
        ],
    })
    
    return render(request, 'admin/painel/portal_sem_video/upload.html', context)

@staff_member_required
def portal_sem_video_detail(request, portal_id):
    """Detalhes e edição de portal sem vídeo"""
    from .models import EldPortalSemVideo
    
    portal = get_object_or_404(EldPortalSemVideo, id=portal_id)
    context = get_admin_context(request)
    
    if request.method == 'POST':
        try:
            # Atualizar campos
            portal.nome = request.POST.get('nome', portal.nome)
            portal.versao = request.POST.get('versao', portal.versao)
            portal.descricao = request.POST.get('descricao', portal.descricao)
            
            # Verificar se foi enviado novo arquivo
            novo_arquivo = request.FILES.get('arquivo_zip')
            if novo_arquivo:
                # Remover arquivo antigo
                if portal.arquivo_zip and os.path.exists(portal.arquivo_zip.path):
                    os.remove(portal.arquivo_zip.path)
                
                portal.arquivo_zip = novo_arquivo
            
            # Atualizar status ativo
            ativo = request.POST.get('ativo') == 'on'
            portal.ativo = ativo
            
            portal.save()
            
            messages.success(request, f'✅ Portal "{portal.nome}" atualizado com sucesso!')
            return redirect('painel:portal_sem_video_list')
            
        except Exception as e:
            messages.error(request, f'❌ Erro ao atualizar portal: {str(e)}')
    
    # Analisar conteúdo do ZIP
    zip_content = []
    if portal.arquivo_zip and os.path.exists(portal.arquivo_zip.path):
        try:
            with zipfile.ZipFile(portal.arquivo_zip.path, 'r') as zip_file:
                for info in zip_file.filelist:
                    zip_content.append({
                        'filename': info.filename,
                        'size': info.file_size,
                        'date': f"{info.date_time[0]}-{info.date_time[1]:02d}-{info.date_time[2]:02d}"
                    })
        except Exception:
            zip_content = [{'filename': 'Erro ao ler arquivo ZIP', 'size': 0, 'date': ''}]
    
    context.update({
        'title': f'Portal: {portal.nome}',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Captive Portal', 'url': '/admin/captive_portal/'},
            {'name': 'Portais sem Vídeo', 'url': '/admin/painel/portal-sem-video/'},
            {'name': portal.nome, 'url': None}
        ],
        'portal': portal,
        'zip_content': zip_content,
    })
    
    return render(request, 'admin/painel/portal_sem_video/detail.html', context)

@staff_member_required
def portal_sem_video_delete(request, portal_id):
    """Deletar portal sem vídeo"""
    from .models import EldPortalSemVideo
    
    portal = get_object_or_404(EldPortalSemVideo, id=portal_id)
    
    if request.method == 'POST':
        try:
            # Remover arquivo físico
            if portal.arquivo_zip and os.path.exists(portal.arquivo_zip.path):
                os.remove(portal.arquivo_zip.path)
            
            nome = portal.nome
            portal.delete()
            
            messages.success(request, f'✅ Portal "{nome}" deletado com sucesso!')
            return redirect('painel:portal_sem_video_list')
            
        except Exception as e:
            messages.error(request, f'❌ Erro ao deletar portal: {str(e)}')
    
    context = get_admin_context(request)
    context.update({
        'title': f'Deletar Portal: {portal.nome}',
        'breadcrumbs': [
            {'name': 'Início', 'url': '/admin/'},
            {'name': 'Captive Portal', 'url': '/admin/captive_portal/'},
            {'name': 'Portais sem Vídeo', 'url': '/admin/painel/portal-sem-video/'},
            {'name': 'Deletar', 'url': None}
        ],
        'portal': portal,
    })
    
    return render(request, 'admin/painel/portal_sem_video/delete.html', context)

@staff_member_required 
@csrf_exempt
def video_preview_ajax(request):
    """AJAX para preview de vídeo"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    try:
        from .models import EldUploadVideo
        
        data = json.loads(request.body)
        video_id = data.get('video_id')
        
        if not video_id:
            return JsonResponse({'success': False, 'error': 'ID do vídeo não fornecido'})
        
        video = get_object_or_404(EldUploadVideo, id=video_id)
        
        return JsonResponse({
            'success': True,
            'video': {
                'id': video.id,
                'name': video.video.name if video.video else 'N/A',
                'url': video.video.url if video.video else '',
                'size': f"{video.tamanho} MB",
                'date': video.data.strftime('%d/%m/%Y') if video.data else 'N/A',
                'filename': video.video.name.split('/')[-1] if video.video else 'N/A'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao obter preview: {str(e)}'
        })

@staff_member_required
def portal_sem_video_download(request, portal_id):
    """Download do arquivo ZIP do portal sem vídeo"""
    from .models import EldPortalSemVideo
    
    portal = get_object_or_404(EldPortalSemVideo, id=portal_id)
    
    if not portal.arquivo_zip or not os.path.exists(portal.arquivo_zip.path):
        raise Http404("Arquivo não encontrado")
    
    response = FileResponse(
        open(portal.arquivo_zip.path, 'rb'),
        content_type='application/zip'
    )
    
    # Nome do arquivo para download
    filename = f"scripts_poppnet_sre_v{portal.versao}.zip"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Content-Length'] = os.path.getsize(portal.arquivo_zip.path)
    
    return response

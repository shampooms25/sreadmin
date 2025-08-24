#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo

print("=== Correção Caminho Arquivo ===")
portal = EldPortalSemVideo.objects.filter(ativo=True).first()

if portal:
    print(f"Portal: {portal.nome}")
    print(f"ANTES - arquivo_zip.name: '{portal.arquivo_zip.name}'")
    
    # Corrigir o campo name removendo a duplicação
    current_name = portal.arquivo_zip.name
    if current_name.startswith('portal_sem_video/portal_sem_video/'):
        # Remover a duplicação
        new_name = current_name.replace('portal_sem_video/portal_sem_video/', 'portal_sem_video/')
        portal.arquivo_zip.name = new_name
        portal.save()
        print(f"CORRIGIDO - arquivo_zip.name: '{portal.arquivo_zip.name}'")
    elif current_name.startswith('portal_sem_video/') and not current_name.startswith('portal_sem_video/portal_sem_video/'):
        # Já está correto, mas vamos garantir que seja apenas o nome do arquivo
        filename = os.path.basename(current_name)
        portal.arquivo_zip.name = filename
        portal.save()
        print(f"NORMALIZADO - arquivo_zip.name: '{portal.arquivo_zip.name}'")
    else:
        print(f"Caminho já está correto: '{current_name}'")
    
    print(f"FINAL - arquivo_zip.path: '{portal.arquivo_zip.path}'")
else:
    print("Nenhum portal sem vídeo ativo encontrado")

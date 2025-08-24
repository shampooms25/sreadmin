#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo

print("=== Debug Caminho Arquivo ===")
portal = EldPortalSemVideo.objects.filter(ativo=True).first()

if portal:
    print(f"Portal: {portal.nome}")
    print(f"arquivo_zip.name: '{portal.arquivo_zip.name}'")
    print(f"arquivo_zip.path: '{portal.arquivo_zip.path}'")
    print(f"Arquivo existe: {os.path.exists(portal.arquivo_zip.path)}")
    
    # Verificar se o caminho correto existe
    correct_path = portal.arquivo_zip.path.replace('/portal_sem_video/portal_sem_video/', '/portal_sem_video/')
    print(f"Caminho corrigido: '{correct_path}'")
    print(f"Caminho corrigido existe: {os.path.exists(correct_path)}")
    
    # Listar arquivos no diretório
    import pathlib
    media_dir = os.path.dirname(portal.arquivo_zip.path)
    parent_dir = os.path.dirname(media_dir)
    print(f"\nArquivos em {parent_dir}:")
    try:
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            if os.path.isdir(item_path):
                print(f"  DIR: {item}/")
                try:
                    for subitem in os.listdir(item_path):
                        print(f"    {subitem}")
                except:
                    pass
            else:
                print(f"  FILE: {item}")
    except Exception as e:
        print(f"Erro ao listar: {e}")
else:
    print("Nenhum portal sem vídeo ativo encontrado")

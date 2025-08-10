#!/usr/bin/env python
"""
Script para testar a configuração de media files do Django
"""
import os
import sys
import django

# Adicionar o diretório do projeto ao Python path
sys.path.append(r'c:\\Projetos\\Poppnet\\sreadmin')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'captive_portal.settings')
django.setup()

from django.conf import settings
from painel.models import EldPortalSemVideo

def test_media_config():
    """Testa a configuração de mídia"""
    print("=== TESTE DE CONFIGURAÇÃO DE MÍDIA ===")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT existe: {os.path.exists(settings.MEDIA_ROOT)}")
    
    # Testar diretório de previews
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'portais_sem_video', 'previews')
    print(f"Preview dir: {preview_dir}")
    print(f"Preview dir existe: {os.path.exists(preview_dir)}")
    
    # Verificar permissões
    try:
        test_file = os.path.join(preview_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ Permissões de escrita OK")
    except Exception as e:
        print(f"❌ Erro de permissões: {e}")
    
    # Verificar modelo
    print("\n=== TESTE DO MODELO ===")
    try:
        # Verificar field preview
        field = EldPortalSemVideo._meta.get_field('preview')
        print(f"Campo preview: {field}")
        print(f"Upload to: {field.upload_to}")
        print(f"Blank: {field.blank}")
        print(f"Null: {field.null}")
        print("✅ Campo preview configurado corretamente")
    except Exception as e:
        print(f"❌ Erro no campo preview: {e}")

if __name__ == "__main__":
    test_media_config()

#!/usr/bin/env python3
"""
Debug da API - Execute no servidor para ver exatamente o que está acontecendo
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, '/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo
from django.conf import settings

def debug_api_portal():
    print("=== DEBUG COMPLETO DA API ===")
    
    # 1. Verificar configuração
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    # 2. Buscar portal ativo
    portal_sem_video = EldPortalSemVideo.objects.filter(ativo=True).first()
    
    if not portal_sem_video:
        print("❌ ERRO: Nenhum portal sem vídeo ativo encontrado!")
        return
    
    print(f"✅ Portal encontrado: {portal_sem_video.nome}")
    
    # 3. Verificar arquivo_zip
    if not portal_sem_video.arquivo_zip:
        print("❌ ERRO: Campo arquivo_zip está vazio!")
        return
    
    print(f"✅ Campo arquivo_zip preenchido")
    
    # 4. Obter path
    file_path = portal_sem_video.arquivo_zip.path
    filename = "scripts_poppnet_sre.zip"
    
    print(f"arquivo_zip.name: '{portal_sem_video.arquivo_zip.name}'")
    print(f"arquivo_zip.path: '{file_path}'")
    print(f"filename para download: '{filename}'")
    
    # 5. Verificar existência - ESTE É O PONTO CRÍTICO
    exists = os.path.exists(file_path)
    print(f"os.path.exists(file_path): {exists}")
    
    if not exists:
        print("❌ ARQUIVO NÃO ENCONTRADO PELA API!")
        print("Simulando erro 404 que seria retornado...")
        
        error_response = {
            'error': 'Arquivo não encontrado',
            'message': f'Arquivo ZIP não existe no servidor: {file_path}',
            'timestamp': '2025-08-25T...'
        }
        print(f"Resposta de erro: {error_response}")
        
        # Tentar verificar paths alternativos
        print("\n=== TENTANDO PATHS ALTERNATIVOS ===")
        alternative_paths = [
            file_path.strip(),
            file_path.replace('\n', '').replace('\r', ''),
            os.path.normpath(file_path),
            os.path.realpath(file_path)
        ]
        
        for i, alt_path in enumerate(alternative_paths):
            alt_exists = os.path.exists(alt_path)
            print(f"Alternativa {i+1}: {alt_exists} - '{alt_path}'")
            if alt_exists:
                print(f"  ✅ ESTE PATH FUNCIONA!")
                break
    else:
        print("✅ ARQUIVO ENCONTRADO!")
        size = os.path.getsize(file_path)
        print(f"Tamanho: {size} bytes")

if __name__ == '__main__':
    debug_api_portal()

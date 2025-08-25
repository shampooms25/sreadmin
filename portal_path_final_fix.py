#!/usr/bin/env python3
"""
Correção definitiva do path do portal sem vídeo
Execute este script no servidor de produção
"""
import os
import sys
import django
from pathlib import Path

# Configuração para produção
sys.path.insert(0, '/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo
from django.conf import settings

def find_working_file():
    """Encontra qual arquivo realmente existe e funciona"""
    
    print("=== DIAGNÓSTICO COMPLETO ===")
    
    # 1. Verificar configuração do Django
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    # 2. Listar todos os arquivos .zip possíveis
    base_dir = Path(settings.MEDIA_ROOT) / 'portal_sem_video'
    subdirs = [
        base_dir,  # /var/www/sreadmin/media/portal_sem_video/
        base_dir / 'portal_sem_video'  # /var/www/sreadmin/media/portal_sem_video/portal_sem_video/
    ]
    
    all_files = []
    for dir_path in subdirs:
        if dir_path.exists():
            zip_files = list(dir_path.glob('*.zip'))
            for f in zip_files:
                relative_path = str(f.relative_to(settings.MEDIA_ROOT))
                all_files.append({
                    'full_path': str(f),
                    'relative_path': relative_path,
                    'size': f.stat().st_size,
                    'exists': f.exists()
                })
    
    print(f"\nArquivos encontrados ({len(all_files)}):")
    for i, file_info in enumerate(all_files):
        print(f"  {i+1}. {file_info['relative_path']}")
        print(f"     Path completo: {file_info['full_path']}")
        print(f"     Tamanho: {file_info['size']} bytes")
        print(f"     Existe: {file_info['exists']}")
        print()
    
    # 3. Verificar estado atual do banco
    portal = EldPortalSemVideo.objects.filter(ativo=True).first()
    if portal:
        print(f"Portal ativo no banco:")
        print(f"  Nome: {portal.nome}")
        print(f"  arquivo_zip.name: '{portal.arquivo_zip.name}'")
        print(f"  arquivo_zip.path: '{portal.arquivo_zip.path}'")
        print(f"  Arquivo existe: {os.path.exists(portal.arquivo_zip.path)}")
        print()
    
    # 4. Retornar arquivo mais adequado
    if all_files:
        # Preferir arquivo na raiz do diretório (sem subdiretório duplicado)
        root_files = [f for f in all_files if not 'portal_sem_video/portal_sem_video' in f['relative_path']]
        if root_files:
            # Pegar o mais recente
            newest = max(root_files, key=lambda x: os.path.getctime(x['full_path']))
            return newest['relative_path']
        else:
            # Se só tem no subdiretório, usar esse
            newest = max(all_files, key=lambda x: os.path.getctime(x['full_path']))
            return newest['relative_path']
    
    return None

def fix_portal_path():
    """Corrige o path do portal"""
    
    working_file = find_working_file()
    
    if not working_file:
        print("❌ ERRO: Nenhum arquivo .zip encontrado!")
        return False
    
    print(f"✅ Arquivo escolhido: {working_file}")
    
    # Atualizar banco
    count = EldPortalSemVideo.objects.filter(ativo=True).update(
        arquivo_zip=working_file
    )
    
    print(f"✅ {count} portal(s) atualizado(s)")
    
    # Verificar se ficou correto
    portal = EldPortalSemVideo.objects.filter(ativo=True).first()
    if portal:
        print(f"\nVerificação pós-correção:")
        print(f"  novo arquivo_zip.name: '{portal.arquivo_zip.name}'")
        print(f"  novo arquivo_zip.path: '{portal.arquivo_zip.path}'")
        print(f"  Arquivo existe agora: {os.path.exists(portal.arquivo_zip.path)}")
        
        if os.path.exists(portal.arquivo_zip.path):
            print(f"  Tamanho: {os.path.getsize(portal.arquivo_zip.path)} bytes")
            return True
        else:
            print("  ❌ AINDA NÃO EXISTE!")
            return False
    
    return False

if __name__ == '__main__':
    print("=== CORREÇÃO DEFINITIVA DO PORTAL SEM VÍDEO ===")
    
    success = fix_portal_path()
    
    if success:
        print("\n🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("Agora teste a API novamente.")
    else:
        print("\n❌ CORREÇÃO FALHOU!")
        print("Verifique se existem arquivos .zip no diretório.")

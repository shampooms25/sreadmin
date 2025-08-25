#!/usr/bin/env python3
"""
Script para corrigir paths do portal sem vídeo em produção
Executa diretamente no servidor Linux de produção
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django para produção
sys.path.insert(0, '/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo

def list_actual_files():
    """Lista arquivos reais no diretório de media"""
    media_dir = Path('/var/www/sreadmin/media/portal_sem_video')
    print(f"=== Arquivos no diretório {media_dir} ===")
    
    if not media_dir.exists():
        print("ERRO: Diretório não existe!")
        return []
    
    files = list(media_dir.glob('*.zip'))
    for f in files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  - {f.name} ({size_mb:.2f} MB)")
    
    return files

def check_database_records():
    """Verifica registros no banco de dados"""
    print("\n=== Registros no banco de dados ===")
    
    portals = EldPortalSemVideo.objects.filter(ativo=True)
    for portal in portals:
        print(f"Portal: {portal.nome}")
        print(f"  Arquivo no DB: '{portal.arquivo_zip.name}'")
        print(f"  Path completo: '{portal.arquivo_zip.path}'")
        print(f"  Arquivo existe: {os.path.exists(portal.arquivo_zip.path)}")
        print()

def fix_portal_paths():
    """Corrige os caminhos dos portais"""
    print("\n=== Iniciando correção dos paths ===")
    
    # Listar arquivos reais
    actual_files = list_actual_files()
    if not actual_files:
        print("ERRO: Nenhum arquivo .zip encontrado!")
        return False
    
    # Pegar o arquivo mais recente (provavelmente o correto)
    latest_file = max(actual_files, key=lambda f: f.stat().st_mtime)
    relative_path = f"portal_sem_video/{latest_file.name}"
    
    print(f"Arquivo mais recente: {latest_file.name}")
    print(f"Path relativo correto: {relative_path}")
    
    # Atualizar registros ativos
    portals = EldPortalSemVideo.objects.filter(ativo=True)
    
    if not portals.exists():
        print("ERRO: Nenhum portal ativo encontrado!")
        return False
    
    for portal in portals:
        print(f"\nCorrigindo portal: {portal.nome}")
        print(f"  Path antigo: '{portal.arquivo_zip.name}'")
        
        # Atualizar usando update() para evitar validação
        EldPortalSemVideo.objects.filter(id=portal.id).update(
            arquivo_zip=relative_path
        )
        
        # Verificar se a correção funcionou
        portal.refresh_from_db()
        print(f"  Path novo: '{portal.arquivo_zip.name}'")
        print(f"  Arquivo existe agora: {os.path.exists(portal.arquivo_zip.path)}")
    
    return True

def main():
    print("=== CORREÇÃO DE PATHS DO PORTAL SEM VÍDEO ===")
    print("Ambiente: Produção Linux")
    print()
    
    try:
        # Verificar estado atual
        check_database_records()
        
        # Executar correção
        success = fix_portal_paths()
        
        if success:
            print("\n✅ CORREÇÃO CONCLUÍDA!")
            print("Verificando resultado...")
            check_database_records()
        else:
            print("\n❌ CORREÇÃO FALHOU!")
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

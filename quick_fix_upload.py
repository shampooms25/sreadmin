#!/usr/bin/env python3
"""
Script de correção rápida para o erro de permissão em /videos
Execute este script diretamente no servidor de produção
"""

import os
import sys
import subprocess
import django
from pathlib import Path

def main():
    print("🚨 CORREÇÃO RÁPIDA - ERRO DE UPLOAD")
    print("=" * 40)
    
    # Configurar Django
    project_path = "/var/www/sreadmin"
    if not os.path.exists(project_path):
        print(f"❌ Projeto não encontrado em {project_path}")
        print("   Ajuste o caminho se necessário")
        return
    
    os.chdir(project_path)
    sys.path.insert(0, project_path)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
        django.setup()
        from django.conf import settings
        
        print(f"✅ Django configurado")
        print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
        
    except Exception as e:
        print(f"❌ Erro Django: {e}")
        return
    
    # Verificar se o diretório /videos existe (problemático)
    if os.path.exists("/videos"):
        print("⚠️  PROBLEMA ENCONTRADO: /videos existe na raiz do sistema")
        print("   Isso está causando conflito com o upload")
        
        # Verificar se é um link simbólico
        if os.path.islink("/videos"):
            print("   É um link simbólico - removendo...")
            try:
                os.unlink("/videos")
                print("   ✅ Link removido")
            except Exception as e:
                print(f"   ❌ Erro ao remover link: {e}")
        else:
            print("   É um diretório real - precisa ser removido manualmente")
            print("   Execute: sudo rm -rf /videos (CUIDADO!)")
    
    # Criar estrutura correta
    media_root = settings.MEDIA_ROOT
    video_dir = os.path.join(media_root, 'videos', 'eld')
    zip_dir = os.path.join(media_root, 'captive_portal_zips')
    
    print(f"\n📁 Criando estrutura correta:")
    
    dirs_to_create = [media_root, video_dir, zip_dir]
    
    for directory in dirs_to_create:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"   ✅ {directory}")
        except Exception as e:
            print(f"   ❌ {directory}: {e}")
    
    # Corrigir permissões
    print(f"\n🔐 Corrigindo permissões:")
    
    commands = [
        f"sudo chown -R www-data:www-data {media_root}",
        f"sudo chmod -R 775 {video_dir}",
        f"sudo chmod -R 775 {zip_dir}",
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {cmd}")
            else:
                print(f"   ❌ {cmd}: {result.stderr}")
        except Exception as e:
            print(f"   ❌ {cmd}: {e}")
    
    # Teste de escrita
    print(f"\n🧪 Testando escrita:")
    
    test_file = os.path.join(video_dir, 'test_upload.txt')
    try:
        with open(test_file, 'w') as f:
            f.write("teste de upload")
        os.remove(test_file)
        print("   ✅ Escrita funcionando!")
    except Exception as e:
        print(f"   ❌ Erro na escrita: {e}")
    
    # Reiniciar Apache
    print(f"\n🔄 Reiniciando Apache:")
    try:
        result = subprocess.run(['sudo', 'systemctl', 'restart', 'apache2'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Apache reiniciado")
        else:
            print(f"   ❌ Erro ao reiniciar Apache: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print(f"\n✅ CORREÇÃO CONCLUÍDA!")
    print(f"   Teste agora em: https://paineleld.poppnet.com.br/admin/eld/videos/upload/")
    print(f"\n📝 Se ainda houver erro, verifique:")
    print(f"   sudo tail -f /var/log/apache2/error.log")

if __name__ == "__main__":
    main()

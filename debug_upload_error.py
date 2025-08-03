#!/usr/bin/env python3
"""
Script de diagnóstico específico para o erro "/videos" em produção
Execute este script no servidor: python3 debug_upload_error.py
"""

import os
import sys
import django
from pathlib import Path

def main():
    print("🔍 DIAGNÓSTICO ESPECÍFICO - ERRO /videos")
    print("=" * 50)
    
    # Configurar Django
    project_path = "/var/www/sreadmin"
    
    # Verificar se estamos no diretório correto
    current_dir = os.getcwd()
    print(f"📁 Diretório atual: {current_dir}")
    
    if not os.path.exists(project_path):
        print(f"❌ Projeto não encontrado em {project_path}")
        return
    
    os.chdir(project_path)
    sys.path.insert(0, project_path)
    
    # Configurar Django
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
        django.setup()
        from django.conf import settings
        
        print(f"✅ Django configurado")
        print(f"   BASE_DIR: {settings.BASE_DIR}")
        print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
        print(f"   MEDIA_URL: {settings.MEDIA_URL}")
        
        # Verificar se MEDIA_ROOT é absoluto
        media_root_abs = os.path.abspath(settings.MEDIA_ROOT)
        print(f"   MEDIA_ROOT (absoluto): {media_root_abs}")
        
    except Exception as e:
        print(f"❌ Erro Django: {e}")
        return
    
    # Verificar estrutura de diretórios
    print(f"\n📂 VERIFICANDO ESTRUTURA:")
    
    dirs_to_check = [
        "/videos",  # Problemático
        "/var/www/sreadmin",
        "/var/www/sreadmin/media",
        "/var/www/sreadmin/media/videos",
        "/var/www/sreadmin/media/videos/eld",
        settings.MEDIA_ROOT,
        os.path.join(settings.MEDIA_ROOT, 'videos'),
        os.path.join(settings.MEDIA_ROOT, 'videos', 'eld'),
    ]
    
    for directory in dirs_to_check:
        if os.path.exists(directory):
            stat_info = os.stat(directory)
            perms = oct(stat_info.st_mode)[-3:]
            print(f"   ✅ {directory} - Permissões: {perms}")
            if directory == "/videos":
                print(f"      ⚠️  PROBLEMA: Este diretório não deveria existir!")
        else:
            print(f"   ❌ {directory} - NÃO EXISTE")
    
    # Testar criação de arquivo no diretório correto
    print(f"\n🧪 TESTE DE ESCRITA:")
    
    correct_video_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'eld')
    
    # Criar diretório se não existir
    os.makedirs(correct_video_dir, exist_ok=True)
    
    test_file_path = os.path.join(correct_video_dir, 'test_write.txt')
    
    try:
        with open(test_file_path, 'w') as f:
            f.write("teste de escrita")
        print(f"   ✅ Escrita OK em: {test_file_path}")
        os.remove(test_file_path)
    except Exception as e:
        print(f"   ❌ Erro na escrita: {e}")
    
    # Verificar se há link simbólico problemático
    print(f"\n🔗 VERIFICANDO LINKS SIMBÓLICOS:")
    
    if os.path.exists("/videos"):
        if os.path.islink("/videos"):
            link_target = os.readlink("/videos")
            print(f"   ⚠️  /videos é um link para: {link_target}")
            print(f"      AÇÃO: sudo rm /videos")
        else:
            print(f"   ⚠️  /videos é um diretório real")
            print(f"      CUIDADO: Verificar conteúdo antes de remover")
    else:
        print(f"   ✅ /videos não existe (correto)")
    
    # Testar modelo Django
    print(f"\n🔧 TESTE DO MODELO DJANGO:")
    
    try:
        from painel.models import EldUploadVideo
        
        # Verificar o upload_to do modelo
        video_field = EldUploadVideo._meta.get_field('video')
        upload_to = video_field.upload_to
        print(f"   Upload_to configurado: {upload_to}")
        
        # Calcular caminho completo
        full_upload_path = os.path.join(settings.MEDIA_ROOT, upload_to)
        print(f"   Caminho completo: {full_upload_path}")
        
        # Verificar se o diretório existe
        if os.path.exists(full_upload_path):
            print(f"   ✅ Diretório de upload existe")
        else:
            print(f"   ❌ Diretório de upload NÃO existe - criando...")
            os.makedirs(full_upload_path, exist_ok=True)
            print(f"   ✅ Diretório criado")
        
    except Exception as e:
        print(f"   ❌ Erro no modelo: {e}")
    
    # Verificar variáveis de ambiente
    print(f"\n🌐 VARIÁVEIS DE AMBIENTE:")
    
    env_vars = [
        'DJANGO_SETTINGS_MODULE',
        'PYTHONPATH',
        'USER',
        'HOME'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'NÃO DEFINIDA')
        print(f"   {var}: {value}")
    
    # Verificar processos Apache/Django
    print(f"\n⚙️  PROCESSOS:")
    
    try:
        import subprocess
        
        # Verificar Apache
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'apache2' in result.stdout:
            print(f"   ✅ Apache2 rodando")
        else:
            print(f"   ❌ Apache2 não encontrado")
        
        # Verificar Django
        if 'manage.py' in result.stdout or 'wsgi' in result.stdout:
            print(f"   ✅ Django detectado")
        else:
            print(f"   ⚠️  Django não detectado nos processos")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar processos: {e}")
    
    # Recomendações finais
    print(f"\n💡 RECOMENDAÇÕES:")
    
    if os.path.exists("/videos"):
        print(f"   1. REMOVER /videos da raiz:")
        print(f"      sudo rm -rf /videos  # CUIDADO!")
    
    print(f"   2. VERIFICAR configuração Apache:")
    print(f"      sudo nano /etc/apache2/sites-available/paineleld.conf")
    
    print(f"   3. REINICIAR Apache:")
    print(f"      sudo systemctl restart apache2")
    
    print(f"   4. VERIFICAR logs:")
    print(f"      sudo tail -f /var/log/apache2/error.log")
    
    print(f"\n✅ DIAGNÓSTICO CONCLUÍDO!")

if __name__ == "__main__":
    main()

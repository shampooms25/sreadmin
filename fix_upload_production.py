#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir problemas de upload em produção
Execute: python3 fix_upload_production.py
"""

import os
import sys
import stat
import subprocess
from pathlib import Path

def run_command(command):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_permissions(path):
    """Verifica permissões de um diretório"""
    try:
        if os.path.exists(path):
            st = os.stat(path)
            permissions = oct(st.st_mode)[-3:]
            owner = st.st_uid
            group = st.st_gid
            return True, permissions, owner, group
        else:
            return False, None, None, None
    except Exception as e:
        return False, str(e), None, None

def main():
    print("🔧 DIAGNÓSTICO DE UPLOAD EM PRODUÇÃO")
    print("=" * 50)
    
    # 1. Verificar diretório do projeto
    project_root = "/var/www/sreadmin"
    if not os.path.exists(project_root):
        print(f"❌ Diretório do projeto não encontrado: {project_root}")
        print("   Ajuste o caminho no script se necessário")
        return
    
    print(f"✅ Projeto encontrado em: {project_root}")
    
    # 2. Verificar configuração Django
    os.chdir(project_root)
    sys.path.insert(0, project_root)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
        import django
        django.setup()
        from django.conf import settings
        
        media_root = settings.MEDIA_ROOT
        media_url = settings.MEDIA_URL
        
        print(f"✅ Django configurado:")
        print(f"   MEDIA_ROOT: {media_root}")
        print(f"   MEDIA_URL: {media_url}")
        
    except Exception as e:
        print(f"❌ Erro ao carregar Django: {e}")
        return
    
    # 3. Verificar estrutura de diretórios
    print("\n📁 VERIFICANDO ESTRUTURA DE DIRETÓRIOS:")
    
    directories_to_check = [
        media_root,
        os.path.join(media_root, 'videos'),
        os.path.join(media_root, 'videos', 'eld'),
        os.path.join(media_root, 'captive_portal_zips'),
    ]
    
    directories_to_create = []
    
    for directory in directories_to_check:
        exists, permissions, owner, group = check_permissions(directory)
        if exists:
            print(f"   ✅ {directory} - Permissões: {permissions}")
        else:
            print(f"   ❌ {directory} - NÃO EXISTE")
            directories_to_create.append(directory)
    
    # 4. Criar diretórios faltantes
    if directories_to_create:
        print(f"\n🛠️  CRIANDO DIRETÓRIOS FALTANTES:")
        for directory in directories_to_create:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"   ✅ Criado: {directory}")
            except Exception as e:
                print(f"   ❌ Erro ao criar {directory}: {e}")
    
    # 5. Verificar usuário do servidor web
    print(f"\n👤 VERIFICANDO USUÁRIO DO SERVIDOR WEB:")
    
    # Detectar servidor web
    apache_running, _, _ = run_command("systemctl is-active apache2")
    nginx_running, _, _ = run_command("systemctl is-active nginx")
    
    web_user = "www-data"  # Padrão para Ubuntu
    
    if apache_running:
        print("   ✅ Apache2 detectado")
    elif nginx_running:
        print("   ✅ Nginx detectado")
    else:
        print("   ⚠️  Servidor web não detectado ou não rodando")
    
    print(f"   Usuário do servidor web: {web_user}")
    
    # 6. Corrigir permissões
    print(f"\n🔐 CORRIGINDO PERMISSÕES:")
    
    commands = [
        f"sudo chown -R {web_user}:{web_user} {media_root}",
        f"sudo chmod -R 755 {media_root}",
        f"sudo chmod -R 775 {os.path.join(media_root, 'videos')}",
        f"sudo chmod -R 775 {os.path.join(media_root, 'captive_portal_zips')}",
    ]
    
    for command in commands:
        success, stdout, stderr = run_command(command)
        if success:
            print(f"   ✅ {command}")
        else:
            print(f"   ❌ {command}")
            print(f"      Erro: {stderr}")
    
    # 7. Verificar se existe o diretório problemático /videos
    if os.path.exists("/videos"):
        print(f"\n⚠️  DIRETÓRIO PROBLEMÁTICO ENCONTRADO:")
        print(f"   /videos existe - isso pode causar conflitos")
        print(f"   Execute: sudo rm -rf /videos (se for um link ou diretório vazio)")
    
    # 8. Teste final
    print(f"\n🧪 TESTE FINAL:")
    
    test_file = os.path.join(media_root, 'videos', 'eld', 'test_write.txt')
    try:
        with open(test_file, 'w') as f:
            f.write("teste de escrita")
        os.remove(test_file)
        print("   ✅ Escrita no diretório de vídeos: FUNCIONANDO")
    except Exception as e:
        print(f"   ❌ Escrita no diretório de vídeos: ERRO - {e}")
    
    # 9. Instruções finais
    print(f"\n📋 PRÓXIMOS PASSOS:")
    print(f"   1. Reinicie o servidor web:")
    print(f"      sudo systemctl restart apache2")
    print(f"      # ou sudo systemctl restart nginx")
    print(f"   2. Teste o upload em:")
    print(f"      https://paineleld.poppnet.com.br/admin/eld/videos/upload/")
    print(f"   3. Se ainda houver erro, verifique os logs:")
    print(f"      sudo tail -f /var/log/apache2/error.log")
    print(f"      sudo tail -f /var/log/nginx/error.log")
    
    print(f"\n✅ DIAGNÓSTICO CONCLUÍDO!")

if __name__ == "__main__":
    main()

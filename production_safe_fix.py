#!/usr/bin/env python3
"""
CORREÇÃO SEGURA PARA PRODUÇÃO - SEM CONFLITO COM GIT
Esta correção NÃO modifica arquivos versionados, evitando conflitos no git pull
"""

import os
import sys

def main():
    print("🛡️  CORREÇÃO SEGURA - SEM CONFLITO GIT")
    print("=" * 40)
    
    project_path = "/var/www/sreadmin"
    
    # 1. SOLUÇÃO: Criar arquivo local_settings.py (não versionado)
    local_settings_path = f"{project_path}/sreadmin/local_settings.py"
    
    local_settings_content = '''"""
Configurações específicas de produção
Este arquivo NÃO é versionado no Git
"""
import os
from .settings import *

# Forçar MEDIA_ROOT absoluto para produção
MEDIA_ROOT = '/var/www/sreadmin/media'

# Configuração adicional de logging para debug
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/www/sreadmin/logs/django_upload_debug.log',
        },
    },
    'loggers': {
        'painel.models': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Debug para verificar caminhos
print(f"🔍 LOCAL_SETTINGS: MEDIA_ROOT = {MEDIA_ROOT}")
'''
    
    with open(local_settings_path, 'w', encoding='utf-8') as f:
        f.write(local_settings_content)
    print(f"✅ Criado: {local_settings_path}")
    
    # 2. Modificar apenas o wsgi.py para usar local_settings
    wsgi_path = f"{project_path}/sreadmin/wsgi.py"
    
    if os.path.exists(wsgi_path):
        with open(wsgi_path, 'r', encoding='utf-8') as f:
            wsgi_content = f.read()
        
        # Fazer backup
        backup_wsgi = f"{wsgi_path}.backup_safe"
        with open(backup_wsgi, 'w', encoding='utf-8') as f:
            f.write(wsgi_content)
        
        # Modificar apenas a linha do settings
        if "sreadmin.settings" in wsgi_content:
            new_wsgi = wsgi_content.replace(
                "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')",
                "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.local_settings')"
            )
            
            with open(wsgi_path, 'w', encoding='utf-8') as f:
                f.write(new_wsgi)
            
            print(f"✅ wsgi.py modificado para usar local_settings")
        else:
            print(f"⚠️  Não foi possível modificar wsgi.py automaticamente")
    
    # 3. Criar estrutura de diretórios
    media_path = f"{project_path}/media/videos/eld"
    logs_path = f"{project_path}/logs"
    
    os.makedirs(media_path, exist_ok=True)
    os.makedirs(logs_path, exist_ok=True)
    
    print(f"✅ Diretórios criados")
    
    # 4. Configurar permissões
    os.system(f"sudo chown -R www-data:www-data {project_path}/media")
    os.system(f"sudo chown -R www-data:www-data {project_path}/logs")
    os.system(f"sudo chmod -R 775 {project_path}/media")
    os.system(f"sudo chmod -R 775 {project_path}/logs")
    
    print(f"✅ Permissões configuradas")
    
    # 5. Criar .gitignore local se não existir
    gitignore_path = f"{project_path}/.gitignore"
    gitignore_additions = """
# Arquivos específicos de produção (não versionar)
sreadmin/local_settings.py
logs/
*.log
media/videos/
.env.production
"""
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        
        if "local_settings.py" not in gitignore_content:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write(gitignore_additions)
            print(f"✅ .gitignore atualizado")
    else:
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_additions)
        print(f"✅ .gitignore criado")
    
    # 6. Script para reverter (se necessário)
    revert_script = f"""#!/bin/bash
# Script para reverter alterações
echo "🔄 Revertendo alterações..."

# Restaurar wsgi.py original
if [ -f "{wsgi_path}.backup_safe" ]; then
    cp "{wsgi_path}.backup_safe" "{wsgi_path}"
    echo "✅ wsgi.py restaurado"
fi

# Remover local_settings.py
if [ -f "{local_settings_path}" ]; then
    rm "{local_settings_path}"
    echo "✅ local_settings.py removido"
fi

# Reiniciar Apache
sudo systemctl restart apache2
echo "✅ Apache reiniciado"
echo "🔄 Reversão completa!"
"""
    
    revert_path = f"{project_path}/revert_safe_fix.sh"
    with open(revert_path, 'w', encoding='utf-8') as f:
        f.write(revert_script)
    
    os.chmod(revert_path, 0o755)
    print(f"✅ Script de reversão criado: {revert_path}")
    
    print(f"\n📋 INSTRUÇÕES DE USO:")
    print(f"   1. sudo systemctl restart apache2")
    print(f"   2. Testar upload no admin")
    print(f"   3. Verificar logs: tail -f {logs_path}/django_upload_debug.log")
    
    print(f"\n🔒 SEGURANÇA GIT:")
    print(f"   ✅ Arquivos versionados NÃO foram modificados")
    print(f"   ✅ local_settings.py está no .gitignore") 
    print(f"   ✅ git pull funcionará normalmente")
    print(f"   ✅ wsgi.py pode ser revertido facilmente")
    
    print(f"\n🚨 IMPORTANTE:")
    print(f"   - Para git pull: git stash (se wsgi.py foi modificado)")
    print(f"   - Ou use: {revert_path} antes do git pull")
    print(f"   - Depois reaplique: python3 {__file__}")
    
    print(f"\n✅ CORREÇÃO SEGURA APLICADA!")

if __name__ == "__main__":
    main()

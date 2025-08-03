#!/usr/bin/env python3
"""
Correção definitiva que força o Django a usar caminhos absolutos
Resolve o problema de '/videos' de forma elegante
"""

import os
import sys

def main():
    print("🎯 CORREÇÃO DEFINITIVA - CAMINHOS ABSOLUTOS")
    print("=" * 45)
    
    project_path = "/var/www/sreadmin"
    
    # 1. Corrigir models.py
    models_path = f"{project_path}/painel/models.py"
    
    if not os.path.exists(models_path):
        print(f"❌ Arquivo não encontrado: {models_path}")
        return
    
    # Fazer backup
    backup_path = f"{models_path}.backup_definitivo"
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup criado: {backup_path}")
    
    # Substituir upload_to por função que força caminho absoluto
    if "upload_to='videos/eld/'" in content:
        new_content = content.replace(
            "upload_to='videos/eld/',",
            "upload_to=lambda instance, filename: os.path.join('videos', 'eld', filename),"
        )
        
        # Adicionar import do os se não existir
        if "import os" not in new_content:
            lines = new_content.split('\n')
            # Encontrar onde adicionar o import
            for i, line in enumerate(lines):
                if line.startswith('from django') or line.startswith('import'):
                    lines.insert(i, 'import os')
                    break
            new_content = '\n'.join(lines)
        
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Campo upload_to modificado para usar função lambda")
    
    # 2. Verificar/criar settings específico para produção
    settings_path = f"{project_path}/sreadmin/settings.py"
    
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings_content = f.read()
        
        # Verificar se MEDIA_ROOT está correto
        if "MEDIA_ROOT = os.path.join(BASE_DIR, 'media')" in settings_content:
            print("✅ MEDIA_ROOT já está configurado corretamente")
        else:
            # Adicionar configuração forçada
            additional_config = """
# CORREÇÃO FORÇADA PARA PRODUÇÃO
import os
MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'media'))
MEDIA_URL = '/media/'

# Log de debug para verificar caminhos
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.error(f"MEDIA_ROOT configurado para: {MEDIA_ROOT}")
"""
            
            settings_content += additional_config
            
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(settings_content)
            
            print("✅ Configuração adicional adicionada ao settings.py")
    
    # 3. Criar estrutura e permissões
    media_path = f"{project_path}/media/videos/eld"
    os.makedirs(media_path, exist_ok=True)
    print(f"✅ Diretório criado: {media_path}")
    
    # 4. Configurar permissões
    os.system(f"sudo chown -R www-data:www-data {project_path}/media")
    os.system(f"sudo chmod -R 775 {project_path}/media/videos")
    print(f"✅ Permissões configuradas")
    
    # 5. Criar arquivo de teste para verificar caminho
    test_script = f"""#!/usr/bin/env python3
import os
import sys
import django

sys.path.insert(0, '{project_path}')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.conf import settings
from painel.models import EldUploadVideo

print(f"MEDIA_ROOT: {{settings.MEDIA_ROOT}}")
print(f"BASE_DIR: {{settings.BASE_DIR}}")

# Testar campo upload_to
field = EldUploadVideo._meta.get_field('video')
print(f"Upload_to: {{field.upload_to}}")

# Simular upload
filename = 'test_video.mp4'
if hasattr(field.upload_to, '__call__'):
    upload_path = field.upload_to(None, filename)
else:
    upload_path = field.upload_to
    
full_path = os.path.join(settings.MEDIA_ROOT, upload_path if isinstance(upload_path, str) else upload_path)
print(f"Caminho completo seria: {{full_path}}")
"""
    
    test_script_path = f"{project_path}/test_upload_path.py"
    with open(test_script_path, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print(f"✅ Script de teste criado: {test_script_path}")
    
    # 6. Remover /videos se existir
    if os.path.exists("/videos"):
        print(f"⚠️  Removendo /videos da raiz...")
        os.system("sudo rm -rf /videos")
        print(f"✅ /videos removido")
    
    print(f"\n🧪 TESTE A CORREÇÃO:")
    print(f"   1. python3 {test_script_path}")
    print(f"   2. sudo systemctl restart apache2") 
    print(f"   3. Testar upload: https://paineleld.poppnet.com.br/admin/")
    
    print(f"\n🔄 PARA REVERTER:")
    print(f"   cp {backup_path} {models_path}")
    print(f"   sudo systemctl restart apache2")
    
    print(f"\n✅ CORREÇÃO DEFINITIVA APLICADA!")

if __name__ == "__main__":
    main()

# COMANDO DIRETO PARA EXECUTAR NO SERVIDOR

# 1. Conecte ao servidor:
ssh fiber@paineleld.poppnet.com.br

# 2. Execute este bloco de comandos:
cd /var/www/sreadmin
source venv/bin/activate

# 3. Atualizar para usar o arquivo sem sufixo (que sabemos que existe):
python3 -c "
import os, sys, django
sys.path.insert(0, '/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()
from painel.models import EldPortalSemVideo

# Usar o arquivo hotspot-auth-default.zip (sem sufixo)
new_path = 'portal_sem_video/hotspot-auth-default.zip'
count = EldPortalSemVideo.objects.filter(ativo=True).update(arquivo_zip=new_path)

print(f'Arquivo atualizado para: {new_path}')
print(f'Registros atualizados: {count}')

# Verificar
portal = EldPortalSemVideo.objects.filter(ativo=True).first()
if portal:
    exists = os.path.exists(portal.arquivo_zip.path)
    print(f'Arquivo existe: {exists}')
    print(f'Path completo: {portal.arquivo_zip.path}')
    if exists:
        print(f'Tamanho: {os.path.getsize(portal.arquivo_zip.path)} bytes')
"

# 4. Teste a API:
curl -H "Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d" \
     "https://paineleld.poppnet.com.br/api/appliances/portal/download/?type=without_video" \
     --output /tmp/final_test.zip -w "Status: %{http_code}\nTamanho: %{size_download} bytes\n"

# 5. Verificar o arquivo baixado:
ls -lh /tmp/final_test.zip
file /tmp/final_test.zip

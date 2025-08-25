#!/bin/bash
# Execute este script no servidor de produção

echo "=== CORREÇÃO FINAL - USANDO SUBDIRETÓRIO ==="

cd /var/www/sreadmin
source venv/bin/activate

# Atualizar para usar arquivo do subdiretório
python3 -c "
import os, sys, django
sys.path.insert(0, '/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()
from painel.models import EldPortalSemVideo

# Usar arquivo do subdiretório portal_sem_video/portal_sem_video/
new_path = 'portal_sem_video/portal_sem_video/hotspot-auth-default.zip'
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
        size = os.path.getsize(portal.arquivo_zip.path)
        print(f'Tamanho: {size} bytes')
        print('✅ SUCESSO!')
    else:
        print('❌ ERRO: Arquivo ainda não encontrado')
"

echo ""
echo "=== TESTANDO API ==="
curl -H "Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d" \
     "https://paineleld.poppnet.com.br/api/appliances/portal/download/?type=without_video" \
     --output /tmp/test_subdirectory.zip -w "Status: %{http_code}\nTamanho: %{size_download} bytes\n"

echo ""
echo "=== RESULTADO ==="
if [ -f /tmp/test_subdirectory.zip ] && [ $(stat -c%s /tmp/test_subdirectory.zip) -gt 1000 ]; then
    echo "✅ DOWNLOAD FUNCIONOU!"
    ls -lh /tmp/test_subdirectory.zip
    file /tmp/test_subdirectory.zip
else
    echo "❌ Download ainda com problema"
    cat /tmp/test_subdirectory.zip
fi

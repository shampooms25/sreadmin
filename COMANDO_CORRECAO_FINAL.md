# COMANDO ÚNICO PARA CORREÇÃO DEFINITIVA EM PRODUÇÃO

# Execute este comando único no servidor de produção:

cd /var/www/sreadmin && source venv/bin/activate && python3 -c "
import os, sys, django
from pathlib import Path
sys.path.insert(0, '/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()
from painel.models import EldPortalSemVideo
from django.conf import settings

# Encontrar arquivo que realmente existe
base_dir = Path(settings.MEDIA_ROOT) / 'portal_sem_video'
all_zips = list(base_dir.glob('*.zip'))

if all_zips:
    # Pegar o mais recente
    latest = max(all_zips, key=lambda f: f.stat().st_mtime)
    relative_path = str(latest.relative_to(settings.MEDIA_ROOT))
    
    print(f'Arquivo encontrado: {latest.name}')
    print(f'Path relativo: {relative_path}')
    print(f'Tamanho: {latest.stat().st_size} bytes')
    
    # Atualizar banco
    count = EldPortalSemVideo.objects.filter(ativo=True).update(arquivo_zip=relative_path)
    print(f'✅ {count} portal(s) corrigido(s)')
    
    # Verificar
    portal = EldPortalSemVideo.objects.filter(ativo=True).first()
    if portal and os.path.exists(portal.arquivo_zip.path):
        print(f'✅ Verificação OK: {portal.arquivo_zip.path}')
    else:
        print(f'❌ ERRO: Arquivo ainda não acessível')
else:
    print('❌ Nenhum arquivo .zip encontrado em /var/www/sreadmin/media/portal_sem_video/')
"

# Depois, teste novamente:
curl -H "Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d" \
     "https://paineleld.poppnet.com.br/api/appliances/portal/download/?type=without_video" \
     --output /tmp/test_final.zip -w "Status: %{http_code}\nTamanho: %{size_download} bytes\n"

# PASSOS PARA CORREÇÃO EM PRODUÇÃO

## PASSO 1: Conectar ao servidor de produção
ssh root@paineleld.poppnet.com.br

## PASSO 2: Navegar para o diretório do projeto
cd /var/www/sreadmin

## PASSO 3: Criar o script de correção diretamente no servidor
cat > fix_production_portal_paths.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.insert(0, '/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo

def main():
    print("=== CORREÇÃO DE PATHS DO PORTAL SEM VÍDEO ===")
    
    # Listar arquivos reais
    media_dir = Path('/var/www/sreadmin/media/portal_sem_video')
    files = list(media_dir.glob('*.zip'))
    
    if not files:
        print("ERRO: Nenhum arquivo encontrado!")
        return
    
    # Pegar arquivo mais recente
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    relative_path = f"portal_sem_video/{latest_file.name}"
    
    print(f"Arquivo encontrado: {latest_file.name}")
    print(f"Corrigindo path para: {relative_path}")
    
    # Atualizar todos os portais ativos
    count = EldPortalSemVideo.objects.filter(ativo=True).update(
        arquivo_zip=relative_path
    )
    
    print(f"✅ {count} portal(s) corrigido(s)!")

if __name__ == '__main__':
    main()
EOF

## PASSO 4: Executar a correção
source venv/bin/activate
python3 fix_production_portal_paths.py

## PASSO 5: Testar se funcionou
curl -H "Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d" \
     "https://paineleld.poppnet.com.br/api/appliances/portal/download/?type=without_video" \
     --output /tmp/test.zip -w "Status: %{http_code}\n"

## PASSO 6: Verificar arquivo baixado
ls -lh /tmp/test.zip
file /tmp/test.zip

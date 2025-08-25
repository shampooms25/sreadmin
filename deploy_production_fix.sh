#!/bin/bash
# Script para executar correção de paths em produção

echo "=== CORREÇÃO DE PATHS DO PORTAL SEM VÍDEO - PRODUÇÃO ==="
echo "Data: $(date)"
echo ""

# Navegar para o diretório do projeto
cd /var/www/sreadmin

# Ativar ambiente virtual
source venv/bin/activate

# Executar script de correção
python3 fix_production_portal_paths.py

echo ""
echo "=== TESTANDO API APÓS CORREÇÃO ==="

# Testar status
echo "1. Testando status da API..."
curl -s -H "Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d" \
     "https://paineleld.poppnet.com.br/api/appliances/portal/status/" | python3 -m json.tool

echo ""
echo "2. Testando download da API..."
curl -H "Authorization: Bearer 884f88da2e8a947500ceb4af1dafa10d" \
     "https://paineleld.poppnet.com.br/api/appliances/portal/download/?type=without_video" \
     --output /tmp/portal_test.zip -w "\nStatus HTTP: %{http_code}\nTamanho: %{size_download} bytes\n"

# Verificar se download funcionou
if [ -f /tmp/portal_test.zip ]; then
    echo "✅ Arquivo baixado com sucesso!"
    ls -lh /tmp/portal_test.zip
    file /tmp/portal_test.zip
else
    echo "❌ Falha no download"
fi

echo ""
echo "=== CORREÇÃO FINALIZADA ==="

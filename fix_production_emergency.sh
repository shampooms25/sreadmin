#!/bin/bash
# Script de Correção Emergencial para Produção
# Força a criação do token e reinicia tudo

echo "🚨 CORREÇÃO EMERGENCIAL - Produção Ubuntu"
echo "========================================="

# Verificar diretório
if [ ! -f "manage.py" ]; then
    echo "❌ Execute no diretório /var/www/sreadmin"
    exit 1
fi

echo "🔄 1. Parando servidor Django..."
pkill -f "manage.py runserver" 2>/dev/null || echo "Nenhum processo encontrado"

echo "🔄 2. Criando token de teste forçadamente..."
python manage.py shell << 'EOF'
from captive_portal.models import ApplianceToken

# Deletar token existente se houver
ApplianceToken.objects.filter(token='c8c786467d4a8d2825eaf549534d1ab0').delete()

# Criar novo token
token = ApplianceToken.objects.create(
    token='c8c786467d4a8d2825eaf549534d1ab0',
    appliance_id='POSTMAN-TEST',
    appliance_name='Appliance Teste Postman',
    description='Token para testes via Postman - Produção Ubuntu',
    is_active=True
)

print(f"✅ Token criado: {token.token}")
print(f"✅ Appliance: {token.appliance_name}")
print(f"✅ Ativo: {token.is_active}")

# Verificar se pode ser encontrado
found = ApplianceToken.objects.get(token='c8c786467d4a8d2825eaf549534d1ab0', is_active=True)
print(f"✅ Verificação OK: {found.appliance_name}")
EOF

echo "🔄 3. Aplicando migrações..."
python manage.py migrate --verbosity=0

echo "🔄 4. Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --verbosity=0

echo "🔄 5. Ajustando permissões..."
chown -R www-data:www-data /var/www/sreadmin/ 2>/dev/null || true
chmod -R 755 /var/www/sreadmin/ 2>/dev/null || true

echo "🔄 6. Iniciando servidor Django..."
export DJANGO_SETTINGS_MODULE=sreadmin.settings
nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &

echo "Aguardando servidor iniciar..."
sleep 5

if pgrep -f "manage.py runserver" > /dev/null; then
    echo "✅ Servidor iniciado com sucesso"
else
    echo "❌ Falha ao iniciar servidor"
    echo "Log:"
    tail -10 django.log
    exit 1
fi

echo "🔄 7. Testando autenticação..."
python manage.py shell << 'EOF'
from captive_portal.api_views import ApplianceAPIAuthentication
from unittest.mock import Mock

mock_request = Mock()
mock_request.META = {
    'HTTP_AUTHORIZATION': 'Bearer c8c786467d4a8d2825eaf549534d1ab0',
    'REMOTE_ADDR': '127.0.0.1'
}

is_valid, result = ApplianceAPIAuthentication.verify_token(mock_request)

if is_valid:
    print(f"✅ Autenticação OK: {result.appliance_name}")
else:
    print(f"❌ Falha na autenticação: {result}")
EOF

echo "🔄 8. Testando API via curl..."
sleep 2

echo "Teste 1 - Sem autenticação (deve dar 401):"
curl -s -w "Status: %{http_code}\n" http://127.0.0.1:8000/api/appliances/info/

echo ""
echo "Teste 2 - Com autenticação (deve dar 200):"
curl -s -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     -w "Status: %{http_code}\n" \
     http://127.0.0.1:8000/api/appliances/info/

echo ""
echo "✅ CORREÇÃO CONCLUÍDA!"
echo ""

# Obter IP do servidor
SERVER_IP=$(hostname -I | awk '{print $1}')

echo "🌐 URLs para teste no Postman:"
echo "   http://$SERVER_IP:8000/api/appliances/info/"
echo "   http://$SERVER_IP:8000/api/appliances/portal/status/"
echo "   http://$SERVER_IP:8000/api/appliances/portal/download/?type=with_video"
echo ""
echo "🔑 Header de autenticação:"
echo "   Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0"
echo ""
echo "⚠️ IMPORTANTE:"
echo "   - Use HTTP (não HTTPS)"
echo "   - Use o IP: $SERVER_IP"
echo "   - Porta: 8000"
echo ""
echo "📊 Para monitorar:"
echo "   tail -f django.log"
echo "   ps aux | grep python"
echo ""

# Mostrar status final
if curl -s -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
        http://127.0.0.1:8000/api/appliances/info/ > /dev/null; then
    echo "🎉 API FUNCIONANDO!"
else
    echo "❌ API ainda com problemas"
    echo "Verifique os logs: tail -f django.log"
fi

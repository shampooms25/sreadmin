#!/bin/bash
# Diagnóstico e Correção para Produção Ubuntu
# Resolve problema de autenticação 401

echo "🔍 DIAGNÓSTICO COMPLETO - Produção Ubuntu"
echo "========================================="

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Execute este script no diretório /var/www/sreadmin"
    exit 1
fi

echo ""
echo "1️⃣ VERIFICANDO AMBIENTE..."
echo "Diretório atual: $(pwd)"
echo "Usuário atual: $(whoami)"
echo "Django settings: $DJANGO_SETTINGS_MODULE"

echo ""
echo "2️⃣ VERIFICANDO BANCO DE DADOS..."
python manage.py shell << 'EOF'
try:
    from captive_portal.models import ApplianceToken
    from django.db import connection
    
    print("✅ Conexão com banco OK")
    
    # Verificar tabela ApplianceToken
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM captive_portal_appliancetoken;")
        count = cursor.fetchone()[0]
        print(f"📊 Total de tokens na tabela: {count}")
    
    # Listar todos os tokens
    tokens = ApplianceToken.objects.all()
    print(f"📋 Tokens encontrados via Django ORM: {tokens.count()}")
    
    for token in tokens:
        print(f"   - {token.token[:20]}... | {token.appliance_name} | Ativo: {token.is_active}")
    
    # Verificar token específico
    test_token = 'c8c786467d4a8d2825eaf549534d1ab0'
    try:
        token_obj = ApplianceToken.objects.get(token=test_token)
        print(f"✅ Token de teste encontrado: {token_obj.appliance_name} - Ativo: {token_obj.is_active}")
    except ApplianceToken.DoesNotExist:
        print(f"❌ Token de teste NÃO encontrado: {test_token}")
        
        # Criar o token
        print("🔧 Criando token de teste...")
        new_token = ApplianceToken.objects.create(
            token=test_token,
            appliance_id='POSTMAN-TEST',
            appliance_name='Appliance Teste Postman',
            description='Token para testes via Postman - Produção',
            is_active=True
        )
        print(f"✅ Token criado: {new_token.appliance_name}")
        
except Exception as e:
    print(f"❌ Erro no banco de dados: {e}")
    import traceback
    traceback.print_exc()
EOF

echo ""
echo "3️⃣ VERIFICANDO AUTENTICAÇÃO..."
python manage.py shell << 'EOF'
from captive_portal.api_views import ApplianceAPIAuthentication
from unittest.mock import Mock

# Simular request
mock_request = Mock()
mock_request.META = {
    'HTTP_AUTHORIZATION': 'Bearer c8c786467d4a8d2825eaf549534d1ab0',
    'REMOTE_ADDR': '127.0.0.1'
}

print("🧪 Testando autenticação...")
print(f"Authorization header: {mock_request.META['HTTP_AUTHORIZATION']}")

try:
    is_valid, result = ApplianceAPIAuthentication.verify_token(mock_request)
    
    if is_valid:
        print(f"✅ Autenticação OK!")
        print(f"   - Appliance ID: {result.username}")
        print(f"   - Appliance Name: {result.appliance_name}")
        print(f"   - Is Authenticated: {result.is_authenticated}")
    else:
        print(f"❌ Falha na autenticação: {result}")
        
except Exception as e:
    print(f"❌ Erro na autenticação: {e}")
    import traceback
    traceback.print_exc()
EOF

echo ""
echo "4️⃣ VERIFICANDO SERVIDOR..."
if pgrep -f "manage.py runserver" > /dev/null; then
    echo "✅ Servidor Django está rodando"
    echo "Processos encontrados:"
    ps aux | grep "manage.py runserver" | grep -v grep
else
    echo "❌ Servidor Django NÃO está rodando"
    echo "🔧 Iniciando servidor..."
    
    # Parar qualquer processo existente
    pkill -f "manage.py runserver" 2>/dev/null || true
    
    # Iniciar servidor
    nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
    sleep 3
    
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo "✅ Servidor iniciado com sucesso"
    else
        echo "❌ Falha ao iniciar servidor"
        echo "Log do servidor:"
        tail -20 django.log
    fi
fi

echo ""
echo "5️⃣ VERIFICANDO CONECTIVIDADE..."
echo "Testando localhost..."
curl -s -w "Status Code: %{http_code}\n" -o /dev/null http://127.0.0.1:8000/admin/ || echo "❌ Conexão falhou"

echo ""
echo "6️⃣ TESTANDO API..."
echo "Testando endpoint sem autenticação..."
curl -s -w "Status Code: %{http_code}\n" -o /tmp/api_test.json http://127.0.0.1:8000/api/appliances/info/
echo "Resposta:"
cat /tmp/api_test.json 2>/dev/null || echo "Sem resposta"

echo ""
echo "Testando endpoint com autenticação..."
curl -s -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     -w "Status Code: %{http_code}\n" \
     -o /tmp/api_auth_test.json \
     http://127.0.0.1:8000/api/appliances/info/

echo "Resposta com auth:"
cat /tmp/api_auth_test.json 2>/dev/null || echo "Sem resposta"

echo ""
echo "7️⃣ VERIFICANDO LOGS..."
if [ -f "django.log" ]; then
    echo "Últimas 10 linhas do log Django:"
    tail -10 django.log
fi

echo ""
echo "8️⃣ VERIFICANDO CONFIGURAÇÕES..."
python manage.py shell << 'EOF'
from django.conf import settings
import os

print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"BASE_DIR: {settings.BASE_DIR}")

# Verificar se arquivo appliance_tokens.json existe
json_file = os.path.join(settings.BASE_DIR, 'appliance_tokens.json')
print(f"appliance_tokens.json existe: {os.path.exists(json_file)}")

if os.path.exists(json_file):
    try:
        with open(json_file, 'r') as f:
            import json
            data = json.load(f)
            tokens_count = len(data.get('tokens', {}))
            print(f"Tokens no JSON: {tokens_count}")
    except Exception as e:
        print(f"Erro ao ler JSON: {e}")
EOF

echo ""
echo "9️⃣ INFORMAÇÕES DO SISTEMA..."
echo "IP do servidor: $(hostname -I | awk '{print $1}')"
echo "Porta 8000 em uso:"
netstat -tlnp | grep :8000 || echo "Porta 8000 não está sendo usada"

echo ""
echo "🔟 CORREÇÕES AUTOMÁTICAS..."

# Ajustar permissões
echo "Ajustando permissões..."
chown -R www-data:www-data /var/www/sreadmin/ 2>/dev/null || echo "⚠️ Não foi possível ajustar owner"
chmod -R 755 /var/www/sreadmin/ 2>/dev/null || echo "⚠️ Não foi possível ajustar permissões"

# Aplicar migrações
echo "Verificando migrações..."
python manage.py migrate --check 2>/dev/null || {
    echo "Aplicando migrações..."
    python manage.py migrate
}

echo ""
echo "✅ DIAGNÓSTICO CONCLUÍDO!"
echo ""
echo "🌐 URLs para teste externo:"
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "   http://$SERVER_IP:8000/api/appliances/info/"
echo "   http://$SERVER_IP:8000/admin/"
echo ""
echo "🔑 Token para teste:"
echo "   Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0"
echo ""
echo "📋 Próximos passos se ainda não funcionar:"
echo "   1. Verifique firewall: sudo ufw status"
echo "   2. Abra porta 8000: sudo ufw allow 8000"
echo "   3. Verifique se o IP está correto no Postman"
echo "   4. Use HTTP (não HTTPS): http://$SERVER_IP:8000"
echo "   5. Veja logs em tempo real: tail -f django.log"

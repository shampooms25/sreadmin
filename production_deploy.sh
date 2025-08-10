#!/bin/bash
# Script de Deploy para Produção - Linux
# Resolve problemas de migração e configura ambiente

echo "🚀 Deploy de Produção - POPPFIRE Sistema"
echo "========================================"

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto Django"
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "🔄 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Instalar dependências necessárias
echo "📦 Verificando dependências..."
pip install Pillow --quiet
pip install requests --quiet

# Fazer backup do banco (apenas estrutura)
echo "💾 Criando backup da estrutura do banco..."
python manage.py dumpdata --natural-foreign --natural-primary \
    captive_portal.ApplianceToken > backup_tokens.json 2>/dev/null || echo "⚠️ Nenhum token para backup"

# Resolver conflitos de migração
echo "🔧 Resolvendo conflitos de migração..."

# Marcar migrações como aplicadas para tabelas existentes
python manage.py shell << 'EOF'
from django.db import connection

with connection.cursor() as cursor:
    # Verificar tabelas existentes
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'eld_%';
    """)
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    if existing_tables:
        print(f"Tabelas ELD existentes: {existing_tables}")
        # Marcar migração inicial como aplicada
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied) 
            VALUES ('captive_portal', '0001_initial', NOW()) 
            ON CONFLICT (app, name) DO NOTHING;
        """)
        print("✅ Migração 0001_initial marcada como aplicada")
    
    # Verificar tabela ApplianceToken
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'captive_portal_appliancetoken'
        );
    """)
    
    if cursor.fetchone()[0]:
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied) 
            VALUES ('captive_portal', '0004_appliancetoken', NOW()) 
            ON CONFLICT (app, name) DO NOTHING;
        """)
        print("✅ Migração 0004_appliancetoken marcada como aplicada")
EOF

# Tentar executar migrações
echo "🚀 Executando migrações..."
if python manage.py migrate --fake-initial; then
    echo "✅ Migrações aplicadas com sucesso!"
else
    echo "⚠️ Erro nas migrações, tentando alternativa..."
    python manage.py migrate captive_portal --fake
    python manage.py migrate
fi

# Coletar arquivos estáticos
echo "📂 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Verificar se sistema está funcionando
echo "🔍 Verificando sistema..."
python manage.py shell << 'EOF'
try:
    from captive_portal.models import ApplianceToken
    count = ApplianceToken.objects.count()
    print(f"✅ Sistema funcionando - {count} tokens cadastrados")
    
    # Testar admin
    from django.contrib.admin.sites import site
    print(f"✅ Admin OK - {len(site._registry)} modelos registrados")
    
    # Verificar API
    from captive_portal.api_views import api_info
    print("✅ API disponível")
    
except Exception as e:
    print(f"⚠️ Erro no sistema: {e}")
EOF

# Restaurar tokens se backup existe
if [ -f "backup_tokens.json" ]; then
    echo "🔄 Restaurando tokens do backup..."
    python manage.py loaddata backup_tokens.json || echo "⚠️ Erro ao restaurar tokens"
fi

# Sincronizar tokens do JSON se existe
if [ -f "appliance_tokens.json" ]; then
    echo "🔄 Sincronizando tokens do arquivo JSON..."
    python manage.py shell << 'EOF'
import json
import os
from captive_portal.models import ApplianceToken
from django.utils import timezone

if os.path.exists('appliance_tokens.json'):
    with open('appliance_tokens.json', 'r') as f:
        data = json.load(f)
    
    tokens_data = data.get('tokens', {})
    created_count = 0
    
    for token, info in tokens_data.items():
        obj, created = ApplianceToken.objects.get_or_create(
            token=token,
            defaults={
                'appliance_id': info['appliance_id'],
                'appliance_name': info['appliance_name'],
                'description': info['description'],
                'is_active': True,
            }
        )
        if created:
            created_count += 1
            print(f"Token criado: {info['appliance_name']}")
    
    print(f"✅ {created_count} tokens sincronizados")
EOF
fi

# Verificações finais
echo ""
echo "🎯 Verificações Finais:"
echo "====================="

# Verificar se servidor está rodando
if pgrep -f "manage.py runserver" > /dev/null; then
    echo "✅ Servidor Django está rodando"
else
    echo "⚠️ Servidor Django não está rodando"
    echo "   Para iniciar: python manage.py runserver 0.0.0.0:8000"
fi

# Verificar permissões de media
if [ -d "media" ]; then
    echo "✅ Diretório media existe"
    chmod -R 755 media/ 2>/dev/null || echo "⚠️ Não foi possível ajustar permissões do media"
else
    echo "⚠️ Diretório media não existe - criando..."
    mkdir -p media/videos media/uploads
    chmod -R 755 media/
fi

# URLs importantes
echo ""
echo "🌐 URLs Importantes:"
echo "==================="
echo "   Admin: http://seu-servidor:8000/admin/"
echo "   API Info: http://seu-servidor:8000/api/appliances/info/"
echo "   Portal Status: http://seu-servidor:8000/api/appliances/portal/status/"
echo "   Tokens: http://seu-servidor:8000/admin/captive_portal/appliancetoken/"

echo ""
echo "🎉 Deploy concluído!"
echo ""
echo "🔧 Próximos passos:"
echo "   1. Verificar se o servidor Django está rodando"
echo "   2. Testar acesso ao admin"
echo "   3. Verificar APIs com curl ou browser"
echo "   4. Configurar OpnSense com os scripts fornecidos"
echo ""

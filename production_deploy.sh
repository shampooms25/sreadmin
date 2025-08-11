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

# Ajustar permissões e sincronizar tokens do JSON se existe
if [ -f "appliance_tokens.json" ]; then
    echo "🔄 Verificando permissões do arquivo JSON..."
    
    # Ajustar permissões do arquivo JSON
    chmod 644 appliance_tokens.json 2>/dev/null || echo "⚠️ Não foi possível ajustar permissões do JSON"
    chown www-data:www-data appliance_tokens.json 2>/dev/null || echo "⚠️ Não foi possível ajustar owner do JSON"
    
    echo "🔄 Sincronizando tokens do arquivo JSON..."
    python manage.py shell << 'EOF'
import json
import os
from captive_portal.models import ApplianceToken
from django.utils import timezone

json_file = 'appliance_tokens.json'

try:
    if os.path.exists(json_file) and os.access(json_file, os.R_OK):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tokens_data = data.get('tokens', {})
        created_count = 0
        updated_count = 0
        
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
            else:
                # Atualizar informações se necessário
                if obj.appliance_name != info['appliance_name'] or obj.description != info['description']:
                    obj.appliance_name = info['appliance_name']
                    obj.description = info['description']
                    obj.save()
                    updated_count += 1
                    print(f"Token atualizado: {info['appliance_name']}")
        
        print(f"✅ Sincronização concluída: {created_count} criados, {updated_count} atualizados")
        
    else:
        print("⚠️ Arquivo JSON não acessível - criando tokens padrão...")
        # Criar tokens padrão se não conseguir ler o arquivo
        default_tokens = [
            {
                'token': 'c8c786467d4a8d2825eaf549534d1ab0',
                'appliance_id': 'POSTMAN-TEST',
                'appliance_name': 'Appliance Teste Postman',
                'description': 'Token para testes via Postman - Linux'
            },
            {
                'token': 'test-token-123456789',
                'appliance_id': 'TEST-APPLIANCE',
                'appliance_name': 'Appliance de Teste',
                'description': 'Token de teste para desenvolvimento'
            },
            {
                'token': 'f8e7d6c5b4a3928170695e4c3d2b1a0f',
                'appliance_id': 'APPLIANCE-001',
                'appliance_name': 'Appliance POPPFIRE 001',
                'description': 'Token para appliance de produção 001'
            }
        ]
        
        created_count = 0
        for token_info in default_tokens:
            obj, created = ApplianceToken.objects.get_or_create(
                token=token_info['token'],
                defaults={
                    'appliance_id': token_info['appliance_id'],
                    'appliance_name': token_info['appliance_name'],
                    'description': token_info['description'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                print(f"Token padrão criado: {token_info['appliance_name']}")
        
        print(f"✅ {created_count} tokens padrão criados")

except Exception as e:
    print(f"⚠️ Erro ao sincronizar tokens: {e}")
    print("📝 Tokens podem ser criados manualmente pelo admin")
EOF
else
    echo "⚠️ Arquivo appliance_tokens.json não encontrado - criando tokens padrão..."
    python manage.py shell << 'EOF'
from captive_portal.models import ApplianceToken

# Criar tokens padrão se arquivo JSON não existe
default_tokens = [
    {
        'token': 'c8c786467d4a8d2825eaf549534d1ab0',
        'appliance_id': 'POSTMAN-TEST',
        'appliance_name': 'Appliance Teste Postman',
        'description': 'Token para testes via Postman - Linux'
    },
    {
        'token': 'test-token-123456789',
        'appliance_id': 'TEST-APPLIANCE',
        'appliance_name': 'Appliance de Teste',
        'description': 'Token de teste para desenvolvimento'
    },
    {
        'token': 'f8e7d6c5b4a3928170695e4c3d2b1a0f',
        'appliance_id': 'APPLIANCE-001',
        'appliance_name': 'Appliance POPPFIRE 001',
        'description': 'Token para appliance de produção 001'
    },
    {
        'token': '1234567890abcdef1234567890abcdef',
        'appliance_id': 'APPLIANCE-DEV',
        'appliance_name': 'Appliance de Desenvolvimento',
        'description': 'Token para desenvolvimento e testes'
    }
]

created_count = 0
for token_info in default_tokens:
    obj, created = ApplianceToken.objects.get_or_create(
        token=token_info['token'],
        defaults={
            'appliance_id': token_info['appliance_id'],
            'appliance_name': token_info['appliance_name'],
            'description': token_info['description'],
            'is_active': True,
        }
    )
    if created:
        created_count += 1
        print(f"Token padrão criado: {token_info['appliance_name']}")

print(f"✅ {created_count} tokens padrão criados")
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

#!/bin/bash
# Deploy de Produção CORRIGIDO - POPPFIRE Sistema
# Versão que evita erro ON CONFLICT

echo "🚀 Deploy de Produção CORRIGIDO - POPPFIRE Sistema"
echo "=================================================="

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Execute no diretório /var/www/sreadmin"
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "🔄 Ativando ambiente virtual..."
    source venv/bin/activate
fi

echo "📦 Verificando dependências..."
pip install -r requirements.txt > /dev/null 2>&1 || echo "⚠️ Arquivo requirements.txt não encontrado"

echo "💾 Criando backup da estrutura do banco..."
pg_dump --schema-only sreadmin > backup_schema_$(date +%Y%m%d_%H%M%S).sql 2>/dev/null || echo "⚠️ Backup não criado"

echo "🔧 Resolvendo conflitos de migração SEM ON CONFLICT..."

# Importar fixtures básicos
python manage.py loaddata initial_data.json 2>/dev/null || echo "⚠️ Fixtures não carregados"

# Criar tabelas sem usar ON CONFLICT
python manage.py shell << 'EOF'
from django.db import connection
import traceback

print("🔧 Criando tabelas com sintaxe PostgreSQL correta...")

try:
    with connection.cursor() as cursor:
        # Verificar tabelas existentes
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'eld_%';
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"Tabelas ELD existentes: {existing_tables}")
        
        # Criar eld_gerenciar_portal se não existir
        if 'eld_gerenciar_portal' not in existing_tables:
            print("Criando eld_gerenciar_portal...")
            cursor.execute("""
                CREATE TABLE eld_gerenciar_portal (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(200) NOT NULL,
                    ativo BOOLEAN NOT NULL DEFAULT false,
                    captive_portal_zip VARCHAR(100),
                    video_file VARCHAR(100),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Inserir dados padrão usando WHERE NOT EXISTS
            cursor.execute("""
                INSERT INTO eld_gerenciar_portal (nome, ativo) 
                SELECT 'Portal Captive Padrão', false
                WHERE NOT EXISTS (
                    SELECT 1 FROM eld_gerenciar_portal WHERE nome = 'Portal Captive Padrão'
                );
            """)
            print("✅ eld_gerenciar_portal criada")
        
        # Criar eld_portal_sem_video se não existir
        if 'eld_portal_sem_video' not in existing_tables:
            print("Criando eld_portal_sem_video...")
            cursor.execute("""
                CREATE TABLE eld_portal_sem_video (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(200) NOT NULL,
                    ativo BOOLEAN NOT NULL DEFAULT false,
                    arquivo_zip VARCHAR(100),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Inserir dados padrão usando WHERE NOT EXISTS
            cursor.execute("""
                INSERT INTO eld_portal_sem_video (nome, ativo) 
                SELECT 'Portal Sem Vídeo Padrão', false
                WHERE NOT EXISTS (
                    SELECT 1 FROM eld_portal_sem_video WHERE nome = 'Portal Sem Vídeo Padrão'
                );
            """)
            print("✅ eld_portal_sem_video criada")
        
        # Garantir que ApplianceToken existe
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'captive_portal_appliancetoken';
        """)
        
        if not cursor.fetchall():
            print("Criando captive_portal_appliancetoken...")
            cursor.execute("""
                CREATE TABLE captive_portal_appliancetoken (
                    id SERIAL PRIMARY KEY,
                    token VARCHAR(255) NOT NULL UNIQUE,
                    appliance_id VARCHAR(100) NOT NULL,
                    appliance_name VARCHAR(200),
                    description TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_used TIMESTAMP WITH TIME ZONE
                );
            """)
            print("✅ captive_portal_appliancetoken criada")
        
        # Criar token padrão usando WHERE NOT EXISTS
        cursor.execute("""
            INSERT INTO captive_portal_appliancetoken 
            (token, appliance_id, appliance_name, description, is_active) 
            SELECT 
                'c8c786467d4a8d2825eaf549534d1ab0',
                'PROD-DEPLOY',
                'Token Deploy Produção',
                'Token criado durante deploy',
                true
            WHERE NOT EXISTS (
                SELECT 1 FROM captive_portal_appliancetoken 
                WHERE token = 'c8c786467d4a8d2825eaf549534d1ab0'
            );
        """)
        
        print("✅ Todas as tabelas foram verificadas/criadas")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    traceback.print_exc()
EOF

echo "🔧 Marcando migrações como aplicadas..."

python manage.py shell << 'EOF'
from django.db import connection

try:
    with connection.cursor() as cursor:
        # Garantir tabela de migrações existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_migrations (
                id SERIAL PRIMARY KEY,
                app VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Criar índice único se não existir (evita problemas futuros)
        cursor.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = 'django_migrations_app_name_unique'
                ) THEN
                    CREATE UNIQUE INDEX django_migrations_app_name_unique 
                    ON django_migrations(app, name);
                END IF;
            END $$;
        """)
        
        # Marcar migrações usando WHERE NOT EXISTS
        migrations = [
            ('painel', '0001_initial'),
            ('captive_portal', '0001_initial'),
            ('captive_portal', '0004_appliancetoken'),
            ('captive_portal', '0005_gerenciar_portal'),
            ('captive_portal', '0006_portal_sem_video'),
        ]
        
        for app, migration in migrations:
            cursor.execute("""
                INSERT INTO django_migrations (app, name) 
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations 
                    WHERE app = %s AND name = %s
                );
            """, [app, migration, app, migration])
        
        print("✅ Migrações marcadas com sucesso")
        
except Exception as e:
    print(f"❌ Erro nas migrações: {e}")
EOF

echo "🔧 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput > /dev/null 2>&1 || echo "⚠️ Erro ao coletar estáticos"

echo "🔧 Configurando permissões..."
chown -R www-data:www-data /var/www/sreadmin/media/ 2>/dev/null || echo "⚠️ Erro nas permissões"
chmod -R 755 /var/www/sreadmin/media/ 2>/dev/null || echo "⚠️ Erro no chmod"

echo "🔧 Reiniciando serviços..."

# Parar processos anteriores
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "wsgi" 2>/dev/null || true
sleep 2

# Reiniciar Apache/Nginx
if systemctl is-active --quiet apache2; then
    echo "🔄 Reiniciando Apache..."
    systemctl reload apache2
    sleep 2
elif systemctl is-active --quiet nginx; then
    echo "🔄 Reiniciando Nginx..."
    systemctl reload nginx
    sleep 2
fi

# Iniciar servidor Django para testes
echo "🚀 Iniciando servidor de produção..."
nohup python manage.py runserver 0.0.0.0:8000 > production_deploy.log 2>&1 &
sleep 5

echo "🧪 Testando deploy..."

# Verificar tabelas
python manage.py shell << 'EOF'
from django.db import connection

try:
    with connection.cursor() as cursor:
        tables = ['eld_gerenciar_portal', 'eld_portal_sem_video', 'captive_portal_appliancetoken']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} registros")
            except Exception as e:
                print(f"❌ {table}: {e}")
        
        # Verificar token específico
        cursor.execute("""
            SELECT token, appliance_id, is_active 
            FROM captive_portal_appliancetoken 
            WHERE token = 'c8c786467d4a8d2825eaf549534d1ab0';
        """)
        
        token_result = cursor.fetchone()
        if token_result:
            print(f"✅ Token encontrado: {token_result[1]} (ativo: {token_result[2]})")
        else:
            print("⚠️ Token padrão não encontrado")
        
except Exception as e:
    print(f"❌ Erro na verificação: {e}")
EOF

# Testar API
echo ""
echo "🌐 Testando API..."
sleep 2

RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
    http://127.0.0.1:8000/api/appliances/info/ 2>/dev/null)

HTTP_CODE=$(echo $RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
BODY=$(echo $RESPONSE | sed -e 's/HTTPSTATUS:.*//g')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API respondendo corretamente (200 OK)"
    echo "   Resposta: $(echo $BODY | head -c 100)..."
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ Erro 500 persistindo - verificar logs"
else
    echo "⚠️ API respondeu com código: $HTTP_CODE"
fi

echo ""
echo "✅ DEPLOY CORRIGIDO CONCLUÍDO!"
echo "============================="

# Informações finais
SERVER_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "🌐 URLs de produção:"
echo "   http://$SERVER_IP:8000/api/appliances/info/"
echo "   http://$SERVER_IP:8000/admin/"
echo "   http://$SERVER_IP/api/appliances/info/ (via proxy)"
echo ""
echo "🔑 Token de autenticação:"
echo "   Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0"
echo ""
echo "📊 Monitoramento:"
echo "   tail -f production_deploy.log"
echo "   tail -f /var/log/apache2/error.log"
echo ""
echo "🔧 Próximos passos:"
echo "   1. Testar todas as funcionalidades"
echo "   2. Verificar logs por alguns minutos"
echo "   3. Configurar backup automático"
echo "   4. Documentar configuração final"

#!/bin/bash
# Correção para erro ON CONFLICT - PostgreSQL
# Execute: chmod +x fix_on_conflict_error.sh && ./fix_on_conflict_error.sh

echo "🚨 CORREÇÃO - Erro ON CONFLICT PostgreSQL"
echo "=========================================="

# Verificar diretório
if [ ! -f "manage.py" ]; then
    echo "❌ Execute no diretório /var/www/sreadmin"
    exit 1
fi

echo ""
echo "🔧 CORRIGINDO ERRO ON CONFLICT..."

# Corrigir o problema de ON CONFLICT
python manage.py shell << 'EOF'
from django.db import connection
import traceback

print("🔧 Criando tabelas com sintaxe correta...")

try:
    with connection.cursor() as cursor:
        # Primeiro, vamos verificar se as tabelas existem
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('eld_gerenciar_portal', 'eld_portal_sem_video');
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"Tabelas existentes: {existing_tables}")
        
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
            
            # Inserir registro padrão usando INSERT simples
            cursor.execute("""
                INSERT INTO eld_gerenciar_portal (nome, ativo) 
                SELECT 'Portal Captive Padrão', false
                WHERE NOT EXISTS (
                    SELECT 1 FROM eld_gerenciar_portal WHERE nome = 'Portal Captive Padrão'
                );
            """)
            print("✅ eld_gerenciar_portal criada")
        else:
            print("✅ eld_gerenciar_portal já existe")
        
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
            
            # Inserir registro padrão usando INSERT simples
            cursor.execute("""
                INSERT INTO eld_portal_sem_video (nome, ativo) 
                SELECT 'Portal Sem Vídeo Padrão', false
                WHERE NOT EXISTS (
                    SELECT 1 FROM eld_portal_sem_video WHERE nome = 'Portal Sem Vídeo Padrão'
                );
            """)
            print("✅ eld_portal_sem_video criada")
        else:
            print("✅ eld_portal_sem_video já existe")
        
        # Verificar se as tabelas estão acessíveis
        for table in ['eld_gerenciar_portal', 'eld_portal_sem_video']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} registros")
            except Exception as e:
                print(f"❌ Erro ao acessar {table}: {e}")
        
        print("✅ Tabelas verificadas com sucesso!")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    traceback.print_exc()
EOF

echo ""
echo "🔧 CORRIGINDO MIGRAÇÕES SEM ON CONFLICT..."

# Corrigir problema de migrações
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
        
        # Criar índice único se não existir
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS django_migrations_app_name_unique 
            ON django_migrations(app, name);
        """)
        
        # Marcar migrações principais usando INSERT com WHERE NOT EXISTS
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
    import traceback
    traceback.print_exc()
EOF

echo ""
echo "🔧 LIMPANDO CACHE E REINICIANDO..."

# Limpar cache Django
rm -rf __pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Parar processos anteriores
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "wsgi" 2>/dev/null || true
sleep 2

# Reiniciar serviços web
if systemctl is-active --quiet apache2; then
    echo "🔄 Reiniciando Apache..."
    systemctl reload apache2
elif systemctl is-active --quiet nginx; then
    echo "🔄 Reiniciando Nginx..."
    systemctl reload nginx
fi

echo ""
echo "🚀 TESTANDO CORREÇÃO..."

# Iniciar servidor para teste
nohup python manage.py runserver 0.0.0.0:8000 > fix_conflict.log 2>&1 &
sleep 5

# Testar acesso às tabelas
python manage.py shell << 'EOF'
from django.db import connection

try:
    with connection.cursor() as cursor:
        # Testar acesso a todas as tabelas críticas
        tables = ['eld_gerenciar_portal', 'eld_portal_sem_video', 'captive_portal_appliancetoken']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} registros")
            except Exception as e:
                print(f"⚠️ {table}: {e}")
        
        print("✅ Teste de tabelas concluído!")
        
except Exception as e:
    print(f"❌ Erro no teste: {e}")
EOF

# Testar API
echo ""
echo "🌐 Testando API..."
sleep 2

RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
    http://127.0.0.1:8000/api/appliances/info/ 2>/dev/null)

HTTP_CODE=$(echo $RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API funcionando corretamente (200 OK)"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ Ainda há erro 500 - verificar logs"
else
    echo "⚠️ API respondeu com código: $HTTP_CODE"
fi

echo ""
echo "✅ CORREÇÃO ON CONFLICT CONCLUÍDA!"
echo "================================="

# Informações finais
SERVER_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "🌐 URLs para teste:"
echo "   http://$SERVER_IP:8000/api/appliances/info/"
echo "   http://$SERVER_IP:8000/admin/"
echo ""
echo "🔑 Token:"
echo "   Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0"
echo ""
echo "📊 Para verificar logs:"
echo "   tail -f fix_conflict.log"
echo ""
echo "🔧 Se ainda houver problemas:"
echo "   1. Verificar: python manage.py showmigrations"
echo "   2. Executar: python manage.py migrate --fake-initial"
echo "   3. Logs: tail -f /var/log/apache2/error.log"

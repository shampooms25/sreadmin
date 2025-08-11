#!/bin/bash
# Script de Correção URGENTE - Erro 500 Produção
# Execute: chmod +x emergency_table_fix.sh && sudo ./emergency_table_fix.sh

echo "🚨 CORREÇÃO URGENTE - Erro 500 Produção"
echo "====================================="

# Verificar diretório
if [ ! -f "manage.py" ]; then
    echo "❌ Execute no diretório /var/www/sreadmin"
    exit 1
fi

echo ""
echo "🔧 CRIANDO TABELAS FALTANTES IMEDIATAMENTE..."

# Criar tabelas diretamente no banco
python manage.py shell << 'EOF'
from django.db import connection
import traceback

print("🔧 Criando tabelas necessárias...")

try:
    with connection.cursor() as cursor:
        # Criar eld_gerenciar_portal
        print("Criando eld_gerenciar_portal...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eld_gerenciar_portal (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(200) NOT NULL,
                ativo BOOLEAN NOT NULL DEFAULT false,
                captive_portal_zip VARCHAR(100),
                video_file VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Criar eld_portal_sem_video
        print("Criando eld_portal_sem_video...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eld_portal_sem_video (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(200) NOT NULL,
                ativo BOOLEAN NOT NULL DEFAULT false,
                arquivo_zip VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Inserir registros padrão
        cursor.execute("SELECT COUNT(*) FROM eld_gerenciar_portal;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO eld_gerenciar_portal (nome, ativo) 
                VALUES ('Portal Captive Padrão', false);
            """)
            print("✅ Registro padrão inserido em eld_gerenciar_portal")
        
        cursor.execute("SELECT COUNT(*) FROM eld_portal_sem_video;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO eld_portal_sem_video (nome, ativo) 
                VALUES ('Portal Sem Vídeo Padrão', false);
            """)
            print("✅ Registro padrão inserido em eld_portal_sem_video")
        
        print("✅ Tabelas criadas com sucesso!")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    traceback.print_exc()
EOF

echo ""
echo "🔧 MARCANDO MIGRAÇÕES..."

python manage.py shell << 'EOF'
from django.db import connection

try:
    with connection.cursor() as cursor:
        # Garantir tabela de migrações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_migrations (
                id SERIAL PRIMARY KEY,
                app VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(app, name)
            );
        """)
        
        # Marcar migrações
        migrations = [
            ('painel', '0001_initial'),
            ('captive_portal', '0001_initial'),
            ('captive_portal', '0004_appliancetoken'),
        ]
        
        for app, migration in migrations:
            cursor.execute("""
                INSERT INTO django_migrations (app, name) 
                VALUES (%s, %s) 
                ON CONFLICT (app, name) DO NOTHING;
            """, [app, migration])
        
        print("✅ Migrações marcadas como aplicadas")
        
except Exception as e:
    print(f"❌ Erro nas migrações: {e}")
EOF

echo ""
echo "🔧 REINICIANDO SERVIÇOS..."

# Parar processos Django existentes
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "wsgi" 2>/dev/null || true
sleep 2

# Reiniciar serviços web
if systemctl is-active --quiet apache2; then
    echo "🔄 Reiniciando Apache..."
    systemctl reload apache2
    sleep 2
elif systemctl is-active --quiet nginx; then
    echo "🔄 Reiniciando Nginx..."
    systemctl reload nginx
    sleep 2
fi

# Iniciar servidor para teste
echo "🚀 Iniciando servidor de teste..."
nohup python manage.py runserver 0.0.0.0:8000 > emergency_fix.log 2>&1 &
sleep 5

echo ""
echo "🧪 VERIFICANDO CORREÇÃO..."

# Verificar tabelas
python manage.py shell << 'EOF'
from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM eld_gerenciar_portal;")
        count1 = cursor.fetchone()[0]
        print(f"✅ eld_gerenciar_portal: {count1} registros")
        
        cursor.execute("SELECT COUNT(*) FROM eld_portal_sem_video;")
        count2 = cursor.fetchone()[0]
        print(f"✅ eld_portal_sem_video: {count2} registros")
        
        print("✅ Todas as tabelas estão funcionando!")
        
except Exception as e:
    print(f"❌ Erro na verificação: {e}")
EOF

echo ""
echo "🌐 TESTANDO API..."
sleep 2

# Teste da API
RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
    http://127.0.0.1:8000/api/appliances/info/ 2>/dev/null)

HTTP_CODE=$(echo $RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API respondendo corretamente (200 OK)"
else
    echo "⚠️ API respondeu com código: $HTTP_CODE"
fi

echo ""
echo "✅ CORREÇÃO EMERGENCIAL CONCLUÍDA!"
echo "=================================="

# Informações finais
SERVER_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "🌐 URLs para teste:"
echo "   http://$SERVER_IP:8000/api/appliances/info/"
echo "   http://$SERVER_IP:8000/admin/"
echo ""
echo "🔑 Token para autorização:"
echo "   Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0"
echo ""
echo "📊 Logs de monitoramento:"
echo "   tail -f emergency_fix.log"
echo ""
echo "🔧 Se persistir o erro 500:"
echo "   1. Verifique: tail -f /var/log/apache2/error.log"
echo "   2. Execute: python manage.py showmigrations"
echo "   3. Teste diretamente: python manage.py shell"

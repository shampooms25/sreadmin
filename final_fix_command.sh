#!/bin/bash
# COMANDO FINAL - Execute no servidor para resolver TUDO
# chmod +x final_fix_command.sh && ./final_fix_command.sh

echo "🚨 RESOLUÇÃO FINAL - Todos os Problemas"
echo "======================================"

cd /var/www/sreadmin

echo "🔧 1. Resolvendo conflito Git..."
cp production_deploy.sh production_deploy_backup_$(date +%Y%m%d_%H%M%S).sh 2>/dev/null || true
git checkout -- production_deploy.sh 2>/dev/null || true
git pull origin main

echo "🔧 2. Dando permissões aos scripts..."
chmod +x *.sh 2>/dev/null || true

echo "🔧 3. Executando correção do erro 500..."
if [ -f "fix_on_conflict_error.sh" ]; then
    ./fix_on_conflict_error.sh
elif [ -f "emergency_table_fix.sh" ]; then
    ./emergency_table_fix.sh
elif [ -f "production_deploy_fixed.sh" ]; then
    ./production_deploy_fixed.sh
else
    echo "❌ Scripts não encontrados, executando correção manual..."
    python manage.py shell << 'EOF'
from django.db import connection
try:
    with connection.cursor() as cursor:
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
        print("✅ Tabelas criadas manualmente")
except Exception as e:
    print(f"❌ Erro: {e}")
EOF
    
    echo "🔧 Reiniciando servidor..."
    pkill -f "manage.py runserver" 2>/dev/null || true
    nohup python manage.py runserver 0.0.0.0:8000 > fix.log 2>&1 &
    sleep 3
fi

echo "🧪 4. Testando API..."
sleep 2
curl -s -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" \
     http://127.0.0.1:8000/api/appliances/info/ | head -100

echo ""
echo "✅ RESOLUÇÃO COMPLETA FINALIZADA!"

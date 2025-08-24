#!/bin/bash
echo "=== CORREÇÃO EMERGENCIAL VIA SQL ==="
echo "Descobrindo nome correto da tabela..."

# Primeiro descobrir o nome da tabela
python << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection
from painel.models import EldPortalSemVideo

# Descobrir nome da tabela
table_name = EldPortalSemVideo._meta.db_table
print(f"Nome correto da tabela: {table_name}")

# Listar todas as tabelas para confirmar
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%portal%'
        ORDER BY table_name;
    """)
    
    print("\nTabelas relacionadas a portal:")
    for row in cursor.fetchall():
        print(f"  {row[0]}")

# Agora executar a correção com o nome correto
try:
    print(f"\n=== ANTES DA CORREÇÃO ===")
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id, nome, arquivo_zip FROM {table_name} WHERE ativo = true;")
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Nome: {row[1]}, Arquivo: '{row[2]}' (len={len(row[2])})")
    
    print(f"\n=== EXECUTANDO CORREÇÃO ===")
    with connection.cursor() as cursor:
        cursor.execute(f"""
            UPDATE {table_name} 
            SET arquivo_zip = TRIM(REPLACE(arquivo_zip, 'portal_sem_video/portal_sem_video/', 'portal_sem_video/'))
            WHERE arquivo_zip LIKE '%portal_sem_video/portal_sem_video/%' OR arquivo_zip != TRIM(arquivo_zip);
        """)
        affected_rows = cursor.rowcount
        print(f"Registros afetados: {affected_rows}")
    
    print(f"\n=== APÓS CORREÇÃO ===")
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id, nome, arquivo_zip FROM {table_name} WHERE ativo = true;")
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Nome: {row[1]}, Arquivo: '{row[2]}' (len={len(row[2])})")
            
    print("\n✅ Correção SQL concluída!")

except Exception as e:
    print(f"❌ Erro durante correção: {e}")
    import traceback
    traceback.print_exc()
EOF

echo ""
echo "=== TESTANDO API APÓS CORREÇÃO ==="

# Testar API
python << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo

# Verificar portal
portal = EldPortalSemVideo.objects.filter(ativo=True).first()
if portal:
    print(f"Portal ativo: {portal.nome}")
    print(f"Arquivo: '{portal.arquivo_zip.name}'")
    print(f"Path: {portal.arquivo_zip.path}")
    print(f"Existe: {os.path.exists(portal.arquivo_zip.path)}")
    
    # Testar API
    try:
        from captive_portal.api_views import portal_download
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/api/appliances/portal/download/?type=without_video')
        request.appliance_user = type('Mock', (), {'username': 'test'})()
        
        response = portal_download(request)
        print(f"API Status: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 API FUNCIONANDO!")
        else:
            print("❌ API ainda com problema")
            
    except Exception as e:
        print(f"Erro no teste API: {e}")
else:
    print("❌ Nenhum portal ativo")
EOF

echo ""
echo "🎉 CORREÇÃO EMERGENCIAL CONCLUÍDA!"

#!/bin/bash
echo "=== CORREÇÃO EMERGENCIAL VIA SQL ==="
echo "Executando correção direta no banco de dados..."

# Conectar no banco e executar SQL direto
python << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection

# SQL direto para corrigir o campo
sql_commands = [
    # Mostrar estado atual
    "SELECT id, nome, arquivo_zip FROM painel_eldportalsemvideo WHERE ativo = true;",
    
    # Corrigir duplicação e espaços
    """UPDATE painel_eldportalsemvideo 
     SET arquivo_zip = TRIM(REPLACE(arquivo_zip, 'portal_sem_video/portal_sem_video/', 'portal_sem_video/'))
     WHERE arquivo_zip LIKE '%portal_sem_video/portal_sem_video/%' OR arquivo_zip != TRIM(arquivo_zip);""",
    
    # Mostrar resultado
    "SELECT id, nome, arquivo_zip FROM painel_eldportalsemvideo WHERE ativo = true;"
]

with connection.cursor() as cursor:
    print("=== ANTES DA CORREÇÃO ===")
    cursor.execute(sql_commands[0])
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Nome: {row[1]}, Arquivo: '{row[2]}' (len={len(row[2])})")
    
    print("\n=== EXECUTANDO CORREÇÃO ===")
    cursor.execute(sql_commands[1])
    affected_rows = cursor.rowcount
    print(f"Registros afetados: {affected_rows}")
    
    print("\n=== APÓS CORREÇÃO ===")
    cursor.execute(sql_commands[2])
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Nome: {row[1]}, Arquivo: '{row[2]}' (len={len(row[2])})")

print("\n✅ Correção SQL concluída!")
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

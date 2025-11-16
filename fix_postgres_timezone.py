import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    print("Configurando timezone do PostgreSQL para America/Campo_Grande...")
    
    # Alterar timezone para America/Campo_Grande
    cursor.execute("ALTER DATABASE radiusd SET timezone TO 'America/Campo_Grande';")
    print("✅ Timezone do banco de dados alterado!")
    
    # Reconectar para aplicar a mudança
    connection.close()
    connection.connect()
    
    # Verificar
    cursor.execute("SHOW timezone;")
    new_tz = cursor.fetchone()[0]
    print(f"🕐 Novo timezone: {new_tz}")
    
    # Verificar hora atual
    cursor.execute("SELECT now();")
    pg_now = cursor.fetchone()[0]
    print(f"🕐 Hora atual do PostgreSQL: {pg_now}")

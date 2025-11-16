import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection
from datetime import datetime

with connection.cursor() as cursor:
    # Verificar timezone do PostgreSQL
    cursor.execute("SHOW timezone;")
    pg_timezone = cursor.fetchone()[0]
    print(f"🕐 Timezone do PostgreSQL: {pg_timezone}")
    
    # Verificar hora atual do PostgreSQL
    cursor.execute("SELECT now();")
    pg_now = cursor.fetchone()[0]
    print(f"🕐 Hora atual do PostgreSQL: {pg_now}")
    
    # Verificar hora do sistema (Python/Django)
    print(f"🕐 Hora atual do sistema (Python): {datetime.now()}")
    
    # Verificar último registro inserido
    cursor.execute("""
        SELECT id, username, video, date_view, hostname
        FROM eld_registro_view_videos 
        ORDER BY id DESC 
        LIMIT 5;
    """)
    print("\n📊 Últimos 5 registros:")
    for row in cursor.fetchall():
        print(f"ID: {row[0]} | User: {row[1]} | Video: {row[2]} | Data: {row[3]} | Host: {row[4]}")

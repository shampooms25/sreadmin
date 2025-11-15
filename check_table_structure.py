import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, data_type, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'eld_registro_view_videos' 
        ORDER BY ordinal_position;
    """)
    print("\n=== Estrutura da tabela eld_registro_view_videos ===")
    for row in cursor.fetchall():
        print(f"Coluna: {row[0]:20} Tipo: {row[1]:20} Default: {row[2]}")

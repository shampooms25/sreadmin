import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Adicionar DEFAULT now() na coluna date_view
    print("Adicionando DEFAULT now() na coluna date_view...")
    cursor.execute("""
        ALTER TABLE eld_registro_view_videos 
        ALTER COLUMN date_view SET DEFAULT now();
    """)
    print("✅ DEFAULT adicionado com sucesso!")
    
    # Verificar a mudança
    cursor.execute("""
        SELECT column_name, data_type, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'eld_registro_view_videos' 
        AND column_name = 'date_view';
    """)
    result = cursor.fetchone()
    print(f"\n=== Verificação ===")
    print(f"Coluna: {result[0]}")
    print(f"Tipo: {result[1]}")
    print(f"Default: {result[2]}")

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Adicionar coluna hostname
    print("Adicionando coluna hostname na tabela eld_registro_view_videos...")
    cursor.execute("""
        ALTER TABLE eld_registro_view_videos 
        ADD COLUMN IF NOT EXISTS hostname VARCHAR(255);
    """)
    print("✅ Coluna hostname adicionada com sucesso!")
    
    # Verificar a estrutura
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'eld_registro_view_videos' 
        ORDER BY ordinal_position;
    """)
    print("\n=== Estrutura da tabela atualizada ===")
    for row in cursor.fetchall():
        print(f"Coluna: {row[0]:20} Tipo: {row[1]:25} Tamanho: {row[2]}")

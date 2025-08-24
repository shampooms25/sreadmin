#!/usr/bin/env python
"""
Script para descobrir o nome correto da tabela no banco
"""
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

# Tentar ver o conteúdo da tabela correta
try:
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id, nome, arquivo_zip FROM {table_name} WHERE ativo = true;")
        print(f"\nConteúdo de {table_name}:")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Nome: {row[1]}, Arquivo: '{row[2]}' (len={len(row[2])})")
except Exception as e:
    print(f"Erro ao acessar tabela {table_name}: {e}")

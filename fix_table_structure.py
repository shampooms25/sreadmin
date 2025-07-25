#!/usr/bin/env python
"""
Script para verificar e corrigir a estrutura da tabela eld_gerenciar_portal
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection

def check_table_structure():
    """
    Verifica a estrutura atual da tabela eld_gerenciar_portal
    """
    print("=== VERIFICAÇÃO DA ESTRUTURA DA TABELA ===\n")
    
    with connection.cursor() as cursor:
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'eld_gerenciar_portal'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ Tabela 'eld_gerenciar_portal' não existe!")
            return False
        
        print("✅ Tabela 'eld_gerenciar_portal' existe!")
        
        # Verificar colunas existentes
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'eld_gerenciar_portal'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\nCOLUNAS EXISTENTES:")
        print("-" * 60)
        for col in columns:
            print(f"• {col[0]} ({col[1]}) - Nullable: {col[2]} - Default: {col[3]}")
        
        # Verificar quais colunas estão faltando
        expected_columns = {
            'id': 'bigint',
            'ativar_video': 'boolean',
            'nome_video_id': 'bigint',  # Esta é a chave estrangeira
            'captive_portal_zip': 'character varying',
            'data_criacao': 'timestamp with time zone',
            'data_atualizacao': 'timestamp with time zone',
            'ativo': 'boolean'
        }
        
        existing_columns = {col[0]: col[1] for col in columns}
        
        print(f"\nCOLUNAS ESPERADAS vs EXISTENTES:")
        print("-" * 60)
        missing_columns = []
        for col_name, col_type in expected_columns.items():
            if col_name in existing_columns:
                print(f"✅ {col_name} - OK")
            else:
                print(f"❌ {col_name} - FALTANDO")
                missing_columns.append((col_name, col_type))
        
        return missing_columns

def fix_table_structure():
    """
    Adiciona as colunas faltantes na tabela
    """
    missing_columns = check_table_structure()
    
    if not missing_columns:
        print("\n🎉 Tabela já está com a estrutura correta!")
        return True
    
    print(f"\n🔧 CORRIGINDO ESTRUTURA DA TABELA...")
    
    with connection.cursor() as cursor:
        # Primeiro, remover a coluna nome_video antiga (VARCHAR) se existir
        try:
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'eld_gerenciar_portal' AND column_name = 'nome_video'
                AND data_type = 'character varying';
            """)
            if cursor.fetchone():
                cursor.execute("ALTER TABLE eld_gerenciar_portal DROP COLUMN nome_video;")
                print("✅ Coluna nome_video (VARCHAR) removida!")
        except Exception as e:
            print(f"⚠️ Aviso ao remover coluna nome_video: {str(e)}")
        
        # Agora adicionar as colunas faltantes
        for col_name, col_type in missing_columns:
            try:
                if col_name == 'nome_video_id':
                    # Adicionar coluna de chave estrangeira simples primeiro
                    sql = """
                    ALTER TABLE eld_gerenciar_portal 
                    ADD COLUMN nome_video_id BIGINT NULL;
                    """
                elif col_name == 'data_criacao':
                    sql = f"""
                    ALTER TABLE eld_gerenciar_portal 
                    ADD COLUMN {col_name} TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                    """
                elif col_name == 'data_atualizacao':
                    sql = f"""
                    ALTER TABLE eld_gerenciar_portal 
                    ADD COLUMN {col_name} TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                    """
                elif col_name == 'ativo':
                    sql = f"""
                    ALTER TABLE eld_gerenciar_portal 
                    ADD COLUMN {col_name} BOOLEAN DEFAULT TRUE;
                    """
                else:
                    sql = f"""
                    ALTER TABLE eld_gerenciar_portal 
                    ADD COLUMN {col_name} {col_type} NULL;
                    """
                
                cursor.execute(sql)
                print(f"✅ Coluna {col_name} adicionada com sucesso!")
                
            except Exception as e:
                print(f"❌ Erro ao adicionar coluna {col_name}: {str(e)}")
                return False
    
    print(f"\n🎉 Estrutura da tabela corrigida com sucesso!")
    return True

if __name__ == "__main__":
    success = fix_table_structure()
    if success:
        print(f"\n✅ PRONTO PARA USAR!")
        print(f"   Execute novamente o test_portal_management.py")
    else:
        print(f"\n❌ PROBLEMAS NA CORREÇÃO - Verifique os erros acima")

"""
Script para marcar migrações como aplicadas diretamente no banco
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection

def mark_migrations_as_applied():
    """Marcar migrações como aplicadas diretamente no banco"""
    
    print("🔧 MARCANDO MIGRAÇÕES COMO APLICADAS")
    print("=" * 50)
    
    cursor = connection.cursor()
    
    try:
        # Verificar se a migração painel já existe
        cursor.execute("""
            SELECT COUNT(*) FROM django_migrations 
            WHERE app = 'painel' AND name = '0009_eldportalsemvideo_and_more';
        """)
        
        exists = cursor.fetchone()[0]
        
        if exists == 0:
            # Inserir registro da migração
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('painel', '0009_eldportalsemvideo_and_more', NOW());
            """)
            print("✅ Migração painel 0009 marcada como aplicada!")
        else:
            print("ℹ️  Migração painel 0009 já está marcada como aplicada!")
        
        # Verificar se a migração captive_portal já existe
        cursor.execute("""
            SELECT COUNT(*) FROM django_migrations 
            WHERE app = 'captive_portal' AND name = '0003_alter_captiveportalproxy_options_and_more';
        """)
        
        exists_cp = cursor.fetchone()[0]
        
        if exists_cp == 0:
            # Inserir registro da migração
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('captive_portal', '0003_alter_captiveportalproxy_options_and_more', NOW());
            """)
            print("✅ Migração captive_portal 0003 marcada como aplicada!")
        else:
            print("ℹ️  Migração captive_portal 0003 já está marcada como aplicada!")
        
        print("\n📊 MIGRAÇÕES ATUAIS:")
        cursor.execute("""
            SELECT app, name, applied 
            FROM django_migrations 
            WHERE app IN ('painel', 'captive_portal')
            ORDER BY app, name;
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} - {row[2]}")
        
        print("\n🎉 PROCESSO CONCLUÍDO!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    finally:
        cursor.close()
    
    return True

if __name__ == "__main__":
    mark_migrations_as_applied()

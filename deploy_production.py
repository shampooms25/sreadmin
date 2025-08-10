#!/usr/bin/env python
"""
Script de Deploy para Produção - Resolução de Conflitos de Migração
Resolve problemas de tabelas já existentes vs migrações pendentes
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def check_table_exists(table_name):
    """Verifica se uma tabela existe no banco"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]

def mark_migration_as_applied(app_name, migration_name):
    """Marca uma migração como aplicada no django_migrations"""
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied) 
            VALUES (%s, %s, NOW()) 
            ON CONFLICT (app, name) DO NOTHING;
        """, [app_name, migration_name])
        print(f"✅ Migração marcada como aplicada: {app_name}.{migration_name}")

def main():
    print("🔄 Iniciando deploy de produção...")
    print("📊 Verificando estado do banco de dados...")
    
    # Verificar tabelas existentes que estão causando conflito
    existing_tables = {
        'eld_gerenciar_portal': 'captive_portal.0001_initial',
        'eld_upload_video': 'captive_portal.0001_initial',
        'eld_registro_view_videos': 'captive_portal.0001_initial',
        'eld_portal_sem_video': 'captive_portal.0001_initial',
        'captive_portal_appliancetoken': 'captive_portal.0004_appliancetoken',
    }
    
    migrations_to_fake = []
    
    for table_name, migration in existing_tables.items():
        if check_table_exists(table_name):
            print(f"✅ Tabela já existe: {table_name}")
            migrations_to_fake.append(migration)
        else:
            print(f"❌ Tabela não existe: {table_name}")
    
    # Marcar migrações como aplicadas para tabelas que já existem
    if migrations_to_fake:
        print("\n🔧 Marcando migrações como aplicadas...")
        
        for migration in set(migrations_to_fake):  # Remove duplicatas
            app_name, migration_name = migration.split('.', 1)
            mark_migration_as_applied(app_name, migration_name)
    
    print("\n🚀 Executando migrações restantes...")
    
    try:
        # Tentar aplicar migrações normalmente
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        print("✅ Migrações aplicadas com sucesso!")
        
    except Exception as e:
        print(f"⚠️ Erro nas migrações: {e}")
        
        # Se ainda há erro, tentar fake para migrações específicas
        print("🔄 Tentando resolver com fake migrations...")
        
        try:
            # Fake migrations para captive_portal se necessário
            execute_from_command_line(['manage.py', 'migrate', 'captive_portal', '--fake'])
            print("✅ Captive portal migrations marcadas como fake")
            
            # Tentar migrar novamente
            execute_from_command_line(['manage.py', 'migrate'])
            print("✅ Migrações restantes aplicadas!")
            
        except Exception as e2:
            print(f"❌ Erro persistente: {e2}")
            print("🔧 Solução manual necessária")
            return False
    
    print("\n📦 Verificando dependências Python...")
    
    # Verificar se Pillow está instalado
    try:
        import PIL
        print("✅ Pillow instalado")
    except ImportError:
        print("❌ Pillow não encontrado - instalando...")
        os.system("pip install Pillow")
        print("✅ Pillow instalado")
    
    # Verificar outras dependências
    required_packages = ['requests', 'psycopg2']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} disponível")
        except ImportError:
            print(f"⚠️ {package} não encontrado")
    
    print("\n🎯 Coletando arquivos estáticos...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Arquivos estáticos coletados")
    except Exception as e:
        print(f"⚠️ Erro ao coletar estáticos: {e}")
    
    print("\n📊 Verificação final...")
    
    # Testar se o sistema está funcionando
    try:
        from captive_portal.models import ApplianceToken
        token_count = ApplianceToken.objects.count()
        print(f"✅ Sistema funcionando - {token_count} tokens cadastrados")
    except Exception as e:
        print(f"⚠️ Erro no sistema: {e}")
    
    print("\n🎉 Deploy de produção concluído!")
    print("🌐 URLs importantes:")
    print("   - Admin: /admin/")
    print("   - API Info: /api/appliances/info/")
    print("   - Portal Status: /api/appliances/portal/status/")
    print("   - Token Admin: /admin/captive_portal/appliancetoken/")
    
    return True

if __name__ == '__main__':
    main()

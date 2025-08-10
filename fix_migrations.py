#!/usr/bin/env python
"""
Fix Migration Conflicts - Produção
Resolve conflitos de migrações quando tabelas já existem
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def main():
    print("🔧 Resolvendo conflitos de migração...")
    
    # 1. Verificar e marcar migrações já aplicadas
    print("📋 Verificando estado das migrações...")
    
    with connection.cursor() as cursor:
        # Verificar se tabelas existem
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('eld_gerenciar_portal', 'eld_upload_video', 'eld_registro_view_videos', 'eld_portal_sem_video');
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Tabelas existentes: {existing_tables}")
        
        if existing_tables:
            print("🔄 Marcando migração captive_portal.0001_initial como aplicada...")
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('captive_portal', '0001_initial', NOW()) 
                ON CONFLICT (app, name) DO NOTHING;
            """)
        
        # Verificar tabela ApplianceToken
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'captive_portal_appliancetoken'
            );
        """)
        
        if cursor.fetchone()[0]:
            print("🔄 Marcando migração captive_portal.0004_appliancetoken como aplicada...")
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('captive_portal', '0004_appliancetoken', NOW()) 
                ON CONFLICT (app, name) DO NOTHING;
            """)
    
    # 2. Executar migrações restantes
    print("🚀 Executando migrações...")
    try:
        call_command('migrate', verbosity=2)
        print("✅ Migrações aplicadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("🔄 Tentando com --fake-initial...")
        try:
            call_command('migrate', fake_initial=True)
            print("✅ Migrações resolvidas com fake-initial!")
        except Exception as e2:
            print(f"❌ Erro persistente: {e2}")
            return False
    
    # 3. Verificar se tudo está funcionando
    print("🔍 Verificando sistema...")
    try:
        from captive_portal.models import ApplianceToken
        count = ApplianceToken.objects.count()
        print(f"✅ Sistema OK - {count} tokens no banco")
        
        # Testar admin
        from django.contrib.admin.sites import site
        print(f"✅ Admin carregado - {len(site._registry)} modelos registrados")
        
    except Exception as e:
        print(f"⚠️ Aviso: {e}")
    
    print("🎉 Resolução de conflitos concluída!")
    return True

if __name__ == '__main__':
    main()

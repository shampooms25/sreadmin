#!/usr/bin/env python
"""
Resolução Rápida de Migração - Produção
Execute: python quick_migration_fix.py
"""

import os
import sys
import django

# Setup Django
sys.path.append('/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def main():
    print("⚡ Resolução Rápida de Migração")
    print("===============================")
    
    try:
        with connection.cursor() as cursor:
            print("🔍 Verificando tabelas existentes...")
            
            # Verificar quais tabelas ELD existem
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN (
                    'eld_gerenciar_portal', 
                    'eld_upload_video', 
                    'eld_registro_view_videos', 
                    'eld_portal_sem_video',
                    'captive_portal_appliancetoken'
                );
            """)
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            print(f"📋 Tabelas encontradas: {existing_tables}")
            
            if existing_tables:
                print("🔧 Marcando migrações como aplicadas...")
                
                # Marcar migração inicial se tabelas ELD existem
                if any(table.startswith('eld_') for table in existing_tables):
                    cursor.execute("""
                        INSERT INTO django_migrations (app, name, applied) 
                        VALUES ('captive_portal', '0001_initial', NOW()) 
                        ON CONFLICT (app, name) DO NOTHING;
                    """)
                    print("✅ 0001_initial marcada como aplicada")
                
                # Marcar migração do ApplianceToken se tabela existe
                if 'captive_portal_appliancetoken' in existing_tables:
                    cursor.execute("""
                        INSERT INTO django_migrations (app, name, applied) 
                        VALUES ('captive_portal', '0004_appliancetoken', NOW()) 
                        ON CONFLICT (app, name) DO NOTHING;
                    """)
                    print("✅ 0004_appliancetoken marcada como aplicada")
            
            print("🚀 Executando migrações...")
            
            # Tentar aplicar migrações com fake-initial
            call_command('migrate', fake_initial=True, verbosity=1)
            print("✅ Migrações aplicadas com sucesso!")
            
            # Verificar se tudo está funcionando
            print("🔍 Testando sistema...")
            from captive_portal.models import ApplianceToken
            count = ApplianceToken.objects.count()
            print(f"✅ Sistema OK - {count} tokens no banco")
            
            # Sincronizar tokens do JSON se existe
            import json
            if os.path.exists('/var/www/sreadmin/appliance_tokens.json'):
                print("🔄 Sincronizando tokens do JSON...")
                with open('/var/www/sreadmin/appliance_tokens.json', 'r') as f:
                    data = json.load(f)
                
                tokens_data = data.get('tokens', {})
                created_count = 0
                
                for token, info in tokens_data.items():
                    obj, created = ApplianceToken.objects.get_or_create(
                        token=token,
                        defaults={
                            'appliance_id': info['appliance_id'],
                            'appliance_name': info['appliance_name'],
                            'description': info['description'],
                            'is_active': True,
                        }
                    )
                    if created:
                        created_count += 1
                        print(f"  Token criado: {info['appliance_name']}")
                
                print(f"✅ {created_count} tokens sincronizados")
            
            print("\n🎉 Resolução concluída com sucesso!")
            print("🌐 URLs para testar:")
            print("   - Admin: http://172.18.25.253:8000/admin/")
            print("   - API: http://172.18.25.253:8000/api/appliances/info/")
            print("   - Tokens: http://172.18.25.253:8000/admin/captive_portal/appliancetoken/")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("📝 Solução manual:")
        print("   1. python manage.py migrate captive_portal --fake")
        print("   2. python manage.py migrate")
        return False

if __name__ == '__main__':
    main()

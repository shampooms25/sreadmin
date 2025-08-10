#!/usr/bin/env python
"""
Script direto para criar tabela ApplianceToken via Django ORM
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

# Configurar Django
django.setup()

from django.db import connection, transaction
from django.core.management import call_command
import json
from datetime import datetime

def create_table_and_sync():
    """Criar tabela e sincronizar dados"""
    
    print("🔄 Criando tabela captive_portal_appliancetoken...")
    
    try:
        # SQL para criar a tabela
        sql_create_table = """
        CREATE TABLE IF NOT EXISTS captive_portal_appliancetoken (
            id SERIAL PRIMARY KEY,
            token VARCHAR(64) UNIQUE NOT NULL,
            appliance_id VARCHAR(100) UNIQUE NOT NULL,
            appliance_name VARCHAR(200) NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_used TIMESTAMP WITH TIME ZONE,
            ip_address INET
        );
        """
        
        sql_create_indexes = """
        CREATE UNIQUE INDEX IF NOT EXISTS captive_portal_appliancetoken_token_unique 
            ON captive_portal_appliancetoken(token);
        CREATE UNIQUE INDEX IF NOT EXISTS captive_portal_appliancetoken_appliance_id_unique 
            ON captive_portal_appliancetoken(appliance_id);
        CREATE INDEX IF NOT EXISTS captive_portal_appliancetoken_is_active_idx 
            ON captive_portal_appliancetoken(is_active);
        """
        
        with connection.cursor() as cursor:
            # Criar tabela
            cursor.execute(sql_create_table)
            print("✅ Tabela criada!")
            
            # Criar índices
            cursor.execute(sql_create_indexes)
            print("✅ Índices criados!")
            
            # Marcar migração como aplicada
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('captive_portal', '0004_appliancetoken', NOW()) 
                ON CONFLICT (app, name) DO NOTHING;
            """)
            print("✅ Migração marcada como aplicada!")
        
        # Agora importar o modelo e sincronizar dados
        from captive_portal.models import ApplianceToken
        from django.utils import timezone
        
        print("🔄 Sincronizando tokens do JSON...")
        
        # Carregar dados do JSON
        json_file = 'appliance_tokens.json'
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
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
                        'created_at': timezone.now(),
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"  ✅ Token criado: {info['appliance_name']}")
                
                # Atualizar last_used se disponível
                if info.get('last_used'):
                    try:
                        # Tentar converter a data
                        last_used_str = info['last_used']
                        for fmt in ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%SZ']:
                            try:
                                last_used = datetime.strptime(last_used_str, fmt)
                                obj.last_used = timezone.make_aware(last_used)
                                obj.save()
                                break
                            except ValueError:
                                continue
                    except Exception as e:
                        print(f"    ⚠️ Erro ao processar last_used: {e}")
            
            print(f"📊 Tokens sincronizados: {created_count} criados")
        
        # Verificar resultado
        total = ApplianceToken.objects.count()
        print(f"\n✅ Sucesso! Total de tokens no banco: {total}")
        
        # Listar tokens
        print("\n📋 Tokens disponíveis:")
        for token in ApplianceToken.objects.all():
            print(f"  - {token.appliance_name} ({token.appliance_id})")
            print(f"    Token: {token.token[:16]}...")
        
        print(f"\n🌐 Acesse: http://localhost:8000/admin/captive_portal/appliancetoken/")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    create_table_and_sync()

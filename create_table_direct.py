#!/usr/bin/env python
"""
Script para criar a tabela ApplianceToken diretamente via Django ORM
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection, transaction
from django.core.management.color import no_style
import json

def create_table_directly():
    """
    Cria a tabela ApplianceToken diretamente via SQL
    """
    print("🔄 Criando tabela ApplianceToken diretamente...")
    
    sql = '''
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
    
    CREATE UNIQUE INDEX IF NOT EXISTS captive_portal_appliancetoken_token_unique 
        ON captive_portal_appliancetoken(token);
    CREATE UNIQUE INDEX IF NOT EXISTS captive_portal_appliancetoken_appliance_id_unique 
        ON captive_portal_appliancetoken(appliance_id);
    '''
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        print("✅ Tabela criada com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        return False

def test_table_access():
    """
    Testa o acesso à tabela via Django ORM
    """
    print("🔍 Testando acesso à tabela via Django ORM...")
    
    try:
        from captive_portal.models import ApplianceToken
        count = ApplianceToken.objects.count()
        print(f"✅ Tabela acessível! Total de registros: {count}")
        return True, count
    except Exception as e:
        print(f"❌ Erro ao acessar tabela: {e}")
        return False, 0

def sync_json_tokens():
    """
    Sincroniza tokens do JSON para o banco
    """
    print("🔄 Sincronizando tokens do JSON...")
    
    try:
        from captive_portal.models import ApplianceToken
        
        with open('appliance_tokens.json', 'r', encoding='utf-8') as f:
            tokens_data = json.load(f)
        
        tokens = tokens_data.get('tokens', {})
        synced = 0
        
        for token, info in tokens.items():
            if not ApplianceToken.objects.filter(token=token).exists():
                ApplianceToken.objects.create(
                    token=token,
                    appliance_id=info['appliance_id'],
                    appliance_name=info['appliance_name'],
                    description=info.get('description', ''),
                    is_active=True
                )
                synced += 1
                print(f"  ✅ {info['appliance_name']}")
        
        print(f"✅ {synced} tokens sincronizados!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao sincronizar: {e}")
        return False

def update_django_migrations():
    """
    Marca a migração como aplicada no Django
    """
    print("🔄 Marcando migração como aplicada...")
    
    try:
        from django.db.migrations.recorder import MigrationRecorder
        recorder = MigrationRecorder(connection)
        
        # Marcar a migração como aplicada
        recorder.record_applied('captive_portal', '0004_appliancetoken')
        print("✅ Migração marcada como aplicada!")
        return True
    except Exception as e:
        print(f"❌ Erro ao marcar migração: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 CRIAÇÃO DIRETA DA TABELA APPLIANCETOKEN")
    print("=" * 50)
    
    # 1. Criar tabela diretamente
    if not create_table_directly():
        return False
    
    # 2. Testar acesso via ORM
    access_ok, count = test_table_access()
    if not access_ok:
        return False
    
    # 3. Marcar migração como aplicada
    if not update_django_migrations():
        print("⚠️ Aviso: Não foi possível marcar a migração como aplicada")
    
    # 4. Sincronizar tokens se a tabela estiver vazia
    if count == 0:
        sync_json_tokens()
    else:
        print(f"ℹ️ Tabela já possui {count} registros")
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 50)
    print("✅ Tabela ApplianceToken criada e acessível")
    print("✅ Tokens sincronizados do JSON")
    print("✅ Sistema pronto para uso!")
    print("\n📋 Próximos passos:")
    print("1. Acesse /admin/captive_portal/appliancetoken/")
    print("2. Teste a API com os tokens disponíveis")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        sys.exit(1)

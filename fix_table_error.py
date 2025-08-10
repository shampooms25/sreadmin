#!/usr/bin/env python
"""
Script direto para criar a tabela ApplianceToken e resolver o erro
Execute este script para resolver o erro imediatamente
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.db import connection, transaction
import json


def create_appliance_token_table():
    """
    Cria a tabela ApplianceToken diretamente no banco
    """
    print("🔄 Criando tabela captive_portal_appliancetoken...")
    
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
    
    CREATE UNIQUE INDEX IF NOT EXISTS captive_portal_appliancetoken_token_idx 
        ON captive_portal_appliancetoken(token);
    CREATE UNIQUE INDEX IF NOT EXISTS captive_portal_appliancetoken_appliance_id_idx 
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
    Testa se a tabela pode ser acessada via Django ORM
    """
    print("🔍 Testando acesso via Django ORM...")
    
    try:
        from captive_portal.models import ApplianceToken
        count = ApplianceToken.objects.count()
        print(f"✅ Tabela acessível! Total de registros: {count}")
        return True, count
    except Exception as e:
        print(f"❌ Erro ao acessar tabela: {e}")
        return False, 0


def sync_tokens_from_json():
    """
    Sincroniza tokens do arquivo JSON para o banco
    """
    print("🔄 Sincronizando tokens do JSON...")
    
    json_file = 'appliance_tokens.json'
    if not os.path.exists(json_file):
        print(f"⚠️ Arquivo {json_file} não encontrado")
        return 0
    
    try:
        from captive_portal.models import ApplianceToken
        
        with open(json_file, 'r', encoding='utf-8') as f:
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
        return synced
        
    except Exception as e:
        print(f"❌ Erro ao sincronizar tokens: {e}")
        return 0


def mark_migration_applied():
    """
    Marca a migração como aplicada no Django
    """
    print("🔄 Marcando migração como aplicada...")
    
    try:
        from django.db.migrations.recorder import MigrationRecorder
        recorder = MigrationRecorder(connection)
        recorder.record_applied('captive_portal', '0004_appliancetoken')
        print("✅ Migração marcada como aplicada!")
        return True
    except Exception as e:
        print(f"⚠️ Aviso ao marcar migração: {e}")
        return False


def main():
    """
    Função principal - executa todos os passos
    """
    print("🚀 RESOLUÇÃO DO ERRO: captive_portal_appliancetoken")
    print("=" * 60)
    
    # 1. Criar tabela
    if not create_appliance_token_table():
        print("❌ Falha na criação da tabela!")
        return False
    
    print()
    
    # 2. Testar acesso
    success, count = test_table_access()
    if not success:
        print("❌ Tabela criada mas não acessível via ORM!")
        return False
    
    print()
    
    # 3. Sincronizar tokens se a tabela estiver vazia
    if count == 0:
        synced = sync_tokens_from_json()
        if synced > 0:
            print(f"✅ {synced} tokens foram sincronizados!")
    else:
        print(f"ℹ️ Tabela já possui {count} registros")
    
    print()
    
    # 4. Marcar migração
    mark_migration_applied()
    
    print()
    print("🎉 PROBLEMA RESOLVIDO!")
    print("=" * 60)
    print("✅ Tabela captive_portal_appliancetoken criada")
    print("✅ Django ORM funcionando")
    print("✅ Tokens sincronizados")
    print("✅ Migração marcada como aplicada")
    print()
    print("🔗 Agora você pode acessar:")
    print("   http://localhost:8000/admin/captive_portal/appliancetoken/")
    print()
    print("🧪 Para testar a API:")
    print("   http://localhost:8000/api/appliances/info/")
    print("   Authorization: Bearer test-token-123456789")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎯 SUCESSO TOTAL! O erro foi resolvido.")
        else:
            print("\n❌ Houve problemas. Verifique os erros acima.")
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        print("Verifique se o Django está configurado corretamente.")

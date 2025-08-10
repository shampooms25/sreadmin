#!/usr/bin/env python
"""
Script para executar migrações do Django
"""

import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.core.management import execute_from_command_line

def run_migrations():
    """
    Executa as migrações do Django
    """
    print("🔄 Executando migrações...")
    
    try:
        # Executar migrate
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações executadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")
        return False

def check_appliancetoken_table():
    """
    Verifica se a tabela ApplianceToken foi criada
    """
    print("🔍 Verificando se a tabela ApplianceToken existe...")
    
    try:
        from captive_portal.models import ApplianceToken
        
        # Tentar fazer uma query simples
        count = ApplianceToken.objects.count()
        print(f"✅ Tabela ApplianceToken existe! Total de registros: {count}")
        return True
    except Exception as e:
        print(f"❌ Erro ao acessar tabela ApplianceToken: {e}")
        return False

def sync_json_tokens():
    """
    Sincroniza tokens do JSON para o banco de dados
    """
    print("🔄 Sincronizando tokens do JSON para o banco...")
    
    try:
        import json
        from captive_portal.models import ApplianceToken
        from django.utils import timezone
        
        # Carregar tokens do JSON
        with open('appliance_tokens.json', 'r', encoding='utf-8') as f:
            tokens_data = json.load(f)
        
        tokens = tokens_data.get('tokens', {})
        synced = 0
        
        for token, info in tokens.items():
            # Verificar se já existe
            if not ApplianceToken.objects.filter(token=token).exists():
                ApplianceToken.objects.create(
                    token=token,
                    appliance_id=info['appliance_id'],
                    appliance_name=info['appliance_name'],
                    description=info.get('description', ''),
                    is_active=True
                )
                synced += 1
                print(f"  ✅ Token sincronizado: {info['appliance_name']}")
        
        print(f"🎉 {synced} tokens sincronizados!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao sincronizar tokens: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 CONFIGURAÇÃO DA TABELA APPLIANCETOKEN")
    print("=" * 50)
    
    # 1. Executar migrações
    if not run_migrations():
        print("❌ Falha nas migrações. Verifique os erros acima.")
        return False
    
    print()
    
    # 2. Verificar se a tabela foi criada
    if not check_appliancetoken_table():
        print("❌ Tabela não foi criada. Verifique as migrações.")
        return False
    
    print()
    
    # 3. Sincronizar tokens do JSON
    if not sync_json_tokens():
        print("⚠️ Falha na sincronização, mas tabela foi criada.")
    
    print()
    print("🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("✅ Tabela ApplianceToken criada")
    print("✅ Você pode acessar /admin/captive_portal/appliancetoken/")
    
    return True

if __name__ == "__main__":
    main()

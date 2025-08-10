#!/usr/bin/env python
"""
Script para criar e executar migrações do modelo ApplianceToken
e sincronizar tokens existentes do JSON para o banco de dados
"""

import os
import sys
import django
import json

# Configurar o Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.core.management import execute_from_command_line
from captive_portal.models import ApplianceToken
from django.utils import timezone


def create_migrations():
    """
    Cria as migrações para o modelo ApplianceToken
    """
    print("🔄 Criando migrações para o modelo ApplianceToken...")
    
    try:
        execute_from_command_line(['manage.py', 'makemigrations', 'captive_portal'])
        print("✅ Migrações criadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar migrações: {e}")
        return False


def run_migrations():
    """
    Executa as migrações
    """
    print("🔄 Executando migrações...")
    
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações executadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")
        return False


def sync_json_to_database():
    """
    Sincroniza tokens do arquivo JSON para o banco de dados
    """
    print("🔄 Sincronizando tokens do JSON para o banco de dados...")
    
    # Verificar se existe arquivo JSON
    json_file = 'appliance_tokens.json'
    if not os.path.exists(json_file):
        print(f"⚠️ Arquivo {json_file} não encontrado. Nenhum token para sincronizar.")
        return True
    
    try:
        # Carregar tokens do JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            tokens_data = json.load(f)
        
        tokens = tokens_data.get('tokens', {})
        if not tokens:
            print("⚠️ Nenhum token encontrado no arquivo JSON.")
            return True
        
        synced_count = 0
        skipped_count = 0
        
        for token, token_info in tokens.items():
            appliance_id = token_info.get('appliance_id')
            appliance_name = token_info.get('appliance_name')
            
            # Verificar se já existe
            if ApplianceToken.objects.filter(token=token).exists():
                print(f"⚠️ Token para {appliance_name} ({appliance_id}) já existe no banco. Pulando...")
                skipped_count += 1
                continue
            
            # Criar token no banco
            token_obj = ApplianceToken.objects.create(
                token=token,
                appliance_id=appliance_id,
                appliance_name=appliance_name,
                description=token_info.get('description', ''),
                is_active=True
            )
            
            # Atualizar datas se disponível
            if token_info.get('created_at'):
                try:
                    from django.utils.dateparse import parse_datetime
                    created_at = parse_datetime(token_info['created_at'])
                    if created_at:
                        token_obj.created_at = created_at
                except:
                    pass
            
            if token_info.get('last_used'):
                try:
                    from django.utils.dateparse import parse_datetime
                    last_used = parse_datetime(token_info['last_used'])
                    if last_used:
                        token_obj.last_used = last_used
                except:
                    pass
            
            if token_info.get('ip_address'):
                token_obj.ip_address = token_info['ip_address']
            
            token_obj.save()
            synced_count += 1
            print(f"✅ Token sincronizado: {appliance_name} ({appliance_id})")
        
        print(f"🎉 Sincronização concluída! {synced_count} tokens sincronizados, {skipped_count} ignorados.")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao sincronizar tokens: {e}")
        return False


def sync_database_to_json():
    """
    Sincroniza tokens do banco de dados para o arquivo JSON
    """
    print("🔄 Sincronizando tokens do banco para o arquivo JSON...")
    
    try:
        # Buscar todos os tokens ativos
        active_tokens = ApplianceToken.objects.filter(is_active=True)
        
        tokens_data = {
            "generated_at": timezone.now().isoformat(),
            "total_tokens": active_tokens.count(),
            "tokens": {}
        }
        
        for token_obj in active_tokens:
            tokens_data["tokens"][token_obj.token] = {
                "appliance_id": token_obj.appliance_id,
                "appliance_name": token_obj.appliance_name,
                "description": token_obj.description or "",
                "created_at": token_obj.created_at.isoformat(),
                "last_used": token_obj.last_used.isoformat() if token_obj.last_used else None,
                "ip_address": token_obj.ip_address
            }
        
        # Salvar no arquivo JSON
        with open('appliance_tokens.json', 'w', encoding='utf-8') as f:
            json.dump(tokens_data, f, indent=4, ensure_ascii=False)
        
        print(f"✅ {active_tokens.count()} tokens sincronizados para o arquivo JSON!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao sincronizar para JSON: {e}")
        return False


def main():
    """
    Função principal
    """
    print("🚀 SETUP DO SISTEMA DE TOKENS APPLIANCE POPPFIRE")
    print("=" * 60)
    
    # 1. Criar migrações
    if not create_migrations():
        return False
    
    print()
    
    # 2. Executar migrações
    if not run_migrations():
        return False
    
    print()
    
    # 3. Sincronizar tokens do JSON para banco
    if not sync_json_to_database():
        return False
    
    print()
    
    # 4. Sincronizar tokens do banco para JSON (garantir consistência)
    if not sync_database_to_json():
        return False
    
    print()
    print("🎉 SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("✅ Modelo ApplianceToken criado e migrado")
    print("✅ Tokens sincronizados entre JSON e banco de dados") 
    print("✅ Interface de administração disponível")
    print()
    print("📋 Próximos passos:")
    print("1. Acesse /admin/captive_portal/appliancetoken/ para gerenciar tokens")
    print("2. Use a API em /api/appliances/ para testar os endpoints")
    print("3. Monitore os logs de autenticação")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

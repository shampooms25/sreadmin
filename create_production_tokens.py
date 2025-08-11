#!/usr/bin/env python
"""
Gerador de Tokens para Produção - Versão Simplificada
Resolve problemas de permissão criando tokens diretamente no banco
"""

import os
import sys
import django

# Setup Django para produção
sys.path.append('/var/www/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from captive_portal.models import ApplianceToken

def main():
    print("🔑 Criando Tokens de Produção...")
    
    # Tokens essenciais para funcionamento
    tokens_config = [
        {
            'token': 'test-token-123456789',
            'appliance_id': 'TEST-APPLIANCE',
            'appliance_name': 'Appliance de Teste',
            'description': 'Token de teste para desenvolvimento'
        },
        {
            'token': 'f8e7d6c5b4a3928170695e4c3d2b1a0f',
            'appliance_id': 'APPLIANCE-001',
            'appliance_name': 'Appliance POPPFIRE 001',
            'description': 'Token para appliance de produção 001'
        },
        {
            'token': '1234567890abcdef1234567890abcdef',
            'appliance_id': 'APPLIANCE-DEV',
            'appliance_name': 'Appliance de Desenvolvimento',
            'description': 'Token para desenvolvimento e testes'
        }
    ]
    
    created_count = 0
    
    for config in tokens_config:
        try:
            obj, created = ApplianceToken.objects.get_or_create(
                token=config['token'],
                defaults={
                    'appliance_id': config['appliance_id'],
                    'appliance_name': config['appliance_name'],
                    'description': config['description'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                print(f"✅ {config['appliance_name']}")
            else:
                print(f"ℹ️ {config['appliance_name']} (já existe)")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    total = ApplianceToken.objects.count()
    print(f"\n📊 Total de tokens: {total}")
    print(f"🆕 Novos tokens criados: {created_count}")
    print("\n✅ Pronto para usar!")

if __name__ == '__main__':
    main()

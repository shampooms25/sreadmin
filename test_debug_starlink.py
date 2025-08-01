#!/usr/bin/env python3
"""
Teste da funcionalidade de debug da API Starlink
"""

import os
import sys
import django

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_all_recurring_data

def test_debug_functionality():
    """Testa a funcionalidade de debug"""
    print("=== TESTE DE DEBUG DA API STARLINK ===")
    
    # Testa uma conta específica
    account_id = "ACC-2744134-64041-5"
    
    print(f"Testando debug para a conta: {account_id}")
    
    try:
        # Chama a função que busca dados de recarga automática
        result = get_all_recurring_data(account_id)
        
        if result:
            print(f"✅ Sucesso! Dados obtidos da API.")
            print(f"📊 Resultado: {result}")
        else:
            print("⚠️  Nenhum dado retornado, mas sem erro.")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug_functionality()

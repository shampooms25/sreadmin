#!/usr/bin/env python3
"""
Teste da funcionalidade de desativação de recarga automática
"""

import os
import sys
import django

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import disable_auto_recharge

def test_disable_auto_recharge():
    """Testa a desativação de recarga automática para uma service line"""
    print("=== TESTE DE DESATIVAÇÃO DE RECARGA AUTOMÁTICA ===")
    
    account_id = "ACC-2744134-64041-5"
    # Usando uma das service lines que sabemos que tem recarga ativa
    service_line_number = "SL-5242096-78596-88"  # Esta apareceu no teste anterior
    
    print(f"Testando desativação para:")
    print(f"  - Conta: {account_id}")
    print(f"  - Service Line: {service_line_number}")
    
    try:
        result = disable_auto_recharge(account_id, service_line_number)
        
        if 'error' in result:
            print(f"❌ Erro: {result['error']}")
        elif result.get('success'):
            print(f"✅ Sucesso! {result['message']}")
        else:
            print(f"⚠️  Resposta inesperada: {result}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("⚠️  ATENÇÃO: Este teste irá DESATIVAR a recarga automática!")
    print("⚠️  Pressione Ctrl+C para cancelar, ou Enter para continuar...")
    
    try:
        input()
        test_disable_auto_recharge()
    except KeyboardInterrupt:
        print("\n🛑 Teste cancelado pelo usuário.")

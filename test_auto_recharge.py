#!/usr/bin/env python3
"""
Teste da funcionalidade de gerenciamento de recarga automática
"""

import os
import sys
import django

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import (
    check_auto_recharge_status, 
    disable_auto_recharge,
    get_service_lines_with_auto_recharge_status
)

def test_auto_recharge_functionality():
    """Testa a funcionalidade de recarga automática"""
    print("=== TESTE DE GERENCIAMENTO DE RECARGA AUTOMÁTICA ===")
    
    # Testa uma conta específica
    account_id = "ACC-2744134-64041-5"
    
    print(f"Testando para a conta: {account_id}")
    
    try:
        # Testa obter service lines com status de recarga automática
        print("\n1. Obtendo service lines com status de recarga automática...")
        result = get_service_lines_with_auto_recharge_status(account_id)
        
        if result and 'error' not in result:
            print(f"✅ Sucesso! {result['total_count']} service lines obtidas.")
            
            # Contar quantas têm recarga ativa
            active_count = 0
            inactive_count = 0
            error_count = 0
            
            for sl in result['service_lines']:
                status = sl.get('auto_recharge_status', {})
                if status.get('active'):
                    active_count += 1
                elif status.get('error'):
                    error_count += 1
                else:
                    inactive_count += 1
            
            print(f"📊 Status das recargas automáticas:")
            print(f"   - Ativas: {active_count}")
            print(f"   - Inativas: {inactive_count}")
            print(f"   - Erros: {error_count}")
            
            # Mostrar algumas service lines com detalhes
            print(f"\n📋 Primeiras 3 service lines:")
            for i, sl in enumerate(result['service_lines'][:3]):
                print(f"   {i+1}. {sl.get('serviceLineNumber', 'N/A')}")
                print(f"      Status: {sl.get('auto_recharge_status', {}).get('active', 'N/A')}")
                if sl.get('auto_recharge_status', {}).get('error'):
                    print(f"      Erro: {sl.get('auto_recharge_status', {}).get('error')}")
                print()
            
        else:
            print(f"❌ Erro: {result.get('error', 'Resposta inválida')}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

def test_individual_service_line():
    """Testa verificação de uma service line específica"""
    print("\n=== TESTE DE SERVICE LINE INDIVIDUAL ===")
    
    account_id = "ACC-2744134-64041-5"
    
    # Você pode colocar aqui um número de service line específico para testar
    # service_line_number = "SL-XXXXXX-XXXXX-XX"
    
    print("Para testar uma service line específica, adicione o número no código.")
    print("Exemplo: service_line_number = 'SL-XXXXXX-XXXXX-XX'")

if __name__ == "__main__":
    test_auto_recharge_functionality()
    test_individual_service_line()

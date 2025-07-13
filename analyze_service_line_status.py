#!/usr/bin/env python3
"""
Script para debugar e analisar os status das Service Lines
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import debug_service_line_status, get_all_accounts_summary, STARLINK_ACCOUNTS

def analyze_all_accounts():
    """Analisa status de todas as contas"""
    print("🔍 ANÁLISE COMPLETA DE STATUS DAS SERVICE LINES")
    print("=" * 80)
    
    total_discrepancies = 0
    
    for account_id, account_info in STARLINK_ACCOUNTS.items():
        print(f"\n📋 Analisando conta: {account_info['name']} ({account_id})")
        print("-" * 60)
        
        try:
            # Debug específico da conta
            result = debug_service_line_status(account_id)
            
            if result.get("success"):
                total_lines = result["total_lines"]
                total_counted = result["total_counted"]
                discrepancy = result["discrepancy"]
                
                print(f"📊 Total Service Lines: {total_lines}")
                print(f"📊 Total Contabilizadas: {total_counted}")
                
                if discrepancy > 0:
                    print(f"⚠️  DISCREPÂNCIA: {discrepancy} Service Lines não contabilizadas!")
                    total_discrepancies += discrepancy
                else:
                    print("✅ Todos os status contabilizados corretamente!")
                
                print(f"\n📋 Status encontrados:")
                for status, count in result["status_analysis"].items():
                    print(f"   {status}: {count}")
                
                print(f"\n📋 Campos disponíveis:")
                for field, values in result["field_analysis"].items():
                    print(f"   {field}:")
                    for value, count in values.items():
                        print(f"      {value}: {count}")
            else:
                print(f"❌ Erro: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Erro ao analisar conta {account_id}: {e}")
    
    print(f"\n🎯 RESUMO GERAL:")
    print("=" * 40)
    print(f"Total de discrepâncias encontradas: {total_discrepancies}")
    
    if total_discrepancies > 0:
        print("\n💡 SUGESTÕES:")
        print("1. Verificar se há novos campos de status na API")
        print("2. Analisar campos como 'state', 'serviceStatus', etc.")
        print("3. Implementar lógica para status 'Pendente', 'Suspenso', etc.")
    else:
        print("✅ Todas as Service Lines foram contabilizadas corretamente!")


def test_enhanced_status():
    """Testa a lógica aprimorada de status"""
    print("\n🧪 TESTANDO LÓGICA APRIMORADA DE STATUS")
    print("=" * 50)
    
    # Casos de teste
    test_cases = [
        {"active": True, "expected": "Ativo", "description": "Service Line ativo"},
        {"active": False, "expected": "Offline", "description": "Service Line offline"},
        {"active": True, "status": "suspended", "expected": "Suspenso", "description": "Service Line suspenso"},
        {"active": True, "state": "pending", "expected": "Pendente", "description": "Service Line pendente"},
        {"startDate": "2025-12-01T00:00:00Z", "expected": "Pendente", "description": "Service Line futuro"},
        {"endDate": "2024-01-01T00:00:00Z", "expected": "Sem Dados", "description": "Service Line antigo"},
        {}, {"expected": "Indeterminado", "description": "Service Line sem dados"}
    ]
    
    from painel.starlink_api import determine_enhanced_status
    
    for i, test_case in enumerate(test_cases, 1):
        expected = test_case.pop("expected")
        description = test_case.pop("description")
        
        result = determine_enhanced_status(test_case)
        
        status = "✅" if result == expected else "❌"
        print(f"{status} Teste {i}: {description}")
        print(f"   Dados: {test_case}")
        print(f"   Esperado: {expected}, Obtido: {result}")
        
        if result != expected:
            print(f"   ⚠️  FALHA NO TESTE!")
        print()


if __name__ == "__main__":
    try:
        analyze_all_accounts()
        test_enhanced_status()
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Script para testar a nova lógica de status das Service Lines
"""

# Configurar Django
import os
import sys
import django
sys.path.append('c:\\Projetos\\Poppnet\\sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_service_lines_with_location, STARLINK_ACCOUNTS

def test_enhanced_status_counting():
    """
    Testa a nova lógica de contagem de status
    """
    print("🔍 TESTANDO NOVA LÓGICA DE STATUS")
    print("=" * 60)
    
    total_global = 0
    total_contabilizado = 0
    total_discrepancia = 0
    
    for account_id, account_info in STARLINK_ACCOUNTS.items():
        print(f"\n📋 Conta: {account_info['name']} ({account_id})")
        print("-" * 40)
        
        try:
            result = get_service_lines_with_location(account_id)
            
            if result.get("success"):
                stats = result.get("statistics", {})
                
                # Valores básicos
                total_lines = stats.get("total_service_lines", 0)
                active = stats.get("active_lines", 0)
                offline = stats.get("offline_lines", 0)
                no_data = stats.get("no_data_lines", 0)
                pending = stats.get("pending_lines", 0)
                suspended = stats.get("suspended_lines", 0)
                indeterminate = stats.get("indeterminate_lines", 0)
                discrepancy = stats.get("discrepancy", 0)
                
                # Calcular total contabilizado
                counted = active + offline + no_data + pending + suspended + indeterminate
                
                print(f"📊 Total Service Lines: {total_lines}")
                print(f"   ✅ Ativo: {active}")
                print(f"   ❌ Offline: {offline}")
                print(f"   📊 Sem Dados: {no_data}")
                print(f"   ⏳ Pendente: {pending}")
                print(f"   🚫 Suspenso: {suspended}")
                print(f"   ❓ Indeterminado: {indeterminate}")
                print(f"   📋 Total Contabilizado: {counted}")
                
                if discrepancy > 0:
                    print(f"   ⚠️  DISCREPÂNCIA: {discrepancy}")
                else:
                    print(f"   ✅ SEM DISCREPÂNCIA")
                
                # Somar totais
                total_global += total_lines
                total_contabilizado += counted
                total_discrepancia += discrepancy
                
            else:
                print(f"❌ Erro: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Erro ao processar conta {account_id}: {e}")
    
    print(f"\n🎯 RESUMO GERAL:")
    print("=" * 40)
    print(f"Total Global: {total_global}")
    print(f"Total Contabilizado: {total_contabilizado}")
    print(f"Discrepância Total: {total_discrepancia}")
    
    if total_discrepancia == 0:
        print("✅ PERFEITO! Todas as Service Lines foram contabilizadas!")
    else:
        print(f"⚠️  AINDA HÁ {total_discrepancia} Service Lines não contabilizadas")
        print("Possíveis causas:")
        print("1. Novos tipos de status na API")
        print("2. Lógica de status ainda não captura todos os casos")
        print("3. Campos de status diferentes do esperado")

if __name__ == "__main__":
    try:
        test_enhanced_status_counting()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

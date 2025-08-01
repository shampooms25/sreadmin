#!/usr/bin/env python3
"""
Teste para verificar a diferença entre total de service lines
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:\\Projetos\\Poppnet\\sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_all_accounts_summary, get_service_lines_with_location, STARLINK_ACCOUNTS

def test_total_discrepancy():
    print("🔍 TESTANDO DISCREPÂNCIA ENTRE TOTAIS")
    print("=" * 60)
    
    # Testar resumo de todas as contas
    print("\n📊 Testando get_all_accounts_summary()...")
    all_accounts = get_all_accounts_summary()
    
    if all_accounts.get("success"):
        total_summary = all_accounts.get("total_summary", {})
        total_from_summary = total_summary.get("total_service_lines", 0)
        active_from_summary = total_summary.get("active_lines", 0)
        offline_from_summary = total_summary.get("offline_lines", 0)
        
        print(f"📋 Resumo de todas as contas:")
        print(f"   Total Service Lines: {total_from_summary}")
        print(f"   Ativas: {active_from_summary}")
        print(f"   Offline: {offline_from_summary}")
        print(f"   Total calculado: {active_from_summary + offline_from_summary}")
        
        # Testar conta por conta
        print(f"\n📋 Testando conta por conta:")
        total_individual = 0
        for account_id in STARLINK_ACCOUNTS.keys():
            result = get_service_lines_with_location(account_id)
            if result.get("success"):
                account_total = result.get("total", 0)
                stats = result.get("statistics", {})
                active = stats.get("active_lines", 0)
                offline = stats.get("offline_lines", 0)
                
                print(f"   {account_id}: {account_total} total ({active} ativas + {offline} offline)")
                total_individual += account_total
            else:
                print(f"   {account_id}: ERRO - {result.get('error')}")
        
        print(f"\n🎯 COMPARAÇÃO:")
        print(f"   Total do resumo: {total_from_summary}")
        print(f"   Total individual: {total_individual}")
        print(f"   Diferença: {abs(total_from_summary - total_individual)}")
        
        if total_from_summary == total_individual:
            print("   ✅ TOTAIS COINCIDEM!")
        else:
            print("   ❌ DISCREPÂNCIA ENCONTRADA!")
            
            # Investigar a causa
            print(f"\n🔍 INVESTIGANDO CAUSA DA DISCREPÂNCIA:")
            print(f"   Verificando dados detalhados de cada conta...")
            
            for account_id in STARLINK_ACCOUNTS.keys():
                account_data = all_accounts["accounts"].get(account_id, {})
                individual_data = get_service_lines_with_location(account_id)
                
                summary_total = account_data.get("total_service_lines", 0)
                individual_total = individual_data.get("total", 0) if individual_data.get("success") else 0
                
                if summary_total != individual_total:
                    print(f"   ⚠️  {account_id}: Summary={summary_total}, Individual={individual_total}")
                    # Verificar fonte dos dados
                    service_lines_stats = account_data.get("service_lines_statistics", {})
                    if isinstance(service_lines_stats, dict):
                        sl_total = service_lines_stats.get("total_service_lines", "N/A")
                        print(f"      service_lines_statistics.total_service_lines: {sl_total}")
                
    else:
        print("❌ Erro ao obter resumo de todas as contas")

if __name__ == "__main__":
    try:
        test_total_discrepancy()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

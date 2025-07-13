#!/usr/bin/env python
"""
Calcula o consumo correto da Service Line SL-854897-75238-43 usando dados reais da API
"""
import json
from datetime import datetime

def calculate_correct_usage():
    """
    Calcula o consumo correto baseado nos dados reais da API
    """
    print("=== CÁLCULO CORRETO DE CONSUMO ===")
    print()
    
    try:
        # Carregar dados do arquivo JSON
        with open('billing_analysis_SL_854897_75238_43.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("📋 DADOS CARREGADOS:")
        print(f"   Service Line: SL-854897-75238-43")
        print()
        
        # Encontrar o ciclo atual (julho 2025)
        results = data.get('content', {}).get('results', [])
        
        if not results:
            print("❌ Nenhum resultado encontrado")
            return False
        
        result = results[0]  # Primeiro (e único) resultado
        billing_cycles = result.get('billingCycles', [])
        
        print(f"📊 {len(billing_cycles)} ciclos de billing encontrados")
        
        # Procurar pelo ciclo atual (julho 2025)
        current_cycle = None
        for cycle in billing_cycles:
            start_date = cycle.get('startDate', '')
            end_date = cycle.get('endDate', '')
            
            if '2025-07-03' in start_date:
                current_cycle = cycle
                print(f"🎯 CICLO ATUAL ENCONTRADO:")
                print(f"   Início: {start_date}")
                print(f"   Fim: {end_date}")
                break
        
        if not current_cycle:
            print("❌ Ciclo atual (julho 2025) não encontrado")
            return False
        
        # Calcular consumo total do ciclo atual
        daily_usage = current_cycle.get('dailyDataUsage', [])
        
        print(f"\n📊 ANALISANDO {len(daily_usage)} DIAS DE DADOS:")
        print()
        
        total_priority = 0
        total_standard = 0
        total_opt_in_priority = 0
        total_non_billable = 0
        
        print("📅 CONSUMO DIÁRIO:")
        for day in daily_usage:
            date = day.get('date', '').split('T')[0]
            priority = day.get('priorityGB', 0)
            opt_in_priority = day.get('optInPriorityGB', 0)
            standard = day.get('standardGB', 0)
            non_billable = day.get('nonBillableGB', 0)
            
            daily_total = priority + standard
            
            print(f"   {date}: Priority={priority:.2f} GB, Standard={standard:.2f} GB, Total={daily_total:.2f} GB")
            
            total_priority += priority
            total_opt_in_priority += opt_in_priority
            total_standard += standard
            total_non_billable += non_billable
        
        # Cálculo final
        total_consumption = total_priority + total_standard
        
        print()
        print("=" * 60)
        print("🎯 RESULTADO FINAL:")
        print("=" * 60)
        print(f"📊 Priority GB: {total_priority:.2f}")
        print(f"📊 Opt-in Priority GB: {total_opt_in_priority:.2f}")
        print(f"📊 Standard GB: {total_standard:.2f}")
        print(f"📊 Non-billable GB: {total_non_billable:.2f}")
        print()
        print(f"🎯 TOTAL CORRETO: {total_consumption:.2f} GB")
        print(f"🎯 TOTAL CORRETO: {total_consumption/1024:.2f} TB")
        print()
        print("📋 COMPARAÇÃO:")
        print(f"   ✅ Valor correto (API): {total_consumption:.2f} GB")
        print(f"   ❌ Valor no sistema: 268,45 GB")
        print(f"   🔧 Diferença: {abs(268.45 - total_consumption):.2f} GB")
        print()
        
        if total_consumption < 100:
            print("✅ CONFIRMADO: O valor correto está próximo dos 90 GB reportados no app Starlink")
        else:
            print("⚠️  ATENÇÃO: Valor ainda alto, verificar cálculo")
        
        print("=" * 60)
        
        # Retornar dados para correção do sistema
        return {
            "service_line": "SL-854897-75238-43",
            "cycle_start": "2025-07-03",
            "cycle_end": "2025-08-03",
            "priority_gb": total_priority,
            "standard_gb": total_standard,
            "total_gb": total_consumption,
            "days_analyzed": len(daily_usage),
            "correct_calculation": True
        }
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 CALCULANDO CONSUMO CORRETO...")
    print()
    
    result = calculate_correct_usage()
    
    print()
    if result:
        print("🎉 CÁLCULO CONCLUÍDO COM SUCESSO!")
        print(f"   Use {result['total_gb']:.2f} GB como valor correto")
        print("   Agora vamos corrigir a função de cálculo no sistema")
    else:
        print("❌ ERRO NO CÁLCULO!")
    
    print("=" * 80)

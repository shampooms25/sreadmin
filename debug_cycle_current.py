#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from datetime import date, datetime

def debug_cycle_calculation():
    """
    Debug do cálculo do ciclo atual
    """
    print("=== DEBUG: Cálculo do Ciclo Atual ===")
    
    today = date.today()
    print(f"📅 Data atual: {today.strftime('%d/%m/%Y')} (dia {today.day})")
    
    # Calcular ciclo atual (mesma lógica da view)
    if today.day < 3:
        # Ciclo começou no dia 3 do mês anterior
        if today.month == 1:
            cycle_start_month = 12
            cycle_start_year = today.year - 1
        else:
            cycle_start_month = today.month - 1
            cycle_start_year = today.year
        cycle_start = date(cycle_start_year, cycle_start_month, 3)
    else:
        # Ciclo começou no dia 3 do mês atual
        cycle_start = date(today.year, today.month, 3)
    
    cycle_end = today
    cycle_days = (cycle_end - cycle_start).days + 1
    
    print(f"🔄 Ciclo calculado:")
    print(f"   Início: {cycle_start.strftime('%d/%m/%Y')}")
    print(f"   Fim: {cycle_end.strftime('%d/%m/%Y')}")
    print(f"   Duração: {cycle_days} dias")
    
    # Verificar o que a API está buscando
    print(f"\n🔍 A API deveria buscar dados de:")
    print(f"   Data início: {cycle_start.strftime('%Y-%m-%d')}")
    print(f"   Data fim: {cycle_end.strftime('%Y-%m-%d')}")
    
    return cycle_start, cycle_end, cycle_days

def test_billing_filter():
    """
    Testa o filtro de billing por data
    """
    print("\n=== TESTE: Filtro de Billing por Data ===")
    
    cycle_start, cycle_end, cycle_days = debug_cycle_calculation()
    
    # Simular dados de billing cycles
    mock_billing_cycles = [
        {
            "startDate": "2025-07-03T00:00:00Z",
            "endDate": "2025-08-02T23:59:59Z",
            "dailyDataUsage": [
                {"date": "2025-07-03", "priorityGB": 10, "standardGB": 50},
                {"date": "2025-07-04", "priorityGB": 12, "standardGB": 55},
                {"date": "2025-07-05", "priorityGB": 8, "standardGB": 45},
                # ... mais dados até julho
                {"date": "2025-07-31", "priorityGB": 15, "standardGB": 60},
                {"date": "2025-08-01", "priorityGB": 9, "standardGB": 40},
                {"date": "2025-08-02", "priorityGB": 11, "standardGB": 48},
                {"date": "2025-08-03", "priorityGB": 13, "standardGB": 52},
                {"date": "2025-08-04", "priorityGB": 14, "standardGB": 58},
                {"date": "2025-08-05", "priorityGB": 12, "standardGB": 55},
            ]
        },
        {
            "startDate": "2025-08-03T00:00:00Z", 
            "endDate": "2025-09-02T23:59:59Z",
            "dailyDataUsage": [
                {"date": "2025-08-03", "priorityGB": 13, "standardGB": 52},
                {"date": "2025-08-04", "priorityGB": 14, "standardGB": 58},
                {"date": "2025-08-05", "priorityGB": 12, "standardGB": 55},
            ]
        }
    ]
    
    # Testar lógica atual (problemática)
    print("\n❌ LÓGICA ATUAL (PROBLEMÁTICA):")
    current_cycle_data = None
    for cycle in mock_billing_cycles:
        start_date = cycle.get("startDate", "")
        end_date = cycle.get("endDate", "")
        
        # Lógica atual - sempre pega julho
        if "2025-07-03" in start_date or "2025-08-03" in end_date:
            current_cycle_data = cycle
            break
    
    if current_cycle_data:
        print(f"   Ciclo selecionado: {current_cycle_data['startDate']} até {current_cycle_data['endDate']}")
        print(f"   Dias de dados: {len(current_cycle_data['dailyDataUsage'])}")
    
    # Lógica corrigida
    print("\n✅ LÓGICA CORRIGIDA:")
    cycle_start_str = cycle_start.strftime("%Y-%m-%d")
    cycle_end_str = cycle_end.strftime("%Y-%m-%d")
    
    print(f"   Procurando ciclo que contenha: {cycle_start_str} até {cycle_end_str}")
    
    best_cycle = None
    for cycle in mock_billing_cycles:
        start_date = cycle.get("startDate", "")[:10]  # Só a data, sem hora
        end_date = cycle.get("endDate", "")[:10]
        
        # Verificar se o ciclo atual está dentro do período do billing cycle
        if start_date <= cycle_start_str and end_date >= cycle_end_str:
            best_cycle = cycle
            print(f"   ✅ Ciclo encontrado: {start_date} até {end_date}")
            break
    
    if best_cycle:
        # Filtrar apenas os dias do ciclo atual
        daily_usage = best_cycle.get("dailyDataUsage", [])
        filtered_usage = []
        
        for day in daily_usage:
            day_date = day.get("date", "")
            if cycle_start_str <= day_date <= cycle_end_str:
                filtered_usage.append(day)
        
        print(f"   Dias filtrados: {len(filtered_usage)} (de {len(daily_usage)} total)")
        
        total_priority = sum(day.get("priorityGB", 0) for day in filtered_usage)
        total_standard = sum(day.get("standardGB", 0) for day in filtered_usage)
        total_gb = total_priority + total_standard
        
        print(f"   Consumo no período atual: {total_gb:.2f} GB")
        print(f"   (Priority: {total_priority:.2f} GB + Standard: {total_standard:.2f} GB)")
    else:
        print("   ❌ Nenhum ciclo adequado encontrado")

if __name__ == "__main__":
    debug_cycle_calculation()
    test_billing_filter()

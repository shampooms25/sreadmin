#!/usr/bin/env python3
"""
Script para testar os dados que estão chegando na view starlink_availability_report
"""
import os
import sys
import django

# Configurar o Django
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_usage_report_data, get_availability_report_data

def test_view_data():
    """Testar exatamente como a view processa os dados"""
    print("=== Teste da Lógica de Dados da View ===\n")
    
    # Parâmetros de teste (mesmos da URL)
    selected_service_lines = ['SL-5242096-78596-88', 'SL-3628728-50239-91', 'SL-854897-75238-43']
    
    # Dados de ciclo (usar os mesmos da view)
    from datetime import datetime
    current_date = datetime.now()
    cycle_start = datetime(current_date.year, current_date.month, 3)
    if current_date.day < 3:
        if current_date.month == 1:
            cycle_start = datetime(current_date.year - 1, 12, 3)
        else:
            cycle_start = datetime(current_date.year, current_date.month - 1, 3)
    
    start_date_str = cycle_start.strftime("%d/%m/%Y")
    if cycle_start.month == 12:
        cycle_end = datetime(cycle_start.year + 1, 1, 2)
    else:
        cycle_end = datetime(cycle_start.year, cycle_start.month + 1, 2)
    end_date_str = cycle_end.strftime("%d/%m/%Y")
    
    print(f"Período: {start_date_str} até {end_date_str}")
    print(f"Service Lines: {selected_service_lines}")
    
    # Buscar dados de disponibilidade
    print("\n=== 1. Dados de Disponibilidade ===")
    availability_data = get_availability_report_data(selected_service_lines, start_date_str, end_date_str)
    print(f"Availability data keys: {list(availability_data.keys()) if availability_data else 'None'}")
    
    # Buscar dados de consumo
    print("\n=== 2. Dados de Consumo ===")
    consumption_data = get_usage_report_data(account_id="ACC-2744134-64041-5", 
                                           cycle_start=start_date_str, 
                                           cycle_end=end_date_str)
    print(f"Consumption data success: {consumption_data.get('success')}")
    print(f"Usage data count: {len(consumption_data.get('usage_data', []))}")
    
    # Processo de combinação (replicar a lógica da view corrigida)
    print("\n=== 3. Processo de Combinação ===")
    combined_data = {}
    for sl in selected_service_lines:
        print(f"\nProcessando {sl}:")
        
        # Dados de disponibilidade
        avail_info = availability_data.get(sl, {})
        print(f"  Avail info keys: {list(avail_info.keys()) if avail_info else 'None'}")
        
        # Dados de consumo - procurar no array usage_data
        consumption_info = {}
        if consumption_data.get('success') and 'usage_data' in consumption_data:
            for usage_line in consumption_data['usage_data']:
                if usage_line.get('serviceLineNumber') == sl:
                    consumption_info = {
                        'priority_gb': usage_line.get('priorityUsageMB', 0) / 1024,
                        'standard_gb': usage_line.get('standardUsageMB', 0) / 1024,
                        'total_gb': usage_line.get('totalUsageMB', 0) / 1024,
                    }
                    print(f"  Consumo encontrado: Priority={consumption_info['priority_gb']:.2f} GB, Standard={consumption_info['standard_gb']:.2f} GB, Total={consumption_info['total_gb']:.2f} GB")
                    break
        else:
            print("  Nenhum consumo encontrado!")
            
        # Combinar
        combined_data[sl] = {
            **avail_info,
            **consumption_info
        }
        
        print(f"  Combined data keys: {list(combined_data[sl].keys())}")
        print(f"  Total GB final: {combined_data[sl].get('total_gb', 'N/A')}")
    
    print(f"\n=== 4. Resumo Final ===")
    total_consumption = sum(data.get('total_gb', 0) for data in combined_data.values())
    print(f"Consumo total de todas as service lines: {total_consumption:.2f} GB")
    
    return combined_data

if __name__ == "__main__":
    test_view_data()

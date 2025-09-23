#!/usr/bin/env python3
"""
Teste simples para verificar se a API está retornando dados
"""
import os
import sys
import django

# Configurar o Django
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_usage_report_data

def test_simple():
    print("=== Teste Simples API ===")
    
    # Buscar dados de consumo
    consumption_data = get_usage_report_data(account_id="ACC-2744134-64041-5", 
                                           cycle_start="03/09/2025", 
                                           cycle_end="02/10/2025")
    
    print(f"Success: {consumption_data.get('success', False)}")
    print(f"Usage data count: {len(consumption_data.get('usage_data', []))}")
    
    if consumption_data.get('success') and 'usage_data' in consumption_data:
        # Procurar pelas 3 service lines da URL
        test_lines = ['SL-5242096-78596-88', 'SL-3628728-50239-91', 'SL-854897-75238-43']
        
        for sl in test_lines:
            found = False
            for usage_line in consumption_data['usage_data']:
                if usage_line.get('serviceLineNumber') == sl:
                    priority_gb = usage_line.get('priorityUsageMB', 0) / 1024
                    standard_gb = usage_line.get('standardUsageMB', 0) / 1024
                    total_gb = usage_line.get('totalUsageMB', 0) / 1024
                    
                    print(f"{sl}: Priority={priority_gb:.2f} GB, Standard={standard_gb:.2f} GB, Total={total_gb:.2f} GB")
                    found = True
                    break
            if not found:
                print(f"{sl}: NÃO ENCONTRADO")

if __name__ == "__main__":
    test_simple()

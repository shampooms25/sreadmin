#!/usr/bin/env python
import os
import sys
import django

# Adicionar o path do projeto
sys.path.append('C:/Projetos/Poppnet/sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_usage_report_data

def test_usage_data():
    print("=== TESTE DE DADOS DE USO ===")
    
    # Testar com dados específicos
    result = get_usage_report_data(
        account_id='ACC-2744134-64041-5',
        cycle_start='03/09/2025',
        cycle_end='02/10/2025'
    )
    
    print(f"Success: {result.get('success', 'N/A')}")
    print(f"Error: {result.get('error', 'N/A')}")
    print(f"Total lines: {result.get('total_lines', 0)}")
    
    if result.get('usage_data'):
        print(f"\n--- DADOS ENCONTRADOS ({len(result['usage_data'])} linhas) ---")
        for item in result['usage_data'][:5]:  # Mostrar apenas os primeiros 5
            sl = item.get('serviceLineNumber', 'N/A')
            priority = item.get('priorityGB', 0)
            standard = item.get('standardGB', 0)
            total = item.get('totalGB', 0)
            print(f"- {sl}: Priority={priority} GB, Standard={standard} GB, Total={total} GB")
    else:
        print("❌ Nenhum dado de uso encontrado")
    
    return result

if __name__ == "__main__":
    result = test_usage_data()

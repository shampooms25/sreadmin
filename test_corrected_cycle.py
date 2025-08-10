#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_usage_report_data
from datetime import date

def test_corrected_cycle_filter():
    """
    Testa se o filtro do ciclo atual foi corrigido
    """
    print("=== TESTE: Filtro do Ciclo Atual CORRIGIDO ===")
    
    # Calcular ciclo atual
    today = date.today()
    
    if today.day < 3:
        if today.month == 1:
            cycle_start_month = 12
            cycle_start_year = today.year - 1
        else:
            cycle_start_month = today.month - 1
            cycle_start_year = today.year
        cycle_start = date(cycle_start_year, cycle_start_month, 3)
    else:
        cycle_start = date(today.year, today.month, 3)
    
    cycle_end = today
    cycle_days = (cycle_end - cycle_start).days + 1
    
    cycle_start_str = cycle_start.strftime("%d/%m/%Y")
    cycle_end_str = cycle_end.strftime("%d/%m/%Y")
    
    print(f"📅 Data atual: {today.strftime('%d/%m/%Y')}")
    print(f"🔄 Ciclo atual: {cycle_start_str} até {cycle_end_str} ({cycle_days} dias)")
    
    # Testar com a conta principal
    account_id = "ACC-2744134-64041-5"
    
    print(f"\n🚀 Testando com conta: {account_id}")
    print(f"📊 Chamando get_usage_report_data com filtro de data...")
    
    try:
        result = get_usage_report_data(
            account_id=account_id,
            cycle_start=cycle_start_str,
            cycle_end=cycle_end_str
        )
        
        if "error" in result:
            print(f"❌ Erro: {result['error']}")
        else:
            print(f"✅ Sucesso!")
            print(f"   📋 Service lines processados: {result.get('total_lines', 0)}")
            print(f"   📅 Ciclo retornado: {result.get('cycle_start')} até {result.get('cycle_end')}")
            
            usage_data = result.get('usage_data', [])
            if usage_data:
                print(f"   📊 Dados de consumo: {len(usage_data)} linhas")
                
                # Mostrar exemplo de uma linha
                first_line = usage_data[0]
                print(f"   📈 Exemplo (primeira linha):")
                print(f"      Service Line: {first_line.get('serviceLineNumber')}")
                print(f"      Consumo: {first_line.get('totalGB')} GB")
                print(f"      Dias analisados: {first_line.get('days_analyzed')}")
                print(f"      Fonte: {first_line.get('data_source')}")
                
                # Verificar se os dados estão proporcionais
                total_consumption = sum(line.get('totalGB', 0) for line in usage_data)
                print(f"   📊 Consumo total: {total_consumption:.2f} GB")
                
                # Verificar estatísticas
                stats = result.get('statistics', {})
                print(f"   📈 Estatísticas:")
                print(f"      Linhas < 70%: {stats.get('lines_under_70', 0)}")
                print(f"      Linhas ≥ 70%: {stats.get('lines_70_plus', 0)}")
                print(f"      Total GB: {stats.get('total_consumption_gb', 0):.2f}")
            else:
                print(f"   ⚠️  Nenhum dado de consumo encontrado")
    
    except Exception as e:
        print(f"❌ Erro na execução: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_corrected_cycle_filter()

#!/usr/bin/env python
import os
import sys
import django
import json
from pprint import pprint

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from painel.starlink_api import get_telemetry_data, get_availability_report_data

def analyze_telemetry_data():
    """Analisar dados completos da API de telemetria"""
    
    print("=" * 80)
    print("🔍 ANÁLISE COMPLETA DOS DADOS DE TELEMETRIA")
    print("=" * 80)
    
    # Service lines para testar
    service_lines = ['75238', '854897', '43']
    start_date = "01/08/2024"
    end_date = "31/08/2024"
    
    print(f"📡 Service Lines: {service_lines}")
    print(f"📅 Período: {start_date} até {end_date}")
    print("-" * 80)
    
    # Testar função individual de telemetria
    print("🧪 TESTANDO get_telemetry_data() INDIVIDUAL:")
    print("-" * 50)
    
    for sl in service_lines:
        print(f"\n🛰️  Testando Service Line: {sl}")
        telemetry_data = get_telemetry_data(sl, start_date, end_date)
        
        print(f"📊 Resposta para {sl}:")
        pprint(telemetry_data, width=100, depth=3)
    
    print("\n" + "=" * 80)
    print("🧪 TESTANDO get_availability_report_data() COMBINADA:")
    print("=" * 80)
    
    # Buscar dados de disponibilidade (inclui telemetria)
    availability_data = get_availability_report_data(service_lines, start_date, end_date)
    
    print("🔍 ESTRUTURA COMPLETA DA RESPOSTA DE AVAILABILITY:")
    print("-" * 50)
    pprint(availability_data, width=120, depth=4)
    
    print("\n" + "=" * 80)
    print("📊 ANÁLISE DETALHADA POR SERVICE LINE - AVAILABILITY")
    print("=" * 80)
    
    for sl in service_lines:
        if sl in availability_data:
            print(f"\n🛰️  SERVICE LINE: {sl}")
            print("-" * 40)
            
            sl_data = availability_data[sl]
            print(f"📈 Tipo de dados: {type(sl_data)}")
            print(f"📊 Chaves disponíveis: {list(sl_data.keys()) if isinstance(sl_data, dict) else 'N/A'}")
            
            # Verificar dados de conectividade/ping
            if isinstance(sl_data, dict):
                print("\n🔗 DADOS DE CONECTIVIDADE:")
                connectivity_fields = [
                    'ping_drop_rate', 'ping_latency_ms', 'connectivity_status',
                    'ping_metrics', 'availability_status', 'uptime_percentage',
                    'has_real_ping_data', 'api_source'
                ]
                
                for field in connectivity_fields:
                    if field in sl_data:
                        print(f"  ✅ {field}: {sl_data[field]}")
                
                # Mostrar todos os campos
                print("\n📋 TODOS OS CAMPOS:")
                for key, value in sl_data.items():
                    if isinstance(value, dict):
                        print(f"  📦 {key}: {type(value)} com {len(value)} itens")
                        for subkey, subvalue in value.items():
                            print(f"      • {subkey}: {subvalue}")
                    else:
                        print(f"  • {key}: {value}")
                        
        else:
            print(f"\n❌ SERVICE LINE {sl}: Dados não encontrados")

if __name__ == "__main__":
    analyze_telemetry_data()

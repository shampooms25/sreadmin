#!/usr/bin/env python3
"""
Script para analisar a estrutura completa dos dados retornados pela API de telemetria
"""
import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_telemetry_data

def print_header(text, char="="):
    """Imprime cabeçalho estilizado"""
    print(f"\n{char * 80}")
    print(f"{text:^80}")
    print(f"{char * 80}")

def print_section(title, char="-"):
    """Imprime seção estilizada"""
    print(f"\n{char * 60}")
    print(f"{title}")
    print(f"{char * 60}")

def analyze_dict_structure(data, prefix="", level=0):
    """Analisa estrutura de dicionário recursivamente"""
    indent = "  " * level
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{indent}{prefix}{key}: [DICT] ({len(value)} keys)")
                analyze_dict_structure(value, f"{key}.", level + 1)
            elif isinstance(value, list):
                print(f"{indent}{prefix}{key}: [LIST] ({len(value)} items)")
                if value and isinstance(value[0], dict):
                    print(f"{indent}  └─ Sample item structure:")
                    analyze_dict_structure(value[0], f"{key}[0].", level + 2)
                elif value:
                    print(f"{indent}  └─ Sample values: {value[:3]}")
            else:
                value_str = str(value)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                print(f"{indent}{prefix}{key}: {type(value).__name__} = {value_str}")
    elif isinstance(data, list):
        print(f"{indent}List with {len(data)} items")
        if data and isinstance(data[0], dict):
            print(f"{indent}Sample item:")
            analyze_dict_structure(data[0], "", level + 1)

def main():
    print_header("ANÁLISE COMPLETA DA API DE TELEMETRIA STARLINK", "🚀")
    
    # Service lines para teste
    service_lines = ['75238']
    
    # Datas para teste (ciclo atual)
    current_date = datetime.now()
    start_date = f"03/{current_date.month:02d}/{current_date.year}"
    end_date = f"02/{current_date.month + 1:02d}/{current_date.year}" if current_date.month < 12 else f"02/01/{current_date.year + 1}"
    
    print(f"📡 Service Lines: {service_lines}")
    print(f"📅 Período: {start_date} até {end_date}")
    
    try:
        print_section("🔄 FAZENDO REQUISIÇÃO À API...")
        
        # Fazer requisição
        telemetry_data = get_telemetry_data(service_lines, start_date, end_date)
        
        print_section("✅ RESPOSTA RECEBIDA - ESTRUTURA GERAL")
        
        # Informações básicas
        print(f"📊 Tipo de dados: {type(telemetry_data)}")
        if isinstance(telemetry_data, dict):
            print(f"🔑 Chaves principais: {list(telemetry_data.keys())}")
            print(f"📏 Tamanho total: {len(telemetry_data)} chaves")
        
        print_section("🔍 ESTRUTURA DETALHADA DOS DADOS")
        
        # Analisar estrutura recursivamente
        analyze_dict_structure(telemetry_data)
        
        print_section("📋 DADOS COMPLETOS (JSON)")
        
        # Imprimir JSON completo formatado
        print(json.dumps(telemetry_data, indent=2, ensure_ascii=False, default=str))
        
        print_section("🎯 CAMPOS RELACIONADOS À CONECTIVIDADE")
        
        # Procurar por campos relacionados a ping/conectividade
        connectivity_fields = []
        
        def find_connectivity_fields(data, path=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Procurar campos relacionados a ping/conectividade
                    key_lower = key.lower()
                    if any(keyword in key_lower for keyword in ['ping', 'latency', 'rtt', 'connectivity', 'icmp', 'uptime', 'availability']):
                        connectivity_fields.append((current_path, key, type(value).__name__, value))
                    
                    if isinstance(value, (dict, list)):
                        find_connectivity_fields(value, current_path)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    find_connectivity_fields(item, f"{path}[{i}]")
        
        find_connectivity_fields(telemetry_data)
        
        if connectivity_fields:
            print("🔗 Campos encontrados relacionados à conectividade:")
            for path, key, type_name, value in connectivity_fields:
                print(f"  📍 {path}")
                print(f"     Tipo: {type_name}")
                print(f"     Valor: {value}")
                print()
        else:
            print("⚠️  Nenhum campo óbvio de conectividade encontrado")
            print("   Verifique os dados completos acima para identificar campos relevantes")
        
        print_section("📊 RESUMO ESTATÍSTICO")
        
        def count_data_types(data):
            counts = {"dict": 0, "list": 0, "str": 0, "int": 0, "float": 0, "bool": 0, "null": 0}
            
            def count_recursive(obj):
                if isinstance(obj, dict):
                    counts["dict"] += 1
                    for value in obj.values():
                        count_recursive(value)
                elif isinstance(obj, list):
                    counts["list"] += 1
                    for item in obj:
                        count_recursive(item)
                elif isinstance(obj, str):
                    counts["str"] += 1
                elif isinstance(obj, int):
                    counts["int"] += 1
                elif isinstance(obj, float):
                    counts["float"] += 1
                elif isinstance(obj, bool):
                    counts["bool"] += 1
                elif obj is None:
                    counts["null"] += 1
            
            count_recursive(data)
            return counts
        
        stats = count_data_types(telemetry_data)
        for data_type, count in stats.items():
            if count > 0:
                print(f"  {data_type.upper()}: {count}")
        
    except Exception as e:
        print_section("❌ ERRO NA REQUISIÇÃO")
        print(f"Erro: {str(e)}")
        print(f"Tipo do erro: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    print_header("🏁 ANÁLISE CONCLUÍDA", "=")

if __name__ == "__main__":
    main()

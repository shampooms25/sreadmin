#!/usr/bin/env python3
"""
Análise detalhada da API de telemetria da Starlink
"""
import os
import sys
import django
import json
import requests
from datetime import datetime, timedelta

# Configurar Django
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def analyze_telemetry_api():
    """Analisar a estrutura completa da API de telemetria"""
    print("=== ANÁLISE DA API DE TELEMETRIA STARLINK ===\n")
    
    # Importar funções necessárias
    from painel.starlink_api import get_auth_headers
    
    # Obter headers de autenticação
    headers = get_auth_headers()
    if not headers:
        print("❌ Erro: Não foi possível obter headers de autenticação")
        return
    
    # Service line para teste
    service_line = "SL-5242096-78596-88"
    
    # Datas para teste (últimos 2 dias)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    print(f"🔍 Testando telemetria para: {service_line}")
    print(f"📅 Período: {start_str} até {end_str}\n")
    
    # URL da API de telemetria
    url = f"https://web-api.starlink.com/enterprise/v1/telemetry/{service_line}"
    
    # Diferentes payloads para testar
    payloads = [
        {
            "name": "Payload Básico",
            "data": {
                "startDate": start_str,
                "endDate": end_str
            }
        },
        {
            "name": "Payload com Métricas",
            "data": {
                "startDate": start_str,
                "endDate": end_str,
                "metrics": ["uptime", "downtime", "ping", "latency", "packet_loss", "throughput", "icmp"]
            }
        },
        {
            "name": "Payload Detalhado",
            "data": {
                "startDate": start_str,
                "endDate": end_str,
                "granularity": "hourly",
                "includeNetworkMetrics": True,
                "includePingMetrics": True
            }
        }
    ]
    
    for payload_info in payloads:
        print(f"🧪 Testando: {payload_info['name']}")
        print(f"📤 Payload: {json.dumps(payload_info['data'], indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, json=payload_info['data'], timeout=30)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ Resposta JSON válida")
                    
                    # Analisar estrutura da resposta
                    print(f"🔑 Chaves principais: {list(data.keys()) if isinstance(data, dict) else 'Lista'}")
                    
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 0:
                                print(f"  📋 {key}: {len(value)} itens")
                                if isinstance(value[0], dict):
                                    print(f"     Campos do primeiro item: {list(value[0].keys())}")
                            elif isinstance(value, dict):
                                print(f"  📁 {key}: {list(value.keys())}")
                            else:
                                print(f"  📝 {key}: {type(value).__name__}")
                    
                    # Procurar especificamente por métricas de ping/ICMP
                    response_str = json.dumps(data, default=str).lower()
                    
                    ping_keywords = ['ping', 'icmp', 'latency', 'rtt', 'response_time', 'packet_loss', 'jitter']
                    found_keywords = [kw for kw in ping_keywords if kw in response_str]
                    
                    if found_keywords:
                        print(f"🎯 Métricas de conectividade encontradas: {found_keywords}")
                    else:
                        print("❌ Nenhuma métrica de ping/ICMP encontrada")
                    
                    # Mostrar amostra da resposta (primeiros 500 caracteres)
                    sample = json.dumps(data, indent=2, default=str)[:500]
                    print(f"📄 Amostra da resposta:\n{sample}...")
                    
                except json.JSONDecodeError:
                    print("❌ Resposta não é JSON válido")
                    print(f"📄 Resposta raw: {response.text[:200]}...")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print(f"📄 Resposta: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout na requisição")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {str(e)}")
        
        print("-" * 60)
    
    # Testar também endpoint de métricas gerais
    print("\n🔍 Testando endpoint de métricas gerais...")
    metrics_url = "https://web-api.starlink.com/enterprise/v1/metrics"
    
    try:
        response = requests.get(metrics_url, headers=headers, timeout=30)
        print(f"📊 Status métricas gerais: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🔑 Métricas disponíveis: {list(data.keys()) if isinstance(data, dict) else len(data)}")
            
    except Exception as e:
        print(f"❌ Erro ao consultar métricas gerais: {str(e)}")

if __name__ == "__main__":
    analyze_telemetry_api()

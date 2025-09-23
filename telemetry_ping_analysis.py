#!/usr/bin/env python3
"""
Análise Completa: API de Telemetria Starlink - Métricas de ICMP/Ping
"""
import os
import sys
import django
import json
import requests
from datetime import datetime

# Configurar Django
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def comprehensive_telemetry_analysis():
    """
    Análise abrangente da API de telemetria para identificar todas as métricas disponíveis,
    com foco especial em dados de ping, latência e ICMP
    """
    print("=" * 80)
    print("ANÁLISE COMPLETA: API DE TELEMETRIA STARLINK")
    print("OBJETIVO: Identificar métricas de ICMP/Ping existentes")
    print("=" * 80)
    print()
    
    from painel.starlink_api import get_auth_headers, get_valid_token
    
    # 1. VERIFICAR AUTENTICAÇÃO
    print("🔐 1. VERIFICAÇÃO DE AUTENTICAÇÃO")
    print("-" * 40)
    
    token = get_valid_token()
    if not token:
        print("❌ Token não disponível")
        return
    else:
        print("✅ Token obtido com sucesso")
    
    headers = get_auth_headers()
    print(f"📋 Headers configurados: {bool(headers)}")
    print()
    
    # 2. ENDPOINTS CONHECIDOS PARA TELEMETRIA
    print("🌐 2. ENDPOINTS DE TELEMETRIA IDENTIFICADOS")
    print("-" * 40)
    
    endpoints = [
        {
            "name": "Telemetria Stream v1",
            "url": "https://web-api.starlink.com/telemetry/stream/v1/telemetry",
            "method": "POST",
            "description": "Endpoint principal atual"
        },
        {
            "name": "Enterprise Telemetria",
            "url": "https://web-api.starlink.com/enterprise/v1/telemetry",
            "method": "GET/POST",
            "description": "Endpoint enterprise"
        },
        {
            "name": "Telemetria por Service Line",
            "url": "https://web-api.starlink.com/enterprise/v1/telemetry/{service_line}",
            "method": "POST",
            "description": "Telemetria específica por SL"
        },
        {
            "name": "Métricas Gerais",
            "url": "https://web-api.starlink.com/enterprise/v1/metrics",
            "method": "GET",
            "description": "Métricas disponíveis"
        }
    ]
    
    for endpoint in endpoints:
        print(f"📡 {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        print(f"   Método: {endpoint['method']}")
        print(f"   Descrição: {endpoint['description']}")
        print()
    
    # 3. TESTAR CADA ENDPOINT
    print("🧪 3. TESTE DOS ENDPOINTS")
    print("-" * 40)
    
    service_line = "SL-5242096-78596-88"  # Service line de teste
    
    # Teste 1: Endpoint atual (Stream v1)
    print("🔸 Testando: Telemetria Stream v1")
    test_stream_v1(headers, service_line)
    print()
    
    # Teste 2: Endpoint enterprise
    print("🔸 Testando: Enterprise Telemetria")
    test_enterprise_telemetry(headers, service_line)
    print()
    
    # Teste 3: Métricas disponíveis
    print("🔸 Testando: Métricas Gerais")
    test_metrics_endpoint(headers)
    print()
    
    # 4. ANÁLISE DE CAMPOS POTENCIAIS
    print("🎯 4. CAMPOS POTENCIAIS PARA PING/ICMP")
    print("-" * 40)
    
    potential_fields = [
        "ping", "icmp", "latency", "rtt", "responseTime", "response_time",
        "packetLoss", "packet_loss", "jitter", "connectionQuality",
        "networkLatency", "network_latency", "pingTime", "ping_time",
        "connectivityMetrics", "connectivity_metrics", "qualityMetrics",
        "downlinkLatency", "uplinkLatency", "averageLatency", "medianLatency"
    ]
    
    print("🔍 Campos que devemos procurar na resposta da API:")
    for i, field in enumerate(potential_fields, 1):
        print(f"   {i:2d}. {field}")
    print()
    
    # 5. RECOMENDAÇÕES
    print("💡 5. RECOMENDAÇÕES")
    print("-" * 40)
    print("✓ Se a API já possui métricas de ping/ICMP, devemos usar esses dados")
    print("✓ Se não possui, podemos implementar monitoramento complementar")
    print("✓ Priorizar sempre os dados oficiais da Starlink")
    print("✓ Usar dados simulados apenas como fallback")
    print()

def test_stream_v1(headers, service_line):
    """Testar o endpoint stream v1"""
    url = "https://web-api.starlink.com/telemetry/stream/v1/telemetry"
    
    payloads = [
        {"serviceLineNumber": service_line},
        {
            "serviceLineNumber": service_line,
            "startDate": "2025-09-03",
            "endDate": "2025-09-04",
            "includeNetworkMetrics": True
        }
    ]
    
    for i, payload in enumerate(payloads, 1):
        print(f"   Payload {i}: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                analyze_response_for_ping_metrics(data, "Stream v1")
            else:
                print(f"   Erro: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   Exceção: {str(e)}")
        
        print()

def test_enterprise_telemetry(headers, service_line):
    """Testar endpoint enterprise"""
    base_url = "https://web-api.starlink.com/enterprise/v1/telemetry"
    
    urls = [
        base_url,
        f"{base_url}/{service_line}"
    ]
    
    for url in urls:
        print(f"   URL: {url}")
        
        try:
            # Tentar GET
            response = requests.get(url, headers=headers, timeout=15)
            print(f"   GET Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                analyze_response_for_ping_metrics(data, "Enterprise GET")
            
            # Tentar POST
            payload = {
                "serviceLineNumber": service_line,
                "startDate": "2025-09-03",
                "endDate": "2025-09-04"
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            print(f"   POST Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                analyze_response_for_ping_metrics(data, "Enterprise POST")
                
        except Exception as e:
            print(f"   Exceção: {str(e)}")
        
        print()

def test_metrics_endpoint(headers):
    """Testar endpoint de métricas gerais"""
    url = "https://web-api.starlink.com/enterprise/v1/metrics"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Estrutura: {type(data).__name__}")
            
            if isinstance(data, dict):
                print(f"   Chaves principais: {list(data.keys())}")
            elif isinstance(data, list):
                print(f"   Itens na lista: {len(data)}")
                if len(data) > 0 and isinstance(data[0], dict):
                    print(f"   Campos do primeiro item: {list(data[0].keys())}")
            
            # Procurar por métricas de ping
            data_str = json.dumps(data, default=str).lower()
            ping_keywords = ['ping', 'icmp', 'latency', 'rtt']
            found = [kw for kw in ping_keywords if kw in data_str]
            
            if found:
                print(f"   ✅ Métricas de ping encontradas: {found}")
            else:
                print("   ❌ Nenhuma métrica de ping identificada")
                
    except Exception as e:
        print(f"   Exceção: {str(e)}")

def analyze_response_for_ping_metrics(data, source):
    """Analisar resposta buscando especificamente métricas de ping/ICMP"""
    print(f"   📊 Analisando resposta de {source}:")
    
    # Converter para string para busca
    data_str = json.dumps(data, default=str).lower()
    
    # Palavras-chave relacionadas a ping/conectividade
    ping_keywords = [
        'ping', 'icmp', 'latency', 'rtt', 'response_time', 'responsetime',
        'packet_loss', 'packetloss', 'jitter', 'delay', 'connectivity',
        'network_latency', 'networklatency', 'round_trip', 'roundtrip'
    ]
    
    found_keywords = []
    for keyword in ping_keywords:
        if keyword in data_str:
            found_keywords.append(keyword)
    
    if found_keywords:
        print(f"   ✅ ENCONTRADO! Métricas relacionadas: {found_keywords}")
        
        # Tentar extrair valores específicos
        if isinstance(data, dict):
            for key, value in data.items():
                key_lower = key.lower()
                if any(kw in key_lower for kw in found_keywords):
                    print(f"      {key}: {value}")
    else:
        print("   ❌ Nenhuma métrica de ping/ICMP encontrada")
    
    # Mostrar estrutura geral
    if isinstance(data, dict):
        print(f"   📋 Chaves disponíveis: {list(data.keys())}")
    elif isinstance(data, list) and len(data) > 0:
        print(f"   📋 Lista com {len(data)} itens")
        if isinstance(data[0], dict):
            print(f"   📋 Campos do primeiro item: {list(data[0].keys())}")

if __name__ == "__main__":
    comprehensive_telemetry_analysis()

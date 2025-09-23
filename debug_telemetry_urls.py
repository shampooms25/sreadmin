#!/usr/bin/env python3
"""
Script para debugar as chamadas da API de telemetria e verificar URLs
"""
import os
import sys
import django
import requests
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def test_telemetry_apis():
    print("🔍 TESTANDO URLS DA API DE TELEMETRIA")
    print("=" * 60)
    
    service_lines = ['75238']
    current_date = datetime.now()
    start_date = f"03/{current_date.month:02d}/{current_date.year}"
    end_date = f"02/{current_date.month + 1:02d}/{current_date.year}" if current_date.month < 12 else f"02/01/{current_date.year + 1}"
    
    print(f"📡 Service Lines: {service_lines}")
    print(f"📅 Período: {start_date} até {end_date}")
    
    # URLs para testar
    stream_url = f"https://api.starlink.sx/telemetry/stream?account_id=ACC-2744134-64041-5&service_lines={','.join(service_lines)}&start_date={start_date}&end_date={end_date}"
    enterprise_url = f"https://api.starlink.sx/telemetry/enterprise?account_id=ACC-2744134-64041-5&service_lines={','.join(service_lines)}&start_date={start_date}&end_date={end_date}"
    
    print(f"\n🌐 Stream URL:")
    print(f"   {stream_url}")
    
    print(f"\n🏢 Enterprise URL:")
    print(f"   {enterprise_url}")
    
    # Testar Stream API
    print(f"\n🔄 TESTANDO STREAM API...")
    try:
        response = requests.get(stream_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.status_code == 200:
            print(f"   Response (primeiros 500 chars): {response.text[:500]}...")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Testar Enterprise API  
    print(f"\n🔄 TESTANDO ENTERPRISE API...")
    try:
        response = requests.get(enterprise_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.status_code == 200:
            print(f"   Response (primeiros 500 chars): {response.text[:500]}...")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Testar outras combinações
    print(f"\n🔄 TESTANDO OUTRAS SERVICE LINES...")
    for sl in ['75238', '854897', '43']:
        test_url = f"https://api.starlink.sx/telemetry/stream?account_id=ACC-2744134-64041-5&service_lines={sl}&start_date={start_date}&end_date={end_date}"
        try:
            response = requests.get(test_url, timeout=5)
            print(f"   SL {sl}: Status {response.status_code}")
            if response.status_code == 200:
                print(f"           Dados: {response.text[:100]}...")
        except:
            print(f"   SL {sl}: Erro de conexão")

if __name__ == "__main__":
    test_telemetry_apis()

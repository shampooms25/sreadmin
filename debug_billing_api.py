#!/usr/bin/env python3
"""
Script para debuggar o erro 422 na API de billing
"""

import sys
import os
sys.path.append('C:\\Projetos\\Poppnet\\sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

import django
django.setup()

import requests
import json
from painel.starlink_api import get_valid_token, get_service_lines_with_location

def test_billing_api():
    """Testa a API de billing com diferentes payloads"""
    
    account_id = "ACC-2744134-64041-5"
    print(f"🧪 Testando API de billing para conta: {account_id}")
    
    # Obter token
    token = get_valid_token()
    if not token:
        print("❌ Não foi possível obter token")
        return
    
    print("✅ Token obtido com sucesso")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # URL da API
    url = f"https://web-api.starlink.com/enterprise/v1/accounts/{account_id}/billing-cycles/query"
    print(f"🌐 URL: {url}")
    
    # Teste 1: Payload mais simples possível
    payload1 = {
        "pageIndex": 0,
        "pageLimit": 10
    }
    
    print(f"\n📋 Teste 1 - Payload simples:")
    print(json.dumps(payload1, indent=2))
    
    response1 = requests.post(url, json=payload1, headers=headers)
    print(f"📊 Status: {response1.status_code}")
    
    if response1.status_code != 200:
        print(f"❌ Erro: {response1.text}")
        print(f"📋 Headers: {dict(response1.headers)}")
    else:
        print("✅ Sucesso!")
        data = response1.json()
        print(f"📊 Keys da resposta: {list(data.keys())}")
        
    # Teste 2: Com previousBillingCycles
    payload2 = {
        "previousBillingCycles": 1,
        "pageIndex": 0,
        "pageLimit": 10
    }
    
    print(f"\n📋 Teste 2 - Com previousBillingCycles:")
    print(json.dumps(payload2, indent=2))
    
    response2 = requests.post(url, json=payload2, headers=headers)
    print(f"📊 Status: {response2.status_code}")
    
    if response2.status_code != 200:
        print(f"❌ Erro: {response2.text}")
    else:
        print("✅ Sucesso!")

if __name__ == "__main__":
    test_billing_api()

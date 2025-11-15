#!/usr/bin/env python
"""
Script de teste para o endpoint /api/captive-portal/success/
Testa o registro de visualizações de vídeos dos portais captive descentralizados.
"""

import requests
import json
from datetime import datetime

# URL base da API (ajuste conforme necessário)
API_BASE_URL = "http://localhost:8000/api/captive-portal/success/"

def test_post_json():
    """Teste com POST e JSON"""
    print("\n=== Teste 1: POST com JSON ===")
    
    payload = {
        "username": "101010",
        "video": "eld01.mp4",
        "origin": "captive_portal",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(API_BASE_URL, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Erro: {e}")

def test_post_form():
    """Teste com POST e form data"""
    print("\n=== Teste 2: POST com Form Data ===")
    
    payload = {
        "username": "202020",
        "video": "eld02.mp4",
        "origin": "beacon"
    }
    
    try:
        response = requests.post(API_BASE_URL, data=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Erro: {e}")

def test_get():
    """Teste com GET"""
    print("\n=== Teste 3: GET com Query Parameters ===")
    
    params = {
        "username": "303030",
        "video": "eld03.mp4",
        "origin": "unified_page",
        "timestamp": "2025-11-15 10:35:00"
    }
    
    try:
        response = requests.get(API_BASE_URL, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Erro: {e}")

def test_missing_username():
    """Teste sem username (deve falhar)"""
    print("\n=== Teste 4: POST sem username (erro esperado) ===")
    
    payload = {
        "video": "eld04.mp4",
        "origin": "captive_portal"
    }
    
    try:
        response = requests.post(API_BASE_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Erro: {e}")

def test_missing_video():
    """Teste sem video (deve falhar)"""
    print("\n=== Teste 5: POST sem video (erro esperado) ===")
    
    payload = {
        "username": "404040",
        "origin": "captive_portal"
    }
    
    try:
        response = requests.post(API_BASE_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Erro: {e}")

def test_cors():
    """Teste OPTIONS para CORS"""
    print("\n=== Teste 6: OPTIONS para CORS ===")
    
    try:
        response = requests.options(API_BASE_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Headers CORS:")
        print(f"  Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
        print(f"  Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods')}")
        print(f"  Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers')}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("Teste do Endpoint: /api/captive-portal/success/")
    print("=" * 60)
    
    # Executar todos os testes
    test_post_json()
    test_post_form()
    test_get()
    test_missing_username()
    test_missing_video()
    test_cors()
    
    print("\n" + "=" * 60)
    print("Testes concluídos!")
    print("=" * 60)

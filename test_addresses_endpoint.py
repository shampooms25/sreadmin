#!/usr/bin/env python3
"""
Script para testar rapidamente o endpoint /addresses da API Starlink
"""
import requests
import json
import time

# Configurações
CLIENT_ID = "498ca080-3eb2-4a4d-a5d9-3828dbef0194"
CLIENT_SECRET = "fibernetworks_api@2025"
AUTH_URL = "https://api.starlink.com/auth/connect/token"
ADDRESSES_URL = "https://web-api.starlink.com/enterprise/v1/account/ACC-2744134-64041-5/addresses"

def get_token():
    """Obter token de autenticação"""
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(AUTH_URL, data=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    return data.get("access_token")

def get_addresses_data():
    """Obter dados do endpoint /addresses"""
    token = get_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(ADDRESSES_URL, headers=headers)
    response.raise_for_status()
    
    return response.json()

if __name__ == "__main__":
    print("🔍 Testando endpoint /addresses...")
    
    try:
        data = get_addresses_data()
        
        # Analisar estrutura dos dados
        print(f"📊 Estrutura dos dados: {list(data.keys())}")
        
        if "content" in data:
            content = data["content"]
            print(f"📄 Estrutura do content: {list(content.keys())}")
            
            if "results" in content:
                results = content["results"]
                print(f"🎯 {len(results)} addresses encontrados")
                
                # Mostrar alguns exemplos
                print("\n📋 Primeiros 3 addresses:")
                for i, addr in enumerate(results[:3]):
                    print(f"\n{i+1}. Address ID: {addr.get('addressReferenceId', 'N/A')}")
                    print(f"   📍 Localização: {addr.get('locality', 'N/A')}, {addr.get('administrativeAreaCode', 'N/A')}, {addr.get('regionCode', 'N/A')}")
                    print(f"   🏠 Endereço: {addr.get('formattedAddress', 'N/A')}")
                    print(f"   📌 Coordenadas: {addr.get('latitude', 'N/A')}, {addr.get('longitude', 'N/A')}")
                    print(f"   📋 Campos disponíveis: {list(addr.keys())}")
                
                # Estatísticas
                with_locality = len([addr for addr in results if addr.get('locality')])
                with_coordinates = len([addr for addr in results if addr.get('latitude') and addr.get('longitude')])
                
                print(f"\n📈 ESTATÍSTICAS:")
                print(f"   📍 Com localidade: {with_locality}/{len(results)} ({with_locality/len(results)*100:.1f}%)")
                print(f"   📌 Com coordenadas: {with_coordinates}/{len(results)} ({with_coordinates/len(results)*100:.1f}%)")
                
                print(f"\n✅ SUCESSO! Endpoint /addresses está funcionando perfeitamente!")
                
    except Exception as e:
        print(f"❌ Erro: {e}")

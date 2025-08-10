#!/usr/bin/env python3
"""
Script de Teste da API POPPFIRE
Testa todas as funcionalidades da API para validar integração
"""

import requests
import json
import sys
from datetime import datetime

# Configurações
API_BASE_URL = "http://172.18.25.253:8000"
API_TOKEN = "test-token-123456789"  # Token de teste

def test_api():
    """Testa todas as APIs disponíveis"""
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    print("=== Teste da API POPPFIRE ===")
    print(f"Servidor: {API_BASE_URL}")
    print(f"Token: {API_TOKEN}")
    print()
    
    # 1. Testar API Info
    print("1. Testando API Info...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/appliances/info/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Info: {data.get('api_name', 'N/A')} v{data.get('version', 'N/A')}")
            print(f"   Servidor: {data.get('server_ip', 'N/A')}")
        else:
            print(f"❌ API Info falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro na API Info: {e}")
    
    print()
    
    # 2. Testar Status do Portal
    print("2. Testando Status do Portal...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/appliances/portal/status/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status', 'N/A')}")
            print(f"   Tipo: {data.get('portal_type', 'N/A')}")
            print(f"   Hash: {data.get('portal_hash', 'N/A')[:16]}...")
            print(f"   Última atualização: {data.get('last_updated', 'N/A')}")
            
            # Salvar dados para próximos testes
            portal_type = data.get('portal_type')
            portal_hash = data.get('portal_hash')
            
        else:
            print(f"❌ Status do Portal falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro no Status do Portal: {e}")
        return False
    
    print()
    
    # 3. Testar Download do Portal
    print("3. Testando Download do Portal...")
    try:
        download_url = f"{API_BASE_URL}/api/appliances/portal/download/?type={portal_type}"
        response = requests.get(download_url, headers=headers)
        
        if response.status_code == 200:
            content_length = len(response.content)
            content_type = response.headers.get('Content-Type', 'N/A')
            filename = response.headers.get('Content-Disposition', 'N/A')
            
            print(f"✅ Download concluído")
            print(f"   Tamanho: {content_length:,} bytes ({content_length/1024/1024:.2f} MB)")
            print(f"   Tipo: {content_type}")
            print(f"   Arquivo: {filename}")
            
            # Verificar se é um ZIP válido
            if content_length > 0 and response.content[:2] == b'PK':
                print(f"   ✅ Arquivo ZIP válido")
            else:
                print(f"   ⚠️ Arquivo pode não ser um ZIP válido")
                
        else:
            print(f"❌ Download falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro no Download: {e}")
    
    print()
    
    # 4. Testar Relatório de Status
    print("4. Testando Relatório de Status...")
    try:
        report_data = {
            "appliance_id": "TEST-APPLIANCE-001",
            "appliance_ip": "192.168.1.100",
            "update_status": "success",
            "portal_hash": portal_hash,
            "portal_type": portal_type,
            "update_timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/appliances/portal/update-status/",
            headers=headers,
            json=report_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Relatório enviado com sucesso")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Mensagem: {data.get('message', 'N/A')}")
        else:
            print(f"❌ Relatório falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro no Relatório: {e}")
    
    print()
    
    # 5. Testar com Token Inválido
    print("5. Testando Token Inválido...")
    try:
        invalid_headers = {
            'Authorization': 'Bearer token-invalido-123',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{API_BASE_URL}/api/appliances/info/", headers=invalid_headers)
        if response.status_code == 401:
            print(f"✅ Autenticação funcionando - Token inválido rejeitado")
        else:
            print(f"⚠️ Token inválido deveria retornar 401, mas retornou {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no teste de token inválido: {e}")
    
    print()
    print("=== Teste Concluído ===")
    return True

def test_portal_types():
    """Testa download de ambos os tipos de portal"""
    
    headers = {'Authorization': f'Bearer {API_TOKEN}'}
    
    print("=== Teste de Tipos de Portal ===")
    
    for portal_type in ['with_video', 'without_video']:
        print(f"\nTestando portal: {portal_type}")
        try:
            url = f"{API_BASE_URL}/api/appliances/portal/download/?type={portal_type}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                size_mb = len(response.content) / 1024 / 1024
                print(f"✅ {portal_type}: {size_mb:.2f} MB")
            elif response.status_code == 404:
                print(f"⚠️ {portal_type}: Não disponível")
            else:
                print(f"❌ {portal_type}: Erro {response.status_code}")
        except Exception as e:
            print(f"❌ {portal_type}: Erro {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--portal-types":
        test_portal_types()
    else:
        test_api()

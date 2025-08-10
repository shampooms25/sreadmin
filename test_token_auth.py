#!/usr/bin/env python
"""
Script para testar a autenticação de tokens da API APPLIANCE POPPFIRE
"""

import os
import sys
import requests
import json

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_token_authentication():
    """
    Testa a autenticação com o token gerado
    """
    # Carregar token do arquivo
    try:
        with open('appliance_tokens.json', 'r', encoding='utf-8') as f:
            tokens_data = json.load(f)
        
        # Pegar o primeiro token disponível
        tokens = tokens_data.get('tokens', {})
        if not tokens:
            print("❌ Nenhum token encontrado no arquivo")
            return False
        
        # Usar o primeiro token
        token = list(tokens.keys())[0]
        token_info = tokens[token]
        
        print(f"🔑 Testando token: {token}")
        print(f"📱 Appliance: {token_info['appliance_name']} ({token_info['appliance_id']})")
        
        # URL base da API (ajuste conforme necessário)
        base_url = "http://127.0.0.1:8000"  # ou http://localhost:8000 para teste local
        
        # Headers com token
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Testar endpoint de informações
        print("\n🧪 Testando endpoint /api/appliances/info/")
        try:
            response = requests.get(f"{base_url}/api/appliances/info/", headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Autenticação bem-sucedida!")
                print(f"Resposta: {response.json()}")
            else:
                print(f"❌ Erro na autenticação: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
        
        # Testar endpoint de status do portal
        print("\n🧪 Testando endpoint /api/appliances/portal/status/")
        try:
            response = requests.get(f"{base_url}/api/appliances/portal/status/", headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Endpoint de status funcionando!")
                print(f"Resposta: {response.json()}")
            else:
                print(f"❌ Erro: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
        
        return True
        
    except FileNotFoundError:
        print("❌ Arquivo appliance_tokens.json não encontrado")
        return False
    except json.JSONDecodeError:
        print("❌ Erro ao ler arquivo appliance_tokens.json")
        return False

def main():
    """
    Função principal
    """
    print("🚀 Teste de Autenticação API APPLIANCE POPPFIRE")
    print("=" * 50)
    
    test_token_authentication()

if __name__ == "__main__":
    main()

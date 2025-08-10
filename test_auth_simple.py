#!/usr/bin/env python
"""
Teste simples da autenticação da API APPLIANCE POPPFIRE
"""

import json
import os

def test_token_loading():
    """
    Testa se conseguimos carregar os tokens do JSON
    """
    print("🔍 Testando carregamento de tokens...")
    
    try:
        with open('appliance_tokens.json', 'r', encoding='utf-8') as f:
            tokens_data = json.load(f)
        
        print("✅ Arquivo JSON carregado com sucesso!")
        print(f"📊 Total de tokens: {tokens_data.get('total_tokens', 0)}")
        
        tokens = tokens_data.get('tokens', {})
        print(f"🔑 Tokens disponíveis: {len(tokens)}")
        
        for token, info in tokens.items():
            print(f"   - {info['appliance_name']} ({info['appliance_id']}): {token[:8]}...{token[-8:]}")
        
        return True, tokens
        
    except FileNotFoundError:
        print("❌ Arquivo appliance_tokens.json não encontrado!")
        return False, {}
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        return False, {}
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False, {}

def test_api_authentication_locally():
    """
    Testa a autenticação simulando a lógica da API
    """
    print("\n🧪 Testando lógica de autenticação localmente...")
    
    success, tokens = test_token_loading()
    if not success:
        return False
    
    # Simular um token de teste
    test_token = "test-token-123456789"
    
    print(f"🔑 Testando token: {test_token}")
    
    # Simular verificação da API
    if test_token in tokens:
        token_info = tokens[test_token]
        print("✅ Token válido encontrado!")
        print(f"   📱 Appliance: {token_info['appliance_name']}")
        print(f"   🆔 ID: {token_info['appliance_id']}")
        print(f"   📝 Descrição: {token_info.get('description', 'N/A')}")
        return True
    else:
        print("❌ Token não encontrado!")
        print(f"   Tokens disponíveis: {list(tokens.keys())}")
        return False

def simulate_api_request():
    """
    Simula como seria uma requisição da API
    """
    print("\n🌐 Simulando requisição da API...")
    
    # Simular headers
    auth_header = "Bearer test-token-123456789"
    
    if not auth_header.startswith('Bearer '):
        print("❌ Header de autorização inválido")
        return False
    
    token = auth_header.replace('Bearer ', '')
    print(f"🔑 Token extraído: {token}")
    
    # Carregar tokens
    try:
        with open('appliance_tokens.json', 'r', encoding='utf-8') as f:
            tokens_data = json.load(f)
        
        tokens = tokens_data.get('tokens', {})
        
        if token in tokens:
            token_info = tokens[token]
            print("✅ Autenticação bem-sucedida!")
            print(f"   👤 Usuário: {token_info['appliance_id']}")
            print(f"   📱 Nome: {token_info['appliance_name']}")
            return True
        else:
            print("❌ Token inválido")
            return False
            
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 TESTE DE AUTENTICAÇÃO API APPLIANCE POPPFIRE")
    print("=" * 55)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('appliance_tokens.json'):
        print("❌ Arquivo appliance_tokens.json não encontrado no diretório atual!")
        print(f"   Diretório atual: {os.getcwd()}")
        print("   Certifique-se de estar no diretório do projeto.")
        return False
    
    # Teste 1: Carregamento de tokens
    success1 = test_token_loading()[0]
    
    # Teste 2: Autenticação local
    success2 = test_api_authentication_locally()
    
    # Teste 3: Simulação de requisição
    success3 = simulate_api_request()
    
    print(f"\n📊 RESULTADOS:")
    print(f"   Carregamento de tokens: {'✅' if success1 else '❌'}")
    print(f"   Autenticação local: {'✅' if success2 else '❌'}")
    print(f"   Simulação de requisição: {'✅' if success3 else '❌'}")
    
    if all([success1, success2, success3]):
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("   A lógica de autenticação está funcionando corretamente.")
        print("   Agora você pode testar com o servidor Django rodando.")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        print("   Verifique os erros acima e corrija antes de prosseguir.")
    
    return all([success1, success2, success3])

if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Teste para descobrir endpoints de billing/usage da API Starlink
"""
import os
import sys
import django
import requests
import json

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

# Configurar Django
django.setup()

def test_billing_endpoints():
    """
    Testa diferentes endpoints para encontrar dados de billing/usage
    """
    print("=== TESTE: Endpoints de Billing/Usage da API Starlink ===")
    print()
    
    try:
        from painel.starlink_api import get_valid_token
        
        # Dados de teste
        account_id = "ACC-2744134-64041-5"
        service_line_number = "SL-854897-75238-43"
        
        print(f"📋 DADOS DO TESTE:")
        print(f"   Conta: {account_id}")
        print(f"   Service Line: {service_line_number}")
        print()
        
        # Obter token
        token = get_valid_token()
        if not token:
            print("❌ ERRO: Token não disponível")
            return False
        
        print(f"✅ Token obtido: {token[:20]}...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Endpoints para testar
        endpoints_to_test = [
            {
                "name": "Billing Cycles Query",
                "url": f"https://web-api.starlink.com/enterprise/v1/accounts/{account_id}/billing-cycles/query",
                "method": "POST",
                "payload": {
                    "serviceLinesFilter": [service_line_number],
                    "previousBillingCycles": 3,
                    "pageIndex": 0,
                    "pageLimit": 10
                }
            },
            {
                "name": "Service Line Details",
                "url": f"https://web-api.starlink.com/enterprise/v1/account/{account_id}/service-lines/{service_line_number}",
                "method": "GET",
                "payload": None
            },
            {
                "name": "Service Line Usage/Data",
                "url": f"https://web-api.starlink.com/enterprise/v1/account/{account_id}/service-lines/{service_line_number}/usage",
                "method": "GET",
                "payload": None
            },
            {
                "name": "Service Line Billing",
                "url": f"https://web-api.starlink.com/enterprise/v1/account/{account_id}/service-lines/{service_line_number}/billing",
                "method": "GET",
                "payload": None
            },
            {
                "name": "Service Line Data Usage",
                "url": f"https://web-api.starlink.com/enterprise/v1/account/{account_id}/service-lines/{service_line_number}/data-usage",
                "method": "GET",
                "payload": None
            }
        ]
        
        for endpoint in endpoints_to_test:
            print(f"🔍 TESTANDO: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            print(f"   Método: {endpoint['method']}")
            
            try:
                if endpoint['method'] == 'GET':
                    response = requests.get(endpoint['url'], headers=headers)
                else:
                    response = requests.post(endpoint['url'], json=endpoint['payload'], headers=headers)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCESSO!")
                    
                    # Salvar resposta para análise
                    filename = f"api_response_{endpoint['name'].replace(' ', '_').lower()}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"   📄 Resposta salva em: {filename}")
                    
                    # Procurar por campos relevantes
                    response_str = json.dumps(data, ensure_ascii=False).lower()
                    relevant_fields = ['priority', 'standard', 'data', 'usage', 'consumption', 'gb', 'tb', 'bytes']
                    
                    found_fields = [field for field in relevant_fields if field in response_str]
                    if found_fields:
                        print(f"   🎯 Campos relevantes encontrados: {found_fields}")
                    
                elif response.status_code == 404:
                    print(f"   ❌ ENDPOINT NÃO EXISTE")
                else:
                    print(f"   ⚠️  ERRO: {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"   Erro: {error_data.get('message', 'N/A')}")
                    except:
                        print(f"   Erro: {response.text[:200]}...")
                
            except Exception as e:
                print(f"   ❌ ERRO DE CONEXÃO: {str(e)}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DE ENDPOINTS DE BILLING/USAGE...")
    print()
    
    success = test_billing_endpoints()
    
    print()
    print("=" * 80)
    if success:
        print("🎉 TESTE CONCLUÍDO!")
        print("   Verifique os arquivos JSON gerados para analisar as respostas")
        print("   Procure por campos como 'priority', 'standard', 'data', 'usage'")
    else:
        print("❌ TESTE FALHOU!")
        print("   Verifique os erros acima")
    
    print("=" * 80)
    
    sys.exit(0 if success else 1)

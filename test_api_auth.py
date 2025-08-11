#!/usr/bin/env python
"""
Script para testar a API e verificar autenticação
"""

import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from captive_portal.models import ApplianceToken
from django.test import RequestFactory
from captive_portal.api_views import ApplianceAPIAuthentication, api_info

def test_token_authentication():
    print("🔍 Verificando tokens no banco de dados...")
    
    # Listar todos os tokens
    tokens = ApplianceToken.objects.all()
    print(f"Total de tokens: {tokens.count()}")
    
    if tokens.count() == 0:
        print("❌ Nenhum token encontrado no banco!")
        print("🔧 Criando token de teste...")
        
        # Criar token de teste
        test_token = ApplianceToken.objects.create(
            token='c8c786467d4a8d2825eaf549534d1ab0',
            appliance_id='POSTMAN-TEST',
            appliance_name='Appliance Teste Postman',
            description='Token para testes via Postman',
            is_active=True
        )
        print(f"✅ Token criado: {test_token.appliance_name}")
        tokens = ApplianceToken.objects.all()
    
    for token in tokens:
        print(f"Token: {token.token[:15]}... | Appliance: {token.appliance_name} | Ativo: {token.is_active}")
    
    # Testar autenticação com o token do Postman
    print("\n🧪 Testando autenticação...")
    test_token = 'c8c786467d4a8d2825eaf549534d1ab0'
    
    # Criar request factory
    factory = RequestFactory()
    request = factory.get('/api/appliances/info/', HTTP_AUTHORIZATION=f'Bearer {test_token}')
    
    # Testar autenticação
    is_valid, result = ApplianceAPIAuthentication.verify_token(request)
    
    if is_valid:
        print(f"✅ Autenticação OK - Appliance: {result.appliance_name}")
        print(f"   Username: {result.username}")
    else:
        print(f"❌ Erro na autenticação: {result}")
        return False
    
    # Testar endpoint da API
    print("\n🌐 Testando endpoint api_info...")
    try:
        response = api_info(request)
        print(f"✅ API Response Status: {response.status_code}")
        
        if hasattr(response, 'content'):
            content = json.loads(response.content.decode('utf-8'))
            print("✅ Conteúdo da resposta:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        import traceback
        traceback.print_exc()
    
    return True

if __name__ == '__main__':
    print("🚀 Teste de Autenticação da API POPPFIRE")
    print("=" * 50)
    test_token_authentication()
    print("\n" + "=" * 50)
    print("✅ Teste concluído!")
    print("\n🔧 Para testar no Postman:")
    print("   URL: http://127.0.0.1:8000/api/appliances/info/")
    print("   Method: GET")
    print("   Header: Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0")

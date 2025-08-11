#!/usr/bin/env python
"""
Teste direto da autenticação - sem servidor externo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.test import RequestFactory
from captive_portal.models import ApplianceToken
from captive_portal.api_views import api_info, ApplianceAPIAuthentication

def test_direct():
    print("🧪 TESTE DIRETO DE AUTENTICAÇÃO")
    print("=" * 40)
    
    # 1. Criar/verificar token
    token = 'c8c786467d4a8d2825eaf549534d1ab0'
    
    obj, created = ApplianceToken.objects.get_or_create(
        token=token,
        defaults={
            'appliance_id': 'POSTMAN-TEST',
            'appliance_name': 'Appliance Teste Postman',
            'description': 'Token para testes via Postman',
            'is_active': True,
        }
    )
    
    print(f"Token: {token}")
    print(f"Appliance: {obj.appliance_name}")
    print(f"Ativo: {obj.is_active}")
    print(f"Criado agora: {created}")
    
    # 2. Criar request simulado
    factory = RequestFactory()
    request = factory.get(
        '/api/appliances/info/',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    print(f"\nHeader Authorization: Bearer {token}")
    print(f"HTTP_AUTHORIZATION no META: {request.META.get('HTTP_AUTHORIZATION', 'NÃO ENCONTRADO')}")
    
    # 3. Testar autenticação
    print("\n🔐 TESTANDO AUTENTICAÇÃO:")
    is_valid, result = ApplianceAPIAuthentication.verify_token(request)
    
    if is_valid:
        print(f"✅ Autenticação OK!")
        print(f"   Appliance ID: {result.username}")
        print(f"   Appliance Name: {result.appliance_name}")
        
        # 4. Testar API endpoint
        print("\n🌐 TESTANDO ENDPOINT API_INFO:")
        try:
            request.appliance_user = result  # Simular o que o decorator faz
            response = api_info(request)
            print(f"✅ Status Code: {response.status_code}")
            
            import json
            content = json.loads(response.content.decode('utf-8'))
            print("✅ Resposta JSON:")
            for key, value in content.items():
                print(f"   {key}: {value}")
                
        except Exception as e:
            print(f"❌ Erro no endpoint: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Autenticação falhou: {result}")
    
    print("\n" + "=" * 40)
    print("🎯 CONFIGURAÇÃO PARA POSTMAN:")
    print(f"   URL: http://127.0.0.1:8000/api/appliances/info/")
    print(f"   Method: GET")
    print(f"   Header: Authorization")
    print(f"   Value: Bearer {token}")
    print("\n💡 Certifique-se que o servidor Django está rodando!")
    print("   Comando: python manage.py runserver 127.0.0.1:8000")

if __name__ == '__main__':
    test_direct()

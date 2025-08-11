#!/usr/bin/env python
"""
Teste rápido de token e autenticação - Windows
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from captive_portal.models import ApplianceToken

def test_token():
    print("🔍 Testando token no Windows...")
    
    # Token que você está usando no Postman
    test_token = 'c8c786467d4a8d2825eaf549534d1ab0'
    
    # Criar/verificar token
    obj, created = ApplianceToken.objects.get_or_create(
        token=test_token,
        defaults={
            'appliance_id': 'POSTMAN-TEST',
            'appliance_name': 'Appliance Teste Postman',
            'description': 'Token para testes via Postman',
            'is_active': True,
        }
    )
    
    print(f"Token: {test_token}")
    print(f"Appliance: {obj.appliance_name}")
    print(f"Ativo: {obj.is_active}")
    print(f"Criado agora: {created}")
    
    # Verificar se pode ser encontrado
    try:
        found = ApplianceToken.objects.get(token=test_token, is_active=True)
        print(f"✅ Token encontrado: {found.appliance_name}")
        return True
    except ApplianceToken.DoesNotExist:
        print("❌ Token não encontrado!")
        return False

def test_auth_logic():
    print("\n🧪 Testando lógica de autenticação...")
    
    from captive_portal.api_views import ApplianceAPIAuthentication
    from unittest.mock import Mock
    
    # Simular request
    mock_request = Mock()
    mock_request.META = {
        'HTTP_AUTHORIZATION': 'Bearer c8c786467d4a8d2825eaf549534d1ab0',
        'REMOTE_ADDR': '127.0.0.1'
    }
    
    try:
        is_valid, result = ApplianceAPIAuthentication.verify_token(mock_request)
        
        if is_valid:
            print(f"✅ Autenticação OK: {result.appliance_name}")
            return True
        else:
            print(f"❌ Falha: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == '__main__':
    print("🪟 Teste Rápido - Windows")
    print("=" * 30)
    
    token_ok = test_token()
    auth_ok = test_auth_logic()
    
    print("\n" + "=" * 30)
    
    if token_ok and auth_ok:
        print("✅ TUDO OK! O problema pode ser:")
        print("   1. Servidor Django não está rodando")
        print("   2. URL incorreta no Postman")
        print("   3. Header mal formatado")
        print("")
        print("🚀 Para testar:")
        print("   1. Execute: python manage.py runserver 127.0.0.1:8000")
        print("   2. URL: http://127.0.0.1:8000/api/appliances/info/")
        print("   3. Header: Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0")
    else:
        print("❌ Há problemas na configuração!")

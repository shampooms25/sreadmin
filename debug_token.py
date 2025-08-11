#!/usr/bin/env python
"""
Teste específico para debug da autenticação
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from captive_portal.models import ApplianceToken

# 1. Criar token se não existe
token = 'c8c786467d4a8d2825eaf549534d1ab0'

print("🔧 Criando/verificando token...")
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

if not obj.is_active:
    obj.is_active = True
    obj.save()
    print("✅ Token reativado!")

# 2. Testar busca do token
print("\n🔍 Testando busca do token...")
try:
    found_token = ApplianceToken.objects.get(token=token, is_active=True)
    print(f"✅ Token encontrado: {found_token.appliance_name}")
except ApplianceToken.DoesNotExist:
    print("❌ Token não encontrado no banco!")
    sys.exit(1)

# 3. Testar função de autenticação manualmente
print("\n🔐 Testando autenticação manual...")

from captive_portal.api_views import ApplianceAPIAuthentication
from unittest.mock import Mock

# Simular request
mock_request = Mock()
mock_request.META = {
    'HTTP_AUTHORIZATION': f'Bearer {token}',
    'REMOTE_ADDR': '127.0.0.1'
}

print(f"Authorization header: {mock_request.META['HTTP_AUTHORIZATION']}")

# Testar autenticação
is_valid, result = ApplianceAPIAuthentication.verify_token(mock_request)

if is_valid:
    print(f"✅ Autenticação OK!")
    print(f"   Appliance ID: {result.username}")
    print(f"   Appliance Name: {result.appliance_name}")
    print(f"   Is Authenticated: {result.is_authenticated}")
else:
    print(f"❌ Autenticação falhou: {result}")

print("\n" + "="*50)
print("🎯 PARA TESTAR NO POSTMAN:")
print("="*50)
print(f"URL: http://127.0.0.1:8000/api/appliances/info/")
print(f"Method: GET")
print(f"Header Name: Authorization")
print(f"Header Value: Bearer {token}")
print("\n💡 Certifique-se que o servidor está rodando:")
print("   python manage.py runserver 127.0.0.1:8000")

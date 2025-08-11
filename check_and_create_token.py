#!/usr/bin/env python
"""
Script para verificar e criar token de teste para Postman
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from captive_portal.models import ApplianceToken

def main():
    print("🔍 Verificando tokens no banco de dados...")
    
    # Verificar tokens existentes
    tokens = ApplianceToken.objects.all()
    print(f"Total de tokens no banco: {tokens.count()}")
    
    for token in tokens:
        print(f"Token: {token.token[:10]}... | Appliance: {token.appliance_name} | Ativo: {token.is_active}")
    
    # Token específico do Postman
    test_token = 'c8c786467d4a8d2825eaf549534d1ab0'
    
    try:
        token_obj = ApplianceToken.objects.get(token=test_token)
        print(f"✅ Token do Postman já existe: {token_obj.appliance_name} - Ativo: {token_obj.is_active}")
        
        if not token_obj.is_active:
            token_obj.is_active = True
            token_obj.save()
            print("✅ Token reativado!")
            
    except ApplianceToken.DoesNotExist:
        print("❌ Token do Postman não encontrado - Criando...")
        new_token = ApplianceToken.objects.create(
            token=test_token,
            appliance_id='POSTMAN-TEST',
            appliance_name='Appliance Teste Postman',
            description='Token para testes via Postman',
            is_active=True
        )
        print(f"✅ Token criado: {new_token.appliance_name}")
    
    print("\n🌐 Teste da API:")
    print("URL: http://localhost:8000/api/appliances/info/")
    print(f"Header: Authorization: Bearer {test_token}")
    
    # Testar a autenticação internamente
    print("\n🔧 Testando autenticação...")
    try:
        from captive_portal.api_views import ApplianceAPIAuthentication
        from unittest.mock import Mock
        
        # Simular request
        mock_request = Mock()
        mock_request.META = {
            'HTTP_AUTHORIZATION': f'Bearer {test_token}',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        is_valid, result = ApplianceAPIAuthentication.verify_token(mock_request)
        
        if is_valid:
            print(f"✅ Autenticação OK - Appliance: {result.appliance_name}")
        else:
            print(f"❌ Erro na autenticação: {result}")
            
    except Exception as e:
        print(f"❌ Erro ao testar autenticação: {e}")

if __name__ == '__main__':
    main()

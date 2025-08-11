#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from captive_portal.models import ApplianceToken
from captive_portal.api_views import ApplianceAPIAuthentication
from unittest.mock import Mock

def diagnose_auth():
    print("=== DIAGNÓSTICO DE AUTENTICAÇÃO ===")
    
    # 1. Verificar tokens no banco
    print("\n1. TOKENS NO BANCO DE DADOS:")
    tokens = ApplianceToken.objects.all()
    print(f"   Total: {tokens.count()}")
    
    if tokens.count() == 0:
        print("   ❌ NENHUM TOKEN ENCONTRADO!")
        print("   🔧 Criando token de teste...")
        test_token = ApplianceToken.objects.create(
            token='c8c786467d4a8d2825eaf549534d1ab0',
            appliance_id='POSTMAN-TEST',
            appliance_name='Appliance Teste Postman',
            description='Token para testes via Postman',
            is_active=True
        )
        print(f"   ✅ Token criado: {test_token.token}")
        tokens = ApplianceToken.objects.all()
    
    for token in tokens:
        print(f"   - {token.token[:20]}... | {token.appliance_name} | Ativo: {token.is_active}")
    
    # 2. Testar token específico
    test_token = 'c8c786467d4a8d2825eaf549534d1ab0'
    print(f"\n2. TESTANDO TOKEN ESPECÍFICO: {test_token[:20]}...")
    
    try:
        token_obj = ApplianceToken.objects.get(token=test_token, is_active=True)
        print(f"   ✅ Token encontrado: {token_obj.appliance_name}")
    except ApplianceToken.DoesNotExist:
        print("   ❌ Token não encontrado ou inativo!")
        return
    
    # 3. Simular request do Postman
    print("\n3. SIMULANDO REQUEST DO POSTMAN:")
    mock_request = Mock()
    mock_request.META = {
        'HTTP_AUTHORIZATION': f'Bearer {test_token}',
        'REMOTE_ADDR': '127.0.0.1'
    }
    
    print(f"   Authorization Header: Bearer {test_token[:20]}...")
    print(f"   IP Address: 127.0.0.1")
    
    # 4. Testar autenticação
    print("\n4. RESULTADO DA AUTENTICAÇÃO:")
    try:
        is_valid, result = ApplianceAPIAuthentication.verify_token(mock_request)
        
        if is_valid:
            print(f"   ✅ SUCESSO!")
            print(f"   - Appliance ID: {result.username}")
            print(f"   - Appliance Name: {result.appliance_name}")
            print(f"   - Is Authenticated: {result.is_authenticated}")
        else:
            print(f"   ❌ FALHA: {result}")
            
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Verificar configurações
    print("\n5. VERIFICAÇÕES ADICIONAIS:")
    print(f"   - Django settings carregados: {'sreadmin.settings' in os.environ.get('DJANGO_SETTINGS_MODULE', '')}")
    
    # Verificar se existe appliance_tokens.json
    import django.conf
    tokens_file = os.path.join(django.conf.settings.BASE_DIR, 'appliance_tokens.json')
    print(f"   - Arquivo appliance_tokens.json existe: {os.path.exists(tokens_file)}")
    
    print("\n=== FIM DO DIAGNÓSTICO ===")
    print(f"\n🧪 TESTE NO POSTMAN:")
    print(f"   URL: http://127.0.0.1:8000/api/appliances/info/")
    print(f"   Method: GET")
    print(f"   Header: Authorization: Bearer {test_token}")

if __name__ == '__main__':
    diagnose_auth()

#!/usr/bin/env python
"""
Script para criar token e testar API - Funciona em Windows e Linux
"""

import os
import sys
import platform
import django

# Detectar sistema operacional
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

print(f"🖥️ Sistema detectado: {platform.system()}")
print(f"🐍 Python: {sys.version}")

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from captive_portal.models import ApplianceToken
from captive_portal.api_views import ApplianceAPIAuthentication
from django.test import RequestFactory
import json

def create_test_token():
    """Criar token de teste específico para Postman"""
    test_token = 'c8c786467d4a8d2825eaf549534d1ab0'
    
    print("\n🔧 Criando/Verificando token de teste...")
    
    obj, created = ApplianceToken.objects.get_or_create(
        token=test_token,
        defaults={
            'appliance_id': 'POSTMAN-TEST',
            'appliance_name': 'Appliance Teste Postman',
            'description': 'Token para testes via Postman - Multiplataforma',
            'is_active': True,
        }
    )
    
    if created:
        print(f"✅ Token criado: {obj.appliance_name}")
    else:
        print(f"ℹ️ Token já existe: {obj.appliance_name}")
        
        # Garantir que está ativo
        if not obj.is_active:
            obj.is_active = True
            obj.save()
            print("✅ Token reativado!")
    
    return obj

def test_authentication(token):
    """Testar autenticação multiplataforma"""
    print("\n🧪 Testando autenticação...")
    
    # Criar request simulado
    factory = RequestFactory()
    request = factory.get(
        '/api/appliances/info/',
        HTTP_AUTHORIZATION=f'Bearer {token.token}',
        REMOTE_ADDR='127.0.0.1'
    )
    
    # Debugging: mostrar headers
    print(f"📋 Headers de teste:")
    print(f"   Authorization: Bearer {token.token[:20]}...")
    print(f"   Remote Address: 127.0.0.1")
    
    # Testar autenticação
    try:
        is_valid, result = ApplianceAPIAuthentication.verify_token(request)
        
        if is_valid:
            print(f"✅ Autenticação OK!")
            print(f"   - Appliance ID: {result.username}")
            print(f"   - Appliance Name: {result.appliance_name}")
            print(f"   - Authenticated: {result.is_authenticated}")
            return True
        else:
            print(f"❌ Falha na autenticação: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint(token):
    """Testar endpoint da API"""
    print("\n🌐 Testando endpoint da API...")
    
    try:
        from captive_portal.api_views import api_info
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get(
            '/api/appliances/info/',
            HTTP_AUTHORIZATION=f'Bearer {token.token}'
        )
        
        # Adicionar usuário simulado (bypass da autenticação para teste)
        class MockUser:
            def __init__(self):
                self.username = token.appliance_id
                self.appliance_name = token.appliance_name
                self.is_authenticated = True
        
        request.appliance_user = MockUser()
        
        # Testar API
        response = api_info(request)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if hasattr(response, 'content'):
            content = json.loads(response.content.decode('utf-8'))
            print("✅ Resposta da API:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da API: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_server_instructions():
    """Instruções específicas para cada sistema"""
    print("\n📋 Instruções para iniciar servidor:")
    
    if IS_WINDOWS:
        print("🪟 Windows:")
        print("   python manage.py runserver 127.0.0.1:8000")
        print("   ou")
        print("   python manage.py runserver 0.0.0.0:8000")
        
    elif IS_LINUX:
        print("🐧 Linux:")
        print("   python manage.py runserver 0.0.0.0:8000")
        print("   ou em background:")
        print("   nohup python manage.py runserver 0.0.0.0:8000 &")
        
    print("\n🧪 URLs de teste:")
    if IS_WINDOWS:
        print("   Desenvolvimento: http://127.0.0.1:8000/api/appliances/info/")
        print("   Rede local: http://localhost:8000/api/appliances/info/")
    else:
        print("   Produção: http://SEU-IP:8000/api/appliances/info/")
        print("   Local: http://127.0.0.1:8000/api/appliances/info/")

def check_differences():
    """Verificar diferenças entre ambientes"""
    print("\n🔍 Verificando diferenças de ambiente...")
    
    # Verificar estrutura de diretórios
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Diretório base: {base_dir}")
    
    # Verificar arquivo de tokens JSON
    json_file = os.path.join(base_dir, 'appliance_tokens.json')
    print(f"📄 appliance_tokens.json: {'✅ Existe' if os.path.exists(json_file) else '❌ Não existe'}")
    
    # Verificar permissões (Linux)
    if IS_LINUX:
        try:
            import stat
            if os.path.exists(json_file):
                file_stat = os.stat(json_file)
                permissions = stat.filemode(file_stat.st_mode)
                print(f"🔐 Permissões do JSON: {permissions}")
        except:
            print("⚠️ Não foi possível verificar permissões")
    
    # Verificar banco de dados
    try:
        count = ApplianceToken.objects.count()
        print(f"🗄️ Tokens no banco: {count}")
    except Exception as e:
        print(f"❌ Erro no banco: {e}")

def main():
    print("🚀 Teste de API POPPFIRE - Multiplataforma")
    print("=" * 50)
    
    # Verificar diferenças de ambiente
    check_differences()
    
    # Criar token de teste
    token = create_test_token()
    
    # Testar autenticação
    auth_ok = test_authentication(token)
    
    # Testar API se autenticação OK
    if auth_ok:
        test_api_endpoint(token)
    
    # Mostrar instruções
    get_server_instructions()
    
    print("\n" + "=" * 50)
    print("✅ Teste concluído!")
    
    print(f"\n🔑 Token para Postman: {token.token}")
    print("📋 Header necessário:")
    print(f"   Authorization: Bearer {token.token}")
    
    if IS_WINDOWS:
        print("\n⚠️ ATENÇÃO - Windows:")
        print("   - Use 127.0.0.1 ou localhost")
        print("   - Certifique-se que o servidor está rodando")
        print("   - Verifique se não há firewall bloqueando")
    else:
        print("\n⚠️ ATENÇÃO - Linux:")
        print("   - Use o IP correto do servidor")
        print("   - Verifique permissões de arquivos")
        print("   - Confirme que a porta 8000 está liberada")

if __name__ == '__main__':
    main()

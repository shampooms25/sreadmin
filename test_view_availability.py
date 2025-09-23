#!/usr/bin/env python
import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

import django
django.setup()

# Importar a função
from painel.views import starlink_availability_selection
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def test_view():
    """Testa a view diretamente"""
    print("🧪 TESTE: View starlink_availability_selection")
    print("=" * 60)
    
    # Criar factory de requisições
    factory = RequestFactory()
    
    # Criar requisição GET
    request = factory.get('/test/?account_id=ACC-2744134-64041-5')
    
    # Criar usuário fake com is_staff=True
    class FakeUser:
        is_active = True
        is_staff = True
        is_authenticated = True
    
    request.user = FakeUser()
    
    try:
        # Chamar a view diretamente (sem decorator)
        from painel.views import starlink_availability_selection
        
        # Remover temporariamente o decorator para teste
        response = starlink_availability_selection.__wrapped__(request)
        
        print("✅ View executada com sucesso")
        print(f"📊 Status Code: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_view()

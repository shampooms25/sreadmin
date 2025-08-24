#!/usr/bin/env python
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

# Testar a API diretamente
API_BASE_URL = "https://paineleld.poppnet.com.br"
API_TOKEN = "884f88da2e8a947500ceb4af1dafa10d"

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'User-Agent': 'OpnSense-Portal-Updater/1.0'
}

print("=== Teste API Status ===")
try:
    response = requests.get(f"{API_BASE_URL}/api/appliances/portal/status/", headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        portal_type = data.get('portal_type')
        print(f"\nTipo de portal detectado: {portal_type}")
        
        print("\n=== Teste API Download ===")
        download_response = requests.get(f"{API_BASE_URL}/api/appliances/portal/download/?type={portal_type}", headers=headers, timeout=30)
        print(f"Download Status Code: {download_response.status_code}")
        print(f"Download Response: {download_response.text[:500]}...")
    
except Exception as e:
    print(f"Erro: {e}")

# Verificar localmente qual API view está sendo usada
print("\n=== Teste Local ===")
from captive_portal.api_views import portal_status, portal_download
from django.test import RequestFactory
from captive_portal.models import ApplianceUser

factory = RequestFactory()

# Simular uma requisição
request = factory.get('/api/appliances/portal/status/')
request.appliance_user = ApplianceUser.objects.first()

print("Testando portal_status localmente...")
try:
    from django.http import JsonResponse
    response = portal_status(request)
    if isinstance(response, JsonResponse):
        print(f"Status: {response.status_code}")
        import json
        content = json.loads(response.content.decode())
        print(f"Content: {content}")
        
        portal_type = content.get('portal_type')
        if portal_type:
            print(f"\nTestando portal_download para tipo: {portal_type}")
            download_request = factory.get(f'/api/appliances/portal/download/?type={portal_type}')
            download_request.appliance_user = ApplianceUser.objects.first()
            download_response = portal_download(download_request)
            print(f"Download Status: {download_response.status_code}")
            if hasattr(download_response, 'content'):
                print(f"Content Length: {len(download_response.content)}")
    
except Exception as e:
    print(f"Erro no teste local: {e}")
    import traceback
    traceback.print_exc()

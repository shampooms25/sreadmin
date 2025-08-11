#!/usr/bin/env python
"""
Teste de API POPPFIRE - Corrigindo problema de HTTPS/HTTP
"""

import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from captive_portal.models import ApplianceToken

def create_token():
    """Criar token para teste"""
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
    
    print(f"✅ Token configurado: {obj.appliance_name} (Ativo: {obj.is_active})")
    return token

def test_endpoints(token):
    """Testar todos os endpoints da API"""
    
    # Base URL correta (HTTP, não HTTPS)
    base_url = "http://localhost:8000"  # ou http://127.0.0.1:8000
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        {
            'name': 'API Info',
            'url': f'{base_url}/api/appliances/info/',
            'method': 'GET'
        },
        {
            'name': 'Portal Status',
            'url': f'{base_url}/api/appliances/portal/status/',
            'method': 'GET'
        },
        {
            'name': 'Portal Download - With Video',
            'url': f'{base_url}/api/appliances/portal/download/?type=with_video',
            'method': 'GET'
        },
        {
            'name': 'Portal Download - Without Video',
            'url': f'{base_url}/api/appliances/portal/download/?type=without_video',
            'method': 'GET'
        },
        {
            'name': 'Portal Download - Auto',
            'url': f'{base_url}/api/appliances/portal/download/?type=auto',
            'method': 'GET'
        }
    ]
    
    print(f"\n🧪 Testando endpoints da API...")
    print(f"🌐 Base URL: {base_url}")
    print(f"🔑 Token: {token[:20]}...")
    print("-" * 60)
    
    for endpoint in endpoints:
        print(f"\n📡 {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        try:
            response = requests.get(endpoint['url'], headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCESSO")
                
                # Se for download, mostrar informações do arquivo
                if 'download' in endpoint['url']:
                    content_type = response.headers.get('Content-Type', '')
                    content_length = response.headers.get('Content-Length', 'Desconhecido')
                    filename = response.headers.get('Content-Disposition', '')
                    
                    print(f"   📁 Tipo: {content_type}")
                    print(f"   📏 Tamanho: {content_length} bytes")
                    print(f"   📄 Arquivo: {filename}")
                    
                    # Headers customizados
                    portal_type = response.headers.get('X-Portal-Type', '')
                    portal_hash = response.headers.get('X-Portal-Hash', '')
                    if portal_type:
                        print(f"   🎯 Tipo Portal: {portal_type}")
                    if portal_hash:
                        print(f"   🔐 Hash: {portal_hash[:16]}...")
                else:
                    # Se for JSON, mostrar conteúdo
                    try:
                        data = response.json()
                        print(f"   📋 Resposta: {json.dumps(data, indent=4, ensure_ascii=False)[:200]}...")
                    except:
                        print(f"   📋 Conteúdo: {response.text[:100]}...")
                        
            elif response.status_code == 401:
                print("   ❌ ERRO 401 - Não autorizado")
                try:
                    error_data = response.json()
                    print(f"   💬 Mensagem: {error_data.get('message', 'N/A')}")
                except:
                    print(f"   💬 Resposta: {response.text}")
                    
            elif response.status_code == 404:
                print("   ⚠️ ERRO 404 - Não encontrado")
                try:
                    error_data = response.json()
                    print(f"   💬 Mensagem: {error_data.get('message', 'N/A')}")
                except:
                    print(f"   💬 Resposta: {response.text}")
                    
            else:
                print(f"   ❌ ERRO {response.status_code}")
                print(f"   💬 Resposta: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ ERRO DE CONEXÃO - Servidor não está rodando?")
            print("   💡 Execute: python manage.py runserver 127.0.0.1:8000")
            
        except requests.exceptions.SSLError as e:
            print("   ❌ ERRO SSL - Use HTTP, não HTTPS!")
            print(f"   💬 Erro: {str(e)[:100]}...")
            
        except Exception as e:
            print(f"   ❌ ERRO: {str(e)}")

def show_correct_urls():
    """Mostrar URLs corretas para teste"""
    print("\n" + "="*60)
    print("🎯 URLS CORRETAS PARA TESTE:")
    print("="*60)
    
    print("\n🖥️ Para Postman/Browser:")
    print("   ❌ ERRADO: https://localhost:8000/...")
    print("   ✅ CORRETO: http://localhost:8000/...")
    print("   ✅ CORRETO: http://127.0.0.1:8000/...")
    
    print("\n📡 Endpoints disponíveis:")
    endpoints = [
        "http://localhost:8000/api/appliances/info/",
        "http://localhost:8000/api/appliances/portal/status/",
        "http://localhost:8000/api/appliances/portal/download/?type=with_video",
        "http://localhost:8000/api/appliances/portal/download/?type=without_video",
        "http://localhost:8000/admin/"
    ]
    
    for url in endpoints:
        print(f"   • {url}")
    
    print("\n🔑 Header necessário:")
    print("   Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0")
    
    print("\n🚀 Para iniciar servidor:")
    print("   python manage.py runserver 127.0.0.1:8000")

def main():
    print("🔧 CORREÇÃO DE PROBLEMA SSL/HTTPS")
    print("="*50)
    
    # Criar token
    token = create_token()
    
    # Testar endpoints
    test_endpoints(token)
    
    # Mostrar URLs corretas
    show_correct_urls()
    
    print("\n" + "="*50)
    print("✅ Teste concluído!")
    print("\n💡 PROBLEMA PRINCIPAL:")
    print("   Você estava usando HTTPS mas o Django roda em HTTP")
    print("   Use http://localhost:8000 em vez de https://localhost:8000")

if __name__ == '__main__':
    main()

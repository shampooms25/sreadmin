#!/usr/bin/env python
"""
Script para testar a API de portal sem vídeo após correções
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.models import EldPortalSemVideo
from captive_portal.api_views import portal_status, portal_download
from django.test import RequestFactory
import json

def test_portal_api():
    print("=== Teste API Portal sem Vídeo ===")
    
    # Verificar modelo
    portal = EldPortalSemVideo.objects.filter(ativo=True).first()
    if not portal:
        print("❌ Nenhum portal sem vídeo ativo encontrado")
        return False
    
    print(f"Portal ativo: {portal.nome}")
    print(f"Arquivo: {portal.arquivo_zip.name}")
    print(f"Path: {portal.arquivo_zip.path}")
    print(f"Existe: {os.path.exists(portal.arquivo_zip.path)}")
    
    # Testar API
    factory = RequestFactory()
    
    # Simular autenticação (assumindo que existe um ApplianceUser)
    try:
        from captive_portal.models import ApplianceUser
        appliance_user = ApplianceUser.objects.first()
        if not appliance_user:
            print("⚠️  Nenhum ApplianceUser encontrado - criando mock")
            appliance_user = type('MockUser', (), {'username': 'test-appliance'})()
    except ImportError:
        print("⚠️  ApplianceUser não disponível - usando mock")
        appliance_user = type('MockUser', (), {'username': 'test-appliance'})()
    
    # Teste 1: Status
    print("\n--- Teste portal_status ---")
    try:
        request = factory.get('/api/appliances/portal/status/')
        request.appliance_user = appliance_user
        
        response = portal_status(request)
        print(f"Status Code: {response.status_code}")
        
        if hasattr(response, 'content'):
            content = json.loads(response.content.decode())
            print(f"Portal Type: {content.get('portal_type')}")
            print(f"Status: {content.get('status')}")
            
            if content.get('portal_type') == 'without_video':
                print("✅ API retornou portal sem vídeo corretamente")
            else:
                print("❌ API não retornou portal sem vídeo")
                return False
    except Exception as e:
        print(f"❌ Erro no teste de status: {e}")
        return False
    
    # Teste 2: Download
    print("\n--- Teste portal_download ---")
    try:
        request = factory.get('/api/appliances/portal/download/?type=without_video')
        request.appliance_user = appliance_user
        
        response = portal_download(request)
        print(f"Download Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Download funcionando corretamente")
            if hasattr(response, 'content'):
                print(f"Content Length: {len(response.content)} bytes")
            return True
        else:
            if hasattr(response, 'content'):
                try:
                    error_content = json.loads(response.content.decode())
                    print(f"❌ Erro: {error_content.get('message', 'Erro desconhecido')}")
                except:
                    print(f"❌ Erro: {response.content.decode()[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de download: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_portal_api()
    print(f"\n{'✅ SUCESSO' if success else '❌ FALHOU'}")
    exit(0 if success else 1)

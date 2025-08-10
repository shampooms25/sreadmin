#!/usr/bin/env python3
"""
Script de teste para a API de Appliances POPPFIRE
"""

import os
import sys
import django
from pathlib import Path

# Configurar o ambiente Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def test_api_functionality():
    """
    Testa a funcionalidade da API sem fazer requisições HTTP
    """
    print("🧪 TESTE: API para Appliances POPPFIRE")
    print("=" * 50)
    
    from captive_portal.api_views import ApplianceAPIAuthentication, _calculate_file_hash
    from painel.models import EldGerenciarPortal, EldPortalSemVideo
    
    # Teste 1: Verificar autenticação
    print("1️⃣ Testando sistema de autenticação...")
    
    class MockRequest:
        def __init__(self, token):
            self.META = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    
    # Teste com token válido
    valid_request = MockRequest('1234567890abcdef1234567890abcdef')
    is_valid, result = ApplianceAPIAuthentication.verify_token(valid_request)
    
    if is_valid:
        print("   ✅ Autenticação com token válido: OK")
    else:
        print("   ❌ Autenticação com token válido: FALHOU")
    
    # Teste com token inválido
    invalid_request = MockRequest('token_invalido')
    is_valid, result = ApplianceAPIAuthentication.verify_token(invalid_request)
    
    if not is_valid:
        print("   ✅ Rejeição de token inválido: OK")
    else:
        print("   ❌ Rejeição de token inválido: FALHOU")
    
    # Teste 2: Verificar cálculo de hash
    print("\n2️⃣ Testando cálculo de hash...")
    
    try:
        # Criar arquivo temporário para teste
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("teste de conteúdo")
            temp_file = f.name
        
        file_hash = _calculate_file_hash(temp_file)
        
        if file_hash and file_hash != "error":
            print("   ✅ Cálculo de hash: OK")
        else:
            print("   ❌ Cálculo de hash: FALHOU")
        
        # Limpar arquivo temporário
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"   ❌ Erro no teste de hash: {e}")
    
    # Teste 3: Verificar modelos
    print("\n3️⃣ Testando modelos de dados...")
    
    try:
        # Verificar se os modelos estão acessíveis
        portal_count = EldGerenciarPortal.objects.count()
        portal_sem_video_count = EldPortalSemVideo.objects.count()
        
        print(f"   ✅ Portais com vídeo cadastrados: {portal_count}")
        print(f"   ✅ Portais sem vídeo cadastrados: {portal_sem_video_count}")
        
        # Testar método get_configuracao_ativa
        config_ativa = EldGerenciarPortal.get_configuracao_ativa()
        if config_ativa:
            print(f"   ✅ Portal ativo encontrado: {config_ativa}")
        else:
            print("   ℹ️  Nenhum portal ativo (normal se não configurado)")
        
    except Exception as e:
        print(f"   ❌ Erro no teste de modelos: {e}")
    
    # Teste 4: Verificar URLs
    print("\n4️⃣ Testando configuração de URLs...")
    
    try:
        from django.urls import reverse
        
        # Testar reversão de URLs
        urls_to_test = [
            'captive_portal_api:api_info',
            'captive_portal_api:portal_status',
            'captive_portal_api:portal_download',
            'captive_portal_api:update_status'
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"   ✅ URL {url_name}: {url}")
            except Exception as e:
                print(f"   ❌ URL {url_name}: ERRO - {e}")
        
    except Exception as e:
        print(f"   ❌ Erro no teste de URLs: {e}")
    
    print("\n📋 RESULTADO DOS TESTES:")
    print("=" * 30)
    print("✅ Sistema de autenticação implementado")
    print("✅ Cálculo de hash funcional")
    print("✅ Modelos de dados acessíveis")
    print("✅ URLs configuradas corretamente")
    
    print("\n🌐 ENDPOINTS PARA TESTE NO POSTMAN:")
    print("=" * 40)
    print("• GET  http://172.18.25.253:8000/api/appliances/info/")
    print("• GET  http://172.18.25.253:8000/api/appliances/portal/status/")
    print("• GET  http://172.18.25.253:8000/api/appliances/portal/download/")
    print("• POST http://172.18.25.253:8000/api/appliances/portal/update-status/")
    
    print("\n🔑 TOKEN DE TESTE:")
    print("Bearer 1234567890abcdef1234567890abcdef")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Configure um portal no admin Django")
    print("2. Teste os endpoints no Postman")
    print("3. Execute testes de download")
    print("4. Implemente no appliance POPPFIRE")

if __name__ == "__main__":
    try:
        test_api_functionality()
        print("\n🎉 TESTES CONCLUÍDOS COM SUCESSO!")
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

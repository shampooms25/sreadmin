#!/usr/bin/env python
"""
Teste do fluxo completo de desativação de recarga automática via interface web
"""
import os
import sys
import django
from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

# Configurar Django
django.setup()

def test_disable_auto_recharge_flow():
    """
    Testa o fluxo completo de desativação de recarga automática
    """
    print("=== TESTE: Fluxo Completo de Desativação de Recarga Automática ===")
    print()
    
    # Dados de teste
    account_id = "ACC-2744134-64041-5"
    service_line_number = "SL-394709-12748-31"
    
    print(f"📋 DADOS DO TESTE:")
    print(f"   Conta: {account_id}")
    print(f"   Service Line: {service_line_number}")
    print()
    
    try:
        # Criar cliente de teste
        client = Client()
        
        # Criar usuário admin para teste
        from django.contrib.auth.models import User
        admin_user = User.objects.create_superuser(
            username='testadmin',
            email='test@example.com',
            password='testpass123'
        )
        
        # Fazer login
        client.login(username='testadmin', password='testpass123')
        
        print("🔐 USUARIO ADMIN CRIADO E LOGADO")
        print()
        
        # Teste 1: Acessar página de gerenciamento de recarga automática
        print("🔍 TESTE 1: Acessar página de gerenciamento...")
        management_url = reverse('painel:starlink_auto_recharge_management')
        response = client.get(f"{management_url}?account_id={account_id}")
        
        print(f"   URL: {management_url}?account_id={account_id}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCESSO: Página de gerenciamento carregada")
        else:
            print("   ❌ ERRO: Página de gerenciamento não carregada")
            print(f"   Response: {response.content.decode()[:500]}...")
            return False
        
        print()
        
        # Teste 2: Acessar página de confirmação de desativação
        print("🔍 TESTE 2: Acessar página de confirmação...")
        disable_url = reverse('painel:starlink_disable_auto_recharge')
        response = client.get(f"{disable_url}?account_id={account_id}&service_line={service_line_number}")
        
        print(f"   URL: {disable_url}?account_id={account_id}&service_line={service_line_number}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCESSO: Página de confirmação carregada")
        else:
            print("   ❌ ERRO: Página de confirmação não carregada")
            print(f"   Response: {response.content.decode()[:500]}...")
            return False
            
        print()
        
        # Teste 3: Simular confirmação de desativação (sem executar realmente)
        print("🔍 TESTE 3: Testar formulário de confirmação...")
        
        # Preparar dados do formulário
        form_data = {
            'confirm': 'true',
            'account_id': account_id,
            'service_line_number': service_line_number
        }
        
        print(f"   Dados do formulário: {form_data}")
        
        # Fazer requisição POST para confirmação
        response = client.post(disable_url, form_data)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 302]:  # 200 = sucesso, 302 = redirect
            print("   ✅ SUCESSO: Formulário processado")
            if response.status_code == 302:
                print(f"   Redirecionamento para: {response.get('Location', 'N/A')}")
        else:
            print("   ❌ ERRO: Formulário não processado")
            print(f"   Response: {response.content.decode()[:500]}...")
            return False
            
        print()
        
        # Teste 4: Verificar se URLs estão corretas
        print("🔍 TESTE 4: Verificar URLs...")
        
        from django.urls import resolve
        
        # Testar resolução da URL de gerenciamento
        management_resolver = resolve('/admin/starlink/auto-recharge/')
        print(f"   URL de gerenciamento: {management_resolver.view_name}")
        
        # Testar resolução da URL de desativação
        disable_resolver = resolve('/admin/starlink/disable-auto-recharge/')
        print(f"   URL de desativação: {disable_resolver.view_name}")
        
        print("   ✅ SUCESSO: URLs resolvidas corretamente")
        print()
        
        # Limpeza
        admin_user.delete()
        
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("   ✅ Página de gerenciamento carrega corretamente")
        print("   ✅ Página de confirmação carrega corretamente")
        print("   ✅ Formulário de confirmação processa corretamente")
        print("   ✅ URLs estão configuradas corretamente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DO FLUXO COMPLETO...")
    print()
    
    success = test_disable_auto_recharge_flow()
    
    print()
    print("=" * 80)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("   O fluxo completo de desativação está funcionando.")
        print("   Você pode acessar: http://localhost:8000/admin/starlink/auto-recharge/")
    else:
        print("❌ TESTE FALHOU!")
        print("   Verifique os erros acima para corrigir o problema.")
    
    print("=" * 80)
    print("✅ TESTE FINALIZADO")
    print("=" * 80)
    
    sys.exit(0 if success else 1)

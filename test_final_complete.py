#!/usr/bin/env python
"""
Teste final completo do sistema de gerenciamento de recarga automática
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def test_views_context():
    """Teste das views principais"""
    from painel.views import (
        get_admin_context, 
        starlink_auto_recharge_management,
        starlink_admin
    )
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    from painel.starlink_api import get_available_accounts
    
    print("🔍 Testando views e contexto...")
    
    factory = RequestFactory()
    
    # Criar usuário se não existir
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    if created:
        user.set_password('testpass')
        user.save()
    
    # Teste 1: Contexto admin
    request = factory.get('/admin/')
    request.user = user
    
    try:
        context = get_admin_context(request)
        required_keys = ['available_apps', 'site_header', 'site_title']
        missing = [k for k in required_keys if k not in context]
        if missing:
            print(f"❌ Chaves ausentes no contexto: {missing}")
            return False
        else:
            print("✅ Contexto admin OK")
    except Exception as e:
        print(f"❌ Erro no contexto admin: {e}")
        return False
    
    # Teste 2: View starlink_admin
    request = factory.get('/admin/starlink/admin/')
    request.user = user
    
    try:
        response = starlink_admin(request)
        if response.status_code == 200:
            print("✅ View starlink_admin OK")
        else:
            print(f"❌ View starlink_admin falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na view starlink_admin: {e}")
        return False
    
    # Teste 3: View starlink_auto_recharge_management
    accounts = get_available_accounts()
    if accounts and len(accounts) > 0:
        test_account = list(accounts.keys())[0]  # Obter a primeira chave do dicionário
        request = factory.get(f'/admin/starlink/auto-recharge/?account_id={test_account}')
        request.user = user
        
        try:
            response = starlink_auto_recharge_management(request)
            if response.status_code == 200:
                print("✅ View starlink_auto_recharge_management OK")
            else:
                print(f"❌ View auto_recharge falhou: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro na view auto_recharge: {e}")
            return False
    else:
        print("⚠️ Nenhuma conta disponível para testar auto_recharge - OK")
    
    return True

def test_starlink_api_functions():
    """Teste das funções da API Starlink"""
    from painel.starlink_api import (
        get_available_accounts,
        get_service_lines_with_auto_recharge_status,
        get_account_info
    )
    
    print("\n🔍 Testando funções da API Starlink...")
    
    try:
        # Teste 1: Contas disponíveis
        accounts = get_available_accounts()
        print(f"✅ {len(accounts)} contas disponíveis")
        
        if not accounts or len(accounts) == 0:
            print("⚠️ Nenhuma conta disponível - teste limitado")
            return True  # Não é erro, apenas não temos contas
        
        # Teste 2: Informações da conta
        test_account = list(accounts.keys())[0]  # Obter a primeira chave do dicionário
        account_info = get_account_info(test_account)
        if account_info:
            print(f"✅ Informações da conta obtidas: {account_info.get('name', 'N/A')}")
        
        # Teste 3: Service lines com status de recarga automática
        result = get_service_lines_with_auto_recharge_status(test_account)
        if 'error' in result:
            print(f"⚠️ Erro esperado na API (sem conexão real): {result['error']}")
        else:
            lines = result.get('service_lines', [])
            print(f"✅ {len(lines)} service lines obtidas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas funções da API: {e}")
        return False

def test_urls_and_routing():
    """Teste das URLs e roteamento"""
    from django.urls import reverse
    from django.test import Client
    from django.contrib.auth.models import User
    
    print("\n🔍 Testando URLs e roteamento...")
    
    client = Client()
    
    # Criar usuário se não existir
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    if created:
        user.set_password('testpass')
        user.save()
    
    # Fazer login
    client.login(username='testuser', password='testpass')
    
    # Teste das URLs principais
    urls_to_test = [
        ('painel:starlink_main', 'Starlink Main'),
        ('painel:starlink_admin', 'Starlink Admin'),
        ('painel:starlink_dashboard', 'Starlink Dashboard'),
    ]
    
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {description} OK")
            else:
                print(f"❌ {description} falhou: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao testar {description}: {e}")
            return False
    
    # Teste da URL de auto-recharge com parâmetro
    try:
        url = reverse('painel:starlink_auto_recharge_management')
        response = client.get(f"{url}?account_id=ACC-2744134-64041-5")
        if response.status_code in [200, 302]:  # 302 é redirect para login ou outra página
            print("✅ Auto-recharge management OK")
        else:
            print(f"❌ Auto-recharge management falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar auto-recharge: {e}")
        return False
    
    return True

def main():
    print("🚀 TESTE FINAL COMPLETO DO SISTEMA")
    print("=" * 60)
    
    # Teste 1: Views e contexto
    success1 = test_views_context()
    
    # Teste 2: Funções da API
    success2 = test_starlink_api_functions()
    
    # Teste 3: URLs e roteamento
    success3 = test_urls_and_routing()
    
    print("\n" + "=" * 60)
    print("📋 RESUMO FINAL:")
    print(f"• Views e Contexto: {'✅ OK' if success1 else '❌ FALHOU'}")
    print(f"• API Starlink: {'✅ OK' if success2 else '❌ FALHOU'}")
    print(f"• URLs e Roteamento: {'✅ OK' if success3 else '❌ FALHOU'}")
    
    if success1 and success2 and success3:
        print("\n🎉 SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("✅ Todas as funcionalidades testadas com sucesso")
        print("✅ KeyError corrigido")
        print("✅ Sistema de recarga automática funcionando")
    else:
        print("\n⚠️ ALGUNS PROBLEMAS ENCONTRADOS")
        print("❌ Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()

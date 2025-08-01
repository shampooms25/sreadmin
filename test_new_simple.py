#!/usr/bin/env python
"""
Teste simples das funções principais
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def test_admin_context():
    """Teste do contexto do admin"""
    from painel.views import get_admin_context
    from django.test import RequestFactory
    from django.contrib.auth.models import User

    print("🔍 Testando get_admin_context...")
    
    factory = RequestFactory()
    request = factory.get('/admin/')
    
    # Criar usuário se não existir
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    if created:
        user.set_password('testpass')
        user.save()
    
    request.user = user
    
    try:
        context = get_admin_context(request)
        print(f"✅ Contexto obtido com {len(context)} itens")
        
        # Verificar chaves importantes
        required_keys = ['available_apps', 'site_header', 'site_title']
        missing = [k for k in required_keys if k not in context]
        if missing:
            print(f"⚠️ Chaves ausentes: {missing}")
            return False
        else:
            print("✅ Todas as chaves necessárias presentes")
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_starlink_api():
    """Teste da API Starlink"""
    from painel.starlink_api import get_available_accounts, get_service_lines_with_auto_recharge_status
    
    print("\n🔍 Testando API Starlink...")
    
    try:
        accounts = get_available_accounts()
        print(f"✅ {len(accounts)} contas disponíveis")
        
        if accounts:
            test_account = accounts[0]
            print(f"🔍 Testando com conta: {test_account}")
            
            result = get_service_lines_with_auto_recharge_status(test_account)
            if 'error' in result:
                print(f"⚠️ Erro na API: {result['error']}")
                return False
            else:
                lines = result.get('service_lines', [])
                print(f"✅ {len(lines)} service lines obtidas")
                return True
        else:
            print("⚠️ Nenhuma conta disponível")
            return False
            
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return False

def main():
    print("🚀 TESTE SIMPLES DO SISTEMA")
    print("=" * 40)
    
    # Teste 1: Contexto admin
    success1 = test_admin_context()
    
    # Teste 2: API Starlink
    success2 = test_starlink_api()
    
    print("\n" + "=" * 40)
    print("📋 RESUMO:")
    print(f"• Contexto Admin: {'✅ OK' if success1 else '❌ FALHOU'}")
    print(f"• API Starlink: {'✅ OK' if success2 else '❌ FALHOU'}")
    
    if success1 and success2:
        print("\n🎉 SISTEMA FUNCIONANDO!")
    else:
        print("\n⚠️ ALGUNS PROBLEMAS ENCONTRADOS")

if __name__ == "__main__":
    main()

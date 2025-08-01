#!/usr/bin/env python
"""
Teste final do sistema de gerenciamento de recarga automática
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.views import starlink_auto_recharge_management, get_admin_context
from painel.starlink_api import get_available_accounts

def test_view_context():
    """Testa se o contexto da view está correto"""
    print("🧪 Testando contexto da view de gerenciamento de recarga automática...")
    
    # Criar request factory
    factory = RequestFactory()
    
    # Criar usuário staff
    user = User.objects.create_user(
        username='testuser',
        password='testpass',
        is_staff=True
    )
    
    # Criar request com conta válida
    accounts = get_available_accounts()
    if not accounts:
        print("❌ Nenhuma conta disponível para teste")
        return False
    
    test_account = accounts[0]
    request = factory.get(f'/admin/starlink/auto-recharge/?account_id={test_account}')
    request.user = user
    
    try:
        # Testar função get_admin_context
        print("🔍 Testando get_admin_context...")
        admin_context = get_admin_context(request)
        print(f"✅ Contexto admin obtido: {len(admin_context)} itens")
        
        # Verificar se tem as chaves necessárias
        required_keys = ['site_header', 'site_title', 'index_title', 'available_apps']
        missing_keys = [key for key in required_keys if key not in admin_context]
        
        if missing_keys:
            print(f"⚠️ Chaves ausentes no contexto: {missing_keys}")
        else:
            print("✅ Todas as chaves necessárias estão presentes")
        
        # Testar a view diretamente
        print("\n🔍 Testando view starlink_auto_recharge_management...")
        response = starlink_auto_recharge_management(request)
        
        if response.status_code == 200:
            print("✅ View executada com sucesso!")
            return True
        else:
            print(f"❌ View retornou status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar view: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_starlink_api():
    """Testa as funções da API Starlink"""
    print("\n🧪 Testando funções da API Starlink...")
    
    from painel.starlink_api import get_service_lines_with_auto_recharge_status
    
    accounts = get_available_accounts()
    if not accounts:
        print("❌ Nenhuma conta disponível")
        return False
    
    test_account = accounts[0]
    print(f"🔍 Testando com conta: {test_account}")
    
    try:
        result = get_service_lines_with_auto_recharge_status(test_account)
        
        if 'error' in result:
            print(f"⚠️ Erro retornado pela API: {result['error']}")
        else:
            service_lines = result.get('service_lines', [])
            print(f"✅ {len(service_lines)} service lines obtidas")
            
            # Mostrar algumas informações
            for i, sl in enumerate(service_lines[:3]):  # Mostrar apenas as primeiras 3
                number = sl.get('serviceLineNumber', 'N/A')
                status = sl.get('auto_recharge_status', {})
                active = status.get('active', False)
                print(f"  - {number}: Recarga automática {'ATIVA' if active else 'INATIVA'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE FINAL DO SISTEMA DE GERENCIAMENTO DE RECARGA AUTOMÁTICA")
    print("=" * 70)
    
    # Teste 1: Contexto da view
    success1 = test_view_context()
    
    # Teste 2: API Starlink
    success2 = test_starlink_api()
    
    print("\n" + "=" * 70)
    print("📋 RESUMO DOS TESTES:")
    print(f"• Contexto da view: {'✅ OK' if success1 else '❌ FALHOU'}")
    print(f"• API Starlink: {'✅ OK' if success2 else '❌ FALHOU'}")
    
    if success1 and success2:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de gerenciamento de recarga automática está funcionando")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("❌ Verifique os erros acima")

if __name__ == "__main__":
    main()

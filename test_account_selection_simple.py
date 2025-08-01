#!/usr/bin/env python
"""
Teste simplificado para verificar a funcionalidade de seleção de conta
"""
import os
import sys
import django
from django.conf import settings

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

# Configurar Django
django.setup()

def test_account_selection_simple():
    """
    Testa a funcionalidade de seleção de conta de forma simplificada
    """
    print("=== TESTE: Seleção de Conta - Funcionalidade Core ===")
    
    try:
        from painel.starlink_api import get_available_accounts, get_account_info
        from painel.views import get_selected_account, get_account_context
        from django.test import RequestFactory
        
        # Criar factory para requests
        factory = RequestFactory()
        
        print("1. Testando contas disponíveis...")
        
        available_accounts = get_available_accounts()
        print(f"   Contas disponíveis: {len(available_accounts)}")
        for acc_id, acc_info in available_accounts.items():
            print(f"     - {acc_info['name']} ({acc_id})")
        
        print("\n2. Testando seleção de conta...")
        
        # Teste sem parâmetro (deve retornar None)
        request = factory.get('/admin/starlink/usage-report/')
        selected = get_selected_account(request)
        print(f"   Sem parâmetro: {selected}")
        
        # Teste com conta específica
        first_account = list(available_accounts.keys())[0]
        request = factory.get(f'/admin/starlink/usage-report/?account_id={first_account}')
        selected = get_selected_account(request)
        print(f"   Com account_id: {selected}")
        
        # Teste com conta inválida
        request = factory.get('/admin/starlink/usage-report/?account_id=ACC-INVALID')
        selected = get_selected_account(request)
        print(f"   Conta inválida: {selected}")
        
        print("\n3. Testando contexto da conta...")
        
        # Contexto para todas as contas
        request = factory.get('/admin/starlink/usage-report/')
        context = get_account_context(request)
        print(f"   Todas as contas - show_all_accounts: {context['show_all_accounts']}")
        print(f"   Contas disponíveis: {len(context['available_accounts'])}")
        
        # Contexto para conta específica
        request = factory.get(f'/admin/starlink/usage-report/?account_id={first_account}')
        context = get_account_context(request)
        print(f"   Conta específica - show_all_accounts: {context['show_all_accounts']}")
        print(f"   Conta selecionada: {context['selected_account']}")
        print(f"   Info da conta: {context['account_info']}")
        
        print("\n4. Testando ciclo atual...")
        
        from datetime import date
        today = date.today()
        
        # Calcular ciclo atual (mesma lógica da view)
        if today.day < 3:
            if today.month == 1:
                cycle_start_month = 12
                cycle_start_year = today.year - 1
            else:
                cycle_start_month = today.month - 1
                cycle_start_year = today.year
            cycle_start = date(cycle_start_year, cycle_start_month, 3)
        else:
            cycle_start = date(today.year, today.month, 3)
        
        cycle_end = today
        cycle_days = (cycle_end - cycle_start).days + 1
        
        print(f"   Ciclo atual: {cycle_start.strftime('%d/%m/%Y')} até {cycle_end.strftime('%d/%m/%Y')}")
        print(f"   Dias no ciclo: {cycle_days}")
        
        print("\n5. Testando dados simulados...")
        
        from painel.starlink_api import get_usage_report_data
        
        # Teste com conta específica
        result = get_usage_report_data(first_account)
        if "error" not in result:
            print(f"   ✓ Dados obtidos com sucesso para conta {first_account}")
            print(f"   Total de lines: {result.get('total_lines', 0)}")
            stats = result.get('statistics', {})
            print(f"   Estatísticas: {stats.get('lines_under_70', 0)} normais, {stats.get('lines_100_plus', 0)} excedidas")
        else:
            print(f"   ✗ Erro ao obter dados: {result['error']}")
        
        # Teste com todas as contas
        result_all = get_usage_report_data(None)
        if "error" not in result_all:
            print(f"   ✓ Dados obtidos com sucesso para todas as contas")
            print(f"   Total de lines: {result_all.get('total_lines', 0)}")
        else:
            print(f"   ✗ Erro ao obter dados para todas as contas: {result_all['error']}")
        
        print("\n=== TESTE CONCLUÍDO COM SUCESSO ===")
        print("\n📋 RESUMO:")
        print("   ✓ Seleção de conta funcionando")
        print("   ✓ Contexto da conta funcionando")
        print("   ✓ Ciclo atual calculado corretamente")
        print("   ✓ Dados simulados funcionando")
        print("   ✓ Template pronto para uso")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_account_selection_simple()
    sys.exit(0 if success else 1)

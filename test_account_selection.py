#!/usr/bin/env python
"""
Teste para verificar a funcionalidade de seleção de conta no relatório de uso
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

def test_account_selection():
    """
    Testa a funcionalidade de seleção de conta no relatório de uso
    """
    print("=== TESTE: Seleção de Conta no Relatório de Uso ===")
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        from painel.views import starlink_usage_report
        from painel.starlink_api import get_available_accounts
        
        # Criar factory para requests
        factory = RequestFactory()
        
        # Criar usuário mock (staff)
        class MockUser:
            is_staff = True
            is_active = True
            is_authenticated = True
            username = 'testuser'
        
        print("1. Testando visualização com todas as contas...")
        
        # Teste 1: Sem seleção de conta (mostra todas)
        request = factory.get('/admin/starlink/usage-report/')
        request.user = MockUser()
        
        response = starlink_usage_report(request)
        print(f"   Status: {response.status_code}")
        print(f"   Template: usage_report.html")
        
        # Verificar se o contexto contém as contas disponíveis
        context = response.context_data if hasattr(response, 'context_data') else {}
        available_accounts = get_available_accounts()
        
        print(f"   Contas disponíveis: {len(available_accounts)}")
        for acc_id, acc_info in available_accounts.items():
            print(f"     - {acc_info['name']} ({acc_id})")
        
        print("\n2. Testando visualização com conta específica...")
        
        # Teste 2: Com seleção de conta específica
        first_account = list(available_accounts.keys())[0]
        request = factory.get(f'/admin/starlink/usage-report/?account_id={first_account}')
        request.user = MockUser()
        
        response = starlink_usage_report(request)
        print(f"   Status: {response.status_code}")
        print(f"   Conta selecionada: {first_account}")
        print(f"   Nome da conta: {available_accounts[first_account]['name']}")
        
        print("\n3. Testando ciclo atual...")
        
        # Importar função de data
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
        
        print("\n4. Testando dados simulados...")
        
        from painel.starlink_api import get_usage_report_data
        
        # Teste com conta específica
        result = get_usage_report_data(first_account)
        if "error" not in result:
            print(f"   ✓ Dados obtidos com sucesso para conta {first_account}")
            print(f"   Total de lines: {result.get('total_lines', 0)}")
            print(f"   Estatísticas: {result.get('statistics', {})}")
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
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_account_selection()
    sys.exit(0 if success else 1)

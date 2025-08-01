#!/usr/bin/env python3
"""
Teste final do dashboard Starlink - Validação das melhorias implementadas
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

User = get_user_model()


class TestDashboardFinal(TestCase):
    """Testes finais do dashboard Starlink"""
    
    def setUp(self):
        """Configurar dados de teste"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Mock data para todas as contas
        self.mock_all_accounts_data = {
            "success": True,
            "total_accounts": 2,
            "total_summary": {
                "total_service_lines": 25,
                "active_lines": 20,
                "offline_lines": 3,
                "no_data_lines": 2,
                "total_charges": 2500.00,
                "accounts_with_errors": 0
            },
            "accounts": {
                "account1": {
                    "name": "Conta Principal",
                    "total_service_lines": 15,
                    "active_lines": 12,
                    "offline_lines": 2,
                    "no_data_lines": 1
                },
                "account2": {
                    "name": "Conta Secundária",
                    "total_service_lines": 10,
                    "active_lines": 8,
                    "offline_lines": 1,
                    "no_data_lines": 1
                }
            }
        }
        
        # Mock data para conta específica
        self.mock_single_account_data = {
            "success": True,
            "service_lines": [],
            "total": 15,
            "statistics": {
                "total_service_lines": 15,
                "active_lines": 12,
                "offline_lines": 2,
                "no_data_lines": 1
            },
            "account_id": "account1"
        }
        
        # Mock data para contas disponíveis
        self.mock_available_accounts = {
            "account1": {
                "name": "Conta Principal",
                "description": "Conta principal da empresa"
            },
            "account2": {
                "name": "Conta Secundária",
                "description": "Conta secundária para filiais"
            }
        }
    
    @patch('painel.starlink_api.get_all_accounts_summary')
    @patch('painel.starlink_api.get_available_accounts')
    def test_dashboard_all_accounts_mode(self, mock_get_available_accounts, mock_get_all_accounts_summary):
        """Testa o dashboard no modo 'todas as contas'"""
        # Configurar mocks
        mock_get_available_accounts.return_value = self.mock_available_accounts
        mock_get_all_accounts_summary.return_value = self.mock_all_accounts_data
        
        # Fazer request sem account_id
        response = self.client.get(reverse('painel:starlink_dashboard'))
        
        # Verificar response
        self.assertEqual(response.status_code, 200)
        
        # Verificar contexto
        context = response.context
        self.assertTrue(context['has_statistics'])
        self.assertEqual(context['account_mode'], 'all')
        self.assertEqual(context['total_service_lines'], 25)
        self.assertEqual(context['statistics']['active_lines'], 20)
        self.assertEqual(context['statistics']['offline_lines'], 3)
        self.assertEqual(context['statistics']['no_data_lines'], 2)
        self.assertEqual(context['total_accounts'], 2)
        self.assertIsNone(context['selected_account'])
        
        # Verificar se o template tem o conteúdo correto
        self.assertContains(response, 'Visualizando resumo de todas as contas')
        self.assertContains(response, 'Selecione uma conta')
        self.assertContains(response, '25')  # Total service lines
        self.assertContains(response, '20')  # Active lines
        self.assertContains(response, '3')   # Offline lines
        self.assertContains(response, '2')   # No data lines
    
    @patch('painel.starlink_api.get_service_lines_with_location')
    @patch('painel.starlink_api.get_available_accounts')
    def test_dashboard_single_account_mode(self, mock_get_available_accounts, mock_get_service_lines):
        """Testa o dashboard no modo 'conta específica'"""
        # Configurar mocks
        mock_get_available_accounts.return_value = self.mock_available_accounts
        mock_get_service_lines.return_value = self.mock_single_account_data
        
        # Fazer request com account_id
        response = self.client.get(reverse('painel:starlink_dashboard'), {'account_id': 'account1'})
        
        # Verificar response
        self.assertEqual(response.status_code, 200)
        
        # Verificar contexto
        context = response.context
        self.assertTrue(context['has_statistics'])
        self.assertEqual(context['account_mode'], 'single')
        self.assertEqual(context['total_service_lines'], 15)
        self.assertEqual(context['statistics']['active_lines'], 12)
        self.assertEqual(context['statistics']['offline_lines'], 2)
        self.assertEqual(context['statistics']['no_data_lines'], 1)
        self.assertEqual(context['selected_account'], 'account1')
        
        # Verificar se o template tem o conteúdo correto
        self.assertContains(response, 'account1')
        self.assertContains(response, '15')  # Total service lines
        self.assertContains(response, '12')  # Active lines
        self.assertContains(response, '2')   # Offline lines
        self.assertContains(response, '1')   # No data lines
    
    @patch('painel.starlink_api.get_available_accounts')
    def test_dashboard_template_structure(self, mock_get_available_accounts):
        """Testa a estrutura do template do dashboard"""
        # Configurar mock
        mock_get_available_accounts.return_value = self.mock_available_accounts
        
        # Fazer request
        response = self.client.get(reverse('painel:starlink_dashboard'))
        
        # Verificar elementos do template
        self.assertContains(response, 'account-selector')
        self.assertContains(response, 'dashboard-cards')
        self.assertContains(response, 'stat-card active')
        self.assertContains(response, 'stat-card offline')
        self.assertContains(response, 'stat-card warning')
        self.assertContains(response, 'changeAccount()')
        
        # Verificar cores dos cards
        self.assertContains(response, 'color: #28a745')  # Verde para ativos
        self.assertContains(response, 'color: #dc3545')  # Vermelho para offline
        self.assertContains(response, 'color: #ffc107')  # Amarelo para sem dados
    
    @patch('painel.starlink_api.get_available_accounts')
    def test_dashboard_breadcrumbs(self, mock_get_available_accounts):
        """Testa os breadcrumbs do dashboard"""
        # Configurar mock
        mock_get_available_accounts.return_value = self.mock_available_accounts
        
        # Fazer request
        response = self.client.get(reverse('painel:starlink_dashboard'))
        
        # Verificar breadcrumbs
        self.assertContains(response, 'breadcrumb')
        self.assertContains(response, 'Início')
        self.assertContains(response, 'Starlink Admin')
        self.assertContains(response, 'Dashboard')
    
    @patch('painel.starlink_api.get_available_accounts')
    def test_dashboard_card_links(self, mock_get_available_accounts):
        """Testa os links dos cards do dashboard"""
        # Configurar mock
        mock_get_available_accounts.return_value = self.mock_available_accounts
        
        # Fazer request sem account_id
        response = self.client.get(reverse('painel:starlink_dashboard'))
        
        # Verificar que os links não têm account_id quando nenhuma conta é selecionada
        self.assertNotContains(response, '?account_id=')
        
        # Fazer request com account_id
        response = self.client.get(reverse('painel:starlink_dashboard'), {'account_id': 'account1'})
        
        # Verificar que os links têm account_id quando uma conta é selecionada
        self.assertContains(response, '?account_id=account1')
    
    def test_dashboard_error_handling(self):
        """Testa o tratamento de erros no dashboard"""
        # Fazer request sem mocks (vai gerar erro)
        response = self.client.get(reverse('painel:starlink_dashboard'))
        
        # Verificar que a página ainda funciona mesmo com erro
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_statistics'])
        
        # Verificar que o seletor de conta ainda aparece
        self.assertContains(response, 'account-selector')


def run_tests():
    """Executar os testes"""
    print("🧪 Executando testes finais do dashboard Starlink...")
    print("=" * 60)
    
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Executar testes
    failures = test_runner.run_tests(["__main__.TestDashboardFinal"])
    
    if failures:
        print(f"❌ {failures} teste(s) falharam!")
        return False
    else:
        print("✅ Todos os testes passaram!")
        return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

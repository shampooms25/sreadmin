#!/usr/bin/env python3
"""
Teste da funcionalidade de desativar/ativar botões do dashboard
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
from unittest.mock import patch

User = get_user_model()


class TestDashboardButtons(TestCase):
    """Testes da funcionalidade de botões do dashboard"""
    
    def setUp(self):
        """Configurar dados de teste"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='testuser', password='testpass123')
        
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
    
    @patch('painel.starlink_api.get_available_accounts')
    def test_dashboard_buttons_disabled_no_account(self, mock_get_available_accounts):
        """Testa se os botões estão desativados quando nenhuma conta é selecionada"""
        # Configurar mock
        mock_get_available_accounts.return_value = self.mock_available_accounts
        
        # Fazer request sem account_id
        response = self.client.get(reverse('painel:starlink_dashboard'))
        
        # Verificar response
        self.assertEqual(response.status_code, 200)
        
        # Verificar se os botões têm classe disabled
        self.assertContains(response, 'class="card-button disabled"')
        
        # Verificar se tem o onclick="return false;"
        self.assertContains(response, 'onclick="return false;"')
        
        # Verificar se aparece o aviso sobre botões desativados
        self.assertContains(response, 'Os botões de ação estão desativados')
        
        # Verificar se não tem parâmetros account_id nos links
        self.assertNotContains(response, '?account_id=')
        
        print("✅ Teste de botões desativados (sem conta): PASSOU")
    
    @patch('painel.starlink_api.get_service_lines_with_location')
    @patch('painel.starlink_api.get_available_accounts')
    def test_dashboard_buttons_enabled_with_account(self, mock_get_available_accounts, mock_get_service_lines):
        """Testa se os botões estão ativados quando uma conta é selecionada"""
        # Configurar mocks
        mock_get_available_accounts.return_value = self.mock_available_accounts
        mock_get_service_lines.return_value = {
            "success": True,
            "service_lines": [],
            "total": 10,
            "statistics": {
                "active_lines": 8,
                "offline_lines": 2,
                "no_data_lines": 0
            }
        }
        
        # Fazer request com account_id
        response = self.client.get(reverse('painel:starlink_dashboard'), {'account_id': 'account1'})
        
        # Verificar response
        self.assertEqual(response.status_code, 200)
        
        # Verificar se os botões NÃO têm classe disabled
        self.assertNotContains(response, 'class="card-button disabled"')
        
        # Verificar se NÃO tem o onclick="return false;"
        self.assertNotContains(response, 'onclick="return false;"')
        
        # Verificar se NÃO aparece o aviso sobre botões desativados
        self.assertNotContains(response, 'Os botões de ação estão desativados')
        
        # Verificar se tem parâmetros account_id nos links
        self.assertContains(response, '?account_id=account1')
        
        print("✅ Teste de botões ativados (com conta): PASSOU")
    
    @patch('painel.starlink_api.get_available_accounts')
    def test_dashboard_css_disabled_buttons(self, mock_get_available_accounts):
        """Testa se o CSS para botões desativados está presente"""
        # Configurar mock
        mock_get_available_accounts.return_value = self.mock_available_accounts
        
        # Fazer request sem account_id
        response = self.client.get(reverse('painel:starlink_dashboard'))
        
        # Verificar response
        self.assertEqual(response.status_code, 200)
        
        # Verificar se o CSS para botões desativados está presente
        self.assertContains(response, '.card-button:disabled')
        self.assertContains(response, '.card-button.disabled')
        self.assertContains(response, 'cursor: not-allowed')
        self.assertContains(response, 'pointer-events: none')
        
        print("✅ Teste de CSS para botões desativados: PASSOU")
    
    @patch('painel.starlink_api.get_available_accounts')
    def test_dashboard_javascript_functions(self, mock_get_available_accounts):
        """Testa se as funções JavaScript estão presentes"""
        # Configurar mock
        mock_get_available_accounts.return_value = self.mock_available_accounts
        
        # Fazer request
        response = self.client.get(reverse('painel:starlink_dashboard'))
        
        # Verificar response
        self.assertEqual(response.status_code, 200)
        
        # Verificar se as funções JavaScript estão presentes
        self.assertContains(response, 'function changeAccount()')
        self.assertContains(response, 'function updateButtonStates()')
        self.assertContains(response, 'addEventListener(\'DOMContentLoaded\'')
        self.assertContains(response, 'button.classList.add(\'disabled\')')
        self.assertContains(response, 'button.classList.remove(\'disabled\')')
        
        print("✅ Teste de funções JavaScript: PASSOU")
    
    @patch('painel.starlink_api.get_available_accounts')
    def test_dashboard_warning_message(self, mock_get_available_accounts):
        """Testa se a mensagem de aviso aparece corretamente"""
        # Configurar mock
        mock_get_available_accounts.return_value = self.mock_available_accounts
        
        # Fazer request sem account_id
        response = self.client.get(reverse('painel:starlink_dashboard'))
        
        # Verificar response
        self.assertEqual(response.status_code, 200)
        
        # Verificar elementos da mensagem de aviso
        self.assertContains(response, 'background: #fff3cd')
        self.assertContains(response, 'fas fa-exclamation-triangle')
        self.assertContains(response, 'Informação')
        self.assertContains(response, 'Selecione uma conta específica')
        
        print("✅ Teste de mensagem de aviso: PASSOU")


def run_tests():
    """Executar os testes"""
    print("🧪 Executando testes da funcionalidade de botões do dashboard...")
    print("=" * 70)
    
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Executar testes
    failures = test_runner.run_tests(["__main__.TestDashboardButtons"])
    
    if failures:
        print(f"\n❌ {failures} teste(s) falharam!")
        return False
    else:
        print("\n✅ Todos os testes passaram!")
        return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

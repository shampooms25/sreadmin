#!/usr/bin/env python3
"""
Teste manual simples da funcionalidade de botões dinâmicos
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

def test_buttons_functionality():
    """Teste manual da funcionalidade de botões"""
    print("🧪 Testando funcionalidade de botões dinâmicos...")
    print("=" * 60)
    
    # Criar cliente de teste
    client = Client()
    
    # Criar usuário staff
    try:
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        client.login(username='testuser', password='testpass123')
        print("✅ Usuário criado e logado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return False
    
    # Mock para contas disponíveis
    mock_accounts = {
        "test-account-1": {
            "name": "Conta de Teste 1",
            "description": "Conta para testes"
        }
    }
    
    # Teste 1: Dashboard sem conta selecionada
    print("\n🔍 Teste 1: Dashboard sem conta selecionada")
    try:
        with patch('painel.starlink_api.get_available_accounts', return_value=mock_accounts):
            response = client.get(reverse('painel:starlink_dashboard'))
            
            if response.status_code == 200:
                print("✅ Dashboard acessível")
                
                content = response.content.decode('utf-8')
                
                # Verificar se tem botões desativados
                if 'class="card-button disabled"' in content:
                    print("✅ Botões estão marcados como desativados")
                else:
                    print("❌ Botões não estão marcados como desativados")
                    return False
                
                # Verificar se tem mensagem de aviso
                if 'Os botões de ação estão desativados' in content:
                    print("✅ Mensagem de aviso presente")
                else:
                    print("❌ Mensagem de aviso não encontrada")
                    return False
                
                # Verificar se tem CSS para botões desativados
                if '.card-button.disabled' in content:
                    print("✅ CSS para botões desativados presente")
                else:
                    print("❌ CSS para botões desativados não encontrado")
                    return False
                
                # Verificar se tem JavaScript
                if 'function updateButtonStates()' in content:
                    print("✅ JavaScript de controle de botões presente")
                else:
                    print("❌ JavaScript de controle de botões não encontrado")
                    return False
                
            else:
                print(f"❌ Dashboard retornou status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro no teste 1: {e}")
        return False
    
    # Teste 2: Dashboard com conta selecionada
    print("\n🔍 Teste 2: Dashboard com conta selecionada")
    try:
        mock_service_lines = {
            "success": True,
            "service_lines": [],
            "total": 5,
            "statistics": {
                "active_lines": 4,
                "offline_lines": 1,
                "no_data_lines": 0
            }
        }
        
        with patch('painel.starlink_api.get_available_accounts', return_value=mock_accounts), \
             patch('painel.starlink_api.get_service_lines_with_location', return_value=mock_service_lines):
            
            response = client.get(reverse('painel:starlink_dashboard'), {'account_id': 'test-account-1'})
            
            if response.status_code == 200:
                print("✅ Dashboard com conta acessível")
                
                content = response.content.decode('utf-8')
                
                # Verificar se NÃO tem botões desativados
                if 'class="card-button disabled"' not in content:
                    print("✅ Botões não estão marcados como desativados")
                else:
                    print("❌ Botões ainda estão marcados como desativados")
                    return False
                
                # Verificar se tem account_id nos links
                if '?account_id=test-account-1' in content:
                    print("✅ Links contêm account_id")
                else:
                    print("❌ Links não contêm account_id")
                    return False
                
                # Verificar se NÃO tem mensagem de aviso
                if 'Os botões de ação estão desativados' not in content:
                    print("✅ Mensagem de aviso não aparece")
                else:
                    print("❌ Mensagem de aviso ainda aparece")
                    return False
                
            else:
                print(f"❌ Dashboard com conta retornou status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro no teste 2: {e}")
        return False
    
    print("\n✅ Todos os testes passaram!")
    return True


if __name__ == "__main__":
    success = test_buttons_functionality()
    sys.exit(0 if success else 1)

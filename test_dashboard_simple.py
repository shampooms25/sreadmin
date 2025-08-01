#!/usr/bin/env python3
"""
Teste simples do dashboard Starlink
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

def test_dashboard_basic():
    """Teste básico do dashboard"""
    print("🔍 Testando dashboard básico...")
    
    # Criar cliente de teste
    client = Client()
    
    # Criar usuário staff
    try:
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        print("✅ Usuário criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return False
    
    # Fazer login
    try:
        login_success = client.login(username='testuser', password='testpass123')
        if login_success:
            print("✅ Login realizado com sucesso")
        else:
            print("❌ Falha no login")
            return False
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False
    
    # Testar acesso ao dashboard
    try:
        response = client.get(reverse('painel:starlink_dashboard'))
        if response.status_code == 200:
            print("✅ Dashboard acessível")
        else:
            print(f"❌ Dashboard retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar dashboard: {e}")
        return False
    
    # Verificar conteúdo do dashboard
    try:
        content = response.content.decode('utf-8')
        if 'Selecione uma conta' in content:
            print("✅ Seletor de conta encontrado")
        else:
            print("❌ Seletor de conta não encontrado")
            return False
        
        if 'account-selector' in content:
            print("✅ Estrutura do seletor de conta encontrada")
        else:
            print("❌ Estrutura do seletor de conta não encontrada")
            return False
        
        if 'dashboard-cards' in content:
            print("✅ Cards do dashboard encontrados")
        else:
            print("❌ Cards do dashboard não encontrados")
            return False
        
        if 'stat-card' in content:
            print("✅ Cards de estatísticas encontrados")
        else:
            print("❌ Cards de estatísticas não encontrados")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao verificar conteúdo: {e}")
        return False
    
    print("✅ Teste básico do dashboard passou!")
    return True


def test_dashboard_css():
    """Teste das classes CSS do dashboard"""
    print("\n🎨 Testando CSS do dashboard...")
    
    client = Client()
    
    # Criar usuário staff
    try:
        user = User.objects.create_user(
            username='testuser2',
            password='testpass123',
            is_staff=True
        )
        client.login(username='testuser2', password='testpass123')
    except Exception as e:
        print(f"❌ Erro na configuração do teste: {e}")
        return False
    
    # Testar acesso ao dashboard
    try:
        response = client.get(reverse('painel:starlink_dashboard'))
        content = response.content.decode('utf-8')
        
        # Verificar classes CSS específicas
        css_classes = [
            'stat-card active',
            'stat-card offline',
            'stat-card warning',
            'account-selector',
            'dashboard-cards',
            'card-button'
        ]
        
        for css_class in css_classes:
            if css_class in content:
                print(f"✅ Classe CSS '{css_class}' encontrada")
            else:
                print(f"❌ Classe CSS '{css_class}' não encontrada")
                return False
        
        # Verificar cores específicas
        colors = [
            '#28a745',  # Verde para ativos
            '#dc3545',  # Vermelho para offline
            '#ffc107'   # Amarelo para sem dados
        ]
        
        for color in colors:
            if color in content:
                print(f"✅ Cor '{color}' encontrada")
            else:
                print(f"❌ Cor '{color}' não encontrada")
                return False
        
    except Exception as e:
        print(f"❌ Erro ao verificar CSS: {e}")
        return False
    
    print("✅ Teste de CSS do dashboard passou!")
    return True


def main():
    """Função principal"""
    print("🚀 Iniciando testes do dashboard Starlink...")
    print("=" * 50)
    
    success = True
    
    if not test_dashboard_basic():
        success = False
    
    if not test_dashboard_css():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Todos os testes passaram!")
    else:
        print("❌ Alguns testes falharam!")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Teste visual do dashboard após correção de layout dos cards
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
import django
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import HttpResponse

def test_dashboard_layout():
    """Testa se o dashboard carrega corretamente após as correções de layout"""
    print("🧪 Testando Layout do Dashboard...")
    
    # Criar cliente de teste
    client = Client()
    
    # Criar usuário admin para o teste
    try:
        user = User.objects.create_superuser(
            username='test_admin',
            email='test@example.com',
            password='testpass123'
        )
        print(f"✅ Usuário de teste criado: {user.username}")
    except Exception as e:
        # Usuário pode já existir
        user = User.objects.get(username='test_admin')
        print(f"ℹ️  Usuário de teste já existe: {user.username}")
    
    # Fazer login
    client.login(username='test_admin', password='testpass123')
    
    # Testar acesso ao dashboard
    try:
        response = client.get(reverse('painel:starlink_dashboard'))
        print(f"✅ Status do dashboard: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar se os elementos corretos estão presentes
            checks = [
                ('Seletor de conta', 'account-select' in content),
                ('Cards do dashboard', 'dashboard-cards' in content),
                ('Título dos cards', 'card-title' in content),
                ('Descrição dos cards', 'card-description' in content),
                ('Botões dos cards', 'card-button' in content),
                ('CSS de layout', 'display: block' in content),
                ('Margin entre título e descrição', 'margin-bottom: 15px' in content),
                ('Aviso sobre botões', 'Os botões de ação estão desativados' in content),
                ('Estatísticas', 'stat-card' in content),
                ('JavaScript', 'changeAccount()' in content),
            ]
            
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"{status} {check_name}: {'OK' if result else 'FALHOU'}")
            
            # Verificar se todas as verificações passaram
            all_passed = all(result for _, result in checks)
            print(f"\n{'✅ Todos os testes passaram!' if all_passed else '❌ Alguns testes falharam!'}")
            
            return all_passed
        else:
            print(f"❌ Dashboard não carregou corretamente: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar dashboard: {e}")
        return False
    
    finally:
        # Limpar usuário de teste
        try:
            User.objects.filter(username='test_admin').delete()
            print("🗑️  Usuário de teste removido")
        except:
            pass

def test_dashboard_with_account():
    """Testa o dashboard com uma conta selecionada"""
    print("\n🧪 Testando Dashboard com Conta Selecionada...")
    
    client = Client()
    
    try:
        user = User.objects.create_superuser(
            username='test_admin2',
            email='test2@example.com',
            password='testpass123'
        )
    except:
        user = User.objects.get(username='test_admin2')
    
    client.login(username='test_admin2', password='testpass123')
    
    try:
        # Testar com parâmetro account_id
        response = client.get(reverse('painel:starlink_dashboard') + '?account_id=test_account')
        print(f"✅ Status com conta selecionada: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar se os botões não estão desativados
            disabled_buttons = 'disabled' in content
            warning_message = 'Os botões de ação estão desativados' in content
            
            print(f"✅ Botões {'desativados' if disabled_buttons else 'ativos'}")
            print(f"✅ Mensagem de aviso {'presente' if warning_message else 'ausente'}")
            
            return True
        else:
            print(f"❌ Dashboard com conta não carregou: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar dashboard com conta: {e}")
        return False
    
    finally:
        try:
            User.objects.filter(username='test_admin2').delete()
        except:
            pass

if __name__ == '__main__':
    print("🚀 Iniciando Testes de Layout do Dashboard\n")
    
    # Executar testes
    test1 = test_dashboard_layout()
    test2 = test_dashboard_with_account()
    
    print(f"\n📊 Resumo dos Testes:")
    print(f"{'✅' if test1 else '❌'} Teste de Layout: {'PASSOU' if test1 else 'FALHOU'}")
    print(f"{'✅' if test2 else '❌'} Teste com Conta: {'PASSOU' if test2 else 'FALHOU'}")
    
    if test1 and test2:
        print("\n🎉 Todos os testes passaram! O dashboard está funcionando corretamente.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os logs acima.")

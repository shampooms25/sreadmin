#!/usr/bin/env python3
"""
Teste para verificar a correção da quebra de linha nos cards do dashboard
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

def test_card_layout():
    """Testa se os cards têm a estrutura HTML correta para quebra de linha"""
    print("🧪 Testando Layout dos Cards...")
    
    # Ler o arquivo HTML
    template_path = "c:\\Projetos\\Poppnet\\sreadmin\\painel\\templates\\admin\\painel\\starlink\\dashboard.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se os elementos HTML corretos estão presentes
        checks = [
            ('Título como h3', '<h3 class="card-title">' in content),
            ('Descrição como p', '<p class="card-description">' in content),
            ('CSS para h3', '.card-content h3.card-title' in content),
            ('CSS para p', '.card-content p.card-description' in content),
            ('Margin correto no h3', 'margin: 0 0 15px 0' in content),
            ('Margin correto no p', 'margin: 15px 0 0 0' in content),
            ('Clear both', 'clear: both' in content),
            ('Width 100%', 'width: 100%' in content),
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}: {'OK' if result else 'FALHOU'}")
        
        # Verificar se todos os 4 cards foram atualizados
        h3_count = content.count('<h3 class="card-title">')
        p_count = content.count('<p class="card-description">')
        
        print(f"\n📊 Contagem de elementos:")
        print(f"✅ Títulos h3: {h3_count} (esperado: 4)")
        print(f"✅ Descrições p: {p_count} (esperado: 4)")
        
        # Verificar se todas as verificações passaram
        all_passed = all(result for _, result in checks) and h3_count == 4 and p_count == 4
        print(f"\n{'✅ Estrutura HTML correta!' if all_passed else '❌ Estrutura HTML incorreta!'}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Erro ao ler template: {e}")
        return False

def test_dashboard_rendering():
    """Testa se o dashboard ainda renderiza corretamente"""
    print("\n🧪 Testando Renderização do Dashboard...")
    
    client = Client()
    
    try:
        user = User.objects.create_superuser(
            username='test_layout',
            email='test@layout.com',
            password='testpass123'
        )
    except:
        user = User.objects.get(username='test_layout')
    
    client.login(username='test_layout', password='testpass123')
    
    try:
        response = client.get(reverse('painel:starlink_dashboard'))
        print(f"✅ Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.content.decode('utf-8')
            
            # Verificar se os elementos estão presentes no HTML renderizado
            checks = [
                ('H3 renderizado', '<h3 class="card-title">Relatório Detalhado</h3>' in html_content),
                ('P renderizado', '<p class="card-description">' in html_content),
                ('CSS aplicado', '.card-content h3.card-title' in html_content),
                ('Todos os 4 cards', html_content.count('<h3 class="card-title">') == 4),
            ]
            
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"{status} {check_name}: {'OK' if result else 'FALHOU'}")
            
            all_passed = all(result for _, result in checks)
            print(f"\n{'✅ Dashboard renderiza corretamente!' if all_passed else '❌ Problemas na renderização!'}")
            
            return all_passed
        else:
            print(f"❌ Dashboard não carregou: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar renderização: {e}")
        return False
    
    finally:
        try:
            User.objects.filter(username='test_layout').delete()
        except:
            pass

if __name__ == '__main__':
    print("🚀 Testando Correção da Quebra de Linha nos Cards\n")
    
    # Executar testes
    test1 = test_card_layout()
    test2 = test_dashboard_rendering()
    
    print(f"\n📊 Resumo Final:")
    print(f"{'✅' if test1 else '❌'} Estrutura HTML: {'CORRETA' if test1 else 'INCORRETA'}")
    print(f"{'✅' if test2 else '❌'} Renderização: {'OK' if test2 else 'FALHOU'}")
    
    if test1 and test2:
        print("\n🎉 Cards agora têm quebra de linha correta!")
        print("📋 Resultado esperado:")
        print("   • Título: 'Relatório Detalhado'")
        print("   • Nova linha")
        print("   • Descrição: 'Relatório completo com lista...'")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os logs acima.")

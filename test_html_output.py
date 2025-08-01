#!/usr/bin/env python
"""
Teste para verificar se o HTML gerado contém as alterações
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

# Configurar Django
django.setup()

def test_html_output():
    """
    Testa se o HTML gerado contém as alterações
    """
    print("=== TESTE: HTML Gerado pela View ===")
    print()
    
    try:
        # Criar cliente de teste
        client = Client()
        
        # Criar usuário admin temporário
        try:
            admin_user = User.objects.create_superuser(
                username='testadmin_temp',
                email='test@example.com',
                password='testpass123'
            )
            print("✅ Usuário admin criado")
        except:
            admin_user = User.objects.get(username='testadmin_temp')
            print("✅ Usuário admin já existe")
        
        # Fazer login
        client.login(username='testadmin_temp', password='testpass123')
        print("✅ Login realizado")
        
        # Fazer requisição para a página
        account_id = "ACC-2744134-64041-5"
        response = client.get(f'/admin/starlink/auto-recharge/?account_id={account_id}')
        
        print(f"✅ Requisição feita - Status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.content.decode('utf-8')
            
            # Verificar se o HTML contém as alterações
            print("\n🔍 VERIFICANDO CONTEÚDO HTML...")
            
            if 'auto-recharge-disabled' in html_content:
                print("   ✅ Estilo CSS 'auto-recharge-disabled' encontrado no HTML")
            else:
                print("   ❌ Estilo CSS 'auto-recharge-disabled' NÃO encontrado no HTML")
                
            if 'Recarga Automática Desativada' in html_content:
                print("   ✅ Texto 'Recarga Automática Desativada' encontrado no HTML")
            else:
                print("   ❌ Texto 'Recarga Automática Desativada' NÃO encontrado no HTML")
                
            if 'btn-warning' in html_content:
                print("   ✅ Classe 'btn-warning' encontrada no HTML")
            else:
                print("   ❌ Classe 'btn-warning' NÃO encontrada no HTML")
                
            if 'Ativar Recarga Automática' in html_content:
                print("   ✅ Texto 'Ativar Recarga Automática' encontrado no HTML")
            else:
                print("   ❌ Texto 'Ativar Recarga Automática' NÃO encontrado no HTML")
                
            if '#ff9500' in html_content:
                print("   ✅ Cor laranja '#ff9500' encontrada no HTML")
            else:
                print("   ❌ Cor laranja '#ff9500' NÃO encontrada no HTML")
            
            # Salvar uma amostra do HTML para inspeção
            with open('html_output_sample.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("   ✅ HTML salvo em 'html_output_sample.html' para inspeção")
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            
        # Limpar usuário de teste
        try:
            admin_user.delete()
            print("✅ Usuário admin temporário removido")
        except:
            pass
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DE HTML GERADO...")
    print()
    
    success = test_html_output()
    
    print()
    print("=" * 80)
    if success:
        print("🎉 TESTE CONCLUÍDO!")
        print("   Verifique o arquivo 'html_output_sample.html' para ver o HTML gerado")
        print("   Se as alterações não estão no HTML, há um problema na view ou template")
    else:
        print("❌ TESTE FALHOU!")
        print("   Verifique os erros acima")
    
    print("=" * 80)
    
    sys.exit(0 if success else 1)

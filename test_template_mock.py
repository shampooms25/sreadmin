#!/usr/bin/env python
"""
Teste para verificar as alterações no template com dados simulados
"""
import os
import sys
import django

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

# Configurar Django
django.setup()

def test_template_with_mock_data():
    """
    Testa o template com dados simulados
    """
    print("=== TESTE: Template com Dados Simulados ===")
    print()
    
    try:
        from django.template.loader import get_template
        from django.template import Context
        
        # Carregar o template
        template = get_template('admin/painel/starlink/auto_recharge_management.html')
        print("✅ Template carregado")
        
        # Dados simulados - uma Service Line com recarga ATIVA e outra DESATIVADA
        mock_data = {
            'title': 'Teste de Gerenciamento de Recarga Automática',
            'selected_account': 'ACC-2744134-64041-5',
            'account_info': {'name': 'Conta Teste'},
            'available_accounts': ['ACC-2744134-64041-5'],
            'service_lines': [
                {
                    'serviceLineNumber': 'SL-111111-11111-11',
                    'nickname': 'Teste Ativa',
                    'status': 'Online',
                    'statusClass': 'online',
                    'auto_recharge_status': {
                        'active': True,
                        'data': {
                            'content': {
                                'activatedDate': '2025-05-03'
                            }
                        }
                    }
                },
                {
                    'serviceLineNumber': 'SL-222222-22222-22',
                    'nickname': 'Teste Desativada',
                    'status': 'Online',
                    'statusClass': 'online',
                    'auto_recharge_status': {
                        'active': False
                    }
                }
            ],
            'total_count': 2,
            'active_count': 1,
            'inactive_count': 1
        }
        
        # Renderizar o template
        rendered_html = template.render(mock_data)
        
        print("✅ Template renderizado com sucesso")
        
        # Verificar se o HTML contém as alterações
        print("\n🔍 VERIFICANDO CONTEÚDO RENDERIZADO...")
        
        checks = [
            ('auto-recharge-disabled', 'Estilo CSS auto-recharge-disabled'),
            ('Recarga Automática Desativada', 'Texto alterado'),
            ('btn-warning', 'Classe btn-warning'),
            ('Ativar Recarga Automática', 'Texto do botão'),
            ('#ff9500', 'Cor laranja'),
            ('ALTERAÇÕES APLICADAS', 'Marcador no título')
        ]
        
        all_checks_passed = True
        
        for check_string, description in checks:
            if check_string in rendered_html:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description} NÃO encontrado")
                all_checks_passed = False
        
        # Salvar HTML renderizado para inspeção
        with open('template_test_output.html', 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        print(f"\n✅ HTML renderizado salvo em 'template_test_output.html'")
        
        # Verificar especificamente a seção de Service Line desativada
        if 'SL-222222-22222-22' in rendered_html:
            print("✅ Service Line de teste (desativada) encontrada no HTML")
            
            # Extrair a seção da Service Line desativada
            start_idx = rendered_html.find('SL-222222-22222-22')
            if start_idx != -1:
                # Pegar uns 500 caracteres ao redor para ver o contexto
                section = rendered_html[max(0, start_idx-200):start_idx+500]
                print("\n📝 SEÇÃO DA SERVICE LINE DESATIVADA:")
                print("-" * 60)
                print(section)
                print("-" * 60)
        
        return all_checks_passed
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE COM DADOS SIMULADOS...")
    print()
    
    success = test_template_with_mock_data()
    
    print()
    print("=" * 80)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("   As alterações estão sendo aplicadas corretamente no template")
        print("   Verifique o arquivo 'template_test_output.html'")
    else:
        print("❌ TESTE FALHOU!")
        print("   Há algum problema na aplicação das alterações")
    
    print("=" * 80)
    
    sys.exit(0 if success else 1)

#!/usr/bin/env python
"""
Teste das alterações visuais no template de gerenciamento de recarga automática
"""
import os
import sys
import django

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

# Configurar Django
django.setup()

def test_template_updates():
    """
    Testa se as alterações no template foram aplicadas corretamente
    """
    print("=== TESTE: Alterações Visuais no Template ===")
    print()
    
    try:
        template_path = "painel/templates/admin/painel/starlink/auto_recharge_management.html"
        
        print("🔍 VERIFICANDO ALTERAÇÕES NO TEMPLATE...")
        print()
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Teste 1: Verificar se o novo estilo CSS foi adicionado
        print("🎨 TESTE 1: Estilo CSS 'auto-recharge-disabled'...")
        if '.auto-recharge-disabled' in content:
            print("   ✅ SUCESSO: Estilo CSS adicionado")
        else:
            print("   ❌ ERRO: Estilo CSS não encontrado")
            return False
        
        # Teste 2: Verificar se o texto foi alterado para "Recarga Automática Desativada"
        print("📝 TESTE 2: Texto 'Recarga Automática Desativada'...")
        if 'Recarga Automática Desativada' in content:
            print("   ✅ SUCESSO: Texto alterado")
        else:
            print("   ❌ ERRO: Texto não encontrado")
            return False
        
        # Teste 3: Verificar se o botão foi alterado para "Ativar Recarga Automática"
        print("🔘 TESTE 3: Botão 'Ativar Recarga Automática'...")
        if 'Ativar Recarga Automática' in content:
            print("   ✅ SUCESSO: Texto do botão alterado")
        else:
            print("   ❌ ERRO: Texto do botão não encontrado")
            return False
        
        # Teste 4: Verificar se a cor do botão foi alterada para btn-warning
        print("🎨 TESTE 4: Cor do botão alterada para 'btn-warning'...")
        if 'btn btn-warning' in content:
            print("   ✅ SUCESSO: Cor do botão alterada")
        else:
            print("   ❌ ERRO: Cor do botão não alterada")
            return False
        
        # Teste 5: Verificar se o fundo laranja foi aplicado
        print("🧡 TESTE 5: Fundo laranja (#ff9500) no estilo...")
        if 'background: #ff9500' in content:
            print("   ✅ SUCESSO: Fundo laranja aplicado")
        else:
            print("   ❌ ERRO: Fundo laranja não encontrado")
            return False
        
        print()
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("   ✅ Estilo CSS para texto desativado adicionado")
        print("   ✅ Texto alterado para 'Recarga Automática Desativada'")
        print("   ✅ Botão alterado para 'Ativar Recarga Automática'")
        print("   ✅ Cor do botão alterada para laranja (btn-warning)")
        print("   ✅ Fundo laranja aplicado ao texto")
        
        print()
        print("📋 RESUMO DAS ALTERAÇÕES:")
        print("   • Para Service Lines com recarga DESATIVADA:")
        print("     - Texto: 'Recarga Automática Desativada'")
        print("     - Estilo: Fundo laranja (#ff9500), formatação similar ao título")
        print("     - Botão: 'Ativar Recarga Automática' (cor laranja)")
        print("   • Para Service Lines com recarga ATIVA:")
        print("     - Mantém: 'Recarga Automática: Ativa desde...'")
        print("     - Botão: 'Desativar Recarga' (cor vermelha)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DAS ALTERAÇÕES VISUAIS...")
    print()
    
    success = test_template_updates()
    
    print()
    print("=" * 80)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("   As alterações visuais foram aplicadas corretamente.")
        print("   Acesse: http://localhost:8000/admin/starlink/auto-recharge/")
        print("   para ver as mudanças na interface.")
    else:
        print("❌ TESTE FALHOU!")
        print("   Verifique os erros acima para corrigir o problema.")
    
    print("=" * 80)
    print("✅ TESTE FINALIZADO")
    print("=" * 80)
    
    sys.exit(0 if success else 1)

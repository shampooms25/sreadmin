#!/usr/bin/env python
"""
Verificar status atual da Service Line após desativação
"""
import os
import sys
import django

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

# Configurar Django
django.setup()

def check_service_line_status():
    """
    Verifica o status atual da Service Line
    """
    print("=== VERIFICAÇÃO DE STATUS DA SERVICE LINE ===")
    print()
    
    try:
        from painel.starlink_api import check_auto_recharge_status_fast
        
        account_id = "ACC-2744134-64041-5"
        service_line_number = "SL-394709-12748-31"
        
        print(f"📋 Verificando status de:")
        print(f"   Conta: {account_id}")
        print(f"   Service Line: {service_line_number}")
        print()
        
        # Verificar status
        status = check_auto_recharge_status_fast(account_id, service_line_number)
        
        if status.get("error"):
            print(f"❌ ERRO: {status['error']}")
            return False
        
        is_active = status.get("active", False)
        print(f"📊 Status da recarga automática: {'ATIVA' if is_active else 'INATIVA'}")
        
        if is_active:
            print("🔄 A recarga automática ainda está ATIVA")
            print("   As alterações visuais só aparecerão quando a recarga estiver DESATIVADA")
        else:
            print("✅ A recarga automática está DESATIVADA")
            print("   Agora você deveria ver as alterações na interface:")
            print("   - Texto: 'Recarga Automática Desativada' com fundo laranja")
            print("   - Botão: 'Ativar Recarga Automática' (cor laranja)")
        
        print(f"\n🌐 Acesse: http://localhost:8000/admin/starlink/auto-recharge/?account_id={account_id}")
        print("   para ver as alterações na interface")
        
        return not is_active  # True se estiver desativada
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 VERIFICANDO STATUS DA SERVICE LINE...")
    print()
    
    is_disabled = check_service_line_status()
    
    print()
    print("=" * 80)
    if is_disabled:
        print("🎉 SERVICE LINE ESTÁ DESATIVADA!")
        print("   As alterações visuais devem estar visíveis na interface")
    else:
        print("⚠️  SERVICE LINE AINDA ESTÁ ATIVA")
        print("   Execute novamente o teste de desativação se necessário")
    
    print("=" * 80)
    
    sys.exit(0 if is_disabled else 1)

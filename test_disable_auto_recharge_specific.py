#!/usr/bin/env python
"""
Teste específico para desativar recarga automática da service line SL-394709-12748-31
"""
import os
import sys
import django
from django.conf import settings

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

# Configurar Django
django.setup()

def test_disable_auto_recharge_specific():
    """
    Testa a desativação de recarga automática para uma service line específica
    """
    print("=== TESTE: Desativação de Recarga Automática - Service Line Específica ===")
    print("🎯 ENDPOINT: DELETE https://web-api.starlink.com/enterprise/v1/account/ACC-2744134-64041-5/service-lines/SL-394709-12748-31/opt-out")
    print()
    
    try:
        from painel.starlink_api import (
            disable_auto_recharge,
            check_auto_recharge_status_fast,
            get_valid_token
        )
        
        # Dados específicos do teste
        account_id = "ACC-2744134-64041-5"
        service_line_number = "SL-394709-12748-31"
        
        print(f"📋 DADOS DO TESTE:")
        print(f"   Conta: {account_id}")
        print(f"   Service Line: {service_line_number}")
        print()
        
        # Verificar se temos token válido
        print("🔑 VERIFICANDO AUTENTICAÇÃO...")
        token = get_valid_token()
        if not token:
            print("❌ ERRO: Token de autenticação não disponível")
            return False
        
        print(f"✅ Token obtido: {token[:20]}...")
        print()
        
        # Primeiro, verificar o status atual da recarga automática
        print("🔍 VERIFICANDO STATUS ATUAL...")
        current_status = check_auto_recharge_status_fast(account_id, service_line_number)
        
        if current_status.get("error"):
            print(f"⚠️  Erro ao verificar status atual: {current_status['error']}")
        else:
            is_active = current_status.get("active", False)
            print(f"📊 Status atual da recarga automática: {'ATIVA' if is_active else 'INATIVA'}")
        
        print()
        
        # Agora tentar desativar a recarga automática
        print("🚀 EXECUTANDO TESTE DE DESATIVAÇÃO...")
        print("=" * 60)
        
        result = disable_auto_recharge(account_id, service_line_number)
        
        print("=" * 60)
        print()
        
        # Processar resultado
        if result.get("success"):
            print("✅ SUCESSO!")
            print(f"   Message: {result.get('message', 'N/A')}")
            print(f"   Service Line: {result.get('service_line', 'N/A')}")
            
            # Verificar novamente o status após a desativação
            print("\n🔍 VERIFICANDO STATUS APÓS DESATIVAÇÃO...")
            new_status = check_auto_recharge_status_fast(account_id, service_line_number)
            
            if new_status.get("error"):
                print(f"⚠️  Erro ao verificar novo status: {new_status['error']}")
            else:
                is_active_after = new_status.get("active", False)
                print(f"📊 Status após desativação: {'ATIVA' if is_active_after else 'INATIVA'}")
                
                # Verificar se mudou
                if current_status.get("active") and not is_active_after:
                    print("🎉 CONFIRMADO: Recarga automática foi desativada com sucesso!")
                elif not current_status.get("active") and not is_active_after:
                    print("ℹ️  NOTA: Recarga automática já estava inativa")
                else:
                    print("⚠️  ATENÇÃO: Status não mudou conforme esperado")
            
        else:
            print("❌ ERRO!")
            print(f"   Error: {result.get('error', 'N/A')}")
            print(f"   Service Line: {result.get('service_line', 'N/A')}")
        
        print()
        print("=== RESULTADO DO TESTE ===")
        
        if result.get("success"):
            print("✅ TESTE CONCLUÍDO COM SUCESSO")
            print("   A chamada DELETE foi executada com sucesso")
            print("   A recarga automática foi desativada")
        else:
            print("❌ TESTE FALHOU")
            print("   A chamada DELETE não foi bem-sucedida")
            print("   Verifique os logs acima para mais detalhes")
        
        print()
        print("🔍 DETALHES TÉCNICOS:")
        print(f"   URL: https://web-api.starlink.com/enterprise/v1/account/{account_id}/service-lines/{service_line_number}/opt-out")
        print(f"   Método: DELETE")
        print(f"   Headers: Authorization: Bearer {token[:20]}...")
        print(f"   Content-Type: application/json")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DE DESATIVAÇÃO DE RECARGA AUTOMÁTICA...")
    print()
    
    success = test_disable_auto_recharge_specific()
    
    print()
    print("=" * 80)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("   A chamada DELETE foi executada com sucesso.")
        print("   Verifique os logs acima para confirmar a desativação.")
    else:
        print("❌ TESTE FALHOU!")
        print("   A chamada DELETE não foi bem-sucedida.")
        print("   Verifique os logs de erro acima para mais detalhes.")
    
    print("=" * 80)
    print("✅ TESTE FINALIZADO - VOCÊ PODE VERIFICAR O CONSOLE ACIMA")
    print("=" * 80)
    
    sys.exit(0 if success else 1)

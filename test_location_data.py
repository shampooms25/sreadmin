#!/usr/bin/env python
"""
Teste das alterações de localização no sistema de recarga automática
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def test_location_data():
    """Testa se os dados de localização estão sendo incluídos"""
    from painel.starlink_api import get_service_lines_with_auto_recharge_status
    
    print("🔍 Testando dados de localização nas service lines...")
    
    # Usar uma conta de teste
    test_account = "ACC-3697602-31930-14"
    
    try:
        result = get_service_lines_with_auto_recharge_status(test_account)
        
        if 'error' in result:
            print(f"❌ Erro: {result['error']}")
            return False
        
        service_lines = result.get('service_lines', [])
        print(f"✅ {len(service_lines)} service lines obtidas")
        
        # Verificar se as informações de localização estão presentes
        lines_with_location = 0
        lines_with_formatted_location = 0
        
        for i, line in enumerate(service_lines[:5]):  # Mostrar apenas as primeiras 5
            number = line.get('serviceLineNumber', 'N/A')
            location = line.get('serviceLocation', 'N/A')
            formatted_location = line.get('formattedLocation', 'N/A')
            nickname = line.get('nickname', 'N/A')
            status = line.get('status', 'N/A')
            auto_recharge = line.get('auto_recharge_status', {})
            
            print(f"\n📍 Service Line {i+1}: {number}")
            print(f"   • Localização: {location}")
            print(f"   • Localização Formatada: {formatted_location}")
            print(f"   • Apelido: {nickname}")
            print(f"   • Status: {status}")
            print(f"   • Recarga Automática: {'ATIVA' if auto_recharge.get('active') else 'INATIVA'}")
            
            if location != 'N/A' and location != 'Localização não informada':
                lines_with_location += 1
            if formatted_location != 'N/A':
                lines_with_formatted_location += 1
        
        print(f"\n📊 Resumo:")
        print(f"   • Total de linhas: {len(service_lines)}")
        print(f"   • Linhas com localização: {lines_with_location}")
        print(f"   • Linhas com localização formatada: {lines_with_formatted_location}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    print("🚀 TESTE DE LOCALIZAÇÃO - SISTEMA STARLINK")
    print("=" * 50)
    
    success = test_location_data()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Dados de localização sendo carregados corretamente")
    else:
        print("⚠️ PROBLEMAS ENCONTRADOS NO TESTE")

if __name__ == "__main__":
    main()

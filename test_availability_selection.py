#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_service_lines_with_location, get_available_accounts

def test_availability_selection():
    """Testa a busca de service lines para seleção de disponibilidade"""
    print("🧪 TESTE: Availability Selection - Service Lines")
    print("=" * 80)
    
    # Obter contas disponíveis
    available_accounts = get_available_accounts()
    
    # Testar a conta específica
    test_account = "ACC-2744134-64041-5"
    
    print(f"📋 Testando conta: {available_accounts[test_account]['name']} ({test_account})")
    print("-" * 60)
    
    try:
        # Obter service lines
        result = get_service_lines_with_location(test_account)
        
        if "error" in result:
            print(f"❌ Erro: {result['error']}")
            return False
        
        service_lines_data = result.get("service_lines", [])
        
        print(f"✅ {len(service_lines_data)} service lines encontradas")
        
        # Processar dados como faz a view
        available_service_lines = []
        service_line_locations = {}
        
        for service_line in service_lines_data:
            service_line_number = service_line.get("serviceLineNumber")
            if service_line_number:
                available_service_lines.append(service_line_number)
                service_line_locations[service_line_number] = service_line.get("serviceLocation", "Localização não informada")
        
        total_service_lines = len(available_service_lines)
        
        print(f"📊 Total processadas: {total_service_lines}")
        print("\n📋 Primeiras 10 service lines:")
        for i, sl in enumerate(available_service_lines[:10]):
            location = service_line_locations[sl]
            print(f"  {i+1:2}. {sl} - {location}")
        
        if total_service_lines > 10:
            print(f"  ... e mais {total_service_lines - 10} service lines")
        
        return True
        
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_availability_selection()

#!/usr/bin/env python
import os
import sys
import django
import json

# Configurar Django
sys.path.append('c:\\Projetos\\Poppnet\\sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_service_lines_with_location

def debug_billing_error():
    print("🔍 Testando obtenção de service lines...")
    
    # Testar função que obtém as service lines
    account_id = "ACC-2744134-64041-5"
    
    try:
        service_lines_result = get_service_lines_with_location(account_id)
        
        print(f"📊 Resultado da consulta de service lines:")
        print(f"  - Total: {service_lines_result.get('total_service_lines', 0)}")
        print(f"  - Erro: {service_lines_result.get('error', 'Nenhum')}")
        
        if service_lines_result.get('service_lines'):
            print(f"📋 Primeiras 3 service lines:")
            for i, sl in enumerate(service_lines_result['service_lines'][:3]):
                print(f"  [{i+1}] Number: {sl.get('serviceLineNumber')}")
                print(f"      Nickname: {sl.get('nickname', 'N/A')}")
                print(f"      Status: {sl.get('status', 'N/A')}")
                print(f"      Location: {sl.get('serviceLocation', 'N/A')}")
                print()
            
            # Verificar se os service line numbers são válidos
            service_line_numbers = [sl.get("serviceLineNumber") for sl in service_lines_result['service_lines'] if sl.get("serviceLineNumber")]
            print(f"🔢 Service Line Numbers extraídos: {len(service_line_numbers)}")
            
            # Mostrar alguns exemplos
            if service_line_numbers:
                print(f"📝 Exemplos:")
                for i, number in enumerate(service_line_numbers[:5]):
                    print(f"  [{i+1}] {number} (tipo: {type(number)})")
                    
                # Verificar se há algum valor None ou inválido
                invalid_numbers = [sl.get("serviceLineNumber") for sl in service_lines_result['service_lines'] if not sl.get("serviceLineNumber")]
                if invalid_numbers:
                    print(f"⚠️  Service lines com números inválidos: {len(invalid_numbers)}")
                    
        else:
            print("❌ Nenhuma service line encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao testar: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_billing_error()

#!/usr/bin/env python3
"""
Teste para verificar a correção do erro HTTP 405 na verificação de recarga automática
"""

import os
import sys
import django
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import check_auto_recharge_status_fast, get_service_lines_with_location

def test_single_service_line():
    """Testa a verificação de recarga automática para uma única service line"""
    print("🧪 TESTE: Verificação de recarga automática - correção do erro HTTP 405")
    print("=" * 80)
    
    account_id = "ACC-2744134-64041-5"
    
    # Primeiro, obter algumas service lines para testar
    print(f"📋 Obtendo service lines da conta: {account_id}")
    service_lines_result = get_service_lines_with_location(account_id)
    
    if "error" in service_lines_result:
        print(f"❌ Erro ao obter service lines: {service_lines_result['error']}")
        return
    
    service_lines = service_lines_result.get("service_lines", [])
    
    if not service_lines:
        print("❌ Nenhuma service line encontrada para teste")
        return
    
    # Testar as primeiras 3 service lines
    test_lines = service_lines[:3]
    
    print(f"🔍 Testando {len(test_lines)} service lines:")
    
    for i, line in enumerate(test_lines, 1):
        service_line_number = line.get("serviceLineNumber", "")
        
        if not service_line_number:
            print(f"[{i}] ⚠️  Service line sem número - pulando")
            continue
            
        print(f"\n[{i}] 🔍 Testando Service Line: {service_line_number}")
        print(f"    📍 Localização: {line.get('serviceLocation', 'N/A')}")
        
        # Testar a função corrigida
        result = check_auto_recharge_status_fast(account_id, service_line_number)
        
        if result.get("error"):
            print(f"    ❌ Erro: {result['error']}")
        else:
            status = "ATIVA" if result.get("active") else "INATIVA"
            print(f"    ✅ Status: Recarga automática {status}")
            
            if result.get("data"):
                print(f"    📊 Dados retornados: {type(result['data'])}")
    
    print("\n" + "=" * 80)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    test_single_service_line()

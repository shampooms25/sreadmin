#!/usr/bin/env python3
"""
Teste completo do painel de recarga automática após correção do erro HTTP 405
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

from painel.starlink_api import get_service_lines_with_auto_recharge_status
import time

def test_complete_panel():
    """Testa a funcionalidade completa do painel de recarga automática"""
    print("🧪 TESTE COMPLETO: Painel de recarga automática")
    print("=" * 80)
    
    account_id = "ACC-2744134-64041-5"
    
    print(f"📋 Obtendo service lines com status de recarga automática para: {account_id}")
    start_time = time.time()
    
    result = get_service_lines_with_auto_recharge_status(account_id)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"⏱️  Tempo total: {total_time:.2f} segundos")
    
    if "error" in result:
        print(f"❌ Erro: {result['error']}")
        return
    
    service_lines = result.get("service_lines", [])
    total_count = result.get("total_count", 0)
    performance_stats = result.get("performance_stats", {})
    
    print(f"📊 Resultados:")
    print(f"   📈 Total de service lines: {total_count}")
    print(f"   🏃 Performance stats: {performance_stats}")
    
    # Contar status
    active_count = 0
    inactive_count = 0
    error_count = 0
    
    print(f"\n🔍 Detalhes das service lines:")
    for i, line in enumerate(service_lines[:5], 1):  # Mostrar apenas as primeiras 5
        service_line_number = line.get("serviceLineNumber", "N/A")
        location = line.get("serviceLocation", "N/A")
        auto_recharge = line.get("auto_recharge_status", {})
        
        if auto_recharge.get("error"):
            status = f"❌ ERRO: {auto_recharge['error']}"
            error_count += 1
        elif auto_recharge.get("active"):
            status = "✅ ATIVA"
            active_count += 1
        else:
            status = "❌ INATIVA"
            inactive_count += 1
        
        print(f"   [{i}] {service_line_number}")
        print(f"       📍 {location}")
        print(f"       🔄 {status}")
        print()
    
    # Contar totais
    for line in service_lines:
        auto_recharge = line.get("auto_recharge_status", {})
        if auto_recharge.get("error"):
            error_count += 1
        elif auto_recharge.get("active"):
            active_count += 1
        else:
            inactive_count += 1
    
    print(f"📊 Resumo final:")
    print(f"   ✅ Recarga automática ATIVA: {active_count}")
    print(f"   ❌ Recarga automática INATIVA: {inactive_count}")
    print(f"   ⚠️  Erros: {error_count}")
    print(f"   📈 Total processado: {active_count + inactive_count + error_count}")
    
    if error_count == 0:
        print(f"\n🎉 SUCESSO! Nenhum erro HTTP 405 encontrado!")
        print(f"🚀 O painel está funcionando corretamente!")
    else:
        print(f"\n⚠️  Ainda há {error_count} erros a serem investigados.")
    
    print("\n" + "=" * 80)
    print("✅ Teste completo concluído!")

if __name__ == "__main__":
    test_complete_panel()

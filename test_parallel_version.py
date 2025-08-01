#!/usr/bin/env python3
"""
Teste da versão paralela otimizada
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

from painel.starlink_api import get_service_lines_with_auto_recharge_status_parallel, clear_auto_recharge_cache
import time

def test_parallel_version():
    """Testa a versão paralela otimizada"""
    print("🧪 TESTE: Versão paralela otimizada")
    print("=" * 80)
    
    # Limpar cache primeiro
    clear_auto_recharge_cache()
    
    account_id = "ACC-2744134-64041-5"
    
    print(f"📋 Testando consulta paralela para: {account_id}")
    start_time = time.time()
    
    result = get_service_lines_with_auto_recharge_status_parallel(account_id, max_workers=5)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"⏱️  Tempo total (parallel): {total_time:.2f} segundos")
    
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
    
    for line in service_lines:
        auto_recharge = line.get("auto_recharge_status", {})
        if auto_recharge.get("error"):
            error_count += 1
        elif auto_recharge.get("active"):
            active_count += 1
        else:
            inactive_count += 1
    
    print(f"📊 Resumo:")
    print(f"   ✅ Recarga automática ATIVA: {active_count}")
    print(f"   ❌ Recarga automática INATIVA: {inactive_count}")
    print(f"   ⚠️  Erros: {error_count}")
    
    # Calcular melhoria de performance
    sequential_time = 127.05  # Do teste anterior
    improvement = ((sequential_time - total_time) / sequential_time) * 100
    
    print(f"\n🚀 MELHORIA DE PERFORMANCE:")
    print(f"   📊 Tempo sequencial: {sequential_time:.2f}s")
    print(f"   📊 Tempo paralelo: {total_time:.2f}s")
    print(f"   📈 Melhoria: {improvement:.1f}%")
    
    if error_count == 0:
        print(f"\n🎉 SUCESSO! Versão paralela funcionando perfeitamente!")
    else:
        print(f"\n⚠️  Ainda há {error_count} erros.")
    
    print("\n" + "=" * 80)
    print("✅ Teste paralelo concluído!")

if __name__ == "__main__":
    test_parallel_version()

#!/usr/bin/env python
"""
Teste de performance das novas funcionalidades otimizadas
"""

import os
import sys
import django
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import (
    get_available_accounts,
    get_service_lines_with_auto_recharge_status,
    get_service_lines_with_auto_recharge_status_parallel,
    clear_auto_recharge_cache
)

def test_performance_comparison():
    """Compara performance entre versão sequencial e paralela"""
    print("🚀 TESTE DE PERFORMANCE - OTIMIZAÇÕES DE RECARGA AUTOMÁTICA")
    print("=" * 80)
    
    # Obter contas disponíveis
    accounts = get_available_accounts()
    if not accounts:
        print("❌ Nenhuma conta disponível para teste")
        return
    
    # Usar primeira conta para teste
    test_account = accounts[0]
    print(f"📋 Testando com conta: {test_account}")
    
    # Limpar cache para teste justo
    clear_auto_recharge_cache()
    print("🗑️ Cache limpo")
    
    # Teste 1: Versão sequencial
    print("\n🔄 TESTE 1: Versão Sequencial")
    print("-" * 40)
    start_time = time.time()
    
    result_sequential = get_service_lines_with_auto_recharge_status(test_account)
    
    end_time = time.time()
    sequential_time = end_time - start_time
    
    if "error" in result_sequential:
        print(f"❌ Erro na versão sequencial: {result_sequential['error']}")
        return
    
    print(f"✅ Versão sequencial finalizada")
    print(f"📊 Tempo: {sequential_time:.2f}s")
    print(f"📋 Service Lines: {result_sequential.get('total_count', 0)}")
    
    if 'performance_stats' in result_sequential:
        stats = result_sequential['performance_stats']
        print(f"📦 Cache hits: {stats.get('cache_hits', 0)}")
        print(f"🌐 API calls: {stats.get('api_calls', 0)}")
    
    # Aguardar um pouco e testar versão paralela
    print("\n⏳ Aguardando 2 segundos...")
    time.sleep(2)
    
    # Teste 2: Versão paralela (com cache já populado)
    print("\n⚡ TESTE 2: Versão Paralela (com cache)")
    print("-" * 40)
    start_time = time.time()
    
    result_parallel = get_service_lines_with_auto_recharge_status_parallel(test_account, max_workers=5)
    
    end_time = time.time()
    parallel_time = end_time - start_time
    
    if "error" in result_parallel:
        print(f"❌ Erro na versão paralela: {result_parallel['error']}")
        return
    
    print(f"✅ Versão paralela finalizada")
    print(f"📊 Tempo: {parallel_time:.2f}s")
    print(f"📋 Service Lines: {result_parallel.get('total_count', 0)}")
    
    if 'performance_stats' in result_parallel:
        stats = result_parallel['performance_stats']
        print(f"📦 Cache hits: {stats.get('cache_hits', 0)}")
        print(f"🌐 API calls: {stats.get('api_calls', 0)}")
        print(f"⚡ Workers: {stats.get('parallel_workers', 0)}")
    
    # Limpar cache novamente
    clear_auto_recharge_cache()
    print("\n🗑️ Cache limpo novamente")
    
    # Teste 3: Versão paralela sem cache
    print("\n⚡ TESTE 3: Versão Paralela (sem cache)")
    print("-" * 40)
    start_time = time.time()
    
    result_parallel_no_cache = get_service_lines_with_auto_recharge_status_parallel(test_account, max_workers=5)
    
    end_time = time.time()
    parallel_no_cache_time = end_time - start_time
    
    if "error" in result_parallel_no_cache:
        print(f"❌ Erro na versão paralela sem cache: {result_parallel_no_cache['error']}")
        return
    
    print(f"✅ Versão paralela sem cache finalizada")
    print(f"📊 Tempo: {parallel_no_cache_time:.2f}s")
    print(f"📋 Service Lines: {result_parallel_no_cache.get('total_count', 0)}")
    
    if 'performance_stats' in result_parallel_no_cache:
        stats = result_parallel_no_cache['performance_stats']
        print(f"📦 Cache hits: {stats.get('cache_hits', 0)}")
        print(f"🌐 API calls: {stats.get('api_calls', 0)}")
        print(f"⚡ Workers: {stats.get('parallel_workers', 0)}")
    
    # Comparação final
    print("\n📊 COMPARAÇÃO FINAL")
    print("=" * 80)
    print(f"🔄 Sequencial:           {sequential_time:.2f}s")
    print(f"⚡ Paralelo (com cache): {parallel_time:.2f}s")
    print(f"⚡ Paralelo (sem cache): {parallel_no_cache_time:.2f}s")
    
    if sequential_time > 0:
        improvement_with_cache = ((sequential_time - parallel_time) / sequential_time) * 100
        improvement_no_cache = ((sequential_time - parallel_no_cache_time) / sequential_time) * 100
        
        print(f"📈 Melhoria com cache:   {improvement_with_cache:.1f}%")
        print(f"📈 Melhoria sem cache:   {improvement_no_cache:.1f}%")
    
    print("\n✅ Teste finalizado!")

if __name__ == "__main__":
    test_performance_comparison()

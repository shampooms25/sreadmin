#!/usr/bin/env python3
"""
Teste completo das novas funcionalidades de ping/ICMP
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def test_ping_integration():
    """
    Testar a nova integração de métricas de ping/ICMP
    """
    print("=" * 70)
    print("TESTE: INTEGRAÇÃO DE MÉTRICAS DE PING/ICMP")
    print("=" * 70)
    print()
    
    from painel.starlink_api import get_telemetry_data
    from datetime import datetime, timedelta
    
    # Service lines para teste
    test_service_lines = [
        "SL-5242096-78596-88",
        "SL-3771955-54471-83", 
        "SL-3481747-13739-82"
    ]
    
    # Datas para teste
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    print(f"📅 Período de teste: {start_str} até {end_str}")
    print(f"🔍 Testando {len(test_service_lines)} service lines")
    print()
    
    results = []
    
    for i, service_line in enumerate(test_service_lines, 1):
        print(f"🧪 Teste {i}/3: {service_line}")
        print("-" * 50)
        
        try:
            # Chamar a nova função de telemetria
            telemetry_data = get_telemetry_data(
                service_line_number=service_line,
                start_date=start_str,
                end_date=end_str
            )
            
            # Analisar resultado
            print(f"✅ Dados obtidos com sucesso")
            print(f"   API Source: {telemetry_data.get('api_source', 'N/A')}")
            print(f"   Uptime: {telemetry_data.get('uptime_percentage', 0)}%")
            print(f"   Downtime: {telemetry_data.get('downtime_hours', 0)}h")
            print(f"   Obstruction: {telemetry_data.get('obstruction_hours', 0)}h")
            print(f"   Status: {telemetry_data.get('availability_status', 'N/A')}")
            
            # Verificar métricas de ping
            ping_metrics = telemetry_data.get('ping_metrics')
            has_real_ping = telemetry_data.get('has_real_ping_data', False)
            
            if ping_metrics:
                print(f"   🎯 Métricas de PING encontradas:")
                for key, value in ping_metrics.items():
                    print(f"      - {key}: {value}")
                
                # Classificar métricas
                latency_metrics = {k: v for k, v in ping_metrics.items() if 'latency' in k or 'ping' in k}
                loss_metrics = {k: v for k, v in ping_metrics.items() if 'loss' in k}
                quality_metrics = {k: v for k, v in ping_metrics.items() if 'quality' in k or 'jitter' in k}
                
                if latency_metrics:
                    avg_latency = sum(latency_metrics.values()) / len(latency_metrics)
                    print(f"      📊 Latência média: {avg_latency:.1f}ms")
                
                if loss_metrics:
                    avg_loss = sum(loss_metrics.values()) / len(loss_metrics)
                    print(f"      📊 Packet loss médio: {avg_loss:.1f}%")
            
            elif has_real_ping:
                print(f"   ✅ API tem dados de ping (estrutura não mapeada)")
            else:
                print(f"   ❌ Nenhuma métrica de ping encontrada")
            
            results.append({
                'service_line': service_line,
                'success': True,
                'has_ping_metrics': bool(ping_metrics),
                'has_real_ping_data': has_real_ping,
                'api_source': telemetry_data.get('api_source'),
                'ping_metrics': ping_metrics
            })
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            results.append({
                'service_line': service_line,
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # Resumo dos resultados
    print("📊 RESUMO DOS RESULTADOS")
    print("-" * 30)
    
    successful_tests = [r for r in results if r['success']]
    tests_with_ping = [r for r in results if r.get('has_ping_metrics', False)]
    tests_with_real_ping = [r for r in results if r.get('has_real_ping_data', False)]
    
    print(f"✅ Testes bem-sucedidos: {len(successful_tests)}/{len(results)}")
    print(f"🎯 Com métricas de ping estruturadas: {len(tests_with_ping)}/{len(results)}")
    print(f"📡 Com dados reais de ping da API: {len(tests_with_real_ping)}/{len(results)}")
    
    # APIs utilizadas
    api_sources = {}
    for result in successful_tests:
        source = result.get('api_source', 'unknown')
        api_sources[source] = api_sources.get(source, 0) + 1
    
    print(f"📡 APIs utilizadas: {dict(api_sources)}")
    
    # Análise das métricas encontradas
    if tests_with_ping:
        print(f"\n🔍 MÉTRICAS DE PING ENCONTRADAS:")
        all_metrics = {}
        for result in tests_with_ping:
            for key, value in result.get('ping_metrics', {}).items():
                if key not in all_metrics:
                    all_metrics[key] = []
                all_metrics[key].append(value)
        
        for metric, values in all_metrics.items():
            avg_val = sum(values) / len(values)
            print(f"   - {metric}: média {avg_val:.2f} (amostras: {len(values)})")
    
    print("\n💡 RECOMENDAÇÕES:")
    if len(tests_with_real_ping) > 0:
        print("✅ A API da Starlink POSSUI dados de ping/ICMP!")
        print("   → Utilizar dados oficiais da API")
        print("   → Implementar parser para extrair todas as métricas")
    else:
        print("❌ A API da Starlink NÃO possui dados de ping/ICMP acessíveis")
        print("   → Considerar implementar monitoramento complementar")
        print("   → Usar dados simulados baseados em uptime/downtime")
    
    return results

if __name__ == "__main__":
    test_ping_integration()

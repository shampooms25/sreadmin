#!/usr/bin/env python3
"""
Teste para verificar a correção do relatório de uso
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

print("🧪 Testando correção do relatório de uso...")

try:
    from painel.starlink_api import get_usage_report_data
    print("✅ Função importada com sucesso")
    
    result = get_usage_report_data("ACC-2744134-64041-5")
    print("✅ Função executada")
    
    if result.get("success"):
        usage_data = result.get('usage_data', [])
        statistics = result.get('statistics', {})
        print(f"✅ Relatório gerado! {len(usage_data)} Service Lines")
        print(f"📊 Estatísticas: {statistics.get('total_lines', 0)} linhas totais")
        print("🎉 CORREÇÃO DO ERRO 'usage_data' APLICADA COM SUCESSO!")
        
        # Mostrar algumas linhas de exemplo
        print(f"\n📋 Primeiras 3 linhas:")
        for i, line in enumerate(usage_data[:3], 1):
            print(f"  {i}. {line['serviceLineNumber']} - {line['location'][:30]}...")
            print(f"     💾 {line['totalGB']:.2f} GB ({line['usagePercentage']}%)")
    else:
        print(f"❌ Erro: {result.get('error')}")
        
except Exception as e:
    print(f"❌ Erro na execução: {e}")
    import traceback
    traceback.print_exc()

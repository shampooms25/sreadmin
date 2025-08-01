#!/usr/bin/env python3
"""
Teste para verificar a correção do relatório de uso
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

from painel.starlink_api import get_usage_report_data

def test_usage_report():
    """Testa a função de relatório de uso"""
    print("🧪 TESTE: Correção do relatório de uso")
    print("=" * 80)
    
    account_id = "ACC-2744134-64041-5"
    
    print(f"📋 Testando relatório de uso para: {account_id}")
    
    result = get_usage_report_data(account_id)
    
    if "error" in result:
        print(f"❌ Erro: {result['error']}")
        return
    
    usage_data = result.get("usage_data", [])
    statistics = result.get("statistics", {})
    
    print(f"✅ Relatório gerado com sucesso!")
    print(f"📊 Total de Service Lines: {len(usage_data)}")
    print(f"📈 Estatísticas:")
    for key, value in statistics.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔍 Primeiras 3 Service Lines:")
    for i, line in enumerate(usage_data[:3], 1):
        print(f"   [{i}] {line['serviceLineNumber']}")
        print(f"       📍 {line['location']}")
        print(f"       💾 Total: {line['totalGB']:.2f} GB ({line['totalTB']} TB)")
        print(f"       📊 Uso: {line['usagePercentage']}% ({line['threshold']})")
        print()
    
    print("=" * 80)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    test_usage_report()

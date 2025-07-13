#!/usr/bin/env python3
"""
VALIDAÇÃO FINAL DA CORREÇÃO DO RELATÓRIO DE USO STARLINK
========================================================

Este script valida se a correção implementada está funcionando corretamente:
- Verifica se o valor do SL-854897-75238-43 está próximo de 90 GB (valor real)
- Confirma que não está mais usando o valor incorreto simulado de 268 GB
- Valida a estrutura dos dados e o funcionamento da API

Esperado: ~90 GB (valor real da API) ao invés de 268 GB (valor simulado)
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_usage_report_data

def validate_billing_fix():
    """Validação final da correção do billing"""
    print("🎯 VALIDAÇÃO FINAL DA CORREÇÃO DO RELATÓRIO DE USO STARLINK")
    print("=" * 70)
    print(f"🕒 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Configurações do teste
    account_id = "ACC-2744134-64041-5"
    target_sl = "SL-854897-75238-43"
    expected_min = 85.0  # GB
    expected_max = 95.0  # GB
    old_wrong_value = 268.45  # Valor incorreto que estava sendo exibido
    
    print(f"📋 DADOS DO TESTE:")
    print(f"   🏢 Account ID: {account_id}")
    print(f"   📡 Service Line: {target_sl}")
    print(f"   🎯 Valor esperado: {expected_min}-{expected_max} GB")
    print(f"   ❌ Valor incorreto anterior: {old_wrong_value} GB")
    print()
    
    try:
        # Obter dados do relatório
        print("🔍 EXECUTANDO TESTE...")
        result = get_usage_report_data(account_id)
        
        if "error" in result:
            print(f"❌ ERRO: {result['error']}")
            return False
        
        usage_data = result.get("usage_data", [])
        total_lines = len(usage_data)
        
        print(f"📊 RESULTADO DA CONSULTA:")
        print(f"   ✅ Total de Service Lines: {total_lines}")
        print(f"   ✅ Função executada com sucesso")
        print()
        
        # Procurar pela Service Line específica
        target_line = None
        for line in usage_data:
            if line.get("serviceLineNumber") == target_sl:
                target_line = line
                break
        
        if not target_line:
            print(f"❌ FALHA: Service Line {target_sl} não encontrada!")
            print(f"   Service Lines disponíveis: {[sl['serviceLineNumber'] for sl in usage_data[:5]]}...")
            return False
        
        # Validar o valor
        total_gb = target_line.get("totalGB", 0)
        priority_gb = target_line.get("priorityGB", 0)
        standard_gb = target_line.get("standardGB", 0)
        location = target_line.get("location", "N/A")
        
        print(f"🎯 SERVICE LINE ENCONTRADA:")
        print(f"   📡 Service Line: {target_sl}")
        print(f"   📍 Localização: {location}")
        print(f"   📊 Priority GB: {priority_gb:.2f} GB")
        print(f"   📊 Standard GB: {standard_gb:.2f} GB")
        print(f"   🎯 Total GB: {total_gb:.2f} GB")
        print(f"   📅 Fonte: {target_line.get('data_source', 'N/A')}")
        print()
        
        # Validação principal
        print("🔍 VALIDAÇÃO:")
        
        # Teste 1: Valor está na faixa correta?
        if expected_min <= total_gb <= expected_max:
            print(f"   ✅ Valor correto: {total_gb:.2f} GB está entre {expected_min}-{expected_max} GB")
            test1_passed = True
        else:
            print(f"   ❌ Valor incorreto: {total_gb:.2f} GB não está entre {expected_min}-{expected_max} GB")
            test1_passed = False
        
        # Teste 2: Não é mais o valor incorreto anterior?
        if abs(total_gb - old_wrong_value) > 100:  # Diferença grande o suficiente
            print(f"   ✅ Não é mais o valor incorreto anterior ({old_wrong_value} GB)")
            test2_passed = True
        else:
            print(f"   ❌ Ainda pode ser o valor incorreto anterior ({old_wrong_value} GB)")
            test2_passed = False
        
        # Teste 3: Dados da API real sendo usados?
        if target_line.get("data_source") == "real_api":
            print(f"   ✅ Usando dados reais da API Starlink")
            test3_passed = True
        else:
            print(f"   ⚠️  Não confirmado se está usando dados reais da API")
            test3_passed = False
        
        # Teste 4: Soma Priority + Standard está correta?
        calculated_total = priority_gb + standard_gb
        if abs(calculated_total - total_gb) < 0.1:  # Tolerância para arredondamento
            print(f"   ✅ Soma Priority + Standard está correta: {calculated_total:.2f} GB")
            test4_passed = True
        else:
            print(f"   ❌ Soma Priority + Standard incorreta: {calculated_total:.2f} ≠ {total_gb:.2f}")
            test4_passed = False
        
        # Resultado final
        all_tests_passed = test1_passed and test2_passed and test3_passed and test4_passed
        
        print()
        print("🎯 RESULTADO FINAL:")
        print("=" * 70)
        print(f"   📊 Teste de valor correto: {'✅ PASSOU' if test1_passed else '❌ FALHOU'}")
        print(f"   🔄 Teste de correção: {'✅ PASSOU' if test2_passed else '❌ FALHOU'}")
        print(f"   🌐 Teste de fonte de dados: {'✅ PASSOU' if test3_passed else '⚠️ INCERTO'}")
        print(f"   🧮 Teste de cálculo: {'✅ PASSOU' if test4_passed else '❌ FALHOU'}")
        print()
        
        if all_tests_passed:
            print("🎉 VALIDAÇÃO COMPLETA: TODOS OS TESTES PASSARAM!")
            print("✅ A correção do relatório de uso está funcionando corretamente!")
            print(f"🌐 Acesse: http://localhost:8000/admin/starlink/usage-report/?account_id={account_id}")
            print("   (Faça login como staff member para ver a interface)")
        else:
            print("❌ VALIDAÇÃO FALHOU: Alguns testes não passaram")
            print("🔧 Revise a implementação da função get_usage_report_data")
        
        return all_tests_passed
        
    except Exception as e:
        print(f"❌ ERRO DURANTE A VALIDAÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_billing_fix()
    print()
    print("=" * 70)
    if success:
        print("🎉 CORREÇÃO VALIDADA COM SUCESSO!")
        print("   O relatório de uso agora exibe valores corretos da API Starlink")
    else:
        print("❌ CORREÇÃO PRECISA DE AJUSTES")
    print("=" * 70)
    
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Teste para validar se a correção do relatório de uso está funcionando corretamente.
Testa tanto o endpoint real quanto a função get_usage_report_data.
"""

import os
import sys
import django
import json
import requests
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_usage_report_data

def test_usage_report_function():
    """Testa a função get_usage_report_data diretamente"""
    print("🚀 TESTANDO FUNÇÃO get_usage_report_data...")
    print("=" * 50)
    
    try:
        account_id = "ACC-2744134-64041-5"
        result = get_usage_report_data(account_id)
        
        print(f"📋 Testando conta: {account_id}")
        print(f"📊 Service Lines encontradas: {len(result.get('usage_data', []))}")
        
        # Procurar pela Service Line específica que corrigimos
        target_sl = "SL-854897-75238-43"
        found_sl = None
        
        for sl in result.get('usage_data', []):
            print(f"   📡 {sl['serviceLineNumber']}: {sl['totalGB']:.2f} GB")
            if sl['serviceLineNumber'] == target_sl:
                found_sl = sl
        
        if found_sl:
            print(f"\n🎯 SERVICE LINE ALVO ENCONTRADA:")
            print(f"   📡 Service Line: {found_sl['serviceLineNumber']}")
            print(f"   📊 Uso atual: {found_sl['totalGB']:.2f} GB")
            print(f"   📊 Priority GB: {found_sl['priorityGB']:.2f} GB")
            print(f"   📊 Standard GB: {found_sl['standardGB']:.2f} GB")
            print(f"   📋 Status: {found_sl['status']}")
            print(f"   📍 Localização: {found_sl['location']}")
            
            # Verificar se o valor está próximo do esperado (89.97 GB)
            expected_usage = 89.97
            actual_usage = found_sl['totalGB']
            
            if abs(actual_usage - expected_usage) < 5.0:  # Tolerância de 5 GB
                print(f"   ✅ VALOR CORRETO! Esperado: ~{expected_usage} GB, Atual: {actual_usage:.2f} GB")
                return True
            else:
                print(f"   ❌ VALOR INCORRETO! Esperado: ~{expected_usage} GB, Atual: {actual_usage:.2f} GB")
                print(f"   🔧 Diferença: {abs(actual_usage - expected_usage):.2f} GB")
                return False
        else:
            print(f"   ❌ Service Line {target_sl} não encontrada!")
            return False
            
    except Exception as e:
        print(f"❌ ERRO ao testar função: {e}")
        return False

def test_usage_report_endpoint():
    """Testa o endpoint web do relatório de uso"""
    print("\n🌐 TESTANDO ENDPOINT WEB...")
    print("=" * 50)
    
    try:
        url = "http://localhost:8000/admin/starlink/usage-report/?account_id=ACC-2744134-64041-5"
        print(f"📋 Testando URL: {url}")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"   ✅ Resposta HTTP: {response.status_code}")
            print(f"   📏 Tamanho da resposta: {len(response.text)} bytes")
            
            # Verificar se a página contém alguns elementos esperados
            content = response.text
            
            checks = [
                ("SL-854897-75238-43", "Service Line específica"),
                ("GB", "Valores em GB"),
                ("90.", "Valor próximo de 90 GB"),  # Pode ser 90.96, 90.9, etc.
                ("Priority", "Campo Priority"),
            ]
            
            results = []
            for check, description in checks:
                if check in content:
                    print(f"   ✅ {description}: Encontrado")
                    results.append(True)
                else:
                    print(f"   ❌ {description}: Não encontrado")
                    results.append(False)
            
            # Se encontrou a SL e o valor próximo de 90, consideramos sucesso
            if results[0] and results[2]:  # SL encontrada e valor ~90
                print(f"   🎯 TESTE PASSOU: Service Line e valor correto encontrados!")
                return True
            else:
                print(f"   ⚠️  TESTE PARCIAL: Alguns elementos não encontrados")
                return False
                
        else:
            print(f"   ❌ Erro HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ ERRO: Servidor não está rodando em localhost:8000")
        return False
    except Exception as e:
        print(f"   ❌ ERRO ao testar endpoint: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🎯 TESTE DE VALIDAÇÃO DA CORREÇÃO DO RELATÓRIO DE USO")
    print("=" * 60)
    print(f"🕒 Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Teste 1: Função direta
    function_test = test_usage_report_function()
    
    # Teste 2: Endpoint web
    endpoint_test = test_usage_report_endpoint()
    
    # Resultado final
    print("\n🎯 RESULTADO FINAL:")
    print("=" * 60)
    print(f"📊 Teste da função: {'✅ PASSOU' if function_test else '❌ FALHOU'}")
    print(f"🌐 Teste do endpoint: {'✅ PASSOU' if endpoint_test else '❌ FALHOU'}")
    
    if function_test and endpoint_test:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A correção do relatório de uso está funcionando corretamente!")
        print(f"🌐 Acesse: http://localhost:8000/admin/starlink/usage-report/?account_id=ACC-2744134-64041-5")
        return True
    elif function_test:
        print("⚠️  FUNÇÃO CORRIGIDA, MAS ENDPOINT COM PROBLEMAS")
        print("🔧 Verifique se o servidor está rodando e tente novamente")
        return False
    else:
        print("❌ CORREÇÃO NÃO FUNCIONOU COMPLETAMENTE")
        print("🔧 Revise o código da função get_usage_report_data")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

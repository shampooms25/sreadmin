#!/usr/bin/env python
"""
Análise específica dos dados de billing da Service Line SL-854897-75238-43
"""
import os
import sys
import django
import requests
import json

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')

# Configurar Django
django.setup()

def analyze_service_line_billing():
    """
    Analisa os dados de billing específicos da Service Line SL-854897-75238-43
    """
    print("=== ANÁLISE: Billing da Service Line SL-854897-75238-43 ===")
    print()
    
    try:
        from painel.starlink_api import get_valid_token
        
        # Dados específicos
        account_id = "ACC-2744134-64041-5"
        service_line_number = "SL-854897-75238-43"
        
        print(f"📋 ANALISANDO:")
        print(f"   Conta: {account_id}")
        print(f"   Service Line: {service_line_number}")
        print(f"   Período esperado: 03/07/2025 até hoje")
        print(f"   Valor esperado: ~90 GB (Priority + Standard)")
        print(f"   Valor atual no sistema: 268,45 GB (INCORRETO)")
        print()
        
        # Obter token
        token = get_valid_token()
        if not token:
            print("❌ ERRO: Token não disponível")
            return False
        
        print(f"✅ Token obtido: {token[:20]}...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Consultar billing cycles com filtro específico para esta service line
        print("🔍 CONSULTANDO BILLING CYCLES...")
        
        url = f"https://web-api.starlink.com/enterprise/v1/accounts/{account_id}/billing-cycles/query"
        payload = {
            "serviceLinesFilter": [service_line_number],
            "previousBillingCycles": 3,  # Últimos 3 ciclos
            "pageIndex": 0,
            "pageLimit": 10
        }
        
        print(f"   URL: {url}")
        print(f"   Filtro: {service_line_number}")
        print()
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ DADOS OBTIDOS COM SUCESSO!")
            
            # Salvar dados completos para análise
            with open(f'billing_analysis_{service_line_number.replace("-", "_")}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"📄 Dados salvos em: billing_analysis_{service_line_number.replace('-', '_')}.json")
            print()
            
            # Analisar estrutura dos dados
            print("📊 ANALISANDO ESTRUTURA DOS DADOS...")
            
            if "content" in data and "results" in data["content"]:
                results = data["content"]["results"]
                print(f"   {len(results)} resultados encontrados")
                
                for i, result in enumerate(results):
                    sl_number = result.get("serviceLineNumber", "N/A")
                    print(f"\n   📋 RESULTADO {i+1}: {sl_number}")
                    
                    if sl_number == service_line_number:
                        print("   🎯 SERVICE LINE ALVO ENCONTRADA!")
                        
                        billing_cycles = result.get("billingCycles", [])
                        print(f"   📅 {len(billing_cycles)} ciclos de billing encontrados")
                        
                        for j, cycle in enumerate(billing_cycles):
                            print(f"\n   📊 CICLO {j+1}:")
                            
                            # Informações básicas do ciclo
                            billing_date = cycle.get("billingDate", "N/A")
                            cycle_start = cycle.get("cycleStartDate", "N/A")
                            cycle_end = cycle.get("cycleEndDate", "N/A")
                            total_amount = cycle.get("totalAmount", 0)
                            
                            print(f"      Data do billing: {billing_date}")
                            print(f"      Início do ciclo: {cycle_start}")
                            print(f"      Fim do ciclo: {cycle_end}")
                            print(f"      Valor total: ${total_amount}")
                            
                            # Procurar dados de consumo
                            if "dataBlocks" in cycle:
                                data_blocks = cycle["dataBlocks"]
                                print(f"      🎯 DATA BLOCKS ENCONTRADOS: {len(data_blocks)}")
                                
                                total_priority = 0
                                total_standard = 0
                                
                                for k, block in enumerate(data_blocks):
                                    print(f"\n         📦 DATA BLOCK {k+1}:")
                                    
                                    # Campos relevantes
                                    block_type = block.get("type", "N/A")
                                    amount = block.get("amount", 0)
                                    unit = block.get("unit", "N/A")
                                    rate = block.get("rate", 0)
                                    usage = block.get("usage", 0)
                                    
                                    print(f"            Tipo: {block_type}")
                                    print(f"            Quantidade: {amount} {unit}")
                                    print(f"            Taxa: ${rate}")
                                    print(f"            Uso: {usage}")
                                    
                                    # Converter para GB se necessário
                                    if "priority" in block_type.lower():
                                        if unit.lower() in ["mb", "megabyte"]:
                                            total_priority += usage / 1024
                                        elif unit.lower() in ["gb", "gigabyte"]:
                                            total_priority += usage
                                        elif unit.lower() in ["tb", "terabyte"]:
                                            total_priority += usage * 1024
                                        else:
                                            total_priority += usage
                                    
                                    if "standard" in block_type.lower():
                                        if unit.lower() in ["mb", "megabyte"]:
                                            total_standard += usage / 1024
                                        elif unit.lower() in ["gb", "gigabyte"]:
                                            total_standard += usage
                                        elif unit.lower() in ["tb", "terabyte"]:
                                            total_standard += usage * 1024
                                        else:
                                            total_standard += usage
                                
                                total_consumption = total_priority + total_standard
                                
                                print(f"\n      🎯 RESUMO DO CICLO:")
                                print(f"         Priority GB: {total_priority:.2f}")
                                print(f"         Standard GB: {total_standard:.2f}")
                                print(f"         TOTAL GB: {total_consumption:.2f}")
                                
                                # Verificar se é o ciclo atual (julho 2025)
                                if "2025-07" in cycle_start or "2025-07" in cycle_end:
                                    print(f"         🎉 CICLO ATUAL IDENTIFICADO!")
                                    print(f"         📊 VALOR CORRETO: {total_consumption:.2f} GB")
                                    print(f"         ❌ VALOR NO SISTEMA: 268,45 GB")
                                    print(f"         🔧 DIFERENÇA: {abs(268.45 - total_consumption):.2f} GB")
                            
                            else:
                                print("      ⚠️  Nenhum data block encontrado neste ciclo")
                    
                    else:
                        print(f"   ⏭️  Pulando service line: {sl_number}")
            
            else:
                print("❌ Estrutura de dados inesperada")
                print(f"Keys encontradas: {list(data.keys())}")
        
        else:
            print(f"❌ ERRO na requisição: {response.status_code}")
            print(f"Resposta: {response.text[:500]}...")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO ANÁLISE DE BILLING DA SERVICE LINE...")
    print()
    
    success = analyze_service_line_billing()
    
    print()
    print("=" * 80)
    if success:
        print("🎉 ANÁLISE CONCLUÍDA!")
        print("   Verifique o arquivo JSON gerado para dados detalhados")
        print("   Use os dados encontrados para corrigir o cálculo no sistema")
    else:
        print("❌ ANÁLISE FALHOU!")
        print("   Verifique os erros acima")
    
    print("=" * 80)
    
    sys.exit(0 if success else 1)

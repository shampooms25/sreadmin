#!/usr/bin/env python3
"""
Script para analisar campos da API de telemetria que indiquem status ativo/inativo
"""
import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_usage_report_data, get_telemetry_data

def print_header(text, char="="):
    """Imprime cabeçalho estilizado"""
    print(f"\n{char * 80}")
    print(f"{text:^80}")
    print(f"{char * 80}")

def print_section(title, char="-"):
    """Imprime seção estilizada"""
    print(f"\n{char * 60}")
    print(f"{title}")
    print(f"{char * 60}")

def analyze_status_fields():
    print_header("📊 ANÁLISE DE CAMPOS DE STATUS ATIVO/INATIVO", "🔍")
    
    print("🎯 **OBJETIVO: Identificar como determinar se um Service Line está ATIVO**")
    
    # Service lines para teste (algumas ativas, outras não)
    test_service_lines = ['75238', '854897', '43', '999999']  # Última é inexistente para teste
    account_id = "ACC-2744134-64041-5"
    
    current_date = datetime.now()
    start_date = f"03/{current_date.month:02d}/{current_date.year}"
    end_date = f"02/{current_date.month + 1:02d}/{current_date.year}" if current_date.month < 12 else f"02/01/{current_date.year + 1}"
    
    print_section("1️⃣ ANÁLISE DOS DADOS DE BILLING (Consumo)")
    
    # Testar API de billing para ver quais SLs existem
    billing_data = get_usage_report_data(account_id, start_date, end_date)
    
    active_service_lines = []
    if billing_data and billing_data.get('success'):
        print("📊 Service Lines encontradas na API de billing:")
        for usage_line in billing_data.get('usage_data', []):
            sl_number = usage_line.get('serviceLineNumber')
            priority_gb = usage_line.get('priorityGB', 0)
            standard_gb = usage_line.get('standardGB', 0) 
            total_gb = usage_line.get('totalGB', 0)
            
            if sl_number:
                active_service_lines.append(sl_number)
                status = "🟢 ATIVO" if total_gb > 0 else "🟡 ATIVO SEM CONSUMO"
                print(f"   • {sl_number}: {status}")
                print(f"     Consumo: {total_gb:.2f} GB (P:{priority_gb:.2f} S:{standard_gb:.2f})")
    
    print(f"\n✅ Total de Service Lines ativas na billing: {len(active_service_lines)}")
    
    print_section("2️⃣ ANÁLISE DOS DADOS DE TELEMETRIA")
    
    for sl in test_service_lines:
        print(f"\n🔍 Testando Service Line: {sl}")
        
        telemetry_data = get_telemetry_data([sl], start_date, end_date)
        
        # Analisar campos que indiquem status
        status_indicators = []
        
        if telemetry_data:
            print(f"   📡 Telemetria obtida - Fonte: {telemetry_data.get('api_source', 'N/A')}")
            
            # 1. Presença de dados
            has_data = telemetry_data.get('api_source') != 'simulated'
            status_indicators.append(f"Dados reais: {'✅' if has_data else '❌'}")
            
            # 2. Uptime percentage
            uptime = telemetry_data.get('uptime_percentage', 0)
            if uptime > 0:
                status_indicators.append(f"Uptime: {uptime}% {'✅' if uptime > 50 else '⚠️'}")
            
            # 3. Erro na resposta
            error = telemetry_data.get('error')
            if error:
                status_indicators.append(f"Erro: {error} ❌")
            else:
                status_indicators.append("Sem erros: ✅")
            
            # 4. Última atualização
            last_update = telemetry_data.get('last_update')
            if last_update:
                status_indicators.append(f"Última atualização: {last_update}")
            
            # 5. Presença na billing
            in_billing = sl in active_service_lines
            status_indicators.append(f"Na billing: {'✅' if in_billing else '❌'}")
            
            # 6. Metrics de ping
            ping_metrics = telemetry_data.get('ping_metrics')
            if ping_metrics:
                status_indicators.append("Métricas ping: ✅")
            
            print("   📋 Indicadores de status:")
            for indicator in status_indicators:
                print(f"      • {indicator}")
        else:
            print("   ❌ Nenhum dado de telemetria obtido")
        
        # Determinar status final
        in_billing = sl in active_service_lines
        has_telemetry = telemetry_data is not None
        has_real_data = telemetry_data and telemetry_data.get('api_source') != 'simulated'
        
        if in_billing and has_telemetry:
            final_status = "🟢 ATIVO E OPERACIONAL"
        elif in_billing and not has_telemetry:
            final_status = "🟡 ATIVO MAS SEM TELEMETRIA"
        elif not in_billing and has_telemetry:
            final_status = "🔵 TELEMETRIA SEM BILLING"
        else:
            final_status = "🔴 INATIVO OU INEXISTENTE"
        
        print(f"   🎯 Status final: {final_status}")
    
    print_section("3️⃣ CAMPOS RECOMENDADOS PARA STATUS")
    
    print("""
🎯 INDICADORES MAIS CONFIÁVEIS PARA DETERMINAR STATUS ATIVO:

1. 📊 PRESENÇA NA API DE BILLING:
   Campo: serviceLineNumber existe em usage_data
   Lógica: Se está faturando, está ativo
   Confiabilidade: ⭐⭐⭐⭐⭐
   
2. 📈 CONSUMO DE DADOS RECENTE:
   Campo: totalGB > 0 nos últimos dias
   Lógica: Se consome dados, está sendo usado
   Confiabilidade: ⭐⭐⭐⭐⭐
   
3. 📡 UPTIME DA TELEMETRIA:
   Campo: uptime_percentage > 0
   Lógica: Se tem uptime, está monitorado/ativo  
   Confiabilidade: ⭐⭐⭐ (dados simulados atualmente)
   
4. ⏰ ÚLTIMA ATUALIZAÇÃO:
   Campo: last_update recente (< 24h)
   Lógica: Se atualizou recentemente, está ativo
   Confiabilidade: ⭐⭐⭐⭐
   
5. ❌ AUSÊNCIA DE ERROS CRÍTICOS:
   Campo: error == null
   Lógica: Sem erros = funcionando
   Confiabilidade: ⭐⭐⭐
    """)
    
    print_section("4️⃣ IMPLEMENTAÇÃO RECOMENDADA")
    
    print("""
🚀 LÓGICA PROPOSTA PARA DETERMINAR STATUS:

def determine_service_line_status(sl_number, billing_data, telemetry_data):
    # 1. Verificar se existe na billing (mais confiável)
    in_billing = any(usage.get('serviceLineNumber') == sl_number 
                    for usage in billing_data.get('usage_data', []))
    
    # 2. Verificar consumo recente
    recent_usage = 0
    for usage in billing_data.get('usage_data', []):
        if usage.get('serviceLineNumber') == sl_number:
            recent_usage = usage.get('totalGB', 0)
            break
    
    # 3. Determinar status
    if in_billing and recent_usage > 0:
        return "🟢 ATIVO - Em uso"
    elif in_billing and recent_usage == 0:
        return "🟡 ATIVO - Sem consumo"
    elif telemetry_data and not telemetry_data.get('error'):
        return "🔵 MONITORADO - Status incerto"
    else:
        return "🔴 INATIVO - Não encontrado"

💡 CAMPOS DA API MAIS ÚTEIS:
   • billing_data.usage_data[].serviceLineNumber
   • billing_data.usage_data[].totalGB
   • telemetry_data.error
   • telemetry_data.last_update
   • telemetry_data.uptime_percentage
    """)
    
    print_section("5️⃣ STATUS VISUAL SUGERIDO")
    
    print("""
🎨 REPRESENTAÇÃO VISUAL NO TEMPLATE:

Situação                    | Ícone | Status Text
---------------------------|-------|-------------
Ativo com consumo          | 🟢    | ATIVO
Ativo sem consumo          | 🟡    | ATIVO (Idle)  
Monitorado sem billing     | 🔵    | MONITORADO
Erro de conectividade      | 🟠    | PROBLEMA
Inativo/Inexistente        | 🔴    | INATIVO
Manutenção programada      | ⚫    | MANUTENÇÃO

📊 TOOLTIP DETALHADO:
   • Última atividade: [timestamp]
   • Consumo atual: [GB]
   • Uptime: [%]
   • Fonte: [billing/telemetry/simulado]
    """)
    
    print_header("✅ CONCLUSÃO E RECOMENDAÇÕES", "=")
    
    print("""
🎯 CAMPO MAIS CONFIÁVEL PARA STATUS ATIVO:
   
   ✅ PRINCIPAL: Presença em billing_data.usage_data[]
   ✅ SECUNDÁRIO: totalGB > 0 (uso recente)
   ✅ TERCIÁRIO: telemetry_data.error == null
   
🚀 IMPLEMENTAÇÃO SUGERIDA:
   1. Verificar billing API primeiro (mais confiável)
   2. Usar telemetria como complemento
   3. Combinar ambos para status detalhado
   4. Implementar cache para performance
   
💡 PRÓXIMOS PASSOS:
   1. Implementar função determine_service_line_status()
   2. Atualizar template para mostrar status visual
   3. Adicionar tooltip com detalhes
   4. Testar com service lines reais vs inexistentes
    """)

def main():
    analyze_status_fields()

if __name__ == "__main__":
    main()

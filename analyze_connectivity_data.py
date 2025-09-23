#!/usr/bin/env python3
"""
Script para mostrar dados de CONECTIVIDADE usando as informações reais disponíveis
"""
import os
import sys
import django
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

def main():
    print_header("📊 ANÁLISE DOS DADOS PARA COLUNA CONECTIVIDADE", "🔗")
    
    # Service line de teste
    service_line = "75238"
    account_id = "ACC-2744134-64041-5"
    
    # Datas do ciclo atual
    current_date = datetime.now()
    start_date = f"03/{current_date.month:02d}/{current_date.year}"
    end_date = f"02/{current_date.month + 1:02d}/{current_date.year}" if current_date.month < 12 else f"02/01/{current_date.year + 1}"
    
    print(f"📡 Service Line: {service_line}")
    print(f"🆔 Account ID: {account_id}")
    print(f"📅 Período: {start_date} até {end_date}")
    
    # 1. DADOS DE BILLING (que já funcionam)
    print_section("💰 DADOS DE BILLING (Funcionando)")
    
    billing_data = get_usage_report_data(account_id, start_date, end_date)
    
    if billing_data and billing_data.get('success'):
        print("✅ Billing API funcionando corretamente!")
        
        # Encontrar dados da service line específica
        for usage_line in billing_data.get('usage_data', []):
            if usage_line.get('serviceLineNumber') == service_line:
                print(f"\n📋 Dados encontrados para SL {service_line}:")
                for key, value in usage_line.items():
                    print(f"   {key}: {value}")
                break
        else:
            print(f"❌ Service Line {service_line} não encontrada nos dados de billing")
    else:
        print("❌ Billing API falhou")
    
    # 2. DADOS DE TELEMETRIA (para conectividade)
    print_section("📡 DADOS DE TELEMETRIA (Para Conectividade)")
    
    telemetry_data = get_telemetry_data([service_line], start_date, end_date)
    
    print("📊 Estrutura dos dados de telemetria:")
    for key, value in telemetry_data.items():
        if key == 'ping_metrics' and isinstance(value, dict):
            print(f"   {key}:")
            for ping_key, ping_value in value.items():
                print(f"      {ping_key}: {ping_value}")
        else:
            print(f"   {key}: {value}")
    
    # 3. DEFININDO CAMPOS PARA CONECTIVIDADE
    print_section("🎯 CAMPOS DISPONÍVEIS PARA CONECTIVIDADE")
    
    connectivity_fields = []
    
    # Campos de telemetria disponíveis
    if 'uptime_percentage' in telemetry_data:
        connectivity_fields.append(f"Uptime: {telemetry_data['uptime_percentage']}%")
    
    if 'ping_metrics' in telemetry_data and telemetry_data['ping_metrics']:
        ping_data = telemetry_data['ping_metrics']
        if 'ping_latency_avg' in ping_data:
            connectivity_fields.append(f"Latência: {ping_data['ping_latency_avg']}ms")
        if 'packet_loss_percentage' in ping_data:
            connectivity_fields.append(f"Perda de Pacotes: {ping_data['packet_loss_percentage']}%")
        if 'jitter_ms' in ping_data:
            connectivity_fields.append(f"Jitter: {ping_data['jitter_ms']}ms")
    
    if 'availability_status' in telemetry_data:
        connectivity_fields.append(f"Status: {telemetry_data['availability_status']}")
    
    print("🔗 Campos que podemos usar na coluna Conectividade:")
    for i, field in enumerate(connectivity_fields, 1):
        print(f"   {i}. {field}")
    
    # 4. PROPOSTA DE FORMATO PARA EXIBIÇÃO
    print_section("💡 PROPOSTA DE FORMATO PARA CONECTIVIDADE")
    
    if telemetry_data.get('ping_metrics'):
        ping = telemetry_data['ping_metrics']
        uptime = telemetry_data.get('uptime_percentage', 0)
        
        # Formato compacto
        print("📱 Formato Compacto:")
        compact_format = f"↑{uptime}% • {ping.get('ping_latency_avg', 0)}ms"
        print(f"   {compact_format}")
        
        # Formato detalhado
        print("\n📋 Formato Detalhado:")
        detailed_format = f"Uptime: {uptime}% | Ping: {ping.get('ping_latency_avg', 0)}ms | Perda: {ping.get('packet_loss_percentage', 0)}%"
        print(f"   {detailed_format}")
        
        # Formato visual com ícones
        print("\n🎨 Formato Visual:")
        status_icon = "🟢" if uptime > 95 else "🟡" if uptime > 90 else "🔴"
        latency_icon = "🟢" if ping.get('ping_latency_avg', 0) < 50 else "🟡" if ping.get('ping_latency_avg', 0) < 100 else "🔴"
        visual_format = f"{status_icon} {uptime}% {latency_icon} {ping.get('ping_latency_avg', 0)}ms"
        print(f"   {visual_format}")
    
    print_header("🏁 ANÁLISE CONCLUÍDA", "=")

if __name__ == "__main__":
    main()

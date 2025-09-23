#!/usr/bin/env python3
"""
Atualizar view para incluir status de service lines
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sreadmin.settings")
django.setup()

# Ler o arquivo
with open('painel/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituição 1: Adicionar imports
old_import = """    determine_service_line_status,
    get_enhanced_service_line_status,
    DEFAULT_ACCOUNT"""

if "get_enhanced_service_line_status" not in content:
    import_section = """    get_telemetry_data,
    get_availability_report_data,
    get_service_line_location,
    DEFAULT_ACCOUNT"""
    
    new_import = """    get_telemetry_data,
    get_availability_report_data,
    get_service_line_location,
    determine_service_line_status,
    get_enhanced_service_line_status,
    DEFAULT_ACCOUNT"""
    
    content = content.replace(import_section, new_import)
    print("✅ Imports atualizados")

# Substituição 2: Adicionar lógica de status após generate_cycle_data
old_pattern = """    report_data, cycle_start, cycle_end = generate_cycle_data(start_date, end_date)
    
    # Preparar dados para exibição
    filtered_data = []"""

new_pattern = """    report_data, cycle_start, cycle_end = generate_cycle_data(start_date, end_date)
    
    # Obter status detalhado para as service lines selecionadas
    try:
        # Extrair apenas os números das service lines (sem SL- prefix)
        sl_numbers = []
        for sl in selected_service_lines:
            if sl.startswith('SL-'):
                # Extrair o número do meio (formato SL-XXXXXX-XXXXX-XX)
                parts = sl.split('-')
                if len(parts) >= 2:
                    sl_numbers.append(parts[1])
            else:
                sl_numbers.append(sl)
        
        status_data = get_enhanced_service_line_status(sl_numbers, include_telemetry=False)
        print(f"📊 Status obtido para {len(status_data)} service lines")
    except Exception as e:
        print(f"⚠️ Erro ao obter status: {e}")
        status_data = {}
    
    # Preparar dados para exibição
    filtered_data = []"""

# Encontrar todas as ocorrências
occurrences = content.count(old_pattern)
print(f"Encontradas {occurrences} ocorrências para atualizar")

# Substituir apenas a primeira ocorrência (função starlink_availability_report)
if occurrences > 0:
    content = content.replace(old_pattern, new_pattern, 1)
    print("✅ Lógica de status adicionada na primeira função")

# Substituição 3: Adicionar status_info no filtered_data.append
old_append = """        filtered_data.append({
            'service_line': sl,
            'location': data.get('location', 'N/A'),
            'uptime_percentage': uptime,
            'downtime_hours': downtime,
            'obstruction_hours': obstruction,
            'availability_status': data.get('availability_status', 'N/A'),
            'priority_gb': data.get('priority_gb', 0),
            'standard_gb': data.get('standard_gb', 0),
            'total_gb': total_gb,
            'usage_percentage': usage_percentage,
            'usage_threshold': data.get('usage_threshold', 'normal'),
            'last_update': data.get('last_update', 'N/A')
        })"""

new_append = """        # Obter status para esta service line
        status_info = None
        if sl.startswith('SL-'):
            parts = sl.split('-')
            if len(parts) >= 2:
                sl_number = parts[1]
                status_info = status_data.get(sl_number)
        
        filtered_data.append({
            'service_line': sl,
            'location': data.get('location', 'N/A'),
            'uptime_percentage': uptime,
            'downtime_hours': downtime,
            'obstruction_hours': obstruction,
            'availability_status': data.get('availability_status', 'N/A'),
            'priority_gb': data.get('priority_gb', 0),
            'standard_gb': data.get('standard_gb', 0),
            'total_gb': total_gb,
            'usage_percentage': usage_percentage,
            'usage_threshold': data.get('usage_threshold', 'normal'),
            'last_update': data.get('last_update', 'N/A'),
            'status_info': status_info  # Adicionar informação de status
        })"""

# Encontrar e substituir a primeira ocorrência
append_occurrences = content.count(old_append)
print(f"Encontradas {append_occurrences} ocorrências do filtered_data.append para atualizar")

if append_occurrences > 0:
    content = content.replace(old_append, new_append, 1)
    print("✅ Status_info adicionado ao filtered_data na primeira função")

# Salvar o arquivo
with open('painel/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("🎉 Arquivo views.py atualizado com sucesso!")
print("\n🔧 Próximos passos:")
print("1. Testar o relatório de disponibilidade")
print("2. Verificar se a nova coluna de status aparece corretamente")
print("3. Confirmar que os ícones e badges estão funcionando")

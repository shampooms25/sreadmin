#!/usr/bin/env python3
"""
Teste da funcionalidade de determinação de status de service lines
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sreadmin.settings")
django.setup()

from painel.starlink_api import get_enhanced_service_line_status, determine_service_line_status

def main():
    print("🧪 TESTANDO DETERMINAÇÃO DE STATUS DE SERVICE LINES")
    print("=" * 60)
    
    # Lista de service lines para teste (algumas existentes, outras não)
    test_service_lines = [
        "854897",    # Deve existir na billing
        "5242096",   # Deve existir na billing
        "999999",    # Não deve existir
        "75238",     # Pode ou não existir
        "43",        # Pode ou não existir
        "395008",    # Deve existir na billing
        "123456"     # Não deve existir
    ]
    
    print(f"🔍 Testando {len(test_service_lines)} service lines...")
    print()
    
    # Obter status detalhado
    try:
        status_results = get_enhanced_service_line_status(test_service_lines, include_telemetry=True)
        
        print("\n📋 RESULTADOS DO TESTE:")
        print("-" * 60)
        
        # Agrupar por status
        status_groups = {
            'active': [],
            'active_idle': [],
            'monitored': [],
            'problem': [],
            'inactive': []
        }
        
        for sl_number, status_info in status_results.items():
            status_groups[status_info['status']].append((sl_number, status_info))
        
        # Exibir resultados agrupados
        status_labels = {
            'active': '🟢 ATIVO',
            'active_idle': '🟡 ATIVO (Idle)',
            'monitored': '🔵 MONITORADO',
            'problem': '🟠 PROBLEMA',
            'inactive': '🔴 INATIVO'
        }
        
        for status_key, label in status_labels.items():
            if status_groups[status_key]:
                print(f"\n{label}:")
                for sl_number, status_info in status_groups[status_key]:
                    confidence_icon = {
                        'high': '⭐⭐⭐',
                        'medium': '⭐⭐',
                        'low': '⭐'
                    }.get(status_info['confidence'], '❓')
                    
                    print(f"   • SL-{sl_number}: {status_info['details']} {confidence_icon}")
        
        print("\n📊 RESUMO:")
        print(f"   Total testado: {len(test_service_lines)}")
        for status_key, label in status_labels.items():
            count = len(status_groups[status_key])
            if count > 0:
                print(f"   {label}: {count}")
        
        print("\n💡 LEGENDA DE CONFIABILIDADE:")
        print("   ⭐⭐⭐ = Alta confiabilidade (baseado em billing)")
        print("   ⭐⭐   = Média confiabilidade (telemetria + billing)")
        print("   ⭐     = Baixa confiabilidade (só telemetria simulada)")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

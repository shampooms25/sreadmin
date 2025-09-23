#!/usr/bin/env python3
"""
Teste final da funcionalidade de status no relatório de disponibilidade
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sreadmin.settings")
django.setup()

from painel.starlink_api import get_enhanced_service_line_status

def main():
    print("🔬 TESTE FINAL - FUNCIONALIDADE DE STATUS")
    print("=" * 50)
    
    # Service lines de exemplo para teste
    test_service_lines = ["854897", "5242096", "395008", "999999", "123456"]
    
    print(f"🧪 Testando status para {len(test_service_lines)} service lines...")
    print()
    
    try:
        # Chamar a função que será usada na view
        status_results = get_enhanced_service_line_status(test_service_lines, include_telemetry=False)
        
        print("📊 RESULTADOS:")
        print("-" * 30)
        
        for sl_number, status_info in status_results.items():
            icon = status_info.get('icon', '❓')
            label = status_info.get('label', 'N/A')
            details = status_info.get('details', 'Sem detalhes')
            confidence = status_info.get('confidence', 'unknown')
            
            confidence_stars = {
                'high': '⭐⭐⭐',
                'medium': '⭐⭐',
                'low': '⭐'
            }.get(confidence, '❓')
            
            print(f"   {icon} SL-{sl_number}: {label}")
            print(f"      └─ {details} {confidence_stars}")
            print()
        
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("\n💡 A funcionalidade está pronta para ser exibida no template HTML")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

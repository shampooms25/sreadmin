#!/usr/bin/env python3
"""
Teste para verificar todos os campos disponíveis nas service lines
"""

import os
import sys
import django
import json

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_billing_summary

def test_service_line_fields():
    """Testa os campos disponíveis nas service lines"""
    print("=== TESTE DOS CAMPOS DAS SERVICE LINES ===")
    
    # Testa uma conta específica
    account_id = "ACC-2744134-64041-5"
    
    print(f"Testando campos para a conta: {account_id}")
    
    try:
        # Chama a função que busca billing summary
        result = get_billing_summary(account_id)
        
        if result and "service_lines" in result:
            service_lines = result["service_lines"]
            
            print(f"✅ Encontradas {len(service_lines)} service lines")
            
            # Analisa a primeira service line para ver todos os campos
            if service_lines:
                first_sl = service_lines[0]
                print("\n📋 CAMPOS DISPONÍVEIS NA PRIMEIRA SERVICE LINE:")
                print("=" * 60)
                print(json.dumps(first_sl, indent=2, ensure_ascii=False))
                print("=" * 60)
                
                # Procurar por campos relacionados a recarga automática
                print("\n🔍 PROCURANDO CAMPOS RELACIONADOS A RECARGA AUTOMÁTICA:")
                keywords_to_check = ['opt', 'auto', 'recurring', 'renewal', 'product', 'data']
                
                for key, value in first_sl.items():
                    key_lower = key.lower()
                    if any(keyword in key_lower for keyword in keywords_to_check):
                        print(f"🎯 {key}: {value}")
            
            # Verificar se há service lines com optInProductId
            lines_with_opt_in = []
            for sl in service_lines:
                if sl.get("optInProductId"):
                    lines_with_opt_in.append(sl)
            
            if lines_with_opt_in:
                print(f"\n✅ Encontradas {len(lines_with_opt_in)} service lines com optInProductId!")
                for sl in lines_with_opt_in:
                    print(f"   - {sl.get('serviceLineNumber')}: {sl.get('optInProductId')}")
            else:
                print("\n⚠️ Nenhuma service line com optInProductId encontrada")
                
        else:
            print("❌ Nenhuma service line encontrada")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service_line_fields()

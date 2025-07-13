#!/usr/bin/env python3
"""
Teste simples para verificar totais
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:\\Projetos\\Poppnet\\sreadmin')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import get_all_accounts_summary

print("🔍 TESTE DE TOTAIS")
print("=" * 40)

try:
    result = get_all_accounts_summary()
    if result.get("success"):
        total_summary = result.get("total_summary", {})
        print(f"Total Service Lines: {total_summary.get('total_service_lines', 0)}")
        print(f"Ativas: {total_summary.get('active_lines', 0)}")
        print(f"Offline: {total_summary.get('offline_lines', 0)}")
        
        # Mostrar por conta
        accounts = result.get("accounts", {})
        for acc_id, acc_data in accounts.items():
            total = acc_data.get("total_service_lines", 0)
            print(f"{acc_id}: {total}")
            
    else:
        print("Erro ao obter dados")
except Exception as e:
    print(f"Erro: {e}")

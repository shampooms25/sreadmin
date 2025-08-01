#!/usr/bin/env python
"""
Teste direto para desativar recarga automática
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from painel.starlink_api import disable_auto_recharge, check_auto_recharge_status_fast, get_valid_token

print("=== TESTE: Desativação de Recarga Automática ===")
print("🎯 ENDPOINT: DELETE https://web-api.starlink.com/enterprise/v1/account/ACC-2744134-64041-5/service-lines/SL-394709-12748-31/opt-out")
print()

account_id = "ACC-2744134-64041-5"
service_line_number = "SL-394709-12748-31"

print(f"📋 Conta: {account_id}")
print(f"📋 Service Line: {service_line_number}")
print()

# Verificar token
print("🔑 Verificando autenticação...")
token = get_valid_token()
if not token:
    print("❌ Token não disponível")
    exit(1)

print(f"✅ Token obtido: {token[:20]}...")
print()

# Verificar status atual
print("🔍 Verificando status atual...")
current_status = check_auto_recharge_status_fast(account_id, service_line_number)
print(f"📊 Status atual: {current_status}")
print()

# Executar desativação
print("🚀 Executando desativação...")
result = disable_auto_recharge(account_id, service_line_number)
print()

print("=== RESULTADO ===")
if result.get("success"):
    print("✅ SUCESSO!")
    print(f"Message: {result.get('message', 'N/A')}")
else:
    print("❌ ERRO!")
    print(f"Error: {result.get('error', 'N/A')}")

print()
print("✅ TESTE FINALIZADO - VOCÊ PODE VERIFICAR O CONSOLE ACIMA")

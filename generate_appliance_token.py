#!/usr/bin/env python3
"""
Script para gerar tokens de autenticação para Appliances POPPFIRE

Usage:
    python generate_appliance_token.py <appliance_name>

Example:
    python generate_appliance_token.py appliance-001
"""

import os
import sys
import django
from pathlib import Path

# Configurar o ambiente Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

def generate_token_for_appliance(appliance_name):
    """
    Gera ou recupera token para um appliance
    """
    from django.contrib.auth.models import User
    
    try:
        # Tentar usar Django REST Framework se disponível
        from rest_framework.authtoken.models import Token
        
        # Criar ou recuperar usuário para o appliance
        user, created = User.objects.get_or_create(
            username=f"appliance-{appliance_name}",
            defaults={
                'email': f'{appliance_name}@poppfire.local',
                'first_name': appliance_name,
                'is_active': True,
                'is_staff': False,
                'is_superuser': False
            }
        )
        
        if created:
            user.set_unusable_password()  # Appliances usam apenas token
            user.save()
            print(f"✅ Usuário criado para appliance: {user.username}")
        else:
            print(f"ℹ️  Usuário já existe: {user.username}")
        
        # Criar ou recuperar token
        token, token_created = Token.objects.get_or_create(user=user)
        
        if token_created:
            print(f"✅ Novo token gerado!")
        else:
            print(f"ℹ️  Token existente recuperado")
        
        return token.key, user.username
        
    except ImportError:
        # Fallback: gerar token simples sem DRF
        import hashlib
        import secrets
        
        print("⚠️  Django REST Framework não encontrado")
        print("⚠️  Gerando token simples (recomenda-se usar DRF em produção)")
        
        # Gerar token deterministico baseado no nome
        token = hashlib.sha256(f"poppfire-{appliance_name}-api-token".encode()).hexdigest()[:32]
        username = f"appliance-{appliance_name}"
        
        return token, username

def main():
    if len(sys.argv) != 2:
        print("❌ Uso: python generate_appliance_token.py <nome_do_appliance>")
        print("📋 Exemplo: python generate_appliance_token.py appliance-001")
        sys.exit(1)
    
    appliance_name = sys.argv[1]
    
    print("🔐 GERADOR DE TOKEN PARA APPLIANCE POPPFIRE")
    print("=" * 50)
    print(f"📱 Appliance: {appliance_name}")
    print()
    
    try:
        token, username = generate_token_for_appliance(appliance_name)
        
        print("✅ TOKEN GERADO COM SUCESSO!")
        print("=" * 50)
        print(f"🔑 Token: {token}")
        print(f"👤 Usuário: {username}")
        print()
        print("📋 INFORMAÇÕES PARA CONFIGURAÇÃO:")
        print("-" * 30)
        print(f"• Server URL: http://172.18.25.253:8000")
        print(f"• API Base URL: http://172.18.25.253:8000/api/")
        print(f"• Authorization Header: Bearer {token}")
        print()
        print("🧪 TESTAR NO POSTMAN:")
        print("-" * 30)
        print("GET http://172.18.25.253:8000/api/appliances/info/")
        print(f"Headers:")
        print(f"  Authorization: Bearer {token}")
        print(f"  Content-Type: application/json")
        print()
        print("📖 ENDPOINTS DISPONÍVEIS:")
        print("-" * 30)
        print("• GET  /api/appliances/info/                    - Informações da API")
        print("• GET  /api/appliances/portal/status/           - Status do portal")
        print("• GET  /api/appliances/portal/download/         - Download do ZIP")
        print("• POST /api/appliances/portal/update-status/    - Report de status")
        print()
        print("🔒 SALVE ESSAS INFORMAÇÕES COM SEGURANÇA!")
        
    except Exception as e:
        print(f"❌ Erro ao gerar token: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

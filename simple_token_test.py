import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()

from captive_portal.models import ApplianceToken

# Verificar tokens
print("Tokens no banco:")
for token in ApplianceToken.objects.all():
    print(f"{token.token[:15]}... - {token.appliance_name} - Ativo: {token.is_active}")

# Criar/verificar token de teste
test_token = 'c8c786467d4a8d2825eaf549534d1ab0'
obj, created = ApplianceToken.objects.get_or_create(
    token=test_token,
    defaults={
        'appliance_id': 'POSTMAN-TEST',
        'appliance_name': 'Appliance Teste Postman',
        'description': 'Token para testes via Postman',
        'is_active': True,
    }
)

if created:
    print(f"Token criado: {obj.appliance_name}")
else:
    print(f"Token existe: {obj.appliance_name} - Ativo: {obj.is_active}")
    if not obj.is_active:
        obj.is_active = True
        obj.save()
        print("Token reativado!")

print(f"\nUse este token no Postman: {test_token}")
print("Header: Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0")
print("URL: http://127.0.0.1:8000/api/appliances/info/")

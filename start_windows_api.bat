@echo off
echo 🪟 POPPFIRE API - Configuração Windows
echo ====================================

echo.
echo 🔧 Criando token para Postman...
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings'); django.setup(); from captive_portal.models import ApplianceToken; obj, created = ApplianceToken.objects.get_or_create(token='c8c786467d4a8d2825eaf549534d1ab0', defaults={'appliance_id': 'POSTMAN-TEST', 'appliance_name': 'Appliance Teste Postman', 'description': 'Token para testes via Postman', 'is_active': True}); print(f'Token: c8c786467d4a8d2825eaf549534d1ab0'); print(f'Nome: {obj.appliance_name}'); print(f'Ativo: {obj.is_active}'); print(f'Criado: {created}')"

echo.
echo 🧪 Testando autenticação...
python quick_test_windows.py

echo.
echo 🚀 Iniciando servidor Django...
echo URL: http://127.0.0.1:8000/api/appliances/info/
echo Header: Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0
echo.
echo ⚠️ Abra outro terminal e teste no Postman
echo.

python manage.py runserver 127.0.0.1:8000

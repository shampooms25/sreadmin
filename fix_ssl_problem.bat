@echo off
echo 🔧 CORREÇÃO PROBLEMA SSL/HTTPS - POPPFIRE API
echo =============================================

echo.
echo ❌ ERRO IDENTIFICADO:
echo    Você está usando HTTPS mas o Django roda em HTTP
echo    https://localhost:8000 ^(ERRADO^)
echo    http://localhost:8000  ^(CORRETO^)

echo.
echo 🔧 Criando token de teste...
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings'); django.setup(); from captive_portal.models import ApplianceToken; obj, created = ApplianceToken.objects.get_or_create(token='c8c786467d4a8d2825eaf549534d1ab0', defaults={'appliance_id': 'POSTMAN-TEST', 'appliance_name': 'Appliance Teste Postman', 'description': 'Token para testes', 'is_active': True}); print(f'Token: {obj.token}'); print(f'Ativo: {obj.is_active}'); print(f'Criado: {created}')"

echo.
echo 🚀 URLs CORRETAS para teste:
echo =============================================
echo Admin:           http://localhost:8000/admin/
echo API Info:        http://localhost:8000/api/appliances/info/
echo Portal Status:   http://localhost:8000/api/appliances/portal/status/
echo Download Video:  http://localhost:8000/api/appliances/portal/download/?type=with_video
echo Download Normal: http://localhost:8000/api/appliances/portal/download/?type=without_video

echo.
echo 🔑 Header necessário:
echo Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0

echo.
echo 🖥️ Para iniciar servidor:
echo python manage.py runserver 127.0.0.1:8000

echo.
echo ⚠️ ATENÇÃO: Use HTTP (não HTTPS) no Postman!
echo.
pause

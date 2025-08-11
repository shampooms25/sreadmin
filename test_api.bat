@echo off
echo Testando API POPPFIRE
echo ======================

echo.
echo 1. Verificando se o servidor está rodando...
curl -s -o nul -w "Status Code: %%{http_code}\n" http://127.0.0.1:8000/admin/ || echo "❌ Servidor não está rodando!"

echo.
echo 2. Testando API sem token...
curl -X GET "http://127.0.0.1:8000/api/appliances/info/" -H "Content-Type: application/json" -w "\nStatus Code: %%{http_code}\n"

echo.
echo 3. Testando API com token...
curl -X GET "http://127.0.0.1:8000/api/appliances/info/" -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" -H "Content-Type: application/json" -w "\nStatus Code: %%{http_code}\n"

echo.
echo 4. Testando URL de status...
curl -X GET "http://127.0.0.1:8000/api/appliances/portal/status/" -H "Authorization: Bearer c8c786467d4a8d2825eaf549534d1ab0" -H "Content-Type: application/json" -w "\nStatus Code: %%{http_code}\n"

echo.
echo Teste concluído!
pause

@echo off
REM Script para ativar o ambiente virtual e iniciar o servidor Django
REM Use este script para desenvolvimento local

echo ======================================
echo POPPFIRE ADMIN - Ambiente de Desenvolvimento
echo ======================================

REM Verificar se está no diretório correto
if not exist "manage.py" (
    echo ERRO: Execute este script no diretório raiz do projeto Django
    pause
    exit /b 1
)

REM Verificar se o ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo ERRO: Ambiente virtual não encontrado!
    echo Certifique-se de que o diretório 'venv' existe
    pause
    exit /b 1
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Verificar se o arquivo settings.py existe
if not exist "sreadmin\settings.py" (
    echo AVISO: Arquivo settings.py não encontrado!
    echo Copiando de settings_local.py...
    copy "sreadmin\settings_local.py" "sreadmin\settings.py"
)

REM Executar migrações se necessário
echo.
echo Verificando migrações...
python manage.py makemigrations
python manage.py migrate

REM Iniciar servidor de desenvolvimento
echo.
echo Iniciando servidor Django...
echo.
echo Acesse: http://127.0.0.1:8000/
echo Admin: http://127.0.0.1:8000/admin/
echo.
echo Para parar o servidor: Ctrl+C
echo ======================================

REM Usar o caminho completo do Python para garantir que funcione
C:\Projetos\Poppnet\sreadmin\venv\Scripts\python.exe manage.py runserver

pause

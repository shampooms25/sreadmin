# Script PowerShell para ativar ambiente virtual e iniciar Django
# Uso: .\start_dev.ps1

Write-Host "======================================" -ForegroundColor Green
Write-Host "POPPFIRE ADMIN - Ambiente de Desenvolvimento" -ForegroundColor Green  
Write-Host "======================================" -ForegroundColor Green

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "ERRO: Execute este script no diretório raiz do projeto Django" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar se o ambiente virtual existe
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERRO: Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "Certifique-se de que o diretório 'venv' existe" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Verificar se o arquivo settings.py existe
if (-not (Test-Path "sreadmin\settings.py")) {
    Write-Host "AVISO: Arquivo settings.py não encontrado!" -ForegroundColor Yellow
    Write-Host "Copiando de settings_local.py..." -ForegroundColor Yellow
    Copy-Item "sreadmin\settings_local.py" "sreadmin\settings.py"
}

# Executar migrações se necessário
Write-Host ""
Write-Host "Verificando migrações..." -ForegroundColor Yellow
& "C:\Projetos\Poppnet\sreadmin\venv\Scripts\python.exe" "manage.py" "makemigrations"
& "C:\Projetos\Poppnet\sreadmin\venv\Scripts\python.exe" "manage.py" "migrate"

# Iniciar servidor de desenvolvimento
Write-Host ""
Write-Host "Iniciando servidor Django..." -ForegroundColor Green
Write-Host ""
Write-Host "Acesse: http://127.0.0.1:8000/" -ForegroundColor Cyan
Write-Host "Admin: http://127.0.0.1:8000/admin/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para parar o servidor: Ctrl+C" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Green

# Usar o caminho completo do Python para garantir que funcione
& "C:\Projetos\Poppnet\sreadmin\venv\Scripts\python.exe" "manage.py" "runserver"

Read-Host "Pressione Enter para sair"

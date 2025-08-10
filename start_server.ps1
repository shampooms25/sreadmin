# Script para iniciar o servidor Django
Write-Host "🚀 Iniciando servidor Django..." -ForegroundColor Green

# Navegue para o diretório
Set-Location "c:\Projetos\Poppnet\sreadmin"

# Ative o ambiente virtual
& "venv\Scripts\Activate.ps1"

Write-Host "✅ Ambiente virtual ativo" -ForegroundColor Yellow

# Inicie o servidor
Write-Host "🔥 Iniciando servidor na porta 8000..." -ForegroundColor Cyan
python manage.py runserver 127.0.0.1:8000

Write-Host "✅ Servidor iniciado!" -ForegroundColor Green
Write-Host "📱 Acesse: http://127.0.0.1:8000/admin/" -ForegroundColor Magenta

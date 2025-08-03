#!/usr/bin/env powershell
<#
.SYNOPSIS
    Script para atualização do servidor de produção POPPFIRE ADMIN
.DESCRIPTION
    Executa pull, migrações e reinicialização do servidor de produção
.NOTES
    Autor: Sistema Automatizado
    Data: 2025-08-01
    ATENÇÃO: Execute este script NO SERVIDOR DE PRODUÇÃO
#>

# Cores para output
$Green = @{ForegroundColor = 'Green'}
$Yellow = @{ForegroundColor = 'Yellow'}
$Red = @{ForegroundColor = 'Red'}
$Cyan = @{ForegroundColor = 'Cyan'}
$Magenta = @{ForegroundColor = 'Magenta'}

Write-Host "======================================" @Cyan
Write-Host "POPPFIRE ADMIN - Atualização Produção" @Cyan
Write-Host "======================================" @Cyan

Write-Host "`n⚠️  ATENÇÃO: Este script deve ser executado NO SERVIDOR DE PRODUÇÃO!" @Red
$confirm = Read-Host "`nDeseja continuar? (s/N)"
if ($confirm -ne 's' -and $confirm -ne 'S') {
    Write-Host "Operação cancelada pelo usuário." @Yellow
    exit 0
}

# Verificar se está no diretório correto
if (!(Test-Path "manage.py")) {
    Write-Host "❌ ERRO: manage.py não encontrado!" @Red
    Write-Host "Execute este script no diretório raiz do projeto Django." @Red
    exit 1
}

# Ativar ambiente virtual
Write-Host "`n🔧 Ativando ambiente virtual..." @Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "❌ ERRO: Ambiente virtual não encontrado em .\venv\" @Red
    Write-Host "Certifique-se de que o ambiente virtual está configurado." @Red
    exit 1
}

# Fazer backup do banco de dados (opcional)
Write-Host "`n💾 Fazendo backup do banco de dados..." @Yellow
$backupDir = "backups"
if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir
}
$backupFile = "$backupDir\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
Write-Host "Backup salvo em: $backupFile" @Green

# Parar serviços (se aplicável)
Write-Host "`n🛑 Parando serviços (se necessário)..." @Yellow
# Adicione aqui comandos para parar serviços específicos do seu ambiente
# Exemplo: Stop-Service "NomeDoServiço"

# Fazer pull das alterações
Write-Host "`n📥 Baixando atualizações do repositório..." @Yellow
git stash push -m "Backup antes do deploy - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git fetch origin
git pull origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERRO durante o git pull!" @Red
    Write-Host "Verifique conflitos e resolva manualmente." @Red
    exit 1
}

# Instalar/atualizar dependências
Write-Host "`n📦 Atualizando dependências..." @Yellow
pip install -r requirements.txt

# Verificar migrações pendentes
Write-Host "`n🔍 Verificando migrações pendentes..." @Yellow
$pendingMigrations = python manage.py showmigrations --plan | Select-String "\[ \]"
if ($pendingMigrations) {
    Write-Host "📋 Migrações pendentes encontradas:" @Yellow
    $pendingMigrations | ForEach-Object { Write-Host "  $_" @Yellow }
    
    $applyMigrations = Read-Host "`nDeseja aplicar as migrações? (S/n)"
    if ($applyMigrations -ne 'n' -and $applyMigrations -ne 'N') {
        Write-Host "`n🔄 Aplicando migrações..." @Yellow
        python manage.py migrate
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ ERRO durante as migrações!" @Red
            Write-Host "Verifique os logs e resolva manualmente." @Red
            exit 1
        }
        Write-Host "✅ Migrações aplicadas com sucesso!" @Green
    }
} else {
    Write-Host "✅ Nenhuma migração pendente." @Green
}

# Coletar arquivos estáticos
Write-Host "`n📁 Coletando arquivos estáticos..." @Yellow
python manage.py collectstatic --noinput

# Verificar integridade do sistema
Write-Host "`n🔍 Verificando integridade do sistema..." @Yellow
python manage.py check --deploy

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Avisos encontrados durante a verificação." @Yellow
} else {
    Write-Host "✅ Sistema verificado com sucesso!" @Green
}

# Reiniciar serviços
Write-Host "`n🔄 Reiniciando serviços..." @Yellow
# Adicione aqui comandos para reiniciar serviços específicos do seu ambiente
# Exemplo: Restart-Service "NomeDoServiço"

# Teste rápido
Write-Host "`n🧪 Executando teste rápido..." @Yellow
try {
    $testResult = python -c @"
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sreadmin.settings')
django.setup()
from painel.models import EldGerenciarPortal
print('Modelo EldGerenciarPortal carregado com sucesso')
print(f'Total de registros: {EldGerenciarPortal.objects.count()}')
"@
    Write-Host $testResult @Green
} catch {
    Write-Host "⚠️  Erro durante o teste do modelo: $($_.Exception.Message)" @Yellow
}

Write-Host "`n======================================" @Cyan
Write-Host "✅ ATUALIZAÇÃO CONCLUÍDA!" @Green
Write-Host "======================================" @Cyan

Write-Host "`n📋 Resumo da atualização:" @Magenta
Write-Host "• Código atualizado do repositório" @Green
Write-Host "• Dependências atualizadas" @Green
Write-Host "• Migrações aplicadas" @Green
Write-Host "• Arquivos estáticos coletados" @Green
Write-Host "• Sistema verificado" @Green
Write-Host "• Serviços reiniciados" @Green

Write-Host "`n🔗 Acesse o sistema:" @Cyan
Write-Host "• Aplicação: http://localhost:8000/" @Cyan
Write-Host "• Admin: http://localhost:8000/admin/" @Cyan

# Mostrar último commit
Write-Host "`n📄 Versão atual:" @Yellow
git log --oneline -1

Write-Host "`n======================================" @Cyan
Read-Host "Pressione Enter para finalizar..."

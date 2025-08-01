#!/usr/bin/env powershell
<#
.SYNOPSIS
    Script para deploy automático das alterações do POPPFIRE ADMIN
.DESCRIPTION
    Executa commit e push das alterações para o repositório principal
.NOTES
    Autor: Sistema Automatizado
    Data: 2025-08-01
#>

# Cores para output
$Green = @{ForegroundColor = 'Green'}
$Yellow = @{ForegroundColor = 'Yellow'}
$Red = @{ForegroundColor = 'Red'}
$Cyan = @{ForegroundColor = 'Cyan'}

Write-Host "======================================" @Cyan
Write-Host "POPPFIRE ADMIN - Deploy Automático" @Cyan
Write-Host "======================================" @Cyan

# Ativar ambiente virtual
Write-Host "`n🔧 Ativando ambiente virtual..." @Yellow
& .\venv\Scripts\Activate.ps1

# Verificar status do repositório
Write-Host "`n📋 Verificando status do repositório..." @Yellow
$status = git status --porcelain
if ($status) {
    Write-Host "📝 Alterações detectadas:" @Green
    git status --short
    
    # Adicionar todas as alterações
    Write-Host "`n➕ Adicionando alterações..." @Yellow
    git add .
    
    # Solicitar mensagem de commit
    $commitMessage = Read-Host "`n💬 Digite a mensagem do commit (ou pressione Enter para usar mensagem padrão)"
    if ([string]::IsNullOrWhiteSpace($commitMessage)) {
        $commitMessage = "Fix: Correção da tabela eld_gerenciar_portal e atualizações do sistema - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    }
    
    # Fazer commit
    Write-Host "`n✅ Fazendo commit..." @Yellow
    git commit -m "$commitMessage"
    
    # Fazer push
    Write-Host "`n🚀 Enviando para o repositório..." @Yellow
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Deploy realizado com sucesso!" @Green
        Write-Host "🔗 Repositório atualizado: https://github.com/shampooms25/sreadmin" @Green
    } else {
        Write-Host "`n❌ Erro durante o push!" @Red
        Write-Host "Verifique sua conexão e tente novamente." @Red
        exit 1
    }
} else {
    Write-Host "ℹ️  Nenhuma alteração detectada para commit." @Green
}

# Mostrar último commit
Write-Host "`n📄 Último commit:" @Yellow
git log --oneline -1

Write-Host "`n======================================" @Cyan
Write-Host "Deploy finalizado!" @Cyan
Write-Host "======================================" @Cyan

# Pausa para visualizar resultado
Read-Host "`nPressione Enter para continuar..."

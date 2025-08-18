<#
.SYNOPSIS
  Força atualização do repositório Git no Windows (PowerShell), com backup de alterações locais e limpeza de merges/rebases pendentes.

.DESCRIPTION
  - Cria um backup dos arquivos modificados e não rastreados
  - Aborta merges/rebases pendentes
  - Executa git fetch --all e git reset --hard origin/<branch>
  - Mostra status e últimos commits ao final

.PARAMETER Branch
  Nome da branch a ser usada (padrão: branch atual detectada).

.PARAMETER Remote
  Nome do remoto (padrão: origin).

.EXAMPLE
  PS> .\force_git_update.ps1

.EXAMPLE
  PS> .\force_git_update.ps1 -Branch main

.NOTES
  Execute no diretório raiz do repositório (onde existe a pasta .git).
#>

param(
  [string]$Branch = "",
  [string]$Remote = "origin"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "`n🔄 FORÇANDO ATUALIZAÇÃO GIT (Windows/PowerShell)" -ForegroundColor Cyan
Write-Host "=============================================="

if (-not (Test-Path ".git")) {
  Write-Error "❌ Este não é um repositório Git!"
  exit 1
}

$cwd = Get-Location
Write-Host "📂 Diretório: $cwd"

# Detectar branch atual, se não informada
if ([string]::IsNullOrWhiteSpace($Branch)) {
  try {
    $Branch = (git branch --show-current).Trim()
    if (-not $Branch) {
      $Branch = (git rev-parse --abbrev-ref HEAD).Trim()
    }
  } catch {
    $Branch = ""
  }
}

if (-not $Branch) {
  Write-Error "❌ Não foi possível detectar a branch atual. Especifique com -Branch main"
  exit 1
}

Write-Host "\n🔍 STATUS ANTES DA ATUALIZAÇÃO:" -ForegroundColor Yellow
Write-Host "=============================="
try { git status --short | Out-Host } catch {}

# Criar backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backup_local_$timestamp"
New-Item -ItemType Directory -Path $backupDir | Out-Null

# Arquivos modificados
$modified = @()
try { $modified = (git diff --name-only) } catch {}
if ($modified -and $modified.Count -gt 0) {
  Write-Host "\n📥 Backup de arquivos modificados..."
  foreach ($f in $modified) {
    if (Test-Path $f -PathType Leaf) {
      $dest = Join-Path $backupDir ([IO.Path]::GetFileName($f))
      Copy-Item -Path $f -Destination $dest -Force
      Write-Host "  ✅ $f"
    }
  }
}

# Arquivos não rastreados
$untracked = @()
try { $untracked = (git ls-files --others --exclude-standard) } catch {}
if ($untracked -and $untracked.Count -gt 0) {
  Write-Host "📥 Backup de arquivos não rastreados..."
  foreach ($f in $untracked) {
    if (Test-Path $f -PathType Leaf) {
      $dest = Join-Path $backupDir ([IO.Path]::GetFileName($f))
      Copy-Item -Path $f -Destination $dest -Force
      Write-Host "  ✅ $f"
    }
  }
}

# Limpar estados pendentes de merge/rebase se existirem
if (Test-Path ".git/MERGE_HEAD") {
  Write-Host "\n⚠️  Merge em andamento detectado. Abortando merge..."
  try { git merge --abort | Out-Null } catch {}
}
if (Test-Path ".git/rebase-apply" -or Test-Path ".git/rebase-merge") {
  Write-Host "⚠️  Rebase em andamento detectado. Abortando rebase..."
  try { git rebase --abort | Out-Null } catch {}
}

Write-Host "\n🔄 FORÇANDO ATUALIZAÇÃO..." -ForegroundColor Yellow
Write-Host "========================"

Write-Host "1. git fetch --all"
try { git fetch --all | Out-Host } catch {}

Write-Host "2. Branch atual: $Branch"
Write-Host "3. git reset --hard $Remote/$Branch"
try { git reset --hard "$Remote/$Branch" | Out-Host } catch {}

Write-Host "\n🔍 STATUS APÓS ATUALIZAÇÃO:" -ForegroundColor Yellow
Write-Host "=========================="
try { git status --short | Out-Host } catch {}

Write-Host "\n📊 ÚLTIMOS COMMITS:" -ForegroundColor Yellow
Write-Host "=================="
try { git --no-pager log --oneline -5 | Out-Host } catch {}

# Remover backup se vazio
$hasFiles = $false
try { $hasFiles = (Get-ChildItem -Path $backupDir -File -ErrorAction SilentlyContinue).Count -gt 0 } catch {}
if ($hasFiles) {
  Write-Host "\n📦 Backup salvo em: $backupDir"
  Write-Host "💡 Para restaurar: Copy-Item $backupDir\\nome_arquivo -Destination ."
} else {
  try { Remove-Item $backupDir -Force -ErrorAction SilentlyContinue } catch {}
}

Write-Host "\n✅ ATUALIZAÇÃO CONCLUÍDA!" -ForegroundColor Green

param(
  [string]$HostAddr = "127.0.0.1",
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot "venv\Scripts\python.exe"
$LogDir = Join-Path $RepoRoot "logs"
$LogFile = Join-Path $LogDir "django_runserver.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

"[{0}] Starting Django local server..." -f (Get-Date -Format s) | Out-File -FilePath $LogFile -Encoding utf8
"RepoRoot=$RepoRoot" | Out-File -FilePath $LogFile -Append -Encoding utf8
"Python=$Python" | Out-File -FilePath $LogFile -Append -Encoding utf8

if (-not (Test-Path $Python)) {
  "ERROR: Python venv not found at $Python" | Out-File -FilePath $LogFile -Append -Encoding utf8
  throw "Python venv not found. Create venv first."
}

Push-Location $RepoRoot
try {
  & $Python manage.py check *>> $LogFile
  if ($LASTEXITCODE -ne 0) { throw "manage.py check failed" }

  & $Python manage.py migrate *>> $LogFile
  if ($LASTEXITCODE -ne 0) { throw "manage.py migrate failed" }

  $Bind = "$HostAddr`:$Port"
  "[{0}] Running: manage.py runserver $Bind" -f (Get-Date -Format s) | Out-File -FilePath $LogFile -Append -Encoding utf8
  "Open: http://$HostAddr`:$Port/admin/" | Out-File -FilePath $LogFile -Append -Encoding utf8

  & $Python manage.py runserver $Bind *>> $LogFile
  exit $LASTEXITCODE
}
finally {
  Pop-Location
}

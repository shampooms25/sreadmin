@echo off
setlocal

REM Runner que NAO depende do terminal do VS Code.
REM Ele escreve logs em .\logs\django_runserver.log

set REPO_ROOT=%~dp0..
set PS1=%REPO_ROOT%\dev_tools\run_django_local.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -HostAddr 127.0.0.1 -Port 8000

echo.
echo ==============================
echo Log gerado em: %REPO_ROOT%\logs\django_runserver.log
echo ==============================
echo.
pause

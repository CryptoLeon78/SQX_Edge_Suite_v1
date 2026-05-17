@echo off
setlocal

set "ROOT=%~dp0"
if "%SQX_CLOUDFLARED_PATH%"=="" set "SQX_CLOUDFLARED_PATH=C:\Tools\cloudflared\cloudflared.exe"

start "" powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%ROOT%tools\remote_operator_status.ps1" -RepoRoot "%ROOT%" -CloudflaredPath "%SQX_CLOUDFLARED_PATH%" -StartOnOpen
exit /b 0

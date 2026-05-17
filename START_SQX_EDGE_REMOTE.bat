@echo off
setlocal

for %%I in ("%~dp0.") do set "ROOT=%%~fI"
if "%SQX_CLOUDFLARED_PATH%"=="" set "SQX_CLOUDFLARED_PATH=C:\Tools\cloudflared\cloudflared.exe"

start "SQX Edge Remote Monitor" /min powershell -NoProfile -Sta -ExecutionPolicy Bypass -File "%ROOT%\tools\remote_operator_status.ps1" -RepoRoot "%ROOT%" -CloudflaredPath "%SQX_CLOUDFLARED_PATH%" -StartOnOpen
exit /b 0

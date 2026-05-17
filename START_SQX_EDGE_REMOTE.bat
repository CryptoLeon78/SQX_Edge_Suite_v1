@echo off
setlocal

for %%I in ("%~dp0.") do set "ROOT=%%~fI"
if "%SQX_CLOUDFLARED_PATH%"=="" set "SQX_CLOUDFLARED_PATH=C:\Tools\cloudflared\cloudflared.exe"
set "SQX_REMOTE_ROOT=%ROOT%"
set "SQX_REMOTE_MODE=start"

start "" mshta.exe "%ROOT%\tools\remote_operator_monitor.hta" --start
exit /b 0

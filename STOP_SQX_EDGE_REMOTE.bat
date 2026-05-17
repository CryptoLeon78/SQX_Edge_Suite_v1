@echo off
setlocal

for %%I in ("%~dp0.") do set "ROOT=%%~fI"
set "SQX_REMOTE_ROOT=%ROOT%"
set "SQX_REMOTE_MODE=stop"

start "" mshta.exe "%ROOT%\tools\remote_operator_monitor.hta" --stop
exit /b 0

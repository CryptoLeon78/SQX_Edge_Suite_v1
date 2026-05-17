@echo off
setlocal

for %%I in ("%~dp0.") do set "ROOT=%%~fI"

start "SQX Edge Remote Monitor" /min powershell -NoProfile -Sta -ExecutionPolicy Bypass -File "%ROOT%\tools\remote_operator_status.ps1" -RepoRoot "%ROOT%" -StopOnOpen
exit /b 0

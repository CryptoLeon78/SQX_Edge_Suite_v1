@echo off
setlocal

set "ROOT=%~dp0"

start "" powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%ROOT%tools\remote_operator_status.ps1" -RepoRoot "%ROOT%" -StopOnOpen
exit /b 0

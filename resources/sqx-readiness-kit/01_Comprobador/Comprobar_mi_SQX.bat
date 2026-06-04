@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%tools\SQX_Readiness_Check.ps1" -Action check
echo.
pause

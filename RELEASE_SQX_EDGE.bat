@echo off
setlocal

cd /d "%~dp0"

echo.
echo ================================================================
echo   SQX Edge Suite - Release Checklist
echo ================================================================
echo.
echo Este asistente ejecuta tests, genera el ZIP portable y valida
echo que el paquete arrancaria con su Python embebido.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0backend\sqx-edge-tool\tools\release_checklist.ps1" -RequireCleanGit

echo.
if errorlevel 1 (
  echo Release checklist fallo. Revisa los mensajes anteriores.
) else (
  echo Release checklist completado correctamente.
)
echo.
pause

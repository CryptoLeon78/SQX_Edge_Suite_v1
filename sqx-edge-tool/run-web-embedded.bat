@echo off
REM SQX Edge Tool - Web API launcher using embedded Python runtime.
REM First-time setup:
REM   powershell -NoProfile -ExecutionPolicy Bypass -File tools\bootstrap_embedded_python.ps1

setlocal
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0runtime\python\python.exe"

if not exist "%PYTHON_EXE%" (
  echo.
  echo Embedded Python runtime not found:
  echo   %PYTHON_EXE%
  echo.
  echo Run first:
  echo   powershell -NoProfile -ExecutionPolicy Bypass -File tools\bootstrap_embedded_python.ps1
  echo.
  pause
  exit /b 1
)

echo.
echo ================================================================
echo   SQX Edge Tool - Web API (embedded Python)
echo ================================================================
echo.
echo   Starting local API. Open SQX_Dashboard_v6.html and go to
echo   Project Generator.
echo.
echo   Press Ctrl+C to stop the server.
echo ================================================================
echo.
"%PYTHON_EXE%" -m api.server %*
pause

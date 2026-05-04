@echo off
REM SQX Edge Tool - CLI launcher using embedded Python runtime.
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
  exit /b 1
)

"%PYTHON_EXE%" -m cli.sqx_edge %*
exit /b %ERRORLEVEL%

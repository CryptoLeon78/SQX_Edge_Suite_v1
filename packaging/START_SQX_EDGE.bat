@echo off
setlocal

set "ROOT=%~dp0..\"
for %%I in ("%ROOT%") do set "ROOT=%%~fI\"
set "TOOL=%ROOT%backend\sqx-edge-tool"
set "PYTHON_EXE=%TOOL%\runtime\python\python.exe"
set "DASHBOARD=%ROOT%app\SQX_Dashboard_v6.html"

if not exist "%PYTHON_EXE%" (
  echo.
  echo SQX Edge no esta preparado todavia.
  echo.
  echo Falta el runtime portable:
  echo   %PYTHON_EXE%
  echo.
  echo Ejecuta una vez:
  echo   powershell -NoProfile -ExecutionPolicy Bypass -File "%TOOL%\tools\bootstrap_embedded_python.ps1"
  echo.
  pause
  exit /b 1
)

if not exist "%DASHBOARD%" (
  echo.
  echo No se encontro el dashboard:
  echo   %DASHBOARD%
  echo.
  pause
  exit /b 1
)

echo.
echo ================================================================
echo   SQX Edge Suite
echo ================================================================
echo.
echo   1. Arrancando API local con Python portable...
echo   2. Esperando conexion...
echo   3. Abriendo dashboard...
echo.

start "SQX Edge API" /min cmd /k ""%TOOL%\run-web-embedded.bat""

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok=$false; for($i=0; $i -lt 45; $i++){ try { $r=Invoke-RestMethod -Uri 'http://127.0.0.1:5050/api/health' -TimeoutSec 1; if($r.ok){ $ok=$true; break } } catch {}; Start-Sleep -Seconds 1 }; if(-not $ok){ exit 1 }"
if errorlevel 1 (
  echo.
  echo No se pudo conectar con la API local en http://127.0.0.1:5050.
  echo Revisa la ventana "SQX Edge API" para ver el detalle.
  echo.
  pause
  exit /b 1
)

start "" "%DASHBOARD%"
echo Dashboard abierto. Puedes cerrar esta ventana.
timeout /t 3 >nul
exit /b 0

@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
title SQX Edge - Instalar snippets y View CORR1

echo.
echo ============================================================
echo  SQX Edge - Instalacion guiada para StrategyQuant X
echo ============================================================
echo.
echo Este asistente instalara SOLO:
echo   - snippets SQX Edge autorizados
echo   - View CORR1: SQX EDGE CORRELATION REVIEW
echo.
echo IMPORTANTE:
echo   1. Cierra StrategyQuant X antes de continuar.
echo   2. Se creara backup automatico antes de sobrescribir nada.
echo   3. No se toca data.db, proyectos, licencias ni activaciones.
echo.
choice /C SN /N /M "Quieres continuar? [S/N]: "
if errorlevel 2 (
  echo.
  echo Cancelado por el usuario.
  echo.
  pause
  exit /b 0
)

echo.
echo Selecciona ahora la carpeta raiz de tu SQX.
echo Ejemplo: C:\StrategyQuantX o la carpeta portable descomprimida.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%tools\SQX_Readiness_Check.ps1" -Action install
set "EXITCODE=%ERRORLEVEL%"
echo.
if not "%EXITCODE%"=="0" (
  echo La instalacion no se completo. Revisa el mensaje anterior.
  echo Si SQX estaba abierto, cierralo y vuelve a ejecutar este archivo.
) else (
  echo Instalacion finalizada. Puedes ejecutar Comprobar_mi_SQX.bat para validar.
)
echo.
pause
exit /b %EXITCODE%

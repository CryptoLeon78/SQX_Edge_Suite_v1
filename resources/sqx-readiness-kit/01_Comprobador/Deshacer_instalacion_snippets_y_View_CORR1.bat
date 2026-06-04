@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
title SQX Edge - Deshacer instalacion snippets y View CORR1

echo.
echo ============================================================
echo  SQX Edge - Rollback guiado para StrategyQuant X
echo ============================================================
echo.
echo Este asistente restaurara el ultimo backup creado por
echo Instalar_snippets_y_View_CORR1.bat.
echo.
echo IMPORTANTE:
echo   1. Cierra StrategyQuant X antes de continuar.
echo   2. Solo se restauran snippets y View CORR1 gestionados por el checker.
echo   3. No se toca data.db, proyectos, licencias ni activaciones.
echo.
choice /C SN /N /M "Quieres deshacer la ultima instalacion? [S/N]: "
if errorlevel 2 (
  echo.
  echo Cancelado por el usuario.
  echo.
  pause
  exit /b 0
)

echo.
echo Selecciona ahora la misma carpeta raiz de SQX donde instalaste.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%tools\SQX_Readiness_Check.ps1" -Action rollback
set "EXITCODE=%ERRORLEVEL%"
echo.
if not "%EXITCODE%"=="0" (
  echo El rollback no se completo. Revisa el mensaje anterior.
) else (
  echo Rollback finalizado. Puedes ejecutar Comprobar_mi_SQX.bat para validar.
)
echo.
pause
exit /b %EXITCODE%

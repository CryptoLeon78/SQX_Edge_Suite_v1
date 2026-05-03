@echo off
REM SQX Edge Tool — Web server launcher
REM Arranca el API REST en http://localhost:5050
REM El dashboard SQX Edge se conecta automáticamente.

cd /d "%~dp0"
echo.
echo ================================================================
echo   SQX Edge Tool — Web API
echo ================================================================
echo.
echo   Iniciando servidor en http://localhost:5050
echo   Abre el dashboard SQX_Dashboard_v6.html y ve al tab
echo   "Project Generator" para usarlo.
echo.
echo   Pulsa Ctrl+C para detener el servidor.
echo ================================================================
echo.
python -m api.server %*
pause

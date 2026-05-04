@echo off
setlocal

echo.
echo Deteniendo API local SQX Edge en puerto 5050...

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":5050" ^| findstr "LISTENING"') do (
  echo Cerrando proceso %%P
  taskkill /PID %%P /F >nul 2>nul
)

echo Listo.
timeout /t 2 >nul
exit /b 0

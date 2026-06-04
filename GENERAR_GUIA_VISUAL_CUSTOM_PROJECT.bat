@echo off
setlocal

cd /d "%~dp0"

echo.
echo ================================================================
echo   SQX Edge Suite - Guia visual Custom Project PDF
echo ================================================================
echo.
echo Generando PDF en modo no estricto.
echo Las capturas reales pendientes se mostraran como placeholders.
echo.

python "%~dp0backend\sqx-edge-tool\tools\render_custom_project_visual_guide.py"

echo.
if errorlevel 1 (
  echo El generador PDF fallo. Revisa los mensajes anteriores.
) else (
  echo PDF generado en output\pdf\sqx_custom_project_visual_check_guide.pdf
  start "" "%~dp0output\pdf\sqx_custom_project_visual_check_guide.pdf"
)
echo.
pause

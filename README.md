# SQX Edge Suite v1

Dashboard y herramienta local para organizar el pipeline SQX Edge, generar Custom Projects `.cfx` para StrategyQuant X y limpiar estrategias `.sqx` post-mining.

## Entrega Final

Paquete recomendado para usuario final:

```text
dist/SQX_Edge_Tool_Portable_*.zip
```

Uso para usuario basico:

1. Descomprime el ZIP en una carpeta normal, por ejemplo `C:\SQX_Edge`.
2. Haz doble click en `START_SQX_EDGE.bat`.
3. Espera unos segundos: se arranca la API local y se abre el dashboard.
4. Usa la app desde el navegador que se abre.
5. Para cerrar la API local, haz doble click en `STOP_SQX_EDGE.bat`.

No hace falta instalar Python. El ZIP incluye un runtime portable dentro de `backend\sqx-edge-tool\runtime\python`.

Problemas frecuentes:

- Si Windows muestra SmartScreen, pulsa `Mas informacion` y despues `Ejecutar de todas formas`.
- Si no abre el dashboard, ejecuta `STOP_SQX_EDGE.bat` y vuelve a abrir `START_SQX_EDGE.bat`.
- Si la API no conecta, revisa que el puerto `5050` no este ocupado por otra aplicacion.
- No muevas archivos internos del ZIP descomprimido; abre siempre desde `START_SQX_EDGE.bat`.
- Si StrategyQuant X esta en una ruta distinta, configuralo desde el tab `Project Generator`.

## Inicio Rapido

Para usuario basico, doble click en:

```bat
START_SQX_EDGE.bat
```

Ese launcher arranca la API local con Python embebido, espera a `http://127.0.0.1:5050/api/health` y abre `app\SQX_Dashboard_v6.html`.

Para cerrar la API local:

```bat
STOP_SQX_EDGE.bat
```

## Estructura

```text
.
├── app/                         Dashboard HTML, CSS y JS
│   ├── SQX_Dashboard_v6.html
│   ├── css/
│   └── js/
├── backend/sqx-edge-tool/        API Flask, CLI, config, templates y tests
├── analysis/                     Scripts analiticos y outputs regenerables
├── data/                         Datasets base versionados
├── docs/                         Documentacion y conceptos visuales
├── packaging/                    Launchers internos y empaquetado
├── START_SQX_EDGE.bat            Acceso directo de un click
└── STOP_SQX_EDGE.bat
```

## Manifiestos Dinamicos

Los datos principales viven en JSON dentro de `backend/sqx-edge-tool/config/`:

- `plan.json`
- `assets.json`
- `strategies.json`
- `ui_manifest.json`
- `generator_profiles.json`
- `instruments.json`

Para regenerar el manifiesto frontend:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\build_frontend_manifest.py
```

El resultado se escribe en `app\js\manifest-data.js`.

## Backend

La configuracion local vive en:

```text
backend/sqx-edge-tool/config.json
```

Ese archivo esta ignorado por Git para no subir rutas personales. Si falta el Python embebido, preparalo una vez con:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\bootstrap_embedded_python.ps1
```

## Tests

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe -m pytest backend\sqx-edge-tool
```

Los tests E2E de interfaz son opcionales. Si quieres activarlos en desarrollo:

```powershell
npm install --no-save --package-lock=false playwright
$env:SQX_E2E_SCREENSHOTS='1'
backend\sqx-edge-tool\venv\Scripts\python.exe -m pytest backend\sqx-edge-tool
```

Si Playwright no esta instalado, esos tests se saltan automaticamente.

## Empaquetado

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\package_portable.ps1 -RequireEmbeddedPython
```

El ZIP portable se crea en `dist/` e incluye el Python embebido para que el usuario final pueda abrir `START_SQX_EDGE.bat` sin instalar nada.

## Checklist de entrega

Para preparar una entrega completa con pruebas, ZIP portable y validacion del ZIP extraido:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\release_checklist.ps1
```

El checklist ejecuta contratos JS, suite Python, `git diff --check`, empaquetado portable, extraccion temporal, import de API con Python embebido y health check local. Al terminar muestra el ZIP listo en `dist/`.

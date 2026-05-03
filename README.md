# SQX Edge Suite v1

Dashboard y herramienta local para organizar el pipeline SQX Edge, generar Custom Projects `.cfx` para StrategyQuant X y limpiar estrategias `.sqx` post-mining.

El proyecto esta pensado para dos perfiles:

- Usuario basico: doble click en `START_SQX_EDGE.bat`.
- Usuario tecnico: CLI/API Python en `sqx-edge-tool/`.

## Inicio Rapido

### Opcion portable recomendada

El paquete portable incluye Python embebido y no requiere instalar Python en Windows.

1. Descarga o clona el repo.
2. Si ya viene preparado con `sqx-edge-tool/runtime/python`, ejecuta:

```bat
START_SQX_EDGE.bat
```

Ese launcher:

1. Arranca la API local con Python embebido.
2. Espera a que `http://127.0.0.1:5050/api/health` responda.
3. Abre `SQX_Dashboard_v6.html` automaticamente.

Para cerrar la API local:

```bat
STOP_SQX_EDGE.bat
```

### Preparar Python embebido

Si el repo no trae `sqx-edge-tool/runtime/python`, preparalo una vez con:

```powershell
cd sqx-edge-tool
powershell -NoProfile -ExecutionPolicy Bypass -File tools\bootstrap_embedded_python.ps1
```

Despues puedes usar:

```bat
run-web-embedded.bat
run-embedded.bat list
```

## Dashboard

Abre `SQX_Dashboard_v6.html` para acceder a:

- Por Activo
- Por Categoria
- Filtros Fase 2
- SQX Priority
- Pipeline State
- Project Generator
- Estrategias
- Workflow

El dashboard funciona como HTML estatico. Los datos y manifiestos estan separados en `js/` y `sqx-edge-tool/config/`.

## Project Generator

El tab Project Generator usa la API local Flask para:

- Leer config SQX.
- Autodetectar instalacion StrategyQuant X.
- Sugerir aliases de instrumentos desde `data.db`.
- Generar `.cfx` Capa 1 / Capa 2.
- Listar outputs generados.
- Limpiar `.sqx` con backup automatico.

La configuracion local vive en:

```text
sqx-edge-tool/config.json
```

Ese archivo esta ignorado por Git para no subir rutas personales.

## Estructura

```text
.
├── START_SQX_EDGE.bat
├── STOP_SQX_EDGE.bat
├── SQX_Dashboard_v6.html
├── README_SETUP.md
├── css/
├── js/
└── sqx-edge-tool/
    ├── api/
    ├── cli/
    ├── config/
    ├── core/
    ├── templates/
    ├── tools/
    ├── run.bat
    ├── run-web.bat
    ├── run-embedded.bat
    └── run-web-embedded.bat
```

## Manifiestos Dinamicos

La app evita hardcodes principales moviendo datos a JSON:

- `sqx-edge-tool/config/plan.json`
- `sqx-edge-tool/config/assets.json`
- `sqx-edge-tool/config/strategies.json`
- `sqx-edge-tool/config/ui_manifest.json`
- `sqx-edge-tool/config/generator_profiles.json`
- `sqx-edge-tool/config/instruments.json`

Para regenerar el manifiesto frontend:

```powershell
python sqx-edge-tool\tools\build_frontend_manifest.py
```

## Empaquetado Portable

Crear ZIP portable:

```powershell
cd sqx-edge-tool
powershell -NoProfile -ExecutionPolicy Bypass -File tools\package_portable.ps1 -RequireEmbeddedPython
```

El ZIP se genera en `dist/` y excluye:

- `config.json`
- `runtime/downloads/`
- `output/`
- backups
- caches

## Tests

Ejecutar suite Python:

```powershell
python -m unittest discover -s sqx-edge-tool -p "test*.py"
```

Validar JavaScript:

```powershell
node --check js\app-config.js
node --check js\data.js
node --check js\dashboard.js
node --check js\main.js
```

## Seguridad Y Datos Locales

Si creas un nuevo repo, no deberian subirse:

- `sqx-edge-tool/config.json`
- `sqx-edge-tool/runtime/`
- `sqx-edge-tool/output/`
- `dist/`
- backups locales

El `.gitignore` ya cubre esos paths.

## Documentacion

- Setup general: `README_SETUP.md`
- Backend y CLI: `sqx-edge-tool/README.md`




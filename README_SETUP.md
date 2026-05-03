# SQX Edge — Dashboard + Project Generator

Suite completa de:

1. **Dashboard SQX Edge** — visualización del pipeline (Por Activo, Categorías, Filtros Fase 2, SQX Priority, Pipeline State, Project Generator, Estrategias, Workflow)
2. **SQX Edge Tool** — backend Python que genera Custom Projects `.cfx` para SQX y limpia `.sqx` post-mining

## Contenido del paquete

```
.
├── START_SQX_EDGE.bat          ← doble click: arranca API portable y abre dashboard
├── STOP_SQX_EDGE.bat           detiene la API local si queda abierta
├── SQX_Dashboard_v6.html       Dashboard principal — abrir con doble-click
├── css/dashboard.css           Estilos
├── js/                         Lógica del dashboard (data + render + main)
├── README_SETUP.md             ← este archivo
└── sqx-edge-tool/              Backend Python (opcional)
    ├── README.md
    ├── run.bat                 CLI
    ├── run-web.bat             ← Web API (lo que usa el dashboard)
    ├── run-embedded.bat        CLI con Python embebido
    ├── run-web-embedded.bat    Web API con Python embebido
    ├── config.template.json    ← copia a config.json y edita
    ├── requirements.txt        flask
    ├── core/                   módulos Python
    ├── cli/                    entry CLI
    ├── api/                    Flask REST API
    ├── templates/              Capa1_Long.cfx + Capa2_Base.cfx (seeds validados)
    └── output/                 (vacía, se llena al generar .cfx)
```

## Setup mínimo (solo dashboard, 0 dependencias)

Doble-click sobre `SQX_Dashboard_v6.html`. Funciona offline en cualquier navegador moderno. Los datasets pesados están separados en `js/historical-data.js` y `js/scores-data.js` para mantener el HTML más limpio. Tabs Por Activo / Categorías / Filtros Fase 2 / SQX Priority / Pipeline State / Project Generator / Estrategias / Workflow funcionan inmediatamente.

El tab **"Project Generator"** mostrará 🔴 backend desconectado hasta que arranques el módulo Python (paso siguiente).

## Uso para usuario básico: un solo click

En el paquete portable final, el usuario solo tiene que hacer doble click en:

```text
START_SQX_EDGE.bat
```

Ese launcher:

1. Arranca la API local con el Python embebido incluido en `sqx-edge-tool/runtime/python`.
2. Espera a que `http://127.0.0.1:5050/api/health` responda.
3. Abre `SQX_Dashboard_v6.html` automáticamente.

Para cerrar la API local, puede cerrar la ventana "SQX Edge API" o hacer doble click en:

```text
STOP_SQX_EDGE.bat
```

## Setup completo (con generador de .cfx)

### 1. Pre-requisitos

- **Windows** (tested on Windows 11)
- **Python 3.10+** ([descargar](https://www.python.org/downloads/) — durante install marca "Add Python to PATH")
- **StrategyQuant X** instalado. Probado con estructura `user/data/data.db`; los aliases se configuran desde la UI para adaptarlo a tu broker/versión.

### 2. Instalar Flask

Abre cmd/PowerShell en la carpeta del proyecto:

```bash
cd sqx-edge-tool
pip install -r requirements.txt
```

### 2B. Opción portable: Python embebido

Si no quieres depender del Python instalado en Windows:

```powershell
cd sqx-edge-tool
powershell -NoProfile -ExecutionPolicy Bypass -File tools\bootstrap_embedded_python.ps1
```

Luego arranca el backend con:

```bat
run-web-embedded.bat
```

También puedes usar la CLI portable:

```bat
run-embedded.bat list
```

Para crear un ZIP portable distribuible:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\package_portable.ps1 -RequireEmbeddedPython
```

### 3. Configurar paths

Copia `config.template.json` a `config.json` y edítalo, **o mejor**: déjalo vacío y configura desde la UI del dashboard (más fácil):

1. Doble-click `sqx-edge-tool/run-web.bat` → arranca el backend en `http://localhost:5050` (deja la ventana abierta)
2. Abre `SQX_Dashboard_v6.html` en el navegador → tab **Project Generator**
3. Banner debe estar en 🟢 verde
4. Click ⚙️ Configuración → desplegable
5. Click **🔍 Auto-detectar SQX** → busca tu instalación automáticamente
6. (Si no la encuentra) escribe el path manual y click **✓ Validar paths**
7. Click **🔍 Auto-sugerir** en la sección "Aliases" para mapear tus tickers (USTEC → tu ticker SQX como NDXm/NDX/etc según tu broker)
8. Click **💾 Guardar config**

### 4. Uso

**Generar Custom Project para un mining:**
- Tab Project Generator → tabla de minings → click **📦 Capa 1** o **📦 Capa 2**
- El `.cfx` se genera en `sqx-edge-tool/output/` con costos REALES de tu broker (leídos de `data.db`)
- Lo abres en SQX (File → Open Project) y arrancas el mining

**Limpiar `.sqx` post-mining:**
- Tab Project Generator → sección 🧹 Strategy Cleaner abajo
- Pega la ruta a `databanks/Foward/` (o donde tengas las estrategias finales)
- Click **📂 Escanear** → tabla con todas las estrategias
- Selecciona, marca opciones (Eliminar ExitAfterBars + Renombrado institucional) → **🧹 Procesar selección**

## Adaptar a tu broker / setup

El paquete viene con templates seed validados (`Capa1_Long.cfx` y `Capa2_Base.cfx`) que probablemente NO son los que usas tú directamente. Tienes 2 opciones:

**Opción A** — usar mis templates como base y dejar que el generador parche todo (symbol, costos, fechas, dirección) según tu mining. Solo tienes que reseleccionar `templateFile` y `strategyFile` en el SQX Builder al cargarlo (los paths absolutos se limpian al generar).

**Opción B** — sustituir las plantillas por las tuyas: copia tus `.cfx` a `sqx-edge-tool/templates/Capa1_Long.cfx` y `Capa2_Base.cfx`. El generador respeta tu config interna (Sequential, MC, MC2, SPP, WFM, etc.) y solo cambia los nodos específicos del mining.

## Arquitectura técnica

- **Dashboard**: HTML estático + JS vanilla (sin frameworks). Los datasets pesados viven en `js/historical-data.js` y `js/scores-data.js`; abre con `file://` sin servidor.
- **SQX Edge Tool**: Python 3.10+ con Flask, o runtime portable en `sqx-edge-tool/runtime/`. CORS restringido a origen local/file para uso con el dashboard. CLI alternativo (`run.bat list / generate / generate-all` o `run-embedded.bat`).
- **Plantillas `.cfx`**: ZIP+XML, modificadas in-memory con `xml.etree.ElementTree` + `zipfile`. Mapeo asset→instrument configurable por broker.
- **Lectura `data.db` SQX**: SQLite read-only, extrae spread/swap/commission reales para el broker activo.
- **Cleaner `.sqx`**: ZIP+regex sobre `strategy_Portfolio.xml` / `settings.xml` / `lastSettings.xml`, paralelizado con ProcessPoolExecutor. Crea backup automático en `__sqx_backups/` antes de modificar.

## Soporte

Cualquier duda escríbeme. El código es legible y self-documented; el README de `sqx-edge-tool/` tiene más detalle técnico.

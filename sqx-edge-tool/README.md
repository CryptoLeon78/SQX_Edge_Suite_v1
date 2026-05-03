# SQX Edge Tool

Generador de Custom Projects (`.cfx`) para SQX adaptado a la metodología SQX Edge. El plan, activos, estrategias, periodos y defaults viven en manifiestos JSON compartidos con el dashboard.

## Requisitos

- Python 3.10+ (probado con 3.12+)
- StrategyQuant X con `user/data/data.db` disponible
- Plantillas seed `.cfx` validadas en SQX (incluidas: `templates/Capa1_Long.cfx` y `templates/Capa2_Base.cfx`)

## Setup

1. Copia `config.template.json` a `config.json` o configura paths desde el tab Project Generator del dashboard.
2. Verifica que `templates/Capa1_Long.cfx` y `templates/Capa2_Base.cfx` existen.
3. Usa aliases por asset en la UI para mapear tus tickers del plan a los instrumentos reales de tu broker.

## Setup portable con Python embebido

F7 permite ejecutar el backend sin depender del Python instalado en Windows. El runtime queda dentro de `sqx-edge-tool/runtime/`.

```powershell
cd sqx-edge-tool
powershell -NoProfile -ExecutionPolicy Bypass -File tools\bootstrap_embedded_python.ps1
```

Después usa los launchers portables:

```bat
run-embedded.bat list
run-web-embedded.bat
```

En el paquete completo, el launcher más simple para un usuario básico está en la raíz:

```bat
START_SQX_EDGE.bat
```

Ese archivo arranca la API con Python embebido y abre el dashboard automáticamente.

Para crear un ZIP distribuible:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\package_portable.ps1 -RequireEmbeddedPython
```

El ZIP se genera en `dist/`. No incluye `config.json`, `output/` ni descargas temporales.

## Uso

```bash
# Listar los minings del plan configurado
run.bat list

# Generar 1 proyecto (Mining 2 = XAUUSD H4 BS_Tendencia L)
run.bat generate --mining 2

# Generar todo el plan de golpe
run.bat generate-all

# Ver config + paths
run.bat info
```

Los `.cfx` generados quedan en `output/` con nombres tipo `Mining02_XAUUSD_H4_BS_Tendencia_Capa1.cfx`. Si ya existe un archivo con el mismo nombre, se guarda copia previa en `output/__cfx_backups/`.

## Cómo cargarlo en SQX

1. Abre StrategyQuant X.
2. File → Open Project → selecciona el `.cfx` generado.
3. **Importante**: en el Builder, vuelve a seleccionar `templateFile` y `strategyFile` con los paths de tu instalación (las rutas absolutas se limpian al generar para evitar referenciar PCs ajenos).

## Arquitectura

```
sqx-edge-tool/
├── core/
│   ├── cfx_editor.py       — abre/modifica/guarda .cfx (zip+xml)
│   ├── xml_patcher.py      — patches: symbol, TF, dates, direction, swap
│   ├── plan.py             — carga el plan desde config/plan.json
│   └── project_generator.py — orquesta el pipeline de generación
├── config/
│   ├── plan.json           — minings + fases
│   ├── generator_profiles.json — periodos, tasks SQX, autodetect/API
│   ├── instruments.json    — defaults, aliases y heurísticas de instrumentos
│   ├── assets.json         — universo de activos del dashboard
│   ├── strategies.json     — estrategias base
│   └── ui_manifest.json    — tabs, filtros, estados, thresholds y textos UI
├── tools/
│   ├── build_frontend_manifest.py — regenera js/manifest-data.js
│   ├── bootstrap_embedded_python.ps1 — prepara runtime/python portable
│   └── package_portable.ps1 — empaqueta ZIP portable
├── cli/
│   └── sqx_edge.py         — CLI entry point
├── templates/
│   ├── Capa1_Long.cfx      — semilla validada Capa 1
│   └── Capa2_Base.cfx      — semilla validada Capa 2
├── output/                 — .cfx generados
├── runtime/                — Python embebido local (generado, no versionado)
├── config.json             — paths SQX + defaults
├── run.bat                 — launcher Windows con Python del sistema
├── run-embedded.bat        — launcher CLI con Python embebido
├── run-web.bat             — Web API con Python del sistema
└── run-web-embedded.bat    — Web API con Python embebido
```

## Roadmap

- [x] **F1**: CLI mínimo + plantilla seed + generación por mining
- [x] **F2**: leer `data.db` para spreads/swaps/fechas reales por símbolo
- [x] **F3**: API REST Flask en `localhost:5050`
- [x] **F4**: Tab "Project Generator" en SQX Edge Dashboard
- [x] **F5**: `strategy_cleaner.py` (limpia `.sqx` post-mining con backup)
- [x] **F6**: Plantilla Capa 2 + UI específica
- [x] **F7**: Empaquetar Python embebido (runtime portable + ZIP distribuible)

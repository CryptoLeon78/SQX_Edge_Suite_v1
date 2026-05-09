# SQX Edge Suite v1

Dashboard y herramienta local para organizar el pipeline SQX Edge, generar Custom Projects `.cfx` para StrategyQuant X y limpiar estrategias `.sqx` post-mining.

## Estado Actual

- Estado interno: PG7 completada con notas Markdown de entrega comprador para `.cfx` desde Project Generator.
- Estado comercial: M99 completada con decision local del siguiente movimiento comercial controlado desde evidencia M98.
- Ultimo commit base verificado antes de S5/M-pre: `d7c0757`.
- Ultimo ZIP portable verificado: `dist/SQX_Edge_Tool_Portable_20260509_102131.zip`.
- SHA256 del ZIP: `18EC98981D8B52535E1FE26EA47876588FA2EB8321DD2A9706CBD30B6A0B7E5D`.
- Siguiente paso recomendado: M100 para ejecutar exactamente el movimiento comercial controlado aprobado por M99, V10 para comparativa de packs SQX Views, SB18 para pulir export de evidencia comprador o R46 solo con autorizacion explicita para publicar GitHub Release.
- Ultima mejora funcional: `dukas_mt5_ohlc_download.py --recent-bars` descarga 33 activos x 4 timeframes desde MT5; A56 devuelve GO con A55/A53/A54 en verde.

## SQX Edge Pro

El proyecto esta preparando una edicion comercial Pro con suscripcion mensual/anual, soporte opcional y packs de plantillas alrededor de la herramienta.

Oferta inicial prevista:

- SQX Edge Free: descarga portable para probar el flujo.
- SQX Edge Pro Mensual: 24 EUR/mes.
- SQX Edge Pro Anual: 199 EUR/ano.
- Setup Assist: instalacion y configuracion guiada.
- Template Pack 1: pack comercial separado.

Aviso responsable: SQX Edge Pro no promete rentabilidad ni resultados financieros. La propuesta es productividad, orden, trazabilidad y reduccion de errores operativos dentro de StrategyQuant X.

Documentos comerciales:

- `docs/COMMERCIAL_README.md`
- `docs/PRIVATE_COMMERCIAL_DOCS.md`
- `docs/PRIVATE_COMMERCIAL_SPLIT_PLAN.md`
- `docs/PUBLIC_COMMERCIAL_POINTERS.md`
- `docs/private_commercial_manifest.json`
- `docs/MONETIZATION_ROADMAP.md`
- `docs/PUBLIC_ROADMAP.md`
- `docs/PROJECT_GOVERNANCE.md` consulta obligatoria antes de fases/mensajes de trabajo; incluye G4 para tratar `SQX_Institutional_Core` como repo original/first-class mediante el remoto `institutional`, sin `force push` ni espejo destructivo.
- `DISCIPLINA_OPERATIVA.md` estandar de sincronizacion y calidad para el equipo institucional.
- `resources/pro-buyer-pack/README.md`
- `resources/pro-buyer-pack/onboarding/START_HERE.md`
- `docs/sales/TEMPLATE_PACK_1_DELIVERY.md`
- `docs/sales/TEMPLATE_PACK_1_PUBLIC_OFFER.md`
- `docs/sales/TEMPLATE_PACK_1_LIVE_CHECKOUT_PUBLICATION.md`
- `docs/sales/TEMPLATE_PACK_1_PURCHASE_DRILL.md`
- `docs/sales/TEMPLATE_PACK_1_HANDOFF.md`
- `docs/sales/TEMPLATE_PACK_1_SALES_REGISTER.md`
- `docs/sales/TEMPLATE_PACK_1_FEEDBACK_COHORT.md`
- `docs/sales/TEMPLATE_PACK_1_ACTION_PLAN.md`
- `docs/sales/TEMPLATE_PACK_2_SPECS.md`
- `docs/sales/TEMPLATE_PACK_2_PURCHASE_DRILL.md`
- `docs/sales/TEMPLATE_PACK_2_HANDOFF.md`
- `docs/sales/TEMPLATE_PACK_2_SALES_REGISTER.md`
- `docs/sales/TEMPLATE_PACK_2_FEEDBACK_COHORT.md`
- `docs/sales/BUYER_READY_CHECKOUT_RELEASE.md`
- `docs/sales/PUBLIC_BUYER_PAGE_CADENCE.md`
- `docs/sales/FIRST_CONTROLLED_BUYER_LOG.md`
- `docs/sales/POST_SALE_IMPROVEMENT_LOOP.md`
- `docs/sales/POST_SALE_MICRO_UPDATES.md`
- `docs/sales/NEXT_CONTROLLED_BUYER_READINESS.md`
- `docs/sales/NEXT_CONTROLLED_BUYER_OUTCOME.md`
- `docs/sales/CONTROLLED_DISTRIBUTION_STEP.md`
- `docs/sales/CONTROLLED_DISTRIBUTION_REVIEW.md`
- `docs/sales/NEXT_BUYER_FACING_ASSET.md`
- `docs/sales/PRIVATE_ASSET_REVIEW.md`
- `docs/sales/CONTROLLED_PUBLICATION_GATE.md`
- `docs/sales/LIMITED_PUBLICATION_DRAFT.md`
- `docs/sales/OPERATOR_PUBLICATION_REVIEW.md`
- `docs/sales/MANUAL_LIMITED_PUBLICATION_RECORD.md`
- `docs/sales/MANUAL_PUBLICATION_MONITOR.md`
- `docs/sales/CONTROLLED_TRAFFIC_EXPANSION_REVIEW.md`

Nota de seguridad comercial: los documentos de venta interna, buyer logs, gates privados, evidencias de checkout/soporte y plantillas operativas ya fueron migrados al repositorio privado `CryptoLeon78/sqx-edge-commercial-private`. El repo publico conserva arquitectura, releases, claims seguros y punteros de trazabilidad; `docs/MONETIZATION_*`, `docs/sales/*` y los packs Pro bajo `resources/` son stubs publicos redactados.

Export privado preparado:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\private_commercial_split.py
```

El export se genera en `commercial-private/sqx-edge-commercial-private/`, carpeta ignorada por git.

El export privado local ya fue inicializado como repo git en `main` con commit `ed79719 Initial private commercial export` y publicado en el repo privado `CryptoLeon78/sqx-edge-commercial-private`.

Activacion Pro prevista:

- El usuario recibe un JSON de licencia firmado.
- Lo pega en Inicio -> Licencia -> Cargar licencia.
- La API local verifica la firma offline y guarda `backend/sqx-edge-tool/config/license.json`.
- La licencia y la clave privada de firma nunca se incluyen en el ZIP portable.

SQX Views:

- El tab `SQX Views` genera archivos `.vw` para Databank sin depender de Python externo.
- La fuente prototipo Tkinter quedo migrada al flujo nativo del dashboard y archivada en backup previo de V5.
- Free incluye el preset `EGT Core`; Pro desbloquea el catalogo completo y presets avanzados.
- Incluye ejemplos buyer-ready para primera revision, robustez, riesgo y auditoria completa.
- Incluye packs por perfil de comprador para evaluacion Free, Setup Assist Pro, comprador centrado en riesgo y entrega de auditoria.
- Incluye packs por familia de activo y flujos de validacion para revisar Forex, indices, oro, intake, robustez, riesgo y auditoria.
- Puedes guardar presets propios en el navegador y moverlos entre instalaciones con packs JSON exportables/importables.
- La importacion de packs SQX Views muestra preview de presets, metricas, columnas estimadas y reemplazos antes de fusionar.
- Workflow y Estrategias incluyen accesos directos para abrir SQX Views con vistas recomendadas ya preparadas.
- La vista descargada puede cargarse en StrategyQuant X desde Databank -> Load View.

Project Generator:

- `Custom libre` permite crear `.cfx` fuera del plan mining con asset, timeframe, blocksetting, direccion y capa propios.
- Incluye presets locales reutilizables, exportacion/importacion JSON, perfiles starter y familias por objetivo para usuarios que quieren empezar sin configurar todo desde cero.
- La importacion de packs custom muestra preview de presets, assets, capas y reemplazos antes de fusionarlos con los guardados locales.
- Las tarjetas de activo/categoria pueden prefijar un Custom Project desde acciones rapidas sin ejecutar generacion automatica.
- `Entrega comprador .cfx` prepara notas Markdown copiables/descargables con configuracion, archivos referenciados, checklist y limites responsables.

Pipeline State:

- Incluye acciones rapidas para anadir candidatos al Plan Mining desde activo/categoria.
- Muestra salud operativa compacta y funnel visual editable sin recuperar tabs eliminados como Top Picks o Matriz.

Herramientas analiticas:

- `plan_quality_advisor.py` revisa el plan actual contra el baseline H1 disponible, propone alternativas diversificadas y puede anadir evidencia multi-timeframe si se le entrega una carpeta de metricas.
- `multi_timeframe_scoring.py` calcula scores por timeframe y consenso ponderado a partir de metricas JSON ya generadas. No descarga datos, no modifica HTML y esta pensado como paso controlado antes de exponer multi-TF en la UI.
- `multi_timeframe_metric_gate.py` valida carpetas de metricas `asset_metrics[_TF].json` con cobertura, completitud, activos desconocidos, compatibilidad del scorer y hashes SHA256 antes de aceptarlas como fuente propia.
- `first_party_metric_source.py` genera el bundle H1 first-party desde `app/js/scores-data.js`, escribe manifiesto de procedencia y ejecuta el gate sin fabricar timeframes no disponibles.
- `multi_timeframe_source_intake.py` prepara una carpeta de intake H1/M30/M15/H4, puede anadir H1 first-party y bloquea M15/M30/H4 si no existen metricas reales.
- `multi_timeframe_plan_artifacts.py` genera reportes del Plan Quality Advisor con evidencia MTF solo si A53 devuelve GO; si no, escribe un NO_GO trazable.
- `ohlc_metric_builder.py` convierte CSV OHLC revisables (`ASSET_TF.csv`) en metricas multi-timeframe compatibles con A53/A54.
- `real_mtf_pipeline_run.py` orquesta A55 -> A53 -> A54 y devuelve GO solo si la cadena completa con datos reales queda validada.

## Entrega Final

Paquete recomendado para usuario final:

```text
dist/SQX_Edge_Tool_Portable_20260509_102131.zip
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

## Entrega Comercial Controlada

Estado real: preparado para demos Pro asistidas, early access, compradores fundadores y primeras ventas manuales con soporte. No esta planteado aun como lanzamiento masivo autoservicio.

Antes de entregar a un comprador:

1. Usar el ZIP verificado `SQX_Edge_Tool_Portable_20260509_102131.zip`.
2. Confirmar SHA256 `18EC98981D8B52535E1FE26EA47876588FA2EB8321DD2A9706CBD30B6A0B7E5D`.
3. Entregar la licencia Pro firmada por separado, nunca dentro del ZIP.
4. Mantener claims seguros: productividad, orden, trazabilidad y reduccion de errores operativos; nunca prometer rentabilidad.
5. Registrar incidencias de instalacion, activacion, soporte y decision de repetir/pausar antes de ampliar trafico.

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

## Tests y CI

Dependencias de desarrollo:

```bat
python -m pip install -r requirements-dev.txt
```

Validacion local recomendada:

```bat
python -m pytest
```

Contratos JS:

```powershell
Get-ChildItem tests/js/contracts -Filter *.mjs | Sort-Object Name | ForEach-Object { node $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
```

GitHub Actions ejecuta el baseline en cada push/PR a `main`: compilacion Python, pytest, contratos JS y `git diff --check`.

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

## Project Generator

- `Generacion masiva` mantiene el flujo original: genera `.cfx` desde los minings del plan.
- `Custom libre` permite crear un proyecto fuera del plan con nombre, asset, timeframe, blocksetting, direccion y capa propios.
- El custom libre usa el template configurado de la capa seleccionada, o un template opcional indicado en el formulario.
- Los presets custom se guardan en el navegador local para reutilizar combinaciones frecuentes sin reescribir campos.
- Los presets custom se pueden exportar/importar como packs JSON para moverlos entre instalaciones.
- Las familias por objetivo agrupan perfiles custom para comprador inicial, validacion intradia, revision de riesgo o muestra Pro completa.
- La API local expone `/api/generate-custom` y aplica la misma licencia Pro que `/api/generate`.

## Plan Quality Advisor

Herramienta backend para revisar el plan actual contra los scores objetivos del dashboard y generar una propuesta diversificada:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\plan_quality_advisor.py
```

Para integraciones o auditoria:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\plan_quality_advisor.py --json
```

Es una guia de revision, no una orden automatica de reemplazo. La version actual usa el baseline H1 disponible en `app/js/scores-data.js`; el scoring multi-timeframe queda planificado como fase A48.

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

Tambien puedes lanzar el modo estricto con doble click desde:

```text
RELEASE_SQX_EDGE.bat
```

Ese modo exige Git limpio antes de empaquetar y deja un resumen en `dist/SQX_release_summary.txt`.

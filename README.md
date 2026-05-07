# SQX Edge Suite v1

Dashboard y herramienta local para organizar el pipeline SQX Edge, generar Custom Projects `.cfx` para StrategyQuant X y limpiar estrategias `.sqx` post-mining.

## Estado Actual

- Estado interno: M61 completada, `template_pack_2_purchase_drill_ready`.
- Ultimo commit base verificado antes de M61: `dff0ba8`.
- Ultimo ZIP portable verificado antes de M47: `dist/SQX_Edge_Tool_Portable_20260507_075847.zip`.
- SHA256 del ZIP: `FE573CADCB79E2D93E1D1491BADC35DF0295C37DD08017AF3A9C784581E47E09`.
- Siguiente paso recomendado: M62, preparar handoff post-compra de Template Pack 2 y decision de escala/pausa.

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
- `docs/MONETIZATION_ROADMAP.md`
- `docs/PUBLIC_ROADMAP.md`
- `docs/PROJECT_GOVERNANCE.md` consulta obligatoria antes de fases/mensajes de trabajo.
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

Activacion Pro prevista:

- El usuario recibe un JSON de licencia firmado.
- Lo pega en Inicio -> Licencia -> Cargar licencia.
- La API local verifica la firma offline y guarda `backend/sqx-edge-tool/config/license.json`.
- La licencia y la clave privada de firma nunca se incluyen en el ZIP portable.

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

Tambien puedes lanzar el modo estricto con doble click desde:

```text
RELEASE_SQX_EDGE.bat
```

Ese modo exige Git limpio antes de empaquetar y deja un resumen en `dist/SQX_release_summary.txt`.

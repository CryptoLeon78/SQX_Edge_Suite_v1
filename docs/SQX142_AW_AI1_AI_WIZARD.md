# SQX142-AW-AI1 AI Wizard Propio Para AlgoWizard 142

Estado: `implemented_v1_pending_manual_sqx_roundtrip`.

Esta fase crea un AI Wizard propio para SQX 142 local como integracion hibrida: overlay completo dentro de AlgoWizard 142, backend Flask local y generacion conservadora de drafts `.sqx` editables. Build 144 queda como referencia de producto; no se copian binarios, internals, plugins core, licencia, activacion ni comportamiento runtime de 144.

## Entrega

- Version: `sqx142-ai-wizard-v1`.
- Backend local-only:
  - `GET /api/sqx142/ai-wizard/status`
  - `POST /api/sqx142/ai-wizard/plan`
  - `POST /api/sqx142/ai-wizard/draft-sqx`
  - `GET /api/sqx142/ai-wizard/draft-sqx/download/<file>`
- Core: `backend/sqx-edge-tool/core/sqx142_ai_wizard.py`.
- Overlay: `integrations/sqx142/ai_wizard_overlay/sqx-edge-aiwizard.js` and `.css`.
- Installer: `tools/sqx142_ai_wizard_overlay.ps1 status/install/rollback`.
- Draft output: `output/ai_wizard_drafts/`, ignored by Git.

## Metodo

El v1 no inventa XML completo desde un prompt. Primero convierte el texto en una especificacion `sqx-edge.ai-wizard-strategy-spec`, luego genera un paquete intermedio compatible con el contrato `sqx-edge.strategy-builder-package`, y solo despues crea el `.sqx` desde ejemplos AlgoWizard 142 validos.

Arquetipos permitidos:

- `ema_cross`
- `breakout`
- `range_breakout`
- `mean_reversion`

Si la idea no encaja, el backend devuelve `blocked_unsupported_rule`. Si el prompt contiene rutas, tokens, licencia, crack, bypass o secretos, devuelve `prompt_not_public_safe`. Si los ejemplos locales no son ZIP o no contienen `strategy_Portfolio.xml`, devuelve `template_probe_failed`.

## Provider IA

- Ollama local es el default.
- OpenAI queda preparado por configuracion privada y desactivado por defecto.
- Variables opcionales:
  - `SQX_AI_WIZARD_PROVIDER=openai`
  - `SQX_AI_WIZARD_OPENAI_ENABLED=1`
  - `SQX_AI_WIZARD_OPENAI_MODEL=<model>`
  - `OPENAI_API_KEY=<private>`
- El v1 no persiste prompts ni respuestas y no llama a proveedores desde el navegador.

## Limites Duros

- No SQX runtime launch.
- No `run_project`, retests, optimizacion ni generacion SQX automatica.
- No writes a `data.db`, `user/projects`, databanks, logs SQX ni settings vivos.
- No copia de engine, binarios, plugins core, internals 144, licencia, activacion, bypass, tokens o credenciales.
- Todo draft requiere revision manual en AlgoWizard antes de cualquier validacion real.

## Operacion

Status dry-run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_ai_wizard_overlay.ps1 status
```

Instalacion local, solo con SQX cerrado:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_ai_wizard_overlay.ps1 install -Apply
```

Rollback local, solo con SQX cerrado:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_ai_wizard_overlay.ps1 rollback -Apply
```

## Verificacion Esperada

- Python: core, rutas local-only, privacidad, `.sqx` ZIP y prompt blockers.
- JS/contracts: overlay DOM, API Flask-only, generate disabled before valid spec and blocked-state rendering.
- Manual: instalar overlay, abrir AlgoWizard, prompt `EMA cross trend-following EURUSD H1 with SL/TP`, descargar `.sqx`, abrirlo en AlgoWizard, revisar que es editable y rollback.

# SQX142-AW-AI2 AlgoWizard AI Studio Con Catalogo Completo

Estado: `blocked_sqx_process_running`.

Esta fase convierte el AI Wizard de AlgoWizard 142 en un AI Studio reutilizable. El alcance v1 de AI2 es Todo AlgoWizard, no Full Editor completo: puede planificar estrategias expresables con bloques, indicadores, senales, operadores y parametros disponibles en AlgoWizard; cualquier peticion de Full Editor, Java custom o engine/plugin queda bloqueada.

SQX estaba abierto durante la implementacion, por descarga de data del operador. Por tanto la entrega inicial fue repo-side y read-only sobre SQX: no se ejecuto install, rollback ni manual roundtrip.

Intento seguro del 2026-06-04: `tools/sqx142_ai_wizard_overlay.ps1 status` detecto overlay/assets existentes, pero `install` dry-run quedo bloqueado por `sqx_process_running`. Una inspeccion read-only confirmo que el marcador previo existe, pero `sqx142-ai-wizard-overlay-v2` no esta instalado y los assets activos no coinciden con la fuente repo. No se ejecuto `install -Apply`, no se forzo cierre de SQX y no se hizo manual roundtrip.

## Entrega

- Version: `sqx142-ai-wizard-studio-v2`.
- Catalogo: `sqx-edge.ai-wizard-capability-catalog-v1`.
- AST: `sqx-edge.ai-wizard-strategy-ast-v1`.
- SQLite local: `.local/sqx142_ai_wizard/ai_wizard.sqlite`.
- Backend core: `backend/sqx-edge-tool/core/sqx142_ai_wizard.py`.
- API Flask local-only: `backend/sqx-edge-tool/api/server.py`.
- Overlay source: `integrations/sqx142/ai_wizard_overlay/sqx-edge-aiwizard.js` and `.css`.
- Tests: `backend/sqx-edge-tool/test_sqx142_ai_wizard_studio.py`, `tests/js/contracts/sqx142_aw_ai2_contracts.mjs`.

## Subfases

- `AI2.0 Baseline`: AW-AI1 queda congelado como `sqx142-ai-wizard-v1`; overlay instalado previamente, manual roundtrip pendiente.
- `AI2.1 Capability Catalog`: extractor read-only allowlist para `wizard.xml`, `conditions.xml`, parameter sets, ejemplos `.sqx`, snippets/bloques, custom indicators metadata y BlockSettings repo. Devuelve conteos, hashes y referencias opacas, no rutas locales ni XML crudo.
- `AI2.2 Strategy AST`: contrato `sqx-edge.ai-wizard-strategy-ast-v1` con long/short entry/exit, operadores logicos, comparaciones, acciones, SL/TP/trailing/MM y referencias a catalogo.
- `AI2.3 Validator`: todo AST debe usar IDs existentes en catalogo y parametros dentro de tipo/rango/enum. Si falta soporte de compilador, se marca `blocked_not_draftable_yet`.
- `AI2.4 Session Studio`: sesiones, interacciones redactadas, revisiones, drafts y auditoria se guardan en SQLite local. No se persisten prompts raw ni respuestas raw de proveedor.
- `AI2.5 Draft Compiler`: genera `.sqx` solo para AST validado y compilable; los demas planes validos quedan como plan editable bloqueado con razon precisa.
- `AI2.6 Overlay UX`: historial, reabrir/forkear sesiones, catalog browser, chips de indicadores/operadores, editor de parametros y panel de bloqueos util.
- `AI2.7 Manual Roundtrip`: pendiente hasta SQX cerrado; requiere abrir draft en AlgoWizard y confirmar editabilidad.

## APIs Local-Only

- `GET /api/sqx142/ai-wizard/catalog`
- `POST /api/sqx142/ai-wizard/catalog/refresh`
- `GET /api/sqx142/ai-wizard/sessions`
- `POST /api/sqx142/ai-wizard/sessions`
- `GET /api/sqx142/ai-wizard/sessions/<id>`
- `POST /api/sqx142/ai-wizard/sessions/<id>/messages`
- `PATCH /api/sqx142/ai-wizard/sessions/<id>/spec`
- `POST /api/sqx142/ai-wizard/sessions/<id>/drafts`
- `GET /api/sqx142/ai-wizard/drafts/<id>/download`

El navegador llama solo a Flask local. No llama a Ollama, OpenAI ni ningun proveedor IA directo.

## Privacidad Y Acceso SQX

- Lectura SQX: allowlist amplia y sanitizada.
- Mientras SQX esta abierto: `user/data` y `user/projects` quedan como `pending_stable_snapshot`.
- API/UI/docs no devuelven rutas locales, XML crudo, codigo SQX, logs, licencias, tokens, provider secrets ni binarios.
- Los prompts/respuestas raw no se persisten por defecto; se guarda hash, resumen estructurado redactado y decisiones estructuradas.
- Downloads de drafts usan ID opaco, no nombre/ruta elegida por el navegador.

## Compilacion

El Studio puede planificar cualquier estrategia expresable con el catalogo de AlgoWizard detectado, pero el draft `.sqx` solo se emite si el compilador tiene soporte probado para ese AST. En esta entrega el compilador mantiene compatibilidad conservadora con el flujo de AW-AI1 para EMA cross y bloquea planes validos no probados con `blocked_not_draftable_yet`.

Bloqueos principales:

- `prompt_required`
- `prompt_not_public_safe`
- `blocked_full_editor_scope`
- `unknown_block`
- `unknown_operator`
- `param_out_of_range`
- `blocked_not_draftable_yet`

## Limites Duros

- No SQX runtime launch.
- No `run_project`, retests, optimizacion ni ejecucion de proyectos.
- No writes a `data.db`, `user/projects`, databanks ni settings vivos.
- No Full Editor completo en v1.
- No copia de internals 144, engine, binarios, plugins core, licencia, activacion, bypass, tokens o credenciales.
- No promesas de rentabilidad, riesgo cero o validez de trading sin revision manual.

## Verificacion

- `python -m pytest backend\sqx-edge-tool\test_sqx142_ai_wizard_studio.py -q`
- `python -m pytest backend\sqx-edge-tool\test_sqx142_ai_wizard.py -q`
- `node tests\js\contracts\sqx142_aw_ai2_contracts.mjs`
- `node tests\js\contracts\sqx142_aw_ai1_contracts.mjs`
- `tools\sqx142_ai_wizard_overlay.ps1 status`

Manual pendiente con SQX cerrado:

1. Instalar overlay actualizado con `tools\sqx142_ai_wizard_overlay.ps1 install -Apply`.
2. Abrir AlgoWizard, crear sesion, pedir una estrategia multi-indicador, editar parametros, cerrar/reabrir, reanudar y forkear.
3. Generar draft solo si el AST es compilable.
4. Abrir el draft en AlgoWizard y confirmar que es editable.
5. Confirmar que no hubo SQX runtime launch, no `data.db` write, no `user/projects` write y no databank mutation.

## Log Public-Safe

2026-06-04:

- status/dry-run: `blocked_sqx_process_running`
- overlay previo: detectado
- overlay v2 instalado: no confirmado
- assets activos: no coinciden con la fuente repo v2
- mutaciones ejecutadas: ninguna
- siguiente accion segura: cerrar SQX manualmente, reintentar `install -Apply` y hacer roundtrip humano en AlgoWizard

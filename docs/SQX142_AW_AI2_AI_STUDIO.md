# SQX142-AW-AI2 AlgoWizard AI Studio Con Catalogo Completo

Estado: `installed_pending_manual_roundtrip`.

Esta fase convierte el AI Wizard de AlgoWizard 142 en un AI Studio reutilizable. El alcance v1 de AI2 es Todo AlgoWizard, no Full Editor completo: puede planificar estrategias expresables con bloques, indicadores, senales, operadores y parametros disponibles en AlgoWizard; cualquier peticion de Full Editor, Java custom o engine/plugin queda bloqueada.

AI3 extiende esta base con `sqx142-aw-ai3-universal-prompt-compiler-v1`: entrada universal de prompt, interpretacion local modelo -> AST y primera familia compilable `candle_atr_sequence`. AI4 anade `sqx142-aw-ai4-rsi-mean-reversion-compiler-v1` para RSI mean-reversion puro. AI5 cierra `sqx142-aw-ai5-compiler-candidate-decision-gate-v1` seleccionando Keltner solo como candidata de fixture/contrato AI6. La regla sigue siendo conservadora: `universal_prompt_intake_not_universal_sqx_generation`; si no hay compilador probado, se bloquea y no se inventa un bot.

SQX estaba abierto durante la implementacion, por descarga de data del operador. Por tanto la entrega inicial fue repo-side y read-only sobre SQX: no se ejecuto install, rollback ni manual roundtrip.

Intento seguro del 2026-06-04: `tools/sqx142_ai_wizard_overlay.ps1 status` detecto overlay/assets existentes, pero `install` dry-run quedo bloqueado por `sqx_process_running`. Una inspeccion read-only confirmo que el marcador previo existe, pero `sqx142-ai-wizard-overlay-v2` no esta instalado y los assets activos no coinciden con la fuente repo. No se ejecuto `install -Apply`, no se forzo cierre de SQX y no se hizo manual roundtrip.

Instalacion del 2026-06-04 tras cierre manual de SQX: `tools/sqx142_ai_wizard_overlay.ps1 install -Apply` devolvio `installed`, creo backup `sqx142_ai_wizard_overlay_20260604_163808` y dejo `sqx142-ai-wizard-overlay-v2` referenciado en AlgoWizard. Verificacion read-only: JS/CSS activos coinciden con la fuente repo y `processCount=0`. El roundtrip humano sigue pendiente.

Patch DRAFT1 del 2026-06-04: durante el roundtrip humano, el operador reporto una pantalla `Not Found` tras la accion de draft. Causa probable: el overlay construia el link de descarga como `API_BASE + draft.downloadUrl` aunque `downloadUrl` ya empieza por `/api/...`, generando `/api/api/...`. El overlay ahora usa `apiUrl()` para resolver descargas backend `/api/...` contra el origen Flask local, instala el JS parcheado con backup `sqx142_ai_wizard_overlay_20260604_170156` y conserva estado `installed_pending_manual_roundtrip` hasta repetir la prueba humana.

UX1 guided bot builder del 2026-06-04: el operador reporto que crear un bot era poco intuitivo y poco amigable. El overlay fuente pasa de una entrada tecnica de sesiones/AST/catalogo a una entrada guiada: `Crear bot SQX`, `Idea del bot`, `Crear plan`, `Generar .sqx`, `Duplicar`, `Modo guiado`, ajustes basicos, bloqueos legibles con `blockerLabel()` y diagnostico local plegado. Instalacion pendiente: `tools/sqx142_ai_wizard_overlay.ps1 status` reporta `sqx_process_running` con `processCount=6`, por tanto no se ejecuto `install -Apply`. Estado UX1: `ux1_repo_ready_install_blocked_sqx_process_running`; AI2 sigue `installed_pending_manual_roundtrip`.

Instalacion UX1 del 2026-06-04 tras cierre manual de SQX: `tools/sqx142_ai_wizard_overlay.ps1 install -Apply` devolvio `installed`, creo backup `sqx142_ai_wizard_overlay_20260604_182545` y `status` queda sin warnings con `processCount=0`. Verificacion read-only: HTML incluye overlay v2, JS/CSS activos coinciden con la fuente repo, `Crear bot SQX`/`Modo guiado` estan instalados, `apiUrl()` sigue presente, `data-sqx-aiwizard-download` sigue presente y `API_BASE + draft.downloadUrl` sigue ausente. Estado UX1: `ux1_installed_pending_manual_roundtrip`; el roundtrip humano sigue pendiente.

Prompt Truthfulness Patch del 2026-06-04: el operador mostro que un prompt natural en espanol para `tres velas rojas`, `vela martillo`, entrada en segunda vela verde, `SP500`, `H1`, largo, filtro `ATR`, `Stop=100` y `TP=200` podia derivar hacia un bot no pedido. AI2 ahora elimina el fallback inseguro a `EMA`, reconoce `SP500 -> US500`, `largo -> long_only`, SL/TP numericos, secuencia de velas/martillo y filtro ATR. Si la logica reconocida no tiene compilador probado, queda como plan editable con `compiler.draftable=false`, `blocked_unsupported_candle_pattern`, `blocked_unsupported_filter` y `blocked_not_draftable_yet`; el overlay desactiva `Generar .sqx` y muestra `Plan entendido, .sqx bloqueado`. Instalacion: overlay con backup `sqx142_ai_wizard_overlay_20260604_190508` y backend local reiniciado en `127.0.0.1:5050`.

AI3 Universal Prompt Compiler del 2026-06-04: el mismo caso de velas/ATR pasa a `compiler.draftable=true` solo para la familia verificada `candle_atr_sequence`. El backend puede pedir AST a Ollama local mediado por Flask y cae al parser seguro si el modelo no esta disponible o devuelve algo invalido. No hay llamada de proveedor desde navegador, no se persisten prompt raw ni respuesta raw, y el draft conserva las entradas del ZIP plantilla parcheando solo `strategy_Portfolio.xml`. Estado: `compiler_built_roundtrip_reported_catalog_expansion_active`.

AI3 Catalog Expansion del 2026-06-04: tras roundtrip manual reportado por el operador, el siguiente salto de nivel aumenta catalogo y explicabilidad. `sqx142-aw-ai3-expanded-catalog-v1` crea `semanticCatalog` sobre bloques Wizard, condiciones AlgoWizard y features observadas en ejemplos `.sqx`; el overlay muestra `Catalogo AlgoWizard ampliado`. Los nuevos `catalogRefs.semanticIds` ayudan a entender Keltner/ADX/RSI/Bollinger y otras familias, pero siguen siendo plan-only salvo compilador probado.

AI4 RSI Mean-Reversion Compiler del 2026-06-04: el operador reporto roundtrip OK sobre AI3 Catalog Expansion y se promueve una sola familia nueva a compilador probado. `sqx142-aw-ai4-rsi-mean-reversion-compiler-v1` genera drafts `rsi_mean_reversion` para RSI puro: long `RSI(14) < 30`, short `RSI(14) > 70`, direccion desde prompt (`long_only`, `short_only`, `both`) y SL/TP desde prompt o defaults con `manualReviewRequired=true`. RSI mezclado con Bollinger u otra familia queda bloqueado con `blocked_multi_family_compiler_not_ready`; Keltner/Bollinger/ADX/Stochastic siguen plan-only. Overlay instalado con backup `sqx142_ai_wizard_overlay_20260604_210522`; HTTP probe confirma RSI draft OK y Keltner `blocked_not_draftable_yet`. El roundtrip manual RSI queda confirmado por operador como `operator_manual_rsi_roundtrip_confirmed_ai4_closed`.

AI5 Compiler Candidate Decision Gate del 2026-06-04: `sqx142-aw-ai5-compiler-candidate-decision-gate-v1` queda cerrado como `candidate_selected_keltner_requires_fixture_ai6`. Keltner Channel se selecciona para `SQX142-AW-AI6 Keltner Fixture And Contract`, pero AI5 no anade patron draftable: Keltner mantiene 12 items semanticos saneados y `planning_only_not_draftable`, sin fixture, contrato AST, compilador ZIP ni roundtrip manual. `draftablePatterns` sigue limitado a `ema_cross`, `candle_atr_sequence` y `rsi_mean_reversion`; Keltner/Bollinger/ADX/Stochastic siguen plan-only.

## Entrega

- Version: `sqx142-ai-wizard-studio-v2`.
- Compiler phase: `sqx142-aw-ai4-rsi-mean-reversion-compiler-v1` on top of `sqx142-aw-ai3-universal-prompt-compiler-v1`; AI5 decision marker `sqx142-aw-ai5-compiler-candidate-decision-gate-v1`.
- Catalogo: `sqx-edge.ai-wizard-capability-catalog-v1`.
- AST: `sqx-edge.ai-wizard-strategy-ast-v1`.
- SQLite local: `.local/sqx142_ai_wizard/ai_wizard.sqlite`.
- Backend core: `backend/sqx-edge-tool/core/sqx142_ai_wizard.py`.
- API Flask local-only: `backend/sqx-edge-tool/api/server.py`.
- Overlay source: `integrations/sqx142/ai_wizard_overlay/sqx-edge-aiwizard.js` and `.css`.
- Tests: `backend/sqx-edge-tool/test_sqx142_ai_wizard_studio.py`, `tests/js/contracts/sqx142_aw_ai2_contracts.mjs`, `tests/js/contracts/sqx142_aw_ai3_contracts.mjs`.

## Subfases

- `AI2.0 Baseline`: AW-AI1 queda congelado como `sqx142-ai-wizard-v1`; overlay instalado previamente, manual roundtrip pendiente.
- `AI2.1 Capability Catalog`: extractor read-only allowlist para `wizard.xml`, `conditions.xml`, parameter sets, ejemplos `.sqx`, snippets/bloques, custom indicators metadata y BlockSettings repo. Devuelve conteos, hashes y referencias opacas, no rutas locales ni XML crudo.
- `AI2.2 Strategy AST`: contrato `sqx-edge.ai-wizard-strategy-ast-v1` con long/short entry/exit, operadores logicos, comparaciones, acciones, SL/TP/trailing/MM y referencias a catalogo.
- `AI2.3 Validator`: todo AST debe usar IDs existentes en catalogo y parametros dentro de tipo/rango/enum. Si falta soporte de compilador, se marca `blocked_not_draftable_yet`.
- `AI2.4 Session Studio`: sesiones, interacciones redactadas, revisiones, drafts y auditoria se guardan en SQLite local. No se persisten prompts raw ni respuestas raw de proveedor.
- `AI2.5 Draft Compiler`: genera `.sqx` solo para AST validado y compilable; los demas planes validos quedan como plan editable bloqueado con razon precisa.
- `AI2.6 Overlay UX`: historial, reabrir/forkear sesiones, catalog browser, chips de indicadores/operadores, editor de parametros y panel de bloqueos util.
- `AI2.7 Manual Roundtrip`: pendiente hasta SQX cerrado; requiere abrir draft en AlgoWizard y confirmar editabilidad.
- `AI3.0 Universal Prompt Compiler`: interprete local modelo -> AST con fallback seguro y compilador `candle_atr_sequence`; status `compiler_built_roundtrip_reported_catalog_expansion_active`.
- `AI4.0 RSI Mean-Reversion Compiler`: compilador `rsi_mean_reversion` para RSI puro con condiciones 30/70, direccion long/short/both y revision manual obligatoria; status `operator_manual_rsi_roundtrip_confirmed_ai4_closed`.
- `AI5.0 Compiler Candidate Decision Gate`: cerrado como `candidate_selected_keltner_requires_fixture_ai6`; Keltner seleccionada solo para fixture/contrato AI6, sin desbloquear Keltner/Bollinger/ADX/Stochastic por defecto.
- `AI6.0 Keltner Fixture And Contract`: siguiente gate local; capturar fixture public-safe, cerrar contrato AST y definir pruebas antes de cualquier compilador.

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

El Studio puede planificar cualquier estrategia expresable con el catalogo de AlgoWizard detectado, pero el draft `.sqx` solo se emite si el compilador tiene soporte probado para ese AST. AI3 mantiene compatibilidad conservadora con EMA cross y anade `candle_atr_sequence`; AI4 anade `rsi_mean_reversion` para RSI puro con `RSI(14) < 30` / `RSI(14) > 70`. AI5 no anade familia draftable: Keltner queda candidata AI6 pero sigue bloqueada. El resto de planes validos no probados siguen bloqueados con `blocked_not_draftable_yet`.

Bloqueos principales:

- `prompt_required`
- `prompt_not_public_safe`
- `blocked_full_editor_scope`
- `unknown_block`
- `unknown_operator`
- `param_out_of_range`
- `prompt_not_understood`
- `blocked_unsupported_candle_pattern`
- `blocked_unsupported_filter`
- `blocked_unsupported_compiler_family`
- `blocked_multi_family_compiler_not_ready`
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
- `node tests\js\contracts\sqx142_aw_ai3_contracts.mjs`
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

2026-06-04 after manual SQX close:

- install status: `installed`
- backup: `sqx142_ai_wizard_overlay_20260604_163808`
- overlay v2 instalado: confirmado
- assets activos: coinciden con la fuente repo v2
- SQX process count after install: `0`
- siguiente accion segura: abrir SQX manualmente y completar el roundtrip humano en AlgoWizard

2026-06-04 DRAFT1:

- reported symptom: AlgoWizard displayed `Not Found` after draft action
- likely cause: duplicated `/api` prefix in draft download link
- fix: `apiUrl()` resolves backend `/api/...` download URLs against Flask origin
- forbidden regression: `API_BASE + draft.downloadUrl`
- reinstall backup: `sqx142_ai_wizard_overlay_20260604_170156`
- status after patch: `installed_pending_manual_roundtrip`

2026-06-04 UX1:

- reported symptom: bot creation felt unintuitive and unfriendly
- fix scope: overlay source copy/order/states only, no backend/runtime contract change
- user-facing markers: `Crear bot SQX`, `Idea del bot`, `Crear plan`, `Generar .sqx`, `Duplicar`, `Modo guiado`
- blocker UX: `blockerLabel()` maps technical blocker codes to actionable Spanish text
- install status: `ux1_repo_ready_install_blocked_sqx_process_running`
- install blocker: `sqx_process_running`, `processCount=6`
- mutation status: no `install -Apply`, no SQX runtime launch from scripts, no `data.db`, no `user/projects`

2026-06-04 UX1 installed:

- install status: `installed`
- backup: `sqx142_ai_wizard_overlay_20260604_182545`
- active status: `ux1_installed_pending_manual_roundtrip`
- active hashes: JS/CSS match repo source
- active UX markers: `Crear bot SQX`, `Modo guiado`
- active safety markers: `apiUrl()`, `data-sqx-aiwizard-download`, no `API_BASE + draft.downloadUrl`
- SQX process count after install: `0`
- siguiente accion segura: abrir SQX manualmente y repetir el roundtrip humano en AlgoWizard con UX1

2026-06-04 Prompt Truthfulness:

- reported symptom: a Spanish candle/hammer/ATR prompt could drift into an unrelated generated bot
- fix: remove unsafe fallback to `EMA` when no supported block is detected
- recognized case: `SP500 -> US500`, `H1`, `long_only`, `Stop=100`, `TP=200`, candle sequence, hammer confirmation and ATR filter intent
- safe result: plan-only AST with `compiler.draftable=false`
- draft blockers: `blocked_unsupported_candle_pattern`, `blocked_unsupported_filter`, `blocked_not_draftable_yet`
- overlay behavior: `Generar .sqx` disabled unless `compiler.draftable=true`; visible message `Plan entendido, .sqx bloqueado`
- install backup: `sqx142_ai_wizard_overlay_20260604_190508`
- backend status: local backend restarted on `127.0.0.1:5050`
- HTTP probe: exact Spanish prompt returns `US500`, `H1`, `long_only`, `Stop=100`, `TP=200`, `draftable=false`, no `EMA`, no `BollingerBands`
- probe cleanup: redacted local probe session removed
- status: `prompt_truthfulness_installed_pending_manual_roundtrip`

2026-06-04 AI3 Universal Prompt Compiler:

- phase marker: `sqx142-aw-ai3-universal-prompt-compiler-v1`
- rule: `universal_prompt_intake_not_universal_sqx_generation`
- interpreter: local model -> AST through Flask when available, safe parser fallback
- privacy: `raw_prompt_persisted=false`, `raw_provider_response_persisted=false`
- compiler family: `candle_atr_sequence`
- safe draft: ZIP entries preserved, only `strategy_Portfolio.xml` patched
- status: `compiler_built_roundtrip_reported_catalog_expansion_active`

2026-06-04 AI4 RSI Mean-Reversion Compiler:

- operator evidence: AI3 Catalog Expansion roundtrip OK
- phase marker: `sqx142-aw-ai4-rsi-mean-reversion-compiler-v1`
- compiler family: `rsi_mean_reversion`
- conditions: long `RSI(14) < 30`, short `RSI(14) > 70`
- direction support: `long_only`, `short_only`, `both`
- safety: mixed RSI+Bollinger prompts blocked with `blocked_multi_family_compiler_not_ready`
- plan-only families preserved: Keltner, Bollinger, ADX, Stochastic
- draft rule: ZIP entries preserved, only `strategy_Portfolio.xml` patched, `manualReviewRequired=true`
- install: overlay backup `sqx142_ai_wizard_overlay_20260604_210522`
- HTTP probe: RSI draft OK; Keltner family understood and blocked with `blocked_not_draftable_yet`
- manual roundtrip: operator confirmed prompt RSI puro, `.sqx` draft, editable open/review, and Keltner/Bollinger/ADX/Stochastic remain plan-only
- status: `operator_manual_rsi_roundtrip_confirmed_ai4_closed`
- next local gate: `SQX142-AW-AI5 Compiler Candidate Decision Gate`

2026-06-04 AI5 Compiler Candidate Decision Gate:

- phase marker: `sqx142-aw-ai5-compiler-candidate-decision-gate-v1`
- status: `candidate_selected_keltner_requires_fixture_ai6`
- decision: Keltner Channel selected only for `SQX142-AW-AI6 Keltner Fixture And Contract`
- evidence: 12 sanitized Keltner semantic items; no fixture, AST contract, ZIP compiler or manual roundtrip yet
- unchanged draftable patterns: `ema_cross`, `candle_atr_sequence`, `rsi_mean_reversion`
- preserved plan-only families: Keltner, Bollinger, ADX, Stochastic
- next local gate: `SQX142-AW-AI6 Keltner Fixture And Contract`

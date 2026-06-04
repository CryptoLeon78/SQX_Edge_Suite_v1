# SQX142-AW-AI3 Universal Prompt Compiler

Estado: `compiler_built_roundtrip_reported_catalog_expansion_active`.

Marcador: `sqx142-aw-ai3-universal-prompt-compiler-v1`.

Catalog level-up: `sqx142-aw-ai3-expanded-catalog-v1`.

Estado posterior reportado por operador: `operator_manual_roundtrip_completed_catalog_level_up_active`.

AI3 convierte el AI Wizard en una entrada universal de prompts gobernada: el usuario puede escribir lenguaje natural libre, el backend local interpreta la intencion hacia un AST validado, y solo los compiladores de familia probada pueden emitir `.sqx`. La regla clave es `universal_prompt_intake_not_universal_sqx_generation`: se aceptan prompts amplios, pero no se promete generar cualquier estrategia si no existe compilador verificable.

## Alcance

- Interprete local modelo -> AST: usa Ollama local mediado por Flask cuando esta disponible; si no responde, vuelve al parser heuristico seguro.
- Catalogo: `allowlisted_catalog_only`; el AST solo puede referenciar IDs detectados en el catalogo sanitizado de AlgoWizard.
- Catalogo ampliado: `sqx142-aw-ai3-expanded-catalog-v1` combina bloques Wizard, condiciones de AlgoWizard y feature IDs observados en ejemplos `.sqx` como indice semantico public-safe.
- Compilador verificable inicial: `candle_atr_sequence`, para secuencias de velas rojas/verdes con confirmacion tipo martillo, entrada long en confirmacion y filtro ATR creciente.
- Draft `.sqx`: se emite solo con `compiler.draftable=true`, conserva las entradas del ZIP plantilla y parchea solo `strategy_Portfolio.xml`.
- Revision: todo draft queda `manualReviewRequired=true`; AlgoWizard debe abrirlo y revisarlo antes de cualquier validacion SQX.

## Contrato De Interpretacion

- `AI_WIZARD_INTERPRETER_SCHEMA` define la salida esperada del modelo local.
- El navegador nunca llama al proveedor: `no provider calls from browser`.
- La llamada al modelo es local-only, sin autostart forzado desde este flujo.
- Privacidad: `raw_prompt_persisted=false`, `raw_provider_response_persisted=false`, `external_api_called=false`.
- Si el modelo inventa bloques, devuelve JSON invalido o no esta disponible, el backend cae a parser seguro y no emite draft fuera de familias probadas.

## Familia Candle/ATR

La primera familia AI3 compila el caso real reportado por el operador:

- activo `SP500` normalizado a `US500`
- timeframe `H1`
- direccion `long_only`
- tres velas rojas previas
- vela verde con proxy conservador de martillo
- segunda vela verde de confirmacion
- filtro `ATR` creciente
- `Stop=100`, `TP=200`

El compilador no intenta detectar rentabilidad ni calidad trading. Solo traduce una estructura de AlgoWizard editable y trazable para revision manual.

## Catalogo Ampliado

AI3-CAT sube el nivel del Studio sin ampliar la superficie de generacion insegura:

- `semanticCatalog.items`: indice saneado de bloques, condiciones y features observadas.
- `semanticCatalog.families`: resumen de familias como Bollinger Bands, RSI, Stochastic, Keltner Channel, ADX, Directional Index, Momentum, Bar/Time y Orders Control cuando existen en `conditions.xml`.
- `examples.featureIds`: claves de `Item` observadas en ejemplos `.sqx`, sin XML crudo ni nombres de plantilla.
- `catalogRefs.semanticIds`: el AST puede registrar condiciones entendidas aunque no sean `blockIds` compilables.
- `compilerBoundary`: los semantic items son para interpretacion/planificacion; no vuelven draftable una familia sin compilador probado.

## Guardrails

- `compiler.draftable=true only for proven compiler families`.
- `unsupportedNaturalLanguageFallback=false`.
- `blocked_not_draftable_yet` para familias sin compilador.
- `blocked_unsupported_prompt_semantics` para peticiones fuera de alcance.
- `blocked_unsupported_compiler_family` si se pide emitir una familia no probada.
- No SQX runtime launch.
- No `run_project`, retests, optimizacion ni ejecucion de proyectos.
- No writes a `data.db`, `user/projects`, databanks ni settings vivos.
- No rutas locales, XML crudo, prompts raw, provider responses raw, licencias, tokens, claves ni URLs protegidas en API/UI/docs.
- No Full Editor completo, Java custom, engine plugin, internals 144, licencia, activacion ni bypass.
- No promesas de rentabilidad, riesgo cero ni validez operativa sin revision manual.

## Verificacion

- `python -m pytest backend\sqx-edge-tool\test_sqx142_ai_wizard_studio.py -q`
- `python -m pytest backend\sqx-edge-tool\test_sqx142_ai_wizard.py -q`
- `node tests\js\contracts\sqx142_aw_ai3_contracts.mjs`
- `node tests\js\contracts\sqx142_aw_ai2_contracts.mjs`
- `python -m pytest backend\sqx-edge-tool\test_docs_state_consistency.py -q`

## Log Public-Safe

2026-06-04:

- fase: `SQX142-AW-AI3 Universal Prompt Compiler`
- estado inicial de construccion: `built_pending_install_and_manual_roundtrip`
- estado actual: `compiler_built_roundtrip_reported_catalog_expansion_active`
- implementado: modelo local -> AST con fallback seguro
- implementado: compilador `candle_atr_sequence`
- implementado: draft `.sqx` trazable con ZIP entries preservadas
- implementado: tests para prompt espanol real y modelo local fake
- verificado: backend local reiniciado y catalogo HTTP devuelve fase AI3 con `ema_cross,candle_atr_sequence`
- pendiente: repetir roundtrip humano especifico del catalogo expandido si se quiere validar nuevas familias en UI real
- limites preservados: no SQX runtime launch, no `data.db`, no `user/projects`, no databanks, no licencia/activacion/bypass

2026-06-04 Catalog Expansion:

- operador: roundtrip manual AI3 realizado
- nuevo marcador: `sqx142-aw-ai3-expanded-catalog-v1`
- catalogo: semantic index sobre Wizard blocks, AlgoWizard conditions y observed example features
- instalado: overlay con backup `sqx142_ai_wizard_overlay_20260604_200549`
- verificado: backend local recargado y catalogo HTTP con `semanticItems=165`, `semanticFamilies=17`, `exampleFeatureIds=49`, `semanticAliases=1286`
- UI: `Catalogo AlgoWizard ampliado`
- AST: `catalogRefs.semanticIds`
- limite: expanded catalog no implica universal `.sqx` generation

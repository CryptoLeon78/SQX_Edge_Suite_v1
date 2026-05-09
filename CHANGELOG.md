# Changelog

## 2026-05-09 - M82 tiny controlled traffic expansion step

- Adds a guarded internal tool and config for one tiny reversible traffic expansion step after M81 approval.
- Keeps evidence redacted: channel, counts, owner and next review only; no buyer identity, checkout payloads or license files.
- Extends portable packaging exclusions, release checklist, public/private commercial traceability and static tests.

## 2026-05-09 - R47 controlled commercial release candidate

- Regenerates the portable ZIP after the Strategy Builder buyer-session support phases.
- Verifies the refreshed package with frontend contracts, full Python suite, `git diff --check`, distribution audit and clean extracted portable API health.
- Records the current candidate as controlled commercial delivery only: demos, assisted early access and manual first-buyer handoff, not mass public launch.
- Publishes local ZIP traceability: `SQX_Edge_Tool_Portable_20260509_102131.zip`, SHA256 `18EC98981D8B52535E1FE26EA47876588FA2EB8321DD2A9706CBD30B6A0B7E5D`.

## 2026-05-08 - R45 controlled publication plan

- Adds a public-safe controlled publication plan for the verified portable ZIP without publishing a GitHub Release.
- Records the release candidate in `product_manifest.json` as `prepared_not_published` with tag draft `v0.2.0-r45`.
- Documents release notes, pre-publication gate command, post-publication record command, rollback steps and no-sensitive-data boundary.
- Adds static coverage for the R45 plan and verified ZIP traceability.

## 2026-05-08 - R44/A63 portable after real MTF GO

- Regenerates the portable ZIP after the real A56 multi-timeframe GO and validates it from a clean extracted folder.
- Adds broad `analysis_output/` exclusion plus explicit `real_mtf_pipeline_run` guards to package, audit, release checklist, product manifest and tests.
- Verifies the release with JS contracts, full Python suite, `git diff --check`, distribution audit and portable API health.
- Publishes local ZIP traceability: `SQX_Edge_Tool_Portable_20260508_201652.zip`, SHA256 `2725D2FC7CB9FD6E05AFDF1C7E20772B629BFBE8BE98532D4F5622A08628116E`.

## 2026-05-08 - A62 recent-bars OHLC download mode

- Adds `--recent-bars` to the MT5/Dukascopy downloader, using `copy_rates_from_pos` for controlled recent OHLC acquisition when fixed historical ranges return no data.
- Aligns the MT5 symbol map with the product manifest universe by using `USDMXN` and `USDZAR` instead of the external-folder draft `AUDCHF` and `NZDCHF`.
- Downloads 33 assets x 4 timeframes from local Dukascopy MT5 and validates the resulting OHLC folder through A56 with GO across A55/A53/A54.

## 2026-05-08 - A61 MT5 IPC diagnostic

- Adds `mt5_ipc_diagnostic.py` as an internal operator diagnostic for MT5 Python IPC readiness before full OHLC download.
- Captures Python/MetaTrader5 versions, terminal process state and configured/active/portable initialization variants into JSON and Markdown evidence.
- Keeps the diagnostic and generated evidence excluded from portable buyer builds, distribution audit and release checklist.
- Records MT5 IPC as GO after active-terminal initialization succeeds; remaining work moves to OHLC retrieval mode and universe alignment.

## 2026-05-08 - A60 MT5 active-terminal retry mode

- Adds `--use-active-terminal` and `--initialize-timeout-ms` to the internal MT5/Dukascopy downloader so the operator can connect to an already-open terminal without forcing the configured executable path.
- Confirms Dukascopy MT5 is open and responsive locally, but records another controlled NO_GO because the Python IPC bridge still returns timeout.
- Adds `docs/A60_MT5_ACTIVE_TERMINAL_MODE.md` with the exact retry command and the remaining manual MT5 checks before full OHLC download.

## 2026-05-08 - A59 local MT5 real-data validation smoke

- Runs the first local A58 smoke against Dukascopy MT5 for `EURUSD/H1`.
- Confirms the terminal path and `MetaTrader5` dependency are present, but records a NO_GO because MT5 returned IPC timeout during initialization.
- Adds `docs/A59_REAL_DATA_VALIDATION.md` with exact rerun, full download and A56 validation commands before any MTF evidence promotion.

## 2026-05-08 - A58 internal MT5/Dukascopy OHLC download gate

- Adds `dukas_mt5_ohlc_download.py` as an operator-only, config-driven downloader for MT5/Dukascopy OHLC CSV files feeding A55/A56 real-data validation.
- Adds coverage JSON/Markdown/CSV output, dry-run support and tests with a fake MT5 module so CI does not require MetaTrader5.
- Excludes the downloader, config and generated OHLC/coverage data from portable buyer packaging, distribution audit, release checklist and product manifest.
- Updates roadmap/governance notes and records Strategy Builder as a future "only one platform" commercial hook, separate from this data-acquisition phase.

## 2026-05-08 - A57 read-only MTF evidence UI

- Anade `core/mtf_evidence.py` y `/api/mtf/evidence` para resumir la salida A56 sin rutas completas ni payloads crudos.
- Incorpora un panel `MTF Evidence` en Inicio y actualiza la franja de `SQX Priority` solo cuando existe evidencia A56 GO.
- Mantiene el dashboard bloqueado/pendiente si A56 devuelve NO_GO, falta el reporte o la API local no esta disponible.

## 2026-05-08 - A56 real MTF pipeline run

- Anade `real_mtf_pipeline_run.py` para orquestar A55 -> A53 -> A54 desde CSV OHLC reales hasta artefactos del Plan Quality Advisor.
- Devuelve GO solo si el builder genera metricas, el intake valida la fuente y los artefactos guardados se crean correctamente.
- Mantiene salida NO_GO trazable cuando faltan CSV o cobertura, sin sintetizar datos ni tocar dashboard.

## 2026-05-08 - A55 OHLC metric builder

- Anade `ohlc_metric_builder.py` para generar `asset_metrics[_TF].json` desde CSV OHLC revisables aportados por el operador.
- Cubre metricas requeridas por el scorer multi-timeframe: ADX, eficiencia, SMA persistence, RSI edge, ATR, vol-of-vol, Hurst distance, OU half-life, kurtosis, VWAP y round bounce.
- Mantiene la regla de no sintetizar timeframes y rechaza archivos con barras insuficientes.

## 2026-05-08 - A54 guarded multi-timeframe plan artifacts

- Anade `multi_timeframe_plan_artifacts.py` para conectar A53 con `Plan Quality Advisor` solo cuando el intake multi-timeframe devuelve GO.
- Genera reportes A53/A54 trazables y bloquea la salida MTF cuando faltan M30/M15/H4 reales.
- Cubre rutas GO/NO-GO con tests sin modificar dashboard ni exponer evidencia parcial en UI.

## 2026-05-08 - A53 multi-timeframe source intake

- Anade `multi_timeframe_source_intake.py` y `multi_timeframe_source_policy.json` para preparar y validar una carpeta real de metricas H1/M30/M15/H4.
- Permite reutilizar el H1 first-party de A52, pero bloquea M15/M30/H4 si faltan archivos reales.
- Deja un flujo GO/NO-GO trazable antes de conectar evidencia multi-timeframe al advisor o a la UI.

## 2026-05-08 - A52 first-party H1 metric source

- Anade `first_party_metric_source.py` para convertir `scores-data.js` en `asset_metrics.json` H1 con manifiesto de procedencia y hashes.
- Ajusta scorer/gate para aceptar `hurst_dist` precomputado del dashboard sin inventar un `hurst` bruto.
- Valida el bundle generado con el gate A51 y deja explicitado que M15/M30/H4 no se sintetizan.

## 2026-05-08 - A51 multi-timeframe metric gate

- Anade `multi_timeframe_metric_gate.py` para validar carpetas `asset_metrics[_TF].json` antes de usarlas como evidencia propia.
- Comprueba archivos por TF, cobertura de activos, completitud de metricas requeridas, activos desconocidos, compatibilidad con el scorer y SHA256.
- Mantiene la disciplina de no descargar datos ni modificar scores del dashboard desde el gate.

## 2026-05-08 - A50 multi-timeframe plan review

- Conecta el consenso multi-timeframe de `multi_timeframe_scoring.py` al `Plan Quality Advisor` como evidencia opcional.
- Mantiene la recomendacion ordenada por baseline H1 para no sustituir automaticamente el plan con metricas no verificadas.
- Anade resumen MTF, cobertura, consenso, mejor TF y assessment por mining cuando existe `asset_metrics[_TF].json`.

## 2026-05-08 - A49 controlled multi-timeframe scoring

- Anade `multi_timeframe_scoring.py` como herramienta backend aislada para convertir `asset_metrics[_TF].json` en scores por timeframe y consenso ponderado.
- Mantiene el flujo seguro: no descarga datos, no inyecta HTML y no cambia UI; solo consume metricas ya preparadas.
- Cubre el contrato con fixtures H1/M15/M30 y salida Markdown/JSON para operador.

## 2026-05-08 - A48 HTML value recovery

- Recupera valor del HTML comparado sin reintroducir los tabs eliminados `Top Picks` ni `Matriz Completa`.
- Anade controles nativos de backup/restauracion de estado local contra los endpoints `/api/state/*`, limitados a claves no sensibles.
- Anade resumen dinamico `Plan v2` en Workflow y una preparacion visual bloqueada para Priority multi-TF, pendiente de motor de scoring dedicado.
- Actualiza arquitectura, contratos JS y tests estaticos para el nuevo modulo `state-backup.js`.

## 2026-05-08 - A47 Jose repo value extraction

- Compara el repo `jlivanmaseda-maker/sqx-edge-pipeline` con nuestra arquitectura actual.
- Integra un `Plan Quality Advisor` propio para revisar el plan de minings contra scores objetivos y proponer alternativas diversificadas.
- Documenta mejoras aprovechables, duplicados ya absorbidos y fases futuras para scoring multi-timeframe.

## 2026-05-08 - R42 portable release candidate refresh

- Regenera el ZIP portable final tras V9 con `SQX_Edge_Tool_Portable_20260508_164956.zip`.
- Verifica contratos frontend, suite Python, `git diff --check`, auditoria de distribucion y arranque del API portable extraido.
- Publica trazabilidad local con SHA256 `92BEF393D5EF4D5B32FB0FBC9A11A04BE30E648B4E0D51E70AA0D5F8A3C73534`.

## 2026-05-08 - V9 SQX Views import preview

- Anade preview visual al importar packs JSON de presets en `SQX Views`.
- Muestra presets entrantes, metricas, columnas estimadas, anos, orden y si reemplaza un preset local.
- Refuerza contratos JS, tests estaticos y E2E para cubrir el preview antes de la fusion local.

## 2026-05-08 - PG6 Project Generator import preview

- Anade preview visual al importar packs JSON de presets custom en `Project Generator`.
- Muestra presets entrantes, asset, timeframe, direccion, capa y si el preset reemplaza uno local.
- Refuerza contratos JS, tests estaticos y E2E para cubrir el preview antes de la fusion local.

## 2026-05-08 - V8 SQX Views asset and validation workflow packs

- Anade packs de `SQX Views` por familia de activo y flujo de validacion.
- Incluye Free Core Validation, Asset Family Review, Validation Screen Flow y Audit Export Flow.
- Permite cargar la primera vista del flujo, guardar el pack completo como presets locales o exportarlo como JSON portable.
- Refuerza contratos JS, tests estaticos y E2E para cubrir los nuevos packs operativos.

## 2026-05-08 - PG5 Project Generator richer custom profile families

- Amplia `Project Generator` con ocho perfiles custom starter y guia de uso por perfil.
- Anade familias por objetivo: comprador inicial, validacion intradia, revision de riesgo y muestra Pro completa.
- Permite cargar el primer perfil de una familia, guardar el pack completo como presets locales o exportarlo como JSON portable.
- Refuerza contratos JS, tests estaticos y E2E para cubrir los nuevos packs de familias.

## 2026-05-08 - V7 SQX Views buyer profile packs

- Anade packs por perfil en `SQX Views`: evaluacion Free, Setup Assist Pro, comprador centrado en riesgo y entrega de auditoria.
- Permite cargar la primera vista del pack, guardar todas sus vistas como presets propios y exportar cada pack como JSON portable.
- Refuerza contratos JS, tests estaticos y E2E para cubrir render, guardado y contrato de exportacion de packs por perfil.

## 2026-05-08 - R41 portable ZIP after PG4

- Regenera el ZIP portable tras los perfiles starter de `Custom libre`.
- Ejecuta release checklist completo: contratos JS, pytest, `git diff --check`, audit distribution y prueba de API desde ZIP extraido.
- Verifica flujo de usuario basico con `START_SQX_EDGE.bat`, `/api/health`, marcador PG4 en dashboard extraido y `STOP_SQX_EDGE.bat`.
- Publica trazabilidad del ZIP `SQX_Edge_Tool_Portable_20260508_075208.zip` con SHA256 `CCB398057E5DEC6AC5AE2993E58E8DCEDBDB0686DD09539E30F9017D54F3A34D`.

## 2026-05-08 - PG4 starter custom preset profiles

- Anade perfiles starter en `Custom libre` para arrancar proyectos Forex, indices y oro sin depender del plan mining.
- Permite cargar cada starter en el formulario, guardarlo como preset local y exportar el pack starter como JSON.
- Refuerza contratos JS, tests estaticos y E2E para cubrir render, eventos y contrato portable del pack starter.

## 2026-05-08 - R40 portable ZIP after V6/PG3

- Regenera el ZIP portable final tras los ejemplos buyer-ready de SQX Views y los packs JSON de `Custom libre`.
- Ejecuta release checklist completo: contratos JS, pytest, `git diff --check`, audit distribution y prueba de API desde ZIP extraido.
- Publica trazabilidad del nuevo ZIP `SQX_Edge_Tool_Portable_20260508_004141.zip` con SHA256 `EB4031FE3A6035DA0F04D569A2963B120CCA6957C5EB4A7F994A078F56556E4C`.

## 2026-05-08 - PG3 Custom libre portable preset packs

- Anade exportacion/importacion JSON para presets de `Custom libre` en Project Generator.
- Fusiona packs importados con presets locales sin duplicar IDs y mantiene validacion de asset/timeframe.
- Refuerza contratos JS, tests estaticos y E2E para cubrir portabilidad de presets custom.

## 2026-05-08 - V6 SQX Views buyer-ready examples

- Anade ejemplos buyer-ready en `SQX Views` para primera revision, robustez, riesgo y auditoria completa.
- Permite cargar cada ejemplo, guardarlo como preset propio y exportar el pack de ejemplos en JSON.
- Activa los contratos JS de SQX Views en la suite principal y refuerza static/E2E para cubrir los ejemplos.

## 2026-05-08 - V5 SQX View Creator integration closeout

- Cierra la integracion del prototipo anual de SQX View Creator dentro del tab nativo `SQX Views`.
- Archiva la carpeta staging `tab a integrar como nueva funcion/` en backup previo y la elimina del workspace local.
- Actualiza trazabilidad de roadmap, gobernanza y arquitectura para dejar el siguiente paso real en V6 o PG3.

## 2026-05-08 - PG2 Custom libre reusable presets

- Anade presets locales para guardar, cargar y eliminar configuraciones de `Custom libre`.
- Mantiene los presets en `localStorage` bajo `sqx_pg_custom_presets_v1` sin tocar backend ni rutas personales.
- Refuerza contratos JS, tests estaticos y E2E para cubrir el flujo de presets custom.

## 2026-05-08 - PG1 Custom libre fuera del plan

- Anade un flujo `Custom libre` en Project Generator para crear `.cfx` sin depender de un mining del plan.
- Expone `/api/generate-custom` con asset, timeframe, direccion, blocksetting, nombre y capa propios.
- Mantiene intacta la generacion masiva por plan y refuerza contratos JS, API y E2E.

## 2026-05-07 - V4 SQX View Creator workflow handoff

- Conecta Workflow y Estrategias con SQX Views mediante handoffs con preset y nombre precargados.
- Mantiene la navegacion y preparacion de vistas dentro de `view-creator.js` para evitar enlaces sueltos.
- Refuerza contratos JS y smoke E2E para cubrir handoff desde ambas zonas operativas.

## 2026-05-07 - V3 SQX View Creator preset packs

- Anade exportacion/importacion JSON para presets propios de SQX Views.
- Valida metricas conocidas al importar y fusiona packs sin duplicar presets existentes.
- Refuerza contratos JS y E2E para cubrir handoff portable entre instalaciones.

## 2026-05-07 - V2 SQX View Creator preset persistence

- Anade presets propios guardados en `localStorage` para SQX Views.
- Permite guardar, cargar y eliminar combinaciones de metricas sin depender de archivos externos.
- Refuerza contratos JS y E2E para cubrir persistencia del View Creator.

## 2026-05-07 - V1 native SQX View Creator

- Integra `SQX Views` como tab nativo para generar vistas `.vw` anuales de StrategyQuant X.
- Migra el prototipo Tkinter a un flujo portable de navegador con preset EGT Core, preview XML y descarga directa.
- Anade contratos JS, cobertura estatica, E2E visual y documentacion de arquitectura.

## 2026-05-07 - M81 controlled traffic expansion review

- Anade gate interno para revisar si procede una ampliacion minima y reversible de trafico.
- Actualiza estado comercial a `controlled_traffic_expansion_review_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M81.

## 2026-05-07 - M80 manual publication monitor

- Anade gate interno para monitorizar la publicacion manual limitada antes de ampliar trafico.
- Actualiza estado comercial a `manual_publication_monitor_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M80.

## 2026-05-07 - M79 manual limited publication record

- Anade gate interno para registrar una publicacion manual limitada despues de M78.
- Actualiza estado comercial a `manual_limited_publication_record_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M79.

## 2026-05-07 - M78 operator publication review

- Anade gate interno para revisar manualmente el borrador limitado antes de cualquier publicacion.
- Actualiza estado comercial a `operator_publication_review_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M78.

## 2026-05-07 - M77 limited publication draft

- Anade gate interno para preparar un borrador de publicacion limitada despues de M76.
- Actualiza estado comercial a `limited_publication_draft_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M77.

## 2026-05-07 - M76 controlled publication gate

- Anade gate interno para preparar publicacion controlada solo despues de la revision privada M75.
- Actualiza estado comercial a `controlled_publication_gate_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M76.

## 2026-05-07 - M75 private asset review

- Anade gate interno para revisar privadamente el asset comprador-facing antes de publicacion o trafico.
- Actualiza estado comercial a `private_asset_review_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M75.

## 2026-05-07 - M74 next buyer-facing asset

- Anade gate interno para preparar un unico asset comprador-facing para review privado tras M73.
- Actualiza estado comercial a `next_buyer_facing_asset_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M74.

## 2026-05-07 - M73 controlled distribution review

- Anade gate interno para revisar evidencia M72 y decidir repetir, corregir, pausar o preparar el siguiente asset buyer-facing.
- Actualiza estado comercial a `controlled_distribution_review_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M73.

## 2026-05-07 - M72 controlled distribution step

- Anade gate interno para ejecutar la decision M71 como paso de distribucion minimo, reversible y sin datos personales.
- Actualiza estado comercial a `controlled_distribution_step_ready`.
- Mantiene la guia operativa completa en el repo privado y deja punteros publicos para M72.

## 2026-05-07 - M71 next controlled buyer outcome

- Anade gate interno para registrar el resultado del siguiente comprador controlado sin datos personales, payloads de checkout ni licencias.
- Actualiza estado comercial a `next_controlled_buyer_outcome_ready`.
- Mantiene el documento operativo completo en el repo privado y deja punteros publicos para M71.

## 2026-05-07 - Public commercial redaction

- Redacta roadmap comercial, runbooks de venta y packs Pro buyer/template en el repo publico como punteros de trazabilidad.
- Mantiene la copia completa en `CryptoLeon78/sqx-edge-commercial-private` con commit base `ed79719 Initial private commercial export`.
- Anade `docs/PUBLIC_COMMERCIAL_POINTERS.md` y actualiza gobernanza/manifiesto/tests para la frontera publico/privado.

## 2026-05-07 - Private commercial repository published

- Instala GitHub CLI en modo portable local bajo `private-commercial/tools/gh`.
- Crea el repo privado `CryptoLeon78/sqx-edge-commercial-private`.
- Sube el export comercial privado con commit `ed79719 Initial private commercial export`.
- Verifica con GitHub CLI que el repositorio remoto es privado.

## 2026-05-07 - Local private commercial repository prepared

- Inicializa el export comercial privado como repositorio git local ignorado por el repo publico.
- Anade `.gitignore`, `PUBLISH_TO_GITHUB.md` y `SECURITY.md` dentro del export privado.
- Registra el commit privado local `ed79719 Initial private commercial export` como base para subir al repo privado.
- Mantiene pendiente la creacion del remoto privado y la posterior redaccion de docs publicos sensibles.

## 2026-05-07 - Private commercial docs split prepared

- Anade `private_commercial_split.py` para exportar docs comerciales sensibles a un staging privado ignorado por git.
- Anade plan de split con indice SHA256, destino privado recomendado y regla de no borrar fuentes publicas hasta verificar copia privada.
- Actualiza exclusiones de portable, audit, release checklist y manifest para no enviar la herramienta interna al usuario final.
- Mantiene trazabilidad publica mediante manifiesto y tests sin mover todavia el historial expuesto.

## 2026-05-07 - CI baseline and private commercial docs boundary

- Anade `requirements-dev.txt` para separar runtime de dependencias de test/CI.
- Anade GitHub Actions para compilar Python, ejecutar pytest, contratos JS y `git diff --check`.
- Define la frontera de documentos comerciales privados con manifiesto de migracion y staging local ignorado.
- Mantiene el estado comercial vigente en `next_controlled_buyer_readiness_ready`.

## 2026-05-07 - Next controlled buyer readiness

- Anade M70 con check formal antes de compartir otro enlace privado con un comprador controlado.
- Anade `next_controlled_buyer_readiness.py` para validar slot unico, checkout, licencia, entrega, soporte, follow-up, safe claims y regla de pausa.
- Actualiza estado comercial a `next_controlled_buyer_readiness_ready`.
- Mantiene evidencia de readiness y herramienta interna fuera del ZIP portable.

## 2026-05-07 - Post-sale micro updates

- Anade M69 con micro-mejoras aplicadas a onboarding, activacion, soporte y copy publico.
- Anade `post_sale_micro_updates.py` para validar marcadores buyer-facing y readiness del siguiente comprador controlado.
- Actualiza estado comercial a `post_sale_micro_updates_ready`.
- Mantiene evidencia de readiness y herramienta interna fuera del ZIP portable.

## 2026-05-07 - Post-sale improvement loop

- Anade M68 con bucle de mejora post-venta para onboarding, soporte y copy publico.
- Anade `post_sale_improvement_loop.py` para validar acciones agregadas desde el primer comprador controlado.
- Actualiza estado comercial a `post_sale_improvement_loop_ready`.
- Mantiene evidencia post-venta y herramienta interna fuera del ZIP portable.

## 2026-05-07 - First controlled buyer log

- Anade M67 con registro operativo del primer comprador controlado y revision post-venta ligera.
- Anade `first_controlled_buyer_log.py` para validar compra, entrega, activacion, soporte, feedback y decision.
- Actualiza estado comercial a `first_controlled_buyer_log_ready`.
- Mantiene evidencia de primera venta controlada fuera del ZIP portable.

## 2026-05-07 - Public buyer page cadence

- Anade M66 con checklist de pagina publica de comprador y cadencia de primera venta.
- Anade `public_buyer_page_cadence.py` para validar copy, pasos de comprador, soporte, claims y rollback.
- Actualiza estado comercial a `public_buyer_page_cadence_ready`.
- Mantiene evidencia de pagina/cadencia fuera del ZIP portable.

## 2026-05-07 - Buyer-ready checkout closeout

- Anade M65 con cierre buyer-ready para checkout, release, licencia, soporte y rollback.
- Anade `buyer_ready_checkout_closeout.py` para validar una ruta de comprador basico antes de ventas controladas.
- Actualiza estado comercial a `buyer_ready_checkout_release_closeout_ready`.
- Mantiene evidencia interna y herramientas comerciales fuera del ZIP portable.

## 2026-05-07 - Template Pack 2 feedback cohort

- Anade M64 con revision de cohorte temprana de Template Pack 2.
- Anade `template_pack_2_feedback_cohort.py` para validar feedback agregado, soporte, refunds y decision de roadmap.
- Actualiza estado comercial a `template_pack_2_feedback_cohort_ready`.
- Mantiene evidencia agregada/redactada y fuera del ZIP portable.

## 2026-05-07 - Template Pack 2 sales register

- Anade M63 con registro interno de ventas de Template Pack 2.
- Anade `template_pack_2_sales_register.py` para validar venta, entrega, soporte, refunds, fallos y decision de escala.
- Actualiza estado comercial a `template_pack_2_sales_register_ready`.
- Mantiene evidencia redactada y fuera del ZIP portable.

## 2026-05-07 - Template Pack 2 post-purchase handoff

- Anade M62 con handoff post-compra de Template Pack 2.
- Anade `template_pack_2_handoff.py` para validar entrega, soporte, primer valor y decision de escala/pausa.
- Actualiza estado comercial a `template_pack_2_handoff_ready`.
- Mantiene evidencia redactada y fuera del ZIP portable.

## 2026-05-07 - Template Pack 2 purchase drill

- Anade M61 con compra controlada de Template Pack 2.
- Anade `template_pack_2_purchase_drill.py` para validar pedido, pago, entrega, soporte y refund/pause.
- Actualiza estado comercial a `template_pack_2_purchase_drill_ready`.
- Mantiene evidencia redactada y fuera del ZIP portable.

## 2026-05-07 - Template Pack 2 controlled publication

- Anade M60 con puerta de publicacion controlada para Template Pack 2.
- Anade `template_pack_2_publication.py` para validar checkout URL, variant ID, soporte, rollback y purchase drill.
- Actualiza estado comercial a `template_pack_2_controlled_publication_ready`.
- Mantiene la escritura de valores reales detras de `--apply`.

## 2026-05-07 - Template Pack 2 offer pack

- Anade M59 con oferta controlada para Template Pack 2.
- Anade `template_pack_2_offer_pack.py` para validar copy, FAQ, checkout draft, macros, soporte y safe claims.
- Actualiza estado comercial a `template_pack_2_offer_pack_ready`.
- Mantiene checkout en modo draft hasta completar URL, variant ID y soporte reales.

## 2026-05-07 - Template Pack 2 assets

- Anade M58 con recursos iniciales reales para Template Pack 2.
- Anade `template_pack_2_assets.py` para validar perfiles, presets CSV, soporte, safe claims y empaquetado add-on separado.
- Actualiza estado comercial a `template_pack_2_assets_ready`.
- Mantiene Template Pack 2 fuera del ZIP portable principal y listo como add-on separado.

## 2026-05-07 - Template Pack 2 specs

- Anade M57 con especificacion inicial de Template Pack 2 derivada del action plan M56.
- Anade `template_pack_2_specs.py` para validar alcance, familias de activos, presets, soporte, entrega, claims y siguiente fase.
- Actualiza estado comercial a `template_pack_2_specs_ready`.
- Mantiene Pack 2 como especificacion trazable antes de crear recursos comerciales.

## 2026-05-07 - Template Pack 1 action plan

- Anade M56 con plan accionable para iterar oferta, ampliar trafico, preparar Template Pack 2 o pausar ventas.
- Anade `template_pack_1_action_plan.py` para validar owner, prioridad, acciones, soporte, claims, distribucion y siguiente fase.
- Actualiza estado comercial a `template_pack_1_action_plan_ready`.
- Mantiene el plan como evidencia redactada sin mensajes crudos de comprador ni payloads de proveedor.

## 2026-05-07 - Template Pack 1 feedback cohort

- Anade M55 con revision de cohorte y feedback real para Template Pack 1.
- Anade `template_pack_1_feedback_cohort.py` para validar compradores, feedback, bugs, friccion, soporte, refunds y decision de roadmap.
- Actualiza estado comercial a `template_pack_1_feedback_cohort_ready`.
- Bloquea escalado o Template Pack 2 sin senales positivas, soporte controlado y claims seguros.

## 2026-05-07 - Template Pack 1 sales register

- Anade M54 con registro interno de ventas add-on para Template Pack 1.
- Anade `template_pack_1_sales_register.py` para validar venta, entrega, soporte, refunds, fulfillment y decision de escala.
- Actualiza estado comercial a `template_pack_1_sales_register_ready`.
- Mantiene referencia de comprador redactada, evidencia local fuera del ZIP base y decision responsable antes de abrir mas trafico.

## 2026-05-07 - Template Pack 1 handoff

- Anade M53 con gate de handoff post-compra para Template Pack 1.
- Anade `template_pack_1_handoff.py` para validar entrega, soporte inicial, primer valor y decision de escalar o pausar.
- Actualiza estado comercial a `template_pack_1_handoff_ready`.
- Mantiene datos de comprador redactados y evidencia local fuera del ZIP base.

## 2026-05-07 - Template Pack 1 purchase drill

- Anade M52 con gate de compra controlada para Template Pack 1.
- Anade `template_pack_1_purchase_drill.py` para validar pedido, pago, entrega separada, soporte y rollback.
- Actualiza estado comercial a `template_pack_1_purchase_drill_ready`.
- Mantiene evidencia de comprador redactada y el gate fuera del ZIP base.

## 2026-05-07 - Governance lookup discipline

- Anade G2 como regla operativa: consultar Project Governance o matriz de agentes antes de cada fase/mensaje de trabajo.
- Actualiza Project Governance, roadmap, ADR y README para reflejar ownership activo y checks esperados.
- Refuerza el contrato estatico de gobernanza.

## 2026-05-07 - Template Pack 1 live checkout gate

- Anade M51 con gate de publicacion controlada para Template Pack 1.
- Anade `template_pack_1_publication.py` para validar URL real, provider variant ID, email de soporte y rollback.
- Actualiza estado comercial a `template_pack_1_live_checkout_gate_ready`.
- Mantiene la publicacion bloqueada hasta recibir valores reales del proveedor.

## 2026-05-07 - Template Pack 1 public offer

- Anade M50 con oferta publica draft de Template Pack 1, FAQ, checkout wiring y macros de entrega/soporte.
- Anade `template_pack_1_offer.py` para validar copy, plan, precio, draft de checkout y claims seguros.
- Actualiza estado comercial a `template_pack_1_public_offer_ready`.
- Mantiene el add-on fuera del ZIP base y listo para conectar checkout real.

## 2026-05-07 - Template Pack 1 delivery

- Anade Template Pack 1 como add-on separado con perfiles JSON, CSV resumen, checklist y limites de soporte.
- Anade `template_pack_1_delivery.py` para validar y empaquetar el add-on.
- Actualiza estado comercial a `template_pack_1_delivery_ready`.
- Refuerza empaquetado para excluir el add-on del ZIP base y generar entrega separada.

## 2026-05-07 - Buyer onboarding support gate

- Anade recursos M48 de onboarding para comprador Pro basico.
- Anade `buyer_onboarding_support_gate.py` para validar compra, ZIP, licencia, instrucciones, FAQ, soporte y claims seguros.
- Actualiza estado comercial a `buyer_onboarding_support_gate_ready`.
- Refuerza empaquetado para excluir la herramienta interna y evidencia local.

## 2026-05-07 - Pro buyer data and template pack

- Anade `resources/pro-buyer-pack` con universo de activos, CSV importable y plantillas de activacion, soporte y primer valor.
- Anade `pro_buyer_pack.py` para validar el pack antes de publicar un ZIP comercial.
- Actualiza estado comercial a `pro_buyer_pack_ready`.
- Refuerza empaquetado para excluir la herramienta interna y evidencia local.

## 2026-05-07 - Commercial customer cockpit

- Anade endpoint read-only `GET /api/customer-cockpit`.
- Anade agregador redactado `customer_cockpit.py` para evidencia de customer success.
- Anade panel `Customer Success` en Inicio con clientes, renovaciones, tickets y oportunidades.
- Actualiza estado comercial a `customer_cockpit_ready`.

## 2026-05-07 - Specialist agent governance

- Anade `docs/PROJECT_GOVERNANCE.md` con agentes especializados, ownership, namespaces de fase y criterios de entrada M46.
- Anade ADR-0001 para registrar el modelo de gobernanza por agentes.
- Refuerza `.gitignore` para excluir `config/license.json` local.
- Actualiza roadmap y README con la baseline `G1`.

## 2026-05-07 - Customer success renewal loop

- Anade `customer_success_renewal.py` para revisar onboarding, activacion, soporte, renovacion y expansion responsable.
- Bloquea decisiones sin cliente, owner, activacion confirmada, soporte triado, notas de exito y claims seguros.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/customer_success_renewal`.
- Actualiza manifiesto a `customer_success_renewal_ready`.

## 2026-05-07 - Status and roadmap refresh

- Actualiza el estado visible del proyecto hasta M44 `hotfix_rollback_release_ready`.
- Registra el ultimo ZIP portable verificado y su SHA256 en README y roadmaps.
- Marca M45 como siguiente paso recomendado: customer success y renewal loop.
- Refresca el roadmap publico para reflejar el estado comercial real sin promesas financieras.

## 2026-05-06 - Launch assets kit

- Anade `launch_assets_kit.py` para validar ZIP, SHA256, capturas, copy, README comercial y release draft.
- Bloquea publicacion sin capturas desktop/mobile, support macro o checklist de publicacion.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/launch_assets_kit`.
- Actualiza manifiesto a `launch_assets_kit_ready`.

## 2026-05-06 - Public offer pack

- Anade `public_offer_pack.py` para validar copy, FAQ, release notes, buyer steps y pagina publica.
- Bloquea claims financieros prohibidos y oferta publica incompleta.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/public_offer_pack`.
- Actualiza manifiesto a `public_offer_pack_ready`.

## 2026-05-06 - Commercial feedback loop

- Anade `commercial_feedback_loop.py` para clasificar feedback y decidir version, precio, copy y siguiente accion.
- Bloquea cambios de oferta si falta feedback revisado, roadmap actualizado o owner de release notes.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/commercial_feedback_loop`.
- Actualiza manifiesto a `commercial_feedback_loop_ready`.

## 2026-05-06 - Post launch control

- Anade `post_launch_control.py` para revisar primeras ventas, activaciones, soporte, refunds y fallos.
- Bloquea escalado publico si hay tickets sin resolver, activaciones pendientes o fulfillment fallido.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/post_launch_control`.
- Actualiza manifiesto a `post_launch_control_ready`.

## 2026-05-06 - Limited public launch gate

- Anade `limited_public_launch.py` para validar una venta publica limitada tras el piloto.
- Bloquea `GO` sin piloto valido, checkout HTTPS, variantes reales, soporte, first sale cap y rollback owner.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/limited_public_launch`.
- Actualiza manifiesto a `limited_public_launch_ready`.

## 2026-05-06 - Pilot purchase kit

- Anade `pilot_purchase_kit.py` para preparar compra piloto privada con orden, licencia, entrega e importacion verificada.
- Consume evidencia M34 y bloquea `GO` si falta licencia firmada, manifest de entrega o confirmacion Pro en app.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/pilot_purchase_kit`.
- Actualiza manifiesto a `pilot_purchase_kit_ready`.

## 2026-05-06 - Commercial release candidate

- Anade `commercial_release_candidate.py` para validar ZIP, SHA256, readiness, clave publica y compra piloto.
- Bloquea venta publica si falta evidencia M33 `GO`, compra piloto o clave publica final.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/commercial_release_candidate`.
- Actualiza manifiesto a `commercial_release_candidate_ready`.

## 2026-05-06 - Checkout live readiness

- Anade `checkout_live_readiness.py` para validar URLs Lemon, variantes, soporte y rollback antes de venta publica.
- Bloquea si faltan `providerVariantId`, checkout HTTPS, relay HTTPS o evidencia M32 `GO`.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/checkout_live_readiness`.
- Actualiza manifiesto a `checkout_live_readiness_ready`.

## 2026-05-06 - Render staging purchase drill

- Anade `render_staging_purchase_drill.py` para probar webhook, cola y dispatch en Render staging.
- Exige flags explicitos `--send-webhook` y `--dispatch` para operaciones mutantes.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-relay/data/render_staging_purchase_drill`.
- Actualiza manifiesto a `relay_render_staging_purchase_drill_ready`.

## 2026-05-06 - Render staging apply gate

- Anade `render_staging_apply_gate.py` para validar la aplicacion final de variables en Render.
- Exige handoff M30 `GO`, confirmacion manual y `render_staging_gate.py` remoto `GO`.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-relay/data/render_staging_apply_gate`.
- Actualiza manifiesto a `relay_render_staging_apply_gate_ready`.

## 2026-05-06 - Local ingest Render handoff

- Anade `local_ingest_render_handoff.py` para convertir sesion local GO en variables listas para Render.
- Genera evidencia JSON/Markdown y `.env` local con `SQX_LOCAL_INGEST_URL`.
- Puede consumir la ultima sesion M29 o una URL explicita.
- Actualiza manifiesto a `relay_local_ingest_render_handoff_ready`.

## 2026-05-06 - Local ingest staging session

- Anade `local_ingest_staging_session.py` para orquestar backend local, tunel e ingest check.
- Mantiene arranque de backend/tunel como opt-in con `--start-backend` y `--start-tunnel`.
- Genera evidencia unica para la sesion previa a Render staging.
- Actualiza manifiesto a `relay_local_ingest_staging_session_ready`.

## 2026-05-06 - Local ingest tunnel launcher

- Anade `local_ingest_tunnel_launcher.py` para detectar `cloudflared`, `ngrok` o `localtunnel`.
- Valida el backend local en `/api/health` antes de lanzar tunel.
- Puede arrancar tunel con `--start` y parsear la URL publica de ingest.
- Actualiza manifiesto a `relay_local_ingest_tunnel_launcher_ready`.

## 2026-05-06 - Local ingest tunnel check

- Anade `local_ingest_tunnel_check.py` para validar `SQX_LOCAL_INGEST_URL` antes de configurarlo en Render.
- Comprueba politica HTTPS, `/api/health` y bundle firmado opcional hacia `/api/fulfillment/relay-ingest`.
- Guarda evidencia local en `backend/sqx-edge-relay/data/local_ingest_tunnel_check`.
- Actualiza manifiesto a `relay_local_ingest_tunnel_check_ready`.

## 2026-05-06 - Render staging secrets kit

- Anade `render_staging_secrets_kit.py` para generar secretos fuertes de staging.
- Escribe `.env` local ignorado por git y evidencia redactada.
- Bloquea placeholders, valores cortos y passwords de cuenta Render en entorno.
- Actualiza manifiesto a `relay_render_staging_secrets_kit_ready`.

## 2026-05-06 - Render staging launch pack

- Anade `render_staging_launch_pack.py` para preparar blueprint, SHA256, variables y comandos de staging.
- Integra el estado del Render staging gate en una evidencia unica.
- Guarda evidencia local en `backend/sqx-edge-relay/data/render_staging_launch_pack`.
- Actualiza manifiesto a `relay_render_staging_launch_pack_ready`.

## 2026-05-06 - Render staging gate

- Anade `render_staging_gate.py` como compuerta GO/NO-GO antes del despliegue vivo.
- Exige handshake Render `GO`, URL staging y evidencia remota `GO`.
- Guarda evidencia local en `backend/sqx-edge-relay/data/render_staging_gate`.
- Actualiza manifiesto a `relay_render_staging_gate_ready`.

## 2026-05-06 - Render credential handshake

- Anade `render_credentials_handshake.py` para validar politica de credenciales antes del deploy real.
- Bloquea el uso de password de cuenta Render mediante `RENDER_PASSWORD` o `RENDER_ACCOUNT_PASSWORD`.
- Guarda evidencia local JSON/Markdown ignorada por git.
- Actualiza manifiesto a `relay_render_credentials_handshake_ready`.

## 2026-05-06 - Render API preflight

- Anade `render_api_preflight.py` para validar API key, owner/workspace y blueprint staging.
- Amplia `.env.staging.example` con variables Render API.
- Documenta el flujo seguro sin usar password de cuenta en scripts.
- Actualiza manifiesto a `relay_render_api_preflight_ready`.

## 2026-05-06 - Render staging evidence pack

- Recomienda Render como primer proveedor de staging para el relay.
- Anade `render.staging.yaml.example`.
- Anade `staging_evidence.py` para generar decision GO/NO-GO en JSON y Markdown.
- Actualiza manifiesto a `relay_staging_execution_ready`.

## 2026-05-06 - Relay staging validation kit

- Anade `.env.staging.example` para entorno staging.
- Anade `staging_smoke.py` para validar health, config, observability, snapshot y webhook firmado.
- Anade checklist go/no-go de staging.
- Actualiza manifiesto a `relay_staging_ready`.

## 2026-05-06 - Production relay deployment package

- Anade Dockerfile, `.dockerignore` y plantillas de despliegue para el relay.
- Anade `deployment_check.py` para preflight de produccion.
- Documenta Render, Railway, Fly.io y VPS/systemd en la guia de despliegue.
- Actualiza manifiesto a `relay_production_deploy_ready`.

## 2026-05-06 - Relay observability and simulation

- Anade eventos JSONL y snapshots de cola para el relay remoto.
- Expone `GET /relay/observability` y `POST /relay/observability/snapshot`.
- Anade `simulate_purchase_flow.py` para probar compra -> relay -> dispatch -> snapshot.
- Actualiza manifiesto a `relay_observability_ready`.

## 2026-05-06 - Relay deployment hardening

- Anade `GET /relay/config-check` para validar configuracion sin exponer secretos.
- Protege endpoints operativos con `SQX_RELAY_OPERATOR_TOKEN` cuando esta configurado.
- Anade `.env.example`, `dispatch_worker.py` y `run-worker.bat` para operacion supervisada.
- Actualiza manifiesto, contratos y documentacion a estado `relay_deployment_ready`.

## 2026-05-06 - Deployable remote relay service

- Anade `backend/sqx-edge-relay` como servicio remoto separado del ZIP portable.
- Implementa cola remota con `pending`, `sent`, `failed`, dispatch y requeue.
- Conecta Lemon webhook -> relay bundle -> ingest local firmado.
- Refuerza packaging para excluir el relay del paquete final de cliente.

## 2026-05-06 - Trusted relay ingest

- Anade `POST /api/fulfillment/relay-ingest` para bundles firmados por relay remoto.
- Anade `relay_bundle.py` para preparar bundles de prueba y validar el flujo de relay.
- Refuerza exclusiones del ZIP con `relay_event_*.json` y tooling interno del relay.
- Actualiza la documentacion de M15 y las notas operativas del relay.

## 2026-05-06 - Operator retry cockpit

- Anade estados operativos y contador de intentos persistidos por request de fulfillment.
- Anade `POST /api/fulfillment/request-status` y resumen enriquecido en la cola local.
- Anade panel de fulfillment en Inicio para refrescar, procesar, ignorar y recolar requests.
- Separa la normalizacion compartida en `core/fulfillment_normalizer.py` para mantener el ZIP portable limpio.

## 2026-05-06 - Private receiver and queue

- Anade receiver privado local para webhooks de Lemon Squeezy.
- Persiste `events`, `requests` y `processed` con deduplicacion por `provider_event_id`.
- Expone endpoints locales para listar, inspeccionar y procesar requests.
- Documenta la fase M13 y la operativa del receiver.

## 2026-05-06 - Fulfillment automation bridge

- Anade `fulfillment_request.py` para validar firma y normalizar eventos de Lemon Squeezy.
- Anade `fulfill_from_request.ps1` para convertir una request en licencia firmada y entrega final.
- Refuerza exclusiones del ZIP para requests, eventos y tools internos de automatizacion.
- Documenta la fase M12 y las notas de automatizacion futura.

## 2026-05-06 - Checkout and fulfillment

- Prepara `upgrade.checkout` para Lemon Squeezy con Gumroad como fallback.
- Anade enlace de checkout en el panel Licencia, oculto hasta configurar URL real.
- Anade `prepare_customer_delivery.ps1` para preparar ZIP + licencia + instrucciones por cliente.
- Documenta M11 y runbook de entrega comercial.

## 2026-05-06 - Manual license issuer

- Anade `license_issue.py` para emitir licencias Pro firmadas en un solo comando.
- Permite cliente, email, plan, pedido, fechas, soporte y limite de equipos.
- Refuerza exclusiones de ZIP/auditoria para el issuer y artefactos locales de licencias.
- Documenta la fase M10 para primeras ventas manuales.

## 2026-05-06 - License key management

- Anade `license_keypair.ps1` para generar claves RSA offline compatibles con el firmador interno.
- Documenta M9 con el flujo manual de emision de licencias Pro.
- Refuerza `.gitignore`, empaquetado, auditoria y checklist contra claves privadas/licencias firmadas.
- Actualiza `product_manifest.json` con politica `never_commit_never_ship`.
- Regenera el ZIP portable y valida la API portable con health OK.

## 2026-05-05 - Release polish

- Anade `RELEASE_SQX_EDGE.bat` para ejecutar el checklist de entrega con doble click.
- El checklist puede exigir Git limpio con `-RequireCleanGit`.
- El release genera `dist/SQX_release_summary.txt` con ZIP, fecha, tamano y estado Git.
- El ZIP portable excluye el BAT de release interno para no confundir al usuario final.

## 2026-05-04 - Entrega profesional

Version entregable de SQX Edge Suite v1.

### Incluido

- Diseno `Premium SaaS Dark v2` con fase `Design Pro`.
- Pagina `Inicio` como cockpit operativo por defecto.
- Navegacion visual refinada para desktop y mobile.
- Tab `Estrategias` con eliminacion de cualquier estrategia visible.
- Restauracion de estrategias base eliminadas de la vista.
- Importacion, consolidacion y exportacion de estrategias.
- Project Generator con asistente de arranque y controles visuales refinados.
- Scripts analiticos y endpoints de backup integrados.
- Tests E2E opcionales con Playwright.
- Empaquetado portable con Python embebido.
- Launchers de un click: `START_SQX_EDGE.bat` y `STOP_SQX_EDGE.bat`.

### Verificacion

- Suite normal: `24 passed, 2 skipped`.
- E2E opcional con Playwright: cubre Inicio, Estrategias, eliminar/restaurar y mobile.
- ZIP portable validado en extraccion limpia.
- Runtime portable validado importando `flask` y `api.server`.

### Paquete

El ZIP final se genera en:

```text
dist/SQX_Edge_Tool_Portable_*.zip
```
# 2026-05-07 - Hotfix rollback release kit

- Anade `hotfix_rollback_release.py` para preparar acciones de hotfix, rollback, pausa o cierre.
- Valida owner, incidente, notas, target de rollback, comunicacion a clientes, soporte, verificacion y evidencia de cierre.
- Refuerza empaquetado, auditoria y checklist para excluir la nueva herramienta interna.
- Documenta M44 y el runbook de hotfix/rollback post-release.

# 2026-05-07 - Post release monitor

- Anade `post_release_monitor.py` para decidir mantener, pausar, hotfix, rollback o `scale_public`.
- Valida descargas, ventas, activaciones, tickets, incidencias severas, refunds y fallos de fulfillment.
- Refuerza empaquetado, auditoria y checklist para excluir la nueva herramienta interna.
- Documenta M43 y el runbook de monitorizacion post-release.

# 2026-05-06 - Release publication record

- Anade `release_publication_record.py` para registrar evidencia post-publicacion.
- Valida GitHub Release publicada, tag, ZIP, SHA256 coincidente, descarga probada, soporte y rollback.
- Refuerza empaquetado, auditoria y checklist para excluir la nueva herramienta interna.
- Documenta M42 y el runbook de evidencia de release publicada.

# 2026-05-06 - Public release gate

- Anade `public_release_gate.py` como compuerta final antes de publicar GitHub Release.
- Valida tag, URL HTTPS de release, ZIP adjunto, SHA256 publicado, soporte y rollback.
- Refuerza exclusiones del ZIP portable para la nueva herramienta interna.
- Documenta M41 y el runbook de publicacion controlada.

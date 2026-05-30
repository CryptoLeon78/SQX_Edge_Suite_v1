# SQX142 Backport From SQX144 Roadmap

Estado: `SQX142-144-BACKPORT9 Closeout & Operator Handoff` completado.

Este documento cambia el enfoque: Build 144 queda como fuente de ideas y superficie estatica, pero la implementacion practica se hara sobre SQX 142 local cuando sea posible. No se copian engine, binarios, licencia, bypass/crack, plugins core ni internals propietarios de 144 a 142.

## Principio

Backport significa recrear o adaptar funcionalidad con artefactos propios de SQX Edge y APIs ya disponibles en SQX 142 local.

Si una feature de 144 necesita cambios en SQX 142, se pueden modificar archivos de usuario/extensiones/configuracion de SQX 142 siempre que el cambio sea propio, reversible, con backup/evidencia y no toque licencia, activacion, engine ni binarios propietarios.

No significa:

- Copiar clases/plugins internos de 144.
- Portar licencias, activacion o bypass.
- Sustituir el motor activo 142.
- Reducir metodologia Capa1/Capa2 para imitar una feature nueva.
- Lanzar proyectos o mutar databanks sin gate explicito.

## Matriz De Frentes

| Frente 144 | Backport 142 | Decision inicial |
| --- | --- | --- |
| Results Plugins | Directo: SQX 142 ya tiene `user/extend/ResultsPlugins` y un plugin local activo. | `implement_first` |
| MCP read-only | Adaptar como API local SQX Edge/Flask que lea estado 142 saneado; no copiar ServletMCP. | `completed_design_build_next` |
| Custom Analysis Correlation Filter | Implementar fuera del engine como filtro Portfolio Lab / CSV / equity series; no databank action core. | `completed_external_build` |
| Nuevos Monte Carlo | Simular como benchmark externo o configuracion de robustez propia; no agregar engine methods de 144. | `completed_external_benchmark` |
| MT5 direct import | Usar pipeline local MT5/CSV ya gobernado y comparar contra `data.db`; no mezclar broker data sin fase. | `completed_probe_no_import` |
| Migration Tool | Sustituir por checklist copy-only de proyectos/settings permitidos; nunca licencia ni activacion. | `completed_checklist_no_copy` |
| Track closeout | Consolidar matriz de entregables, limites y siguiente decision operativa. | `completed_closeout_handoff` |

## SQX142-144-BACKPORT1 - Results Plugin Readiness Panel

Objetivo:

- Instalar `SQX Edge Readiness Panel` en SQX 142 local como Results Plugin propio.
- Mantener `Source Code Translator` intacto.
- No pedir `GET_SOURCE_CODE` ni `GET_ORDERS`.
- Tolerar que SQX 142 no emita `GET_STATS`, `GET_LAST_SETTINGS_XML` o `GET_SYMBOL_INFO`; si no llegan, mostrar `blocked/review` sin romper.
- No escribir archivos, no usar browser persistence, no llamar MCP y no mutar databanks.

Payload permitido:

- `index.html`
- `fixtures/fixtures.js`

Destino:

- `user/extend/ResultsPlugins/SQX Edge Readiness Panel` en SQX 142 local.

Aceptacion:

- Preflight SQX/Java limpio antes de copiar.
- Backup o evidencia de no-colision antes de instalar.
- Hashes instalados coinciden con el prototipo SQX Edge.
- Render offline desde carpeta SQX 142 pasa con estados `ready`, `review`, `blocked`.
- SQX 142 abre sin pantalla de licencia y el plugin queda pendiente de smoke visual en Results si no se automatiza la navegacion.

Resultado 2026-05-26:

- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport1_results_plugin_readiness_panel_20260526_153500.json`.
- Estado: `completed_installed_in_sqx142_local`.
- Instalado en SQX 142 local como `user/extend/ResultsPlugins/SQX Edge Readiness Panel`.
- Payload instalado: `index.html` y `fixtures/fixtures.js`.
- Plugin existente `Source Code Translator` preservado.
- Verificacion: hashes instalados coinciden con prototipo, render Playwright desde carpeta SQX 142 `passed`, estados `ready`, `review`, `blocked`.
- Bloqueado: `GET_SOURCE_CODE`, `GET_ORDERS`, `resultsPlugins/create`, `resultsPlugins/rename`, `resultsPlugins/delete`, MCP writes, project run, databank mutation, MT5 import, Migration Tool, licencia/bypass y copia de internals 144.
- Siguiente bloque recomendado: `SQX142-144-BACKPORT2 MCP-Like Read-Only API Design`.

## Bloques Posteriores

`SQX142-144-BACKPORT2 MCP-Like Read-Only API`:

- Exponer una API local SQX Edge para listar proyectos/databanks/estrategias de SQX 142 con redaccion de nombres.
- Prohibido `run_project` y `stop_project`.
- Resultado 2026-05-26: completado como diseno sin runtime en `docs/SQX142_144_MCP_LIKE_READ_ONLY_API_DESIGN.md`.
- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport2_mcp_like_read_only_api_design_20260526_160500.json`.
- Contrato: `/api/sqx142/mcp-like/status`, `/api/sqx142/mcp-like/projects`, `/api/sqx142/mcp-like/data-catalog`, `/api/sqx142/mcp-like/databanks`, `/api/sqx142/mcp-like/strategies` y `/api/sqx142/mcp-like/results-plugin-readiness`.
- Fuentes permitidas: `build_sqx142_status(include_paths=False)`, `build_sqx142_performance_status(..., include_paths=False)`, `data.db mode=ro`, `user/projects` scan read-only, `user/extend/ResultsPlugins` saneado y fixtures mock.
- Snapshot estatico saneado: `projectDirCount=29`, `resultsPluginCount=2`, `BROKER=12`, `DATA=34`, `INSTRUMENTS=989`, `SESSIONS=1081`, procesos SQX/Java `0`.
- Bloqueado: `POST`, `PUT`, `PATCH`, `DELETE`, `run_project`, `stop_project`, `project/start`, `project/stop`, `taskmanager/activateTask`, `resultsPlugins/create`, `resultsPlugins/rename`, `resultsPlugins/delete`, `GET_SOURCE_CODE`, `GET_ORDERS`, escritura en `data.db`, proyectos, databanks, settings, browser storage o logs SQX, MT5 import, Migration Tool, licencia, activacion, bypass/crack, engine, binarios e internals de SQX 144.
- Siguiente bloque recomendado: `SQX142-144-BACKPORT3 MCP-Like Read-Only API Build`.

`SQX142-144-BACKPORT3 MCP-Like Read-Only API Build`:

- Resultado 2026-05-26: completado como build sin runtime SQX en `docs/SQX142_144_MCP_LIKE_READ_ONLY_API_BUILD.md`.
- Implementado en `backend/sqx-edge-tool/core/sqx142_mcp_like_readonly.py` y `backend/sqx-edge-tool/api/server.py`.
- Tests: `backend/sqx-edge-tool/test_sqx142_mcp_like_readonly.py`.
- Version de respuesta: `sqx142-mcp-like-readonly-v1`.
- Rutas activas: `/api/sqx142/mcp-like/status`, `/api/sqx142/mcp-like/projects`, `/api/sqx142/mcp-like/data-catalog`, `/api/sqx142/mcp-like/databanks`, `/api/sqx142/mcp-like/strategies` y `/api/sqx142/mcp-like/results-plugin-readiness`.
- Gate: operador local solo; remoto/tester devuelve `403 local_operator_required`.
- Privacidad: `privacy.local_paths_returned=false`, `privacy.raw_project_names_returned=false`, IDs opacos y `includeRawNames=true` bloqueado.
- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport3_mcp_like_read_only_api_build_20260526_164500.json`.
- Verificacion: `test_sqx142_mcp_like_readonly.py` -> `5 passed`; `test_local_ai_agent.py` -> `24 passed`.
- Sin SQX runtime, sin API interna SQX, sin escritura en SQX 142, sin source code/orders, sin MT5 import, sin Migration Tool, sin licencia/bypass, sin engine/binarios e internals 144.
- Siguiente bloque recomendado: `SQX142-144-BACKPORT4 Correlation Filter External Design`.

`SQX142-144-BACKPORT4 Correlation Filter External`:

- Implementar filtro de correlacion sobre CSV/equity series exportadas, no sobre databank activo.
- Comparar con Portfolio Lab Phase29.
- Resultado 2026-05-26: completado como diseno externo sin mutacion SQX en `docs/SQX142_144_CORRELATION_FILTER_EXTERNAL_DESIGN.md`.
- Referencia 144: `DatabankFilterByCorrelation`, accion `Filter by correlation`, endpoint interno `filterByCorrelation/filter`, periodo `Day`, `maxCorrelation=0.5`.
- Decision 142: reproducir como benchmark externo Portfolio Lab/CSV/equity series; no copiar plugin 144, no llamar endpoint interno, no borrar databanks.
- Entradas permitidas: Forward/Foward CSV natural, Portfolio Lab JSON, `returnSeries` o `equitySeries` comparables.
- Algoritmo propuesto: normalizar candidatos, validar Forward/Foward natural, construir retornos, alinear ventana, calcular Pearson, aplicar `maxCorrelation=0.50`, mantener similitud operativa cuando falten series y clasificar `portfolio`, `similar` o `review`.
- Integracion: reutiliza la logica existente de `app/js/modules/edge-factory.js` (`portfolioReturnSeries`, `pearsonCorrelation`, `bestCorrelation`, `correlationThreshold=0.50`) sin cambiarla en este bloque.
- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport4_correlation_filter_external_design_20260526_171500.json`.
- Bloqueado: `filterByCorrelation/filter`, `DatabankFilterByCorrelation` copiado, borrar filas de databank SQX, `data.db` writes, `user/projects` writes, SQX runtime, `CustomAnalysis=true`, `FitPortfolio=true`, retest rerun, forced pass, sample como real, profit guarantee, risk zero.
- Siguiente bloque recomendado: `SQX142-144-BACKPORT5 Correlation Filter External Build`.

`SQX142-144-BACKPORT5 Correlation Filter External Build`:

- Resultado 2026-05-26: completado como build externo sin runtime SQX en `docs/SQX142_144_CORRELATION_FILTER_EXTERNAL_BUILD.md`.
- Implementado en `backend/sqx-edge-tool/core/sqx142_correlation_filter_external.py` y `backend/sqx-edge-tool/api/server.py`.
- API local-only: `POST /api/sqx142/correlation-filter/external`.
- Version de respuesta: `sqx142-correlation-filter-external-v1`.
- Entradas: `rows`, `csv` o `portfolioLab`, con `returnSeries` o `equitySeries` comparables.
- Salidas: JSON `external_readonly`, decisiones `portfolio/similar/review`, `correlationStatus` `available/similarity_only/not_comparable`, IDs opacos y export CSV opcional.
- Privacidad: `privacy.local_paths_returned=false`, `privacy.raw_strategy_names_returned=false`, `privacy.private_fields_returned=false`, `privacy.tokens_returned=false`.
- Tests: `backend/sqx-edge-tool/test_sqx142_correlation_filter_external.py` -> `6 passed`.
- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport5_correlation_filter_external_build_20260526_181500.json`.
- Bloqueado: `filterByCorrelation/filter`, `DatabankFilterByCorrelation` copiado, `SQX databank deletion`, `data.db` writes, `user/projects` writes, SQX runtime, `CustomAnalysis=true`, `FitPortfolio=true`, retest rerun, forced pass, sample-as-real, profit guarantees, risk-zero claims y acceso remoto/tester.
- Siguiente bloque recomendado: `SQX142-144-BACKPORT6 Monte Carlo Candidate Benchmarks`.

`SQX142-144-BACKPORT6 Monte Carlo Candidate Benchmarks`:

- Modelar `MACHRBlockRandomization`, `SimulateParameterJitter` y `RandomlyDegradeExecution` como benchmarks externos o configuracion de robustez reproducible.
- No sustituir MC/MC2 canonicos sin evidencia.
- Resultado 2026-05-26: completado como build externo sin runtime SQX en `docs/SQX142_144_MONTE_CARLO_CANDIDATE_BENCHMARKS.md`.
- Implementado en `backend/sqx-edge-tool/core/sqx142_monte_carlo_candidate_benchmarks.py` y `backend/sqx-edge-tool/api/server.py`.
- API local-only: `POST /api/sqx142/monte-carlo/benchmarks`.
- Version de respuesta: `sqx142-monte-carlo-candidate-benchmarks-v1`.
- Entradas: `rows`, `csv` o `portfolioLab`, con `returnSeries` o `equitySeries` comparables.
- Metodos externos: `MACHRBlockRandomization`, `SimulateParameterJitter` y `RandomlyDegradeExecution`; seed determinista, `simulations=64`, `blockSize=4`, `parameterJitterPct=0.15`, `executionDegradeBps=2.0`.
- Salidas: JSON `external_readonly`, decisiones `benchmark_pass/benchmark_review/benchmark_fail`, `medianReturnPct`, `p05ReturnPct`, `medianDrawdownPct`, `maxDrawdownPct`, `survivalRate`, IDs opacos y export CSV opcional.
- Privacidad: `privacy.local_paths_returned=false`, `privacy.raw_strategy_names_returned=false`, `privacy.private_fields_returned=false`, `privacy.tokens_returned=false`.
- Tests: `backend/sqx-edge-tool/test_sqx142_monte_carlo_candidate_benchmarks.py` -> `6 passed`.
- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport6_monte_carlo_candidate_benchmarks_20260526_183500.json`.
- Bloqueado: metodos/clases/plugins internos 144 copiados, MC runtime SQX, API interna SQX, `data.db` writes, `user/projects` writes, SQX runtime, retest rerun, `CustomAnalysis=true`, `FitPortfolio=true`, sample-as-real, forced pass, profit guarantees, risk-zero claims y acceso remoto/tester.
- Siguiente bloque recomendado: `SQX142-144-BACKPORT7 MT5 Data Intake Probe`.

`SQX142-144-BACKPORT7 MT5 Data Intake Probe`:

- Un simbolo/timeframe en copia, comparado contra `data.db` gobernado.
- No alimentar generacion real.
- Resultado 2026-05-26: completado como probe externo sin importacion en `docs/SQX142_144_MT5_DATA_INTAKE_PROBE.md`.
- Implementado en `backend/sqx-edge-tool/core/sqx142_mt5_data_intake_probe.py` y `backend/sqx-edge-tool/api/server.py`.
- API local-only: `POST /api/sqx142/mt5-data-intake/probe`.
- Version de respuesta: `sqx142-mt5-data-intake-probe-v1`.
- Entradas: CSV OHLC copiado o `rows`, `asset`, `timeframe`, y opcional `sqxDataRows`/`dataDbRows`/`catalogRows` para comparar contra catalogo SQX saneado.
- Comparacion: valida forma OHLC, barras suficientes, duplicados/gaps, rango `dateFrom/dateTo` y solape contra `data.db mode=ro` o fixture payload.
- Salidas: JSON `external_readonly`, decisiones `intake_probe_pass/intake_probe_review/intake_probe_fail`, `assetRef`, `barsHash`, `catalogMatches`, `bestOverlapDays`, IDs opacos y export CSV opcional.
- Privacidad: `privacy.local_paths_returned=false`, `privacy.raw_mt5_symbol_returned=false`, `privacy.raw_sqx_symbol_returned=false`, `privacy.private_fields_returned=false`, `privacy.tokens_returned=false`.
- Tests: `backend/sqx-edge-tool/test_sqx142_mt5_data_intake_probe.py` -> `6 passed`.
- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport7_mt5_data_intake_probe_20260526_190500.json`.
- Bloqueado: terminal MT5 start, MT5 IPC, import directo SQX, `data.db` writes, `user/projects` writes, SQX runtime, Project Generator feed, Template Maker feed, Capa1/Capa2 feed, Portfolio Master feed, `run_project`, `project/start`, Migration Tool, internals 144, licencia/bypass, sample-as-real y acceso remoto/tester.
- Siguiente bloque recomendado: `SQX142-144-BACKPORT8 Copy-Only Migration Checklist`.

`SQX142-144-BACKPORT8 Copy-Only Migration Checklist`:

- Migrar solo preferencias/proyectos permitidos si aplica.
- Excluir licencias, activacion, cracks, tokens, engine y binarios.
- Resultado 2026-05-26: completado como checklist sin copia en `docs/SQX142_144_COPY_ONLY_MIGRATION_CHECKLIST.md`.
- Implementado en `backend/sqx-edge-tool/core/sqx142_copy_only_migration_checklist.py` y `backend/sqx-edge-tool/api/server.py`.
- API local-only: `POST /api/sqx142/migration/copy-only-checklist`.
- Version de respuesta: `sqx142-copy-only-migration-checklist-v1`.
- Entradas: `items`, `migrationItems`, `copyItems` o `checklist`, con `kind`, `label`, `relativePath` y `operation`.
- Salidas: JSON `checklist_only_no_copy`, decisiones `allow_copy/review_copy/block_copy`, IDs opacos, pasos manuales `preflight_process_sweep`, `backup_destination`, `copy_only_after_operator_confirmation`, `hash_verify`, `manual_open_check` y export CSV opcional.
- Privacidad: `privacy.local_paths_returned=false`, `privacy.raw_item_names_returned=false`, `privacy.private_fields_returned=false`, `privacy.tokens_returned=false`.
- Tests: `backend/sqx-edge-tool/test_sqx142_copy_only_migration_checklist.py` -> `5 passed`.
- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport8_copy_only_migration_checklist_20260526_193000.json`.
- Bloqueado: `Migration Tool`, licencia, activacion, cracks, bypass, tokens, cookies, secretos, engine, binarios, `internal`, `jre`, runtime, jars, ejecutables, `data.db`, databanks, logs, `data.db` writes, `user/projects` writes, SQX runtime, `run_project`, retests, `CustomAnalysis=true`, `FitPortfolio=true`, internals 144 y acceso remoto/tester.
- Siguiente bloque recomendado: `SQX142-144-BACKPORT9 Closeout & Operator Handoff`.

`SQX142-144-BACKPORT9 Closeout & Operator Handoff`:

- Resultado 2026-05-26: completado como cierre operativo en `docs/SQX142_144_BACKPORT_CLOSEOUT_OPERATOR_HANDOFF.md`.
- Estado: `completed_closeout_handoff`.
- Consolida BACKPORT1..8 como track cerrado para SQX 142 local: Results Plugin propio, API MCP-like read-only, Correlation Filter externo, Monte Carlo Candidate Benchmarks, MT5 Data Intake Probe y Copy-Only Migration Checklist.
- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport9_closeout_operator_handoff_20260526_200000.json`.
- Limites preservados: no engine/binarios/internals 144, no licencia/activacion/bypass, no SQX runtime, no `data.db` writes, no `user/projects` writes, no databank mutation, no `run_project`, no MT5 import directo, no Migration Tool, no forced pass, no sample-as-real, no profit guarantees y no risk-zero claims.
- `SQX142/144 backport track closed`.
- Siguiente decision recomendada: `UI-INTEGRATION1 Backport Operator Panel` o volver a `phase30_capa2_portfolio_master_inputs_pending` con inputs reales.

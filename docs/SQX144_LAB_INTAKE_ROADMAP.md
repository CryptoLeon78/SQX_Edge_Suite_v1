# SQX144 Lab Intake Roadmap

Estado: `SQX144-FULL-PROMOTE1 Host Promotion Gate` cerrado como `completed_operator_results_confirmed_sqx144_primary_no_sqx142_fallback`, `SQX144-FULL-UPDATE1` cerrado como `blocked_updated_host_requires_license_activation_and_migration_alignment` y `SQX144-FULL-UPDATE2` activo como ruta de promocion 144.2953 por carpeta nueva. `SQX144-COMPAT7 Results Plugin Manual Visual Confirmation` queda como bloqueo historico del lab anterior; la confirmacion Results de la build SQX144 Full queda cerrada por confirmacion del operador el 2026-06-06.

Este documento empezo gobernando la evaluacion de StrategyQuant X Build 144 (`v.144.2938`, May 2026) como candidato local para SQX Edge Suite. Tras el closeout del 2026-06-06, SQX144 Full sustituye a SQX 142 como host primario confirmado para el flujo actual; los textos de candidatura previos quedan historicos.

Fuentes publicas oficiales:

- <https://strategyquant.com/whatsnew/?date=2026-5>
- <https://strategyquant.com/doc/strategyquant/results-plugins/>
- <https://strategyquant.com/doc/strategyquant/mcp-integration/>
- <https://strategyquant.com/volume-market-profile/>
- <https://strategyquant.com/doc/strategyquant/how-to-install-strategyquant-x-and-transfer-your-data-from-a-previous-version/>

Fuente local candidata:

- Build 144 local instalada por el operador, tratada como evidencia privada/local-only.
- Build SQX 144 Full licenciada por el operador, perfil local `sqx144_full`, tratada como host primario confirmado; SQX142 fallback operativo cerrado el 2026-06-06.
- Migration Tool oficial ejecutada por el operador el 2026-06-04 sobre SQX 144 Full para importar SQX 142 Codex; resultado local `operator_migration_completed_snippets_compile_passed`, sin salida privada versionada en el repo.
- Build 144.2953 localizada como host actualizado separado por `SQX144-FULL-UPDATE1`; version confirmada pero no promovida por licencia/alineacion de migracion pendiente.
- El operador confirmo que el instalador oficial no permite elegir el directorio existente `SQX_144_Full`; `SQX144-FULL-UPDATE2` gobierna la ruta alternativa: instalar 144.2953 en carpeta nueva, activar/abrir workspace legitimamente, alinear por Migration Tool oficial o export/import documentado y promover solo tras preflight limpio.

## SQX144-FULL-PROMOTE1 - Host Promotion Gate

Objetivo:

- Promover `SQX_144_Full` como host primario confirmado de SQX Edge Suite sin copiar internals propietarios.
- Cerrar SQX 142 como fallback operativo activo tras preflight, switch local y confirmacion manual del operador.
- Registrar la decision en `docs/SQX144_FULL_PROMOTION_GATE.md` con marker `sqx144-full-promotion-gate-v1`.

Alcance:

- Gate read-only con `tools/sqx144_full_host_gate.ps1 status|preflight`.
- Validacion de ejecutable, `user/data/data.db`, `user/projects`, `user/extend/ResultsPlugins` y cero procesos SQX relevantes.
- Metadata minima en backend para detectar `sqx144_full` en `autodetect-sqx` y `validate-sqx-path`.
- Configuracion local ignorada puede apuntar a SQX 144 Full solo despues de backup local y preflight limpio.

Bloqueado:

- Engine/binarios/runtime/internal/jars de 144 en repo o copiados a SQX 142.
- Licencia, activacion, bypass, tokens, cookies, secretos, `data.db`, databanks, logs o salida de Migration Tool en el repo.
- Project runs, MT5 import, MCP writes, `data.db` writes, `user/projects` mutation, databank mutation, forced pass y claims de rentabilidad/riesgo cero.

Resultado 2026-06-04:

- Decision `completed_operator_results_confirmed_sqx144_primary_no_sqx142_fallback`.
- Preflight read-only: `sqx144_full_host_gate_passed`, shape completo, cero procesos relevantes, sin copia, sin escritura directa sobre `data.db` ni `user/projects`.
- Configuracion local ignorada actualizada a `sqx_host_profile=sqx144_full` tras backup en `.local/sqx144_full_promotion/`.
- El operador completo Migration Tool oficial; Codex adapto 13 snippets de usuario migrados que usaban `MainApp.isRangerLicense()` obsoleto y la compilacion forzada termino con `Compiling Snippets done in 11s`.
- Avisos residuales: `sqcustomization` HTTP 422, metadata de mercados auxiliar ausente y update 144.2953 tratado por `SQX144-FULL-UPDATE1` como no-promote controlado.
- Confirmacion Results cerrada: `docs/SQX144_RESULTS_CONFIRMATION_CLOSEOUT.md` registra `sqx144-results-confirmation-closeout-v1`.

## SQX144-FULL-UPDATE1 - Controlled Build 144.2953 Update Gate

Objetivo:

- Ejecutar la actualizacion a 144.2953 como gate controlado, sin copiar licencia, internals ni salida de migracion al repo.
- Validar si el host actualizado puede sustituir al host SQX 144 Full migrado/licenciado.
- Mantener el host SQX144 Full migrado anterior como fuente operativa mientras falten licencia/alineacion; SQX 142 ya no es fallback activo.

Resultado 2026-06-04:

- Documento de gate: `docs/SQX144_FULL_UPDATE1_GATE.md`.
- Marker: `sqx144-full-update1-gate-v1`.
- Herramienta read-only: `tools/sqx144_full_update_gate.ps1 status|preflight`.
- Build confirmado: `SQX version: 144.2953` en el host actualizado separado.
- Decision: `blocked_license_activation_pending_and_migration_alignment`.
- No-promote: el host actualizado llega a pantalla de licencia antes del workspace, no observa compilacion de snippets y no contiene la alineacion migrada ni `SQX Edge Readiness Panel`.
- Configuracion local ignorada: sin cambio; sigue apuntando al host SQX 144 Full migrado/licenciado anterior.
- Fronteras preservadas: sin copia de licencia/activacion/bypass, sin engine/binarios/internals al repo, sin Migration Tool automatizada por Codex, sin proyectos, sin MT5 import, sin `data.db` writes y sin `user/projects` mutation.

## SQX144-FULL-UPDATE2 - New Directory 144.2953 Promotion Gate

Objetivo:

- Beneficiarse de Build 144.2953 sin forzar una actualizacion in-place que el instalador oficial bloquea.
- Mantener `SQX_144_Full` como fuente operativa licenciada/migrada; SQX 142 ya no es fallback activo.
- Promover solo una carpeta nueva 144.2953 que pase licencia/workspace, alineacion oficial de migracion, panel, snippets y shape migrado.

Resultado inicial 2026-06-05:

- Documento de gate: `docs/SQX144_FULL_UPDATE2_GATE.md`.
- Marker: `sqx144-full-update2-gate-v1`.
- Herramienta read-only: `tools/sqx144_full_update2_gate.ps1 status|preflight`.
- Decision inicial: `blocked_candidate_license_and_official_migration_alignment_pending`.
- El script no ejecuta instalador, no automatiza Migration Tool, no copia licencia/activacion/bypass, no muta `hosts`, no lanza proyectos, no escribe `data.db`/`user/projects` y no cambia configuracion local.

## Objetivo

Integrar tres prioridades sin degradar la metodologia validada:

1. **Puente IA/SQX**: MCP y Results Plugins para leer proyectos, databanks, estrategias y crear analitica SQX Edge dentro de Results.
2. **Inteligencia de seleccion/robustez**: Custom Analysis Databank Correlation Filter y nuevos metodos Monte Carlo como candidatos, no reemplazos automaticos.
3. **Operativa de datos/versiones**: importacion directa MT5 y migracion entre versiones como laboratorio reversible antes de cualquier promocion.

## Reglas De Seguridad

- No ejecutar SQX 144 ni lanzar proyectos desde bloques historicos sin un bloque posterior explicito; en `SQX144-FULL-PROMOTE1` solo se permiten arranques cortos de validacion sin proyectos.
- No copiar engine, binarios, licencia, bypass/crack, plugins core ni internals propietarios al repo.
- No automatizar Migration Tool desde Codex ni versionar su salida; la migracion oficial ejecutada manualmente por el operador queda como evidencia privada/local-only.
- No sustituir rutas `sqx_path`, `sqx_data_db`, templates ni host 142/143 hasta decision `promote`.
- No mezclar datos MT5 importados con Darwinex/Dukascopy gobernado sin comparativa de symbol, source, broker, precision, timezone, sesiones, spread y rango de fechas.
- No activar nuevos metodos Monte Carlo en Capa1/Capa2 actual sin benchmark y aprobacion metodologica.
- Toda evidencia bruta queda bajo `.local/sqx144_lab_intake/` o carpeta local ignorada; tracked docs solo registran resumen saneado.

## Prioridades

### P1 - Compatibilidad, Migracion Y Puente IA

Alcance:

- Registrar build 144 como candidato local.
- Comparar estructura contra 142/143: runtime Java, configs, `user/data/data.db`, `user/projects`, `user/settings`, `user/extend`, `internal/plugins`, `internal/libs`.
- Probar Migration Tool solo en copia y verificar que la instalacion origen no cambia.
- Inspeccionar MCP sin tareas pesadas: herramientas expuestas, puerto, auth/local access y capacidad de listar proyectos/databanks.
- Inspeccionar Results Plugins y `CLAUDE.md` local para entender API, postMessage, stats, disclaimers y theming.

Aceptacion:

- Decision `observe`, `partial_adopt` o `promote_candidate`.
- Cero mutaciones en SQX 142 y cero cambios de motor activo.
- Riesgos de rutas/datos/licencia documentados.

### P2 - Correlation Filter Y Nuevos Monte Carlo

Alcance:

- Evaluar Custom Analysis Databank Correlation Filter con databank de prueba/clon.
- Comparar su logica daily P/L contra Portfolio Lab/Phase29 para saber si filtra clones sin matar diversidad util.
- Catalogar `MACHRBlockRandomization`, `SimulateParameterJitter` y `RandomlyDegradeExecution` como candidatos Capa2/Capa3.
- Definir benchmark minimo contra MC/MC2 actuales antes de cualquier promocion.

Aceptacion:

- Ningun filtro nuevo afecta la cadena de supervivientes actual.
- Cada metodo Monte Carlo queda clasificado como `candidate`, `defer` o `reject` con motivo.
- Se preserva `DeleteFailedStrategies=true` en retests/robustez que escriban output databank si se llegara a promover.

### P3 - MT5 Direct Import

Alcance:

- Importar como probe aislado un simbolo/timeframe desde MT5.
- Comparar shape contra `data.db` gobernado: nombre, broker/source, precision, timezone, sesiones, tick size/step, point value, spread, fechas y filas.
- Decidir si MT5 import puede alimentar diagnostico, datos alternativos o futuro broker-context intake.

Aceptacion:

- El probe no se usa para generacion real.
- No se mezclan datos de broker en templates Capa1/Capa2 sin nueva fase.
- Queda una matriz clara de compatibilidad MT5 vs Darwinex/Dukascopy.

## SQX144-COMPAT1 - StrategyQuant X 144 Lab Intake

Primer bloque ejecutable:

1. Snapshot local saneado de Build 144.
2. Hashes/fechas/tamanos de ejecutables y runtime.
3. Inventario de proyectos/plugins/result plugins sin copiar contenido privado.
4. Comparativa documental contra Build 142/143.
5. Matriz de riesgos para MCP, Results Plugins, Correlation Filter, Monte Carlo, MT5 import y Migration Tool.
6. Decision de siguiente bloque.

Resultado 2026-05-26:

- Evidencia local ignorada: `.local/sqx144_lab_intake/sqx144_lab_intake_20260526_143542.json`.
- Estado: `completed_snapshot_no_execution`.
- Decision: `partial_adopt`; Build 144 queda como candidato para herramientas perifericas, no como motor activo.
- Snapshot saneado: Build 144 contiene runtime Zulu 25, configs base `-Xms4g`/`ParallelGC`/`--enable-native-access=ALL-UNNAMED`, `data.db`, instalador, `VolumeProfile`, `ResultsPlugins`, `ServletMCP`, `DatabankFilterByCorrelation`, `DataSourceMt5Api` y `PortfolioMaster`.
- Results Plugins detectados: `CustomPlugin`, `Prop analytics` y `Prop Monte Carlo`, todos con `index.html`.
- Monte Carlo snippets detectados: `MACHRBlockRandomization`, `SimulateParameterJitter`, `RandomlyDegradeExecution`, junto a los metodos clasicos `RandomizeTradesOrder` y `RandomlySkipTrades`.
- Preflight de procesos: no se lanzo SQX 144; habia procesos SQX 142 abiertos, por lo que cualquier COMPAT2 con lectura runtime debe exigir preflight limpio o aceptacion explicita del operador.
- No se migro ningun dato, no se copio ningun internal al repo, no se cambio `sqx_path`, no se ejecuto SQX 144 y no se tocaron templates Capa1/Capa2.

Decision por frente:

| Frente | Decision | Siguiente paso |
| --- | --- | --- |
| MCP | `candidate_probe_next` | Mapear superficie estatica y preparar probe de solo lectura en bloque posterior. |
| Results Plugins | `partial_adopt_candidate` | Extraer API estatica y disenar plugin SQX Edge sin instalar en 142. |
| Correlation Filter | `candidate_benchmark_required` | Comparar en clon/databank contra Portfolio Lab diversity. |
| Nuevos Monte Carlo | `candidate_capa2_capa3` | Mapear parametros y preparar benchmark contra MC/MC2 actuales. |
| MT5 direct import | `isolated_probe_only` | Un simbolo/timeframe en copia, comparado contra `data.db` gobernado. |
| Migration Tool | `copy_only_later` | Probar solo sobre copia de instalacion, nunca sobre origen activo. |

## SQX144-COMPAT2 - Static Feature Surface

Segundo bloque ejecutado sin runtime:

1. Mapeo estatico de MCP.
2. Mapeo de Results Plugins y PostMessage API.
3. Mapeo de parametros de nuevos Monte Carlo.
4. Lectura estatica de Correlation Filter y MT5 import como contexto de riesgo.

Resultado 2026-05-26:

- Evidencia local ignorada: `.local/sqx144_lab_intake/sqx144_compat2_static_feature_surface_20260526_144600.json`.
- Estado: `completed_static_no_runtime`.
- No se lanzo SQX 144, no se instalo ningun plugin en SQX 142, no se llamo a MCP, no se importaron datos MT5 y no se modifico ningun databank/proyecto.

Superficie MCP:

| Tool | Tipo | Inputs requeridos | Decision |
| --- | --- | --- | --- |
| `list_projects` | lectura | ninguno | candidato para probe read-only. |
| `list_databanks` | lectura | `name` | candidato para probe read-only con proyecto controlado. |
| `list_strategies` | lectura | `name`, `databank` | candidato con redaccion de nombres en evidencia. |
| `get_strategy_stats` | lectura | `name`, `databank`, `strategy` | util para agente/Portfolio Lab, requiere control de privacidad. |
| `run_project` | runtime/mutacion | `name` | bloqueado hasta aprobacion explicita. |
| `stop_project` | runtime/mutacion | `name` | bloqueado hasta aprobacion explicita. |

El servidor MCP se registra bajo `/mcp`, anuncia `StrategyQuant X 1.0.0` y habilita capacidad `tools`. La politica inicial de SQX Edge debe permitir solo las cuatro tools de lectura en cualquier probe; `run_project` y `stop_project` quedan fuera del primer cliente MCP.

Superficie Results Plugins:

- Carpeta esperada: `user/extend/ResultsPlugins/<PluginName>/index.html`.
- Plugins bundled detectados: `CustomPlugin`, `Prop analytics`, `Prop Monte Carlo`.
- Limites observados: Starter `0` custom plugins; Professional `3` custom plugins.
- Endpoints internos de gestion: `resultsPlugins/list`, `create`, `rename`, `delete`; `create/rename/delete` mutan carpetas y no se usan en el primer prototipo.
- Mensajes SQX -> plugin: `STRATEGY_DATA`, `SET_THEME`, `SET_LANGUAGE`, `STATS_RESPONSE`, `ORDERS_RESPONSE`, `LAST_SETTINGS_XML_RESPONSE`, `SOURCE_CODE_RESPONSE`, `SYMBOL_INFO_RESPONSE`.
- Mensajes plugin -> SQX: `GET_STATS`, `GET_ORDERS`, `GET_LAST_SETTINGS_XML`, `GET_SOURCE_CODE`, `GET_SYMBOL_INFO`.
- Endpoints internos de datos: `resultsPlugins/stats`, `resultsPlugins/orders`, `resultsPlugins/settings`, `sourcecode/print`.
- Formatos source-code observados: `xml`, `mq4`, `mq5`, `el`, `pseudo`.
- Decision: `SQX144-COMPAT3` debe empezar por un prototipo de Results Plugin de solo lectura, sin instalar en SQX 142 hasta revisar cache, licencia y privacidad.

Parametros de nuevos Monte Carlo:

| Metodo | Parametros | Decision |
| --- | --- | --- |
| `MACHRBlockRandomization` | `BlockSize=5` (`2-50`), `PreserveTimestamps=true` | candidato de robustez por regimen; benchmark requerido. |
| `SimulateParameterJitter` | `Skip Probability=5`, `Adjust Probability=20`, `Max Price Adjust Percent=15` | candidato de sensibilidad; no sustituye MC/MC2. |
| `RandomlyDegradeExecution` | `Probability=15`, `Max Degradation Percent=25` | candidato de stress de ejecucion; comparar contra spread/slippage actuales. |

Lecturas adicionales:

- `DatabankFilterByCorrelation` expone accion de databank `Filter by correlation`, periodo por defecto `Day`, `maxCorrelation=0.5` y endpoint `filterByCorrelation/filter`; elimina estrategias del databank activo por correlacion mayor al umbral, por lo que exige clon/benchmark contra Portfolio Lab.
- `DataSourceMt5Api` expone `loadAvailableSymbols`, `importData` e `importDataAction`, con instalacion MT5 instalada/portable, simbolos, `TICK`/`M1`, broker profile, postfix y rango de fechas. Sigue limitado a probe aislado un simbolo/timeframe.

Decision del bloque:

- Estado: `completed`.
- Recomendacion: `SQX144-COMPAT3 Results Plugin Prototype Design`.
- Alternativas posteriores: `SQX144-MCP1 Read-Only Probe Plan`, `SQX144-MC1 Benchmark Design`, `SQX144-MT5-IMPORT1 Isolated Probe Plan`.
- Motivo: Results Plugins ofrece valor rapido para SQX Edge con flujo static-first y sin necesidad de lanzar SQX 144 runtime.

## SQX144-COMPAT3 - Results Plugin Prototype Design

Tercer bloque ejecutado sin runtime:

1. Preflight de procesos SQX limpio.
2. Contrato del primer Results Plugin SQX Edge.
3. Whitelist de mensajes PostMessage.
4. Reglas de privacidad, UI y aceptacion antes de construir archivos.

Resultado 2026-05-26:

- Documento de diseno: `docs/SQX144_RESULTS_PLUGIN_PROTOTYPE_DESIGN.md`.
- Evidencia local ignorada: `.local/sqx144_lab_intake/sqx144_compat3_results_plugin_design_20260526_145500.json`.
- Estado: `completed_design_no_runtime`.
- Prototipo definido: `SQX Edge Readiness Panel`.
- Alcance v0: read-only, estrategia seleccionada, `GET_STATS`, `GET_LAST_SETTINGS_XML`, `GET_SYMBOL_INFO`, disclaimer y readiness visual.
- Bloqueado en v0: `GET_SOURCE_CODE`, `GET_ORDERS`, endpoints `create/rename/delete`, escritura de archivos, databank mutation y cualquier instalacion en SQX 142.
- Siguiente bloque recomendado: `SQX144-COMPAT4 Results Plugin Prototype Build`, creando prototipo offline bajo `.local/sqx144_lab_intake/plugin_prototypes/` con fixtures mock antes de instalar nada en SQX.

## SQX144-COMPAT4 - Results Plugin Prototype Build

Cuarto bloque ejecutado sin runtime:

1. Preflight de procesos SQX limpio.
2. Prototipo offline `SQX Edge Readiness Panel` creado bajo `.local/sqx144_lab_intake/plugin_prototypes/`.
3. Fixtures mock `ready`, `review` y `blocked`.
4. Smoke local de archivos, privacidad y ausencia de llamadas peligrosas.
5. Render Playwright con estados `ready`, `review` y `blocked`.

Resultado 2026-05-26:

- Evidencia local ignorada: `.local/sqx144_lab_intake/sqx144_compat4_results_plugin_prototype_build_20260526_150500.json`.
- Estado: `completed_offline_prototype_no_install`.
- Archivos offline: `index.html`, `fixtures/fixtures.js`, `fixtures/ready.json`, `fixtures/review.json`, `fixtures/blocked.json`, `smoke/offline_smoke.ps1`.
- Captura local ignorada: `.local/sqx144_lab_intake/plugin_prototypes/SQX Edge Readiness Panel/smoke/compat4_panel_desktop.png`.
- Verificacion: `offline_smoke.ps1` paso con 5 archivos y 3 fixtures; Playwright confirmo readiness `ready`, `review` y `blocked`.
- Permitido en v0: `STRATEGY_DATA`, `STATS_RESPONSE`, `LAST_SETTINGS_XML_RESPONSE`, `SYMBOL_INFO_RESPONSE`, `SET_THEME`, `SET_LANGUAGE`, `GET_STATS`, `GET_LAST_SETTINGS_XML`, `GET_SYMBOL_INFO`.
- Bloqueado: `GET_SOURCE_CODE`, `GET_ORDERS`, `resultsPlugins/create`, `resultsPlugins/rename`, `resultsPlugins/delete`, MCP calls, SQX runtime, SQX install, file writes, browser persistence y databank mutation.
- Siguiente bloque recomendado: `SQX144-COMPAT5 Results Plugin Install Gate`, que debe decidir si se copia manualmente a un SQX 144 lab aislado; SQX 142 sigue intocable.

## SQX144-COMPAT5 - Results Plugin Install Gate

Quinto bloque ejecutado sin copia y sin runtime:

1. Preflight de procesos SQX/Java limpio.
2. Verificacion read-only de carpeta Results Plugins en SQX 144 lab.
3. Confirmacion de que `SQX Edge Readiness Panel` no existe aun en el destino.
4. Revalidacion de `offline_smoke.ps1`.
5. Decision de instalacion manual aislada y rollback.

Resultado 2026-05-26:

- Documento de gate: `docs/SQX144_RESULTS_PLUGIN_INSTALL_GATE.md`.
- Evidencia local ignorada: `.local/sqx144_lab_intake/sqx144_compat5_results_plugin_install_gate_20260526_151000.json`.
- Estado: `completed_ready_for_manual_install_no_copy`.
- Decision: `ready_for_manual_install_in_sqx144_lab_only`.
- `installExecuted=false`; no se copio ningun archivo, no se lanzo SQX 144, no se toco SQX 142 y no se cambio `sqx_path`.
- Destino futuro: `user/extend/ResultsPlugins/SQX Edge Readiness Panel` dentro del lab SQX 144.
- Payload minimo permitido para instalacion manual futura: `index.html` y `fixtures/fixtures.js`.
- Bloqueado: instalacion en SQX 142, sobrescritura de plugins existentes, MCP calls, `run_project`, `stop_project`, `GET_SOURCE_CODE`, `GET_ORDERS`, `resultsPlugins/create`, `resultsPlugins/rename`, `resultsPlugins/delete`, MT5 import, Migration Tool, file writes y databank mutation.
- Siguiente bloque recomendado: `SQX144-COMPAT6 Results Plugin Lab Smoke`, solo despues de que el operador apruebe/copie manualmente al SQX 144 lab.

## SQX144-COMPAT6 - Results Plugin Lab Smoke

Sexto bloque ejecutado con instalacion minima en SQX 144 lab:

1. Preflight de procesos SQX/Java limpio.
2. Copia de payload minimo `index.html` y `fixtures/fixtures.js` a `user/extend/ResultsPlugins/SQX Edge Readiness Panel` en SQX 144 lab.
3. Comparacion de hashes contra prototipo COMPAT4.
4. Privacy/static scan del payload instalado.
5. Render Playwright desde carpeta instalada.
6. Arranque corto de SQX 144 lab y cierre posterior con procesos a cero.

Resultado 2026-05-26:

- Documento de smoke: `docs/SQX144_RESULTS_PLUGIN_LAB_SMOKE.md`.
- Evidencia local ignorada: `.local/sqx144_lab_intake/sqx144_compat6_results_plugin_lab_smoke_20260526_151800.json`.
- Estado: `completed_lab_install_runtime_smoke_partial_visual`.
- Decision: `lab_smoke_passed_with_manual_results_tab_pending`.
- `installExecuted=true` solo en SQX 144 lab; SQX 142 no se toco.
- Archivos copiados: `index.html`, `fixtures/fixtures.js`; sobrescritura `false`.
- Verificacion instalada: hashes match, privacy scan `passed`, Playwright estados `ready`, `review`, `blocked`.
- Runtime: SQX 144 lab lanzo `StrategyQuantX`/`StrategyQuantX_ui`, no se lanzaron proyectos, no hubo MCP calls, no MT5 import, no Migration Tool, cierre final `remainingRelevantProcesses=0`.
- Limitacion: `visualResultsTabObserved=false`; falta confirmacion manual dentro del tab Results.
- Siguiente bloque recomendado: `SQX144-COMPAT7 Results Plugin Manual Visual Confirmation`.

## SQX144-COMPAT7 - Results Plugin Manual Visual Confirmation

Septimo bloque intentado con SQX 144 lab:

1. Preflight de procesos SQX/Java limpio.
2. Confirmacion de payload instalado en SQX 144 lab.
3. Lanzamiento visible de SQX 144.
4. Captura local de la ventana.
5. Cierre de procesos antes de registrar evidencia.

Resultado 2026-05-26:

- Documento de confirmacion: `docs/SQX144_RESULTS_PLUGIN_MANUAL_VISUAL_CONFIRMATION.md`.
- Evidencia local ignorada: `.local/sqx144_lab_intake/sqx144_compat7_results_plugin_manual_visual_confirmation_20260526_152500.json`.
- Estado: `blocked_by_license_gate_before_results`.
- Decision: `blocked_pending_operator_license_or_valid_lab_session`.
- SQX 144 lab abrio en pantalla de licencia antes del workspace.
- `resultsTabObserved=false`.
- `pluginVisibleInResults=false`.
- No se introdujo licencia y no se intento bypass.
- No se lanzaron proyectos, no hubo MCP calls, no MT5 import, no Migration Tool, no `GET_SOURCE_CODE`, no `GET_ORDERS` y no databank mutation.
- Cierre final `finalRelevantProcesses=0`.
- Siguiente bloque recomendado: `SQX144-COMPAT7B Results Plugin Visual Confirmation After Operator License`.

## Estados Permitidos

- `observe`: solo se conserva como referencia.
- `partial_adopt`: se adoptan herramientas perifericas, no motor ni datos.
- `promote_candidate`: se autoriza un bloque posterior para probar SQX 144 como motor candidato en clones.
- `blocked`: riesgo de compatibilidad, licencia, privacidad o metodologia.

## No-Go Inmediato

- Cualquier necesidad de copiar binarios/core internals al repo.
- Cualquier migracion que modifique una instalacion activa.
- Cualquier resultado que reduzca precision/OOS/Forward, simulaciones, filtros finales o trazabilidad para ganar velocidad.
- Cualquier salida que exponga rutas locales, licencias, identidad, tokens, protected URLs o evidencia privada.

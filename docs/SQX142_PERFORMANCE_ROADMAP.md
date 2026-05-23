# SQX 142 Performance Gate Roadmap

Estado: SQX142-PERF1 aplicado el 2026-05-22.

Este documento es el gate maestro para mejorar rendimiento de SQX 142 sin bajar calidad metodologica ni comprometer persistencia. La regla base queda fijada:

- `qualityReductionAllowed: false`
- no reducir OOS/Forward, precision validada, simulaciones MonteCarlo, Synthetic, Monkey, WFM/SPP ni filtros finales sin evidencia explicita
- todo cambio de config, view, ranking, databank o proyecto requiere backup o dry-run previo
- no tocar engine, plugins core, licencia, ejecutables ni binarios
- la exposicion de rutas, procesos y discos queda limitada al operador local

## Estado Base

Verificado localmente:

- SQX 142 esta alineado con runtime Zulu 22.32+15 de la build 143.
- Perfil activo: `baseline_143_safe`.
- Config base: `-Xms4g`, `ParallelGC`, `--enable-native-access=ALL-UNNAMED`.
- Host: doble Xeon E5-2695 v4, RAM suficiente para minado/retests.
- Espacio actual saneado: `C:` queda por encima de 300 GB libres tras limpieza y liberacion manual; disco deja de ser el cuello de botella inmediato.
- Settings favorables ya presentes: `storeChartData=false`, `dontStorePendingOrders=true`, `syncDatabanksAfterTaskDone=false`, metricas pips/pcts desactivadas.

## Interfaces

- Script operador: `tools/sqx142_performance_gate.ps1`
- Core Python: `backend/sqx-edge-tool/core/sqx_performance.py`
- CLI Python: `backend/sqx-edge-tool/tools/sqx142_performance_gate.py`
- Endpoint local-only: `GET /api/sqx142/performance/status`
- Evidencia local ignorada por Git: `.local/sqx142_performance/`
- Agente local: capability `sqx142_performance_help`
- Monitor local: panel `SQX 142 performance status`

El endpoint nunca devuelve rutas locales, emails, tokens ni URLs protegidas. Testers remotos reciben `visible: false` dentro de `/api/agent/status`.

Estado de acceso local SQX:

- El status incluye `localAccess`: `remote_access.xml`, requisito de password, presencia de `BrowserToken` y bandera `unrestrictedOnThisPc`.
- El gate no imprime ni persiste tokens; solo registra si existe token local.
- La URL base de pruebas API es `http://localhost:8080`, alineada con Electron.
- `api-auth-smoke --apply` arranca SQX, espera la API local, prueba `main/checkaccess`, cierra procesos y deja evidencia.

## Perfiles JVM

`baseline_143_safe`
- Perfil por defecto.
- Mantiene forma de config de build 143.
- Uso: baseline, comparativas y operacion normal estable.

`mining_fast_safe`
- Heap acotado para minados largos en el host operador.
- No cambia filtros, OOS ni reglas de calidad.
- Uso: pruebas comparativas de minado CPU-heavy tras baseline.

`retest_robust`
- Heap conservador para MonteCarlo, Synthetic, WFM y retests lentos.
- Uso: estabilidad antes que velocidad.

`diagnostic_low_risk`
- Heap mas bajo para smokes, UI y diagnostico.
- Uso: detectar crashes, procesos colgados y errores de consola sin cargar el sistema.

Aplicacion:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 apply-profile baseline_143_safe
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 apply-profile retest_robust --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 compare-profiles baseline_143_safe diagnostic_low_risk retest_robust mining_fast_safe --apply --wait-seconds 18 --restore-profile baseline_143_safe
```

El comando es dry-run por defecto. Con `--apply` crea backup bajo `SQX_142_Crack_local_backups`.

Power-loss hardening:

- Las escrituras de perfiles usan archivo temporal y replace atomico.
- El status valida `StrategyQuantX_nocheck.config`, `sqcli.config` y `CodeEditor.config`.
- Si un config contiene bytes nulos o no coincide con el perfil activo, el gate emite `runtime_config_corrupt` o `runtime_config_mismatch`.
- Tras el corte de luz del 2026-05-22 se detecto `CodeEditor.config` con bytes nulos, se restauro `baseline_143_safe` y se dejo evidencia local con backup previo.

## Views De Rendimiento

Views creadas en SQX 142 local:

- `MINING FAST REVIEW`: columnas ligeras para descartar barato durante minado.
- `RETEST QUICK REVIEW`: columnas de revision rapida tras OOS/retests basicos.
- `RETEST ROBUST REVIEW`: columnas analiticas para candidatos ya filtrados.
- `FINAL DECISION FULL`: revision completa/export con columnas pesadas.

Se mantienen separadas las views MonteCarlo especializadas:

- `MC MONKEY RETEST`
- `MC SYNTHETIC RETEST`

Regla: no mezclar metricas de Monkey en Synthetic ni al reves. Durante ejecucion se priorizan views ligeras; las columnas pesadas quedan para revision final.

## Fases

### Phase 0 - Safety, Backup And Baseline Lock

- Baseline bloqueado en `baseline_143_safe`.
- Backups obligatorios antes de escribir configs o views.
- Rollback por perfil documentado.
- Calidad protegida por `qualityReductionAllowed: false`.

Aceptacion:

- `tools/sqx142_performance_gate.ps1 status` responde.
- `GET /api/sqx142/performance/status` no devuelve rutas.

### Phase 1 - Measurement Gate

La herramienta mide:

- perfil JVM activo
- runtime/config
- procesos vivos/colgados
- CPU/RAM
- disco libre
- tamanos de projects/logs/views/cache Electron
- views de rendimiento y MonteCarlo
- ultimo smoke/evidencia

Aceptacion:

- Snapshot escrito en `.local/sqx142_performance/`.
- Warning de disco si `C:` baja de 100 GB.
- Critical si baja de 60 GB.

### Phase 2 - Runtime And JVM Profiles

Probar perfiles de uno en uno:

1. `baseline_143_safe`
2. `diagnostic_low_risk`
3. `retest_robust`
4. `mining_fast_safe`

Cada perfil necesita smoke de arranque/cierre, sin `hs_err_pid*.log` y sin procesos colgados.

Resultado local 2026-05-22:

| Perfil | Smoke | hs_err | Procesos colgados | RAM libre tras arranque | Decision |
| --- | --- | --- | --- | --- | --- |
| `baseline_143_safe` | OK | 0 | 0 | 111.6 GB | Default operativo |
| `diagnostic_low_risk` | OK | 0 | 0 | 115.6 GB | Diagnostico/UI |
| `retest_robust` | OK | 0 | 0 | 111.7 GB | Candidato para Monkey/Synthetic/WFM |
| `mining_fast_safe` | OK | 0 | 0 | 107.3 GB | Candidato para minado; requiere prueba real |

Evidencia local: `.local/sqx142_performance/profile_compare_20260522_180051.json`.

Decision: mantener `baseline_143_safe` como perfil restaurado por defecto. Usar `retest_robust` solo para la siguiente prueba real de retests pesados y `mining_fast_safe` solo cuando toque smoke de minado corto.

### Phase 3 - Mining Pipeline Efficiency

Orden recomendado:

1. Generacion amplia con filtros baratos.
2. Seleccion intermedia.
3. Robustez pesada solo sobre candidatos.
4. Revision con `MINING FAST REVIEW` antes de views completas.

No lanzar minados caros contra databanks mezclados o gigantes.

Estado 2026-05-23:

- `project-mining-pipeline-advisor` implementa la Fase 3 en dry-run: lee la tarea Build, databanks de entrada/salida, ranking, condiciones, bloques disponibles y riesgos de eficiencia antes de proponer cualquier smoke.
- Evidencia `mining_pipeline_advisor_20260523_090121.json`: Build Capa1 usa `genetic-evolution`, `MaxStrategies=5000`, `MaxGenerations=50`, `Islands=4`, ranking activo `RExpectancy`, `23/31` condiciones activas y `StoreChartData=false`.
- Riesgos detectados: `large_max_strategies`, `large_max_generations`, `output_databank_null` y `build_has_active_crosschecks`. Esto no es fallo, pero bloquea minado largo a ciegas.
- Entrada Build actual: `Syntetic` con `86` estrategias, `85 passed / 1 failed`; salida declarada `null`. No se modifica porque configurar valores individuales de tareas queda pendiente de decision metodologica de Ivan tras optimizacion.
- Stage plan Fase 3: `build_short_single_run` con `mining_fast_safe`, revision `cheap_review` con `MINING FAST REVIEW` y `survivor_handoff` hacia Fase 4.
- Siguiente experimento seguro: crear clon `_PERFQ_*` desde Capa1 base y preparar un smoke de Build en el clon; no tocar el maestro.

### Phase 4 - Retest Scheduling And Quality Preservation

Orden recomendado:

1. Retest/OOS basicos.
2. Tick/higher precision.
3. Monkey/Synthetic/MC sobre supervivientes.
4. WFM/SPP/OptProfile solo para candidatos justificables.

`Retest Robust Queue`: no ejecutar varios retests lentos compitiendo por RAM/disco.

Estado 2026-05-22:

- `project-retest-queue-plan` lee `project.cfx`, cruza tareas con logs reales y genera una cola medible sin modificar el proyecto.
- Evidencia inicial: `retest_queue_plan_20260522_190228.json`.
- `prepare-queue-step` activa una unica tarea de la cola, protege el proyecto maestro por defecto, aplica el perfil recomendado y puede lanzar SQX.
- La cola marca como pesados: Build, TICK REAL, MC, MC 2, Sequential, Monkey Test, Synthetic, SPP y WFM.
- Smoke de cola en copia `_PERFQ_*`: MC completo en `2 min. 31 s.` con `83 passed / 3 failed`; MC 2 completo en `4 min. 17 s.` con `0 passed / 86 failed`, rechazo natural por filtros, no forzado.
- Sequential queda aislado: el primer smoke con 84 candidatos mostro actividad viva pero no volco salida dentro del presupuesto usado; el smoke diagnostico acotado ya confirma que la tarea funciona y persiste resultados cuando la escala es manejable.
- Monkey conserva duracion real `5 min. 35 s.` y resultado natural `53 passed / 33 failed`.
- Synthetic conserva duracion real `4 min. 7 s.` y resultado natural `85 passed / 1 failed`.
- Recomendacion operativa: `retest_robust` para retests pesados, `mining_fast_safe` solo para experimentos de minado y `baseline_143_safe` como default.
- Regla reforzada: Monkey, Synthetic, WFM y SPP no deben ejecutarse simultaneamente hasta que un smoke comparativo demuestre que no aumenta crash rate ni altera persistencia.
- Regla reforzada: Sequential se ejecuta solo en proyecto `_PERFQ_*`, con timeout, snapshot antes/despues y cierre de procesos verificado.
- Capa nueva 2026-05-22: `sequential-smoke` prepara Sequential, aplica `retest_robust`, arranca SQX, espera API, intenta start por API, mide databank/logs y siempre cierra/restaura baseline.
- Blocker `Remote access disabled` resuelto: SQX 142 no acepta solo `remote_access.xml`; el backend mantiene un flag runtime adicional y permite las llamadas del navegador local cuando recibe la cabecera `browserToken` actual de `settings.xml`. El gate envia esa cabecera sin exponer el valor, usa cookies de sesion y conserva el cierre con guardia de procesos.
- Evidencia de resolucion: `api_auth_smoke_20260522_205359.json` arranca SQX, espera API en `77.17 s.`, valida `/main/checkaccess` con `Access granted` y cierra sin procesos vivos (`leftAfterForce: 0`).
- Smoke Sequential endurecido: `sequential_smoke_20260522_211255.json` confirma que la automatizacion ya funciona (`start-project` y `stop-project` OK, cierre sin procesos vivos, restore a `baseline_143_safe`), pero marca `ok: false` porque el retest termina como `completed_without_work`, `total: 0`, sin cambio de databank ni timestamp. El siguiente problema ya no es acceso API, sino configuracion/entrada real de Sequential.
- Guardia de entrada aplicada: `sequential_smoke_20260522_211636.json` detecta antes de arrancar SQX que `Sequential` usa `MC2` como input, `MC2` contiene 86 estrategias pero `0 passed`, y por tanto salta el lanzamiento con `no_input_candidates`. Esto evita smokes de 0 trabajo y conserva calidad porque no relaja filtros ni fuerza passed.
- Smoke Sequential diagnostico cerrado: `create-sequential-diagnostic-variant --max-passed 8 --apply` creo `_PERFQ_SEQDIAG_20260522_230211` desde el clon MC2 reparado, mantuvo solo 8 candidatos `passed` de MC2 y movio 78 archivos a `diagnostic_backups` dentro del clon. `queue_task_smoke_20260522_231046.json` completo `Sequential` en `4 min. 50 s.`, genero 8 salidas, `8 passed / 0 failed`, `total=624`, `timePerStrategy=24 s.`, sin procesos vivos y con restore a `baseline_143_safe`.
- Smoke Sequential intermedio cerrado: `create-sequential-diagnostic-variant --max-passed 24 --apply` creo `_PERFQ_SEQDIAG_20260522_231548`, mantuvo 24 candidatos `passed` y archivo 62 excluidos dentro del clon. `queue_task_smoke_20260522_233239.json` completo `Sequential` en `12 min. 57 s.`, genero 24 salidas, `24 passed / 0 failed`, `total=1908`, `timePerStrategy=28 s.`, sin procesos vivos y con restore a `baseline_143_safe`.
- Cola Sequential por lotes disenada: `create-sequential-batch-plan --batches "24,24,24,12" --apply` creo plan `sequential_batch_plan_20260522_234314.json` con 84 candidatos cubiertos sin solape y cuatro clones `_PERFQ_SEQBATCH_*`. `sequential-batch-merge-review --plan-evidence sequential_batch_plan_20260522_234314.json` valida estado inicial: `expectedTotal=84`, `expectedUnique=84`, `producedTotal=0`, `missingTotal=84`, `duplicateOutputs={}`. Esto deja la cola lista para ejecutar lote a lote y revisar merge sin tocar el proyecto maestro.
- Ejecucion de lotes Sequential:
  - B01 `_PERFQ_SEQBATCH_B01_001-024_20260522_234217` produjo `24/24`; el merge-review posterior deja `producedTotal=24`, `missingTotal=60`, sin duplicados ni inesperados. El smoke antiguo quedo `ok=false` por clasificacion de log, pero `automationOk=true`, `methodologicalProgress=true`, `afterFiles=24`; la herramienta queda corregida para completado por cobertura.
  - B02 `_PERFQ_SEQBATCH_B02_025-048_20260522_234231` produjo `24/24` con smoke `ok=true`, `outcome=completed`, `databankCoverageCompletion=true`, `elapsed=1405.4 s`, sin procesos vivos y restore a `baseline_143_safe`. Evidencia `queue_task_smoke_20260523_012052.json`; merge-review `sequential_batch_merge_review_20260523_012106.json` deja `producedTotal=48`, `missingTotal=36`, `duplicateOutputs={}`.
  - B03 `_PERFQ_SEQBATCH_B03_049-072_20260522_234245` produjo `24/24` con smoke `ok=true`, `outcome=completed`, `databankCoverageCompletion=true`, `elapsed=1368.22 s`, sin procesos vivos y restore a `baseline_143_safe`. Evidencia `queue_task_smoke_20260523_062112.json`; merge-review posterior deja `producedTotal=72`, `missingTotal=12`, `duplicateOutputs={}`.
  - B04 `_PERFQ_SEQBATCH_B04_073-084_20260522_234259` produjo `12/12` con smoke `ok=true`, `outcome=completed`, `elapsed=718.34 s`, log final correcto `8 min. 30 s.`, sin procesos vivos y restore a `baseline_143_safe`. Evidencia `queue_task_smoke_20260523_063343.json`.
- Merge final Sequential por lotes: `sequential_batch_merge_review_20260523_063358.json` valida `producedTotal=84`, `producedUnique=84`, `missingTotal=0`, `unexpectedTotal=0`, `duplicateOutputs={}`. `sequential_batch_merge_review_20260523_063406.json --apply` copia los outputs a `.local/sqx142_performance/sequential_merge_reviews/sequential_batch_plan_20260522_234314_20260523_063406/` para inspeccion, sin tocar el proyecto maestro.
- Auditor final Sequential: `sequential-final-review --latest --write-csv --apply` lee los 84 `.sqx` copiados como ZIP, extrae `settings.xml` y `SequentialOptimization_Results.xml`, y deja evidencia `sequential_final_review_20260523_071458.json` mas CSV local `sequential_final_review_20260523_071458.csv`. Resultado: `84/84` legibles, `84` con filtro `passed`, `84` con `sequentialPassed=true`, `0` invalidos, `569` areas estables, distribucion de parametros `26x6`, `51x7`, `7x8`. Esto audita persistencia y contenido sin modificar ningun proyecto SQX.
- Promocion MC2 preparada: `promote-mc2-spread-to-base` no usa un rango absoluto como regla general; por defecto calcula `RandomizeSpread = spread base x2-x5` del activo/proyecto seleccionado. En USDJPY/H4 detecta spread base `1.4` y deriva `2.8-7.0`, que coincide con el clon diagnostico validado. Dry-run `mc2_spread_promotion_20260523_072103.json` confirma evidencia final Sequential valida (`84/84`), diff XML `Min 30 -> 2.8`, `Max 50 -> 7`, backup planificado y `readyToApply=true`, sin tocar el Capa1 base.
- La promocion real queda bloqueada salvo flags explicitos: `--apply --allow-master-project --accept-methodology-change`. El rollback queda definido por evidencia mediante `rollback-mc2-spread-promotion --promotion-evidence <evidence> --apply`, restaurando el `project.cfx` desde backup y creando backup previo del estado actual.
- Promocion MC2 aplicada al Capa1 base: `mc2_spread_promotion_20260523_072626.json` cambia solo `MC 2 / RandomizeSpread` de `30-50` a `baseSpread x2-x5` (`2.8-7.0` en USDJPY/H4), con backup en `SQX_142_Crack_local_backups` y rollback directo por evidencia.
- Smoke post-promocion sobre copia `_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260523_072637`: el primer intento `MC` con settle corto quedo sin progreso porque SQX aun cargaba databanks; se ajusta `queue-task-smoke` a `--start-settle-seconds 180` por defecto. Reintento `queue_task_smoke_20260523_074738.json`: `MC` 86 outputs, `81 passed / 5 failed`, `2 min. 17 s.`.
- Smoke post-promocion MC2: `queue_task_smoke_20260523_075933.json` valida `MC 2` con regla adaptativa aplicada: `86` outputs, `84 passed / 2 failed`, `5 min. 46 s.`, metodo `Randomize spread from 2.80 to 7.00`.
- Smoke post-promocion Sequential corto: `sequential_diag_variant_20260523_080026.json` crea `_PERFQ_SEQBATCH_POSTPROMO8_20260523_080012` con 8 candidatos MC2 passed y archiva Sequential viejo; `queue_task_smoke_20260523_081133.json` completa `Sequential` con `8/8 passed`, `4 min. 52 s.`, sin bajar filtros ni tocar el maestro.
- Higiene de clones aplicada: `performance-clone-hygiene --keep-newest 2 --apply` deja activos solo `_PERFQ_SEQBATCH_POSTPROMO8_20260523_080012` y `_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260523_072637`; archiva reversiblemente 8 clones antiguos en `SQX_142_Crack_local_backups/archived_perf_projects/20260523_081819`. Evidencia `performance_clone_hygiene_20260523_081821.json`. `user/projects` baja a `919.5 MB`.

### Phase 5 - Databanks, Views And Columns

Mantener views ligeras para ejecucion y analiticas para decision.

No usar durante ejecucion:

- mini charts si no hacen falta
- indicadores completos
- auditorias full
- metricas no usadas por el filtro actual

Estado 2026-05-23:

- `phase5-databank-view-guard` implementa la Fase 5 con politica estricta: views de ejecucion sin `MiniEquityChart`, `EntryIndicators`, `ExitIndicators` ni `PriceIndicators`; Monkey/Synthetic mantienen views separadas.
- Aplicado con `--apply --archive-views`: reasigna databanks del proyecto a `MINING FAST REVIEW`, `RETEST QUICK REVIEW`, `RETEST ROBUST REVIEW`, `MC MONKEY RETEST` y `MC SYNTHETIC RETEST`.
- Views legacy pesadas archivadas fuera de SQX activo, con backup reversible: `todas las metricas posibles`, `PROPIA`, `MONTECARLO RETEST`, `MONTECARLO TRADES`, `ROBUSTEZ`.
- Evidencia aplicada `phase5_databank_view_guard_20260523_091310.json`; backup en `SQX_142_Crack_local_backups/sqx142_phase5_views_before_20260523_091309`.
- Verificacion posterior `phase5_databank_view_guard_20260523_091327.json`: `blocking=[]`, `projectViewActions=[]`, `executionViewIssues=[]`.

### Phase 6 - Persistence, Cleanup And Project Hygiene

Solo limpieza reversible:

- archivar databanks antiguos
- separar resultados smoke/retest
- limpiar cache Electron/SQX solo con backup/runbook
- detectar logs repetidos
- detectar views rotas

No borrar proyectos, databanks, licencias ni settings de usuario.

Estado 2026-05-22:

- `archive-old-logs --keep-days 2 --apply` archiva logs anteriores al 2026-05-21 y elimina solo originales verificados dentro del ZIP.
- Ejecucion aplicada: 128 logs antiguos, 1.43 GB originales, ZIP verificado `sqx142_logs_before_20260521_20260522_185130.zip` de ~17 MB, evidencia `old_log_archive_20260522_185150.json`.
- Verificacion posterior: no quedan logs anteriores a ayer; `user/log` queda con 8 logs, solo fechas 2026-05-21 y 2026-05-22.
- Status posterior: `ok`, `baseline_143_safe`, sin warnings, logs bajan de ~1.5 GB a ~141 MB.

### Phase 7 - Parallelism And Resource Control

Medir el punto dulce por tipo de tarea:

- mining CPU-heavy
- retest stability
- UI/diagnostic

Mas hilos no se considera mejora hasta demostrar menor tiempo sin mas crashes.

Estado 2026-05-23:

- `performance-parallelism-advisor` implementa la Fase 7 en modo dry-run: lee CPU/RAM/disco, perfil activo, settings SQX relevantes (`GCType`, `threadAffinity`, `parallelDownload`, `syncDatabanksAfterTaskDone`, `storeChartData`, etc.) y smokes validados.
- Evidencia `performance_parallelism_advisor_20260523_085248.json`: host con `36` logical per socket, `117.7 GB` libres de RAM, `307.9 GB` libres en disco, status `ok` y perfil `baseline_143_safe`.
- Politica activa: `defaultMaxConcurrentSQXProjects=1`, `allowParallelHeavyRetests=false`, `allowMiningWhileRetesting=false`. Motivo: SQX 142 ya ha demostrado sensibilidad a procesos colgados/carga tardia y no existe smoke paralelo que mejore tiempo sin empeorar estabilidad.
- Perfiles de control:
  - `ui_diagnostic`: `diagnostic_low_risk`, max 1 instancia, sin retests pesados.
  - `retest_stability`: `retest_robust`, max 1 retest pesado, para MC/MC2/Monkey/Synthetic/Sequential.
  - `mining_cpu_heavy`: `mining_fast_safe`, max 1 proyecto SQX, sin mezclar con retests.
  - `sequential_batch_queue`: `retest_robust`, lotes `24+24+24+12`, max 1 lote concurrente.
- Siguiente experimento seguro: minado corto controlado en single-run con `mining_fast_safe`; no se prueba paralelismo hasta tener baseline de minado corto.

### Phase 8 - 143/144 Backport Candidates For Performance

Usar `docs/SQX142_143_BACKPORT_LEDGER.md` como fuente de control.

Backport permitido solo para artefactos extensibles:

- snippets
- columns
- views
- templates
- configs

Prohibido: engine, libs, plugins core, licencias y ejecutables.

### Phase 9 - Agent And Monitor Integration

Agente local puede responder:

- perfil activo
- cuello de botella probable
- ultima evidencia/smoke
- estado disco/procesos
- cobertura de views de rendimiento
- siguiente accion recomendada

Fuente fija: `fixed_sqx142_performance`. No ejecuta cambios sin confirmacion.

Implementacion aplicada:

- `/api/sqx142/performance/status` devuelve `intelligence.version=sqx142-performance-intelligence-v1`.
- `intelligence` incluye perfil activo, cobertura de views, ultima evidencia, evidencias clave, faltantes, recomendacion activa, capability del agente y privacidad `local_paths_returned=false`.
- El monitor local (`tools/remote_operator_monitor.hta`, `tools/remote_operator_probe.ps1`, fallback `tools/remote_operator_status.ps1`) muestra perfil, views, evidencia y siguiente accion recomendada.
- El agente local `sqx142_performance_help` usa esa inteligencia antes que respuesta libre del LLM.
- Modo de arranque: `passive_on_probe`. Se actualiza al pulsar `Arrancar`, `Refrescar`, consultar el agente o detectar SQX abierto; no crea un servicio residente adicional para evitar procesos colgados.
- Si SQX esta abierto, la recomendacion cambia a modo observacion y bloquea cambios de perfil/views/cache hasta cierre seguro.

### Phase 9B - Live Guard Safety Belt

Live Guard es el cinturon final antes de cerrar PERF1.

Reglas:

- Mientras SQX esta abierto, Live Guard solo observa: logs recientes, `hs_err_pid*.log`, procesos vivos y API local `localhost:8080`.
- No edita perfiles, views, cache, databanks, proyectos ni logs mientras SQX esta abierto.
- Al abrir SQX, su papel es preflight pasivo: avisar si hay crashes recientes, errores repetidos, API no responsiva o perfil no baseline.
- Al cerrar SQX, puede preparar reparacion segura y reversible con `tools\sqx142_performance_gate.ps1 live-guard --apply`.
- Reparaciones post-cierre permitidas: restaurar `baseline_143_safe` si el perfil/config no esta limpio, archivar logs antiguos con backup ZIP y guardar evidencia.
- Reparaciones no automaticas: borrar cache Electron, matar procesos, tocar databanks/proyectos o cambiar metodologia. Esas requieren confirmacion/manual review.

Comandos:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 live-guard
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 live-guard --apply
```

El endpoint `/api/sqx142/performance/status` incluye `intelligence.liveGuard` con estado, alertas, plan de reparacion, recomendacion y privacidad `local_paths_returned=false`.

### Phase 10 - Controlled Real Smokes

Smokes controlados:

- arranque/cierre
- minado corto
- Monkey
- Synthetic
- export/revision de databanks
- cierre sin procesos colgados

Comparar siempre contra baseline y guardar evidencia local.

Antes de tocar scheduling real:

- `clone-performance-project` prepara una copia controlada del proyecto real para experimentos de rendimiento.
- Es dry-run por defecto; con `--apply` crea un proyecto `_PERFQ_*` dentro de `user\projects`.
- No borra databanks, no limpia resultados y no altera el proyecto fuente.
- Copia creada: `_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338`, 761 archivos, ~197.7 MB, evidencia `project_clone_20260522_190339.json`.
- Verificacion de copia: `project-retest-queue-plan` y `project-mc-snapshot` funcionan sobre la copia; snapshot `mc_project_snapshot_20260522_190422.json` queda `ok`, sin `viewMismatches` ni issues.
- Primer paso preparado: `prepare-queue-step MC --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --apply --launch` deja activa solo la tarea `MC`, aplica `retest_robust`, crea backup `sqx142_queue_step_before_20260522_193258\project.cfx` y lanza SQX 142.
- Hardening aplicado: el reemplazo de `project.cfx` se hace despues de cerrar el ZIP de lectura para evitar `PermissionError` de Windows.
- API local descubierta durante smoke real: `POST /project/start` arranca el proyecto y `POST /taskmanager/activateTask` cambia la tarea activa. Queda documentada como capacidad operador-local, no remota, y no debe ejecutar cambios sin confirmacion explicita.
- `sqx-local-api` queda como wrapper operador-local dry-run por defecto para `probe`, `start-project`, `stop-project` y `activate-task`; protege proyectos fuente en acciones mutantes salvo `--allow-source-project`.
- `sqx-local-api` usa `http://localhost:8080`, cabeceras tipo navegador, cookies de sesion y fallback de `BrowserToken` sin exponer el token.
- `api-auth-smoke` valida la capa de autenticacion SQX local sin tocar proyectos.

Estado 2026-05-22:

- `project-mc-snapshot` lee el proyecto real `Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1` sin abrir SQX y guarda evidencia en `.local/sqx142_performance/`.
- `project-mc-diff` compara dos snapshots MC y muestra deltas por databank: numero de estrategias, bytes, timestamps, passed/failed, simulaciones y cambios de metodo.
- `begin-project-mc-smoke` prepara una sesion real: snapshot inicial, verificacion de views, perfil `retest_robust`, instrucciones de snapshot final y diff posterior.
- Snapshot validado: `Monkey Test` contiene 86 estrategias, 200 simulaciones, metodo `Real Monkey Test (PyRE), scale 1/3-3x, thr 15-85`, con 53 `passed` y 33 `failed` naturales por filtro MC.
- Snapshot validado: `Syntetic` contiene 86 estrategias, 100 simulaciones, metodo `Randomize OHLC history data`, con 85 `passed` y 1 `failed` natural por filtro MC.
- Se confirma que no debe forzarse `Passed`: el resultado `FiltersResultFailedReason` ya expresa correctamente si el retest fallo por filtro aunque el calculo MC exista.
- `prepare-project-mc-views --apply` reasigno solo las views del `project.cfx`: `Monkey Test -> MC MONKEY RETEST` y `Syntetic -> MC SYNTHETIC RETEST`, con backup local previo de `project.cfx`.
- La verificacion posterior queda sin `viewMismatches` y sin issues de lectura MC.
- Smoke real ejecutado con perfil `retest_robust`: snapshot inicial `mc_project_snapshot_20260522_182128.json`, snapshot posterior `mc_project_snapshot_20260522_183950.json`, diff `mc_project_diff_20260522_184006.json`.
- Resultado smoke real Monkey: 86 estrategias, 200 simulaciones en las 86, metodo sin cambios, timestamp actualizado a `2026-05-22T18:34:14`, mezcla natural estable `53 passed / 33 failed`.
- Resultado smoke real Syntetic: 86 estrategias, 100 simulaciones en las 86, metodo sin cambios, timestamp actualizado a `2026-05-22T18:39:20`, mezcla natural estable `85 passed / 1 failed`.
- No se detectan `hs_err_pid*.log` en la raiz SQX 142 tras el smoke.
- Post-smoke cerrado: `baseline_143_safe` restaurado con evidencia `profile_baseline_143_safe_20260522_184704.json`, status final `ok`, sin warnings, sin procesos y sin `hs_err_pid*.log`.
- Detector endurecido: los perfiles JVM se reconocen por firma semantica de lineas aunque SQX reordene opciones durante el cierre.
- `project-log-summary` extrae duracion por tarea desde logs del proyecto. Evidencia `project_log_summary_20260522_184936.json`.
- Duraciones smoke registradas: Monkey `5 min. 35 s.` con 53/33 y Synthetic `4 min. 7 s.` con 85/1. En ambos, `Monte Carlo retest methods` consume ~91% del tiempo; esto confirma que la siguiente optimizacion debe ser scheduling/colas y no reduccion de simulaciones/filtros.
- Smoke de cola real sobre la copia `_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338`: `MC` genero 86 resultados en `2 min. 31 s.` con mezcla natural `83 passed / 3 failed`; `MC 2` genero 86 resultados en `4 min. 17 s.` con mezcla natural `0 passed / 86 failed`; `Sequential` inicio y escribio resultados parciales, pero quedo fuera de presupuesto por falta de progreso y se cerro con guardia de procesos.
- Evidencia de cierre de cola: `project_log_summary_20260522_200457.json` y restore `baseline_143_safe` en `profile_baseline_143_safe_20260522_200505.json`.
- Smoke API dedicado inicial: `api-auth-smoke_20260522_203814.json` confirma arranque API en ~76 s, cierre limpio sin procesos vivos y blocker reproducible `Remote access disabled`.
- Smoke API resuelto: `api_auth_smoke_20260522_205359.json` confirma acceso local con cabecera `browserToken`, `Access granted`, cierre limpio y `baseline_143_safe` intacto.
- Smoke Sequential dedicado: `sequential_smoke_20260522_211255.json` separa `automationOk: true` de `methodologicalProgress: false`; no hay procesos colgados ni crash, pero Sequential no procesa estrategias en esta configuracion.
- Smoke Sequential optimizado: `sequential_smoke_20260522_211636.json` anade guardia previa de candidatos; `automationOk: true`, `methodologicalProgress: false`, `inputFiles: 86`, `inputPassed: 0`, `stopApi` saltado correctamente y sin lanzar SQX.
- Siguiente paso recomendado: `retest_next_step_20260522_212528.json` separa tareas listas, bloqueadas y no medidas; la cadena medida llega hasta Synthetic, `SPP` queda como siguiente experimento pesado y `FOWARD` como alternativa normal de menor coste.
- Decision operativa posterior: `SPP` y `FOWARD` quedan omitidos de pruebas y optimizacion. El recomendador aplica `operatorOmittedTasks=["FOWARD","SPP"]`, bloquea `WFM` por depender del databank omitido `SPP`, y deja como foco primario `Sequential` bloqueado por `MC2` con `0 passed`. Evidencia `retest_next_step_20260522_213847.json`.
- Hipotesis de usuario validada por lectura XML: `MC 2` usa `MonteCarloRetest` con `RandomizeSpread` activo en rango `30-50`, mientras el setup base del retest usa spread `1.4`. El detector marca `spread_stress_extreme_vs_base` con ratio `21.43x-35.71x`; esto es causa probable de `MC2 = 0 passed / 86 failed` y del bloqueo posterior de Sequential. Evidencias `retest_queue_plan_20260522_214541.json` y `retest_next_step_20260522_214541.json`.
- Variante diagnostica creada: `create-mc2-spread-variant --spread-min 2.8 --spread-max 7.0 --apply` crea `_PERFQ_MC2SPREAD__PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338_20260522_215125`, cambia solo `MC 2 / RandomizeSpread` de `30-50` a `2.8-7.0`, archiva 176 resultados viejos de `MC2`/`Sequential` dentro del clon y deja `MC2` limpio para smoke. Evidencia `mc2_spread_variant_20260522_215143.json`.
- Verificacion de variante: `retest_queue_plan_20260522_215159.json` confirma input `MC` con 83 passed, output `MC2` limpio con 0 archivos y spread `2.8-7.0` (`2x-5x` del spread base `1.4`). Sigue marcado como `spread_stress_high_vs_base`, pero ya no extremo.
- Reparacion del smoke API de cola: `queue-task-smoke` ahora arranca como la UI, enviando `projectXML`, `taskXMLFile` y `taskXML` desde `project.cfx`; ademas espera asentamiento inicial (`--start-settle-seconds`, 45 s usado en smoke) porque SQX responde por API antes de terminar de cargar databanks. Esto elimina el error `Cannot start project in incorrect running status: 100`.
- Reparacion de medicion: el reloj de `stall` empieza despues de `Project execution started`, no durante launch/carga inicial; los outputs previos del databank de salida se archivan de forma reversible antes del smoke para no mezclar muestras parciales.
- Smoke MC2 diagnostico completo: `queue_task_smoke_20260522_223328.json` procesa 86 estrategias en `5 min. 5 s.` con resultado natural `84 passed / 2 failed`, `total=8772`, `timePerStrategy=3 s.` y `Monte Carlo retest methods` como 89.51% del coste. El `ok` de esa evidencia antigua queda falso por clasificacion post-poll (`stalled_without_progress`) aunque `automationOk=true` y `methodologicalProgress=true`; la clasificacion posthoc queda corregida en herramienta para evidencias siguientes.
- Implicacion metodologica: el rango original `30-50` era demasiado extremo para este setup; el candidato `2.8-7.0` desbloquea MC2 con mezcla natural y permite volver a evaluar Sequential. No se promociona a Capa1 base hasta repetir/aceptar el cambio como regla metodologica.
- Sequential con MC2 desbloqueado: `queue_task_smoke_20260522_224504.json` confirma que ya no esta bloqueado por falta de candidatos (`MC2=84 passed / 2 failed`) y que SQX ejecuta optimizacion secuencial real en logs (`ProgressEngine - Sequential : Sequential optimization...`). No produjo databank dentro del presupuesto y `stop-project` agoto timeout, pero el cierre de procesos dejo `leftAfterForce=0` y `baseline_143_safe` restaurado.
- Reparacion de observabilidad Sequential: `queue-task-smoke` ahora detecta actividad viva en el log global de SQX, no solo cambios de databank/log final. Esto evita clasificar como colgada una tarea larga que esta optimizando pero no vuelca resultados hasta terminar.
- Variante Sequential diagnostica: `create-sequential-diagnostic-variant` crea un clon `_PERFQ_SEQDIAG_*` sin tocar el proyecto fuente, conserva solo un subconjunto de candidatos `passed` de `MC2` y archiva los excluidos de forma reversible. Evidencia `sequential_diag_variant_20260522_230224.json`.
- Smoke Sequential diagnostico completo: `queue_task_smoke_20260522_231046.json` confirma que Sequential no esta roto: con 8 candidatos `passed` de MC2 completo en `4 min. 50 s.`, genero 8 estrategias en el databank `Sequential`, `8 passed / 0 failed`, `total=624`, `timePerStrategy=24 s.` y `Sequential Optimization` concentro 90.49% del coste. La escala completa de 84 candidatos debe tratarse como prueba larga o por lotes, no como cuelgue.
- Smoke Sequential intermedio: `queue_task_smoke_20260522_233239.json` valida escala 24 con `24 passed / 0 failed`, `24` salidas, `12 min. 57 s.`, `timePerStrategy=28 s.` y `Sequential Optimization` en 92.83% del coste. La extrapolacion lineal sencilla para 84 candidatos queda en torno a 45-50 minutos, asi que la cola recomendada es por lotes de 24 antes de considerar una ejecucion completa.
- Plan de lotes real: `sequential_batch_plan_20260522_234314.json` reparte los 84 `MC2 passed` en clones no solapados `24+24+24+12`. Clones creados:
  - B01 `001-024`: `_PERFQ_SEQBATCH_B01_001-024_20260522_234217`
  - B02 `025-048`: `_PERFQ_SEQBATCH_B02_025-048_20260522_234231`
  - B03 `049-072`: `_PERFQ_SEQBATCH_B03_049-072_20260522_234245`
  - B04 `073-084`: `_PERFQ_SEQBATCH_B04_073-084_20260522_234259`
- Merge-review real: `sequential_batch_merge_review_20260522_234321.json` comprueba cobertura esperada, outputs producidos, missing/unexpected y duplicados. Por defecto no modifica SQX; con `--apply` copia outputs a `.local/sqx142_performance/sequential_merge_reviews/` para inspeccion, no al proyecto maestro.
- Correccion de smoke por cobertura: `queue-task-smoke` ahora considera completado un lote cuando el databank de salida alcanza el numero esperado de candidatos de entrada. B02 valida esta correccion con `ok=true`; evita esperar al timeout cuando SQX no expone un bloque final parseable en el log.
- B03 y B04 cierran la cola completa: los 84 candidatos MC2 reparados fueron procesados por Sequential en lotes `24+24+24+12`; el merge-review final queda verde y reversible.

## Comandos Operador

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 status
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 snapshot
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 create-views --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 compare-profiles baseline_143_safe retest_robust --apply --wait-seconds 20 --restore-profile baseline_143_safe
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 begin-project-mc-smoke --apply --launch
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 project-mc-snapshot --sample-limit 500
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 project-mc-diff --before mc_project_snapshot_YYYYMMDD_HHMMSS.json
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 project-mining-pipeline-advisor --project-name "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1"
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 phase5-databank-view-guard --project-name "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1"
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 phase5-databank-view-guard --project-name "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1" --apply --archive-views
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 project-log-summary --limit 30
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 project-retest-queue-plan --log-limit 80
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 project-retest-next-step --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --log-limit 80
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 mc2-spread-diagnostic --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --log-limit 80
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 create-mc2-spread-variant --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --spread-min 2.8 --spread-max 7.0 --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 queue-task-smoke "MC 2" --project-name "_PERFQ_MC2SPREAD__PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338_20260522_215125" --apply --max-seconds 700 --stall-seconds 300 --poll-seconds 20 --api-ready-timeout 120 --start-settle-seconds 45
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 create-sequential-diagnostic-variant --project-name "_PERFQ_MC2SPREAD__PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338_20260522_215125" --max-passed 8 --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 queue-task-smoke "Sequential" --project-name "_PERFQ_SEQDIAG_20260522_230211" --apply --max-seconds 900 --stall-seconds 240 --poll-seconds 20 --api-ready-timeout 120 --start-settle-seconds 45
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 create-sequential-diagnostic-variant --project-name "_PERFQ_MC2SPREAD__PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338_20260522_215125" --max-passed 24 --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 queue-task-smoke "Sequential" --project-name "_PERFQ_SEQDIAG_20260522_231548" --apply --max-seconds 1800 --stall-seconds 360 --poll-seconds 20 --api-ready-timeout 120 --start-settle-seconds 45
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 create-sequential-batch-plan --project-name "_PERFQ_MC2SPREAD__PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338_20260522_215125" --batches "24,24,24,12" --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 queue-task-smoke "Sequential" --project-name "_PERFQ_SEQBATCH_B01_001-024_20260522_234217" --apply --max-seconds 1800 --stall-seconds 360 --poll-seconds 20 --api-ready-timeout 120 --start-settle-seconds 45
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 queue-task-smoke "Sequential" --project-name "_PERFQ_SEQBATCH_B02_025-048_20260522_234231" --apply --max-seconds 1800 --stall-seconds 360 --poll-seconds 20 --api-ready-timeout 120 --start-settle-seconds 45
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 queue-task-smoke "Sequential" --project-name "_PERFQ_SEQBATCH_B03_049-072_20260522_234245" --apply --max-seconds 1800 --stall-seconds 360 --poll-seconds 20 --api-ready-timeout 120 --start-settle-seconds 45
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 queue-task-smoke "Sequential" --project-name "_PERFQ_SEQBATCH_B04_073-084_20260522_234259" --apply --max-seconds 1200 --stall-seconds 360 --poll-seconds 20 --api-ready-timeout 120 --start-settle-seconds 45
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 sequential-batch-merge-review --plan-evidence sequential_batch_plan_20260522_234314.json
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 sequential-batch-merge-review --plan-evidence sequential_batch_plan_20260522_234314.json --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 sequential-final-review --latest --write-csv --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 promote-mc2-spread-to-base --project-name "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1" --min-multiplier 2 --max-multiplier 5
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 promote-mc2-spread-to-base --project-name "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1" --min-multiplier 2 --max-multiplier 5 --apply --allow-master-project --accept-methodology-change
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 rollback-mc2-spread-promotion --promotion-evidence mc2_spread_promotion_YYYYMMDD_HHMMSS.json
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 performance-clone-hygiene --keep-newest 2
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 performance-clone-hygiene --keep-newest 2 --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 restore-performance-clone --archive-stamp 20260523_081819 --clone-name _PERFQ_SEQBATCH_B01_001-024_20260522_234217
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 restore-performance-clone --archive-stamp 20260523_081819 --clone-name _PERFQ_SEQBATCH_B01_001-024_20260522_234217 --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 performance-closeout-report
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 performance-next-action
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 performance-parallelism-advisor
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 live-guard
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 clone-performance-project
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 prepare-queue-step MC --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --apply --launch
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 sqx-local-api probe
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 api-auth-smoke --apply --api-ready-timeout 120
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 sqx-local-api activate-task --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --task-title Sequential --active true
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 sqx-local-api start-project --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338"
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 sequential-smoke --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --apply --max-seconds 180 --stall-seconds 60 --api-ready-timeout 120
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 prepare-project-mc-views --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 archive-old-logs --keep-days 2 --apply
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 cleanup-plan
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_performance_gate.ps1 smoke-start --apply --wait-seconds 20
```

## Evidencia PERF1

- Views de rendimiento creadas en SQX 142.
- Fase 3 implementada: `project-mining-pipeline-advisor` audita Build/minado sin tocar valores individuales ni proyecto maestro; evidencia `mining_pipeline_advisor_20260523_090121.json`.
- Fase 5 implementada con mano dura: views legacy pesadas archivadas y databanks reasignados a views ligeras/especializadas; evidencia `phase5_databank_view_guard_20260523_091310.json` y verificacion verde `phase5_databank_view_guard_20260523_091327.json`.
- Snapshot local creado en `.local/sqx142_performance/`.
- Smoke real de arranque/cierre validado: sin `hs_err_pid*.log`, cierre reforzado sin procesos restantes.
- Warning de disco cerrado: `C:` paso de ~81 GB a ~311 GB libres.
- Phase 2 validada: comparativa de perfiles JVM con restore automatico a `baseline_143_safe`, sin procesos colgados ni `hs_err_pid*.log`.
- Phase 10 snapshot validado sobre proyecto real: Monkey/Syntetic tienen metodos y simulaciones correctas, mezcla `passed/failed` natural y views del proyecto corregidas a las especializadas.
- Phase 4 iniciada: `project-retest-queue-plan` genera cola robusta por dependencias, coste, perfil recomendado y duraciones reales; `clone-performance-project` queda listo para crear copias de smoke sin contaminar el proyecto maestro.
- Copia performance creada y verificada: `_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338`.
- Cola performance medida: `MC` y `MC 2` completan correctamente con resultados naturales; `Sequential` queda marcado como tarea de aislamiento, no como paso default de cola rapida.
- API local de SQX queda medida por `api-auth-smoke`: arranca, responde `GET /`, autentica llamadas locales con cabecera `browserToken` y cierra sin procesos vivos.
- Sequential queda diagnosticado como bloqueo metodologico de proyecto: la API lo arranca y lo para, pero SQX registra `0 total` y no actualiza el databank `Sequential`; no debe promocionarse a cola automatica hasta corregir entrada/configuracion.
- Optimizacion aplicada: Sequential ahora no arranca si su input no tiene candidatos `passed`; en la copia `_PERFQ_*`, `MC2` tiene `0 passed`, asi que la cola debe saltar Sequential o cambiar a una rama de diagnostico con input valido, siempre sin reducir filtros.
- Planificador reforzado: `retest_queue_plan_20260522_211803.json` marca `Sequential` con `input=MC2`, `inputFiles=86`, `inputPassed=0`, `inputFailed=86`, `blockedByNoPassedInput=true` y guidance `blocked_no_passed_input`. La cola ya puede evitar tareas caras sin candidatos antes de arrancar SQX.
- Recomendador de siguiente paso: `retest_next_step_20260522_212528.json` propone no repetir Sequential, mantener `SPP` como siguiente experimento pesado tras Synthetic y usar `FOWARD` como alternativa barata si se quiere una smoke de menor coste.
- Politica operador aplicada: `SPP` y `FOWARD` no se recomiendan ni se preparan; `WFM` queda bloqueado por input omitido. `retest_next_step_20260522_213847.json` confirma que no quedan retests pendientes utiles en esta rama y que el bloqueo primario es `Sequential:no_passed_input_candidates`.
- Diagnostico MC2: `RandomizeSpread` `30-50` frente a spread base `1.4` queda marcado como extremo. No se cambia automaticamente porque ajustar rango de estres afecta metodologia; requiere decision explicita y smoke comparativo con evidencia.
- Variante MC2 lista: clon `_PERFQ_MC2SPREAD__..._20260522_215125` preparado con `RandomizeSpread 2.8-7.0`, `MC2`/`Sequential` limpios y proyecto fuente intacto.
- Sequential validado en escala diagnostica: clon `_PERFQ_SEQDIAG_20260522_230211` completo con 8 candidatos de MC2 en `4 min. 50 s.` y produjo 8 salidas `passed`. El bloqueo restante es coste/escala de Sequential con 84 candidatos, no fallo funcional ni falta de persistencia.
- Sequential validado en escala intermedia: clon `_PERFQ_SEQDIAG_20260522_231548` completo con 24 candidatos de MC2 en `12 min. 57 s.` y produjo 24 salidas `passed`. La curva 8 -> 24 se mantiene razonable (`24 s.` -> `28 s.` por estrategia), con estimacion de 84 candidatos alrededor de 45-50 min si se ejecuta entero.
- Cola Sequential lista: `create-sequential-batch-plan` crea clones no solapados y `sequential-batch-merge-review` audita cobertura antes/despues. La primera revision de merge confirma 84 esperados y 0 producidos antes de ejecutar, sin duplicados ni inesperados.
- Cola Sequential cerrada: B01+B02+B03+B04 completados, `84/84` outputs revisados, `0` pendientes, sin duplicados ni inesperados. La copia de inspeccion queda bajo `.local/sqx142_performance/sequential_merge_reviews/`.
- Auditor Sequential final cerrado: `sequential_final_review_20260523_071458.json` confirma que los 84 outputs no son solo archivos presentes, sino estrategias `.sqx` legibles con XML Sequential pasado y parametros auditables; el CSV local queda en `.local/sqx142_performance/sequential_final_reviews/`.
- Promocion MC2 lista en dry-run: `mc2_spread_promotion_20260523_072103.json` valida la regla adaptativa `baseSpread x2-x5`, detecta `baseSpread=1.4`, deriva `2.8-7.0`, confirma evidencia Sequential final y deja diff/backup/rollback planificados.
- Promocion MC2 aplicada y validada: Capa1 base queda en regla adaptativa `baseSpread x2-x5`; copia post-promocion confirma `MC -> MC2 -> Sequential` con resultados naturales (`MC 81/5`, `MC2 84/2`, `Sequential 8/0`).
- Higiene de clones cerrada: 8 clones de diagnostico/lotes antiguos quedan archivados en backup reversible y no cargan en `user/projects`; se conservan evidencias JSON, backups y los dos clones post-promocion utiles.
- Restauracion selectiva lista: `restore-performance-clone` puede recuperar un unico clon `_PERFQ_*` desde `archived_perf_projects` hacia `user/projects`, en dry-run por defecto, sin sobrescribir clones activos y con bloqueo si SQX esta abierto. Dry-run validado con `performance_clone_restore_20260523_082600.json`.
- Cierre auditable preparado: `performance-closeout-report` resume estado, clones activos/archivados, evidencias clave y deja como pregunta obligatoria posterior: que enfoque usar para configurar valores individuales de tareas custom base Capa1/Capa2. No se tocaran esos valores sin decision explicita. Evidencia `performance_closeout_report_20260523_084012.json`: status `ok`, perfil `baseline_143_safe`, 2 clones activos, 8 clones archivados y sin warnings.
- Recomendador de siguiente accion listo: `performance-next-action` revisa status, perfil activo, warnings y evidencias clave para devolver el siguiente comando PERF1. Evidencia actualizada tras Fase 5: incluye `phase5_databank_view_guard`, `mining_pipeline_advisor` y `performance_parallelism_advisor`, sin evidencias faltantes, sin warnings y recomendacion `performance-closeout-report`.
- Fase 7 implementada: `performance-parallelism-advisor` fija perfiles de concurrencia y politica conservadora basada en evidencia. Evidencia `performance_parallelism_advisor_20260523_085248.json`: no paralelizar retests pesados ni mezclar minado/retests hasta smoke dedicado.
- Post-cola: `baseline_143_safe` restaurado, sin procesos vivos esperados y con evidencia local de logs/perfil.
- PERF1 cerrado formalmente: `performance_closeout_report_20260523_095800.json` confirma status `ok`, perfil `baseline_143_safe`, disco `307.9 GB` libre, sin warnings, SPP/FOWARD omitidos por decision operativa y politica MC2 `adaptive_base_spread_x2_to_x5`.
- Recomendador final: `performance_next_action_20260523_095758.json` confirma `completeEnoughForPerf1Closeout=true`, `missingOrBadEvidence=[]` y recomendacion `ready_for_perf1_closeout`.
- Live Guard final: `performance_live_guard_20260523_095802.json` queda `clean_idle`, sin alertas, sin procesos SQX y sin reparacion pendiente.

## Siguiente Capa Recomendada

1. Usar `restore-performance-clone` solo cuando haga falta inspeccionar un lote antiguo en SQX; mantener los clones archivados fuera de `user/projects` mientras no se usen.
2. Mantener `SPP`, `FOWARD` y dependencias fuera; `WFM` sigue bloqueado por politica operativa.
3. Si otro activo tiene spread base distinto, mantener multiplicadores y dejar que la herramienta derive el rango; solo usar `--spread-min/--spread-max` para excepciones metodologicas justificadas.
4. Preguntar a Ivan el enfoque para configurar valores individuales de tareas en los custom base Capa1 y Capa2 antes de editar nada.

Estado tras smoke MC2 diagnostico:

1. `MC2 2.8-7.0` ya produjo candidatos `passed` reales: 84/86.
2. Sequential ya procesa, completa y persiste resultados en escala diagnostica/intermedia y completa: 8/8 en `4 min. 50 s.`, 24/24 en `12 min. 57 s.` y 84/84 por lotes `24+24+24+12`.
3. La ejecucion completa de 84 candidatos debe presupuestarse como tarea larga por lotes; no debe etiquetarse como colgada si el log `ProgressEngine` sigue avanzando o si el databank alcanza la cobertura esperada.
4. Si `2.8-7.0` sigue siendo demasiado duro o demasiado laxo, crear otro clon diagnostico; no tocar el proyecto maestro sin evidencia y decision metodologica explicita.

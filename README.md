# SQX Edge Suite v1

Servicio web Pro para organizar el pipeline SQX Edge, generar Custom Projects `.cfx` para StrategyQuant X, crear views, preparar templates y mantener trazabilidad sin instalacion local del usuario final.

## Estado Actual

- Estado interno: REMOTE-AI-TESTER1 esta aplicado; Edge Factory incluye un agente IA local con Ollama mediado por Flask para operador y sesiones remotas autenticadas en modo tester seguro. El monitor Backend/Tunnel/Ollama sigue siendo local solo para el creador, y el boton `Arrancar` conecta Ollama automaticamente antes de dar listo para testers.
- Estado interno: SQX142-TRANSLATOR1 esta aplicado; el traductor `Local Ollama Translator` aparece en el tab nativo `Source Code` de SQX 142, usando Flask/Ollama local sin OpenAI externo ni API key. Si `localhost:8080` muestra cambios pero la app Electron no, usar el runbook de cache SQX 142.
- Estado interno: SQX142-143-BACKPORT1 esta aplicado; `docs/SQX142_143_BACKPORT_LEDGER.md` registra la compatibilidad 142/143/144, `/api/sqx142/compat/status` expone solo estado local-safe para operador, el monitor local muestra SQX 142 runtime/procesos y `tools\sqx142_compatibility.ps1` hace preflight/backport dry-run por defecto.
- Estado interno: SQX142-PERF1 esta aplicado y cerrado formalmente; `docs/SQX142_PERFORMANCE_ROADMAP.md` gobierna el rendimiento SQX 142 con `/api/sqx142/performance/status`, `tools\sqx142_performance_gate.ps1`, perfiles JVM reversibles, views ligeras, Live Guard e inteligencia local de monitor/agente sin bajar calidad metodologica.
- Estado interno: C1-CONFIG1 esta iniciado; Capa1 queda cerrada, `phase15_capa2_planning` queda documentado con `phase15_capa2_planning_20260524_190708.json`, `phase16_capa2_preflight_snapshot` queda cerrado con `phase16_capa2_preflight_snapshot_20260524_195729.json`, `phase17_capa2_build_questionnaire` queda generado con `phase17_capa2_build_questionnaire_20260524_201405.json` (13 pestañas, 16.647 entradas completas y 6 diferencias base/template para generator profile layer 2), `phase17_capa2_build_what_to_build` queda cerrado con `phase17_capa2_build_what_to_build_target_20260524_204601.json`, `phase17_capa2_build_blocks` queda cerrado con `phase17_capa2_build_blocks_target_20260524_211347.json`, `phase17_capa2_build_data_databanks_resources_options` queda cerrado con `phase17_capa2_build_data_databanks_resources_options_target_20260524_213626.json`, `phase17_capa2_build_rankings` queda cerrado con `phase17_capa2_build_rankings_target_20260524_220916.json`, `phase17_capa2_build_crosschecks` queda cerrado con `phase17_capa2_build_crosschecks_target_20260524_223128.json` y `phase17_capa2_build_static_tabs` queda cerrado con `phase17_capa2_build_static_tabs_target_20260524_231540.json`. WhatToBuild Capa2 registra 67/67 respuestas: `StrategyType=template`, `templateFile` operator-owned solo local, `MarketSides` generator-owned y SL/TP/trailing bounded. Blocks registra 15.995/15.995 respuestas: `EnterAtMarket` only, SL/PT 100%, `TrailingStop` 50%, `ExitAfterBars=false`, señal neutral `AlwaysTrue`, filtro indicador Capa2 y stop/limit entries off. Data/Databanks/Resources/Options registra 48/48 respuestas con periodo `BUILD 2017.10.02-2023.12.31`, `testPrecision=2 simulated`, seed generico `AUDCAD_darwinex/H1/TICK/EETUS`, `Input=Results`, `Output=null`, Options `No Session`, `RealisticGapsHandling=true`, `StoreChartData=false`, y `generator_profiles.json` ya gobierna ventanas Capa2 por timeframe. Rankings registra 173/173 respuestas y se resuelve por `Build-Task1.xml` para tolerar el task title generado por la web: `MaxStrategies=2000`, `passedStrategies=500`, `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false`, `FitPortfolio=false`, `CustomAnalysis=false`, objetivo unico `RExpectancy` y filtros `NumberOfTrades >= 120`, `ProfitFactor >= 1.1`, `Expectancy >= 0.05`. CrossChecks registra 303/303 respuestas: `CrossChecks use=false`, `evaluateAll=false`, cero checks activos, metodos ocultos apagados, `ForceRunCrossChecks=false` protegido y robustez pesada fuera del Build. Static Tabs registra 61/61 respuestas: `FixedAmount` activo, ATMs desactivados, mejora de entradas/tipos de orden apagada, mejora de salidas activa para SL/TP/trailing, Optimization acotado y Notes preservado. No se lanzo SQX, no hubo smoke, no hubo optimizacion ni `Results=passed` forzado. El siguiente bloque es `phase18_capa2_retest0`.
- Estado interno: G9 Per-Message Subagents And Session Bootstrap esta aplicado; cada mensaje activa una evaluacion breve de subagentes/skills disponibles y cada nueva sesion/chat arranca con bootstrap de estado, frentes abiertos, gates y riesgos. Codex conserva la orquestacion y las mutaciones siguen sujetas a fase, backup, diff, tests y confirmacion.
- Ancla Capa2 Phase16: `BS_Filtros_v6*` queda reference-only/trazabilidad y `templateFile` local queda reconocido como artefacto Template Maker C2 operator-owned.
- Estado interno: G8-SQX-AGENT-SKILLS1 esta aplicado antes de RETEST 0; las skills locales SQX, `SQX Test Guardian`, `SQX Docs Curator`, perfiles del agente y handoffs `.local/agent_handoffs/` quedan alineados con C1-CONFIG1 y siguen siendo local-only para operador.
- Estado interno: G8-SQX-ACADEMIC-LOPEZ1 esta aplicado antes de Fase 6 MC; `SQX Academic Lopez` queda local-only para revisar OOS, MC, data snooping, backtest overfitting, PBO/DSR y contaminacion de validacion sin ejecutar cambios.
- Estado interno: WFCO-ACCEPT1 esta aplicado; Edge Factory tiene `Modo básico` por defecto para compradores/testers y `Modo avanzado` para abrir herramientas internas, checks manuales y custom libre sin cambiar motores sensibles.
- Estado interno: WFCO-5 Visual Polish And Desktop QA esta aplicado; Edge Factory ya funciona como superficie Command Premium de escritorio con command strip vivo, stack de estado y Portfolio Lab Capa 2 para importar CSV, ajustar diversidad, clasificar candidatos como portfolio/similar/revisar y exportar shortlist/resumen desde navegador.
- Estado interno: TM-PERF2 esta aplicado; Template Maker delega parsing CSV, apertura ZIP `.sqx`, hash, extraccion XML y precalculo de diversidad a un Web Worker local cuando el navegador lo permite, mostrando progreso por archivo y conservando fallback compatible.
- Estado interno: CFX-RILIS-TARGET1 esta aplicado; Project Generator genera por defecto `.cfx` de descarga con perfil `SQ default / simbolo exacto` para usuarios con Broker profile `SQ default`, manteniendo Dukascopy solo en Retest 1/OOS2.
- Estado comercial: CANONICAL-LINK1 fija `https://sqxedgesuite.org/` como unico enlace externo; REMOTE-RILIS-STANDBY queda activo con REMOTE-PG-SESSION-FIX esta aplicado, CREATOR-IVAN funcionando correctamente y TESTER-RILIS pendiente de retest.
- Estado de despliegue: Windows laptop + API localhost + Cloudflare Tunnel sigue siendo la ruta activa; el dashboard protegido queda como destino interno detras del CTA del dominio raiz.
- Ancla historica: Estado interno: WFCO-3 Content Overhaul esta aplicado; Edge Factory usa copy de decision accionable para guiar del asset al portfolio, explicando en cada etapa que hacer, que sale y que queda pendiente sin devolver al usuario a una lista tecnica de tabs.
- Ancla historica: Estado interno: WFCO-2 Methodology Handoffs esta aplicado; Edge Factory ya arrastra contexto real entre tarjeta, mining seleccionado, Project Generator, Template Maker, Template C2, Capa 2 y Portfolio Lab sin exponer tabs tecnicos como ruta principal.
- Ancla historica: Estado interno: WFCO-1 Edge Factory Shell esta aplicado.
- Ancla historica: Estado comercial: REMOTE-OPS1 valida el portatil como host Pro antes de cualquier siguiente movimiento real con testers o compradores.
- Ancla historica: Estado comercial: REMOTE-8H cycle bridge conecta la decision REMOTE-8L con el paquete de siguiente movimiento sin ejecutar expansion.
- Ancla historica: Estado de despliegue: REMOTE-SUG1 revisa la sugerencia Docker/Ubuntu del tester y mantiene el piloto activo en Windows laptop + API localhost + Cloudflare Tunnel.
- Ultimo commit base verificado antes de S5/M-pre: `d7c0757`.
- Distribucion principal: enlace unico comercial `https://sqxedgesuite.org/`; el usuario final no descarga ZIP, no ejecuta launchers y no instala Python.
- URL de acceso comunicable: `https://sqxedgesuite.org/`. El dashboard protegido bajo Cloudflare Access es infraestructura interna y no se presenta como segundo enlace al cliente.
- Fallback interno conservado: `dist/SQX_Edge_Tool_Portable_Tester_20260512_184709.zip` con SHA256 `247797085555789B3CE07E7BC7E72AC7F08B0AB7FFF8C552DB9719964EFA4CE3`.
- Siguiente paso recomendado: esperar el retest de TESTER-RILIS para REMOTE y entregarle un `.cfx` nuevo generado con perfil `SQ default / simbolo exacto` para registrar si abre sin `BrokerDto.getName()`. En paralelo, mantener REMOTE-RILIS-STANDBY hasta cerrar el retest remoto; CFX-METHOD2 queda listo cuando llegue la base Capa 2 v2.
- Ancla historica: Siguiente paso recomendado: rellenar evidencia privada REMOTE-OPS1 en `.local/remote_service/remote_ops1_laptop_readiness.local.json`; si devuelve GO, volver a REMOTE-8H private package evidence.
- Ancla historica: Siguiente paso recomendado: rellenar evidencia privada REMOTE-8H desde una decision REMOTE-8L `prepare_next_controlled_movement` y pedir aprobacion REMOTE-8I antes de ejecutar nada.
- Ultima mejora funcional: `dukas_mt5_ohlc_download.py --recent-bars` descarga 33 activos x 4 timeframes desde MT5; A56 devuelve GO con A55/A53/A54 en verde.

## Limpieza Local

Para retirar caches, builds y artefactos generados sin tocar runtime portable, venv, licencias ni evidencia privada:

```powershell
powershell -ExecutionPolicy Bypass -File tools\clean_workspace.ps1 -Aggressive
```

El modo agresivo conserva el ZIP tester mas reciente en `dist/` y elimina ZIPs/builds antiguos que se pueden regenerar.

Para refrescar la cache Electron de SQX 142 cuando `localhost:8080` ya sirve bundles nuevos pero la app local no los muestra:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx142_electron_cache_refresh.ps1 -SQXRoot "C:\BOTS\Versiones\SQX_142_Crack" -Restart
```

La limpieza mueve caches a backup bajo `.local_cache_backups` dentro de la carpeta SQX; no borra proyectos, databanks, licencias ni archivos del repo. Ver `docs/maintenance/SQX142_ELECTRON_CACHE_RUNBOOK.md`.

## SQX 142 / 143 Compatibility

La build 143 local queda como referencia controlada para estabilizar SQX 142 sin copiar motor, licencia ni ejecutables de StrategyQuant. El ledger vivo es `docs/SQX142_143_BACKPORT_LEDGER.md`.

Comandos operador:

```powershell
tools\sqx142_compatibility.ps1 status
tools\sqx142_compatibility.ps1 compare
tools\sqx142_compatibility.ps1 apply-runtime
```

`apply-runtime` es dry-run si no se pasa `--apply`. El monitor local consulta `/api/sqx142/compat/status` y muestra runtime SQX 142, procesos vivos y estado de hardening sin exponer rutas a usuarios remotos.

## SQX 142 Performance Gate

El rendimiento de SQX 142 se optimiza por medicion, perfiles seguros y limpieza reversible, nunca reduciendo calidad de metodologia. El roadmap vivo es `docs/SQX142_PERFORMANCE_ROADMAP.md`.

Comandos operador:

```powershell
tools\sqx142_performance_gate.ps1 status
tools\sqx142_performance_gate.ps1 snapshot
tools\sqx142_performance_gate.ps1 create-views
tools\sqx142_performance_gate.ps1 smoke-start
tools\sqx142_performance_gate.ps1 begin-project-mc-smoke
tools\sqx142_performance_gate.ps1 project-mc-snapshot
tools\sqx142_performance_gate.ps1 project-mc-diff
tools\sqx142_performance_gate.ps1 project-mining-pipeline-advisor
tools\sqx142_performance_gate.ps1 phase5-databank-view-guard
tools\sqx142_performance_gate.ps1 project-retest-queue-plan
tools\sqx142_performance_gate.ps1 project-retest-next-step --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --log-limit 80
tools\sqx142_performance_gate.ps1 mc2-spread-diagnostic --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --log-limit 80
tools\sqx142_performance_gate.ps1 create-mc2-spread-variant --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --spread-min 2.8 --spread-max 7.0 --apply
tools\sqx142_performance_gate.ps1 create-sequential-diagnostic-variant --project-name "_PERFQ_MC2SPREAD__PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338_20260522_215125" --max-passed 8 --apply
tools\sqx142_performance_gate.ps1 queue-task-smoke "Sequential" --project-name "_PERFQ_SEQDIAG_20260522_230211" --apply --max-seconds 900 --stall-seconds 240 --poll-seconds 20 --api-ready-timeout 120 --start-settle-seconds 45
tools\sqx142_performance_gate.ps1 create-sequential-diagnostic-variant --project-name "_PERFQ_MC2SPREAD__PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338_20260522_215125" --max-passed 24 --apply
tools\sqx142_performance_gate.ps1 queue-task-smoke "Sequential" --project-name "_PERFQ_SEQDIAG_20260522_231548" --apply --max-seconds 1800 --stall-seconds 360 --poll-seconds 20 --api-ready-timeout 120 --start-settle-seconds 45
tools\sqx142_performance_gate.ps1 create-sequential-batch-plan --project-name "_PERFQ_MC2SPREAD__PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338_20260522_215125" --batches "24,24,24,12" --apply
tools\sqx142_performance_gate.ps1 sequential-batch-merge-review --plan-evidence sequential_batch_plan_20260522_234314.json
tools\sqx142_performance_gate.ps1 sequential-final-review --latest --write-csv --apply
tools\sqx142_performance_gate.ps1 promote-mc2-spread-to-base --project-name "Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1" --min-multiplier 2 --max-multiplier 5
tools\sqx142_performance_gate.ps1 performance-clone-hygiene --keep-newest 2
tools\sqx142_performance_gate.ps1 restore-performance-clone --archive-stamp 20260523_081819 --clone-name _PERFQ_SEQBATCH_B01_001-024_20260522_234217
tools\sqx142_performance_gate.ps1 performance-closeout-report
tools\sqx142_performance_gate.ps1 performance-next-action
tools\sqx142_performance_gate.ps1 performance-parallelism-advisor
tools\sqx142_performance_gate.ps1 live-guard
tools\sqx142_performance_gate.ps1 clone-performance-project
tools\sqx142_performance_gate.ps1 prepare-queue-step MC --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --apply --launch
tools\sqx142_performance_gate.ps1 sqx-local-api probe
tools\sqx142_performance_gate.ps1 api-auth-smoke --apply --api-ready-timeout 120
tools\sqx142_performance_gate.ps1 sequential-smoke --project-name "_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338" --apply --max-seconds 180 --stall-seconds 60 --api-ready-timeout 120
```

`create-views`, `apply-profile`, `smoke-start` y `live-guard` son dry-run si no se pasa `--apply`. El monitor local consulta `/api/sqx142/performance/status` para mostrar perfil activo, disco, views, ultima evidencia, Live Guard y siguiente accion recomendada sin exponer rutas a usuarios remotos. Esta inteligencia es pasiva y bajo demanda: se activa al arrancar/refrescar el monitor, al consultar el agente y al detectar SQX abierto, sin proceso residente adicional.

Tras liberar espacio en `C:`, el gate queda en verde con mas de 300 GB libres. La comparativa JVM validada mantiene `baseline_143_safe` como default, deja `retest_robust` como candidato para Monkey/Synthetic/WFM y `mining_fast_safe` como candidato para minado real. Las escrituras de perfil son atomicas y el status detecta configs corruptos o no alineados. `project-mining-pipeline-advisor` cubre Fase 3: lee Build, databanks, ranking, condiciones, bloques y riesgos de eficiencia antes de proponer un smoke de minado en clon `_PERFQ_*`.

El smoke de databanks MC lee `.sqx` directamente sin abrir SQX: `Monkey Test` queda validado con 86 estrategias, 200 simulaciones y mezcla natural 53 passed / 33 failed; `Syntetic` queda validado con 86 estrategias, 100 simulaciones y mezcla natural 85 passed / 1 failed. El proyecto real fue reasignado con backup a las views dedicadas `MC MONKEY RETEST` y `MC SYNTHETIC RETEST`. Para smoke real, `begin-project-mc-smoke --apply --launch` prepara snapshot inicial, perfil `retest_robust` y arranque de SQX; despues de ejecutar Monkey/Synthetic, `project-mc-snapshot` y `project-mc-diff` comparan el resultado.

Smoke real 2026-05-22: Monkey y Syntetic se reejecutaron en SQX 142, actualizaron timestamps, conservaron metodos/simulaciones y mantuvieron la mezcla natural de passed/failed sin warnings de diff ni `hs_err_pid*.log`.

Post-smoke: SQX se cerro, `baseline_143_safe` quedo restaurado y el status vuelve a `ok`. `project-log-summary` mide logs del proyecto: Monkey tardo `5 min. 35 s.`, Synthetic `4 min. 7 s.`, y el 91% del tiempo se concentra en `Monte Carlo retest methods`.

Limpieza local aplicada: `archive-old-logs --keep-days 2 --apply` conserva hoy/ayer, comprime 128 logs antiguos en `SQX_142_Crack_local_backups\archived_logs`, verifica el ZIP y elimina los originales archivados. `user/log` queda en ~141 MB.

Scheduling aplicado: `project-retest-queue-plan` genera una cola robusta desde el `project.cfx` y los logs reales, marcando MC/Monkey/Synthetic/SPP/WFM como tareas a ejecutar solas con perfil `retest_robust`. `clone-performance-project --apply` creo la copia `_PERFQ_Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1_20260522_190338`, verificada con snapshot MC, para medir cambios sin contaminar el proyecto maestro.

Smoke de cola real: `MC` completo en `2 min. 31 s.` con `83 passed / 3 failed`; `MC 2` original completo en `4 min. 17 s.` con `0 passed / 86 failed`, rechazo natural por filtros. El perfil default quedo restaurado a `baseline_143_safe`. `sqx-local-api` y `api-auth-smoke` dejan preparado un wrapper local-only con `localhost:8080`, cookies, cabeceras tipo navegador y cabecera `browserToken` local no expuesta; el bloqueo `Remote access disabled` queda resuelto con evidencia `api_auth_smoke_20260522_205359.json` y `/main/checkaccess` responde `Access granted`. `Sequential` ya arranca por API, pero requiere observabilidad especial porque puede optimizar durante minutos sin escribir databank. La guardia previa evita repetir coste cuando el input no tiene candidatos: `sequential_smoke_20260522_211636.json` detecta `MC2` con 86 archivos y `0 passed`, salta el arranque SQX con `no_input_candidates` y conserva filtros intactos. `SPP` y `FOWARD` quedan omitidos por decision operativa; `WFM` queda bloqueado por depender de `SPP`. `project-retest-next-step` confirma que el foco primario es diagnosticar `MC2 -> Sequential`. El diagnostico XML confirma `MC 2` con `RandomizeSpread` `30-50` frente a spread base `1.4` (`21.43x-35.71x`), causa probable del rechazo total. La variante diagnostica `_PERFQ_MC2SPREAD__..._20260522_215125` cambia solo `MC 2` a `2.8-7.0`; el smoke completo procesa 86 estrategias en `5 min. 5 s.` con `84 passed / 2 failed` naturales. Sequential con ese MC2 desbloqueado muestra actividad real en `ProgressEngine`; el smoke diagnostico `_PERFQ_SEQDIAG_20260522_230211` con 8 candidatos completo en `4 min. 50 s.`, produjo 8 salidas y `8 passed / 0 failed`. El lote intermedio `_PERFQ_SEQDIAG_20260522_231548` con 24 candidatos completo en `12 min. 57 s.`, produjo 24 salidas y `24 passed / 0 failed`; el bloqueo restante es coste/escala. La cola real queda cerrada como `24+24+24+12` en cuatro clones `_PERFQ_SEQBATCH_*`, con merge final `sequential_batch_merge_review_20260523_063406.json`: `84/84`, cero missing, cero inesperados y cero duplicados. El auditor `sequential-final-review` confirma `84/84` `.sqx` legibles, `84` resultados Sequential passed, `569` areas estables y genera CSV local para inspeccion de parametros sin tocar el proyecto maestro. La promocion MC2 queda aplicada con regla adaptativa `spread base x2-x5`: en USDJPY/H4 deriva `2.8-7.0` desde spread base `1.4`, cambia solo `MC 2 / RandomizeSpread` y deja rollback por evidencia `mc2_spread_promotion_20260523_072626.json`. La copia post-promocion valida `MC 81/5` en `2 min. 17 s.`, `MC2 84/2` en `5 min. 46 s.` y `Sequential 8/8` en `4 min. 52 s.`. `queue-task-smoke` espera ahora 180 s por defecto antes de arrancar el proyecto para evitar starts prematuros mientras SQX carga databanks grandes. `performance-clone-hygiene --keep-newest 2 --apply` archiva reversiblemente 8 clones antiguos y deja activos solo los 2 clones post-promocion. `restore-performance-clone` recupera un clon archivado concreto desde `archived_perf_projects` a `user/projects` en dry-run por defecto, bloquea colisiones y exige SQX cerrado al aplicar. `performance-closeout-report` consolida estado, evidencias y la pregunta pendiente obligatoria sobre el enfoque de valores individuales para tareas custom base Capa1/Capa2. `performance-next-action` lee el estado y decide si falta reparar warnings, refrescar evidencia, restaurar baseline o cerrar PERF1. `performance-parallelism-advisor` cubre Fase 7 con perfiles de concurrencia conservadores: un SQX/proyecto pesado a la vez, sin mezclar minado con retests, hasta que un smoke paralelo dedicado demuestre lo contrario. `phase5-databank-view-guard --apply --archive-views` cubre Fase 5: reasigna databanks a views ligeras/especializadas y archiva views legacy pesadas con backup reversible. Fase 9 queda integrada: `/api/sqx142/performance/status` devuelve `intelligence` con perfil, views, evidencia clave, recomendacion activa y modo pasivo `passive_on_probe`; el monitor y el agente consumen ese resumen local-only. `live-guard` añade el cinturon final: vigila logs, crash JVM, API local y procesos mientras SQX esta abierto, y solo aplica reparaciones seguras tras cierre. PERF1 queda cerrado formalmente con `performance_closeout_report_20260523_095800.json`, `performance_next_action_20260523_095758.json` y Live Guard limpio `performance_live_guard_20260523_095802.json`.

## SQX 142 Custom Task Config Gate

C1-CONFIG1 configura Capa1 base tarea por tarea y pestaña por pestaña. El donor es `Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1`, pero la promocion a base es selectiva: no se copian simbolos, timeframe, active flags, resultados ni estado de ejecucion. El roadmap vivo es `docs/SQX142_CUSTOM_TASK_CONFIG_ROADMAP.md`.

Comandos operador:

```powershell
tools\sqx142_task_config_gate.ps1 status
tools\sqx142_task_config_gate.ps1 preflight --apply
tools\sqx142_task_config_gate.ps1 promote-views --target both
tools\sqx142_task_config_gate.ps1 task-questionnaires --task-title "Build BS_Volatilidad_v6 · Capa1 L+S H4" --write
tools\sqx142_task_config_gate.ps1 questionnaire --task-title "MC 2" --tab "CrossChecks" --write
tools\sqx142_task_config_gate.ps1 record-answer --task-title "MC 2" --tab "CrossChecks" --question-id "<id>" --answer "<answer>"
tools\sqx142_task_config_gate.ps1 mc2-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 mc2-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 mc2-data-databanks-resources-options-target --target both
tools\sqx142_task_config_gate.ps1 mc2-data-databanks-resources-options-target --target both --apply
tools\sqx142_task_config_gate.ps1 mc2-passive-generation-target --target both
tools\sqx142_task_config_gate.ps1 mc2-passive-generation-target --target both --apply
tools\sqx142_task_config_gate.ps1 mc2-static-tabs-target --target both
tools\sqx142_task_config_gate.ps1 mc2-static-tabs-target --target both --apply
tools\sqx142_task_config_gate.ps1 mc2-closeout-report --target both
tools\sqx142_task_config_gate.ps1 mc2-closeout-report --target both --write
tools\sqx142_task_config_gate.ps1 sequential-open-report --target both
tools\sqx142_task_config_gate.ps1 sequential-open-report --target both --write
tools\sqx142_task_config_gate.ps1 sequential-data-databanks-resources-options-target --target both
tools\sqx142_task_config_gate.ps1 sequential-data-databanks-resources-options-target --target both --apply
tools\sqx142_task_config_gate.ps1 sequential-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 sequential-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 sequential-passive-generation-target --target both
tools\sqx142_task_config_gate.ps1 sequential-passive-generation-target --target both --apply
tools\sqx142_task_config_gate.ps1 sequential-static-tabs-target --target both
tools\sqx142_task_config_gate.ps1 sequential-static-tabs-target --target both --apply
tools\sqx142_task_config_gate.ps1 sequential-closeout-report --target both
tools\sqx142_task_config_gate.ps1 sequential-closeout-report --target both --write
tools\sqx142_task_config_gate.ps1 monkey-open-report --target both
tools\sqx142_task_config_gate.ps1 monkey-open-report --target both --write
tools\sqx142_task_config_gate.ps1 monkey-data-databanks-resources-options-target --target both
tools\sqx142_task_config_gate.ps1 monkey-data-databanks-resources-options-target --target both --apply
tools\sqx142_task_config_gate.ps1 monkey-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 monkey-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 monkey-passive-generation-target --target both
tools\sqx142_task_config_gate.ps1 monkey-passive-generation-target --target both --apply
tools\sqx142_task_config_gate.ps1 monkey-static-tabs-target --target both
tools\sqx142_task_config_gate.ps1 monkey-static-tabs-target --target both --apply
tools\sqx142_task_config_gate.ps1 monkey-closeout-report --target both
tools\sqx142_task_config_gate.ps1 monkey-closeout-report --target both --write
tools\sqx142_task_config_gate.ps1 synthetic-open-report --target both
tools\sqx142_task_config_gate.ps1 synthetic-open-report --target both --write
tools\sqx142_task_config_gate.ps1 synthetic-data-databanks-resources-options-target --target both
tools\sqx142_task_config_gate.ps1 synthetic-data-databanks-resources-options-target --target both --apply
tools\sqx142_task_config_gate.ps1 synthetic-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 synthetic-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 synthetic-passive-generation-target --target both
tools\sqx142_task_config_gate.ps1 synthetic-passive-generation-target --target both --apply
tools\sqx142_task_config_gate.ps1 synthetic-static-tabs-target --target both
tools\sqx142_task_config_gate.ps1 synthetic-static-tabs-target --target both --apply
tools\sqx142_task_config_gate.ps1 synthetic-closeout-report --target both
tools\sqx142_task_config_gate.ps1 synthetic-closeout-report --target both --write
tools\sqx142_task_config_gate.ps1 spp-open-report --target both
tools\sqx142_task_config_gate.ps1 spp-open-report --target both --write
tools\sqx142_task_config_gate.ps1 spp-data-databanks-resources-options-target --target both
tools\sqx142_task_config_gate.ps1 spp-data-databanks-resources-options-target --target both --apply
tools\sqx142_task_config_gate.ps1 spp-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 spp-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 spp-static-tabs-target --target both
tools\sqx142_task_config_gate.ps1 spp-static-tabs-target --target both --apply
tools\sqx142_task_config_gate.ps1 spp-closeout-report --target both
tools\sqx142_task_config_gate.ps1 spp-closeout-report --target both --write
tools\sqx142_task_config_gate.ps1 task-questionnaires --task-title "SPP" --write
tools\sqx142_task_config_gate.ps1 wfm-open-report --target both
tools\sqx142_task_config_gate.ps1 wfm-open-report --target both --write
tools\sqx142_task_config_gate.ps1 wfm-data-databanks-resources-options-target --target both
tools\sqx142_task_config_gate.ps1 wfm-data-databanks-resources-options-target --target both --apply
tools\sqx142_task_config_gate.ps1 wfm-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 wfm-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 task-questionnaires --task-title "WFM" --write
```

Fase 1 ya promociona solo las views allowlisted de databanks hacia base local y template repo. Fase 2 genera cuestionarios Build completos: todas las entradas detectadas se guardan por defecto, incluidas rutas XML repetidas con indice estable. Las respuestas completas viven en `.local/sqx142_task_config/`; los docs solo reciben resumen limpio al cerrar fase.
Fase 8 `Sequential` queda cerrada formalmente con `phase8_sequential_closeout_20260524_085653.json`: `Input=MC2`, `Output=Sequential`, portador dual `Data+CustomData`, Options inertes, Project Generator sin ventana horaria para `AutomaticRetest-Task3.xml`, solo `SequentialOptimization` activo, `ApplyToStrategy=false`, aceptacion `80/5/25`, placeholder `Strategies to improve` normalizado a `MC2`, `PartsToImprove` pasivo, evolution restarts apagados, no Signals, no Stop/Limit entry blocks, Indicators preservados, solo `EnterAtMarket` + `ExitAfterBars` probability `100`, Rankings inert, `FitPortfolio=false`, `CustomAnalysis.filter=false`, ATMs disabled, FixedSize active y `SelectedStrategies` empty. Todos los guards de Sequential y MC2 previo quedan `ok=true`, `changed=false`, `changedActionCount=0`, `guardOk=true`, con `issues=[]`, `warnings=[]`, `processes=[]`. Siguiente bloque exacto: `phase9_monkey_test_open`.
Fase 9 `Monkey Test` queda abierta con `phase9_monkey_test_open_20260524_091714.json`: `AutomaticRetest-Task6.xml`, `Input=Sequential`, `Output=Monkey Test`, `MonteCarloRetest` como unico crosscheck activo, metodo `RealMonkeyTest`, `NumberOfSimulations=200`, `MCUseFullSample=true` y `MaxChange=90`. El open no lanza SQX ni cambia CFX; registra decisiones pendientes sobre Data/CustomData, recursos generator-owned, filtros de aceptacion inactivos y metodos activos ocultos en checks inactivos. El cuestionario completo de Monkey Test queda generado en ledger local con `20,036` entradas detectadas y `12,332` diferencias donor/base. Siguiente bloque exacto: `phase9_monkey_test_data_databanks_resources_options`.
`phase9_monkey_test_data_databanks_resources_options` queda cerrado con `phase9_monkey_test_data_databanks_resources_options_20260524_093446.json`: portador dual `Data+CustomData` sincronizado en `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, seed `AUDCAD_darwinex/H1` con spread `2.0`, `Input=Sequential`, `Output=Monkey Test`, recursos `TICK/EETUS` sin sesiones y Options inertes. Project Generator ya no inyecta ventanas horarias en `AutomaticRetest-Task6.xml`; los customs generados mantienen simbolo/timeframe/spread adaptados por activo. Dry-run posterior queda idempotente (`changed=false`, `changedActionCount=0`, `guardOk=true`). Siguiente bloque exacto: `phase9_monkey_test_crosschecks`.
`phase9_monkey_test_crosschecks` queda cerrado con `phase9_monkey_test_crosschecks_20260524_101913.json`: `monkey-crosschecks-target` mantiene `AutomaticRetest-Task6.xml` con solo `MonteCarloRetest`/`RealMonkeyTest` activo, `NumberOfSimulations=200`, `MCUseFullSample=true`, `MCBacktestPrecision=-1`, `MaxChange=90`, filtros activos `NetProfit >= 50%` y `Max DD <= 200%`, `SyntheticBootstrapV2/V3` apagados y metodos ocultos de `MonteCarloManipulation`/`WhatIf` desactivados. Ledger local respondido para `Monkey Test > CrossChecks` (`372/372`) y dry-run posterior idempotente (`changed=false`, `changedActionCount=0`, `guardOk=true`). Siguiente bloque exacto: `phase9_monkey_test_passive_generation`.
`phase9_monkey_test_passive_generation` queda cerrado con `phase9_monkey_test_passive_generation_20260524_104201.json`: `monkey-passive-generation-target` deja `AutomaticRetest-Task6.xml` como retest pasivo puro desde `Sequential`, normaliza `StrategyType.improveDatabank=Sequential`, apaga `PartsToImprove`, evolution restarts y placeholders de generacion, conserva Indicators de metodologia/BlockSettings, desactiva Signals y Stop/Limit entry blocks, y permite solo `EnterAtMarket` + `ExitAfterBars` probability `100` sin salidas por dias. Ledger local respondido para `Monkey Test > PartsToImprove` (`8/8`), `WhatToBuild` (`67/67`) y `Blocks` (`17.583/17.583`); dry-run posterior idempotente (`changed=false`, `changedActionCount=0`, `guardOk=true`). Siguiente bloque exacto: `phase9_monkey_test_static_tabs`.
`phase9_monkey_test_static_tabs` queda cerrado con `phase9_monkey_test_static_tabs_20260524_105942.json`: `monkey-static-tabs-target` cierra las pestanas estaticas de `AutomaticRetest-Task6.xml` sin tocar `RealMonkeyTest`: Rankings inerte (`type=never`, `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false`, `FitPortfolio.active=false`, sin condiciones extra), `FixedSize` activo, ATMs apagado, Notes preservado, `SelectedStrategies` vacio/ausente aceptado y `CustomData` dual sincronizado con Data (`ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, commission `0.0`, `MainTestValues` correctos). Ledger local respondido para `Monkey Test > Rankings` (`23/23`), `ATMs` (`9/9`), `RiskMoneyManagement` (`25/25`), `Notes` (`1/1`), `SelectedStrategies` (`0/0`) y `CustomData` (`6/6`); dry-run posterior idempotente (`changed=false`, `changedActionCount=0`, `guardOk=true`). Siguiente bloque exacto: `phase9_monkey_test_closeout`.
`phase9_monkey_test_closeout` queda cerrado con `phase9_monkey_test_closeout_20260524_114205.json`: `monkey-closeout-report` consolida Sequential previo y los cuatro guards Monkey (`monkey-data-databanks-resources-options-target`, `monkey-crosschecks-target`, `monkey-passive-generation-target`, `monkey-static-tabs-target`) sobre base local y template repo, todos en dry-run idempotente con `ok=true`, `issues=[]`, `warnings=[]`, `processes=[]`, `changed=false`, `changedActionCount=0` y `guardOk=true`. Monkey queda como gate de robustez natural `Input=Sequential / Output=Monkey Test`, `RealMonkeyTest`, `NumberOfSimulations=200`, `MCUseFullSample=true`, `MaxChange=90`, filtros `NetProfit >= 50%` y `Max DD <= 200%`, sin ejecucion SQX ni forzar `Results=passed`. Siguiente bloque exacto: `phase10_synthetic_open`.
`phase10_synthetic_open` queda abierto con `phase10_synthetic_open_20260524_115744.json`: `synthetic-open-report` confirma el alias historico `Synthetic / Syntetic`, task real `Syntetic`, `AutomaticRetest-Task5.xml`, `Input=Monkey Test`, `Output=Syntetic`, `MonteCarloRetest` activo con `SyntheticBootstrapV3`, `NumberOfSimulations=100`, `MCUseFullSample=true`, `BlockSize=20`, `WarmupBars=200` y `PreservePct=85`. El open no lanza SQX y no muta CFX; registra warnings pendientes sobre `Data+CustomData`, metodos activos ocultos en checks inactivos y `StrategyType.improveDatabank=Strategies to improve`. Cuestionario local generado para `Syntetic` con `20.008` entradas detectadas y `12.341` diferencias donor/base. Siguiente bloque exacto: `phase10_synthetic_data_databanks_resources_options`.
`phase10_synthetic_data_databanks_resources_options` queda cerrado con `phase10_synthetic_data_databanks_resources_options_20260524_121641.json`: `synthetic-data-databanks-resources-options-target` mantiene `AutomaticRetest-Task5.xml` con portador dual `Data+CustomData` sincronizado en `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, sin OOS interno, seed generico `AUDCAD_darwinex/H1` spread `2.0`, `Input=Monkey Test`, `Output=Syntetic`, recursos `TICK/EETUS` sin sesiones y Options inertes (`LimitTimeRange=false`, `RealisticGapsHandling=false`, `StoreChartData=false`). Project Generator ya no inyecta ventanas horarias en `AutomaticRetest-Task5.xml`; los customs generados mantienen simbolo/timeframe/spread adaptados por activo sin convertir Synthetic en filtro horario. El unico cambio CFX aplicado fue normalizar `Data/Chart spread` de `2` a `2.0` en base local y template repo, con backup local y diff `phase10_synthetic_data_databanks_resources_options_target_20260524_121559.json`; el dry-run posterior queda idempotente (`changed=false`, `changedActionCount=0`, `guardOk=true`). Ledger local respondido para `Syntetic > Data` (`7/7`), `Syntetic > Databanks` (`2/2`), `Syntetic > Resources` (`1.899/1.899`) y `Syntetic > Options` (`34/34`). Siguiente bloque exacto: `phase10_synthetic_crosschecks`.
`phase10_synthetic_crosschecks` queda cerrado con `phase10_synthetic_crosschecks_20260524_123911.json`: `synthetic-crosschecks-target` mantiene `AutomaticRetest-Task5.xml` con solo `MonteCarloRetest`/`SyntheticBootstrapV3` activo, `NumberOfSimulations=100`, `MCUseFullSample=true`, `MCBacktestPrecision=-1`, `BlockSize=20`, `WarmupBars=200` y `PreservePct=85`. Se preserva el filtro Synthetic propio de `NetProfit` MC retest confidence `85` frente a main `NetProfit`, no se copian filtros Monkey, no se fuerza `Results=passed`, `RealMonkeyTest` y `SyntheticBootstrapV2` quedan apagados, y los metodos ocultos de `MonteCarloManipulation`/`WhatIf` quedan inertes. El apply usa backup `phase10_synthetic_crosschecks_20260524_123823`, diff `phase10_synthetic_crosschecks_target_20260524_123825.json`, dry-run posterior idempotente `phase10_synthetic_crosschecks_target_20260524_123846.json` (`changed=false`, `changedActionCount=0`, `guardOk=true`) y ledger local `Syntetic > CrossChecks` (`345/345`). Siguiente bloque exacto: `phase10_synthetic_passive_generation`.
`phase10_synthetic_passive_generation` queda cerrado con `phase10_synthetic_passive_generation_20260524_130638.json`: `synthetic-passive-generation-target` deja `AutomaticRetest-Task5.xml` como retest pasivo puro desde `Monkey Test`, normaliza `StrategyType.improveDatabank=Monkey Test`, apaga `PartsToImprove`, evolution restarts y restos de generacion, conserva Indicators de metodologia/BlockSettings, desactiva Signals y Stop/Limit entry blocks, y permite solo `EnterAtMarket` + `ExitAfterBars` probability `100` sin salidas por dias ni forzar `Results=passed`. El apply usa backup `phase10_synthetic_passive_generation_20260524_130601`, diff `phase10_synthetic_passive_generation_target_20260524_130603.json`, dry-run posterior idempotente `phase10_synthetic_passive_generation_target_20260524_130615.json` (`changed=false`, `changedActionCount=0`, `guardOk=true`) y ledger local `Syntetic > PartsToImprove` (`8/8`), `WhatToBuild` (`67/67`) y `Blocks` (`17.583/17.583`). Siguiente bloque exacto: `phase10_synthetic_static_tabs`.
`phase10_synthetic_static_tabs` queda cerrado con `phase10_synthetic_static_tabs_20260524_133337.json`: `synthetic-static-tabs-target` cierra superficies inertes sin tocar `SyntheticBootstrapV3`: Rankings inerte (`type=never`, `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false`, `FitPortfolio.active=false`, `CustomAnalysis.filter=false/method=none`, sin condiciones extra), `FixedSize` activo, ATMs apagado, Notes preservado, `SelectedStrategies` vacio/ausente aceptado y `CustomData` dual sincronizado con Data (`ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, commission `0.0`, `MainTestValues` correctos). El apply usa backup `phase10_synthetic_static_tabs_20260524_133242`, diff `phase10_synthetic_static_tabs_target_20260524_133244.json`, dry-run posterior idempotente `phase10_synthetic_static_tabs_target_20260524_133254.json` (`changed=false`, `changedActionCount=0`, `guardOk=true`) y ledger local `Syntetic > Rankings` (`22/22`), `ATMs` (`9/9`), `RiskMoneyManagement` (`25/25`), `Notes` (`1/1`), `SelectedStrategies` (`1/0` empty accepted) y `CustomData` (`6/6`). Siguiente bloque exacto: `phase10_synthetic_closeout`.
`phase10_synthetic_closeout` queda cerrado con `phase10_synthetic_closeout_20260524_135151.json`: `synthetic-closeout-report` consolida Monkey previo y los cuatro guards Synthetic (`synthetic-data-databanks-resources-options-target`, `synthetic-crosschecks-target`, `synthetic-passive-generation-target`, `synthetic-static-tabs-target`) sobre base local y template repo, todos en dry-run idempotente con `ok=true`, `issues=[]`, `warnings=[]`, `processes=[]`, `changed=false`, `changedActionCount=0` y `guardOk=true`. Synthetic queda como gate de robustez natural `Input=Monkey Test / Output=Syntetic`, `SyntheticBootstrapV3`, `NumberOfSimulations=100`, `MCUseFullSample=true`, `MCBacktestPrecision=-1`, `BlockSize=20`, `WarmupBars=200`, `PreservePct=85`, filtro dedicado `NetProfit` MC retest confidence `85` frente a main `NetProfit`, sin ejecucion SQX ni forzar `Results=passed`. Evidencia dry-run de cierre: `phase10_synthetic_data_databanks_resources_options_target_20260524_135137.json`, `phase10_synthetic_crosschecks_target_20260524_135138.json`, `phase10_synthetic_passive_generation_target_20260524_135139.json` y `phase10_synthetic_static_tabs_target_20260524_135140.json`. Siguiente bloque exacto: `phase11_spp_open`.
`phase11_spp_open` queda abierto con `phase11_spp_open_20260524_140703.json`: `spp-open-report` confirma `SPP`, `AutomaticRetest-Task7.xml`, `Input=Syntetic`, `Output=SPP`, unico crosscheck activo `OptProfileSysParamPermutation`, `MaxTests=3000`, `DistributionUp=20`, `DistributionDown=20`, `Steps=25`, `ProfitOptPct=30`, `UniformDistrChanges=15` y 2 condiciones activas (`NetProfit` y `DrawdownPct`). El gate queda `ok=true`, `issues=[]`, `processes=[]`, no lanza SQX, no ejecuta SPP y fija politica `configuration_review_only_no_smoke_no_optimization`; avisa que SPP usa `CustomData` como portador canonico, que hay metodos activos ocultos en crosschecks inactivos para limpiar/revisar y que WFM depende de SPP pero sigue review-only/bloqueado. Cuestionario local completo `_task_summary_20260524_140647.json`: 7 tabs, 180 entradas y 9 diferencias donor/base. Siguiente bloque exacto: `phase11_spp_data_databanks_resources_options`.
`phase11_spp_data_databanks_resources_options` queda cerrado con `phase11_spp_data_databanks_resources_options_20260524_144847.json`: `spp-data-databanks-resources-options-target` mantiene `AutomaticRetest-Task7.xml` en portador unico `CustomData`, sin `Data`, con `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, semilla `AUDCAD_darwinex/H1` spread `2.0`, `Input=Syntetic`, `Output=SPP`, resources `TICK/EETUS` sin sesiones y Options inertes (`LimitTimeRange=false`, `RealisticGapsHandling=false`, `StoreChartData=false`). Project Generator ya no inyecta ventanas horarias en `AutomaticRetest-Task7.xml`; los customs generados adaptan simbolo/timeframe/spread/recursos por activo. El apply no necesitó cambiar CFX (`changed=false`, `changedActionCount=0`, `guardOk=true`) y el ledger local queda respondido para `SPP > CustomData` (`6/6`), `Databanks` (`2/2`), `Resources` (`4/4`) y `Options` (`34/34`). Siguiente bloque exacto: `phase11_spp_crosschecks`.
`phase11_spp_crosschecks` queda cerrado con `phase11_spp_crosschecks_20260524_152918.json`: `spp-crosschecks-target` mantiene `AutomaticRetest-Task7.xml` con solo `OptProfileSysParamPermutation` activo, `MaxTests=3000`, `DistributionUp=20`, `DistributionDown=20`, `Steps=25`, `WhatToParametrize` metodologico, filtros SPP `NetProfit >= 50%` main y `DrawdownPct <= 200%` main, `ForceRunCrossChecks=false`, sin ejecutar SPP ni forzar `Results=passed`. Se apagan los metodos ocultos de `MonteCarloManipulation` y `MonteCarloRetest`, y el setup anidado queda normalizado a `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, seed `AUDCAD_darwinex/H1` spread `2.0`. El apply usa backup `phase11_spp_crosschecks_20260524_152857`, diff `phase11_spp_crosschecks_target_20260524_152857.json`, dry-run posterior idempotente `phase11_spp_crosschecks_target_20260524_152905.json` (`changed=false`, `changedActionCount=0`, `guardOk=true`) y ledger local `SPP > CrossChecks` (`94/94`). Siguiente bloque exacto: `phase11_spp_static_tabs`.
`phase11_spp_static_tabs` queda cerrado con `phase11_spp_static_tabs_20260524_155130.json`: `spp-static-tabs-target` deja `AutomaticRetest-Task7.xml` con Rankings inerte (`type=never`, `MaxStrategies=10000`, `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false`, `FitPortfolio.active=false`, `CustomAnalysis.filter=false/method=none`, sin condiciones extra), `FixedSize` activo, ATMs apagado, Notes preservado, `SelectedStrategies` vacio/ausente aceptado y `CustomData` unico preservado (`ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, seed `AUDCAD_darwinex/H1` spread `2.0`, commission `0.0`, `MainTestValues` correctos). No ejecuta SPP, no desbloquea WFM y preserva failed naturales. El apply usa backup `phase11_spp_static_tabs_20260524_155003`, diff `phase11_spp_static_tabs_target_20260524_155003.json`, dry-run posterior idempotente `phase11_spp_static_tabs_target_20260524_155015.json` (`changed=false`, `changedActionCount=0`, `guardOk=true`) y ledger local `SPP > Rankings` (`21/21`), `ATMs` (`1/1`), `RiskMoneyManagement` (`24/24`), `Notes` (`1/0` empty accepted), `SelectedStrategies` (`1/0` empty accepted) y `CustomData` (`6/6`). Siguiente bloque exacto: `phase11_spp_closeout`.
`phase11_spp_closeout` queda cerrado con `phase11_spp_closeout_20260524_163545.json`: `spp-closeout-report` consolida Synthetic previo y los tres guards SPP (`spp-data-databanks-resources-options-target`, `spp-crosschecks-target`, `spp-static-tabs-target`) sobre base local y template repo, todos en dry-run idempotente con `ok=true`, `issues=[]`, `warnings=[]`, `processes=[]`, `changed=false`, `changedActionCount=0` y `guardOk=true`. SPP queda como revision de configuracion `Input=Syntetic / Output=SPP`, `CustomData` unico, `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, seed `AUDCAD_darwinex/H1` spread `2.0`, `OptProfileSysParamPermutation`, `MaxTests=3000`, `DistributionUp=20`, `DistributionDown=20`, `Steps=25`, filtros `NetProfit >= 50%` main y `DrawdownPct <= 200%` main, sin ejecutar SPP, sin smoke, sin optimizacion, sin desbloquear WFM y sin forzar `Results=passed`. Evidencia dry-run de cierre: `phase11_spp_data_databanks_resources_options_target_20260524_163530.json`, `phase11_spp_crosschecks_target_20260524_163530.json` y `phase11_spp_static_tabs_target_20260524_163530.json`. Siguiente bloque exacto: `phase12_wfm_open`.
`phase12_wfm_open` queda abierto con `phase12_wfm_open_20260524_165030.json`: `wfm-open-report` confirma `WFM`, `AutomaticRetest-Task4.xml`, `Input=SPP`, `Output=WFM`, unico crosscheck activo `WalkForwardMatrix`, `WalkForward type=2`, `period=10`, `optimization=15`, `distributionUp=20`, `distributionDown=20`, `maxSteps=8`, `Param1 20-36 step 2`, `Param2 5-8 step 1`, `MaxTests=3000` y 6 condiciones activas. El gate queda `ok=true`, `issues=[]`, `processes=[]`, no lanza SQX, no ejecuta WFM, no hace smoke, no inicia optimizacion y fija politica `configuration_review_only_no_smoke_no_optimization_blocked_by_spp`. Warnings aceptados para el siguiente bloque: WFM depende de SPP no ejecutado, `Data engine=MetaTrader5 (hedged)` difiere de `CustomData engine=MetaTrader4`, `Data spread=2` difiere de `CustomData spread=2.0`, y hay metodos activos ocultos en `MonteCarloRetest`, `MonteCarloManipulation` y `WhatIf` aunque esos checks estan inactivos. Cuestionario local completo `_task_summary_20260524_165019.json`: 13 tabs, 20.011 entradas y 12.323 diferencias donor/base. Siguiente bloque exacto: `phase12_wfm_data_databanks_resources_options`.
`phase12_wfm_data_databanks_resources_options` queda cerrado con `phase12_wfm_data_databanks_resources_options_20260524_171211.json`: `wfm-data-databanks-resources-options-target` mantiene `AutomaticRetest-Task4.xml` con portador dual `Data+CustomData` sincronizado, `Input=SPP`, `Output=WFM`, `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, seed `AUDCAD_darwinex/H1` spread `2.0`, `Data engine=MetaTrader5 (hedged)`, `CustomData engine=MetaTrader4`, resources `TICK/EETUS` sin sesiones y Options inertes. Project Generator ya no inyecta ventanas horarias en `AutomaticRetest-Task4.xml`; los customs generados adaptan simbolo/timeframe/spread/recursos por activo sin convertir WFM en filtro horario. El unico cambio CFX aplicado fue normalizar `Data/Chart spread` de `2` a `2.0` en base local y template repo, con apply `phase12_wfm_data_databanks_resources_options_target_20260524_171147.json` e idempotencia `phase12_wfm_data_databanks_resources_options_target_20260524_171200.json` (`changed=false`, `changedActionCount=0`, `guardOk=true`). No ejecuta WFM, no hace smoke, no inicia optimizacion, no desbloquea SPP y preserva resultados failed/passed naturales. Siguiente bloque exacto: `phase12_wfm_crosschecks`.
`phase12_wfm_crosschecks` queda cerrado con `phase12_wfm_crosschecks_20260524_174355.json`: `wfm-crosschecks-target` mantiene `AutomaticRetest-Task4.xml` aislado en `WalkForwardMatrix` como unico crosscheck activo, `CrossChecks use=true/evaluateAll=true`, `WalkForward type=2`, `period=10`, `optimization=15`, `distributionUp=20`, `distributionDown=20`, `maxSteps=8`, `Param1 20-36 step 2`, `Param2 5-8 step 1` y `MaxTests=3000`. Se fijan seis filtros WFM dedicados: `NetProfit > 0`, `NetProfit > 60`, `WFPctOfProfitableRuns > 70`, `WFMaxProfitByRunInPct < 50`, `WFMinTradesInRun > 20` y `WFMaxPctDDbyRun <= 25`; los dos umbrales estrictos son politica conservadora de fragilidad, no claim academico universal. Los metodos ocultos de `MonteCarloRetest`, `MonteCarloManipulation`, `WhatIf` y demas checks inactivos quedan apagados, los setups anidados quedan normalizados a `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, seed `AUDCAD_darwinex/H1` spread `2.0`, y `ForceRunCrossChecks=false` queda explicito. Evidencia: dry-run `phase12_wfm_crosschecks_target_20260524_174318.json`, apply `phase12_wfm_crosschecks_target_20260524_174334.json`, idempotencia `phase12_wfm_crosschecks_target_20260524_174344.json` (`changed=false`, `changedActionCount=0`, `guardOk=true`) y reporte local. No ejecuta WFM, no hace smoke, no inicia optimizacion, no desbloquea SPP/WFM y no fuerza `Results=passed`. Siguiente bloque exacto: `phase12_wfm_static_tabs`.

## SQX Edge Pro

El proyecto se presenta como una edicion comercial Pro de acceso web con suscripcion mensual/anual, soporte opcional y packs de plantillas alrededor de la metodologia.

Oferta inicial prevista:

- SQX Edge Pro Mensual: acceso web protegido con email validado, sesion Pro y workspace aislado.
- SQX Edge Pro Anual: acceso web protegido con email validado, sesion Pro y workspace aislado.
- Soporte opcional: acompanamiento, configuracion operativa y revisiones de metodologia.
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
- `docs/STATE_CONSISTENCY_GUARD.md` y `docs/state_consistency_manifest.json` mantienen alineados README, roadmap, governance y UX-NAV con un test pytest contra frases obligatorias/obsoletas.
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

Acceso remoto Pro previsto:

- REMOTE-0 fija el roadmap de servicio remoto en `docs/REMOTE_SERVICE_ROADMAP.md`.
- Ancla historica: Estado comercial: REMOTE-0 inicia el giro oficial a acceso web Pro.
- REMOTE-1 fija la base de portatil servidor en `docs/REMOTE_1_LAPTOP_SERVER_BASELINE.md`.
- REMOTE-2 fija el tunel protegido en `docs/REMOTE_2_CLOUDFLARE_TUNNEL_ACCESS.md`.
- CANONICAL-LINK1 fija `https://sqxedgesuite.org/` como unico enlace comercial y de soporte; los subdominios de app/preview quedan como infraestructura interna o fallback tecnico.
- REMOTE-2B fija acceso completo `tester_free` para testers aprobados y recomienda privatizar `origin` e `institutional` antes de venta en `docs/REMOTE_2B_TESTER_GRANTS_REPO_PRIVACY.md`.
- REMOTE-3A fija la base backend `remote-access-v1`, endpoint `/api/remote/access/status`, ejemplo local de entitlements y privacidad de repos verificada en `docs/REMOTE_3A_REMOTE_ACCESS_FOUNDATION.md`.
- REMOTE-3B fija la sesion de app `remote-session-v1`, cookie `__Host-sqx_remote_session`, endpoints `/api/remote/session/login`, `/api/remote/session/status`, `/api/remote/session/logout` y verificacion de clave tester en `docs/REMOTE_3B_APP_SESSION_GRANT_KEY.md`.
- REMOTE-3C fija el webhook de pago firmado `remote-payment-webhook-v1`, secreto privado `SQX_REMOTE_PAYMENT_WEBHOOK_SECRET`, endpoint `/api/remote/payment/webhook`, endpoint piloto `/api/remote/protected/write-pilot` y altas/cancelaciones idempotentes en `docs/REMOTE_3C_PAID_WEBHOOK_PROTECTED_WRITE.md`.
- REMOTE-4 fija el workspace aislado `remote-workspace-v1`, endpoint `/api/remote/workspace/status`, `SQX_REMOTE_WORKSPACES_ROOT` privado y el write-pilot auditado dentro del workspace en `docs/REMOTE_4_WORKSPACE_ISOLATION.md`.
- REMOTE-PERSIST1A fija persistencia remota de Plan Mining, Pipeline State y Strategy Control en `remote-workspace-state-v1` dentro de `<workspace>/config/workspace_state.sqlite`.
- REMOTE-PERSIST1B fija outputs de Project Generator en `remote-workspace-output-v1`, con `.cfx` por usuario en `<workspace>/outputs` y bloqueo de `output` remoto manual para evitar colisiones entre usuarios.
- REMOTE-PERSIST1C fija Template Maker como estado workspace-scoped en `remote-template-maker-state-v1`, con estrategias/configuracion por usuario en `<workspace>/config/template_maker.sqlite` y IndexedDB solo como cache de compatibilidad.
- REMOTE-PERSIST1D fija backups/restores de Control Panel en `remote-state-backup-v1`, con snapshots por usuario en `<workspace>/config/state_backups` y filtrado backend de claves sensibles.
- REMOTE-PERSIST1E fija presets propios de SQX Views en `remote-workspace-state-v1`, con `sqx_view_creator_presets_v1` por usuario en `<workspace>/config/workspace_state.sqlite` y `localStorage` solo como cache de compatibilidad.
- CFX-BASE142 repara los templates base `Capa1_Long.cfx` y `Capa2_Base.cfx` para que abran en SQX 142 con recursos/broker resolubles y sin sesiones fantasma `Futures_Commodities1` antes de ajustar parametros default.
- REMOTE-5 fija el panel `remote-pro-panel` en Home, consumiendo `/api/remote/access/status`, `/api/remote/session/status`, `/api/remote/workspace/status` y `/api/health` para mostrar acceso Pro, readiness remoto, workspace corto y privacidad en `docs/REMOTE_5_REMOTE_UX.md`.
- REMOTE-6 fija `remote-security-v1`, endpoint `/api/remote/security/status`, endpoint `/api/remote/security/audit/recent`, `SQX_REMOTE_SECURITY_POLICY_PATH`, rate limits, kill switch, revocacion, bloqueo por hash, watermark remoto y auditoria redaccionada en `docs/REMOTE_6_SECURITY_ABUSE_CONTROLS.md`.
- REMOTE-SEC2 fija `remote-access-control-v1`, cookie de dispositivo `__Host-sqx_device_id`, 2 contextos confiables por identidad, bloqueo de sesiones copiadas a otro contexto y aprobacion operador para contextos extra en `docs/REMOTE_SEC2_CREDENTIAL_SHARING_CONTROL.md`.
- REMOTE-7 fija la oferta web Pro mensual/anual, el onboarding sin instalacion, FAQ, soporte, acceso `tester_free` y portable como fallback interno en `docs/REMOTE_7_MONETIZATION_REWRITE.md`.
- REMOTE-8 fija `remote-controlled-pilot-v1`, herramienta `backend/sqx-edge-tool/tools/remote_controlled_pilot.py`, evidencia ignorada `.local/remote_service/remote8_controlled_pilot/` y `Controlled Pilot Gate` en `docs/REMOTE_8_CONTROLLED_PILOT.md`.
- REMOTE-8B fija `remote-live-pilot-evidence-v1`, herramienta `backend/sqx-edge-tool/tools/remote_live_pilot_evidence.py`, ejemplo `docs/examples/remote8b_live_pilot_evidence.local.example.json`, evidencia ignorada `.local/remote_service/remote8b_live_pilot_evidence*` y `Live Pilot Evidence Gate` en `docs/REMOTE_8B_LIVE_PILOT_EVIDENCE.md`.
- REMOTE-8C fija `remote-first-user-observation-v1`, herramienta `backend/sqx-edge-tool/tools/remote_first_user_observation.py`, ejemplo `docs/examples/remote8c_first_user_observation.local.example.json`, evidencia ignorada `.local/remote_service/remote8c_first_user_observation*` y `First User Observation Gate` en `docs/REMOTE_8C_FIRST_USER_OBSERVATION.md`.
- REMOTE-SUPPORT1 añade intake seguro de incidencias en Control Panel con `support-incident-v1`, endpoint `/api/support/incidents`, helper `tools/remote_support_status.ps1` y evidencia local ignorada `.local/remote_service/support_cases/`.
- WAIT-4 añade Trust Evidence Pack en `docs/WAIT4_TRUST_EVIDENCE_PACK.md`: self-assessment, privacy statement, safety checklist y escaneos externos planificados sin certificados ficticios.
- REMOTE-8D fija `remote-tiny-cohort-activation-v1`, herramienta `backend/sqx-edge-tool/tools/remote_tiny_cohort_activation.py`, ejemplo `docs/examples/remote8d_tiny_cohort_activation.local.example.json`, evidencia ignorada `.local/remote_service/remote8d_tiny_cohort_activation*` y `Tiny Cohort Activation Package Gate` en `docs/REMOTE_8D_TINY_COHORT_ACTIVATION.md`.
- REMOTE-8E fija `remote-tiny-cohort-execution-v1`, herramienta `backend/sqx-edge-tool/tools/remote_tiny_cohort_execution.py`, ejemplo `docs/examples/remote8e_tiny_cohort_execution.local.example.json`, evidencia ignorada `.local/remote_service/remote8e_tiny_cohort_execution*` y `Tiny Cohort Manual Execution Record Gate` en `docs/REMOTE_8E_TINY_COHORT_EXECUTION.md`.
- REMOTE-8F fija `remote-tiny-cohort-monitoring-v1`, herramienta `backend/sqx-edge-tool/tools/remote_tiny_cohort_monitoring.py`, ejemplo `docs/examples/remote8f_tiny_cohort_monitoring.local.example.json`, evidencia ignorada `.local/remote_service/remote8f_tiny_cohort_monitoring*` y `Tiny Cohort Monitoring Gate` en `docs/REMOTE_8F_TINY_COHORT_MONITORING.md`.
- REMOTE-8G fija `remote-tiny-cohort-decision-review-v1`, herramienta `backend/sqx-edge-tool/tools/remote_tiny_cohort_decision_review.py`, ejemplo `docs/examples/remote8g_tiny_cohort_decision_review.local.example.json`, evidencia ignorada `.local/remote_service/remote8g_tiny_cohort_decision_review*` y `Tiny Cohort Decision Review Gate` en `docs/REMOTE_8G_TINY_COHORT_DECISION_REVIEW.md`.
- REMOTE-8H fija `remote-next-controlled-movement-package-v1`, herramienta `backend/sqx-edge-tool/tools/remote_next_controlled_movement_package.py`, ejemplo `docs/examples/remote8h_next_controlled_movement_package.local.example.json`, evidencia ignorada `.local/remote_service/remote8h_next_controlled_movement_package*` y `Next Controlled Movement Package Gate` en `docs/REMOTE_8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE.md`; el ciclo actual usa REMOTE-8L como fuente y conserva REMOTE-8G solo como compatibilidad historica.
- REMOTE-8I fija `remote-next-controlled-movement-execution-approval-v1`, herramienta `backend/sqx-edge-tool/tools/remote_next_controlled_movement_execution_approval.py`, ejemplo `docs/examples/remote8i_next_controlled_movement_execution_approval.local.example.json`, evidencia ignorada `.local/remote_service/remote8i_next_controlled_movement_execution_approval*` y `Next Controlled Movement Execution Approval Gate` en `docs/REMOTE_8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVAL.md`.
- REMOTE-8J fija `remote-next-controlled-movement-manual-execution-v1`, herramienta `backend/sqx-edge-tool/tools/remote_next_controlled_movement_manual_execution.py`, ejemplo `docs/examples/remote8j_next_controlled_movement_manual_execution.local.example.json`, evidencia ignorada `.local/remote_service/remote8j_next_controlled_movement_manual_execution*` y `Next Controlled Movement Manual Execution Gate` en `docs/REMOTE_8J_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION.md`.
- REMOTE-8K fija `remote-next-controlled-movement-monitoring-v1`, herramienta `backend/sqx-edge-tool/tools/remote_next_controlled_movement_monitoring.py`, ejemplo `docs/examples/remote8k_next_controlled_movement_monitoring.local.example.json`, evidencia ignorada `.local/remote_service/remote8k_next_controlled_movement_monitoring*` y `Next Controlled Movement Monitoring Gate` en `docs/REMOTE_8K_NEXT_CONTROLLED_MOVEMENT_MONITORING.md`.
- REMOTE-8L fija `remote-post-monitoring-decision-review-v1`, herramienta `backend/sqx-edge-tool/tools/remote_post_monitoring_decision_review.py`, ejemplo `docs/examples/remote8l_post_monitoring_decision_review.local.example.json`, evidencia ignorada `.local/remote_service/remote8l_post_monitoring_decision_review*` y `Post Monitoring Decision Review Gate` en `docs/REMOTE_8L_POST_MONITORING_DECISION_REVIEW.md`.
- REMOTE-OPS1 fija `remote-ops1-laptop-readiness-v1`, herramienta `backend/sqx-edge-tool/tools/remote_ops1_laptop_readiness.py`, ejemplo `docs/examples/remote_ops1_laptop_readiness.local.example.json`, evidencia ignorada `.local/remote_service/remote_ops1_laptop_readiness*` y `Laptop Production Readiness Drill Gate` en `docs/REMOTE_OPS1_LAPTOP_READINESS_DRILL.md`.
- REMOTE-OPS1B - Cloudflare Operator Handoff fija `docs/REMOTE_OPS1B_CLOUDFLARE_OPERATOR_HANDOFF.md`, `tools/remote_tunnel_operator_handoff.ps1`, `docs/examples/cloudflared-config.local.example.yml` y archivos locales ignorados `.local/remote_service/cloudflare_tunnel_operator_handoff.local.md` / `.local/remote_service/cloudflared-config.local.yml.template`.
- REMOTE-SUG1 incorpora las mejores ideas de hardening de la propuesta tester en `docs/REMOTE_SUG1_DEPLOYMENT_HARDENING_REVIEW.md`: zero ingress, Cloudflare Access/Tunnel, persistencia, backup y resiliencia. Docker/Linux queda como ruta futura REMOTE-9, no como requisito actual para testers ni compradores.
- La comunicacion de seguridad y privacidad vive en `docs/REMOTE_SERVICE_SECURITY_PRIVACY_COPY.md`.
- El piloto corre en portatil 24/7 mediante dominio propio, Cloudflare Tunnel y Cloudflare Access.
- Los testers aprobados podran usar todas las funcionalidades sin pago mientras su grant `tester_free` este activo, pero siempre autenticados, auditados y revocables como cualquier usuario.
- Recomendacion comercial: convertir `SQX_Edge_Suite_v1` y `SQX_Institutional_Core` a repos privados antes de activar ventas, salvo decision explicita de mantener una estrategia public-source.
- Estado de repos: `SQX_Edge_Suite_v1` e `SQX_Institutional_Core` verificados como privados por GitHub CLI el 2026-05-16.
- Cada usuario pagado tendra workspace aislado para config, imports, outputs, exports y auditoria.
- El navegador no selecciona rutas locales de SQX; las rutas SQX, `data.db`, templates y BlockSettings se gestionan en el servidor.
- La comunicacion al usuario se basa en entorno controlado, auditado y aislado; no se promete riesgo cero.

Operativa local REMOTE-1:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_service_preflight.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_service_watchdog.ps1 -Once -NoStart
```

Operativa privada REMOTE-2:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_operator_handoff.ps1 -CloudflaredPath C:\Tools\cloudflared\cloudflared.exe
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_preflight.ps1 -RequireEvidence
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_smoke.ps1 -ProtectedUrl "<private protected url>"
```

Arranque operador REMOTE-RUNBOOK1:

```bat
START_SQX_EDGE_REMOTE.bat
STOP_SQX_EDGE_REMOTE.bat
```

`START_SQX_EDGE_REMOTE.bat` abre un monitor visual visible de Backend/Tunnel/Ollama, arranca los servicios en segundo plano, dispara la conexion local de Ollama a traves de Flask y solo muestra OK cuando el portatil esta listo para testers. `STOP_SQX_EDGE_REMOTE.bat` abre el mismo monitor y detiene solo el backend/tunel de este proyecto.

Operativa privada REMOTE-OPS1:

```powershell
Copy-Item docs\examples\remote_ops1_laptop_readiness.local.example.json .local\remote_service\remote_ops1_laptop_readiness.local.json
python backend\sqx-edge-tool\tools\remote_ops1_laptop_readiness.py --evidence .local\remote_service\remote_ops1_laptop_readiness.local.json
```

REMOTE-OPS1 no ejecuta expansion, no invita usuarios, no cambia grants, no envia emails y no publica enlaces. Solo valida que el portatil esta preparado para volver a REMOTE-8H con evidencia privada.

Nota de despliegue REMOTE-SUG1: no se debe anadir `Dockerfile`, `docker-compose.yml` ni `.dockerignore` en la raiz del proyecto durante el piloto Windows. La ruta activa sigue siendo portatil Windows con SQX local, backend en `127.0.0.1`, Cloudflare Tunnel y Cloudflare Access. Docker/Linux queda aparcado como hardening futuro cuando la compatibilidad con SQX, workspaces y backups este probada.

Portal tester Pro previsto (historico):

- T1 define un futuro repo privado `SQX_Edge_Tester_Portal` para alojar en Vercel una experiencia tester Pro controlada.
- T2 deja un bootstrap seguro en `templates/SQX_Edge_Tester_Portal/`, listo para copiar a un repo privado cuando lo autoricemos.
- T3 define contratos de testers, password hashing Argon2id, cookie `__Host-sqx_tester_session`, tokens de renovacion de un uso, eventos de auditoria y limites de secretos.
- T4 anade un prototipo local de login/sesion desactivado por defecto con middleware para rutas protegidas y logout.
- T5 anade gates `tester_pro` de servidor para features Pro: dashboard completo, Strategy Builder, Project Generator, Views, handoff exports y soporte.
- T6 anade caducidad de 15 dias, estados `pending_renewal`/`expired`/`denied`/`blocked` y preview manual approve/deny/block sin mutar datos reales.
- T7 anade consola admin protegida para preview de crear, renovar, denegar, bloquear y revisar auditoria sin persistir datos reales.
- T8 anade rate-limit contract, headers reforzados, watermark visible, kill switch y checklist de Deployment Protection antes de cualquier preview.
- T9 intento el preflight externo de Vercel con autorizacion explicita; el deploy quedo bloqueado por token local invalido y se anadio script de preflight reproducible.
- T9b autentico Vercel, intento deploy y lo elimino al detectar alias de produccion; no hay deployment activo ni URL publica operativa.
- T9c anade `audit:vercel-protection` y deja el estado `NO_GO_PROTECTION_NOT_VERIFIED` hasta verificar Deployment Protection por API/dashboard.
- T9d activa/verifica Vercel Authentication Standard Protection y deja `GO_PROTECTION_VERIFIED` sin desplegar ni publicar URL.
- T9e reintento preview con proteccion activa; T9e reintenta deploy sin `--prod`, Vercel vuelve a reportar produccion y se elimina inmediatamente; no queda deployment activo ni URL publica operativa.
- T9f anade `proof:vercel-preview-path` para bloquear cualquier avance hasta que exista una ruta Git/PR preview privada, protegida y separada de produccion.
- T9g crea el repo privado `SQX_Edge_Tester_Portal`, prepara `main` y `tester-preview`, conecta Vercel por GitHub y verifica `GO_GIT_PREVIEW_PATH_READY` sin deploy manual.
- T10 intento preview interno desde `tester-preview`. T10 dispara el primer piloto interno desde `tester-preview`, detecta `target=production`, elimina el deployment y deja T10b como correccion obligatoria antes de compartir URL.
- T10b anade `vercel-target-guard.mjs` al `prebuild`, bloquea `production/tester-preview` con codigo 43, elimina el deployment fallido y deja el proyecto sin deployment activo ni dominios.
- T10c define una ruta API preview explicita sin desplegar; T10c anade `proof:vercel-explicit-preview`, confirma por API `productionBranch=main` y prepara una ruta explicita con `target: "preview"` sin desplegar ni compartir URL.
- T10d ejecuta una unica preview API explicita, detecta que Vercel devuelve `target=production`, elimina el deployment y deja T10e como correccion obligatoria antes de compartir URL.
- T10e anade `proof:vercel-omitted-target-preview`; T10e intento preview API con `target` omitido, detecta que Vercel vuelve a devolver `target=production`, elimina el deployment y deja T10f como recreacion/separacion obligatoria.
- T10f anade `proof:vercel-preview-project-separation`; T10f separo un proyecto preview Vercel nuevo sin deployment, sin dominios y sin Git link, y deja T10g como link/proof obligatorio antes de publicar cualquier URL.
- T10g anade `proof:vercel-linked-preview-project`. T10g linko el repo privado del portal tester al proyecto preview separado, confirma `main` como production branch, `tester-preview` como no-produccion, Deployment Protection activo y sin deployment ni dominios.
- T10h anade `proof:vercel-protected-preview-rollback`. T10h intento una preview protegida desde el proyecto separado, detecta `target=production`, confirma que el guard T10b bloqueo el build con codigo 43, elimina el deployment y deja T10i como correccion obligatoria.
- T10i anade `proof:vercel-cli-default-preview-route`; T10i para corregir o reemplazar la ruta preview de Vercel antes de otro intento de deployment adopta `vercel deploy` sin `--prod` ni `--target`, conserva el proyecto sin deployment/dominios y deja T10j como intento unico con rollback inmediato.
- T10i corrigio la siguiente ruta preview hacia `vercel deploy` por defecto como prueba sin deployment.
- T10j anade `proof:vercel-cli-default-preview-command-rollback`; T10j para ejecutar una unica preview CLI default detecta que `--skip-domain` solo vale para produccion, no crea deployment ni URL, y deja T10k como intento corregido sin `--skip-domain`.
- T10j ejecuto el comando CLI default aprobado y lo cerro sin deployment creado.
- T10k anade `proof:vercel-cli-default-preview-rollback`; T10k ejecuta una preview CLI default sin `--skip-domain`, Vercel vuelve a reportar `target=production`, el guard bloquea con codigo 43, se elimina el deployment y T10l queda como investigacion sin deploy.
- T10k ejecuto una preview CLI default corregida y la cerro como rollback seguro.
- T10l anade `proof:vercel-route-investigation`; investiga Vercel sin deploy, detecta `project.productionBranch` ausente, `project.targets` vacio y senales de ruta produccion, y deja T10m como correccion/reemplazo sin deploy previo.
- T10l investigo Vercel sin deploy y dejo T10m para correccion manual/API o ruta alternativa antes de cualquier deployment.
- T10m endurecio la configuracion Vercel por API sin deploy y dejo T10n para proof no-deploy de target/ruta antes de cualquier deployment.
- T10m anade `proof:vercel-config-hardening`; aplica por API `autoAssignCustomDomains=false` y `previewDeploymentsDisabled=false` sin deploy, mantiene el proyecto sin dominios/deployments y deja T10n como proof/reemplazo de ruta antes de cualquier deployment.
- T10n anade `proof:vercel-route-decision`; confirma sin deploy que la ruta Vercel actual no debe usarse para rollout y deja T10o como reemplazo/proof provider-level antes de cualquier deployment.
- T10n rechaza la ruta Vercel actual y deja T10o para ruta alternativa o proof manual/provider-level antes de cualquier deployment.
- T10o anade `proof:replacement-route-contract`; selecciona `fresh_staging_route_with_no_deploy_preflight`, mantiene rechazada la ruta Vercel actual y deja T10p solo con aprobacion explicita antes de crear/verificar cualquier ruta externa.
- T10o deja lista una ruta alternativa contractual sin deploy y T10p para crear/verificar una ruta staging nueva queda condicionado a aprobacion explicita.
- T10p anade `proof:fresh-staging-route-preflight`; deja preparado el gate local sin API/deploy/proyecto/URL y reserva T10q para una aprobacion exacta de accion externa sin deployment.
- T10p deja listo el preflight local de ruta staging fresca y T10q para pedir aprobacion exacta queda como siguiente gate externo sin deployment.
- T10q anade `proof:fresh-staging-route-access-check`; registra aprobacion explicita, verifica lectura Vercel por app conectada y bloquea creacion/verificacion porque la CLI espera login interactivo y no hay `VERCEL_TOKEN`.
- T10q registra aprobacion explicita y T10r para autenticar Vercel CLI queda completado antes de crear/verificar la ruta staging.
- T10r anade `proof:fresh-staging-project-created`; crea/verifica `sqx-edge-tester-staging` sin deploy, sin dominios, sin Git link y sin URL publicada, dejando T10s como gate de proteccion/settings.
- T10s anade `proof:staging-protection-verified`; confirma SSO Deployment Protection `all_except_custom_domains`, Git fork protection, cero deployments y cero dominios antes de cualquier Git link o deploy.
- T10t anade `proof:staging-local-link`; enlaza localmente el repo privado del portal tester a `sqx-edge-tester-staging` mediante metadata ignorada, manteniendo cero deployments, cero dominios y ninguna URL publicada.
- T10u anade `proof:staging-deployment-readiness`; prepara el gate no-deploy para un unico deployment staging controlado con inspeccion de target/aliases y rollback obligatorio antes de compartir cualquier URL.
- T10v anade `proof:controlled-staging-deploy-rollback`; ejecuta un unico intento staging, Vercel devuelve `target=production`, el guard bloquea y se elimina el deployment fallido sin publicar URL.
- T10w anade `proof:provider-target-mapping-investigation`; rechaza la ruta CLI default y prepara `vercel deploy --target=preview --force --yes --format json` como unico siguiente intento controlado.
- T10x anade `proof:explicit-preview-target-rollback`; prueba la ruta explicita `--target=preview`, Vercel vuelve a devolver `target=production`, el guard bloquea y se elimina el deployment fallido.
- T10x prueba `--target=preview` como intento unico y queda cerrado como rollback limpio.
- T10y anade `proof:no-deploy-provider-dashboard-decision`; T10y para dejar de reintentar Vercel CLI pausa la ruta y selecciona correccion provider-dashboard sin deploy antes de cualquier nuevo intento.
- T10z para preparar el paquete/checklist provider-dashboard sin deploy quedo como siguiente paso de T10y.
- T10z anade `proof:provider-dashboard-correction-package`; deja checklist y formato de evidencia para correccion provider-dashboard sin deploy antes de cualquier nuevo intento.
- T10aa para registrar evidencia provider-dashboard sin deploy quedo como siguiente paso de T10z.
- T10aa anade `proof:provider-dashboard-evidence-record`; confirma por CLI cero deployments/dominios/proteccion activa, pero deja `NO_GO_PROVIDER_CANNOT_PROVE_PREVIEW_TARGET` hasta revision manual de dashboard. T10ab para ingerir evidencia manual de dashboard queda cerrado en la siguiente fase.
- T10ab anade `proof:manual-dashboard-evidence-ingest`; ingiere evidencia manual de dashboard, confirma Git no conectado, production branch no visible, correccion no visible y `next_deployment_allowed=unknown`, por lo que decide `NO_GO_REPLACE_VERCEL_TESTER_ROUTE`. T10ac para comparar y seleccionar una ruta tester protegida queda completado sin deploy.
- T10ac anade `proof:replacement-tester-route-options`; compara rutas no-Vercel y selecciona Cloudflare Pages preview + Cloudflare Access email OTP como candidata, sin crear proyecto, deploy, URL ni politicas externas. T10ad para preparar el preflight Cloudflare Access queda completado sin accion externa.
- T10ad anade `proof:cloudflare-access-preflight`; define ramas, Access OTP, no custom domains, no URL y una barrera T10ae de compatibilidad runtime Next.js antes de crear nada en Cloudflare. T10ae para resolver la compatibilidad runtime Cloudflare localmente queda completado sin proveedor.
- T10ae anade `proof:cloudflare-runtime-compatibility`; inventaria middleware y 7 API route handlers, rechaza static export y selecciona Cloudflare Workers/OpenNext como runtime candidato sin instalar dependencias ni tocar proveedor.
- T10af anade `proof:opennext-cloudflare-adapter`; prepara `wrangler.jsonc`, `open-next.config.ts`, `.dev.vars.example`, `@opennextjs/cloudflare`, `wrangler` y scripts locales `cf:build`, `cf:preview`, `cf:typegen` sin exponer `cf:deploy` ni crear recursos Cloudflare.
- T10ag anade `proof:opennext-local-smoke`; confirma que el build OpenNext genera worker/assets y que preview WSL/Linux devuelve `/api/health` 200, mientras preview nativo Windows queda como `NO_GO_NATIVE_WINDOWS_PREVIEW_ROUTE_500`.
- T10ah anade `proof:next-proxy-migration`; documenta que `proxy.ts` queda bloqueado para esta ruta porque OpenNext/Cloudflare no soporta Node Middleware, conserva `middleware.ts` y mantiene la fase sin deploy ni recursos Cloudflare.
- T10ai anade `proof:cloudflare-provider-project-preflight`; prepara contrato Cloudflare Workers/OpenNext + Access OTP sin deploy, sin proyecto, sin politica Access, sin Git link y sin URL tester.
- T10aj anade `proof:cloudflare-project-shell`; registra el NO-GO seguro por falta de autenticacion Wrangler/ruta shell sin deploy y memoriza T10ajb-T10an/T11/T12.
- T10ajb anade `proof:cloudflare-auth-handoff`; documenta login/API token local, crea ejemplo de evidencia Cloudflare sin secretos e ignora `cloudflare-shell-evidence.local.json` para T10ajc.
- T10ajc anade `proof:cloudflare-shell-evidence-ingest`; ingiere evidencia local si existe, devuelve NO-GO seguro porque aun no existe y mantiene T10ak bloqueada.
- T10ajd anade `proof:cloudflare-shell-evidence-capture`; deja checklist manual/autenticado exacto para rellenar evidencia local ignorada y rerun de T10ajc.
- T10aje anade `proof:cloudflare-readonly-shell-capture`; con Wrangler autenticado, Cloudflare devuelve `worker_not_found` para deployments/versions/secrets del worker propuesto.
- T10ajf anade `proof:cloudflare-shell-creation-decision`; documenta que `wrangler versions upload` no sirve para el primer Worker y que el siguiente gate T10ajg debe preparar un `wrangler deploy` exacto, sin ejecutarlo ni compartir URL.
- T10ajg anade `proof:cloudflare-first-deploy-approval-gate`; deja la frase de aprobacion, comando exacto, prechecks, postchecks y cleanup para T10ajh sin crear recursos Cloudflare.
- T10ajh anade `proof:cloudflare-first-deploy-readiness`; instala dependencias locales, versiona `package-lock.json`, confirma `npm run cf:build` y mantiene el deploy bloqueado hasta aprobacion exacta.
- T10aji anade `proof:cloudflare-first-deploy-rollback`; intenta el primer deploy, detecta requisito de subdominio/ruta Cloudflare, elimina el Worker y deja T10ajj como decision de ruta antes de reintento.
- T10ajj anade `proof:cloudflare-route-onboarding-decision`; decide custom route/domain protegido como opcion preferente, desactiva `workers_dev` y `preview_urls`, mantiene el Worker inexistente y deja T10ajk como ruta/onboarding + Access antes de cualquier redeploy.
- T10ajk anade `proof:cloudflare-route-access-precreate`; verifica Wrangler autenticado con Worker inexistente, crea ejemplo local seguro para evidencia de ruta/Access y mantiene T10ak bloqueado hasta que T10ajl seleccione hostname/zona privada o onboarding `workers.dev`.
- T10ajl anade `proof:cloudflare-hostname-zone-selection`; prepara evidencia local ignorada para hostname/zona o `workers.dev` protegido, mantiene `workers_dev=false` y `preview_urls=false`, y mantiene T10ak bloqueado hasta que esa evidencia privada devuelva GO.
- T10ajl2 anade `prepare:cloudflare-hostname-zone-selection`; crea/revisa el archivo local ignorado y bloquea campos sensibles como hostname, zone ID, emails, URL, tokens o claves antes de permitir T10ak.
- T10ajm anade `proof:cloudflare-workers-dev-shell-gate`; al no haber dominio ni Worker existente, prepara un shell Worker 404/no-app con config dedicada `workers_dev=true`, mantiene la app real con `workers_dev=false`, y deja T10ajn como unico paso externo para crear el target antes de Access.
- T10ajn anade `proof:cloudflare-workers-dev-shell-deploy`; crea el shell target con Wrangler, verifica respuesta 404/no-app, bloquea T10ak porque Access API requiere permisos `Access: Apps and Policies Write` o habilitacion manual en dashboard.
- T10ajo anade `proof:cloudflare-workers-dev-access`; verifica que Cloudflare Access intercepta el shell `workers.dev` antes del cuerpo 404/no-app y desbloquea T10ak como fase de registro/verificacion de app/policy, sin deploy real ni URL tester.
- T10ak anade `proof:cloudflare-access-policy-boundary`; registra/verifica con evidencia local ignorada que Access app/policy protege el shell y permite solo usuarios piloto aprobados, sin deploy real, URL tester ni emails en Git.
- T10al prepara el gate exacto de deploy real controlado y anade `proof:cloudflare-controlled-real-app-deploy-gate`; deja frase de aprobacion exacta, comando futuro, prechecks, smoke post-deploy y rollback, sin ejecutar deploy real ni publicar URL tester.
- T10am anade `proof:cloudflare-real-app-deploy-result`; ejecuta el deploy autorizado, registra que la version real queda subida sin target publico, mantiene Access en verde y bloquea URL/testers hasta T10an.
- T10an selecciona `workers.dev` protegido por Cloudflare Access como target tester y anade `proof:cloudflare-protected-tester-publication-target`; mantiene `workers_dev=false` hasta aprobacion exacta T10ao.
- T10ao prepara el preflight de publicacion controlada y anade `proof:cloudflare-controlled-workers-dev-publication-preflight`; mantiene `workers_dev=false`, URL/testers bloqueados y mueve el deploy real a T10ap con aprobacion exacta.
- T10ap publica el target `workers.dev` con un unico deploy autorizado, verifica Cloudflare Access antes de cualquier cuerpo de app y anade `proof:cloudflare-workers-dev-publication-result`; mantiene URL/testers bloqueados.
- T10aq prepara handoff controlado de acceso tester y anade `proof:tester-access-handoff`; mantiene URL, emails, cuentas y canales privados fuera de Git.
- T10ar prepara el gate privado de activacion de cuentas tester y anade `proof:tester-account-activation-gate`; mantiene URL, emails, credenciales, invitaciones y evidencias reales fuera de Git.
- T10as ingiere evidencia privada de activacion tester con `proof:tester-activation-evidence-ingest`; el resultado esperado sin archivo local es `NO_GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_SAFE_NO_GIT_LEAK`.
- T10at prepara el gate privado para compartir URL tester con `proof:tester-url-share-approval-gate`; el resultado esperado sin aprobacion local es `NO_GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_READY_NO_GIT_LEAK`.
- T10au prepara el gate de primer smoke privado tester con `proof:tester-first-smoke-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_FIRST_TESTER_SMOKE_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_FIRST_TESTER_SMOKE_PASSED_NO_GIT_LEAK`.
- T10av prepara el gate de expansion privada a micro-cohorte tester con `proof:tester-cohort-expansion-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_COHORT_EXPANSION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_COHORT_EXPANSION_READY_NO_GIT_LEAK`.
- T10aw prepara intake privado de feedback tester con `proof:tester-feedback-intake-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_FEEDBACK_INTAKE_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_FEEDBACK_INTAKE_READY_NO_GIT_LEAK`.
- T10ax prepara triage privado de feedback tester con `proof:tester-feedback-triage-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_READY_NO_GIT_LEAK`.
- T10ay prepara action plan privado de feedback tester con `proof:tester-action-plan-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_ACTION_PLAN_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_ACTION_PLAN_READY_NO_GIT_LEAK`.
- T10az prepara ejecucion privada de acciones tester con `proof:tester-action-execution-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_ACTION_EXECUTION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_ACTION_EXECUTION_READY_NO_GIT_LEAK`.
- T10ba prepara validacion privada de resultados tester con `proof:tester-result-validation-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_RESULT_VALIDATION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_RESULT_VALIDATION_READY_NO_GIT_LEAK`.
- T10bb prepara decision privada de iteracion tester con `proof:tester-iteration-decision-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_ITERATION_DECISION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_ITERATION_DECISION_READY_NO_GIT_LEAK`.
- T10bc prepara siguiente iteracion privada tester con `proof:tester-next-iteration-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_NEXT_ITERATION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_NEXT_ITERATION_READY_NO_GIT_LEAK`.
- TL1 resume el lanzamiento tester con `proof:tester-launch-candidate`; el resultado esperado sin evidencia local es `NO_GO_TESTER_LAUNCH_PRIVATE_EVIDENCE_MISSING` y el GO seguro es `GO_TESTER_LAUNCH_CANDIDATE_READY_NO_GIT_LEAK`.
- El acceso sera por usuario tester, email y password, con ciclo de renovacion de 15 dias y aprobacion/denegacion manual.
- Vercel Deployment Protection sera capa adicional, no sustituto de auth propia por tester.
- El nuevo ownership `Access/Security Gatekeeper` cubre auth, sesiones, expiracion, auditoria, watermarks, secretos Vercel y proteccion anti-distribucion.
- No se crearan testers, se enviaran emails ni se publicaran URLs Vercel sin autorizacion explicita.

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

- `Custom libre` permite crear `.cfx` fuera de Mining Control con asset, timeframe, blocksetting, direccion y capa propios.
- Incluye presets locales reutilizables y exportacion/importacion JSON para mover configuraciones propias entre instalaciones.
- La importacion de packs custom muestra preview de presets, assets, capas y reemplazos antes de fusionarlos con los guardados locales.
- Las tarjetas de activo/categoria pueden prefijar un Custom Project desde acciones rapidas sin ejecutar generacion automatica.

Mining Control:

- Incluye acciones rapidas para anadir candidatos a Mining Control desde activo/categoria.
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

## Acceso Web Pro

Flujo objetivo para usuario final:

1. El cliente paga o renueva la suscripcion.
2. El webhook activa su email validado.
3. El cliente entra por el enlace protegido.
4. Cloudflare Access y la autenticacion propia validan su sesion.
5. La app abre su workspace aislado en el servidor.
6. El cliente usa Workflow, Activos, Mining Control, SQX Views, Project Generator, Template Maker, Strategy Control y Champion vs Challenger desde el navegador.

El usuario final no instala Python, no descomprime ZIPs, no ejecuta `START_SQX_EDGE.bat` y no configura rutas SQX locales. Las rutas SQX, templates, `data.db`, BlockSettings y outputs se gestionan en el servidor remoto controlado.

Mensaje base de seguridad: SQX Edge Pro opera en un entorno autenticado, auditado y aislado por workspace. No se promete riesgo cero; se comunica control operativo, trazabilidad y privacidad razonable.

## Entrega Comercial Controlada

Estado real: REMOTE-0 documenta el pivote; la entrega comercial controlada pasa a acceso web Pro asistido. No esta planteado aun como lanzamiento masivo autoservicio.

Antes de activar a un comprador:

1. Confirmar pago activo y email validado.
2. Crear o verificar workspace aislado.
3. Confirmar que Cloudflare Tunnel, Access, backend, rutas SQX servidor y output estan en verde.
4. Mantener claims seguros: productividad, orden, trazabilidad y reduccion de errores operativos; nunca prometer rentabilidad.
5. Registrar incidencias de acceso, generacion, soporte y decision de ampliar/pausar antes de mas trafico.

## Fallback Interno Portable

El portable queda como herramienta interna de rollback, soporte o diagnostico. No es el flujo comercial principal.

Launcher interno desde la carpeta `packaging/` o desde el ZIP portable generado:

```bat
packaging\START_SQX_EDGE.bat
```

Ese launcher arranca la API local con Python embebido, espera a `http://127.0.0.1:5050/api/health` y abre `app\SQX_Dashboard_v6.html`.

Para cerrar la API local:

```bat
packaging\STOP_SQX_EDGE.bat
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
├── START_SQX_EDGE_REMOTE.bat     Launcher operador remoto
└── STOP_SQX_EDGE_REMOTE.bat
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

## Empaquetado Interno Fallback

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\package_portable.ps1 -RequireEmbeddedPython
```

El ZIP portable se crea en `dist/` e incluye el Python embebido. Desde REMOTE-0 se conserva como fallback interno, no como onboarding comercial del usuario final.

## Checklist de fallback

Para preparar una entrega interna con pruebas, ZIP portable y validacion del ZIP extraido:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\release_checklist.ps1
```

El checklist ejecuta contratos JS, suite Python, `git diff --check`, empaquetado portable, extraccion temporal, import de API con Python embebido y health check local. Al terminar muestra el ZIP listo en `dist/`.

Tambien puedes lanzar el modo estricto con doble click desde:

```text
RELEASE_SQX_EDGE.bat
```

Ese modo exige Git limpio antes de empaquetar y deja un resumen en `dist/SQX_release_summary.txt`.

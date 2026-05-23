# SQX142 Custom Task Config Roadmap

Estado: C1-CONFIG1 con Fase 5 `TICK REAL` cerrada y Fase 6 `MC` abierta el 2026-05-23. Fase 0 dejo
preflight, snapshots y diff semantico en `.local/sqx142_task_config/`; Fase 1
promociono las views ligeras/especializadas desde Mining15 a la base local y al
template repo; Fase 2 genero los cuestionarios completos de Build Capa1 y cerro
Build. Antes de `RETEST 0`, G8-SQX-AGENT-SKILLS1 alinea skills, guardianes,
perfiles del agente y handoffs locales para proteger el resto del cuestionario.
Antes de cerrar TICK y abrir MC, `sqx-academic-lopez` queda disponible como
consulta academica local-only para OOS, MC, data snooping y backtest
overfitting.
La mini fase `SQX142-BRANDING1` queda cerrada antes de `RETEST 0`: cambia solo
la capa visual local de SQX a `Build: 142.2336 Codex`, oculta en About las
lineas privadas de licencia/identidad y muestra la trazabilidad
`Optimized and Controlled by Codex 3.0 & QxPro for Edge Suite v1.0`; la version
tecnica interna continua siendo `142.2336`.

Este documento gobierna la configuracion interactiva de parametros del custom
base Capa 1. La fuente inicial es el custom mas actualizado:

`Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1`

La promocion hacia base sera `selective_normalized`: se usan los ajustes
metodologicos validados como donante, pero no se copia el proyecto completo.

## Targets

- Donor local SQX: `Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1`
- Base local SQX: `Capa1_Long_SQX142_Base`
- Template repo: `backend/sqx-edge-tool/templates/Capa1_Long.cfx`
- Ledger local ignorado por Git: `.local/sqx142_task_config/`
- Tool dry-run-first: `tools/sqx142_task_config_gate.ps1`

## Reglas

- No promocionar directamente simbolos `USDJPY_*`, timeframe `H4`, nombre de
  proyecto, active flags de sesion, resultados/databanks, rutas locales, logs ni
  estado de ejecucion.
- Toda decision de parametro se pregunta, se responde y se guarda antes de
  aplicar.
- Cada fase termina con reporte local y el siguiente paso exacto.
- Si un valor depende de Project Generator, tambien se alinea su fuente real en
  config, patcher, test o doc.
- La metrica de exito no es aumentar passed; es coherencia, trazabilidad,
  carga correcta en SQX y metodologia alineada.

## Herramienta

Comandos principales:

```powershell
tools\sqx142_task_config_gate.ps1 status
tools\sqx142_task_config_gate.ps1 preflight
tools\sqx142_task_config_gate.ps1 preflight --apply
tools\sqx142_task_config_gate.ps1 phases
tools\sqx142_task_config_gate.ps1 promote-views --target both
tools\sqx142_task_config_gate.ps1 promote-views --target both --apply
tools\sqx142_task_config_gate.ps1 build-genetic-target --target both
tools\sqx142_task_config_gate.ps1 build-genetic-target --target both --apply
tools\sqx142_task_config_gate.ps1 build-ranking-target --target both
tools\sqx142_task_config_gate.ps1 build-ranking-target --target both --apply
tools\sqx142_task_config_gate.ps1 build-blocks-target --target both
tools\sqx142_task_config_gate.ps1 build-blocks-target --target both --apply
tools\sqx142_task_config_gate.ps1 build-indicators-target --target both
tools\sqx142_task_config_gate.ps1 build-indicators-target --target both --apply
tools\sqx142_task_config_gate.ps1 build-data-target --target both
tools\sqx142_task_config_gate.ps1 build-data-target --target both --apply
tools\sqx142_task_config_gate.ps1 build-resources-target --target both
tools\sqx142_task_config_gate.ps1 build-resources-target --target both --apply
tools\sqx142_task_config_gate.ps1 build-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 build-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 build-static-tabs-target --target both
tools\sqx142_task_config_gate.ps1 retest1-data-resources-target --target both
tools\sqx142_task_config_gate.ps1 retest1-data-resources-target --target both --apply
tools\sqx142_task_config_gate.ps1 retest1-options-databanks-rankings-target --target both
tools\sqx142_task_config_gate.ps1 retest1-options-databanks-rankings-target --target both --apply
tools\sqx142_task_config_gate.ps1 retest1-passive-generation-target --target both
tools\sqx142_task_config_gate.ps1 retest1-passive-generation-target --target both --apply
tools\sqx142_task_config_gate.ps1 retest1-static-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 retest1-static-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 tick-real-data-databanks-resources-target --target both
tools\sqx142_task_config_gate.ps1 tick-real-data-databanks-resources-target --target both --apply
tools\sqx142_task_config_gate.ps1 tick-real-options-rankings-target --target both
tools\sqx142_task_config_gate.ps1 tick-real-options-rankings-target --target both --apply
tools\sqx142_task_config_gate.ps1 tick-real-passive-generation-target --target both
tools\sqx142_task_config_gate.ps1 tick-real-passive-generation-target --target both --apply
tools\sqx142_task_config_gate.ps1 tick-real-static-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 tick-real-static-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 phase-report --phase phase5_tick_real_closeout --summary "<summary>" --next-phase phase6_mc_open --write
tools\sqx142_task_config_gate.ps1 task-questionnaires --task-title "MC" --write
tools\sqx142_task_config_gate.ps1 questionnaire --task-title "MC" --tab "Data" --write
tools\sqx142_task_config_gate.ps1 record-answer --task-title "MC" --tab "Data" --question-id "<id>" --answer "<answer>"
tools\sqx142_task_config_gate.ps1 mc-data-databanks-resources-options-target --target both
tools\sqx142_task_config_gate.ps1 mc-data-databanks-resources-options-target --target both --apply
tools\sqx142_task_config_gate.ps1 mc-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 mc-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 mc-passive-generation-target --target both
tools\sqx142_task_config_gate.ps1 mc-passive-generation-target --target both --apply
tools\sqx142_task_config_gate.ps1 mc-static-tabs-target --target both
tools\sqx142_task_config_gate.ps1 mc-static-tabs-target --target both --apply
tools\sqx142_task_config_gate.ps1 archive-exit-day-snippets
tools\sqx142_task_config_gate.ps1 archive-exit-day-snippets --apply
tools\sqx142_task_config_gate.ps1 task-questionnaires --task-title "Build BS_Volatilidad_v6 · Capa1 L+S H4" --write
tools\sqx142_task_config_gate.ps1 questionnaire --task-title "MC 2" --tab "CrossChecks" --write
tools\sqx142_task_config_gate.ps1 questionnaire --task-title "MC 2" --tab "CrossChecks" --write --full-output
tools\sqx142_task_config_gate.ps1 record-answer --task-title "MC 2" --tab "CrossChecks" --question-id "<id>" --answer "<answer>"
tools\sqx142_task_config_gate.ps1 phase-report --phase phase1 --summary "<summary>" --next-phase phase2 --write
```

`preflight --apply` escribe solo evidencia local ignorada por Git: snapshots de
donor/base/template, diff semantico y `session_state.json`.

`questionnaire` y `task-questionnaires` detectan y guardan todas las entradas
por defecto, incluyendo entradas XML repetidas con indice estable para que no se
colapsen; los IDs largos anaden hash estable para no perder condiciones
repetidas en CrossChecks. `--max-values` queda solo como throttle diagnostico
temporal y no debe usarse para cerrar una fase. Cuando se usa `--write`, la
consola devuelve resumen para no inundar el terminal; el JSON completo se guarda
en `.local`. `--full-output` imprime todas las preguntas si hace falta
inspeccionarlo directamente.

## Fases

0. Preflight, backup plan, snapshots donor/base/template y diff semantico.
1. Promocion selectiva inicial Mining15 -> Capa1 base, solo fixes validados y
   reversibles.
2. Build Capa1, pestaña por pestaña.
2.5. `G8-SQX-AGENT-SKILLS1`, guardianes SQX antes de `RETEST 0`.
2.6. `SQX142-BRANDING1`, etiqueta visual local antes de `RETEST 0`.
3. `RETEST 0`.
4. `RETEST 1`.
5. `TICK REAL`.
6. `MC`.
7. `MC 2`.
8. `Sequential`.
9. `Monkey Test`.
10. `Synthetic` / `Syntetic`.
11. `SPP`, revision de configuracion si; smoke/optimizacion omitidos salvo
    decision nueva.
12. `WFM`, revision de configuracion si; ejecucion solo si deja de depender de
    SPP o se aprueba.
13. `FOWARD`, revision de configuracion si; pruebas de rendimiento omitidas por
    decision operativa previa.
14. Cierre Capa1, regeneracion de custom sample, validacion SQX, docs, tests y
    resumen del siguiente ciclo Capa2.

## Estado Fase 0

Preflight aplicado:

- donor, base local y template repo existen y son `.cfx` ZIP validos.
- SQX no tenia procesos vivos durante el preflight.
- base local todavia usa views `GENERAL`/`Default - Main data` en databanks que
  el donor ya tiene asignados a views ligeras/especializadas.
- `MC 2` difiere en `RandomizeSpread`: base `30-50`, donor `2.8-7.0`; la regla
  metodologica objetivo sigue siendo adaptativa por spread base `x2-x5`.
- `Synthetic`/`Syntetic` se trata como alias historico para evitar falsos
  missing.

## Estado Fase 1

Promocion selectiva aplicada solo a `config.xml`:

- Target local: `Capa1_Long_SQX142_Base/project.cfx`.
- Target repo: `backend/sqx-edge-tool/templates/Capa1_Long.cfx`.
- Backup local: `.local/sqx142_task_config/backups/phase1_views_20260523_104759/`.
- Evidencia local: `.local/sqx142_task_config/diffs/phase1_view_promotion_20260523_104800.json`.
- SHA template tras promocion: `C63AE53E952113462C0C39943E0E5A1FA616420D865F6D71C30F7E0E97851AD8`.

Views promocionadas:

- `Results`, `Initial population`, `Last generation`, `Strategies to improve`
  y `Strategies to optimize` -> `MINING FAST REVIEW`.
- `RETEST 0`, `retest 1` y `Foward` -> `RETEST QUICK REVIEW`.
- `TICK`, `MC`, `MC2`, `Sequential`, `SPP` y `WFM` ->
  `RETEST ROBUST REVIEW`.
- `Monkey Test` -> `MC MONKEY RETEST`.
- `Syntetic` -> `MC SYNTHETIC RETEST`.

No se tocaron simbolos, timeframe, fechas, filtros, active flags, resultados ni
databanks fisicos.

## Estado Fase 2

Cuestionarios Build Capa1 generados en:

`.local/sqx142_task_config/questionnaires/capa1/Build_BS_Volatilidad_v6_Capa1_L_S_H4/`

Resumen:

- `13` pestañas.
- `18.327` entradas/preguntas auditadas.
- `1.375` diferencias base vs donor.
- `Blocks` ya no colapsa rutas repetidas: guarda `17.621` preguntas y `1.363`
  diferencias.
- La consola muestra resumen; el contenido completo vive en `.local`.

Promocion aplicada de `Build > Genetic options`:

- Target local: `Capa1_Long_SQX142_Base/project.cfx`.
- Target repo: `backend/sqx-edge-tool/templates/Capa1_Long.cfx`.
- Backup local: `.local/sqx142_task_config/backups/phase2_build_genetic_20260523_123832/`.
- Evidencia local: `.local/sqx142_task_config/diffs/phase2_build_genetic_target_20260523_123833.json`.
- `MarketSides` queda sin tocar y sigue gobernado por el Project Generator.
- `FitnessRestartType` queda en `In sample (whole)` porque Build Capa1 mina edge
  en IS; la validacion metodologica vive en los retests Capa1 y Capa2.
- La poblacion inicial queda filtrada por `ProfitFactor >= 1` y
  `NumberOfTrades >= 100`.
- Smoke local `MarketSides` validado: generando `long`, `short` y `both` desde
  `Capa1_Long.cfx`, todos los XML internos con `MarketSides` heredan el lado
  seleccionado y el titulo Build sale como `LONG`, `SHORT` o `L+S`.
- `Build > Ranking` queda cerrado con la decision final del operador aceptando
  la recomendacion: `MaxStrategies=2000` y
  `StopCondition.passedStrategies=500`, manteniendo el resto de la logica igual
  para reducir seleccion por suerte sin ahogar la cantera.
- Limpieza `WhatToBuild/BuildMode`: se eliminan de la base local los nodos
  legacy `FilterInitialPopulation`, `EvoFitnessRestartType` y
  `EvoStagnationRestartGenerations`. SQX 142/143 lee y guarda la configuracion
  actual mediante `Conditions` y atributos de `EvoRestartOnStagnation`.
- Bloque estructural `What to build` cerrado: `StrategyType`,
  `RulesComplexity`, `SL/PT options` y simetrias de entrada/salida mantienen la
  base. El `MarketSides=long` de la plantilla se trata como placeholder y queda
  cubierto por el Project Generator.
- Bloque azul `Building blocks` cerrado segun captura: `OrderTypes` mantiene
  solo `EnterAtMarket`; `ExitTypes` mantiene solo `ExitAfterBars` activo; no se
  permiten bloques `ExitAfterDays` ni `ExitAfterTradingDays`; `CustomData`
  queda `showAll=false` y vacio. Los snippets locales de salida por dias en
  `user/extend` se archivan reversiblemente en `.local`.
- Bloque blanco `Building blocks`: `Signals` y `Stop/Limit entry blocks` quedan
  siempre desactivados para Capa1 base; `Indicators` se preserva como bloque
  dinamico gobernado por metodologia/BlockSettings.
- Subbloque `Indicators`: la base Capa1 usa `BS_Volatilidad/H4` solo como
  placeholder de plantilla, resuelto a `BS_Volatilidad_v6.sqb`; el Project
  Generator sustituye el `BuildingBlocks` final segun familia/timeframe del
  usuario. No se copian indicadores desde el donor; la fuente real es
  `backend/sqx-edge-tool/resources/blocksettings/*.sqb`.
- Bloque `Build > Data` cerrado como guardia, no como copia donor:
  `dateFrom/dateTo` siguen el periodo `BUILD_C1` de `generator_profiles.json`
  (`2017.10.02` a `2023.01.01`), `testPrecision=2` conserva data simulated,
  `session=No Session` y Build no usa rangos OOS. `Chart`, `spread` y `Swap`
  quedan genericos y los reescribe Project Generator por activo/timeframe.
- Bloque `Build > Resources` cerrado como placeholder generico controlado por
  generador: no se copian recursos `USDJPY` del donor, no hay sesiones de
  recursos, los simbolos coinciden con los `Chart` placeholder, `precision=TICK`
  se conserva como tipo de fuente y el modo simulated sigue viviendo en
  `Data/Setup testPrecision=2`.
- Bloque `Build > CrossChecks` cerrado: en minado Capa1 solo queda activo
  `SequentialOptimization`; `MonteCarlo`, `WhatIf`, `HigherPrecision`,
  `RetestOnAdditionalMarkets`, WFO/WFM y demas robustez pesada permanecen
  desactivados y no se promocionan settings internos del donor para evitar
  arrastrar simbolos, fechas o cargas impropias del Build.
- Pestañas estaticas restantes de Build cerradas por hash/auditoria:
  `Options`, `ATMs`, `PartsToImprove`, `RiskMoneyManagement`, `Databanks`,
  `Notes` y `Optimization` quedan como valores actuales confirmados. `Databanks`
  mantiene `Output=null`; el guardia documenta que el flujo real es
  minado -> `Ranking` filters -> `Results`.

Orden recomendado de preguntas: pestañas sin diferencias primero para cerrar
bloques rápidos, después `Data`, `Resources`, `WhatToBuild`, `CrossChecks` y al
final `Blocks` por volumen.

## Estado G8-SQX-AGENT-SKILLS1

Aplicado como fase puente antes de `RETEST 0`:

- Skills locales actualizadas: `sqx-edge-suite-governance` y
  `sqx142-local-intelligence`.
- Skills locales nuevas: `sqx-test-guardian` y `sqx-docs-curator`.
- Perfiles del agente local: `sqx-c1-config`, `sqx-test-guardian`,
  `sqx-docs-curator`, `sqx-academic-lopez` y `sqx-agent-skills`.
- Handoffs locales ignorados: `.local/agent_handoffs/`.
- Los guardianes pueden usarse proactivamente para lectura, revision de docs,
  matriz de tests y dry-runs seguros, pero no ejecutan `--apply`, `--write`,
  `--launch`, retests reales ni mutaciones de proyectos/databanks sin
  confirmacion explicita.

## Estado SQX142-BRANDING1

Aplicado como mini fase local antes de `RETEST 0`:

- Cambio limitado a UI web local de SQX 142: footer `Build: 142.2336 Codex`.
- About queda saneado visualmente: no muestra `Hardware ID`, `License number`
  ni `Licensed to`; en su lugar muestra
  `Optimized and Controlled by Codex 3.0 & QxPro for Edge Suite v1.0`.
- Version tecnica intacta: `/main/getCommon` sigue devolviendo
  `appVersion=142.2336`.
- No se tocaron binarios, motor, licencia, XMLs de estrategias ni endpoints.
- Backup y evidencia privada ignorada por Git:
  `.local/sqx142_branding/SQX142-BRANDING1-20260523-161541/`.
- Cache Electron refrescada archivando solo carpetas volatiles `Cache`,
  `Code Cache`, `GPUCache` y `DawnCache`.
- Smoke real local tras refresh: `http://127.0.0.1:8080/SQUANT/index.html#!/`
  mostro `ALGOTRADING Build: 142.2336 Codex ...`.
- Smoke visual About confirmado con Playwright local: modal abierto, marca
  Codex/QxPro visible y lineas privadas ausentes.
- Cierre final limpio: sin procesos `StrategyQuantX*` vivos.

Siguiente fase tras cerrar SQX142-BRANDING1: Fase 3 `RETEST 0`.

## Estado Fase 3 - RETEST 0

Fase cerrada el 2026-05-23. Objetivo: configurar `RETEST 0` como primer OOS
real de Capa1, con data no explorada y sin convertirlo en un tramite blando. Es
normal que muchas estrategias caigan aqui; el criterio de exito es coherencia,
trazabilidad, OOS1 limpio y passed/failed natural, no mejorar artificialmente el
ratio de aprobadas.

Fuente actual inspeccionada:

- Base local y template repo: `Retest-Task3.xml`.
- Input databank: `Results`.
- Output databank: `RETEST 0`.
- View asignada: `RETEST QUICK REVIEW`.
- Periodo base actual: `2017.10.02` a `2025.01.01`.
- OOS1 actual: `2023.01.01` a `2025.01.01`.
- Precision de test: `testPrecision=2`, simulated.

Reglas de decision:

- No copiar fechas vivas del donor Mining15 ni su `USDJPY/H4`.
- Mantener el rol de `RETEST 0` como OOS1 real posterior al Build Capa1
  (`BUILD_C1` termina en `2023.01.01`).
- `RETEST 0` corre el periodo completo IS+OOS1 (`2017.10.02` a
  `2025.01.01`) con el rango OOS1 marcado (`2023.01.01` a `2025.01.01`), no
  solo el tramo OOS aislado. Asi SQX puede comparar IS vs OOS1 en filtros y
  ranking; correr solo OOS1 perderia la referencia IS del mismo retest.
- Las caidas masivas no autorizan suavizar filtros sin evidencia explicita y
  nueva decision metodologica.
- Project Generator mantiene propiedad sobre simbolo, timeframe, spread,
  swap, recursos y lado de mercado cuando dependan de activo/timeframe.
- Costes de `Data`: spread, swaps, comisiones y recursos son placeholders en la
  base; Project Generator los reescribe por instrumento. Si no hay `data.db`,
  el fallback queda normalizado a comision neutra `SizeBased=0.0` en todos los
  tasks generados.
- La fase cierra sin mutacion adicional de base/template: las decisiones finales
  mantienen base o placeholders gobernados por Project Generator. Los cambios
  reales necesarios ya quedan cubiertos por el guardia de comisiones fallback en
  el generador.

Mapa inicial del cuestionario:

- `14` pestañas detectadas.
- `18.176` entradas auditadas.
- `8.344` diferencias base vs donor.
- `CrossChecks` fue regenerado tras corregir IDs largos de cuestionario: `367`
  preguntas y `367` respuestas unicas en ledger local.
- El gate incorpora `record-tab-answer` para registrar de forma atomica una
  decision agrupada sobre pestañas gigantes, rechazando cuestionarios con IDs
  duplicados. `Blocks` de `RETEST 0` fue regenerado con IDs unicos antes de
  cualquier respuesta masiva: `17.583` preguntas, `8.331` diferencias y `0`
  duplicados.
- La mayoria de diferencias vive en `Blocks`; se tratan como ruido de donor
  salvo que una pregunta concreta demuestre valor metodologico.
- Primer bloque operativo cerrado: `Data/OOS`, porque define si el retest
  conserva la frontera real entre Build IS y primer OOS.
- Pestañas `Data`, `Options`, `Databanks`, `Rankings`, `Resources`,
  `WhatToBuild`, `CrossChecks`, `ATMs`, `RiskMoneyManagement`,
  `PartsToImprove`, `Notes`, `Optimization` y `SelectedStrategies` quedan
  respondidas en ledger local segun confirmacion del operador.
- `Blocks` queda cerrado con `17.583/17.583` respuestas: mantener base completa,
  porque `RETEST 0` no debe generar estrategias nuevas. `Signals` y
  `Stop/Limit` permanecen inactivos, `Indicators` sigue gobernado por
  metodologia/BlockSettings, y solo se conserva `EnterAtMarket` +
  `ExitAfterBars`. No se copia el donor porque arrastra universo especifico de
  Mining15/volatilidad y no aporta al retest OOS.
- Reporte local de cierre: `.local/sqx142_task_config/phase_reports/`.
- Siguiente fase exacta: Fase 4 `RETEST 1`.

## Estado Fase 4 - RETEST 1

Fase abierta el 2026-05-23. Objetivo: revisar `RETEST 1` sin asumir que es un
duplicado de `RETEST 0`. `RETEST 1` mapea a `Retest-Task1.xml`; segun
gobernanza, generator profiles y tests existentes, su rol metodologico
protegido es OOS2/cross-broker Dukascopy `2010.01.01` a `2017.10.02`, con
entrada desde `RETEST 0` y salida a `retest 1`.

Decision operativa aplicada para el bloque inicial:

- `RETEST 1` queda tratado como clon pasivo de `RETEST 0` mas override
  protegido Dukascopy/OOS2.
- `Data` y `Resources` son el corazon de esta decision y quedan cerrados en
  base local y template repo con backup/diff dry-run-first.
- `Retest-Task1.xml` usa `RETEST_1_C1` (`2010.01.01` a `2017.10.02`),
  `testPrecision=2`, `No Session`, placeholder `AUDCAD_dukascopy`, source `2`,
  broker `3`, spread `1.9` resuelto desde `data.db`, sin rangos OOS internos y
  sin sesiones ni `CustomBlocks` embebidos en `Resources`.
- Los `Setup/Chart` internos de crosschecks desactivados tambien se normalizan
  al placeholder Dukascopy para no dejar referencias Darwinex huérfanas que
  rompan la compatibilidad SQX142.
- No se copia literalmente el donor Mining15: el target sale de governance del
  Project Generator mas evidencia local SQX142, y el generador reescribira el
  activo/timeframe real manteniendo la regla cross-broker protegida.
- Ledger local respondido para `RETEST 1 > Data` (`8/8`) y
  `RETEST 1 > Resources` (`12/12`).

Decision aplicada para `Options` / `Databanks` / `Rankings`:

- `Options` mantiene `No Session`, ventana H1 placeholder `02:00-22:00`
  (`7200-79200`) gobernada por Project Generator segun timeframe, y sube
  `RealisticGapsHandling=true` para que OOS2/cross-broker no sea mas blando
  que `RETEST 0`.
- `Databanks` queda cerrado como cadena pasiva `Input=RETEST 0` y
  `Output=retest 1`.
- `Rankings` queda `advisory-not-coladero`: `DeleteFailedStrategies=false`
  conserva filas failed para analisis y trazabilidad, pero los filtros siguen
  activos con `NumberOfTrades >= 100`, `RExpectancy > 0.05` y
  `NetProfit >= 0`.
- `FitPortfolio=false`; `RETEST 1` valida OOS2/cross-broker en Capa1 y no debe
  hacer seleccion de portfolio ni usar `Existing portfolio`.
- Ledger local respondido para `RETEST 1 > Options` (`34/34`),
  `RETEST 1 > Databanks` (`3/3`) y `RETEST 1 > Rankings` (`40/40`).

Decision aplicada para `PartsToImprove` / `WhatToBuild` / `Blocks`:

- `PartsToImprove` queda pasivo puro: `EntryRules`, `OrderTypes` y `ExitRules`
  tienen `LongImprovement` y `ShortImprovement` en `use=false`; se apaga el
  antiguo resto de mejora de salida que podia convertir el retest en retrabajo.
- `WhatToBuild/StrategyType` queda apuntando a `improveDatabank=RETEST 0` para
  reflejar la cadena real de entrada. `BuildMode.generationType` se conserva
  como `random-generation` porque no se ha encontrado en CFX locales un enum SQX
  seguro de tipo `none/passive`; la pasividad se impone con databank de entrada,
  mejoras apagadas y toggles de evolucion/fresh blood apagados.
- `BuildMode` desactiva `ShowLastGenerationDatabank`,
  `FreshBloodReplaceSimilar`, `FreshBloodReplaceWeakest`,
  `EvoRestartOnFinish` y `EvoRestartOnStagnation`.
- `Blocks` se normaliza desde el contrato interno ya aprobado de `RETEST 0`, no
  desde Mining15 donor: `Signals` y `Stop/Limit` quedan inactivos, los
  indicadores permanecen gobernados por metodologia/BlockSettings,
  `EnterAtMarket` es la unica entrada activa y `ExitAfterBars` queda como unica
  salida activa con probabilidad `100`.
- No hay salidas por dias: `ExitAfterDays` y `ExitAfterTradingDays` quedan
  prohibidos para este bloque.
- Ledger local respondido para `RETEST 1 > PartsToImprove` (`9/9`),
  `RETEST 1 > WhatToBuild` (`67/67`) y `RETEST 1 > Blocks`
  (`17.583/17.583`).

Decision aplicada para pestañas estaticas restantes y `CrossChecks`:

- `CrossChecks` queda completamente apagado en `RETEST 1`: parent
  `use=false/evaluateAll=false`, todos los checks directos `use=false` y todos
  los `Settings/Methods/Method` internos `use=false`.
- Se conserva la normalizacion de los setups internos desactivados a
  Dukascopy/OOS2, pero no queda ningun metodo de robustez ejecutable dentro de
  este retest.
- `RiskMoneyManagement` se alinea con `RETEST 0` y el resto de retests Capa1:
  `FixedSize=true` y `FixedAmount=false`, para no meter ruido de sizing en la
  comparacion OOS2.
- `ATMs` se mantiene desactivado, `Notes` se conserva y
  `SelectedStrategies` queda vacio en base/template.
- El guard de generacion pasiva sigue verde: no quedan mejoras activas,
  fresh-blood/evolucion quedan apagados, `Signals`/`StopLimit` quedan off y no
  se reintroducen salidas por dias.
- Ledger local respondido para `RETEST 1 > CrossChecks` (`339/339`),
  `RETEST 1 > RiskMoneyManagement` (`25/25`), `RETEST 1 > ATMs` (`9/9`),
  `RETEST 1 > Notes` (`1/1`) y `RETEST 1 > SelectedStrategies` (`0/0`).

Cuestionario inicial generado:

- `13` pestañas detectadas.
- `20.024` entradas auditadas.
- `12.343` diferencias base vs donor.
- Todos los IDs del cuestionario son unicos; no hay duplicados.
- `RETEST 1` no contiene seccion `Optimization`, a diferencia de `RETEST 0`.

Diferencias estructurales detectadas antes de decidir:

- `Databanks` coincide en base y donor: input `RETEST 0`, output `retest 1`.
- `Data` ya no arrastra el periodo `2017.10.02` a `2025.01.01`: queda alineado
  con OOS2 Dukascopy `2010.01.01` a `2017.10.02`.
- `Resources` ya no conserva recursos Darwinex pesados ni `CustomBlocks`
  embebidos: queda compacto en Dukascopy source `2` / broker `3`, sin copia
  literal del donor.
- `Blocks` ya no queda abierto: se cerro como contrato pasivo desde `RETEST 0`,
  con universo controlado, indicadores/metodologia y `ExitAfterBars` principal.
- `PartsToImprove` ya no mantiene `ExitRules` activo; `WhatToBuild` conserva el
  enum SQX conocido `random-generation` solo como placeholder interno, con los
  toggles de mejora/evolucion apagados.
- `Rankings/DeleteFailedStrategies` difiere: base `false`, donor `true`.
- `Options` ya no contiene sesion donor ni gaps blandos: `MarketOpenSession`
  queda `No Session` y `RealisticGapsHandling=true`; la ventana horaria sigue
  siendo generator-owned por timeframe.
- `Rankings/DeleteFailedStrategies=false` se mantiene a proposito como modo
  advisory; no fuerza `Results=passed` ni borra failed.
- `RiskMoneyManagement` ya no queda abierto: se cerro en `FixedSize=true` /
  `FixedAmount=false` como `RETEST 0` y los retests Capa1.

Fase cerrada formalmente el 2026-05-23 con reporte local:
`.local/sqx142_task_config/phase_reports/phase4_20260523_194139.json`.
`RETEST 1` queda protegido como OOS2/Dukascopy pasivo y el siguiente paso
exacto es Fase 5 `TICK REAL`.

## Estado Fase 5 - TICK REAL

Fase abierta el 2026-05-23. Objetivo: comprobar si las estrategias que ya
superaron `RETEST 0` y `RETEST 1` sobreviven a la precision de data del retest
de robustez, sin mezclarlo con generacion, portfolio ni crosschecks internos.

Fuente actual inspeccionada:

- Base local y template repo: `AutomaticRetest-Task2.xml`.
- Cuestionario vigente en ledger local: `13` pestañas, `19.992` entradas tras
  el guard estatico, `12.334` diferencias base vs donor y `0` IDs duplicados.
- Periodo gobernado por metodologia/generador: `ROBUSTNESS_C1`
  (`2017.10.02` a `2023.12.31`).
- `Data/Setup` actual: `testPrecision=2`, `session=No Session`, engine
  `MetaTrader5 (hedged)`.
- Recursos actuales: placeholder Darwinex (`AUDCAD_darwinex`, source `4`,
  broker `4`) con `precision=TICK`; activo/timeframe/spread/swap siguen siendo
  generator-owned.
- `CrossChecks` padre esta desactivado, pero conserva settings internos de
  metodos desactivados; se revisara como bloque propio antes del cierre de
  fase para evitar restos ejecutables.

Decision aplicada para `TICK REAL > Data / Databanks / Resources`:

- Se anade `tick-real-data-databanks-resources-target` con dry-run-first,
  backup/diff cuando hay escritura, guard de recursos y evidencia local
  ignorada por Git.
- `TICK REAL` queda como retest pasivo posterior a `RETEST 1`:
  `Input=retest 1` y `Output=TICK`; no consume `RETEST 0` directamente.
- Periodo: `ROBUSTNESS_C1` (`2017.10.02` a `2023.12.31`).
- `Data/Setup`: `testPrecision=2`, `session=No Session`, sin rangos OOS
  internos.
- `Resources`: placeholder Darwinex generico `AUDCAD_darwinex`, source `4`,
  broker `4`, `precision=TICK`, timezone `EETUS`, fecha de recurso acotada a
  `2023.12.31`, sesiones vacias y `CustomBlocks` preservados.
- No se copia el donor `USDJPY/H4`; activo, timeframe, spread, swap y rebuild
  final de recursos siguen siendo propiedad del Project Generator.
- El dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `TICK REAL > Data` (`7/7`),
  `TICK REAL > Databanks` (`3/3`) y `TICK REAL > Resources` (`1.899/1.899`).

Reporte local:
`.local/sqx142_task_config/phase_reports/phase5_20260523_195637.json`.

Decision aplicada para `TICK REAL > Options / Rankings`:

- Se anade `tick-real-options-rankings-target` con dry-run-first,
  backup/diff/apply, guard contra coladero y tests negativos.
- Criterio academico aplicado: no se anade split IS/OOS1 interno a TICK REAL.
  `RETEST 0` ya gobierna IS/OOS1; repetir ese split dentro del gate de tick
  aumenta riesgo de data-snooping/backtest overfitting. TICK queda como test de
  precision-data sobre el periodo total `ROBUSTNESS_C1`.
  Referencias consultadas: Bailey/Borwein/Lopez de Prado/Zhu sobre backtest
  overfitting (`https://ssrn.com/abstract=2308659`), White Reality Check para
  data snooping (`https://doi.org/10.1111/1468-0262.00152`) y Hansen SPA para
  comparaciones predictivas multiples (`https://ssrn.com/abstract=264569`).
- `Options`: `No Session`, `StoreChartData=false`,
  `RealisticGapsHandling=true`, `LimitTimeRange=true` y ventana placeholder H1
  `02:00-22:00`; Project Generator reescribe la ventana por timeframe.
- `Rankings`: `DeleteFailedStrategies=false` para conservar failed naturales,
  `ConditionsType=1`, `ForceRunCrossChecks=false`, `FitPortfolio=false`,
  `CustomAnalysis.filter=false`.
- Filtros activos total-tick: `NumberOfTrades >= 200`,
  `ProfitFactor >= 1.3`, `WinningPct >= 50` y `ReturnDDRatio >= 4`.
- Se evita el coladero manteniendo condiciones activas y el estado failed real;
  no se fuerza `Results=passed` ni se borran filas failed.
- El dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `TICK REAL > Options` (`34/34`) y
  `TICK REAL > Rankings` (`46/46`).

Reporte local:
`.local/sqx142_task_config/phase_reports/phase5_20260523_202446.json`.

Decision aplicada para `TICK REAL > PartsToImprove / WhatToBuild / Blocks`:

- Se anade `tick-real-passive-generation-target` con dry-run-first,
  backup/diff/apply, guard de pasividad e idempotencia posterior.
- `PartsToImprove` queda pasivo puro: no mejora ATM, reglas de entrada, tipos
  de orden ni reglas de salida; `LongImprovement` y `ShortImprovement` quedan
  `use=false`.
- `WhatToBuild/StrategyType` consume `improveDatabank=retest 1`. El
  `BuildMode.generationType=random-generation` se conserva como enum conocido
  de SQX porque no hay un enum local seguro de "none/passive", pero la conducta
  pasiva queda forzada por input databank, mejoras desactivadas y toggles de
  evolucion apagados.
- `ShowLastGenerationDatabank=false`, `FreshBloodReplaceSimilar=false`,
  `FreshBloodReplaceWeakest=false`, `EvoRestartOnFinish=false` y
  `EvoRestartOnStagnation=false`.
- `Blocks` preserva el universo existente de `TICK REAL` para no cambiar la
  logica heredada por error; solo aplica el contrato pasivo: `signals` y
  `stopLimitBlocks` quedan desactivados, `Indicators` sigue gobernado por
  metodologia/BlockSettings, `EnterAtMarket` es la unica entrada y
  `ExitAfterBars` es la unica salida activa con probabilidad `100`.
- No quedan salidas por dias (`ExitAfterDays` / `ExitAfterTradingDays`) ni
  `CustomData` externo visible; `CustomData.showAll=false`.
- Estado post-apply: `activeBlockCount=100`, `activeIndicatorCount=50`,
  `activeSignalCount=0`, `activeStopLimitCount=0`, `changedActionCount=0` y
  `guardOk=true` en dry-run posterior.
- Ledger local respondido para `TICK REAL > PartsToImprove` (`9/9`),
  `TICK REAL > WhatToBuild` (`67/67`) y `TICK REAL > Blocks`
  (`17.583/17.583`).

Reporte local:
`.local/sqx142_task_config/phase_reports/phase5_20260523_204910.json`.

Decision aplicada para `TICK REAL > pestañas estaticas restantes y
CrossChecks`:

- Se anade `tick-real-static-crosschecks-target` con dry-run-first,
  backup/diff/apply, guard compuesto e idempotencia posterior.
- `CrossChecks` queda completamente no ejecutable: parent `use=false`,
  `evaluateAll=false`, `0` crosschecks directos activos y `0`
  `Settings/Methods/Method` internos activos.
- Se limpiaron los restos internos que quedaban aunque el parent estuviera
  apagado: `MonteCarloRetest` tenia `6` metodos activos,
  `MonteCarloManipulation` tenia `2` y `WhatIf` tenia `2`.
- `RiskMoneyManagement` queda como retest Capa1 comparable:
  `FixedSize=true`, `FixedAmount=false` y resto de metodos desactivados.
- `ATMs` queda `enable=false`; `Notes` se mantiene sin cambios.
- `CustomData` queda auditado, no copiado desde Mining15: periodo
  `ROBUSTNESS_C1`, `session=No Session`, sin `USDJPY` donor leak y sin rutas
  locales. No se usa para cambiar activo/timeframe final, que sigue siendo
  propiedad del Project Generator.
- El dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `TICK REAL > CrossChecks` (`303/303`),
  `TICK REAL > RiskMoneyManagement` (`25/25`), `TICK REAL > ATMs` (`9/9`),
  `TICK REAL > CustomData` (`6/6`) y `TICK REAL > Notes` (`1/1`).

Reporte local:
`.local/sqx142_task_config/phase_reports/phase5_20260523_210515.json`.

Fase cerrada formalmente el 2026-05-23 con reporte local:
`.local/sqx142_task_config/phase_reports/phase5_tick_real_closeout_20260523_211917.json`.
El cierre reejecuto en dry-run los cuatro guards de TICK REAL
(`tick-real-data-databanks-resources-target`,
`tick-real-options-rankings-target`, `tick-real-passive-generation-target` y
`tick-real-static-crosschecks-target`) contra base local y template repo:
`ok=true`, `changed=false`, `changedActionCount=0` y `guardOk=true` en todos
los bloques. La cadena queda `Input=retest 1` / `Output=TICK`, failed
naturales preservados y sin crosschecks/metodos internos ejecutables.

## Estado Fase 6 - MC

Fase abierta el 2026-05-23. Objetivo: comprobar robustez por perturbacion
Monte Carlo sobre candidatos que ya pasaron `RETEST 0`, `RETEST 1` y `TICK
REAL`, sin convertir MC en un optimizador ni en otro filtro que contamine OOS.

Fuente actual inspeccionada:

- Base local y template repo: `AutomaticRetest-Task1.xml`.
- Cuestionario vigente en ledger local: `13` pestañas, `19.966` entradas y
  `12.326` diferencias base vs donor.
- Databanks actuales: `Input=TICK` y `Output=MC`.
- `Data/Setup` actual: `dateFrom=2017.10.02`, `dateTo=2023.12.31`,
  `testPrecision=2`, `session=No Session` y engine `MetaTrader5 (hedged)`.
- Los recursos, activo, timeframe, spread y swaps siguen siendo
  generator-owned; no se copia el donor `USDJPY/H4`.

Criterio inicial recomendado antes del cuestionario:

- MC debe quedar en precision fast/simulated (`testPrecision=2`) por eficacia
  computacional: TICK REAL ya cubre la supervivencia a precision-data y MC
  debe medir estabilidad ante perturbaciones, no repetir el coste maximo de
  tick en cada simulacion.
- No anadir split OOS interno por defecto. `RETEST 0` y `RETEST 1` ya gobiernan
  OOS; reusar OOS dentro de MC para seleccionar candidatos aumenta presion de
  seleccion, data snooping y backtest overfitting.
- Mantener passed/failed naturales: MC puede fallar candidatos, pero no se
  fuerza `Results=passed` ni se borran failed por comodidad.
- El primer bloque a decidir sera `MC > Data / Databanks / Resources /
  Options`; despues se abrira `MC > CrossChecks`, donde vive el metodo Monte
  Carlo real.

Consulta academica registrada:

- White, "A Reality Check for Data Snooping", Econometrica 2000:
  `https://doi.org/10.1111/1468-0262.00152`.
- Bailey, Borwein, Lopez de Prado y Zhu, "Pseudo-Mathematics and Financial
  Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample
  Performance": `https://ssrn.com/abstract=2308659`.
- Bailey y Lopez de Prado, "The Deflated Sharpe Ratio: Correcting for
  Selection Bias, Backtest Overfitting and Non-Normality":
  `https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf`.
- Carr y Lopez de Prado, "Determining Optimal Trading Rules without
  Backtesting": `https://doi.org/10.48550/arXiv.1408.1159`.

Decision aplicada para `MC > Data / Databanks / Resources / Options`:

- Se anade `mc-data-databanks-resources-options-target` con dry-run-first,
  backup/diff/apply y guard contra contaminacion OOS/donor.
- `MC` queda como retest de perturbacion posterior a `TICK`:
  `Input=TICK` y `Output=MC`.
- Periodo: `ROBUSTNESS_C1` (`2017.10.02` a `2023.12.31`).
- `Data/Setup`: `testPrecision=2` fast/simulated, `session=No Session`, sin
  rangos OOS internos.
- `Resources`: placeholder Darwinex generico `AUDCAD_darwinex`, source `4`,
  broker `4`, `precision=TICK`, timezone `EETUS`, fechas acotadas a
  `2023.12.31`, sesiones vacias y `CustomBlocks` preservados.
- `Options`: se mantiene la base generica para MC rapido:
  `Session=No Session`, `MarketOpenSession=No Session`,
  `StoreChartData=false`, `RealisticGapsHandling=false` y
  `LimitTimeRange=false`.
- No se copia el donor `USDJPY/H4` ni la ventana H4 `04:00-20:00`; activo,
  timeframe, spread, swap y recursos finales siguen siendo propiedad de
  Project Generator.
- El dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `MC > Data` (`7/7`), `MC > Databanks` (`2/2`),
  `MC > Resources` (`1.899/1.899`) y `MC > Options` (`34/34`).

Reporte local:
`.local/sqx142_task_config/phase_reports/phase6_mc_data_databanks_resources_options_20260523_214211.json`.

Decision aplicada para `MC > CrossChecks`:

- Se anade `mc-crosschecks-target` con dry-run-first, backup/diff/apply y guard
  especifico de metodo Monte Carlo.
- `CrossChecks` queda ejecutable en el task `MC`: parent `use=true` y
  `evaluateAll=true`.
- Solo queda activo `MonteCarloManipulation`; `MC 2`, `Monkey Test` y
  `Synthetic` siguen siendo tareas separadas y no se mezclan aqui.
- Metodo activo: `RandomizeTradesOrder` con `Method=resampling`.
- Metodo apagado dentro del activo: `RandomlySkipTrades=false` con
  `Probability=10` preservado como parametro no ejecutable.
- Ajustes: `NumberOfSimulations=200` y `MCUseFullSample=true`, coherente con
  no crear OOS interno dentro de MC.
- Condiciones de aceptacion naturales a confianza `80`: `NetProfit`
  MonteCarloManipulation `>= 40%` del `NetProfit` main y `DrawdownPct`
  MonteCarloManipulation `<= 200%` del `DrawdownPct` main.
- Se apagan los metodos residuales que estaban activos dentro de crosschecks
  desactivados (`MonteCarloRetest` y `WhatIf`) para evitar ejecucion accidental
  o ruido futuro.
- Los setups internos de crosschecks desactivados quedan acotados a
  `ROBUSTNESS_C1` (`2017.10.02` a `2023.12.31`), `testPrecision=2`,
  `session=No Session` y el chart seed generico actual.
- No se copia donor `USDJPY/H4`; Project Generator sigue siendo propietario del
  activo/timeframe/spread/swap final.
- El dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `MC > CrossChecks` (`303/303`).

Reporte local:
`.local/sqx142_task_config/phase_reports/phase6_mc_crosschecks_20260523_220422.json`.

Decision aplicada para `MC > PartsToImprove / WhatToBuild / Blocks`:

- Se anade `mc-passive-generation-target` con dry-run-first,
  backup/diff/apply y guard especifico de retest pasivo.
- `MC` consume candidatos desde `TICK`: `StrategyType.improveDatabank=TICK`.
- `PartsToImprove` queda sin mejora/generacion: `improveATM=false`,
  Entry/Order/Exit improvements off y simetrias sin copia donor.
- `WhatToBuild` mantiene `MarketSides` base/generator-owned, apaga
  `ShowLastGenerationDatabank`, `FreshBloodReplaceSimilar`,
  `FreshBloodReplaceWeakest`, `EvoRestartOnFinish` y
  `EvoRestartOnStagnation`.
- `Blocks` conserva el universo MC existente para evitar drift Mining15, con
  `signals=0`, `stopLimitBlocks=0`, `activeIndicatorCount=50`,
  solo `EnterAtMarket` y solo `ExitAfterBars` con probability `100`.
- No se copian bloques donor `USDJPY/H4`, no se aceptan salidas por dias y no
  se inventa un enum SQX pasivo desconocido para `generationType`.
- El dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `MC > PartsToImprove` (`8/8`),
  `MC > WhatToBuild` (`67/67`) y `MC > Blocks` (`17.583/17.583`).

Reporte local:
`.local/sqx142_task_config/phase_reports/phase6_mc_passive_generation_20260523_221854.json`.

Decision aplicada para `MC > Rankings / ATMs / RiskMoneyManagement / Notes / SelectedStrategies / CustomData`:

- Se anade `mc-static-tabs-target` con dry-run-first, backup/diff/apply y
  guard compuesto sobre los bloques MC anteriores.
- `Rankings` queda sin filtros extra: `ConditionsType=1`, sin condiciones,
  `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false` y
  `CustomAnalysis.filter=false`.
- `FitPortfolio=false`; MC no hace seleccion de portfolio en Capa1 y el
  passed/failed queda gobernado por `MonteCarloManipulation`.
- `ATMs` queda desactivado y `RiskMoneyManagement` mantiene `FixedSize=true`
  con el resto de modos de riesgo apagados para comparabilidad de retest.
- `Notes` se preserva y `SelectedStrategies` ausente/vacio queda aceptado como
  estado pasivo valido.
- `CustomData` queda generico/no donor: sin copia `USDJPY/H4`, chart seed
  sincronizado con el Data principal, `Commission=0.0` y `testPrecision=2`
  simulated.
- El dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `MC > Rankings` (`22/22`), `MC > ATMs` (`9/9`),
  `MC > RiskMoneyManagement` (`25/25`), `MC > Notes` (`1/1`),
  `MC > SelectedStrategies` (`0/0` allow-empty) y `MC > CustomData` (`6/6`).

Reporte local:
`.local/sqx142_task_config/phase_reports/phase6_mc_static_tabs_20260523_223913.json`.

Siguiente bloque exacto: `phase6_mc_closeout`, para reejecutar todos los guards
MC en dry-run y cerrar formalmente la Fase 6 antes de `MC 2`.

## Disciplina Operativa

En cada fase:

1. Extraer valores actuales.
2. Mostrar pregunta con valor actual, donor, recomendacion y opciones para
   todas las entradas detectadas.
3. Guardar cada respuesta inmediatamente en `.local/sqx142_task_config/answers`.
4. Aplicar primero en clon o dry-run.
5. Mostrar diff antes de tocar base.
6. Aplicar a base solo con la fase cerrada.
7. Emitir reporte de fase.
8. Indicar exactamente que fase toca en el siguiente mensaje.
9. Invocar `SQX Test Guardian` y/o `SQX Docs Curator` cuando haya riesgo de
   regresion, drift documental o verificacion paralela util.

## Criterios De Aceptacion

- `tools\sqx142_task_config_gate.ps1 preflight --apply` queda `ok: true`.
- El ledger local conserva `session_state.json`, snapshots y diff.
- El roadmap y governance nombran C1-CONFIG1.
- La Fase 1 no deja `viewAssignments` pendientes en el diff semantico.
- Docs guard pasa.
- Antes de promocionar cambios reales a la base, existe diff y rollback.

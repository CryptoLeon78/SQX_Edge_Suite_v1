# SQX142 Custom Task Config Roadmap

Estado: C1-CONFIG1 con Fase 19
`Capa2 Retest 1` cerrada el 2026-05-25 con
`phase19_capa2_retest1_target_20260525_003750.json`, despues de
cerrar `phase18_capa2_retest0_target_20260524_234752.json`, despues de
cerrar `phase17_capa2_build_static_tabs_target_20260524_231540.json`,
despues de
cerrar `phase17_capa2_build_crosschecks_target_20260524_223128.json`,
despues de
cerrar `phase17_capa2_build_rankings_target_20260524_220916.json`,
`phase17_capa2_build_data_databanks_resources_options_target_20260524_213626.json`,
`phase17_capa2_build_blocks_target_20260524_211347.json` y
`phase17_capa2_build_what_to_build_target_20260524_204601.json`,
despues de generar `phase17_capa2_build_questionnaire_20260524_201405.json`,
despues de la Fase 16 `Capa2 Preflight Snapshot`
(`phase16_capa2_preflight_snapshot_20260524_195729.json`) y de la Fase 15
`Capa2 Planning`
(`phase15_capa2_planning_20260524_190708.json`) y de la Fase 14
`Capa1 Closeout` (`phase14_capa1_closeout_20260524_183012.json`) y de
`phase13_foward_closeout` verde (`phase13_foward_closeout_20260524_182647.json`).
Capa2 queda planificada, no aplicada: integra SL/TP/trailing, elimina
`ExitAfterBars` como salida de Build, agrega un filtro de indicador gobernado
por BlockSettings/metodologia y protege que la ventaja detectada en Capa1 no
se fabrique despues por gestion de riesgo. No lanza SQX, no hace smoke, no
inicia optimizacion, no toca CFX y no fuerza `Results=passed`. Fase 16 deja
snapshot local y rollback selectivo en
`.local/sqx142_task_config/snapshots/phase16_capa2_preflight_20260524_195729/`.
Phase17 deja cuestionarios completos de Build Capa2 en
`.local/sqx142_task_config/questionnaires/capa2/Build_strategies/`: 13
pestanas, 16.647 entradas detectadas y 6 diferencias base/template. El
bloque WhatToBuild queda cerrado con 67/67 respuestas, `StrategyType=template`,
`templateFile` operator-owned solo local, repo `templateFile` limpio,
`MarketSides` generator-owned, SL/PT bounded, BuildMode acotado y sin cambios
CFX semanticos porque local base y template repo ya estaban alineados. El
bloque Blocks queda cerrado con 15.995/15.995 respuestas, `EnterAtMarket`
only, SL/PT al 100%, `TrailingStop` al 50%, `ExitAfterBars=false`, salidas por
dias desactivadas, `AlwaysTrue` neutral, filtro indicador Capa2 y stop/limit
entries off, tambien sin cambios CFX semanticos. El bloque
Data/Databanks/Resources/Options queda cerrado con 48/48 respuestas: periodo
`BUILD 2017.10.02-2023.12.31`, `testPrecision=2 simulated`, seed generico
`AUDCAD_darwinex/H1/TICK/EETUS`, sin OOS interno, `Input=Results`,
`Output=null`, Options `No Session`, `RealisticGapsHandling=true` y
`StoreChartData=false`; `generator_profiles.json` ya gobierna ventanas Capa2
por timeframe y evita inyectarlas en retests pesados. Rankings queda cerrado
con 173/173 respuestas y `Build-Task1.xml` como identidad tecnica:
`MaxStrategies=2000`, `passedStrategies=500`, `DeleteFailedStrategies=false`,
`ForceRunCrossChecks=false`, `FitPortfolio=false`, `CustomAnalysis=false`,
objetivo unico `RExpectancy` y filtros `NumberOfTrades >= 120`,
`ProfitFactor >= 1.1`, `Expectancy >= 0.05`. CrossChecks queda cerrado con
303/303 respuestas como superficie inerte: `CrossChecks use=false`,
`evaluateAll=false`, cero checks activos, metodos/condiciones ocultas
apagadas, `ForceRunCrossChecks=false` protegido y setups internos
normalizados al seed generico Capa2 Build. Static Tabs queda cerrado con
61/61 respuestas: `FixedAmount` activo como sizing seed de Build Capa2, ATMs
desactivados, mejora de entradas/tipos de orden apagada, mejora de salidas
activa para la capa SL/TP/trailing, Optimization acotado y Notes preservado,
sin cambios CFX semanticos porque local base y template repo ya estaban
alineados. Retest 0 Capa2 queda cerrado como validacion OOS1, no tuning:
`Retest-Task1.xml`, `Input=Results`, `Output=RETEST 0`, periodo
`2017.10.02-2025.01.01`, OOS1 `2024.01.01-2025.01.01`, FOWARD reservado
desde `2025.01.01`, `StrategyType` pasivo desde Results, `PartsToImprove`
off, `CrossChecks use=false`, `FitPortfolio=false`, `CustomAnalysis=false`,
filtros OOS predeclarados `NumberOfTrades >= 80`, `ProfitFactor >= 1.05`,
`ReturnDDRatio >= 1` y `ExitAfterBars=false`. Retest 1 Capa2 queda cerrado
como validacion historica cross-broker, no tuning: `AutomaticRetest-Task7.xml`,
`Input=RETEST 0`, `Output=retest 1`, periodo `RETEST_1
2010.01.01-2017.10.02`, `CustomData` canonico sin `Data`, data Dukascopy
`AUDCAD_dukascopy` source `2` broker `3`, `StrategyType` pasivo desde
`RETEST 0`, `CrossChecks use=false/evaluateAll=false`, `FitPortfolio=false`,
`CustomAnalysis=false`, filtros predeclarados `NumberOfTrades >= 80`,
`ProfitFactor >= 1.05`, `ReturnDDRatio >= 1` y `ExitAfterBars=false`.
`phase20_capa2_tick_real` y el resto de Capa2 vuelven a Darwinex. El
siguiente bloque exacto es `phase20_capa2_tick_real`. Fase 0 dejo
preflight, snapshots y diff semantico en `.local/sqx142_task_config/`; Fase 1
promociono las views ligeras/especializadas desde Mining15 a la base local y al
template repo; Fase 2 genero los cuestionarios completos de Build Capa1 y cerro
Build. Antes de `RETEST 0`, G8-SQX-AGENT-SKILLS1 alinea skills, guardianes,
perfiles del agente y handoffs locales para proteger el resto del cuestionario.
Antes de cerrar TICK y abrir MC, `sqx-academic-lopez` queda disponible como
consulta academica local-only para OOS, MC, data snooping y backtest
overfitting.
Fase 8 `Sequential` queda cerrada formalmente con
`phase8_sequential_closeout_20260524_085653.json`: `Input=MC2`,
`Output=Sequential`,
portador dual `Data+CustomData` sincronizado para SQX142, Options inertes,
solo `SequentialOptimization` activo, `ApplyToStrategy=false`, aceptacion
`80/5/25`, metodos ocultos de crosschecks inactivos apagados,
`StrategyType.improveDatabank=MC2`, `PartsToImprove` pasivo, evolution restarts
apagados, no Signals, no Stop/Limit entry blocks, Indicators preservados, solo
`EnterAtMarket` + `ExitAfterBars` probability `100`, Rankings inert,
`FitPortfolio=false`, `CustomAnalysis.filter=false`, ATMs disabled, FixedSize
active y `SelectedStrategies` empty. Todos los guards quedan `ok=true`,
`changed=false`, `changedActionCount=0`, `guardOk=true`, con `issues=[]`,
`warnings=[]`, `processes=[]`. Siguiente bloque exacto
`phase9_monkey_test_open`.
Subbloques cerrados: `Sequential > Data / Databanks / Resources / Options`,
`Sequential > CrossChecks`, `Sequential > Passive Generation` y
`Sequential > Static Tabs`.
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
tools\sqx142_task_config_gate.ps1 mc-closeout-report --target both
tools\sqx142_task_config_gate.ps1 mc-closeout-report --target both --write
tools\sqx142_task_config_gate.ps1 archive-exit-day-snippets
tools\sqx142_task_config_gate.ps1 archive-exit-day-snippets --apply
tools\sqx142_task_config_gate.ps1 task-questionnaires --task-title "Build BS_Volatilidad_v6 · Capa1 L+S H4" --write
tools\sqx142_task_config_gate.ps1 questionnaire --task-title "MC 2" --tab "CrossChecks" --write
tools\sqx142_task_config_gate.ps1 questionnaire --task-title "MC 2" --tab "CrossChecks" --write --full-output
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
tools\sqx142_task_config_gate.ps1 questionnaire --task-title "Sequential" --tab "CrossChecks" --write
tools\sqx142_task_config_gate.ps1 sequential-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 sequential-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 sequential-passive-generation-target --target both
tools\sqx142_task_config_gate.ps1 sequential-passive-generation-target --target both --apply
tools\sqx142_task_config_gate.ps1 sequential-static-tabs-target --target both
tools\sqx142_task_config_gate.ps1 sequential-static-tabs-target --target both --apply
tools\sqx142_task_config_gate.ps1 sequential-closeout-report --target both
tools\sqx142_task_config_gate.ps1 sequential-closeout-report --target both --write
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
tools\sqx142_task_config_gate.ps1 wfm-open-report --target both
tools\sqx142_task_config_gate.ps1 wfm-open-report --target both --write
tools\sqx142_task_config_gate.ps1 wfm-data-databanks-resources-options-target --target both
tools\sqx142_task_config_gate.ps1 wfm-data-databanks-resources-options-target --target both --apply
tools\sqx142_task_config_gate.ps1 wfm-crosschecks-target --target both
tools\sqx142_task_config_gate.ps1 wfm-crosschecks-target --target both --apply
tools\sqx142_task_config_gate.ps1 task-questionnaires --task-title "SPP" --write
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
15. `Capa2 Planning`, puerta read-only anti-overfit antes de tocar Capa2.
16. `Capa2 Preflight Snapshot`, backup/diff/rollback de base local, template,
    generator profile y BlockSettings.
17. `Capa2 Build Questionnaire`, SL/TP/trailing, filtro indicador,
    `ExitAfterBars` bloqueado y fuente fija C2.
18. `Capa2 RETEST 0`.
19. `Capa2 RETEST 1`.
20. `Capa2 TICK REAL`.
21. `Capa2 MC`.
22. `Capa2 MC 2`.
23. `Capa2 Sequential`.
24. `Capa2 Monkey`.
25. `Capa2 Synthetic`.
26. `Capa2 SPP/WFM/FOWARD Review`.
27. `Capa2 Closeout And Methodology Sync`.

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

Closeout formal de Fase 6 `MC`:

- Se anade `mc-closeout-report` para consolidar, en dry-run, los cuatro guards
  de MC antes de abrir `MC 2`.
- El reporte local `phase6_mc_closeout_20260523_224903.json` queda `ok=true`.
- `mc-data-databanks-resources-options-target`, `mc-crosschecks-target`,
  `mc-passive-generation-target` y `mc-static-tabs-target` quedan
  idempotentes en base local y template repo: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- No habia procesos SQX vivos durante el cierre (`processes=0`).
- La sesion local queda en `currentPhase=phase6_mc_closeout` y
  `nextPhase=phase7_mc2_open`.

Siguiente bloque exacto: `MC 2 > CrossChecks`, empezando por revisar el stress
de spread adaptativo `baseSpread x2-x5` antes de tocar valores.

## Estado Fase 7 - MC 2

Fase abierta tras el closeout formal de `MC`. `MC 2` es el retest de Monte
Carlo historico/coste posterior a `MC`; no debe forzar resultados, relajar
filtros ni convertirse en optimizador.

Consulta academica registrada para `MC 2 > CrossChecks`:

- White, "A Reality Check for Data Snooping", Econometrica 2000:
  `https://doi.org/10.1111/1468-0262.00152`.
- Bailey, Borwein, Lopez de Prado y Zhu, "Pseudo-Mathematics and Financial
  Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample
  Performance": `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659`.
- Horvath, de Carvalho, Leitao y Sowa, "On the different impacts of fixed
  versus floating bid-ask spreads on an automated intraday stock trading":
  `https://doi.org/10.1016/j.najef.2020.101247`.

Conclusion aplicada:

- La literatura respalda tratar costes, bid-ask spread y fricciones como parte
  del realismo de backtest, y tambien advierte contra reusar validaciones para
  seleccionar/tunear hasta que salgan bien.
- La regla `baseSpread x2-x5` es una inferencia metodologica local y una
  heuristica acotada validada por smokes, no un teorema universal.
- El rango absoluto `30-50` quedaba desanclado del activo: en el seed generico
  `AUDCAD/H1` con spread `2.0` equivalia a `15x-25x`; en USDJPY/H4 ya se habia
  observado como extremo y bloqueo posterior.

Decision aplicada para `MC 2 > CrossChecks`:

- Se anade `mc2-crosschecks-target` con dry-run-first, backup/diff/apply y
  guard idempotente para base local y template repo.
- `MonteCarloRetest` queda como unico crosscheck activo de `MC 2`.
- Metodos activos dentro de `MonteCarloRetest`: `RandomizeHistoryData` y
  `RandomizeSpread`; los metodos activos ocultos dentro de crosschecks
  inactivos se apagan.
- `NumberOfSimulations=100` y `MCUseFullSample=true` se preservan.
- Se preservan los filtros de aceptacion existentes:
  `AnnualPctReturnDDRatio` MC2 `>= 0` y `AnnualPctReturnDDRatio` MC2 `>= 30%`
  del main.
- `RandomizeSpread` pasa de absoluto `30-50` a adaptativo
  `baseSpread x2-x5`; en el seed generico `spread=2.0` queda `4-10`.
- Project Generator incorpora `adaptiveSpreadStress` para recalcular el rango
  por activo/timeframe; smoke de contrato genera AUDCAD/H4 con spread `10` y
  `RandomizeSpread=20-50`.
- El dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `MC 2 > CrossChecks` (`133/133`).

Reporte local:
`.local/sqx142_task_config/phase_reports/phase7_mc2_crosschecks_20260523_230735.json`.

Bloque posterior ya cerrado: `MC 2 > Data / Databanks / Resources / Options`,
donde se cerro la cadena `Input=MC` / `Output=MC2`, periodo, precision y
placeholders generator-owned antes de pasar a generacion pasiva/estaticos.

Decision aplicada para `MC 2 > Data / Databanks / Resources / Options`:

- Se anade `mc2-data-databanks-resources-options-target` con dry-run-first,
  backup/diff/apply y guard idempotente para base local y template repo.
- `MC 2` no usa una seccion `Data` directa en este XML de SQX; `CustomData`
  queda como portador canonico del setup y se prohibe una fuente `Data`
  paralela.
- `CustomData` queda en `ROBUSTNESS_C1` (`2017.10.02-2023.12.31`),
  `testPrecision=2`, `No Session`, `slippage=0`, `minDist=0`,
  `engine=MetaTrader4`, `Commission=0.0` y `MainTestValues` completos.
- La cadena queda explicita: `Input=MC` y `Output=MC2`; no se anade split OOS
  interno ni se fuerza ningun estado `Results=passed`.
- `Resources` queda alineado al seed generico `AUDCAD/H1`, precision `TICK`,
  timezone `EETUS`, sin sesiones y sin tokens donor `USDJPY/H4`; Project
  Generator sigue siendo dueno del simbolo/timeframe/spread final.
- `Options` queda rapido/inert: `LimitTimeRange=false`,
  `RealisticGapsHandling=false`, `StoreChartData=false`, `Session=No Session`
  y `MarketOpenSession=No Session`.
- Project Generator queda alineado para no inyectar ventanas horarias en
  `MC` ni `MC 2`, mientras conserva `adaptiveSpreadStress` para recalcular el
  spread stress por activo/timeframe.
- El dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `MC 2 > Data` (`0/0` allow-empty),
  `MC 2 > Databanks` (`2/2`), `MC 2 > Resources` (`4/4`) y
  `MC 2 > Options` (`34/34`).

Reporte local:
`.local/sqx142_task_config/phase_reports/phase7_mc2_data_databanks_resources_options_20260523_233831.json`.

Decision aplicada para `phase7_mc2_static_or_next_block`:

- Se decide que `MC 2` si necesita cierre pasivo/estatico antes de `Sequential`:
  no como fase larga adicional, sino como candado final para demostrar que no
  quedan generacion, mejora, ranking/portfolio selection, seleccion manual ni
  mutaciones ocultas antes de entregar `MC2` a `Sequential`.
- Se anaden `mc2-passive-generation-target`, `mc2-static-tabs-target` y
  `mc2-closeout-report`, todos dry-run-first y con backup/diff/apply sobre base
  local y template repo.
- `MC 2 > PartsToImprove / WhatToBuild / Blocks` queda pasivo puro:
  `StrategyType.improveDatabank=MC`, `ShowLastGenerationDatabank=false`,
  `FreshBloodReplaceSimilar=false`, `FreshBloodReplaceWeakest=false`,
  `EvoRestartOnFinish=false`, `EvoRestartOnStagnation=false`, signals `0`,
  stop/limit blocks `0`, indicadores preservados desde el universo metodologico
  y solo `EnterAtMarket` + `ExitAfterBars` con probability `100`.
- Como el XML base de `MC 2` no traia `Blocks` explicitos, el guard copia los
  controles pasivos faltantes desde la tarea `MC` antes de forzar el contrato.
  Esto evita inventar universo nuevo y mantiene la cadena metodologica
  `MC -> MC2 -> Sequential`.
- `MC 2 > Rankings / ATMs / RiskMoneyManagement / Notes / SelectedStrategies /
  CustomData` queda inerte: `DeleteFailedStrategies=false`,
  `ForceRunCrossChecks=false`, `FitPortfolio=false`,
  `CustomAnalysis.filter=false`, ATMs desactivado, FixedSize activo,
  `SelectedStrategies` vacio y `CustomData` conservado como portador canonico
  `ROBUSTNESS_C1`.
- `mc2-closeout-report --target both --write` queda `ok=true`, `issues=0`,
  `processes=0`; los cuatro guards `mc2-data-databanks-resources-options-target`,
  `mc2-crosschecks-target`, `mc2-passive-generation-target` y
  `mc2-static-tabs-target` quedan verdes e idempotentes (`changed=false`,
  `changedActionCount=0`, `guardOk=true`) en base local y template repo.
- La justificacion academica se mantiene conservadora: MC/MC2 son gates de
  robustez sobre supervivientes, no optimizadores nuevos. Repetir ajustes hasta
  mejorar resultados aumentaria presion de data snooping/backtest overfitting;
  por eso se preservan failed naturales y no se anade seleccion adicional antes
  de Sequential. Referencias de criterio: White, "A Reality Check for Data
  Snooping"; Bailey, Borwein, Lopez de Prado y Zhu, "The Probability of
  Backtest Overfitting"; Bailey y Lopez de Prado, "The Deflated Sharpe Ratio".

Reporte local:
`.local/sqx142_task_config/phase_reports/phase7_mc2_closeout_20260524_064023.json`.

Estado Fase 8 - Sequential Open:

- `phase8_sequential_open` queda abierto con `sequential-open-report --target both --write`.
- `Sequential` queda mapeado a `AutomaticRetest-Task3.xml`; no se confunde con
  `Retest-Task3.xml` de `RETEST 0`.
- La cadena ya es correcta en base local y template repo: `Input=MC2` y
  `Output=Sequential`.
- `MC 2` queda verificado como gate previo cerrado: `mc2-closeout-report` sigue
  `ok=true`, sin issues y con `processes=0`.
- `Sequential` mantiene un unico crosscheck activo: `SequentialOptimization`;
  `ApplyToStrategy=false`, `PctToPass=80`, `ResultsCount=5` y
  `StabilityRange=25`.
- La compuerta no lanza SQX ni ejecuta retests reales; solo lee XML, verifica
  estado local y guarda reporte.
- Se conservan las reglas de rendimiento aprendidas: los smokes reales de
  Sequential deben ir por lotes/snapshot y no lanzar todos los supervivientes
  de golpe.
- Quedan dos decisiones tecnicas detectadas antes de mutar:
  `StrategyType.improveDatabank` sigue como placeholder `Strategies to improve`,
  y el XML conserva `Data` + `CustomData`; el siguiente bloque decidirá si se
  normaliza a `MC2` y cual sera el portador canonico.

Reporte local:
`.local/sqx142_task_config/phase_reports/phase8_sequential_open_20260524_065707.json`.

Siguiente bloque exacto: `phase8_sequential_data_databanks_resources_options`,
para cerrar Data/Databanks/Resources/Options de `Sequential` con diff antes de
tocar la base.

Decision aplicada para `phase8_sequential_data_databanks_resources_options`:

- Se anade `sequential-data-databanks-resources-options-target` con
  dry-run-first, backup/diff/apply sobre base local y template repo.
- `Sequential` mantiene portador dual `Data + CustomData` porque esta es la
  forma observada en SQX142 y los smokes reales de Sequential ya funcionaron con
  esa estructura; no se elimina ningun portador sin evidencia UI adicional.
- Ambos portadores quedan sincronizados en `ROBUSTNESS_C1`, `testPrecision=2`,
  `No Session`, `slippage=0`, `minDist=0`, seed generico `AUDCAD_darwinex/H1`
  y spread `2.0`.
- No se anade split OOS interno: Sequential consume supervivientes de `MC2` y
  escribe en `Sequential`.
- `Databanks` queda explicito: `Input=MC2` y `Output=Sequential`.
- `Resources` queda `TICK/EETUS`, sin sesiones y con brokers/instrumentos
  coherentes con el chart seed; Project Generator sigue reescribiendo simbolo,
  timeframe, spread, broker y recursos por activo/target profile.
- `Options` queda inerte para este robustness gate:
  `LimitTimeRange=false`, `RealisticGapsHandling=false`, `StoreChartData=false`,
  `Session=No Session` y `MarketOpenSession=No Session`.
- Project Generator queda alineado para no inyectar ventanas horarias en
  `AutomaticRetest-Task3.xml`; los customs generados mantienen simbolo/timeframe
  adaptados, pero Sequential ya no pasa a `LimitTimeRange=true` por accidente.
- El unico cambio XML real en base/template fue normalizar `Data/Chart spread`
  de `2` a `2.0` para igualarlo a `CustomData`; el dry-run posterior queda
  idempotente (`changed=false`, `changedActionCount=0`, `guardOk=true`).
- Ledger local respondido para `Sequential > Data` (`7/7`),
  `Sequential > Databanks` (`2/2`), `Sequential > Resources` (`1.899/1.899`)
  y `Sequential > Options` (`34/34`).

Reportes locales:
`.local/sqx142_task_config/diffs/phase8_sequential_data_databanks_resources_options_target_20260524_071203.json`.
`.local/sqx142_task_config/phase_reports/phase8_sequential_data_databanks_resources_options_20260524_071310.json`.

Siguiente bloque exacto: `phase8_sequential_crosschecks`, para cerrar
`SequentialOptimization` antes de pasar a generacion/pasividad/rankings.

Decision aplicada para `phase8_sequential_crosschecks`:

- Se anade `sequential-crosschecks-target` con dry-run-first, backup/diff/apply
  sobre base local y template repo.
- `Sequential` queda con `CrossChecks use=true/evaluateAll=true` y solo
  `SequentialOptimization` activo; no se activa MC, WhatIf, Higher Precision,
  WFM ni otros checks internos dentro de esta tarea.
- `SequentialOptimization` queda como gate de estabilidad, no como optimizador:
  `ApplyToStrategy=false`, `DistributionUp=130`, `DistributionDown=70`,
  `Steps=12`.
- `WhatToParametrize` queda acotado a `Periods=true`, `Constants=true` y
  `ExitParamsUsed=true`; `Recommended`, `Shifts`, `OtherParams`, `EntryParams`,
  `EntryLogic`, `ExitParamsUnused` y `BooleanParams` quedan en `false`.
- La aceptacion queda en `PctToPass=80`, `ResultsCount=5` y
  `StabilityRange=25`, con `Conditions` vacio para no convertir Sequential en
  otro filtro manual ni forzar resultados.
- Se apagan metodos que estaban activos dentro de crosschecks inactivos
  (`MonteCarloRetest`, `MonteCarloManipulation`, `WhatIf`) y se normaliza el
  setup anidado de crosscheck de spread `2` a `2.0`.
- La justificacion academica es conservadora: limitar la superficie de busqueda
  y mantener `ApplyToStrategy=false` reduce la presion de backtest overfitting;
  Sequential sigue evaluando estabilidad de supervivientes de MC2 y no reescribe
  estrategias.
- Dry-run posterior queda idempotente en local base y repo template:
  `changed=false`, `changedActionCount=0`, `guardOk=true`.
- Ledger local respondido para `Sequential > CrossChecks` (`321/321`).

Reportes locales:
`.local/sqx142_task_config/diffs/phase8_sequential_crosschecks_target_20260524_074656.json`.
`.local/sqx142_task_config/phase_reports/phase8_sequential_crosschecks_20260524_074726.json`.

Decision aplicada para `phase8_sequential_passive_generation`:

- `sequential-passive-generation-target` se aplica sobre base local y template
  repo con backup/diff dry-run-first; el apply queda `ok=true` y `guardOk=true`.
- `Sequential` queda como gate pasivo: consume `MC2`, escribe en `Sequential` y
  no mejora, genera ni reescribe estrategias.
- Se resuelve el placeholder de SQX: `StrategyType.improveDatabank` pasa de
  `Strategies to improve` a `MC2`.
- `PartsToImprove` queda pasivo (`improveATM=false`; EntryRules, OrderTypes y
  ExitRules con `use=false`).
- `BuildMode.generationType` se conserva como enum SQX conocido, pero los
  restos evolutivos se apagan: `ShowLastGenerationDatabank=false`,
  `FreshBloodReplaceSimilar=false`, `FreshBloodReplaceWeakest=false`,
  `EvoRestartOnFinish=false` y `EvoRestartOnStagnation=false`.
- `Blocks` conserva el universo indicador de la metodologia/BlockSettings:
  quedan `50` indicators activos, `0` signals activos y `0` stop/limit entry
  blocks activos.
- La entrada/salida queda acotada a `EnterAtMarket` y
  `ExitAfterBars.ExitAfterBars` con probability `100`; no hay salidas por dias.
- Ledger local respondido para `Sequential > PartsToImprove` (`8/8`),
  `Sequential > WhatToBuild` (`67/67`) y `Sequential > Blocks`
  (`17.583/17.583`).

Reportes locales:
`.local/sqx142_task_config/diffs/phase8_sequential_passive_generation_target_20260524_081914.json`.
`.local/sqx142_task_config/phase_reports/phase8_sequential_passive_generation_20260524_081943.json`.

Bloque posterior cerrado: `phase8_sequential_static_tabs`, para cerrar
Rankings / ATMs / RiskMoneyManagement / Notes / SelectedStrategies /
CustomData de `Sequential`.

Decision aplicada para `phase8_sequential_static_tabs`:

- Se anade `sequential-static-tabs-target` con dry-run-first, backup/diff/apply
  sobre base local y template repo.
- `Sequential` conserva `SequentialOptimization` activo; no se apaga el
  crosscheck real de estabilidad desde esta fase.
- `Rankings` queda inert: `type=never`, `DeleteFailedStrategies=false`,
  `ForceRunCrossChecks=false`, `FitPortfolio=false`,
  `CustomAnalysis.filter=false` y sin condiciones de ranking. El pass/fail
  natural lo gobierna `SequentialOptimization`, no la pestaña Ranking.
- `RiskMoneyManagement` conserva `FixedSize` como unico metodo activo para
  mantener evidencia comparable de Capa1.
- `ATMs` queda disabled, `Notes` preservado y `SelectedStrategies`
  empty/missing accepted porque Sequential consume el databank `MC2`.
- `CustomData` queda como partner dual sincronizado de `Data`: no se elimina
  `Data`, se conserva `subcharts=false`, `Commission=0.0`, `No Session`,
  `testPrecision=2` y no se arrastran tokens donor.
- El dry-run posterior queda idempotente en base local y repo template:
  `changed=false`, `changedActionCount=0`, `guardOk=true`.
- Ledger local respondido para `Sequential > Rankings` (`22/22`),
  `Sequential > ATMs` (`9/9`), `Sequential > RiskMoneyManagement` (`25/25`),
  `Sequential > Notes` (`1/1`), `Sequential > SelectedStrategies` (`0/0`)
  y `Sequential > CustomData` (`6/6`).

Reportes locales:
`.local/sqx142_task_config/diffs/phase8_sequential_static_tabs_target_20260524_084048.json`.
`.local/sqx142_task_config/phase_reports/phase8_sequential_static_tabs_20260524_084121.json`.

Closeout formal de Fase 8 `Sequential`:

- Se anade `sequential-closeout-report` para cerrar Fase 8 solo si MC2 previo
  y los cuatro guards Sequential estan verdes e idempotentes en dry-run.
- Verifica `sequential-data-databanks-resources-options-target`,
  `sequential-crosschecks-target`, `sequential-passive-generation-target` y
  `sequential-static-tabs-target` en base local y template repo.
- El reporte escrito queda `ok=true`, `issues=[]`, `warnings=[]`,
  `processes=[]`; todos los targets quedan `changed=false`,
  `changedActionCount=0`, `guardOk=true` y `AutomaticRetest-Task3.xml`.
- El estado de sesion local pasa a `currentPhase=phase8_sequential_closeout`
  y `nextPhase=phase9_monkey_test_open`.
- No se lanza SQX ni se ejecutan retests reales; el cierre solo lee XML/estado
  local y escribe evidencia ignorada por Git.

Reporte local:
`.local/sqx142_task_config/phase_reports/phase8_sequential_closeout_20260524_085653.json`.

Siguiente bloque exacto: `phase9_monkey_test_open`, para abrir `Monkey Test`
con la misma disciplina de cuestionario/dry-run antes de tocar valores.

Estado Fase 9 - Monkey Test Open:

- `phase9_monkey_test_open` queda abierto con
  `monkey-open-report --target both --write`.
- `Monkey Test` queda mapeado a `AutomaticRetest-Task6.xml`; no se confunde
  con `MC`, `MC 2`, `Sequential` ni `Synthetic`.
- La cadena base/template ya es correcta: `Input=Sequential` y
  `Output=Monkey Test`.
- `Sequential` queda verificado como gate previo cerrado:
  `sequential-closeout-report` sigue `ok=true`, sin issues y con
  `processes=0`.
- El unico crosscheck activo de Monkey es `MonteCarloRetest`, con metodo
  `RealMonkeyTest`, `NumberOfSimulations=200`, `MCUseFullSample=true` y
  `MaxChange=90`.
- Este open no lanza SQX, no ejecuta retests reales y no muta el CFX; solo lee
  XML/estado local, escribe reporte y prepara cuestionario completo.
- Quedan decisiones pendientes antes de aplicar valores: elegir portador
  `Data`/`CustomData`, mantener recursos gobernados por Project Generator,
  decidir si los filtros de aceptacion inactivos quedan advisory/off o se
  activan, y limpiar metodos activos dentro de crosschecks inactivos si seguimos
  la disciplina de Sequential.
- Se preserva la regla critica: Monkey debe conservar passed/failed naturales y
  nunca forzar `Results=passed`.
- Cuestionario completo generado para `Monkey Test`: `20,036` entradas
  detectadas y `12,332` diferencias donor/base.

Reporte local:
`.local/sqx142_task_config/phase_reports/phase9_monkey_test_open_20260524_091714.json`.

Siguiente bloque exacto: `phase9_monkey_test_data_databanks_resources_options`,
para cerrar Data/Databanks/Resources/Options de `Monkey Test` con diff antes de
tocar la base.

Decision aplicada para `phase9_monkey_test_data_databanks_resources_options`:

- Se anade `monkey-data-databanks-resources-options-target` con
  dry-run-first, backup/diff/apply sobre base local y template repo.
- `Monkey Test` mantiene portador dual `Data + CustomData` porque esta forma ya
  existe en SQX142 y es compatible con el proyecto base; no se elimina ningun
  portador sin evidencia UI adicional.
- Ambos portadores quedan sincronizados en `ROBUSTNESS_C1`, `testPrecision=2`,
  `No Session`, `slippage=0`, `minDist=0`, seed generico
  `AUDCAD_darwinex/H1` y spread `2.0`.
- No se anade split OOS interno: Monkey consume supervivientes de `Sequential`
  y escribe en `Monkey Test`.
- `Databanks` queda explicito: `Input=Sequential` y `Output=Monkey Test`.
- `Resources` queda `TICK/EETUS`, sin sesiones y con brokers/instrumentos
  coherentes con el chart seed; Project Generator sigue reescribiendo simbolo,
  timeframe, spread, broker y recursos por activo/target profile.
- `Options` queda inerte para este robustness gate:
  `LimitTimeRange=false`, `RealisticGapsHandling=false`, `StoreChartData=false`,
  `Session=No Session` y `MarketOpenSession=No Session`.
- Project Generator queda alineado para no inyectar ventanas horarias en
  `AutomaticRetest-Task6.xml`; los customs generados mantienen simbolo/timeframe
  adaptados, pero Monkey ya no pasa a `LimitTimeRange=true` por accidente.
- El unico cambio XML real en base/template fue normalizar `Data/Chart spread`
  de `2` a `2.0` para igualarlo a `CustomData`; el dry-run posterior queda
  idempotente (`changed=false`, `changedActionCount=0`, `guardOk=true`).
- Ledger local respondido para `Monkey Test > Data` (`7/7`),
  `Monkey Test > Databanks` (`2/2`), `Monkey Test > Resources` (`1.899/1.899`)
  y `Monkey Test > Options` (`34/34`).
- Se preserva la regla critica: passed/failed naturales, sin forzar
  `Results=passed`.

Reportes locales:
`.local/sqx142_task_config/diffs/phase9_monkey_test_data_databanks_resources_options_target_20260524_093418.json`.
`.local/sqx142_task_config/phase_reports/phase9_monkey_test_data_databanks_resources_options_20260524_093446.json`.

Siguiente bloque exacto: `phase9_monkey_test_crosschecks`, para decidir filtros
de aceptacion y limpiar metodos activos dentro de crosschecks inactivos sin
mezclar Monkey con Synthetic.

Decision aplicada para `phase9_monkey_test_crosschecks`:

- Se anade `monkey-crosschecks-target` con dry-run-first, backup/diff/apply
  sobre base local y template repo.
- `Monkey Test` queda como gate puro de `RealMonkeyTest`: `CrossChecks`
  activo/evaluateAll, solo `MonteCarloRetest` activo, solo metodo
  `RealMonkeyTest` activo, `NumberOfSimulations=200`, `MCUseFullSample=true`,
  `MCBacktestPrecision=-1` y `MaxChange=90`.
- Los filtros de aceptacion dejan de ser advisory/off y quedan activos:
  `NetProfit >= 50%` del main y `Max DD <= 200%` del main. Esto conserva
  passed/failed naturales sin forzar `Results=passed`.
- `SyntheticBootstrapV2` y `SyntheticBootstrapV3` quedan apagados dentro de
  Monkey para no mezclarlo con la fase posterior `Synthetic`/`Syntetic`.
- Los metodos activos ocultos de checks inactivos quedan limpiados:
  `MonteCarloManipulation` ya no conserva `RandomizeTradesOrder` ni
  `RandomlySkipTrades`; `WhatIf` ya no conserva exclusiones de trades activas.
- El setup anidado de crosscheck inactivo se normaliza al seed seguro
  `AUDCAD_darwinex/H1` spread `2.0`, `ROBUSTNESS_C1`, `testPrecision=2`,
  `No Session`, `slippage=0` y `minDist=0`; Project Generator sigue adaptando
  simbolo/timeframe/spread por activo.
- Dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `Monkey Test > CrossChecks` (`372/372`).

Reportes locales:
`.local/sqx142_task_config/diffs/phase9_monkey_test_crosschecks_target_20260524_101857.json`.
`.local/sqx142_task_config/phase_reports/phase9_monkey_test_crosschecks_20260524_101913.json`.

Siguiente bloque exacto: `phase9_monkey_test_passive_generation`, para cerrar
`PartsToImprove` / `WhatToBuild` / `Blocks` y demostrar que Monkey no genera,
no mejora y no altera logica de entrada/salida.

Decision aplicada para `phase9_monkey_test_passive_generation`:

- `monkey-passive-generation-target` se aplica sobre base local y template repo
  con backup/diff previo y `guardOk=true`.
- `Monkey Test` queda como retest pasivo puro de supervivientes `Sequential`:
  `StrategyType.improveDatabank=Sequential` sustituye el placeholder
  `Strategies to improve`.
- `PartsToImprove` queda apagado: `improveATM=false`, `EntryRules`,
  `OrderTypes` y `ExitRules` con mejoras long/short `use=false`.
- `BuildMode` conserva `generationType=random-generation` como enum SQX conocido,
  pero se neutraliza por contrato: `ShowLastGenerationDatabank=false`,
  `FreshBloodReplaceSimilar=false`, `FreshBloodReplaceWeakest=false`,
  `EvoRestartOnFinish.status=false` y
  `EvoRestartOnStagnation.status=false`.
- `Blocks` preserva Indicators de metodologia/BlockSettings, apaga todos los
  `signals` y `stopLimitBlocks`, conserva solo `EnterAtMarket=true` y fuerza
  `ExitAfterBars.ExitAfterBars` con `probability=100`.
- No quedan salidas por dias (`ExitAfterDays` / `ExitAfterTradingDays`) ni rutas
  locales; el resultado passed/failed sigue siendo natural de SQX.
- Dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `Monkey Test > PartsToImprove` (`8/8`),
  `Monkey Test > WhatToBuild` (`67/67`) y `Monkey Test > Blocks`
  (`17.583/17.583`).

Reportes locales:
`.local/sqx142_task_config/diffs/phase9_monkey_test_passive_generation_target_20260524_104138.json`.
`.local/sqx142_task_config/phase_reports/phase9_monkey_test_passive_generation_20260524_104201.json`.

Siguiente bloque exacto: `phase9_monkey_test_static_tabs`, para cerrar Rankings,
ATMs, RiskMoneyManagement, Notes, SelectedStrategies y CustomData de Monkey sin
activar ejecucion ni mutar logica de estrategia.

Decision aplicada para `phase9_monkey_test_static_tabs`:

- Se anade `monkey-static-tabs-target` con dry-run-first, backup/diff/apply y
  guard compuesto sobre Data, CrossChecks y generacion pasiva de Monkey.
- `AutomaticRetest-Task6.xml` conserva `MonteCarloRetest`/`RealMonkeyTest`
  como unico ejecutor de robustez; este bloque no lanza SQX ni cambia filtros
  de aceptacion Monkey.
- `Rankings` queda inerte: `type=never`, `MaxStrategies=10000`,
  `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false`,
  `FitPortfolio.active=false`, `CustomAnalysis.filter=false` y sin condiciones
  adicionales. El passed/failed lo decide `RealMonkeyTest`, no Ranking.
- `RiskMoneyManagement` queda comparable: `FixedSize=true` y el resto de
  metodos de sizing en `false`.
- `ATMs` queda `enable=false`; `Notes` se audita y preserva por hash.
- `SelectedStrategies` queda vacio o ausente, aceptado como vacio para retests
  automaticos de SQX.
- `CustomData` queda como portador dual sincronizado con `Data`:
  `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, seed generico
  `AUDCAD_darwinex/H1`, commission `0.0` y `MainTestValues` con
  `subcharts=false` y simbolo/timeframe/spread/dates/precision activos.
- Dry-run posterior queda idempotente: `changed=false`,
  `changedActionCount=0` y `guardOk=true`.
- Ledger local respondido para `Monkey Test > Rankings` (`23/23`),
  `Monkey Test > ATMs` (`9/9`), `Monkey Test > RiskMoneyManagement` (`25/25`),
  `Monkey Test > Notes` (`1/1`), `Monkey Test > SelectedStrategies` (`0/0`) y
  `Monkey Test > CustomData` (`6/6`).

Reportes locales:
`.local/sqx142_task_config/diffs/phase9_monkey_test_static_tabs_target_20260524_105703.json`.
`.local/sqx142_task_config/phase_reports/phase9_monkey_test_static_tabs_20260524_105942.json`.

Siguiente bloque exacto: `phase9_monkey_test_closeout`, para cerrar formalmente
Monkey Test con todos sus guards previos y dejar preparado el salto posterior a
Synthetic/Syntetic.

Closeout formal de Fase 9 `Monkey Test`:

- Se anade `monkey-closeout-report` para consolidar en dry-run los cuatro
  guards de Monkey y el gate previo `sequential-closeout-report`.
- `monkey-closeout-report --target both --write` queda `ok=true`, sin issues,
  sin warnings y sin procesos SQX vivos: `issues=[]`, `warnings=[]`,
  `processes=[]`.
- Las cuatro operaciones quedan idempotentes sobre base local y template repo:
  `monkey-data-databanks-resources-options-target`, `monkey-crosschecks-target`,
  `monkey-passive-generation-target` y `monkey-static-tabs-target` devuelven
  `changed=false`, `changedActionCount=0` y `guardOk=true`.
- Contrato cerrado: `AutomaticRetest-Task6.xml`, `Input=Sequential`,
  `Output=Monkey Test`, `ROBUSTNESS_C1`, `testPrecision=2`, `RealMonkeyTest`,
  `NumberOfSimulations=200`, `MCUseFullSample=true`, `MaxChange=90`, filtros
  `NetProfit >= 50%` y `Max DD <= 200%`, generacion pasiva, Rankings inerte,
  FixedSize, ATMs off y `CustomData` dual sincronizado.
- No se lanza SQX, no se ejecutan retests reales y no se fuerza
  `Results=passed`; se preservan passed/failed naturales para el smoke real
  futuro.
- El estado de sesion local pasa a `currentPhase=phase9_monkey_test_closeout`
  y `nextPhase=phase10_synthetic_open`.

Reportes locales:
`.local/sqx142_task_config/phase_reports/phase9_monkey_test_closeout_20260524_114205.json`.

Siguiente bloque exacto: `phase10_synthetic_open`, para abrir `Synthetic` /
`Syntetic` sin arrastrar filtros ni columnas especificas de Monkey.

Estado Fase 10 - Synthetic/Syntetic Open:

- `phase10_synthetic_open` queda abierto con
  `synthetic-open-report --target both --write`.
- `Synthetic` y `Syntetic` se tratan como alias historico; el task real del
  `.cfx` sigue siendo `Syntetic` y queda mapeado a
  `AutomaticRetest-Task5.xml`.
- La cadena actual queda verificada como `Input=Monkey Test` y
  `Output=Syntetic`; no se mezcla con `MC`, `MC 2`, `Sequential` ni las
  columnas especificas de Monkey.
- El unico crosscheck activo es `MonteCarloRetest`, con metodo
  `SyntheticBootstrapV3`, `NumberOfSimulations=100`, `MCUseFullSample=true`,
  `MCBacktestPrecision=-1`, `BlockSize=20`, `WarmupBars=200` y
  `PreservePct=85`.
- El open es read-only: no lanza SQX, no ejecuta retests reales, no muta CFX y
  no fuerza `Results=passed`.
- Warnings pendientes para los siguientes bloques: decidir portador
  `Data+CustomData`, limpiar metodos activos ocultos en `MonteCarloManipulation`
  y `WhatIf`, y normalizar `StrategyType.improveDatabank=Strategies to improve`
  hacia el input real `Monkey Test` si procede.
- Cuestionario completo generado para `Syntetic`: `20.008` entradas detectadas
  y `12.341` diferencias donor/base.

Reporte local:
`.local/sqx142_task_config/phase_reports/phase10_synthetic_open_20260524_115744.json`.

Siguiente bloque exacto: `phase10_synthetic_data_databanks_resources_options`,
para cerrar Data, Databanks, Resources y Options de `Synthetic`/`Syntetic` sin
copiar filtros ni columnas especificas de Monkey.

Estado Fase 10 - Synthetic/Syntetic Data/Databanks/Resources/Options:

- `phase10_synthetic_data_databanks_resources_options` queda cerrado con
  `phase10_synthetic_data_databanks_resources_options_20260524_121641.json`.
- `synthetic-data-databanks-resources-options-target --target both --apply`
  toca solo `AutomaticRetest-Task5.xml` y mantiene el alias real `Syntetic`;
  no ejecuta SQX, no fuerza `Results=passed` y no copia columnas ni filtros de
  Monkey.
- Se conserva el portador dual `Data+CustomData` por compatibilidad SQX142,
  sincronizado en `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, sin split
  OOS interno, `slippage=0`, `minDist=0`, comision `0.0` y
  `MainTestValues` alineado.
- `Databanks` queda explicito como `Input=Monkey Test` y `Output=Syntetic`.
- Recursos quedan como seed generico local-safe `AUDCAD_darwinex/H1` con spread
  `2.0`, precision `TICK`, timezone `EETUS`, sin sesiones; el Project
  Generator sigue siendo propietario del activo/timeframe/spread real al
  generar customs.
- `Options` queda inerte: `LimitTimeRange=false`,
  `RealisticGapsHandling=false`, `StoreChartData=false`, `Session=No Session`
  y `MarketOpenSession=No Session`.
- Project Generator ya no inyecta ventanas horarias en
  `AutomaticRetest-Task5.xml`; los customs generados mantienen
  simbolo/timeframe/spread adaptados por activo sin convertir Synthetic en
  filtro horario.
- El unico cambio CFX aplicado fue normalizar `Data/Setup/Chart spread` de `2`
  a `2.0` en base local y template repo, con backup en
  `.local/sqx142_task_config/backups/phase10_synthetic_data_databanks_resources_options_20260524_121557/`
  y diff
  `.local/sqx142_task_config/diffs/phase10_synthetic_data_databanks_resources_options_target_20260524_121559.json`.
- Dry-run posterior idempotente:
  `phase10_synthetic_data_databanks_resources_options_target_20260524_121612.json`
  con `changed=false`, `changedActionCount=0`, `guardOk=true` e `issues=[]`.
- Ledger local respondido para `Syntetic > Data` (`7/7`),
  `Syntetic > Databanks` (`2/2`), `Syntetic > Resources` (`1.899/1.899`) y
  `Syntetic > Options` (`34/34`).

Siguiente bloque exacto: `phase10_synthetic_crosschecks`, para decidir y
limpiar `SyntheticBootstrapV3`, filtros de aceptacion Synthetic y metodos
activos ocultos en crosschecks inactivos sin mezclarlo con Monkey.

Estado Fase 10 - Synthetic/Syntetic CrossChecks:

- `phase10_synthetic_crosschecks` queda cerrado con
  `phase10_synthetic_crosschecks_20260524_123911.json`.
- `synthetic-crosschecks-target --target both --apply` toca solo
  `AutomaticRetest-Task5.xml`, no ejecuta SQX, no fuerza `Results=passed` y
  no copia filtros de Monkey.
- `CrossChecks` queda activo/evaluateAll por el propio retest Synthetic:
  solo `MonteCarloRetest` queda en `use=true`.
- El unico metodo activo es `SyntheticBootstrapV3`; `RealMonkeyTest`,
  `SyntheticBootstrapV2`, `RandomizeSpread`, `RandomizeSlippage` y el resto de
  metodos del bloque `MonteCarloRetest` quedan apagados.
- Parametros Synthetic fijados: `NumberOfSimulations=100`,
  `MCUseFullSample=true`, `MCBacktestPrecision=-1`, `BlockSize=20`,
  `WarmupBars=200` y `PreservePct=85`.
- Se preserva el filtro de aceptacion propio de Synthetic: `NetProfit` del MC
  retest con `confidenceLevel=85` frente a main `NetProfit`; no se sustituyen por los filtros de Monkey (`NetProfit >= 50%` / `Max DD <= 200%`).
- Los metodos activos escondidos en crosschecks inactivos quedan apagados:
  `MonteCarloManipulation` ya no deja activos `RandomizeTradesOrder` ni
  `RandomlySkipTrades`, y `WhatIf` ya no deja activos
  `ExcludeTradesWithBiggestPl` ni `ExcludeTradesWithLowestPl`.
- Nested setups de CrossChecks quedan sincronizados con `ROBUSTNESS_C1`,
  `testPrecision=2`, `No Session`, `slippage=0`, `minDist=0` y seed
  `AUDCAD_darwinex/H1` spread `2.0`.
- Backup local:
  `.local/sqx142_task_config/backups/phase10_synthetic_crosschecks_20260524_123823/`.
- Diff/apply:
  `.local/sqx142_task_config/diffs/phase10_synthetic_crosschecks_target_20260524_123825.json`.
- Dry-run posterior idempotente:
  `phase10_synthetic_crosschecks_target_20260524_123846.json` con
  `changed=false`, `changedActionCount=0`, `guardOk=true` e `issues=[]`.
- Ledger local respondido para `Syntetic > CrossChecks` (`345/345`).

Siguiente bloque exacto: `phase10_synthetic_passive_generation`, para cerrar
`PartsToImprove`, `WhatToBuild` y `Blocks` de Synthetic/Syntetic como retest
pasivo puro desde `Monkey Test`.

Estado Fase 10 - Synthetic/Syntetic Passive Generation:

- `phase10_synthetic_passive_generation` queda cerrado con
  `phase10_synthetic_passive_generation_20260524_130638.json`.
- `synthetic-passive-generation-target --target both --apply` toca solo
  `AutomaticRetest-Task5.xml`, no ejecuta SQX, no fuerza `Results=passed` y
  no convierte Synthetic en generador.
- `Syntetic` queda como retest pasivo puro desde `Monkey Test`:
  `StrategyType.improveDatabank=Monkey Test`.
- `PartsToImprove` queda apagado para entradas, ordenes y salidas; no se
  mejora ni reemplaza logica de estrategia en este gate.
- Restos de evolucion/generacion quedan inertes:
  `ShowLastGenerationDatabank=false`, `FreshBloodReplaceSimilar=false`,
  `EvoRestartOnFinish.status=false` y
  `EvoRestartOnStagnation.status=false`.
- `Blocks` preserva Indicators gobernados por metodologia/BlockSettings, apaga
  todos los Signals y todos los Stop/Limit entry blocks.
- `OrderTypes` permite solo `EnterAtMarket`; `ExitTypes` permite solo
  `ExitAfterBars` con probability `100`.
- El guard bloquea salidas por dias (`ExitAfterDays` /
  `ExitAfterTradingDays`) y preserva resultados naturales.
- Backup local:
  `.local/sqx142_task_config/backups/phase10_synthetic_passive_generation_20260524_130601/`.
- Diff/apply:
  `.local/sqx142_task_config/diffs/phase10_synthetic_passive_generation_target_20260524_130603.json`.
- Dry-run posterior idempotente:
  `phase10_synthetic_passive_generation_target_20260524_130615.json` con
  `changed=false`, `changedActionCount=0`, `guardOk=true` e `issues=[]`.
- Ledger local respondido para `Syntetic > PartsToImprove` (`8/8`),
  `Syntetic > WhatToBuild` (`67/67`) y
  `Syntetic > Blocks` (`17.583/17.583`).

Siguiente bloque exacto: `phase10_synthetic_static_tabs`, para cerrar Rankings,
ATMs, RiskMoneyManagement, Notes, SelectedStrategies y CustomData sin activar
superficies de ejecucion adicionales.

Estado Fase 10 - Synthetic/Syntetic Static Tabs:

- `phase10_synthetic_static_tabs` queda cerrado con
  `phase10_synthetic_static_tabs_20260524_133337.json`.
- `synthetic-static-tabs-target --target both --apply` toca solo
  `AutomaticRetest-Task5.xml`, no ejecuta SQX, no fuerza `Results=passed` y no
  toca `SyntheticBootstrapV3`.
- `Rankings` queda inerte: `type=never`, `DeleteFailedStrategies=false`,
  `ForceRunCrossChecks=false`, sin condiciones extra, `FitPortfolio.active=false`
  y `CustomAnalysis.filter=false` con `method=none`.
- `RiskMoneyManagement` mantiene `FixedSize` activo y el resto de metodos
  desactivados para evitar ruido de sizing en Capa1.
- `ATMs` queda desactivado, `Notes` preservado y `SelectedStrategies` queda vacio/ausente aceptado porque la entrada real viene del databank `Monkey Test`.
- `CustomData` queda como portador dual sincronizado con `Data`:
  `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, `commission=0.0`,
  `MainTestValues` alineados y seed generico `AUDCAD_darwinex/H1` spread `2.0`.
- Backup local:
  `.local/sqx142_task_config/backups/phase10_synthetic_static_tabs_20260524_133242/`.
- Diff/apply:
  `.local/sqx142_task_config/diffs/phase10_synthetic_static_tabs_target_20260524_133244.json`.
- Dry-run posterior idempotente:
  `phase10_synthetic_static_tabs_target_20260524_133254.json` con
  `changed=false`, `changedActionCount=0`, `guardOk=true` e `issues=[]`.
- Ledger local respondido para `Syntetic > Rankings` (`22/22`),
  `Syntetic > ATMs` (`9/9`), `Syntetic > RiskMoneyManagement` (`25/25`),
  `Syntetic > Notes` (`1/1`), `Syntetic > SelectedStrategies`
  (`1/0` empty accepted) y `Syntetic > CustomData` (`6/6`).

Siguiente bloque exacto: `phase10_synthetic_closeout`, para cerrar formalmente
la Fase 10 solo si Data/Resources/Options, CrossChecks, Passive Generation y
Static Tabs siguen idempotentes en base local y template repo.

## Estado Fase 10 - Synthetic/Syntetic Closeout

- `phase10_synthetic_closeout` queda cerrado con
  `phase10_synthetic_closeout_20260524_135151.json`.
- `synthetic-closeout-report --target both --write` consolida el gate previo
  `monkey-closeout-report` y los cuatro guards Synthetic:
  `synthetic-data-databanks-resources-options-target`,
  `synthetic-crosschecks-target`, `synthetic-passive-generation-target` y
  `synthetic-static-tabs-target`.
- Todos los guards quedan en dry-run idempotente sobre base local y template
  repo con `ok=true`, `issues=[]`, `warnings=[]`, `processes=[]`,
  `changed=false`, `changedActionCount=0` y `guardOk=true`.
- Synthetic/Syntetic queda como gate de robustez natural en
  `AutomaticRetest-Task5.xml`: `Input=Monkey Test`, `Output=Syntetic`,
  `MonteCarloRetest` activo con `SyntheticBootstrapV3`,
  `NumberOfSimulations=100`, `MCUseFullSample=true`,
  `MCBacktestPrecision=-1`, `BlockSize=20`, `WarmupBars=200` y
  `PreservePct=85`.
- Se conserva el filtro dedicado `NetProfit` MC retest confidence `85` frente
  a main `NetProfit`; no se copian filtros Monkey, no se lanza SQX y no se
  fuerza `Results=passed`.
- Contrato pasivo final: `StrategyType.improveDatabank=Monkey Test`,
  `Signals=0`, `Stop/Limit entry blocks=0`, solo `EnterAtMarket` y
  `ExitAfterBars probability 100`, sin salidas por dias.
- Contrato estatico final: `Rankings` inerte, `DeleteFailedStrategies=false`,
  `ForceRunCrossChecks=false`, `FitPortfolio=false`,
  `CustomAnalysis.filter=false`, `FixedSize`, ATMs desactivado,
  `SelectedStrategies` vacio/ausente aceptado y `CustomData` dual sincronizado
  con `Data`.
- Evidencia local de cierre:
  `phase10_synthetic_data_databanks_resources_options_target_20260524_135137.json`,
  `phase10_synthetic_crosschecks_target_20260524_135138.json`,
  `phase10_synthetic_passive_generation_target_20260524_135139.json` y
  `phase10_synthetic_static_tabs_target_20260524_135140.json`.
- El estado local queda en `currentPhase=phase10_synthetic_closeout` y
  `nextPhase=phase11_spp_open`.

Siguiente bloque exacto: `phase11_spp_open`, para abrir la revision de
configuracion de SPP. SPP sigue omitido de pruebas/smoke/optimizacion por la
decision operativa previa salvo aprobacion nueva; aqui toca revisar
configuracion, coherencia y dependencias.

## Estado Fase 11 - SPP Open

- `phase11_spp_open` queda abierto con
  `phase11_spp_open_20260524_140703.json`.
- `spp-open-report --target both --write` confirma el task real `SPP` en
  `AutomaticRetest-Task7.xml`, con `Input=Syntetic` y `Output=SPP`.
- El unico crosscheck activo es `OptProfileSysParamPermutation` con
  `MaxTests=3000`, `DistributionUp=20`, `DistributionDown=20`, `Steps=25`,
  `ProfitOptPct=30`, `UniformDistrChanges=15` y 2 condiciones activas:
  `NetProfit` y `DrawdownPct`.
- El gate queda `ok=true`, `issues=[]` y `processes=[]`; no lanza SQX,
  no ejecuta SPP, no hace smoke y no inicia optimizacion.
- Politica de ejecucion: `configuration_review_only_no_smoke_no_optimization`.
- Warnings aceptados para el siguiente bloque:
  `SPP` usa `CustomData` como portador canonico, hay metodos activos ocultos
  en `MonteCarloManipulation` y `MonteCarloRetest` aunque esos crosschecks
  estan inactivos, y `WFM` depende de `SPP` pero sigue review-only/bloqueado
  salvo decision posterior.
- Cuestionario local completo:
  `_task_summary_20260524_140647.json`, 7 tabs, 180 entradas detectadas y
  9 diferencias donor/base.
- Breakdown del cuestionario: `CrossChecks` 94, `CustomData` 6, `Databanks` 2,
  `Options` 34, `Rankings` 16, `Resources` 4 y `RiskMoneyManagement` 24.
- El estado local queda en `currentPhase=phase11_spp_open` y
  `nextPhase=phase11_spp_data_databanks_resources_options`.

Siguiente bloque exacto: `phase11_spp_data_databanks_resources_options`, para
revisar `CustomData`, `Databanks`, `Resources` y `Options` sin copiar tokens
del donor y sin ejecutar SPP.

## Estado Fase 11 - SPP Data/Databanks/Resources/Options

- `phase11_spp_data_databanks_resources_options` queda cerrado con
  `phase11_spp_data_databanks_resources_options_20260524_144847.json`.
- `spp-data-databanks-resources-options-target` valida base local y template
  repo con `ok=true`, `changed=false`, `changedActionCount=0`, `guardOk=true`
  e `issues=[]`; el apply no necesitó reescribir CFX porque el portador ya
  estaba alineado.
- `SPP` queda en `AutomaticRetest-Task7.xml` como gate de revision de
  configuracion: no lanza SQX, no ejecuta SPP, no hace smoke y no inicia
  optimizacion.
- Portador canonico: `CustomData` only. No se crea `Data`, no hay OOS interno,
  y se conserva `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, engine
  `MetaTrader4`, comision `0.0`, `MainTestValues` completos y semilla generica
  `AUDCAD_darwinex/H1` con spread `2.0`.
- Cadena: `Input=Syntetic` y `Output=SPP`; no se fuerza `Results=passed` y se
  preserva la mezcla natural de passed/failed que decidan los filtros SPP.
- `Resources` queda `TICK/EETUS` sin sesiones y sin tokens donor `USDJPY/H4`;
  Project Generator sigue siendo dueno de simbolo, timeframe, spread, swap,
  comisiones y recursos finales por activo/timeframe.
- `Options` queda inerte: `LimitTimeRange=false`, `RealisticGapsHandling=false`,
  `StoreChartData=false`, `Session=No Session` y
  `MarketOpenSession=No Session`.
- Project Generator ya no inyecta ventanas horarias en
  `AutomaticRetest-Task7.xml`; los customs generados adaptan
  simbolo/timeframe/spread/recursos sin convertir SPP en filtro horario.
- Evidencia local: dry-run
  `phase11_spp_data_databanks_resources_options_target_20260524_144738.json`,
  apply `phase11_spp_data_databanks_resources_options_target_20260524_144758.json`
  e idempotent dry-run
  `phase11_spp_data_databanks_resources_options_target_20260524_144818.json`.
- Ledger local respondido: `SPP > CustomData` (`6/6`), `Databanks` (`2/2`),
  `Resources` (`4/4`) y `Options` (`34/34`).
- El estado local queda en
  `currentPhase=phase11_spp_data_databanks_resources_options` y
  `nextPhase=phase11_spp_crosschecks`.

Siguiente bloque exacto: `phase11_spp_crosschecks`, para revisar
`OptProfileSysParamPermutation`, filtros de aceptacion SPP y limpieza de metodos
activos ocultos en crosschecks inactivos sin ejecutar SPP.

### Estado Fase 11 - SPP CrossChecks

- `phase11_spp_crosschecks` queda cerrado con
  `phase11_spp_crosschecks_20260524_152918.json`.
- Nuevo target aplicado: `spp-crosschecks-target` sobre base local y template
  repo, con dry-run-first, backup/diff y dry-run posterior idempotente.
- `SPP` sigue como gate de revision de configuracion: no lanza SQX, no ejecuta
  SPP, no hace smoke, no inicia optimizacion y no fuerza `Results=passed`.
- `AutomaticRetest-Task7.xml` queda aislado con solo
  `OptProfileSysParamPermutation` activo.
- Parametros SPP preservados: `MaxTests=3000`, `DistributionUp=20`,
  `DistributionDown=20`, `Steps=25`, `WhatToParametrize type=1`,
  `symmetricVariables=false`, `Periods=true`, `Constants=true`,
  `EntryParams=true`, `ExitParamsUsed=true`, y el resto de familias no usadas
  en `false`.
- Filtros SPP dedicados: `NetProfit` de
  `OptProfileSysParamPermutation >= 50%` del main y `DrawdownPct` de
  `OptProfileSysParamPermutation <= 200%` del main. No se copian filtros Monkey
  ni Synthetic.
- Limpieza: los metodos ocultos que estaban activos dentro de
  `MonteCarloManipulation` y `MonteCarloRetest` quedan apagados aunque esos
  crosschecks ya estuvieran inactivos.
- El setup anidado de CrossChecks queda normalizado a `ROBUSTNESS_C1`,
  `testPrecision=2`, `No Session`, seed `AUDCAD_darwinex/H1` con spread `2.0`.
- `ForceRunCrossChecks=false` queda explicito para que SPP no pueda ejecutarse
  como arrastre interno desde ranking/static tabs.
- Evidencia local: dry-run
  `phase11_spp_crosschecks_target_20260524_152849.json`, apply
  `phase11_spp_crosschecks_target_20260524_152857.json`, backup
  `phase11_spp_crosschecks_20260524_152857/` e idempotent dry-run
  `phase11_spp_crosschecks_target_20260524_152905.json` con `ok=true`,
  `changed=false`, `changedActionCount=0`, `guardOk=true` e `issues=[]`.
- Ledger local respondido: `SPP > CrossChecks` (`94/94`).
- El estado local queda en `currentPhase=phase11_spp_crosschecks` y
  `nextPhase=phase11_spp_static_tabs`.

### Estado Fase 11 - SPP Static Tabs

`phase11_spp_static_tabs` queda cerrado con
`phase11_spp_static_tabs_20260524_155130.json`.

Decision aplicada para `phase11_spp_static_tabs`:

- `spp-static-tabs-target` queda disponible en dry-run/apply para base local y
  template repo.
- `SPP` sigue como gate de revision de configuracion: no lanza SQX, no ejecuta
  SPP, no hace smoke, no inicia optimizacion, no desbloquea WFM y no fuerza
  `Results=passed`.
- `AutomaticRetest-Task7.xml` mantiene `CustomData` como unico portador, sin
  `Data`, con `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, seed
  `AUDCAD_darwinex/H1` y spread `2.0`.
- Rankings queda inerte: `type=never`, `MaxStrategies=10000`,
  `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false`,
  `FitPortfolio.active=false`, `CustomAnalysis.filter=false`, `method=none` y
  sin condiciones extra. El resultado passed/failed lo decide
  `OptProfileSysParamPermutation`.
- `RiskMoneyManagement` conserva `FixedSize=true` y el resto de metodos en
  `false` para evitar ruido de sizing en Capa1.
- `ATMs` queda apagado, `Notes` preservado, y `SelectedStrategies`
  vacio/ausente aceptado.
- Evidencia local: dry-run
  `phase11_spp_static_tabs_target_20260524_154942.json`, apply
  `phase11_spp_static_tabs_target_20260524_155003.json`, backup
  `phase11_spp_static_tabs_20260524_155003/` e idempotent dry-run
  `phase11_spp_static_tabs_target_20260524_155015.json` con `ok=true`,
  `changed=false`, `changedActionCount=0`, `guardOk=true` e `issues=[]`.
- Ledger local respondido: `SPP > Rankings` (`21/21`), `ATMs` (`1/1`),
  `RiskMoneyManagement` (`24/24`), `Notes` (`1/0` empty accepted),
  `SelectedStrategies` (`1/0` empty accepted) y `CustomData` (`6/6`).
- El estado local queda en `currentPhase=phase11_spp_static_tabs` y
  `nextPhase=phase11_spp_closeout`.

### Estado Fase 11 - SPP Closeout

`phase11_spp_closeout` queda cerrado con
`phase11_spp_closeout_20260524_163545.json`.

Decision aplicada para `phase11_spp_closeout`:

- `spp-closeout-report` queda disponible en modo reporte/`--write` para base
  local y template repo.
- El cierre consolida `synthetic-closeout-report` previo y los tres guards SPP:
  `spp-data-databanks-resources-options-target`, `spp-crosschecks-target` y
  `spp-static-tabs-target`.
- Todos los guards quedan en dry-run idempotente sobre base local y template
  repo con `ok=true`, `issues=[]`, `warnings=[]`, `processes=[]`,
  `changed=false`, `changedActionCount=0` y `guardOk=true`.
- `SPP` queda como revision de configuracion, no como ejecucion real:
  `configuration_review_only_no_smoke_no_optimization`, sin ejecutar SPP,
  sin smoke, sin optimizacion, sin desbloquear WFM y sin forzar
  `Results=passed`.
- `AutomaticRetest-Task7.xml` queda trazado como `Input=Syntetic / Output=SPP`,
  `CustomData` unico, sin `Data`, `ROBUSTNESS_C1`, `testPrecision=2`,
  `No Session`, seed `AUDCAD_darwinex/H1` y spread `2.0`.
- `OptProfileSysParamPermutation` queda como unico crosscheck activo con
  `MaxTests=3000`, `DistributionUp=20`, `DistributionDown=20`, `Steps=25`,
  `WhatToParametrize` metodologico y filtros `NetProfit >= 50%` main y
  `DrawdownPct <= 200%` main.
- Las superficies estaticas quedan inertes: Rankings `type=never`,
  `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false`,
  `FitPortfolio.active=false`, `CustomAnalysis.filter=false`, `FixedSize`
  activo, ATMs apagado y `SelectedStrategies` vacio/ausente aceptado.
- Evidencia local de cierre:
  `phase11_spp_data_databanks_resources_options_target_20260524_163530.json`,
  `phase11_spp_crosschecks_target_20260524_163530.json`,
  `phase11_spp_static_tabs_target_20260524_163530.json` y reporte
  `phase11_spp_closeout_20260524_163545.json`.
- El estado local queda en `currentPhase=phase11_spp_closeout` y
  `nextPhase=phase12_wfm_open`.

Siguiente bloque exacto: `phase12_wfm_open`, para abrir `WFM` como revision de
configuracion review-only, recordando que WFM depende de SPP pero sigue
bloqueado para ejecucion mientras SPP no tenga aprobacion explicita.

## Estado Fase 12 - WFM Open

- `phase12_wfm_open` queda abierto con
  `phase12_wfm_open_20260524_165030.json`.
- `wfm-open-report --target both --write` confirma el task real `WFM` en
  `AutomaticRetest-Task4.xml`, con `Input=SPP` y `Output=WFM`.
- El unico crosscheck activo es `WalkForwardMatrix`; `CrossChecks` queda
  `use=true` y `evaluateAll=true`.
- Configuracion detectada de matriz: `WalkForward type=2`, `period=10`,
  `optimization=15`, `distributionUp=20`, `distributionDown=20`,
  `maxSteps=8`, `Param1 start=20 stop=36 step=2`, `Param2 start=5 stop=8
  step=1` y `MaxTests=3000`.
- `WhatToParametrize` queda detectado como `type=1`,
  `symmetricVariables=false`, `Periods=true`, `Constants=true`,
  `EntryParams=true`, `ExitParamsUsed=true` y el resto de familias no usadas
  en `false`.
- Filtros activos detectados: 6 condiciones activas en `WalkForwardMatrix`,
  incluyendo `NetProfit > 0`, `NetProfit > 60`, `WFPctOfProfitableRuns > 70`,
  `WFMaxProfitByRunInPct < 50`, `WFMinTradesInRun > 20` y
  `WFMaxPctDDbyRun <= 25`.
- El gate queda `ok=true`, `issues=[]` y `processes=[]`; no lanza SQX,
  no ejecuta WFM, no hace smoke y no inicia optimizacion.
- Politica de ejecucion:
  `configuration_review_only_no_smoke_no_optimization_blocked_by_spp`.
- Warnings aceptados para el siguiente bloque: WFM depende de SPP no ejecutado,
  `Data engine=MetaTrader5 (hedged)` difiere de `CustomData engine=MetaTrader4`,
  `Data spread=2` difiere de `CustomData spread=2.0`, y hay metodos activos
  ocultos en `MonteCarloRetest`, `MonteCarloManipulation` y `WhatIf` aunque esos
  checks estan inactivos.
- Cuestionario local completo:
  `_task_summary_20260524_165019.json`, 13 tabs, 20.011 entradas detectadas y
  12.323 diferencias donor/base.
- Breakdown del cuestionario: `ATMs` 9, `Blocks` 17.583, `CrossChecks` 330,
  `CustomData` 6, `Data` 7, `Databanks` 2, `Notes` 1, `Options` 34,
  `PartsToImprove` 8, `Rankings` 40, `Resources` 1.899,
  `RiskMoneyManagement` 25 y `WhatToBuild` 67.
- El estado local queda en `currentPhase=phase12_wfm_open` y
  `nextPhase=phase12_wfm_data_databanks_resources_options`.

Siguiente bloque exacto: `phase12_wfm_data_databanks_resources_options`, para
revisar `Data`, `CustomData`, `Databanks`, `Resources` y `Options` sin copiar
tokens del donor, sin lanzar WFM y manteniendo el bloqueo por dependencia de
SPP.

## Estado Fase 12 - WFM Data/Databanks/Resources/Options

- `phase12_wfm_data_databanks_resources_options` queda cerrado con
  `phase12_wfm_data_databanks_resources_options_20260524_171211.json`.
- `wfm-data-databanks-resources-options-target --target both --apply` normaliza
  `AutomaticRetest-Task4.xml` en base local y template repo con backup/diff y
  guardia verde.
- Portador: dual `Data+CustomData` sincronizado para compatibilidad SQX142. Se
  conserva `Data engine=MetaTrader5 (hedged)` y
  `CustomData engine=MetaTrader4`; no se exige igualdad de engine porque cada
  seccion cumple un rol distinto, pero si se exige igualdad en fechas,
  precision, sesion, slippage, minDist y `Chart`.
- Cadena: `Input=SPP` y `Output=WFM`. WFM sigue bloqueado para ejecucion porque
  SPP no se ha producido con una ejecucion real aprobada.
- Data objetivo: periodo `ROBUSTNESS_C1` (`2017.10.02` a `2023.12.31`),
  `testPrecision=2`, `No Session`, sin rangos OOS internos.
- Seed generico: `AUDCAD_darwinex/H1` con spread `2.0`. El unico cambio CFX
  aplicado fue normalizar `Data/Chart spread` de `2` a `2.0` para igualarlo con
  `CustomData`.
- Resources quedan `TICK/EETUS`, sin sesiones, con broker/resource coherente y
  sin copiar tokens del donor.
- Options quedan inertes: `Session=No Session`, `MarketOpenSession=No Session`,
  `LimitTimeRange=false`, `RealisticGapsHandling=false` y
  `StoreChartData=false`.
- Project Generator excluye `AutomaticRetest-Task4.xml` de inyeccion de ventanas
  horarias; los customs generados siguen adaptando simbolo/timeframe/spread y
  resources por activo/timeframe.
- Evidencia local: dry-run previo
  `phase12_wfm_data_databanks_resources_options_target_20260524_171133.json`,
  apply `phase12_wfm_data_databanks_resources_options_target_20260524_171147.json`
  e idempotencia posterior
  `phase12_wfm_data_databanks_resources_options_target_20260524_171200.json`
  con `changed=false`, `changedActionCount=0`, `guardOk=true` e `issues=[]`.
- No lanza SQX, no ejecuta WFM, no hace smoke, no inicia optimizacion,
  no desbloquea SPP y no fuerza `Results=passed`.
- El estado local queda en
  `currentPhase=phase12_wfm_data_databanks_resources_options` y
  `nextPhase=phase12_wfm_crosschecks`.

Siguiente bloque exacto: `phase12_wfm_crosschecks`, para revisar
`WalkForwardMatrix`, filtros WFM y limpiar metodos activos ocultos en
crosschecks inactivos sin ejecutar WFM.

## Estado Fase 12 - WFM CrossChecks

- `phase12_wfm_crosschecks` queda cerrado con
  `phase12_wfm_crosschecks_20260524_174355.json`.
- `wfm-crosschecks-target --target both --apply` normaliza
  `AutomaticRetest-Task4.xml` en base local y template repo con backup/diff,
  guardia verde e idempotencia posterior.
- Solo queda activo `WalkForwardMatrix`; `CrossChecks` permanece
  `use=true/evaluateAll=true`.
- Matriz objetivo: `WalkForward type=2`, `period=10`, `optimization=15`,
  `distributionUp=20`, `distributionDown=20`, `maxSteps=8`,
  `Param1 start=20 stop=36 step=2`, `Param2 start=5 stop=8 step=1` y
  `MaxTests=3000`.
- Filtros WFM dedicados: `NetProfit > 0`, `NetProfit > 60`,
  `WFPctOfProfitableRuns > 70`, `WFMaxProfitByRunInPct < 50`,
  `WFMinTradesInRun > 20` y `WFMaxPctDDbyRun <= 25`.
- La consulta academica interna respalda el enfoque general: WFM queda como
  revision conservadora de fragilidad, no como reoptimizador ni aceptacion
  automatica post-SPP. Los umbrales `>70` y `<=25` se documentan como
  politica metodologica conservadora, no como umbrales academicos universales.
- Se apagan metodos ocultos en checks inactivos, incluidos
  `MonteCarloRetest`, `MonteCarloManipulation` y `WhatIf`.
- Los setups anidados de checks inactivos quedan normalizados a
  `ROBUSTNESS_C1`, `testPrecision=2`, `No Session`, seed
  `AUDCAD_darwinex/H1` spread `2.0`.
- `Rankings/ForceRunCrossChecks=false` queda explicito para evitar ejecucion
  accidental desde Rankings.
- Evidencia local: dry-run previo
  `phase12_wfm_crosschecks_target_20260524_174318.json`, apply
  `phase12_wfm_crosschecks_target_20260524_174334.json` e idempotencia
  posterior `phase12_wfm_crosschecks_target_20260524_174344.json` con
  `changed=false`, `changedActionCount=0`, `guardOk=true` e `issues=[]`.
- No lanza SQX, no ejecuta WFM, no hace smoke, no inicia optimizacion, no
  desbloquea SPP/WFM y no fuerza `Results=passed`.
- El estado local queda en `currentPhase=phase12_wfm_crosschecks` y
  `nextPhase=phase12_wfm_static_tabs`.

Siguiente bloque exacto: `phase12_wfm_static_tabs`, para cerrar Rankings,
ATMs, RiskMoneyManagement, Notes, SelectedStrategies y CustomData de WFM sin
activar superficies extra ni convertir WFM en ejecucion live.

## Estado Fase 12 - WFM Static Tabs

- `phase12_wfm_static_tabs` queda cerrado mediante
  `wfm-static-tabs-target --target both --apply`.
- Evidencia local: dry-run previo
  `phase12_wfm_static_tabs_target_20260524_180624.json`, apply
  `phase12_wfm_static_tabs_target_20260524_180633.json`, dry-run posterior
  `phase12_wfm_static_tabs_target_20260524_180642.json` e idempotencia de
  cierre `phase12_wfm_static_tabs_target_20260524_180645.json`.
- El apply cambia solo las superficies estaticas necesarias y el dry-run
  posterior queda idempotente sobre base local y template repo con
  `changed=false`, `changedActionCount=0`, `guardOk=true` e `issues=[]`.
- Rankings queda inerte: `type=never`, `MaxStrategies=10000`,
  `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false`,
  `FitPortfolio.active=false`, `CustomAnalysis.filter=false/method=none` y
  sin condiciones extra. El passed/failed sigue gobernado por
  `WalkForwardMatrix`.
- `RiskMoneyManagement` queda en `FixedSize`, ATMs apagado, Notes preservado y
  `SelectedStrategies` vacio/ausente aceptado.
- `CustomData` queda sincronizado con el contrato dual de WFM: periodo
  `ROBUSTNESS_C1`, `2017.10.02` a `2023.12.31`, `testPrecision=2`,
  `No Session`, engine `MetaTrader4`, comision `0.0`, seed
  `AUDCAD_darwinex/H1` spread `2.0` y `MainTestValues` alineados.
- No lanza SQX, no ejecuta WFM, no hace smoke, no inicia optimizacion, no
  desbloquea SPP/WFM y no fuerza `Results=passed`.

## Estado Fase 12 - WFM Closeout

- `phase12_wfm_closeout` queda cerrado con
  `phase12_wfm_closeout_20260524_180702.json`.
- `wfm-closeout-report --target both --write` consolida `spp-closeout-report`
  previo y los tres guards WFM:
  `wfm-data-databanks-resources-options-target`, `wfm-crosschecks-target` y
  `wfm-static-tabs-target`.
- El reporte queda `ok=true`, `issues=[]`, `warnings=[]`, `processes=[]`; los
  tres guards WFM quedan verdes e idempotentes en dry-run sobre base local y
  template repo con `changed=false`, `changedActionCount=0` y `guardOk=true`.
- WFM queda cerrado como revision de configuracion, no como ejecucion real:
  `Input=SPP / Output=WFM`, `Data+CustomData` dual sincronizado,
  `ROBUSTNESS_C1`, resources `TICK/EETUS` sin sesiones, Options inertes,
  `WalkForwardMatrix` como unico crosscheck activo y filtros dedicados de WFM.
- El closeout conserva la politica conservadora de fragilidad de CrossChecks y
  la frontera SPP: `phase11_spp_closeout` esta verde como revision de
  configuracion, pero no implica que SPP se haya ejecutado en vivo.
- No lanza SQX, no ejecuta WFM, no hace smoke, no inicia optimizacion, no
  desbloquea SPP/WFM y no fuerza `Results=passed`.
- El estado local queda en `currentPhase=phase12_wfm_closeout` y
  `nextPhase=phase13_foward_open`.

Siguiente bloque exacto al cerrar WFM: `phase13_foward_open`.

## Estado Fase 13 - FOWARD Open

- `phase13_foward_open` queda abierto como revision de configuracion posterior
  a WFM, sin lanzar SQX, sin smoke y sin optimizacion.
- `FOWARD` queda mapeado al retest forward de Capa1 con cadena
  `Input=Syntetic / Output=Foward`.
- La apertura conserva la frontera review-only heredada de SPP/WFM: no implica
  ejecucion de SPP, WFM ni FOWARD, y no fuerza `Results=passed`.
- El siguiente bloque interno de Fase 13 es
  `phase13_foward_data_databanks_resources_options`.

## Estado Fase 13 - FOWARD Data/Databanks/Resources/Options

- `phase13_foward_data_databanks_resources_options` queda cerrado dentro del
  cierre verde de Fase 13.
- `foward-data-databanks-resources-options-target` valida la configuracion
  forward para base local y template repo sin convertirla en ejecucion SQX.
- Cadena canonica: `Input=Syntetic / Output=Foward`.
- Periodo objetivo: `FOWARD_C1`, con OOS
  `2025.01.01-2026.01.01` y `2026.01.01-2026.04.08`.
- Data objetivo: `testPrecision=2`, `No Session`, sin smoke y sin
  optimizacion.
- Resources quedan `TICK/EETUS`; Project Generator mantiene el control final
  de simbolo, timeframe, spread, swap y recursos por activo/timeframe.
- Options quedan especificas de forward: `RealisticGapsHandling=true` y
  `StoreChartData=false`.
- El siguiente bloque interno de Fase 13 es `phase13_foward_crosschecks`.

## Estado Fase 13 - FOWARD CrossChecks

- `phase13_foward_crosschecks` queda cerrado dentro del cierre verde de Fase 13.
- `foward-crosschecks-target` preserva FOWARD como retest directo de ventana
  forward, sin activar metodos de robustez anidados ni ejecuciones ocultas.
- `ForceRunCrossChecks=false` queda explicito para evitar arrastres desde
  Rankings o static tabs.
- No lanza SQX, no hace smoke, no inicia optimizacion y no fuerza
  `Results=passed`.
- El siguiente bloque interno de Fase 13 es `phase13_foward_static_tabs`.

## Estado Fase 13 - FOWARD Static Tabs

- `phase13_foward_static_tabs` queda cerrado dentro del cierre verde de Fase 13.
- `foward-static-tabs-target` deja los filtros forward en
  `NumberOfTrades>=30`, `RExpectancy>0` y `NetProfit>=0`.
- Superficies estaticas: `DeleteFailedStrategies=false`,
  `ForceRunCrossChecks=false`, `FitPortfolio=false` y `FixedSize`.
- La generacion queda pasiva pura: `StrategyType.improveDatabank=Syntetic`,
  sin Signals, sin Stop/Limit entry blocks y solo
  `EnterAtMarket + ExitAfterBars`.
- FOWARD queda review-only: no SQX run, no smoke, no optimizacion ni
  `Results=passed` forzado.
- El siguiente bloque interno de Fase 13 es `phase13_foward_closeout`.

## Estado Fase 13 - FOWARD Closeout

- `phase13_foward_closeout` queda cerrado con
  `phase13_foward_closeout_20260524_182647.json`.
- `foward-closeout-report --target both --write` consolida
  `foward-data-databanks-resources-options-target`,
  `foward-crosschecks-target` y `foward-static-tabs-target`.
- El cierre preserva la cadena `Input=Syntetic / Output=Foward`, periodo
  `FOWARD_C1`, OOS `2025.01.01-2026.01.01` y
  `2026.01.01-2026.04.08`, `testPrecision=2`, resources `TICK/EETUS`,
  Options `RealisticGapsHandling=true` y `StoreChartData=false`, filtros
  `NumberOfTrades>=30`, `RExpectancy>0`, `NetProfit>=0`, `FixedSize` y pasivo
  puro `EnterAtMarket + ExitAfterBars`.
- El closeout no lanza SQX, no hace smoke, no inicia optimizacion, no ejecuta
  FOWARD en vivo y no fuerza `Results=passed`.
- El estado local queda en `currentPhase=phase13_foward_closeout` y
  `nextPhase=phase14_capa1_closeout`.

## Estado Fase 14 - Capa1 Closeout

- `phase14_capa1_closeout` queda cerrado con
  `phase14_capa1_closeout_20260524_183012.json`.
- `capa1-closeout-report --target both --write` consolida el cierre de Capa1
  tras Build, RETEST 0, RETEST 1, TICK, MC, MC 2, Sequential, Monkey,
  Syntetic, SPP(review-only), WFM(review-only) y Foward.
- Cadena de Capa1 documentada:
  `Build -> RETEST 0 -> RETEST 1 -> TICK -> MC -> MC 2 -> Sequential -> Monkey -> Syntetic -> SPP(review-only) -> WFM(review-only) -> Foward`.
- El cierre de Capa1 no convierte SPP/WFM/FOWARD en ejecuciones SQX reales:
  no hay SQX run, smoke, optimizacion ni `Results=passed` forzado por la
  documentacion.
- El estado local queda en `currentPhase=phase14_capa1_closeout` y
  `nextPhase=phase15_capa2_planning`.

Siguiente bloque exacto: `phase15_capa2_planning`.

## Estado Fase 15 - Capa2 Planning

- `phase15_capa2_planning` queda cerrada como fase de planificacion
  read-only con `phase15_capa2_planning_20260524_190708.json`.
- `capa2-planning-report --target both --write` inspecciona base local
  `Capa2_Base_SQX142_Base`, template repo `Capa2_Base.cfx`, generator profile
  y BlockSettings Capa2 sin mutar CFX ni arrancar SQX.
- Objetivo Capa2: preservar la ventaja de mercado encontrada en Capa1 mientras
  se anade gestion de riesgo operativa (`SL`, `TP`, `Trailing`) y un filtro de
  indicador controlado, evitando que Capa2 se convierta en un optimizador
  abierto de performance.
- Contrato Build Capa2: fuente fija C2 generada desde el ganador Capa1,
  `EnterAtMarket` salvo decision explicita, `ExitAfterBars` fuera de Build,
  salidas por dias prohibidas y filtro indicador acotado por metodologia /
  BlockSettings.
- Correccion de contrato: `BS_Filtros_v6` y `BS_Filtros_v6_D1` no forman parte
  activa de esta capa; se conservan como referencia/trazabilidad. Si algun dia
  se promocionan, antes deben sanearse para no reintroducir
  `ExitAfterBars=true`.
- Correccion de contrato: el `templateFile` con ruta local en la base Build es
  el artefacto esperado de Template Maker C2, construido desde las estrategias
  que pasaron Forward Capa1 para analisis de cluster, clasificacion y montaje
  del template C2. Es operator-owned/local, no un valor publico que deba
  congelarse en generacion.
- Hallazgos adicionales: varios retests de Capa2 arrastran `ExitAfterBars`;
  `tradingTimeRanges.capa2` esta vacio; `adaptiveSpreadStress` no tiene layer 2;
  y `taskPeriodMaps` layer 2 no cubre todos los retests Capa2.
- Guard academico: Capa2 se trata como segunda capa de seleccion con coste de
  multiple testing. White Reality Check, PBO/DSR y Carr/Lopez de Prado se usan
  como anclas para evitar data snooping; Kaminski/Lo y Lo/Remorov obligan a no
  asumir que stops/trailing siempre mejoran tras costes.
- Reglas de validacion: resultados passed/failed naturales, retests como gates
  de validacion y no como feedback infinito, comparacion padre Capa1 vs hijo
  Capa2, y ningun ajuste de OOS/forward para "hacer pasar" una estrategia.
- Subagentes usados: `SQX Test Guardian` para baseline read-only,
  `SQX Local Capa2 Inspector` para inspeccion CFX/generator/BlockSettings y
  `SQX Academic Lopez` para riesgo academico de SL/TP/trailing y filtros.
- El estado local queda en `currentPhase=phase15_capa2_planning`,
  `nextPhase=phase16_capa2_preflight_snapshot`, `scope=capa2`.

## Estado Fase 16 - Capa2 Preflight Snapshot

- `phase16_capa2_preflight_snapshot` queda cerrada con
  `phase16_capa2_preflight_snapshot_20260524_195729.json`.
- `capa2-preflight-snapshot --target both --write` crea snapshot local ignorado
  por Git en
  `.local/sqx142_task_config/snapshots/phase16_capa2_preflight_20260524_195729/`.
- Snapshot incluido: base local
  `Capa2_Base_SQX142_Base/project.cfx`, template repo `Capa2_Base.cfx`,
  `generator_profiles.json`, `blocksettings_manifest.json` y los recursos
  reference-only `BS_Filtros_v6.sqb` / `BS_Filtros_v6_D1.sqb`.
- No se muta ningun CFX, generator, BlockSettings, binario, licencia ni runtime
  SQX. `processProbe` queda sin procesos SQX vivos.
- Rollback: restauracion selectiva desde snapshot local solo tras diff y
  confirmacion de la fase; nunca restaurar engine binaries, licencias, plugins
  core ni internals no relacionados.
- Phase16 deja como decisiones activas: `BS_Filtros_v6*` reference-only y
  `templateFile` local como artefacto Template Maker C2 operator-owned desde
  supervivientes Forward Capa1.
- El estado local queda en `currentPhase=phase16_capa2_preflight_snapshot`,
  `nextPhase=phase17_capa2_build_questionnaire`, `scope=capa2`.

Siguiente bloque exacto: `phase17_capa2_build_questionnaire`.

## Estado Fase 17 - Capa2 Build Questionnaire

- `phase17_capa2_build_questionnaire` queda generada con
  `phase17_capa2_build_questionnaire_20260524_201405.json`.
- `capa2-build-questionnaire --write` escribe cuestionarios completos
  local-only en
  `.local/sqx142_task_config/questionnaires/capa2/Build_strategies/`.
- Cobertura completa detectada: 13 pestanas Build, 16.647 entradas y 6
  diferencias base/template.
- Conteo por pestana: `WhatToBuild` 67/1, `Data` 8/1, `Resources` 4/3,
  `Blocks` 15.995/0, `RiskMoneyManagement` 25/0, `ATMs` 9/0, `Options` 34/0,
  `Databanks` 2/0, `Rankings` 173/0, `CrossChecks` 303/1,
  `PartsToImprove` 9/0, `Optimization` 17/0 y `Notes` 1/0
  (`preguntas/diferencias`).
- Phase17 no aplica CFX ni cambia base/template. Solo abre decisiones para:
  Template Maker C2 `templateFile`, fuente `StrategyType=template`,
  `EnterAtMarket`, retirada de `ExitAfterBars` en Build, `SL`/`TP`/`Trailing`,
  risk money management, filtro indicador unico, placeholders Project Generator
  layer 2, rankings/filtros y politica de crosschecks.
- Guardias activos: `BS_Filtros_v6*` sigue reference-only/trazabilidad, rutas
  locales Template Maker C2 siguen operator-owned, no SQX run, no smoke, no
  optimizacion y no `Results=passed` forzado.
- El estado local queda en `currentPhase=phase17_capa2_build_questionnaire`,
  `nextPhase=phase17_capa2_build_what_to_build`, `scope=capa2`.

Siguiente bloque exacto: `phase17_capa2_build_what_to_build`.

## Estado Fase 17 - Capa2 Build WhatToBuild

- `phase17_capa2_build_what_to_build` queda cerrada con
  `phase17_capa2_build_what_to_build_target_20260524_204601.json`.
- `capa2-build-what-to-build-target --target both --apply` revisa local base y
  template repo, registra 67/67 respuestas en
  `.local/sqx142_task_config/answers/capa2/Build_strategies/WhatToBuild.json`
  y no detecta issues ni warnings.
- El apply real queda `ok=true`, `localChanged=false`, `repoChanged=false`,
  `changedActionCount=0` y `processes=[]`; no hubo cambios CFX semanticos
  porque ambos targets ya estaban alineados.
- Decisiones cerradas: `StrategyType=template`, `templateFile` local
  operator-owned como fuente Template Maker C2 desde supervivientes Capa1
  Forward, repo `templateFile` vacio, `MarketSides` generator-owned
  long/short/both, SL/PT bounded, BuildMode bounded, condicion inicial
  `ProfitFactor > 1`, `EnterAtMarket` validado y contexto Blocks con
  `ExitAfterBars=false` y salidas por dias prohibidas.
- Contrato app web: Template Maker C2 conserva trazabilidad/provenance del
  template local, mientras Project Generator/xml_patcher limpian rutas privadas
  y adaptan direccion, activo, timeframe, costes, recursos y ventanas segun el
  usuario.
- Guard academico: Capa2 no se convierte en un segundo optimizador libre; la
  gestion SL/TP/trailing y el filtro indicador se revisan en bloques
  posteriores sin fabricar edge nuevo ni contaminar los retests.
- Guardias activos: no SQX run, no smoke, no optimizacion, no public path
  freezing, no copia de `BS_Filtros_v6*` como fuente activa y no
  `Results=passed` forzado.
- El estado local queda en `currentPhase=phase17_capa2_build_what_to_build`,
  `nextPhase=phase17_capa2_build_blocks`, `scope=capa2`.

Siguiente bloque exacto: `phase17_capa2_build_blocks`.

## Estado Fase 17 - Capa2 Build Blocks

- `phase17_capa2_build_blocks` queda cerrada con
  `phase17_capa2_build_blocks_target_20260524_211347.json`.
- `capa2-build-blocks-target --target both --apply` revisa local base y
  template repo, registra 15.995/15.995 respuestas en
  `.local/sqx142_task_config/answers/capa2/Build_strategies/Blocks.json` y no
  detecta issues ni warnings.
- El apply real queda `ok=true`, `localChanged=false`, `repoChanged=false`,
  `changedActionCount=0` y `processes=[]`; no hubo cambios CFX semanticos
  porque ambos targets ya estaban alineados.
- Decisiones cerradas: `EnterAtMarket` only, `EnterReverseAtMarket=false`,
  `EnterAtStop=false`, `EnterAtLimit=false`, `ExitAfterBars=false`,
  `StopLoss` y `ProfitTarget` activos al 100%, `TrailingStop` activo al 50%,
  `TrailingActivation=false`, `MoveSL2BE=false`, `_ExitRule_=false` y salidas
  por dias prohibidas.
- Universo de filtro Capa2: `AlwaysTrue` queda como semilla neutral de senal,
  `Signals` libres siguen apagadas, `Stop/Limit entry blocks` siguen apagados,
  y la familia activa de indicadores/operadores/precios permite una condicion
  de filtro Capa2 porque `WhatToBuild` limita la complejidad a una condicion.
- Guard academico: SL/PT/trailing se tratan como gestion de riesgo acotada y
  verificable, no como permiso para fabricar edge nuevo; `ExitAfterBars` queda
  fuera de Build para no arrastrar la salida por barras de Capa1.
- Guardias activos: no donor copy, no `BS_Filtros_v6*` activo, no SQX run, no
  smoke, no optimizacion, no public path freezing y no `Results=passed` forzado.
- El estado local queda en `currentPhase=phase17_capa2_build_blocks`,
  `nextPhase=phase17_capa2_build_data_databanks_resources_options`,
  `scope=capa2`.

Siguiente bloque exacto: `phase17_capa2_build_data_databanks_resources_options`.

## Estado Fase 17 - Capa2 Build Data/Databanks/Resources/Options

- `phase17_capa2_build_data_databanks_resources_options` queda cerrada con
  `phase17_capa2_build_data_databanks_resources_options_target_20260524_213626.json`.
- `capa2-build-data-databanks-resources-options-target --target both --apply`
  revisa local base y template repo con backup/diff, registra 48/48 respuestas
  en `.local/sqx142_task_config/answers/capa2/Build_strategies/{Data,Databanks,Resources,Options}.json`
  y no detecta issues ni warnings.
- Data queda como minado puro Capa2: periodo `BUILD 2017.10.02-2023.12.31`,
  `testPrecision=2 simulated`, `No Session`, un unico seed generico
  `AUDCAD_darwinex/H1` con spread `2.0` y sin rangos OOS internos. OOS sigue
  reservado a los retests.
- Databanks queda `Input=Results` y `Output=null`; la salida a `Results` la
  gobierna Ranking, no una copia directa de databank.
- Resources queda como seed generico compatible SQX142: `AUDCAD_darwinex`,
  broker Darwinex id `4`, precision `TICK`, timezone `EETUS`, sin sesiones,
  con `InstrumentInfo` coherente en local base y template repo. Project
  Generator sigue siendo el dueno final de activo, timeframe, spread, costes,
  swap y recursos por seleccion del usuario.
- Options queda `No Session`, `MarketOpenSession=No Session`,
  `LimitTimeRange=true`, ventana seed H1 `02:00-22:00`,
  `RealisticGapsHandling=true`, `StoreChartData=false` y sin salidas EOD,
  Friday ni end-of-range.
- `generator_profiles.json` ya define `tradingTimeRanges.capa2` para
  M5/M15/M30/H1 (`02:00-22:00`) y H4 (`04:00-20:00`), y
  `disableTradingTimeRanges.2` bloquea la inyeccion de ventanas en retests
  pesados de robustez para no contaminar MC/Sequential/Monkey/Synthetic/SPP/WFM.
- Dry-run posterior idempotente:
  `phase17_capa2_build_data_databanks_resources_options_target_20260524_213857.json`
  con `changed=false`, `changedActionCount=0`, `guardOk=true`,
  `issues=[]`, `warnings=[]` y `processes=[]`.
- Guard academico: Data/Options del Build Capa2 no se usan para optimizar OOS;
  mantienen realismo de gaps y ventana operativa generator-owned mientras los
  filtros y validacion viven en Rankings/retests posteriores.
- Guardias activos: no donor copy, no tokens `USDJPY`, no rutas locales en
  Data/Databanks/Resources/Options, no SQX run, no smoke, no optimizacion, no
  public path freezing y no `Results=passed` forzado.
- El estado local queda en
  `currentPhase=phase17_capa2_build_data_databanks_resources_options`,
  `nextPhase=phase17_capa2_build_rankings`, `scope=capa2`.

Siguiente bloque exacto: `phase17_capa2_build_rankings`.

## Estado Fase 17 - Capa2 Build Rankings

- `phase17_capa2_build_rankings` queda cerrada con
  `phase17_capa2_build_rankings_target_20260524_220916.json`.
- Comando aplicado: `capa2-build-rankings-target --target both --apply`, con
  dry-run posterior idempotente (`changed=false`, `changedActionCount=0`,
  `guardOk=true`, `issues=[]`) sobre base local y template repo.
- Ledger local: `Rankings` queda contestado con 173/173 entradas en
  `.local/sqx142_task_config/answers/capa2/Build_strategies/Rankings.json`.
- Identidad de tarea: el Build de Capa2 se resuelve por `Build-Task1.xml`,
  no por el texto visible `Build strategies`, porque el task title lo puede
  generar la app web segun activo, plan mining o descarga elegida por el
  usuario.
- Contrato Rankings Capa2:
  - `MaxStrategies=2000`.
  - `StopCondition.type=databank-full`, `passedStrategies=500`.
  - `DeleteFailedStrategies=false`, `ForceRunCrossChecks=false`.
  - `FitPortfolio.active=false`, `CustomAnalysis.filter=false`.
  - Objetivo activo unico: `RExpectancy`.
  - Filtros activos: `NumberOfTrades >= 120`,
    `ProfitFactor >= 1.1`, `Expectancy >= 0.05`.
- Guard academico: Rankings es filtro de cantera, no validador ni segundo
  optimizador. No usa OOS/Forward, no fuerza crosschecks internos, no borra
  fallidos, no activa portfolio fitting y no fabrica `Results=passed`.
- No hubo lanzamiento SQX, smoke, optimizacion ni ejecucion real.
- El estado local queda en `currentPhase=phase17_capa2_build_rankings`,
  `nextPhase=phase17_capa2_build_crosschecks`, `scope=capa2`.

Siguiente bloque exacto: `phase17_capa2_build_crosschecks`.

## Estado Fase 17 - Capa2 Build CrossChecks

- `phase17_capa2_build_crosschecks` queda cerrada con
  `phase17_capa2_build_crosschecks_target_20260524_223128.json`.
- Comando aplicado: `capa2-build-crosschecks-target --target both --apply`,
  con backup automatico y dry-run posterior idempotente
  (`phase17_capa2_build_crosschecks_target_20260524_223211.json`,
  `changed=false`, `changedActionCount=0`, `guardOk=true`, `issues=[]`) sobre
  base local y template repo.
- Ledger local: `CrossChecks` queda contestado con 303/303 entradas en
  `.local/sqx142_task_config/answers/capa2/Build_strategies/CrossChecks.json`.
- Identidad de tarea: el Build de Capa2 se resuelve por `Build-Task1.xml`,
  no por el texto visible generado por la app web.
- Contrato CrossChecks Capa2:
  - `CrossChecks use=false`, `evaluateAll=false`.
  - Cero checks activos: `SequentialOptimization`, `MonteCarloRetest`,
    `MonteCarloManipulation`, `WalkForwardOptimization`, `WalkForwardMatrix`,
    `RetestWithHigherPrecision`, `RetestOnAdditionalMarkets`,
    `OptProfileSysParamPermutation` y `WhatIf` quedan inactivos.
  - Metodos activos ocultos y condiciones de aceptacion dentro de checks
    inactivos quedan apagados.
  - Setups internos normalizados al seed Capa2 Build:
    `2017.10.02-2023.12.31`, `testPrecision=2`, `No Session`,
    `AUDCAD_darwinex/H1`, spread `2.0`.
  - `ForceRunCrossChecks=false` sigue protegido desde Rankings.
- Guard academico: Build Capa2 mina variantes acotadas de gestion de riesgo y
  filtro indicador; la robustez/validacion pertenece a los retests dedicados
  para no mezclar seleccion, optimizacion y validacion dentro del mismo Build.
- No hubo lanzamiento SQX, smoke, optimizacion ni ejecucion real; no se fuerza
  `Results=passed`.
- El estado local queda en `currentPhase=phase17_capa2_build_crosschecks`,
  `nextPhase=phase17_capa2_build_static_tabs`, `scope=capa2`.

Siguiente bloque exacto: `phase17_capa2_build_static_tabs`.

## Estado Fase 17 - Capa2 Build Static Tabs

- `phase17_capa2_build_static_tabs` queda cerrada con
  `phase17_capa2_build_static_tabs_target_20260524_231540.json`.
- Comando aplicado: `capa2-build-static-tabs-target --target both --apply`,
  con dry-run previo y sin procesos SQX vivos.
- Ledger local: `RiskMoneyManagement`, `ATMs`, `PartsToImprove`,
  `Optimization` y `Notes` quedan contestados con 61/61 entradas en
  `.local/sqx142_task_config/answers/capa2/Build_strategies/`.
- Contrato Static Tabs Capa2:
  - `FixedAmount=true` queda como sizing seed de Build Capa2.
  - `ATMs enable=false`.
  - `PartsToImprove` mantiene entradas y tipos de orden apagados; solo las
    salidas siguen activas para la capa SL/TP/trailing.
  - `Optimization` conserva superficie acotada, sin lanzar SQX ni optimizador.
  - `Notes` queda preservado.
- Ambos targets estaban ya alineados: `changed=false`,
  `changedActionCount=0`, `guardOk=true`, `issues=[]`, `warnings=[]` y
  `processes=[]`.
- Guard academico: Static Tabs no abre una nueva busqueda de edge; mantiene
  Capa2 limitada a gestion de riesgo/salida y deja la validacion a los retests.
- No hubo lanzamiento SQX, smoke, optimizacion ni ejecucion real; no se fuerza
  `Results=passed`.
- El estado local queda en `currentPhase=phase17_capa2_build_static_tabs`,
  `nextPhase=phase18_capa2_retest0`, `scope=capa2`.

Siguiente bloque exacto: `phase18_capa2_retest0`.

## Estado Fase 18 - Capa2 Retest 0

- `phase18_capa2_retest0` queda cerrada con
  `phase18_capa2_retest0_target_20260524_234752.json`.
- Comando aplicado: `capa2-retest0-target --target both --apply`, con
  dry-run previo, backup/diff local, dry-run posterior idempotente y sin
  procesos SQX vivos.
- Contrato tecnico: `Retest-Task1.xml`, `Input=Results`,
  `Output=RETEST 0`, `testPrecision=2`, `No Session`, seed generico
  `AUDCAD_darwinex/H1/TICK/EETUS`.
- Contrato temporal anti-overfit: Retest 0 usa periodo
  `2017.10.02-2025.01.01` con OOS1 `2024.01.01-2025.01.01`;
  FOWARD queda reservado desde `2025.01.01` hasta `2026.04.30` en
  `generator_profiles.json`.
- Contrato de validacion: `StrategyType` pasivo desde Results,
  `PartsToImprove` apagado, `CrossChecks use=false/evaluateAll=false`,
  `FitPortfolio=false`, `CustomAnalysis=false` y `ExitAfterBars=false` para
  no reintroducir la salida por barras eliminada en Capa2 Build.
- Filtros OOS predeclarados y amplios: `NumberOfTrades >= 80`,
  `ProfitFactor >= 1.05` y `ReturnDDRatio >= 1`, todos en muestra OOS.
- Ambos targets quedan idempotentes tras apply: `changedActionCount=0`,
  `guardOk=true`, `issues=[]`, `warnings=[]`, `processes=[]`.
- Guard academico: Retest 0 mide supervivencia OOS de candidatos Capa2 ya
  generados; no ajusta parametros, rankings, filtros ni estados de resultado.
- No hubo lanzamiento SQX, smoke, optimizacion ni ejecucion real; no se fuerza
  `Results=passed`.
- El estado local queda en `currentPhase=phase18_capa2_retest0`,
  `nextPhase=phase19_capa2_retest1`, `scope=capa2`.

Siguiente bloque exacto: `phase19_capa2_retest1`.

## Estado Fase 19 - Capa2 Retest 1

- `phase19_capa2_retest1` queda cerrada con
  `phase19_capa2_retest1_target_20260525_003750.json`.
- Comando aplicado: `capa2-retest1-target --target both --apply`, con
  dry-run previo, backup/diff local, dry-run posterior idempotente y
  `processes=[]`.
- Contrato tecnico: `AutomaticRetest-Task7.xml`, `Input=RETEST 0`,
  `Output=retest 1`, `testPrecision=2`, `No Session`, portador canonico
  `CustomData` sin `Data` directo.
- Contrato temporal anti-overfit: Retest 1 usa `RETEST_1
  2010.01.01-2017.10.02`, terminando exactamente al inicio de Build Capa2.
- Contrato de datos: esta fase usa Dukascopy por validacion historica
  cross-broker (`AUDCAD_dukascopy`, source `2`, broker `3`). El siguiente
  bloque `phase20_capa2_tick_real` y el resto de Capa2 vuelven a Darwinex.
- Contrato de validacion: `StrategyType` pasivo desde `RETEST 0`,
  `CrossChecks use=false/evaluateAll=false`, metodos/condiciones ocultas
  apagadas, `FitPortfolio=false`, `CustomAnalysis=false`,
  `ExitAfterBars=false`.
- Filtros predeclarados y amplios: `NumberOfTrades >= 80`,
  `ProfitFactor >= 1.05` y `ReturnDDRatio >= 1`.
- Ambos targets quedan idempotentes tras apply: `changedActionCount=0`,
  `guardOk=true`, `issues=[]`, `warnings=[]`, `processes=[]`.
- Guard academico: Retest 1 mide supervivencia historica de candidatos ya
  filtrados por Retest 0; no ajusta parametros, rankings, filtros ni estados
  de resultado.
- No hubo lanzamiento SQX, smoke, optimizacion ni ejecucion real; no se fuerza
  `Results=passed`.
- El estado local queda en `currentPhase=phase19_capa2_retest1`,
  `nextPhase=phase20_capa2_tick_real`, `scope=capa2`.

Siguiente bloque exacto: `phase20_capa2_tick_real`.

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
10. Cada mensaje del operador activa un triage de subagentes/skills disponibles
    y se invocan los adecuados si aportan valor real a seguridad, metodologia,
    verificacion, docs, privacidad o implementacion. Se pueden usar todos los
    subagentes disponibles cuando las tareas sean independientes y utiles.
11. Si el operador pide G9, subagentes, delegacion o paralelo y Multi-agent
    tools no estan expuestas, el orquestador debe cargarlas con `tool_search`;
    el paralelismo de subagentes exige spawn real en la misma ronda, no solo
    lectura de skills/docs.
12. Cada nueva sesion/chat empieza con bootstrap breve: fase activa, siguiente
    bloque exacto, frentes abiertos, gates, riesgos de verificacion y tarea
    anterior pendiente.
13. Tras compactacion automatica o si los subagentes condicionan el siguiente
    paso, dejar resumen sanitizado en `.local/agent_handoffs/`.
14. Los permisos ampliados de subagentes no son automaticos: Codex sigue siendo
    orquestador, y toda mutacion mantiene fase, backup, diff, tests y
    confirmacion cuando el gate lo exige.

## Criterios De Aceptacion

- `tools\sqx142_task_config_gate.ps1 preflight --apply` queda `ok: true`.
- El ledger local conserva `session_state.json`, snapshots y diff.
- El roadmap y governance nombran C1-CONFIG1.
- La Fase 1 no deja `viewAssignments` pendientes en el diff semantico.
- Docs guard pasa.
- Antes de promocionar cambios reales a la base, existe diff y rollback.

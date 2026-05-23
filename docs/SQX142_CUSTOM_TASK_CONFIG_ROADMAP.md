# SQX142 Custom Task Config Roadmap

Estado: C1-CONFIG1 con Fase 4 `RETEST 1` abierta el 2026-05-23. Fase 0 dejo
preflight, snapshots y diff semantico en `.local/sqx142_task_config/`; Fase 1
promociono las views ligeras/especializadas desde Mining15 a la base local y al
template repo; Fase 2 genero los cuestionarios completos de Build Capa1 y cerro
Build. Antes de `RETEST 0`, G8-SQX-AGENT-SKILLS1 alinea skills, guardianes,
perfiles del agente y handoffs locales para proteger el resto del cuestionario.
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
  `sqx-docs-curator` y `sqx-agent-skills`.
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
- `Blocks` en la base local aparece con `Signals`, `Indicators` y
  `Stop/Limit` activos, `ExitAfterBars` al `50%` y sin `version`; donor y la
  regla cerrada de `RETEST 0` apuntan a un universo mas controlado, con
  indicadores/metodologia y `ExitAfterBars` como salida principal.
- `PartsToImprove` mantiene `ExitRules` activo y `WhatToBuild` usa
  `random-generation`, lo que sugiere una forma de mejora/retrabajo de salida
  mas que un retest pasivo puro. Este punto queda abierto para debate
  metodologico antes de registrar respuestas masivas.
- `Rankings/DeleteFailedStrategies` difiere: base `false`, donor `true`.
- `Options` contiene diferencias de ventana horaria y sesion de mercado que
  deben seguir siendo generator-owned por timeframe/broker.
- `RiskMoneyManagement` difiere entre `FixedAmount` y `FixedSize`; la regla
  historica de Capa1 v2 dice Fixed size order size `1`, pero se revisara en la
  pregunta de fase.

Siguiente bloque de decision: `Options` / `Databanks` / `Rankings`, manteniendo
el rol pasivo de OOS2 y dejando los filtros de `retest 1` algo mas tolerantes o
advisory que `RETEST 0` si la evidencia de la pestaña lo confirma.

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

# SQX142 Custom Task Config Roadmap

Estado: C1-CONFIG1 en Fase 1 aplicada el 2026-05-23. Fase 0 dejo
preflight, snapshots y diff semantico en `.local/sqx142_task_config/`; Fase 1
promociono las views ligeras/especializadas desde Mining15 a la base local y al
template repo.

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
tools\sqx142_task_config_gate.ps1 questionnaire --task-title "MC 2" --tab "CrossChecks" --write
tools\sqx142_task_config_gate.ps1 questionnaire --task-title "MC 2" --tab "CrossChecks" --write --full-output
tools\sqx142_task_config_gate.ps1 record-answer --task-title "MC 2" --tab "CrossChecks" --question-id "<id>" --answer "<answer>"
tools\sqx142_task_config_gate.ps1 phase-report --phase phase1 --summary "<summary>" --next-phase phase2 --write
```

`preflight --apply` escribe solo evidencia local ignorada por Git: snapshots de
donor/base/template, diff semantico y `session_state.json`.

`questionnaire` detecta y guarda todas las entradas de la pestaña por defecto.
`--max-values` queda solo como throttle diagnostico temporal y no debe usarse
para cerrar una fase. Cuando se usa `--write`, la consola devuelve resumen para
no inundar el terminal; el JSON completo se guarda en `.local`. `--full-output`
imprime todas las preguntas si hace falta inspeccionarlo directamente.

## Fases

0. Preflight, backup plan, snapshots donor/base/template y diff semantico.
1. Promocion selectiva inicial Mining15 -> Capa1 base, solo fixes validados y
   reversibles.
2. Build Capa1, pestaña por pestaña.
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

## Criterios De Aceptacion

- `tools\sqx142_task_config_gate.ps1 preflight --apply` queda `ok: true`.
- El ledger local conserva `session_state.json`, snapshots y diff.
- El roadmap y governance nombran C1-CONFIG1.
- La Fase 1 no deja `viewAssignments` pendientes en el diff semantico.
- Docs guard pasa.
- Antes de promocionar cambios reales a la base, existe diff y rollback.

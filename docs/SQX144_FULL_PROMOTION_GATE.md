# SQX144 Full Host Promotion Gate

Estado: `completed_preflight_passed_local_config_switched_pending_manual_results_confirmation`.

Fase: `SQX144-FULL-PROMOTE1 Host Promotion Gate`.

Marker: `sqx144-full-promotion-gate-v1`.

Este bloque promueve `SQX_144_Full` como host primario candidato para SQX Edge Suite, con SQX 142 como fallback hasta que pasen los gates de compatibilidad y la confirmacion manual del operador. No es una migracion por copia de internals de SQX 144 al repo ni a SQX 142.

## Decision

- Host candidato: `SQX_144_Full`.
- Perfil local: `sqx144_full`.
- Fallback: el host SQX 142 actual sigue siendo rollback operativo hasta que la promocion este verificada.
- Fuente de memoria: gbrain page `sqx-edge-suite/sqx144-full-promotion-decision-20260604`.
- Rama de trabajo: `codex/sqx144-full-host-promotion`.

## Alcance Permitido

- Validar en modo read-only que el host 144 Full tiene ejecutable, `user/data/data.db`, `user/projects` y `user/extend/ResultsPlugins`.
- Extender metadata local para detectar `sqx144_full` en autodetect/validate.
- Actualizar solo configuracion local ignorada para apuntar a SQX 144 Full despues de un preflight limpio.
- Conservar backup local ignorado de la configuracion previa para volver al host SQX 142.
- Reanudar la confirmacion visual manual de Results Plugin desde `SQX144-COMPAT7B` cuando el operador abra una sesion licenciada valida.

## Bloqueado

- Copiar engine, binarios, runtime, `internal`, jars, licencia, activacion, bypass, tokens, cookies o secretos.
- Copiar `data.db`, databanks, logs o proyectos completos al repo.
- Usar Migration Tool como fuente automatica de migracion.
- Lanzar proyectos, retests, MT5 import, MCP write calls, `run_project` o `stop_project`.
- Mutar `user/projects`, escribir en `data.db`, borrar databanks o forzar resultados.
- Cambiar endpoints `/api/sqx142/*` en esta fase.
- Hacer claims de rentabilidad, riesgo cero, certificacion externa o auditoria externa.

## Read-Only Gate

Herramienta: `tools/sqx144_full_host_gate.ps1`.

Modos:

- `status`: inspeccion saneada del host candidato sin mutacion.
- `preflight`: exige shape completo y cero procesos SQX relevantes antes de permitir el switch local.

El path local del host se pasa en ejecucion con `-SqxRoot` o con la variable `SQX144_FULL_ROOT`; el script trackeado no hardcodea rutas locales.

Criterios `preflight`:

- `rootExists=true`.
- `executableExists=true`.
- `dataDbExists=true`.
- `projectsDirExists=true`.
- `resultsPluginsDirExists=true`.
- `noRelevantProcesses=true`.
- `copyExecuted=false`.
- `sqxRuntimeStarted=false`.
- `projectRunStarted=false`.
- `migrationToolUsed=false`.
- `dataDbWriteAllowed=false`.
- `userProjectsWriteAllowed=false`.

## Config Local Y Rollback

Tras `preflight` limpio, `backend/sqx-edge-tool/config.json` puede actualizarse localmente a:

- `sqx_path`: host SQX 144 Full.
- `sqx_data_db`: `user/data/data.db` del host 144 Full.
- `sqx_projects_dir`: `user/projects` del host 144 Full.
- `sqx_host_profile`: `sqx144_full`.

Antes del cambio se debe guardar una copia ignorada bajo `.local/sqx144_full_promotion/`. Si cualquier verificacion posterior falla, se restaura esa copia o se reelige el host SQX 142 anterior desde la UI.

## Verificacion

- `tools/sqx144_full_host_gate.ps1 preflight`.
- Tests focales de `validate-sqx-path` y `autodetect-sqx` para `sqx144_full`.
- Tests de copy-only migration checklist para confirmar que licencia, engine, `data.db`, databanks y Migration Tool siguen bloqueados.
- Confirmacion manual pendiente: abrir SQX 144 Full con licencia valida, llegar al workspace/Results sin bypass, no lanzar proyectos y verificar si `SQX Edge Readiness Panel` aparece sin errores.

## Estado Actual

`SQX144-FULL-PROMOTE1` ya paso `tools/sqx144_full_host_gate.ps1 preflight` con decision `sqx144_full_host_gate_passed`: shape completo, `projectDirCount=15`, `resultsPluginCount=3`, `relevantProcessCount=0`, `copyExecuted=false`, `sqxRuntimeStarted=false`, `projectRunStarted=false`, `migrationToolUsed=false`, `dataDbWriteAllowed=false` y `userProjectsWriteAllowed=false`.

La configuracion local ignorada fue actualizada a `sqx_host_profile=sqx144_full` tras guardar backup en `.local/sqx144_full_promotion/`. SQX 142 sigue como fallback. Queda pendiente la confirmacion manual de workspace/Results en SQX 144 Full; el `SQX Edge Readiness Panel` no se copio en esta fase y sigue pendiente de decision/backup especifico.

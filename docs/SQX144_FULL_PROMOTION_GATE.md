# SQX144 Full Host Promotion Gate

Estado: `completed_preflight_passed_operator_migration_done_snippets_compile_passed_pending_results_confirmation_update1_no_promote`.

Fase: `SQX144-FULL-PROMOTE1 Host Promotion Gate`.

Marker: `sqx144-full-promotion-gate-v1`.

Este bloque promueve `SQX_144_Full` como host primario candidato para SQX Edge Suite, con SQX 142 como fallback hasta que pasen los gates de compatibilidad y la confirmacion manual del operador. No es una migracion por copia de internals de SQX 144 al repo ni a SQX 142.

## Decision

- Host candidato: `SQX_144_Full`.
- Perfil local: `sqx144_full`.
- Fallback: el host SQX 142 actual sigue siendo rollback operativo hasta que la promocion este verificada.
- Migracion local: el operador ejecuto la Migration Tool oficial de SQX 144 Full e importo la instalacion SQX 142 Codex con exito; esta accion queda registrada como `operator_migration_completed_snippets_compile_passed`, sin copiar salidas privadas al repo.
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
- Automatizar Migration Tool desde Codex, versionar su salida o usarla como fuente publica de migracion.
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

## Operator Migration And Snippet Compatibility

El 2026-06-04 el operador abrio SQX 144 Full con licencia valida, llego al workspace y ejecuto la Migration Tool oficial para importar la instalacion SQX 142 Codex. La migracion fue reportada como completa por el operador.

Tras esa migracion, la compilacion de snippets fallo por una incompatibilidad API localizada: 13 snippets de usuario bajo `SQ.Columns.Databanks` llamaban al metodo obsoleto `MainApp.isRangerLicense()`, ausente en SQX 144 Full. La comparacion con columnas internas de SQX 144 mostro que el filtro Ranger/EndTest fue retirado en Build 144. Codex adapto solo esos snippets de usuario, eliminando la llamada obsoleta y sus imports, con backup local ignorado bajo `.local/sqx144_full_migration_fix/`.

Verificacion local saneada:

- Snippet compile forzado tras regenerar el indice `user/settings/snippets.txt`: `Compiling Snippets done in 11s`.
- Referencias obsoletas `MainApp.isRangerLicense()` en Databanks: `0`.
- Gate `tools/sqx144_full_host_gate.ps1 -Mode preflight -SqxRoot <local>`: `sqx144_full_host_gate_passed`.
- Procesos SQX relevantes al cierre: `0`.

Avisos residuales no bloqueantes para la compilacion: `sqcustomization` devuelve HTTP 422 para la cuenta local y faltan ficheros auxiliares de metadata de mercados (`Exchanges`, `Countries`, `Sectors`, `Custom timeframes`). La actualizacion 144.2953 queda registrada en `docs/SQX144_FULL_UPDATE1_GATE.md` como `blocked_license_activation_pending_and_migration_alignment`: existe un host actualizado separado con Build 144.2953 confirmado, pero no se promueve porque abre pantalla de licencia antes del workspace y no contiene la alineacion migrada ni `SQX Edge Readiness Panel`. Tras confirmar que el instalador oficial no permite seleccionar el directorio existente `SQX_144_Full`, `docs/SQX144_FULL_UPDATE2_GATE.md` abre la ruta activa por carpeta nueva 144.2953, activacion legitima y alineacion oficial antes de promocion. Estos avisos no autorizan proyectos, imports MT5, escritura directa en `data.db` ni claims de rentabilidad.

## Estado Actual

`SQX144-FULL-PROMOTE1` ya paso `tools/sqx144_full_host_gate.ps1 preflight` con decision `sqx144_full_host_gate_passed`: shape completo, `projectDirCount=29`, `resultsPluginCount=5`, `sqxEdgeReadinessPanelPresent=true`, `relevantProcessCount=0`, `copyExecuted=false`, `sqxRuntimeStarted=false`, `projectRunStarted=false`, `migrationToolUsed=false` para el gate/script, `dataDbWriteAllowed=false` y `userProjectsWriteAllowed=false`.

La configuracion local ignorada fue actualizada a `sqx_host_profile=sqx144_full` tras guardar backup en `.local/sqx144_full_promotion/`. SQX 142 sigue como fallback. Tras la migracion oficial ejecutada por el operador, `SQX Edge Readiness Panel` esta presente en el host 144; Codex no copio engine, internals, licencia, `data.db`, databanks, logs ni salidas de Migration Tool al repo. Queda pendiente la confirmacion manual de Results en SQX 144 Full.

`SQX144-FULL-UPDATE1` confirmo Build 144.2953 en un host actualizado separado, pero no cambio esta promocion: la config local sigue apuntando al host migrado/licenciado anterior hasta que el host 144.2953 pase activacion/licencia y alineacion oficial de migracion. `SQX144-FULL-UPDATE2` es ahora el carril activo para una carpeta nueva 144.2953, gobernado por `tools/sqx144_full_update2_gate.ps1`.

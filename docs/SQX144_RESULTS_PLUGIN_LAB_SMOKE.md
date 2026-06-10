# SQX144 Results Plugin Lab Smoke

Estado: `SQX144-COMPAT6 Results Plugin Lab Smoke` completado como smoke de lab con confirmacion visual manual pendiente.

Este bloque instala el payload minimo aprobado de `SQX Edge Readiness Panel` en el SQX 144 lab aislado y verifica que el lab arranca sin dejar procesos vivos. No toca SQX 142, no lanza proyectos, no llama MCP, no importa MT5 y no usa Migration Tool.

## Resultado

Decision: `lab_smoke_passed_with_manual_results_tab_pending`.

Evidencia local ignorada: `.local/sqx144_lab_intake/sqx144_compat6_results_plugin_lab_smoke_20260526_151800.json`.

Instalacion ejecutada:

- Destino: `user/extend/ResultsPlugins/SQX Edge Readiness Panel` dentro del lab SQX 144.
- Archivos copiados: `index.html` y `fixtures/fixtures.js`.
- Sobrescritura: `false`; el destino no existia antes de COMPAT6.
- Hashes instalados coinciden con el prototipo offline COMPAT4.

Smoke automatico:

- Privacy/static scan: `passed`.
- Render desde carpeta instalada: `passed`.
- Estados Playwright confirmados: `ready`, `review`, `blocked`.
- Captura local ignorada: `.local/sqx144_lab_intake/plugin_prototypes/SQX Edge Readiness Panel/smoke/compat6_installed_panel_desktop.png`.
- SQX 144 lab launch: `passed_process_start`.
- Procesos observados: `StrategyQuantX` y `StrategyQuantX_ui`.
- Cierre final: `remainingRelevantProcesses=0`.

Limitacion honesta:

- `visualResultsTabObserved=false`. El smoke automatico confirmo instalacion, render del HTML instalado y arranque del lab, pero no se hizo seleccion interactiva dentro del tab Results de SQX.

## Bloqueos Preservados

Sigue bloqueado:

- SQX 142 install/runtime.
- Project run, `run_project`, `stop_project`.
- MCP calls.
- `GET_SOURCE_CODE`, `GET_ORDERS`.
- `resultsPlugins/create`, `resultsPlugins/rename`, `resultsPlugins/delete`.
- File writes desde el plugin, browser persistence y databank mutation.
- MT5 import, Migration Tool, migracion entre versiones y cambio de `sqx_path`.

## Rollback

Rollback permitido si el operador rechaza el smoke visual:

1. Cerrar SQX 144.
2. Borrar solo la carpeta `SQX Edge Readiness Panel` del lab SQX 144.
3. Registrar evidencia local saneada del rollback.

## Siguiente Bloque

`SQX144-COMPAT7 Results Plugin Manual Visual Confirmation` debe confirmar manualmente en SQX 144 lab:

- El plugin aparece en Results.
- No hay error visible al abrirlo.
- La UI mantiene disclaimer y estados legibles.
- No se observa solicitud de source code, orders, MCP, proyecto, importacion o escritura.

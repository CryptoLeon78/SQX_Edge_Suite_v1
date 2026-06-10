# SQX144 Full Update1 Gate

Estado: `blocked_updated_host_requires_license_activation_and_migration_alignment`.

Fase: `SQX144-FULL-UPDATE1 Controlled Build 144.2953 Update Gate`.

Marker: `sqx144-full-update1-gate-v1`.

Este bloque registra la actualizacion a Build 144.2953 como gate controlado. La actualizacion fue localizada como un host separado instalado por el updater oficial, pero no se promueve todavia como host primario porque no alcanza workspace licenciado ni contiene la alineacion migrada del host SQX 144 Full actual.

## Decision

- Candidato actualizado: `SQX144_2953_updated_host_candidate`.
- Build confirmado por log local saneado: `SQX version: 144.2953`.
- Decision: `blocked_license_activation_pending_and_migration_alignment`.
- Configuracion local: se conserva apuntando al host SQX 144 Full migrado/licenciado anterior.
- Rollback: SQX 142 ya no es fallback operativo activo; reselectarlo seria una excepcion manual desde backup/config local si el operador lo aprueba.

## Hallazgos

- El host actualizado pasa shape basico read-only: ejecutable, `user/data/data.db`, `user/projects`, `user/extend/ResultsPlugins` y cero procesos relevantes.
- El arranque corto de validacion llega a la pantalla de licencia antes del workspace, por lo que no hay confirmacion de Results ni compilacion de snippets en 144.2953.
- La alineacion migrada no esta presente en el host actualizado: el conteo saneado queda por debajo del host migrado y `SQX Edge Readiness Panel` no aparece en Results Plugins.
- El host SQX 144 Full migrado anterior sigue siendo el candidato operativo: preflight limpio, `projectDirCount=29`, `resultsPluginCount=5`, `sqxEdgeReadinessPanelPresent=true` y snippets compilados.

## Alcance Permitido

- Leer estructura, logs saneados, conteos y procesos del host actualizado.
- Confirmar version por log sin exponer rutas locales ni lineas privadas completas.
- Mantener `backend/sqx-edge-tool/config.json` sin cambio cuando el gate no promueve.
- Reintentar el gate despues de activacion/licencia del host actualizado o despues de una nueva migracion oficial ejecutada por el operador.

## Bloqueado

- Copiar licencia, activacion, bypass, tokens, cookies o secretos entre hosts.
- Copiar engine, binarios, runtime, `internal`, jars o plugins propietarios al repo o a SQX 142.
- Copiar `data.db`, databanks, logs, proyectos completos o salida de Migration Tool al repo.
- Automatizar la Migration Tool desde Codex en este gate.
- Lanzar proyectos, MT5 import, MCP writes, `run_project`, `stop_project`, escribir `data.db`, mutar `user/projects` o borrar databanks.
- Forzar estado de pass, prometer rentabilidad o declarar riesgo cero.

## Herramienta

Herramienta: `tools/sqx144_full_update_gate.ps1`.

Modos:

- `status`: inspeccion saneada y read-only del candidato actualizado.
- `preflight`: exige Build 144.2953 confirmado, workspace sin pantalla de licencia, shape migrado, `SQX Edge Readiness Panel`, cero procesos y ausencia de fallo de snippets antes de permitir promocion.

La herramienta no ejecuta updater, no lanza proyectos, no usa Migration Tool, no manipula licencia y no cambia la configuracion local.

Guard clave: `localConfigSwitched = $false`.

## Verificacion

- `tools/sqx144_full_host_gate.ps1 -Mode preflight` sobre el host actualizado: shape basico OK, `projectDirCount=15`, `resultsPluginCount=3`, `sqxEdgeReadinessPanelPresent=false`, procesos `0`.
- Arranque controlado del host actualizado: Build 144.2953 confirmado, pantalla de licencia detectada antes de workspace, compilacion de snippets no observada, cierre con procesos `0`.
- `tools/sqx144_full_host_gate.ps1 -Mode preflight` sobre el host SQX 144 Full migrado anterior: `projectDirCount=29`, `resultsPluginCount=5`, `sqxEdgeReadinessPanelPresent=true`, procesos `0`.
- `tools/sqx144_full_update_gate.ps1 -Mode status` clasifica el host actualizado como `blocked_license_activation_pending_and_migration_alignment`.

## Estado Actual

`SQX144-FULL-UPDATE1` queda cerrado como no-promote controlado: la actualizacion 144.2953 existe y fue confirmada, pero requiere activacion/licencia del host actualizado y alineacion oficial de migracion antes de cambiar `sqx_path` o promoverlo como host primario.

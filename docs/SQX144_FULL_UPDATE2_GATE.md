# SQX144 Full Update2 Gate

Estado: `active_new_directory_update_path_pending_operator_install_activation_and_official_migration_alignment`.

Fase: `SQX144-FULL-UPDATE2 New Directory 144.2953 Promotion Gate`.

Marker: `sqx144-full-update2-gate-v1`.

Este bloque sustituye la idea de actualizacion in-place del host licenciado porque el instalador oficial permite elegir ruta, pero bloquea avanzar si el directorio elegido ya contiene una instalacion SQX. La ruta correcta pasa a ser: instalar Build 144.2953 en una carpeta nueva, mantener `SQX_144_Full` como fuente licenciado/migrada, y promover la carpeta nueva solo despues de activacion legitima y alineacion oficial de migracion.

## Decision

- Fuente operativa: `SQX_144_Full_working_migrated_source`.
- Candidato nuevo: `SQX144_2953_new_directory_candidate`.
- Perfil candidato futuro: `sqx144_full_2953_candidate`.
- Decision inicial: `blocked_candidate_license_and_official_migration_alignment_pending`.
- Configuracion local: sin cambio; sigue apuntando al host SQX 144 Full migrado/licenciado anterior.
- Fallback: SQX 142 sigue disponible como rollback operativo.

## Motivo

El operador confirmo que el instalador oficial no deja seleccionar el directorio actual `SQX_144_Full` porque detecta una instalacion existente. Por tanto, no se debe forzar una actualizacion en sitio ni copiar a mano motor, `internal`, licencia o activacion desde otro host.

## Alcance Permitido

- Validar read-only el host fuente y el candidato nuevo con `tools/sqx144_full_update2_gate.ps1 status|preflight`.
- Instalar 144.2953 en una carpeta nueva mediante el instalador oficial, como accion manual/operator-owned.
- Activar o abrir workspace por flujo legitimo de SQX, sin bypass ni manipulacion de licencia por Codex.
- Alinear proyectos/plugins/panel/snippets mediante Migration Tool oficial o export/import documentado, ejecutado o confirmado por el operador.
- Reinstalar solo payloads propios de SQX Edge, como `SQX Edge Readiness Panel`, con backup y cero procesos SQX.

## Bloqueado

- Copiar licencia, activacion, bypass, tokens, cookies, secretos o cambios de `hosts`.
- Copiar engine, binarios, runtime, `internal`, jars o plugins propietarios entre hosts por script de Codex.
- Copiar `data.db`, databanks, logs, proyectos completos o salida de Migration Tool al repo.
- Automatizar Migration Tool desde Codex en este gate.
- Lanzar proyectos, MT5 import, MCP writes, `run_project`, `stop_project`, escribir `data.db`, mutar `user/projects` o borrar databanks.
- Cambiar `backend/sqx-edge-tool/config.json` al candidato antes de `preflight` limpio.
- Forzar estados de pass, prometer rentabilidad o declarar riesgo cero.

## Herramienta

Herramienta: `tools/sqx144_full_update2_gate.ps1`.

Modos:

- `status`: inspeccion saneada y read-only de fuente y candidato.
- `preflight`: exige fuente valida, candidato en carpeta distinta, Build 144.2953 confirmado, workspace sin pantalla de licencia, shape migrado, `SQX Edge Readiness Panel`, cero procesos y ausencia de fallo de snippets antes de permitir promocion.

Variables opcionales:

- `SQX144_FULL_ROOT`: host fuente licenciado/migrado.
- `SQX144_UPDATE2_ROOT`: candidato nuevo 144.2953.

La herramienta no ejecuta instalador, no lanza proyectos, no usa Migration Tool, no manipula licencia y no cambia configuracion local.

Guard clave: `installerExecutedByThisScript = $false`, `officialMigrationToolExecutedByThisScript = $false`, `licenseMaterialHandled = $false`, `localConfigSwitched = $false`.

## Verificacion Inicial

- Ejecutar `tools/sqx144_full_update2_gate.ps1 -Mode status -SourceRoot <host-bueno> -CandidateRoot <candidato-2953>`.
- Esperado antes de accion manual: fuente OK, candidato bloqueado por licencia/alineacion si aun es `C:\StrategyQuantX144`.
- Despues de instalacion/activacion/migracion oficial: ejecutar `preflight`; solo puede devolver `sqx144_full_update2_ready_for_promotion` cuando todos los checks pasen.

## Estado Actual

`SQX144-FULL-UPDATE2` queda activo como ruta de promocion a 144.2953 por carpeta nueva. La actualizacion no se consigue pisando `SQX_144_Full`; se consigue preparando un candidato 144.2953 nuevo, activandolo por flujo legitimo, alineandolo oficialmente desde el host bueno y promoviendo solo tras gate limpio.

# SQX142-144-BACKPORT8 Copy-Only Migration Checklist

Estado: `completed_checklist_no_copy`.

Este bloque sustituye la idea de `Migration Tool` de Build 144 por un checklist copy-only propio de SQX Edge. No ejecuta migracion, no copia archivos, no arranca SQX y no toca instalaciones locales.

## Implementacion

- Core: `backend/sqx-edge-tool/core/sqx142_copy_only_migration_checklist.py`.
- API local-only: `POST /api/sqx142/migration/copy-only-checklist`.
- Tests: `backend/sqx-edge-tool/test_sqx142_copy_only_migration_checklist.py`.
- Version de respuesta: `sqx142-copy-only-migration-checklist-v1`.
- Modo: `checklist_only_no_copy`.
- Fuente esperada: `operator_copy_plan`.

## Entradas

El endpoint acepta `items`, `migrationItems`, `copyItems` o `checklist`. Cada item puede declarar:

- `kind`.
- `label`.
- `relativePath`.
- `operation`.

Si no se pasan items, devuelve una matriz por defecto con Results Plugin propio, proyecto seleccionado, preferencias no sensibles y materiales bloqueados.

## Decisiones

- `allow_copy`: payload SQX Edge-owned y reversible, como `SQX Edge Readiness Panel`.
- `review_copy`: proyectos, `.sqx`, `.cfx`, settings, presets, templates o BlockSettings que requieren revision, backup, confirmacion manual y hash.
- `block_copy`: licencia, activacion, crack/bypass, tokens, engine, binarios, runtime, internals, `data.db`, databanks, logs, Migration Tool o cualquier material sensible.

## Pasos Manuales Para Items No Bloqueados

- `preflight_process_sweep`.
- `backup_destination`.
- `copy_only_after_operator_confirmation`.
- `hash_verify`.
- `manual_open_check`.

Estos pasos son solo checklist; el endpoint no ejecuta ninguno.

## Gate Y Privacidad

El endpoint exige operador local y devuelve `403 local_operator_required` a remoto/tester. La respuesta mantiene:

- `privacy.local_paths_returned=false`.
- `privacy.raw_item_names_returned=false`.
- `privacy.private_fields_returned=false`.
- `privacy.tokens_returned=false`.

Tambien mantiene guards explicitos:

- `copy_executed=false`.
- `migration_tool_used=false`.
- `license_material_allowed=false`.
- `activation_material_allowed=false`.
- `engine_binary_allowed=false`.
- `data_db_write_allowed=false`.
- `user_projects_write_allowed=false`.
- `sqx_runtime_started=false`.
- `remote_tester_access=false`.

## Bloqueado

- Usar `Migration Tool`.
- Copiar licencias, activacion, cracks, bypass, tokens, cookies o secretos.
- Copiar engine, binarios, `internal`, `jre`, runtime, jars o ejecutables.
- Copiar `data.db`, databanks o logs como migracion.
- Escribir `data.db` o `user/projects` desde la API.
- Arrancar SQX, lanzar proyectos o retests.
- Activar `CustomAnalysis=true` o `FitPortfolio=true`.
- Copiar internals de SQX 144 a SQX 142.
- Exponer rutas locales o nombres crudos.

## Verificacion

- `test_sqx142_copy_only_migration_checklist.py` -> `5 passed`.
- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport8_copy_only_migration_checklist_20260526_193000.json`.

Siguiente bloque recomendado: cierre de backport 142/144 o decision de nuevo frente por operador.

# SQX142-144-BACKPORT3 MCP-Like Read-Only API Build

Estado: `completed_build_no_sqx_runtime`.

Este bloque implementa el contrato definido en `docs/SQX142_144_MCP_LIKE_READ_ONLY_API_DESIGN.md` como API Flask local propia de SQX Edge. No copia `ServletMCP`, no arranca SQX, no llama a la API local interna de StrategyQuant y no escribe en SQX 142.

## Implementado

Modulo nuevo:

- `backend/sqx-edge-tool/core/sqx142_mcp_like_readonly.py`

Rutas nuevas:

- `GET /api/sqx142/mcp-like/status`
- `GET /api/sqx142/mcp-like/projects`
- `GET /api/sqx142/mcp-like/data-catalog`
- `GET /api/sqx142/mcp-like/databanks`
- `GET /api/sqx142/mcp-like/strategies`
- `GET /api/sqx142/mcp-like/results-plugin-readiness`

Tests nuevos:

- `backend/sqx-edge-tool/test_sqx142_mcp_like_readonly.py`

Version de respuesta:

- `sqx142-mcp-like-readonly-v1`

## Seguridad

Todas las rutas usan el gate local de operador:

- `request.remote_addr` local.
- `request.host` local.
- Sin cabecera de usuario remoto autenticado.
- Acceso remoto/tester: `403 local_operator_required`.

Todas las respuestas conservan:

- `mode=read_only`
- `scope=local_operator_only`
- `privacy.local_paths_returned=false`
- `privacy.raw_project_names_returned=false`
- `privacy.license_material_returned=false`
- `privacy.tokens_returned=false`

## Fuentes

Fuentes permitidas y usadas:

- `build_sqx142_status(include_paths=False)`
- `build_sqx142_performance_status(..., include_paths=False)`
- `user/projects` scan read-only
- `user/data/data.db` via SQLite URI `mode=ro`
- `user/extend/ResultsPlugins` conteo saneado

## Bloqueos

La build mantiene bloqueado:

- `POST`, `PUT`, `PATCH`, `DELETE`
- `includeRawNames=true`
- `run_project`
- `stop_project`
- `project/start`
- `project/stop`
- `taskmanager/activateTask`
- `GET_SOURCE_CODE`
- `GET_ORDERS`
- Escritura en `data.db`
- Escritura en proyectos/databanks/settings/browser storage/logs SQX
- MT5 import
- Migration Tool
- licencia, activacion, bypass/crack
- engine, binarios e internals de SQX 144

## Comportamiento

- `projects` devuelve `projectId` opaco, clase, timestamps redondeados y conteos de archivos, sin nombre crudo ni ruta.
- `data-catalog` devuelve tablas, conteos y muestras de series con `seriesId`/`instrumentId` opacos, sin simbolos crudos.
- `databanks` y `strategies` requieren `projectId` opaco.
- `strategies` devuelve `sourceCodeIncluded=false` y `ordersIncluded=false`.
- `results-plugin-readiness` devuelve estado `ready/review/blocked` para alimentar `SQX Edge Readiness Panel`.

## Evidencia

Evidencia local ignorada:

- `.local/sqx142_144_backport/sqx142_144_backport3_mcp_like_read_only_api_build_20260526_164500.json`

Verificacion ejecutada:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe -m pytest backend\sqx-edge-tool\test_sqx142_mcp_like_readonly.py -q
backend\sqx-edge-tool\venv\Scripts\python.exe -m pytest backend\sqx-edge-tool\test_local_ai_agent.py -q
```

Resultado:

- `5 passed`
- `24 passed`

Siguiente bloque recomendado: `SQX142-144-BACKPORT4 Correlation Filter External Design`.

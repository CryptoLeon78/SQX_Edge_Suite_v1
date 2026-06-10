# SQX142-144-BACKPORT2 MCP-Like Read-Only API Design

Estado: `completed_design_no_runtime`.

Este bloque adapta la idea MCP de Build 144 a SQX 142 como una API local propia de SQX Edge. No copia `ServletMCP`, clases, plugins internos, binarios, licencia ni endpoints propietarios de 144.

## Objetivo

Crear un contrato de API local, read-only y saneada para que el monitor/agente de SQX Edge pueda consultar contexto de SQX 142 sin abrir proyectos, lanzar tareas ni modificar databanks.

La API debe servir como superficie `MCP-like`, no como MCP nativo de StrategyQuant:

- Flask/SQX Edge es el unico servidor expuesto.
- SQX 142 se trata como fuente local de lectura.
- Las respuestas publicas no devuelven rutas Windows, nombres crudos sensibles, licencias, tokens, emails ni logs privados.
- Los usuarios remotos/testers reciben `local_operator_required`.

## Evidencia Estatica

Snapshot local saneado 2026-05-26:

- SQX 142 local existe.
- `projectDirCount=29`: `user/projects` existe con `29` carpetas de proyecto.
- `resultsPluginCount=2`: `user/extend/ResultsPlugins` existe con `2` plugins.
- `user/data/data.db` existe.
- Tablas detectadas en `data.db`: `BROKER`, `BROKER_STOCK`, `DATA`, `ELEMENTS`, `INSTRUMENTS`, `SESSIONS`, `STOCK`, `STOCK_GROUP`, `sqlite_sequence`.
- Conteos read-only: `BROKER=12`, `DATA=34`, `INSTRUMENTS=989`, `SESSIONS=1081`.
- Procesos SQX/Java relevantes durante el snapshot: `0`.

Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport2_mcp_like_read_only_api_design_20260526_160500.json`.

## Endpoints Propuestos

Todos los endpoints deben vivir bajo `/api/sqx142/mcp-like/*`, exigir operador local y devolver `privacy.local_paths_returned=false`.

| Endpoint | Funcion | Fuente permitida | Notas |
| --- | --- | --- | --- |
| `GET /api/sqx142/mcp-like/status` | Estado agregado de disponibilidad local | `build_sqx142_status`, `build_sqx142_performance_status` | Similar a health/readiness, sin rutas. |
| `GET /api/sqx142/mcp-like/projects` | Lista saneada de proyectos | `user/projects` scan read-only | Devuelve `projectId`, hash corto, clase, timestamps redondeados y flags; no ruta ni nombre crudo por defecto. |
| `GET /api/sqx142/mcp-like/data-catalog` | Catalogo de datos/brokers/sesiones | `data.db` en `mode=ro` | Devuelve conteos, simbolos redacted/hashed y metadatos utiles para compatibilidad. |
| `GET /api/sqx142/mcp-like/databanks` | Databanks disponibles por proyecto | Carpeta de proyecto en read-only | Requiere `projectId` opaco; no carga estrategias completas. |
| `GET /api/sqx142/mcp-like/strategies` | Resumen de estrategias exportables | Archivos `.sqx`/metadatos en read-only | Limitado, paginado, sin source code ni orders. |
| `GET /api/sqx142/mcp-like/results-plugin-readiness` | Estado para `SQX Edge Readiness Panel` | API propia + fixtures si no hay datos | Alimenta el panel sin PostMessage sensible. |

## Contrato De Respuesta

Forma comun:

```json
{
  "ok": true,
  "version": "sqx142-mcp-like-readonly-v1",
  "scope": "local_operator_only",
  "mode": "read_only",
  "data": {},
  "warnings": [],
  "blockers": [],
  "privacy": {
    "local_paths_returned": false,
    "raw_project_names_returned": false,
    "license_material_returned": false,
    "tokens_returned": false
  }
}
```

Reglas:

- IDs opacos estables por sesion o por hash de nombre + tipo + mtime; no usar rutas como identificador publico.
- `limit` maximo por defecto `50`, maximo absoluto `200`.
- Fechas redondeadas a minuto o dia si no hace falta precision fina.
- `includeRawNames=true` queda bloqueado en v1.
- Cualquier error devuelve version, `ok=false`, `error`, `privacy.local_paths_returned=false`.

## Fuentes Permitidas

- `core.sqx_compatibility.build_sqx142_status(include_paths=False)`.
- `core.sqx_performance.build_sqx142_performance_status(..., include_paths=False)`.
- `user/data/data.db` con SQLite URI `mode=ro`.
- `user/projects` con lectura de directorios, conteos y metadatos.
- `user/extend/ResultsPlugins` solo para conteo/lista saneada de plugins propios.
- Fixtures mock del `SQX Edge Readiness Panel` cuando no exista contexto runtime.

## Operaciones Bloqueadas

La v1 debe rechazar o no implementar:

- `POST`, `PUT`, `PATCH`, `DELETE`.
- `run_project`, `stop_project`, `project/start`, `project/stop`.
- `taskmanager/activateTask`.
- `resultsPlugins/create`, `resultsPlugins/rename`, `resultsPlugins/delete`.
- `GET_SOURCE_CODE`, `GET_ORDERS`, export de source code u orders.
- Escritura en `data.db`, proyectos, databanks, settings, browser storage o logs SQX.
- MT5 import.
- Migration Tool.
- Licencia, activacion, bypass/crack, engine, binarios o internals de SQX 144.

## Seguridad Y Privacidad

El gate de acceso debe copiar el patron de `/api/sqx142/compat/status`:

- `request.remote_addr` local.
- `request.host` local.
- Sin cabecera de usuario remoto autenticado.
- Respuesta `403` con `local_operator_required` para cualquier acceso remoto o tester.

Los tests deben comprobar que `json.dumps(response)` no contiene:

- private local drive roots
- `<LOCAL_SQX142_ROOT>`
- emails
- tokens
- license
- password
- protected URLs

## Implementacion

`SQX142-144-BACKPORT3` construye esta API con estos cambios minimos:

- Nuevo modulo `backend/sqx-edge-tool/core/sqx142_mcp_like_readonly.py`.
- Nuevas rutas Flask en `backend/sqx-edge-tool/api/server.py`.
- Tests en `backend/sqx-edge-tool/test_sqx142_mcp_like_readonly.py`.
- Opcional: el `SQX Edge Readiness Panel` puede consultar `/api/sqx142/mcp-like/results-plugin-readiness` desde localhost y mantener fixtures offline si falla.

## Criterios De Aceptacion

- No se arranca SQX.
- No se llama a la API local interna de SQX.
- No se escribe en SQX 142.
- No se devuelven rutas locales ni nombres crudos por defecto.
- Las rutas remotas/tester reciben `403 local_operator_required`.
- `pytest` cubre local-only, path-safe, read-only, paginacion y bloqueo de verbos mutantes.
- El manifest de consistencia registra este bloque antes de cualquier build.

Siguiente bloque recomendado: `SQX142-144-BACKPORT3 MCP-Like Read-Only API Build`.

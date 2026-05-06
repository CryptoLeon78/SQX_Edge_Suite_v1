# Render Staging Runbook

## Decision

Render es el proveedor recomendado para el primer staging del relay.

Usaremos:

- `backend/sqx-edge-relay/deploy/render.staging.yaml.example`
- `backend/sqx-edge-relay/Dockerfile`
- `backend/sqx-edge-relay/tools/deployment_check.py`
- `backend/sqx-edge-relay/tools/staging_smoke.py`
- `backend/sqx-edge-relay/tools/staging_evidence.py`

## Antes De Crear Servicios

1. Copiar `render.staging.yaml.example` como blueprint de staging si se quiere usar Blueprint.
2. Configurar secretos en Render, no en GitHub:
   - `SQX_LEMON_WEBHOOK_SECRET`
   - `SQX_FULFILLMENT_RELAY_SECRET`
   - `SQX_RELAY_OPERATOR_TOKEN`
   - `SQX_LOCAL_INGEST_URL`
3. Confirmar que el worker existe como servicio separado.
4. Confirmar `healthCheckPath: /relay/health`.

## Despues Del Deploy

Ejecutar:

```powershell
python backend\sqx-edge-relay\tools\staging_smoke.py --base-url https://sqx-edge-relay-staging.onrender.com
```

Luego:

```powershell
python backend\sqx-edge-relay\tools\staging_smoke.py --base-url https://sqx-edge-relay-staging.onrender.com --send-webhook
```

Y finalmente:

```powershell
python backend\sqx-edge-relay\tools\staging_evidence.py --provider render --base-url https://sqx-edge-relay-staging.onrender.com --send-webhook
```

## Go/No-Go

GO requiere:

- `deployment_check.py --strict` en verde con secretos staging.
- `/relay/health` estable.
- `/relay/config-check` limpio.
- `/relay/observability` protegido por token.
- `/relay/observability/snapshot` crea evidencia.
- `wh_m20_staging_demo` entra firmado.
- worker procesa o deja error trazable.

NO-GO si:

- falta URL real,
- falta cualquier secreto,
- cola/observability responden sin token,
- el webhook sin firma entra,
- no hay persistencia para cola/logs,
- el worker no esta desplegado.

## Evidence Pack

`staging_evidence.py` genera:

- JSON para auditoria automatica,
- Markdown para decision humana,
- blockers y warnings.

Guardar esos archivos antes de pasar a produccion.

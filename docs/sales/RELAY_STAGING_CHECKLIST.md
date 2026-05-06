# SQX Edge Relay Staging Checklist

## Inputs

- Provider elegido: Render, Railway, Fly.io o VPS.
- URL staging: `SQX_RELAY_STAGING_BASE_URL`.
- Webhook secret staging: `SQX_LEMON_WEBHOOK_SECRET`.
- Relay shared secret staging: `SQX_FULFILLMENT_RELAY_SECRET`.
- Operator token staging: `SQX_RELAY_OPERATOR_TOKEN`.
- Local ingest staging/tunnel: `SQX_LOCAL_INGEST_URL`.

## Preflight Local

```powershell
python backend\sqx-edge-relay\tools\deployment_check.py --strict
```

Debe devolver `production_ready: true` con secretos de staging cargados.

## Remote Smoke

```powershell
python backend\sqx-edge-relay\tools\staging_smoke.py --base-url https://tu-relay-staging.example.com
```

Debe validar:

- `/relay/health`
- `/relay/config-check`
- `/relay/observability`
- `/relay/observability/snapshot`

## Signed Webhook Smoke

```powershell
python backend\sqx-edge-relay\tools\staging_smoke.py --base-url https://tu-relay-staging.example.com --send-webhook
```

Debe crear un evento demo `wh_m20_staging_demo` y dejar trazas en observabilidad.

## Lemon Test

1. Configurar Lemon Squeezy webhook URL:
   `https://tu-relay-staging.example.com/relay/webhook/lemon`
2. Usar el secret staging.
3. Enviar evento test desde Lemon.
4. Confirmar que aparece en cola.
5. Confirmar que el worker intenta dispatch.
6. Confirmar snapshot posterior.

## Evidence Pack

Guarda para la decision go/no-go:

- salida de `deployment_check.py --strict`,
- salida de `staging_smoke.py`,
- salida de `staging_smoke.py --send-webhook`,
- captura/log de `/relay/observability`,
- snapshot JSON,
- estado final de cola.

## Go

Puede avanzarse a produccion si:

- health estable,
- config check limpio,
- operator token requerido,
- eventos firmados aceptados,
- eventos sin firma rechazados,
- worker activo,
- cola sin fallos persistentes,
- snapshots y logs disponibles.

## No-Go

No avanzar si:

- falta cualquier secreto,
- observability/queue responden sin token,
- Lemon no firma como esperamos,
- el worker no puede llegar al ingest,
- se pierden eventos tras reinicio,
- no hay persistencia configurada para cola/logs en el proveedor.

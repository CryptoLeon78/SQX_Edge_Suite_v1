# Render Staging Launch Pack

Este runbook convierte el despliegue de staging en una secuencia auditable.

## Generar launch pack

```powershell
python backend\sqx-edge-relay\tools\render_staging_launch_pack.py
```

El resultado incluye:

- ruta del blueprint,
- SHA256 del blueprint,
- variables Render requeridas,
- comandos de operador,
- estado actual del staging gate,
- decision `GO` o `NO-GO`.

## Variables Render requeridas

Estas variables salen del blueprint staging:

- `SQX_LEMON_WEBHOOK_SECRET`
- `SQX_FULFILLMENT_RELAY_SECRET`
- `SQX_RELAY_OPERATOR_TOKEN`
- `SQX_LOCAL_INGEST_URL`
- `SQX_RELAY_WORKER_INTERVAL_SECONDS`
- `SQX_RELAY_WORKER_LIMIT`

Los secretos se configuran en Render. No se versionan en git.

## Comandos post-deploy

```powershell
python backend\sqx-edge-relay\tools\render_credentials_handshake.py
python backend\sqx-edge-relay\tools\render_staging_gate.py --use-latest-handshake --base-url https://tu-relay-staging.onrender.com
python backend\sqx-edge-relay\tools\render_staging_gate.py --use-latest-handshake --base-url https://tu-relay-staging.onrender.com --send-webhook
```

## Criterio para M26

Avanzar solo si:

- el launch pack existe,
- el blueprint SHA256 coincide,
- Render tiene los secretos configurados,
- el staging gate devuelve `GO`,
- no hay password de cuenta Render en ningun entorno operativo.

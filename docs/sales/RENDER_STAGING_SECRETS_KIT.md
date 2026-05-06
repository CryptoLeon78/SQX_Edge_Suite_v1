# Render Staging Secrets Kit

Este runbook prepara los valores sensibles para staging.

## Generar secretos

```powershell
python backend\sqx-edge-relay\tools\render_staging_secrets_kit.py --local-ingest-url https://tu-local-ingest-tunnel.example.com/api/fulfillment/relay-ingest
```

El comando genera un `.env` local en:

```text
backend/sqx-edge-relay/data/render_staging_secrets_kit
```

Esa carpeta esta ignorada por git.

## Valores que se pegan en Render

- `SQX_FULFILLMENT_RELAY_SECRET`
- `SQX_RELAY_OPERATOR_TOKEN`
- `SQX_LOCAL_INGEST_URL`
- `SQX_RELAY_WORKER_INTERVAL_SECONDS`
- `SQX_RELAY_WORKER_LIMIT`

## Valor que tambien debe coincidir con Lemon

- `SQX_LEMON_WEBHOOK_SECRET`

Ese valor se configura en Render y en el webhook de Lemon para que la firma sea verificable.

## Reglas

- No usar password de cuenta Render.
- No subir el `.env` generado.
- No pegar secretos en issues, commits o README.
- Rotar secretos staging antes de produccion.
- Repetir `render_staging_gate.py` despues de configurar Render.

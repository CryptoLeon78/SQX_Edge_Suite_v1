# Render Staging Purchase Drill

Este runbook prueba el camino de compra en staging antes de conectar checkout real.

## Requisitos

- Apply gate M31 en `GO`.
- Render staging desplegado.
- Backend local accesible desde `SQX_LOCAL_INGEST_URL`.
- `SQX_RELAY_OPERATOR_TOKEN` disponible localmente.
- `SQX_LEMON_WEBHOOK_SECRET` disponible localmente.

## Revision seca

```powershell
python backend\sqx-edge-relay\tools\render_staging_purchase_drill.py --use-latest-apply-gate --base-url https://tu-relay-staging.onrender.com
```

Debe quedar `NO-GO` porque no envia webhook ni ejecuta dispatch.

## Prueba completa

```powershell
python backend\sqx-edge-relay\tools\render_staging_purchase_drill.py --use-latest-apply-gate --base-url https://tu-relay-staging.onrender.com --send-webhook --dispatch
```

La herramienta recorre:

- `GET /relay/queue`
- `POST /relay/webhook/lemon`
- `GET /relay/queue`
- `POST /relay/dispatch`
- `GET /relay/queue`

## Criterio GO

- Apply gate M31 en `GO`.
- Webhook demo aceptado por Render.
- Cola remota accesible con token de operador.
- Dispatch ejecutado sin fallo.
- Evidencia JSON/Markdown generada en `backend/sqx-edge-relay/data/render_staging_purchase_drill`.

## Seguridad

Usa solo staging. No conectes el webhook real de Lemon Squeezy ni publiques enlaces de checkout hasta que esta prueba sea `GO`.

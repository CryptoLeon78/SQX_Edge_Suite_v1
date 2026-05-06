# SQX Edge Relay

Relay remoto para recibir webhooks de Lemon Squeezy, persistir cola propia y reenviar bundles firmados al ingest local de SQX Edge.

## Variables de entorno

- `SQX_LEMON_WEBHOOK_SECRET`: secreto del webhook de Lemon.
- `SQX_FULFILLMENT_RELAY_SECRET`: secreto compartido con el ingest local.
- `SQX_LOCAL_INGEST_URL`: URL del ingest local, por defecto `http://127.0.0.1:5050/api/fulfillment/relay-ingest`.

## Endpoints

- `GET /relay/health`
- `POST /relay/webhook/lemon`
- `GET /relay/queue`
- `GET /relay/queue/<name>`
- `POST /relay/dispatch`
- `POST /relay/requeue`

## Flujo

1. Lemon envia webhook al relay.
2. El relay verifica `X-Signature`.
3. Se normaliza el evento y se guarda un `relay_bundle_*.json` en cola.
4. El relay firma el bundle con `X-SQX-Relay-Signature`.
5. El relay lo envia al ingest local cuando el target esta disponible.

## Arranque rapido

```bat
run-web.bat
```

o:

```powershell
python api\server.py
```

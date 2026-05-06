# SQX Edge Relay

Relay remoto para recibir webhooks de Lemon Squeezy, persistir cola propia y reenviar bundles firmados al ingest local de SQX Edge.

## Variables de entorno

- `SQX_LEMON_WEBHOOK_SECRET`: secreto del webhook de Lemon.
- `SQX_FULFILLMENT_RELAY_SECRET`: secreto compartido con el ingest local.
- `SQX_RELAY_OPERATOR_TOKEN`: token para proteger endpoints operativos del relay.
- `SQX_LOCAL_INGEST_URL`: URL del ingest local, por defecto `http://127.0.0.1:5050/api/fulfillment/relay-ingest`.
- `SQX_RELAY_WORKER_INTERVAL_SECONDS`: segundos entre pasadas del worker, por defecto `30`.
- `SQX_RELAY_WORKER_LIMIT`: maximo de bundles por pasada, por defecto `10`.

Usa `.env.example` como plantilla. No subas `.env` real al repo.

## Endpoints

- `GET /relay/health`
- `GET /relay/config-check`
- `GET /relay/observability`
- `POST /relay/observability/snapshot`
- `POST /relay/webhook/lemon`
- `GET /relay/queue`
- `GET /relay/queue/<name>`
- `POST /relay/dispatch`
- `POST /relay/requeue`

Cuando `SQX_RELAY_OPERATOR_TOKEN` esta definido, los endpoints de cola, dispatch y requeue requieren:

```text
X-SQX-Operator-Token: <token>
```

Tambien se acepta:

```text
Authorization: Bearer <token>
```

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

## Preflight de despliegue

Antes de exponer el relay a compras reales:

```powershell
python tools\deployment_check.py
```

En produccion, con secretos reales:

```powershell
python tools\deployment_check.py --strict
```

El modo estricto exige `SQX_LEMON_WEBHOOK_SECRET`, `SQX_FULFILLMENT_RELAY_SECRET` y `SQX_RELAY_OPERATOR_TOKEN` configurados con valores largos y no placeholder.

## Staging smoke test

Con una URL de staging real:

```powershell
python tools\staging_smoke.py --base-url https://tu-relay-staging.example.com
```

Para enviar un evento demo firmado:

```powershell
python tools\staging_smoke.py --base-url https://tu-relay-staging.example.com --send-webhook
```

Usa `.env.staging.example` como lista de variables necesarias.

## Worker de dispatch

Una vez configurado `SQX_FULFILLMENT_RELAY_SECRET` y `SQX_LOCAL_INGEST_URL`, puedes lanzar el worker:

```bat
run-worker.bat
```

o una pasada unica:

```powershell
python worker\dispatch_worker.py --once
```

## Checklist antes de produccion

1. Configurar secretos reales, largos y distintos.
2. Proteger endpoints operativos con `SQX_RELAY_OPERATOR_TOKEN`.
3. Validar `GET /relay/config-check`.
4. Apuntar Lemon Squeezy a `POST /relay/webhook/lemon`.
5. Ejecutar worker como proceso supervisado.
6. Monitorizar `pending`, `failed` y logs del worker.

## Observabilidad

El relay escribe eventos JSONL en `data/observability/logs/relay_events.jsonl` y snapshots en `data/observability/snapshots`.

```powershell
python tools\simulate_purchase_flow.py
```

La simulacion recorre webhook firmado, cola, dispatch firmado y snapshot sin llamar a servicios externos.

## Despliegue

Ruta principal recomendada: Docker.

```powershell
docker build -f backend/sqx-edge-relay/Dockerfile -t sqx-edge-relay .
docker run --env-file backend/sqx-edge-relay/.env -p 6060:6060 sqx-edge-relay
```

Plantillas incluidas:

- `deploy/docker-compose.yml`
- `deploy/render.yaml.example`
- `deploy/railway.json`
- `deploy/fly.toml.example`
- `deploy/systemd/*.service`

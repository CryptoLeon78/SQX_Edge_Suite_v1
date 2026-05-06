# SQX Edge Relay Deployment Guide

## Recommended Path

Usa Docker como camino principal. El relay necesita dos procesos:

- `web`: recibe webhooks y expone health, cola y observabilidad.
- `worker`: reintenta dispatch hacia `SQX_LOCAL_INGEST_URL`.

Antes de desplegar:

```powershell
python backend\sqx-edge-relay\tools\deployment_check.py
```

En entorno real:

```powershell
python backend\sqx-edge-relay\tools\deployment_check.py --strict
```

## Required Secrets

- `SQX_LEMON_WEBHOOK_SECRET`
- `SQX_FULFILLMENT_RELAY_SECRET`
- `SQX_RELAY_OPERATOR_TOKEN`
- `SQX_LOCAL_INGEST_URL`

Usa valores largos, distintos y guardados en el panel de secretos del proveedor. Nunca los subas a GitHub.

## Local Docker Smoke Test

Desde la raiz del repo:

```powershell
docker build -f backend/sqx-edge-relay/Dockerfile -t sqx-edge-relay .
docker run --env-file backend/sqx-edge-relay/.env -p 6060:6060 sqx-edge-relay
```

Validaciones:

```powershell
curl http://127.0.0.1:6060/relay/health
curl http://127.0.0.1:6060/relay/config-check
```

## Render

Plantilla: `backend/sqx-edge-relay/deploy/render.yaml.example`.

Puntos importantes:

- Render permite servicios Docker desde repo.
- Define `healthCheckPath: /relay/health`.
- Configura secretos desde el dashboard, no en YAML.
- Usa un worker separado con `python worker/dispatch_worker.py`.
- Si necesitas preservar cola/logs entre despliegues, configura disco persistente.

## Railway

Plantilla: `backend/sqx-edge-relay/deploy/railway.json`.

Puntos importantes:

- Usa `RAILWAY_DOCKERFILE_PATH` o el `railway.json` para apuntar al Dockerfile.
- Define `healthcheckPath: /relay/health`.
- Configura variables desde Railway Variables.
- Crea otro servicio para el worker o usa un proceso separado supervisado.

## Fly.io

Plantilla: `backend/sqx-edge-relay/deploy/fly.toml.example`.

Puntos importantes:

- Usa `fly launch --no-deploy` para revisar config antes del primer deploy.
- Usa `fly secrets set` para secretos reales.
- Ajusta `app`, `primary_region` y `internal_port`.
- Para persistencia real de cola, usa volumen o almacenamiento externo.

## VPS / systemd

Plantillas:

- `backend/sqx-edge-relay/deploy/systemd/sqx-edge-relay.service`
- `backend/sqx-edge-relay/deploy/systemd/sqx-edge-relay-worker.service`
- `backend/sqx-edge-relay/deploy/systemd/sqx-edge-relay.env.example`

Ruta recomendada:

1. Crear usuario `sqxrelay`.
2. Copiar relay a `/opt/sqx-edge-relay`.
3. Crear venv e instalar `requirements.txt`.
4. Copiar env real a `/etc/sqx-edge-relay/sqx-edge-relay.env`.
5. Activar servicios web y worker.
6. Poner Nginx/Caddy delante con HTTPS.

## Go Live Checklist

1. `deployment_check.py --strict` en verde.
2. `/relay/health` responde 200.
3. `/relay/config-check` no muestra secretos faltantes.
4. `/relay/observability` protegido por token.
5. Worker activo y logs revisados.
6. Webhook test de Lemon encola un bundle.
7. Dispatch test llega al ingest local.
8. Snapshot creado tras la prueba.

## Rollback

- Desactivar webhook en Lemon Squeezy.
- Parar worker.
- Exportar `data/observability` y `data/queue`.
- Restaurar imagen/commit anterior.
- Rehabilitar webhook solo cuando `/relay/health` y `/relay/config-check` esten correctos.

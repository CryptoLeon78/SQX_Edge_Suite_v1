# Monetization M19 - Production Relay Deployment Package

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar el relay remoto para un despliegue real con un camino principal claro, checks previos y alternativas documentadas por proveedor.

## Entregables

- Estado `relay_production_deploy_ready`.
- `backend/sqx-edge-relay/Dockerfile`.
- `backend/sqx-edge-relay/.dockerignore`.
- `backend/sqx-edge-relay/tools/deployment_check.py`.
- `backend/sqx-edge-relay/deploy/docker-compose.yml`.
- `backend/sqx-edge-relay/deploy/render.yaml.example`.
- `backend/sqx-edge-relay/deploy/railway.json`.
- `backend/sqx-edge-relay/deploy/fly.toml.example`.
- `backend/sqx-edge-relay/deploy/systemd/sqx-edge-relay.service`.
- `backend/sqx-edge-relay/deploy/systemd/sqx-edge-relay-worker.service`.
- Guia `docs/sales/RELAY_DEPLOYMENT_GUIDE.md`.

## Decision

Docker queda como ruta principal. Render, Railway, Fly.io y VPS/systemd quedan como caminos soportados por plantilla, no como promesa de despliegue automatico sin revisar.

## Preflight

Antes de abrir ventas reales:

```powershell
python backend\sqx-edge-relay\tools\deployment_check.py --strict
```

Debe validar:

- archivos de despliegue presentes,
- Dockerfile listo para `gunicorn`,
- secretos reales, largos y no placeholder,
- `SQX_RELAY_OPERATOR_TOKEN` activo,
- health/config/observability paths documentados.

## Riesgos Controlados

- Los secretos no se versionan.
- El relay sigue fuera del ZIP portable del cliente.
- `backend/sqx-edge-relay/data/` queda ignorado para evitar subir logs y snapshots.
- La cola remota necesita persistencia si el proveedor puede reiniciar contenedores.

## Siguiente Paso

M20 deberia ser una fase de ensayo de produccion: elegir proveedor, configurar secretos reales de prueba, levantar relay staging, apuntar un webhook test y validar compra simulada contra el ingest local.

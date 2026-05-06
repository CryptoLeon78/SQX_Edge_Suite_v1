# Monetization M17 - Relay Deployment Hardening

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar el relay remoto para una puesta en produccion mas seria sin convertirlo todavia en una plataforma SaaS completa.

## Entregables

- Estado de automatizacion `relay_deployment_ready`.
- Endpoint `GET /relay/config-check`.
- Token operativo `SQX_RELAY_OPERATOR_TOKEN` para proteger cola, dispatch y requeue.
- Plantilla `backend/sqx-edge-relay/.env.example`.
- Worker `backend/sqx-edge-relay/worker/dispatch_worker.py`.
- Arranque rapido `run-worker.bat`.
- Documentacion operativa de readiness y worker.

## Decision

El relay queda como infraestructura separada y supervisable. Lemon Squeezy solo entra por `/relay/webhook/lemon`; las operaciones internas de cola se protegen con token; el dispatch puede ejecutarse por worker en modo `supervised_dispatch_loop`.

## Notas De Seguridad

- `SQX_LEMON_WEBHOOK_SECRET`, `SQX_FULFILLMENT_RELAY_SECRET` y `SQX_RELAY_OPERATOR_TOKEN` deben ser secretos distintos.
- `.env` real no debe ir al repo ni al ZIP portable.
- `GET /relay/config-check` permite validar preparacion sin exponer secretos.
- Los endpoints operativos aceptan `X-SQX-Operator-Token` o `Authorization: Bearer`.

## Siguiente Paso

M18 deberia centrarse en observabilidad: logs rotables, snapshot de cola, alertas simples y una prueba end-to-end simulando compra -> relay -> ingest local.

# Monetization M18 - Relay Observability And Simulation

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Dar visibilidad operativa al relay remoto y validar el flujo comercial sin depender de eventos reales de Lemon Squeezy.

## Entregables

- Estado de automatizacion `relay_observability_ready`.
- Eventos JSONL en `data/observability/logs/relay_events.jsonl`.
- Snapshots de cola en `data/observability/snapshots`.
- Endpoint `GET /relay/observability`.
- Endpoint `POST /relay/observability/snapshot`.
- Tool `backend/sqx-edge-relay/tools/simulate_purchase_flow.py`.
- Modo `jsonl_events_and_queue_snapshots`.

## Decision

El relay debe poder responder tres preguntas sin abrir archivos a mano:

1. Que ha pasado recientemente.
2. Como esta la cola ahora mismo.
3. Si el flujo webhook -> cola -> dispatch -> snapshot sigue funcionando.

## Seguridad

Los eventos redactan campos sensibles como `secret`, `signature`, `token` y `authorization`. Los endpoints de observabilidad quedan bajo el mismo `SQX_RELAY_OPERATOR_TOKEN` que cola, dispatch y requeue.

## Siguiente Paso

M19 deberia preparar una guia de despliegue real por proveedor: local VPS, Render/Railway/Fly.io o servidor propio, con variables, reverse proxy y supervisor.

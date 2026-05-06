# Monetization M20 - Relay Staging Validation Kit

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar una fase de staging real para validar el relay antes de abrir ventas con webhooks de Lemon Squeezy.

## Entregables

- Estado `relay_staging_ready`.
- Plantilla `backend/sqx-edge-relay/.env.staging.example`.
- Tool `backend/sqx-edge-relay/tools/staging_smoke.py`.
- Checklist `docs/sales/RELAY_STAGING_CHECKLIST.md`.
- Contratos y tests para smoke remoto firmado.

## Flujo Staging

1. Elegir proveedor.
2. Configurar secretos staging.
3. Desplegar relay web y worker.
4. Ejecutar `deployment_check.py --strict`.
5. Ejecutar `staging_smoke.py`.
6. Ejecutar `staging_smoke.py --send-webhook`.
7. Validar cola, observabilidad, snapshot y dispatch.
8. Activar webhook test de Lemon.

## Decision

M20 no fuerza un proveedor concreto. Deja el proyecto listo para conectar el proveedor elegido sin reescribir codigo.

## Go/No-Go

Go solo si:

- `/relay/health` responde 200.
- `/relay/config-check` no muestra secretos faltantes.
- `/relay/observability` exige token.
- `/relay/observability/snapshot` crea snapshot.
- evento demo firmado entra por `/relay/webhook/lemon`.
- el evento demo usa `wh_m20_staging_demo` para facilitar busqueda en logs.
- worker puede mover bundle a `sent`.

## Siguiente Paso

M21 deberia elegir proveedor y ejecutar staging real con URL publica, secretos de prueba, webhook Lemon test y evidencia de capturas/logs.

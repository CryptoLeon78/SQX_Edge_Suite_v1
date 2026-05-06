# Phase M16 - Deployable Remote Relay Service

Objetivo: convertir el relay en un servicio remoto real dentro del repo, con cola propia, health, dispatch y requeue, listo para desplegarse por separado del ZIP portable.

## Decision

- El estado contractual pasa a `remote_relay_ready`.
- El proyecto del relay vive en `backend/sqx-edge-relay`.
- El relay mantiene su propia cola remota con `pending`, `sent` y `failed`.
- El dispatch al ingest local usa `SQX_LOCAL_INGEST_URL`.
- La politica de retry del relay es `exponential_backoff_remote_queue`.

## Relay Endpoints

- `GET /relay/health`
- `POST /relay/webhook/lemon`
- `GET /relay/queue`
- `GET /relay/queue/<name>`
- `POST /relay/dispatch`
- `POST /relay/requeue`

## Runtime Shape

- Lemon entra por `POST /relay/webhook/lemon`.
- El relay valida `X-Signature`.
- Se genera un `relay_bundle_*.json` con `normalized_request`.
- El relay intenta enviar el bundle firmado a `/api/fulfillment/relay-ingest`.
- Si falla, lo mueve a `failed` con `next_attempt_at`.
- Si se corrige el problema, el operador o job remoto puede recolarlo y volver a despachar.

## Boundaries

- `backend/sqx-edge-relay` no viaja en el ZIP portable del cliente.
- El relay no contiene private keys de licencias.
- La licencia sigue emitiendose solo en el entorno privado del operador.

## Risks Still Open

- Falta desplegarlo en un host concreto.
- Falta scheduler/worker permanente para dispatch automatico continuo.
- Falta observabilidad externa mas rica si el volumen crece.

Estado: Done.

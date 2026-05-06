# Relay Service Operations

## Daily Checks

1. Revisar `GET /relay/health`.
2. Confirmar secretos configurados.
3. Vigilar volumen en `pending`, `sent` y `failed`.
4. Confirmar que `SQX_LOCAL_INGEST_URL` apunta al destino esperado.

## Dispatch Loop

- Usar `POST /relay/dispatch` para enviar un item concreto o varios `pending`.
- El relay firma cada bundle con `X-SQX-Relay-Signature`.
- El destino local debe responder `200` para considerar el envio correcto.

## Failure And Requeue

- Un fallo mueve el bundle a `failed`.
- El bundle registra `attempt_count`, `last_error` y `next_attempt_at`.
- Para reactivar un item, usar `POST /relay/requeue`.
- Despues se puede relanzar `POST /relay/dispatch`.

## Deployment Notes

- Desplegar este servicio separado del dashboard portable.
- Proteger los secretos en variables de entorno del host.
- Mantener logs por `relay_event_id` y `provider_event_id`.

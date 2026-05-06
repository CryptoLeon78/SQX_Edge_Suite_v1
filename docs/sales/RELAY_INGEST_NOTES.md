# Relay Ingest Notes

## Trusted Relay Flow

1. Recibir webhook de Lemon Squeezy en un endpoint publico controlado.
2. Verificar `X-Signature` con el secreto del webhook.
3. Crear bundle con `relay_event_id`, `provider_event_id`, payload y `normalized_request`.
4. Firmar el JSON del bundle con `X-SQX-Relay-Signature`.
5. Enviar el bundle a `POST /api/fulfillment/relay-ingest`.

## Security Notes

- Usar un secreto distinto para Lemon y para el relay.
- No guardar private keys de licencia en el relay.
- Registrar logs minimos: `relay_event_id`, fecha, `provider_event_id`, resultado.
- Si el POST local no devuelve `200`, dejar el evento en cola de reintentos del relay.

## Operational Advice

- Empezar con un relay muy pequeno y cerrado.
- Permitir solo los eventos comerciales necesarios.
- Mantener el bundle estable y versionado para no romper la cola local.

# SQX Edge Pro - Webhook Receiver Operations

## Receiver Daily Flow

1. Verificar que `SQX_LEMON_WEBHOOK_SECRET` esta definido.
2. Recibir o reenviar webhook al endpoint local.
3. Revisar `GET /api/fulfillment/requests`.
4. Procesar la request elegible.
5. Confirmar que existe un `delivery_receipt_*.json`.

## Duplicate Event Rule

- La clave de deduplicacion es `provider_event_id`.
- Si llega el mismo evento dos veces, no se crea una segunda request.
- Esto permite tolerar reintentos normales del proveedor.

## Operator Notes

- No procesar requests con `eligible_for_fulfillment = false` salvo revision manual.
- Mantener la private key fuera del repo y fuera del ZIP.
- Conservar receipts y requests hasta cerrar soporte o renovacion.

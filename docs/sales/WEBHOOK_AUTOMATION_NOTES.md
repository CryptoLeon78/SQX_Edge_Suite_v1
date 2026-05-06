# SQX Edge Pro - Webhook Automation Notes

## Current State

- Checkout: preparado.
- Licencia firmada: preparada.
- Entrega por cliente: preparada.
- Puente de automatizacion local: preparado.
- Endpoint publico: no activado.

## Manual To Assisted Automation

1. Exportar o capturar payload bruto del proveedor.
2. Guardarlo como `webhook_event_*.json`.
3. Ejecutar `fulfillment_request.py`.
4. Revisar `eligible_for_fulfillment`.
5. Ejecutar `fulfill_from_request.ps1`.

## Recommended Future M13+

- Receiver local o privado para webhooks.
- Carpeta/cola persistente para eventos y requests.
- Deduplicacion por `provider_event_id`.
- Registro de fulfillment completado.
- Reintento seguro para errores temporales.

## Event Rules

- `order_created`: candidato a fulfillment.
- `subscription_created`: candidato a fulfillment.
- `subscription_payment_success`: candidato a renovacion/fulfillment.
- `subscription_updated`: evento contable, no siempre entrega.
- `subscription_cancelled`: no emitir nueva licencia.
- `subscription_expired`: no emitir nueva licencia.

## Request Fields To Preserve

- `provider_event_id`
- `order_id`
- `customer_email`
- `plan`
- `provider_variant_id`
- `eligible_for_fulfillment`

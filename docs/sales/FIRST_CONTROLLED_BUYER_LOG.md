# First Controlled Buyer Operating Log And Post-Sale Review

Esta fase registra la primera venta controlada de forma operativa y sin ansiedad: compra, entrega, activacion, soporte, feedback y decision post-venta.

## Datos minimos

- Gate M66 de pagina/cadencia en `GO`.
- Referencia de pedido no sensible.
- Canal de venta y estado de pago.
- Entrega confirmada.
- Activacion de licencia revisada.
- Soporte abierto/cerrado y numero de incidencias abiertas.
- Feedback agregado sin mensajes crudos.
- Refunds y fallos de fulfillment.
- Decision: `continue_private_sales`, `iterate_onboarding`, `schedule_followup` o `pause_sales`.

## Comando base

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\first_controlled_buyer_log.py `
  --use-latest-public-page-cadence `
  --order-ref "order_0001" `
  --sale-channel "Lemon Squeezy private link" `
  --payment-status paid `
  --delivery-status delivered `
  --license-activation-status reviewed `
  --activation-events 1 `
  --open-support-items 0 `
  --refund-count 0 `
  --fulfillment-failures 0 `
  --first-value-status pending_followup `
  --decision schedule_followup `
  --feedback-summary "Buyer received the ZIP and license; first-value follow-up is scheduled." `
  --review-notes "Keep sales private until activation and first-value feedback are complete." `
  --confirm-public-page-cadence-go `
  --confirm-sale-recorded `
  --confirm-delivery-confirmed `
  --confirm-license-activation-reviewed `
  --confirm-support-reviewed `
  --confirm-feedback-reviewed `
  --confirm-safe-claims-reviewed `
  --confirm-post-sale-decision-recorded
```

## Decisiones

- `continue_private_sales`: continuar con enlace privado si no hay soporte abierto, refunds ni fallos.
- `iterate_onboarding`: mejorar pasos, FAQ o soporte antes de otra venta.
- `schedule_followup`: esperar confirmacion de primer valor sin pausar todo.
- `pause_sales`: detener ventas si falla entrega, activacion, soporte, refund o claims.

## Privacidad

No guardar emails completos, nombres de comprador, licencias firmadas, payloads de proveedor, claves ni mensajes crudos. Usa referencias operativas y resumen agregado.

# Template Pack 1 Add-On Sales Register

Este registro sirve para revisar ventas reales de Template Pack 1 sin exponer datos sensibles ni improvisar decisiones comerciales.

## Datos minimos

- Handoff M53 en `GO`.
- Buyer reference redactada o buyer id interno.
- Provider order id.
- Canal de venta y estado de pago.
- Importe y moneda.
- Estado de entrega del add-on.
- Estado de soporte, incidencias abiertas, refunds y fallos de fulfillment.
- Decision: `keep_tracking`, `scale_limited` o `pause_sales`.

## Comando base

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_1_sales_register.py `
  --use-latest-handoff `
  --buyer-email buyer@example.org `
  --provider-order-id order_live_001 `
  --sale-channel "Lemon Squeezy" `
  --sale-status paid `
  --amount 49.00 `
  --currency EUR `
  --delivery-status delivered `
  --support-status open `
  --sales-count 1 `
  --open-support-items 0 `
  --refund-count 0 `
  --fulfillment-failures 0 `
  --scale-decision keep_tracking `
  --register-notes "First add-on sale recorded; support window remains open." `
  --confirm-handoff-go `
  --confirm-sale-recorded `
  --confirm-delivery-status-recorded `
  --confirm-support-status-recorded `
  --confirm-safe-claims-reviewed `
  --confirm-scale-decision-recorded `
  --append-register
```

## Reglas de decision

- `keep_tracking`: decision por defecto mientras hay pocas ventas o soporte inicial abierto.
- `scale_limited`: solo con venta pagada, entrega confirmada, cero soporte abierto, cero refunds y cero fallos.
- `pause_sales`: usar si hay disputa, refund, entrega fallida, soporte sin resolver o dudas en claims.

## Privacidad

No pegues payloads crudos de Lemon Squeezy, Gumroad ni correos completos en notas. El gate redacta email, pero el operador debe mantener las notas sin datos personales innecesarios.

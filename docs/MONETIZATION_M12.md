# Phase M12 - Local Fulfillment Automation Bridge

Objetivo: preparar la automatizacion del fulfillment sin abrir aun un endpoint publico ni depender de credenciales en el repo.

## Decision

- El primer paso de automatizacion sera local y offline-friendly.
- Los eventos de checkout se normalizan a una `fulfillment request` interna antes de emitir la licencia.
- Lemon Squeezy queda como proveedor principal de webhook.
- La firma del webhook se valida con `X-Signature` usando `HMAC SHA256`.
- El flujo automatico se divide en dos herramientas:
  - `fulfillment_request.py`
  - `fulfill_from_request.ps1`

## Flow

1. Guardar el payload bruto del proveedor.
2. Verificar firma del webhook.
3. Normalizar a `fulfillment_request_*.json`.
4. Revisar `eligible_for_fulfillment`.
5. Ejecutar `fulfill_from_request.ps1`.
6. Generar licencia firmada y carpeta de entrega final.

## Initial Event Set

- `order_created`
- `subscription_created`
- `subscription_updated`
- `subscription_payment_success`
- `subscription_cancelled`
- `subscription_expired`

## Tools

### `fulfillment_request.py`

- Lee un payload bruto de Lemon Squeezy.
- Verifica firma si se aporta `--signature` y secreto.
- Resuelve `plan`, `duration`, `machine_limit` y elegibilidad.
- Escribe una request interna estable y procesable.

### `fulfill_from_request.ps1`

- Lee la request normalizada.
- Emite licencia con `license_issue.py`.
- Prepara entrega con `prepare_customer_delivery.ps1`.
- Añade una nota interna trazable con proveedor, evento y variant id.

## Example

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\fulfillment_request.py --payload C:\SQX_PRIVATE_KEYS\webhook_event_order_created.json --out C:\SQX_PRIVATE_KEYS\fulfillment_request_order_created.json --signature abc123 --secret-env LEMON_WEBHOOK_SECRET
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\fulfill_from_request.ps1 -RequestPath C:\SQX_PRIVATE_KEYS\fulfillment_request_order_created.json -PrivateKey C:\SQX_PRIVATE_KEYS\sqx-prod-2026-05-v1_private_key.json -ZipPath dist\SQX_Edge_Tool_Portable_YYYYMMDD_HHMMSS.zip -SupportEmail soporte@example.com
```

## Scope Boundary

- No endpoint publico aun.
- No credenciales reales en repo.
- No webhook receiver persistente aun.
- No reintentos automaticos ni panel operador todavia.

## Official References Checked

- Lemon Squeezy signing requests: https://docs.lemonsqueezy.com/help/webhooks/signing-requests
- Lemon Squeezy webhooks overview: https://docs.lemonsqueezy.com/help/webhooks
- Lemon Squeezy orders API object: https://docs.lemonsqueezy.com/api/orders/the-order-object
- Lemon Squeezy subscriptions API object: https://docs.lemonsqueezy.com/api/subscriptions/the-subscription-object

## Residual Risks

- Falta un receiver real para guardar eventos automaticamente.
- Aun no hay deduplicacion persistente por `provider_event_id`.
- La cola local esta pensada para operacion asistida, no para volumen alto.

Estado: Done.

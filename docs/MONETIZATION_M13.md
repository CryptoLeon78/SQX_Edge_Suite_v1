# Phase M13 - Private Receiver And Persistent Queue

Objetivo: pasar del puente local a un receiver privado usable por operador, con persistent queue y deduplication por evento.

## Decision

- El receiver vive en la API local bajo `/api/fulfillment/webhook/lemon`.
- El secreto del webhook se toma desde `SQX_LEMON_WEBHOOK_SECRET`.
- La cola persiste en `backend/sqx-edge-tool/fulfillment_requests`.
- La deduplicacion usa `provider_event_id`.
- El receiver no se considera publico; sigue siendo `local_private_operator_only`.
- El estado contractual de esta fase en el manifiesto es `private_receiver_ready`.

## Endpoints

- `POST /api/fulfillment/webhook/lemon`
- `GET /api/fulfillment/requests`
- `GET /api/fulfillment/requests/<filename>`
- `POST /api/fulfillment/process`

## Behavior

- Si falta secreto: no se acepta el webhook.
- Si la firma `X-Signature` es invalida: rechazo.
- Si el `provider_event_id` ya existe: se responde como duplicado sin reinsertar.
- Si el evento es nuevo: se guarda payload bruto y request normalizada.
- El operador puede procesar una request concreta y generar la entrega final.

## Persistence

- `events/`: payload bruto recibido.
- `requests/`: request lista para fulfillment.
- `processed/`: recibos de fulfillment completado.

## Official References Checked

- Lemon Squeezy signing requests: https://docs.lemonsqueezy.com/help/webhooks/signing-requests
- Lemon Squeezy webhooks overview: https://docs.lemonsqueezy.com/help/webhooks
- Lemon Squeezy order object: https://docs.lemonsqueezy.com/api/orders/the-order-object
- Lemon Squeezy subscription object: https://docs.lemonsqueezy.com/api/subscriptions/the-subscription-object

## Residual Risks

- Aun falta un servicio publico o tunel controlado para recibir webhooks reales desde internet.
- La cola persiste en disco, pero todavia no hay panel visual de operador.
- Falta una politica de reintentos y un estado de error mas fino por request.

Estado: Done.

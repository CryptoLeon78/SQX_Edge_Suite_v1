# Phase M14 - Operator States And Retry Cockpit

Objetivo: convertir la cola privada en un queue cockpit usable desde el dashboard interno, con operator_status, reintentos y trazabilidad por request.

## Decision

- El estado contractual del manifiesto pasa a `operator_retry_ready`.
- Cada request conserva `operator_status`, `attempt_count`, `last_attempt_at`, `last_error` y `processed_receipt_file`.
- El operador puede cambiar estado via `POST /api/fulfillment/request-status`.
- El dashboard muestra un queue cockpit en Inicio con resumen, refresh, ignore, requeue y process.
- El retry mode oficial de esta fase es `manual_retry_with_attempt_log`.

## Endpoints

- `GET /api/fulfillment/requests`
- `GET /api/fulfillment/requests/<filename>`
- `POST /api/fulfillment/process`
- `POST /api/fulfillment/request-status`

## Runtime Behavior

- Una request nueva entra como `queued` o `needs_review` segun `eligible_for_fulfillment`.
- Cada intento incrementa `attempt_count`.
- Un fallo no destruye la request: la deja en `failed` con `last_error`.
- Un operador puede marcar `ignored` o devolverla a `queued`.
- El request detail sigue siendo el source of truth; el panel del dashboard consume el resumen.

## Operator UI

- El panel vive en `Inicio`.
- Guarda localmente la ruta de private key, ZIP portable y soporte.
- Permite procesar desde el dashboard sin abrir scripts manualmente.
- Muestra hasta 8 requests recientes con badges, intentos y ultimo error.

## Risks Still Open

- El receiver sigue siendo privado/local; no hay aun relay remoto gestionado.
- La ruta de private key y ZIP vive en el navegador local, no en el backend.
- Falta una fase posterior de tunel seguro o receiver remoto controlado.

Estado: Done.

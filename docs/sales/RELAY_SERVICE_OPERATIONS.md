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

## Production Readiness

- Copiar `.env.example` como referencia y guardar el `.env` real fuera del repo.
- Configurar secretos largos y distintos: `SQX_LEMON_WEBHOOK_SECRET`, `SQX_FULFILLMENT_RELAY_SECRET` y `SQX_RELAY_OPERATOR_TOKEN`.
- Comprobar `GET /relay/config-check` antes de exponer el webhook.
- Proteger cola, detalle, dispatch y requeue con `X-SQX-Operator-Token` o `Authorization: Bearer`.
- Mantener el relay fuera del ZIP portable del cliente.

## Worker Operation

El worker permite enviar bundles pendientes sin operacion manual constante.

```powershell
python worker\dispatch_worker.py --once
```

Para modo continuo:

```bat
run-worker.bat
```

Variables relevantes:

- `SQX_RELAY_WORKER_INTERVAL_SECONDS`
- `SQX_RELAY_WORKER_LIMIT`
- `SQX_LOCAL_INGEST_URL`

El proceso debe ejecutarse supervisado por el host elegido. Si el ingest local no esta disponible, los bundles fallan con backoff y quedan trazados en `failed`.

## Observability

- `GET /relay/observability` devuelve resumen de cola, eventos recientes y rutas de logs.
- `POST /relay/observability/snapshot` escribe un snapshot JSON de cola, config y eventos recientes.
- Los eventos se guardan en `data/observability/logs/relay_events.jsonl`.
- Los snapshots se guardan en `data/observability/snapshots`.
- Los campos sensibles se redactan antes de escribir logs.

## Purchase Flow Simulation

Usa:

```powershell
python tools\simulate_purchase_flow.py
```

La simulacion crea un evento de compra firmado, lo encola, simula el ingest local, mueve el bundle a `sent` y genera un snapshot. Sirve como prueba rapida antes de tocar Lemon Squeezy real.

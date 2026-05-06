# Local Ingest Render Handoff

Este runbook prepara los valores finales que se pegaran en Render staging.

## Desde ultima sesion

```powershell
python backend\sqx-edge-relay\tools\local_ingest_render_handoff.py --use-latest-session
```

Por defecto exige que la sesion local sea `GO`.

## Desde URL explicita

```powershell
python backend\sqx-edge-relay\tools\local_ingest_render_handoff.py --ingest-url https://tu-tunnel.example.com/api/fulfillment/relay-ingest
```

## Validacion seca

```powershell
python backend\sqx-edge-relay\tools\local_ingest_render_handoff.py --ingest-url https://tu-tunnel.example.com/api/fulfillment/relay-ingest --validate --relay-secret <SQX_FULFILLMENT_RELAY_SECRET>
```

## Valores Render

El `.env` generado incluye:

```text
SQX_LOCAL_INGEST_URL=https://...
SQX_RELAY_WORKER_INTERVAL_SECONDS=30
SQX_RELAY_WORKER_LIMIT=10
```

Los secretos siguen saliendo de `render_staging_secrets_kit.py`.

## Despues de pegar en Render

Cuando Render staging ya tenga los valores anteriores, ejecuta el gate remoto:

```powershell
python backend\sqx-edge-relay\tools\render_staging_gate.py --use-latest-handshake --base-url https://tu-relay-staging.onrender.com
```

El handoff no sustituye ese gate: solo prepara la URL local y los ajustes de worker para que el relay pueda llamar al ingest local.

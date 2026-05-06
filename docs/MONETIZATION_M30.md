# Monetization M30 - Local Ingest Render Handoff

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar el paquete final de handoff entre la sesion local de ingest y Render staging.

## Entregables

- Estado `relay_local_ingest_render_handoff_ready`.
- Tool `backend/sqx-edge-relay/tools/local_ingest_render_handoff.py`.
- `.env` local con:
  - `SQX_LOCAL_INGEST_URL`
  - `SQX_RELAY_WORKER_INTERVAL_SECONDS`
  - `SQX_RELAY_WORKER_LIMIT`
- Evidencia JSON/Markdown en `backend/sqx-edge-relay/data/local_ingest_render_handoff`.
- Consumo de ultima sesion M29 o URL explicita.
- Guia `docs/sales/LOCAL_INGEST_RENDER_HANDOFF.md`.

## Decision

El handoff no debe guardar secretos de firma. Solo prepara valores no sensibles y la URL de ingest que Render necesita.

## Uso

```powershell
python backend\sqx-edge-relay\tools\local_ingest_render_handoff.py --use-latest-session
```

Con URL explicita:

```powershell
python backend\sqx-edge-relay\tools\local_ingest_render_handoff.py --ingest-url https://tu-tunnel.example.com/api/fulfillment/relay-ingest
```

## Siguiente Paso

M31 debe configurar Render staging con estos valores y ejecutar `render_staging_gate.py` contra la URL real de Render.

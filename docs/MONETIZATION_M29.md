# Monetization M29 - Local Ingest Staging Session

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Unificar las piezas de backend local, tunnel publico e ingest validation en una sesion operativa auditable.

## Entregables

- Estado `relay_local_ingest_staging_session_ready`.
- Tool `backend/sqx-edge-relay/tools/local_ingest_staging_session.py`.
- Arranque opt-in del backend local.
- Arranque opt-in del tunnel.
- Check firmado opcional del ingest.
- Evidencia local en `backend/sqx-edge-relay/data/local_ingest_staging_session`.
- Guia `docs/sales/LOCAL_INGEST_STAGING_SESSION.md`.

## Decision

La sesion no abre procesos por defecto. Para una prueba real hay que pedirlo expresamente con `--start-backend` y `--start-tunnel`.

## Uso

```powershell
python backend\sqx-edge-relay\tools\local_ingest_staging_session.py
```

Sesion real:

```powershell
python backend\sqx-edge-relay\tools\local_ingest_staging_session.py --start-backend --start-tunnel --relay-secret <SQX_FULFILLMENT_RELAY_SECRET> --send-bundle
```

## Siguiente Paso

M30 debe ejecutar la sesion real, capturar la URL publica de ingest y alimentar Render staging con esa URL.

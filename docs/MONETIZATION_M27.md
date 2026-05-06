# Monetization M27 - Local Ingest Tunnel Readiness

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Validar la URL publica/tunnel que Render usara como `SQX_LOCAL_INGEST_URL` para reenviar bundles firmados al backend local.

## Entregables

- Estado `relay_local_ingest_tunnel_check_ready`.
- Tool `backend/sqx-edge-relay/tools/local_ingest_tunnel_check.py`.
- Validacion de URL HTTPS y path `/api/fulfillment/relay-ingest`.
- Health check contra `/api/health`.
- Bundle demo firmado opcional con `--send-bundle`.
- Evidencia local en `backend/sqx-edge-relay/data/local_ingest_tunnel_check`.
- Guia `docs/sales/LOCAL_INGEST_TUNNEL_CHECK.md`.

## Decision

M27 no crea tunel por si solo. M27 prepara la validacion para que, cuando exista un tunnel real, sepamos si la URL se puede pegar en Render con confianza.

## Uso

```powershell
python backend\sqx-edge-relay\tools\local_ingest_tunnel_check.py --ingest-url https://tu-tunnel.example.com/api/fulfillment/relay-ingest --relay-secret <SQX_FULFILLMENT_RELAY_SECRET>
```

Con bundle firmado:

```powershell
python backend\sqx-edge-relay\tools\local_ingest_tunnel_check.py --ingest-url https://tu-tunnel.example.com/api/fulfillment/relay-ingest --relay-secret <SQX_FULFILLMENT_RELAY_SECRET> --send-bundle
```

## Siguiente Paso

M28 debe crear o configurar un tunnel real para el backend local, ejecutar este check con `--send-bundle` y usar esa URL en el secrets kit/Render.

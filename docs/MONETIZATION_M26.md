# Monetization M26 - Render Staging Secrets Kit

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar secretos fuertes para Render staging sin meter valores sensibles en git, ZIP portable ni documentacion publica.

## Entregables

- Estado `relay_render_staging_secrets_kit_ready`.
- Tool `backend/sqx-edge-relay/tools/render_staging_secrets_kit.py`.
- `.env` local generado en `backend/sqx-edge-relay/data/render_staging_secrets_kit`.
- Evidencia JSON/Markdown redactada.
- Validacion de placeholders, longitud minima y password de cuenta Render.
- Guia `docs/sales/RENDER_STAGING_SECRETS_KIT.md`.

## Decision

El siguiente desbloqueo real es tener secretos listos para pegar en Render y Lemon. La herramienta genera secretos staging, pero devuelve `NO-GO` si falta `SQX_LOCAL_INGEST_URL` real.

## Uso

```powershell
python backend\sqx-edge-relay\tools\render_staging_secrets_kit.py --local-ingest-url https://tu-local-ingest-tunnel.example.com/api/fulfillment/relay-ingest
```

Para forzar secretos nuevos:

```powershell
python backend\sqx-edge-relay\tools\render_staging_secrets_kit.py --fresh --local-ingest-url https://tu-local-ingest-tunnel.example.com/api/fulfillment/relay-ingest
```

## Siguiente Paso

M27 debe configurar estos valores en Render, ejecutar handshake con API key real y obtener la primera URL staging real.

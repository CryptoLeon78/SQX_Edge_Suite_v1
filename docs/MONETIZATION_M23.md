# Monetization M23 - Render Credential Handshake

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Convertir el paso hacia Render en un handshake seguro y auditable antes de crear servicios reales.

## Entregables

- Estado `relay_render_credentials_handshake_ready`.
- Tool `backend/sqx-edge-relay/tools/render_credentials_handshake.py`.
- Evidencia local en `backend/sqx-edge-relay/data/render_preflight_evidence`.
- Politica `api_key_only_no_account_password`.
- Guia `docs/sales/RENDER_CREDENTIAL_HANDSHAKE.md`.
- Tests para bloqueo sin credenciales, rechazo de password de cuenta y GO mockeado.

## Decision

Render se integra solo con `RENDER_API_KEY` y `RENDER_OWNER_ID`. No se acepta password de cuenta en variables de entorno, scripts, docs ni commits. Si aparecen `RENDER_PASSWORD` o `RENDER_ACCOUNT_PASSWORD`, el handshake devuelve `NO-GO`.

## Uso

```powershell
python backend\sqx-edge-relay\tools\render_credentials_handshake.py
```

Sin API key y owner ID reales, devuelve `NO-GO` con bloqueos esperados. Con credenciales reales, delega en `render_api_preflight.py`, valida acceso API y blueprint, y escribe evidencia JSON/Markdown local ignorada por git.

## Siguiente Paso

M24 deberia ejecutar el handshake con API key real, owner ID real y blueprint staging. Si devuelve `GO`, el siguiente paso real es crear el servicio staging en Render y ejecutar `staging_evidence.py` contra la URL resultante.

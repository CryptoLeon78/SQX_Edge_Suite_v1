# Render Credential Handshake

Este runbook prepara el primer contacto real con Render sin usar password de cuenta.

## Variables permitidas

- `RENDER_API_KEY`: API key de Render.
- `RENDER_OWNER_ID`: owner/workspace ID de Render.
- `SQX_RENDER_STAGING_BLUEPRINT`: blueprint staging a validar.

## Variables bloqueadas

- `RENDER_PASSWORD`
- `RENDER_ACCOUNT_PASSWORD`

Si cualquiera de esas variables existe, el resultado debe ser `NO-GO`.

## Comando

```powershell
python backend\sqx-edge-relay\tools\render_credentials_handshake.py
```

## Resultado esperado sin credenciales

- Decision: `NO-GO`.
- Bloqueos:
  - `render_api_key_missing`
  - `render_owner_id_missing`

## Resultado esperado con credenciales reales

- Decision: `GO`.
- `render_api_preflight.py` ejecutado.
- Blueprint validado por Render API.
- Evidencia JSON y Markdown en `backend/sqx-edge-relay/data/render_preflight_evidence`.

## Criterio para avanzar

Solo se pasa a deploy staging real si:

- el handshake devuelve `GO`,
- no hay placeholders,
- no hay password de cuenta en entorno,
- la evidencia queda guardada localmente,
- el blueprint validado corresponde al entorno staging.

# Render Staging Gate

Este runbook define la compuerta previa a conectar pagos o webhooks reales.

## Regla principal

La decision final debe ser `GO` solo si:

- `render_credentials_handshake.py` devuelve `GO`.
- Existe una URL staging real.
- `staging_evidence.py` valida la URL staging.
- El smoke remoto no falla.
- No hay password de cuenta Render en entorno.

## Comando basico

```powershell
python backend\sqx-edge-relay\tools\render_staging_gate.py
```

Sin credenciales ni URL real, el resultado correcto es `NO-GO`.

## Usar evidencia previa

```powershell
python backend\sqx-edge-relay\tools\render_staging_gate.py --use-latest-handshake
```

## Usar URL staging real

```powershell
python backend\sqx-edge-relay\tools\render_staging_gate.py --use-latest-handshake --base-url https://tu-relay-staging.onrender.com
```

## Activar webhook firmado demo

```powershell
python backend\sqx-edge-relay\tools\render_staging_gate.py --use-latest-handshake --base-url https://tu-relay-staging.onrender.com --send-webhook
```

## Evidencia

La compuerta escribe JSON y Markdown en:

```text
backend/sqx-edge-relay/data/render_staging_gate
```

Esta carpeta esta ignorada por git.

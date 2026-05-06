# Render Staging Apply Gate

Este runbook confirma la ultima milla antes de conectar checkout real.

## Paso 1 - Generar o localizar handoff

```powershell
python backend\sqx-edge-relay\tools\local_ingest_render_handoff.py --use-latest-session
```

El handoff debe contener:

```text
SQX_LOCAL_INGEST_URL=https://...
SQX_RELAY_WORKER_INTERVAL_SECONDS=30
SQX_RELAY_WORKER_LIMIT=10
```

## Paso 2 - Pegar valores en Render

Aplica esos valores en el servicio web y en el worker de Render staging. Los secretos siguen saliendo de `render_staging_secrets_kit.py`; no uses passwords de cuenta Render como credenciales tecnicas.

## Paso 3 - Ejecutar gate final

```powershell
python backend\sqx-edge-relay\tools\render_staging_apply_gate.py --use-latest-handoff --confirm-env-applied --use-latest-handshake --base-url https://tu-relay-staging.onrender.com
```

`--confirm-env-applied` significa que ya has verificado visualmente en Render que los valores estan configurados.

## Revision seca

```powershell
python backend\sqx-edge-relay\tools\render_staging_apply_gate.py --use-latest-handoff --skip-remote-gate
```

La revision seca debe quedar `NO-GO` porque no ejecuta `render_staging_gate.py`. Sirve para comprobar el handoff y el checklist sin tocar staging.

## Criterio GO

- Handoff M30 en `GO`.
- Valores Render confirmados.
- URL real de Render staging configurada.
- `render_staging_gate.py` remoto en `GO`.
- Webhook real todavia desconectado hasta completar la prueba staging de compra.

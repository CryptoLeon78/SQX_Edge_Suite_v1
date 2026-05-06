# Monetization M31 - Render Staging Apply Gate

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Convertir el handoff de M30 en una compuerta final para confirmar que Render staging ya tiene los valores aplicados y que el gate remoto devuelve `GO`.

## Entregables

- Estado `relay_render_staging_apply_gate_ready`.
- Tool `backend/sqx-edge-relay/tools/render_staging_apply_gate.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-relay/data/render_staging_apply_gate`.
- Consumo de ultimo handoff M30 o fichero explicito.
- Confirmacion manual obligatoria con `--confirm-env-applied`.
- Ejecucion del `render_staging_gate.py` remoto salvo bloqueo explicito con `--skip-remote-gate`.
- Guia `docs/sales/RENDER_STAGING_APPLY_GATE.md`.

## Decision

M31 no automatiza cambios en Render ni guarda secretos. La fase verifica la aplicacion manual de variables y exige un gate remoto `GO` antes de conectar checkout real.

## Uso

```powershell
python backend\sqx-edge-relay\tools\render_staging_apply_gate.py --use-latest-handoff --confirm-env-applied --use-latest-handshake --base-url https://tu-relay-staging.onrender.com
```

Para una revision seca sin llamadas remotas:

```powershell
python backend\sqx-edge-relay\tools\render_staging_apply_gate.py --use-latest-handoff --skip-remote-gate
```

## Siguiente Paso

M32 debe ejecutar la prueba de compra staging completa contra Render y el ingest local, con webhook demo firmado y trazabilidad de cola/dispatch.

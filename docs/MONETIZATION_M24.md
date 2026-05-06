# Monetization M24 - Render Staging Gate

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Anadir una compuerta operacional antes del despliegue vivo en Render: ninguna conexion comercial avanza sin handshake, URL staging y evidencia remota.

## Entregables

- Estado `relay_render_staging_gate_ready`.
- Tool `backend/sqx-edge-relay/tools/render_staging_gate.py`.
- Evidencia local en `backend/sqx-edge-relay/data/render_staging_gate`.
- Uso de `render_credentials_handshake.py` como requisito previo.
- Uso de `staging_evidence.py` cuando existe URL staging.
- Guia `docs/sales/RENDER_STAGING_GATE.md`.

## Decision

M24 no crea servicios en Render. M24 crea la disciplina de despliegue: primero `GO` de credenciales, despues servicio staging, despues smoke/evidencia remota, y solo entonces pagos/webhooks reales.

## Uso

```powershell
python backend\sqx-edge-relay\tools\render_staging_gate.py
```

Con una evidencia de handshake previa:

```powershell
python backend\sqx-edge-relay\tools\render_staging_gate.py --use-latest-handshake
```

Con URL staging:

```powershell
python backend\sqx-edge-relay\tools\render_staging_gate.py --use-latest-handshake --base-url https://tu-relay-staging.onrender.com
```

## Siguiente Paso

M25 deberia usar credenciales reales para obtener handshake `GO`, crear el servicio staging en Render y ejecutar esta compuerta contra la URL real.

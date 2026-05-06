# Monetization M25 - Render Staging Launch Pack

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar el paquete operativo para crear y validar staging en Render sin perder trazabilidad ni exponer secretos.

## Entregables

- Estado `relay_render_staging_launch_pack_ready`.
- Tool `backend/sqx-edge-relay/tools/render_staging_launch_pack.py`.
- SHA256 del blueprint staging.
- Extraccion de variables Render requeridas desde `render.staging.yaml.example`.
- Comandos de operador para handshake, gate y smoke con URL real.
- Evidencia local en `backend/sqx-edge-relay/data/render_staging_launch_pack`.
- Guia `docs/sales/RENDER_STAGING_LAUNCH_PACK.md`.

## Decision

M25 no despliega recursos. M25 prepara el paquete de lanzamiento para que M26 sea ejecucion real: credenciales reales, servicio staging en Render, URL real y gate final.

## Uso

```powershell
python backend\sqx-edge-relay\tools\render_staging_launch_pack.py
```

Con URL staging real:

```powershell
python backend\sqx-edge-relay\tools\render_staging_launch_pack.py --base-url https://tu-relay-staging.onrender.com
```

## Siguiente Paso

M26 debe ejecutar el launch pack con credenciales reales ya configuradas, crear el servicio staging en Render y obtener `GO` del staging gate contra la URL real.

# Monetization M28 - Local Ingest Tunnel Launcher

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar el lanzamiento controlado del tunel que dara a Render una URL publica hacia el backend local.

## Entregables

- Estado `relay_local_ingest_tunnel_launcher_ready`.
- Tool `backend/sqx-edge-relay/tools/local_ingest_tunnel_launcher.py`.
- Deteccion de proveedores:
  - `cloudflared`
  - `ngrok`
  - `npx localtunnel`
- Validacion de `http://127.0.0.1:5050/api/health`.
- Comandos de tunel sin arrancar por defecto.
- `--start` opt-in para lanzar tunel y parsear URL publica.
- Guia `docs/sales/LOCAL_INGEST_TUNNEL_LAUNCHER.md`.

## Decision

M28 evita automatizar a ciegas. Primero detecta proveedor y backend local. Solo con `--start` intenta abrir tunel. La URL publica resultante se pasa despues a `local_ingest_tunnel_check.py`.

## Uso

```powershell
python backend\sqx-edge-relay\tools\local_ingest_tunnel_launcher.py
```

Lanzamiento:

```powershell
python backend\sqx-edge-relay\tools\local_ingest_tunnel_launcher.py --start
```

## Siguiente Paso

M29 debe ejecutar el launcher con un proveedor real instalado, obtener URL publica, validar con `local_ingest_tunnel_check.py --send-bundle` y actualizar el secrets kit con la URL final.

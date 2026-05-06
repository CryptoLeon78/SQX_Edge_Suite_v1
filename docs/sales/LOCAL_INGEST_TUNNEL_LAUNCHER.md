# Local Ingest Tunnel Launcher

Este runbook prepara una URL publica temporal para que Render pueda llegar al backend local.

## Backend local

Primero arranca SQX Edge local:

```powershell
backend\sqx-edge-tool\run-web.bat
```

Health esperado:

```text
http://127.0.0.1:5050/api/health
```

## Detectar proveedor

```powershell
python backend\sqx-edge-relay\tools\local_ingest_tunnel_launcher.py
```

Proveedores soportados:

- `cloudflared`
- `ngrok`
- `npx localtunnel`

## Lanzar tunel

```powershell
python backend\sqx-edge-relay\tools\local_ingest_tunnel_launcher.py --start
```

Si detecta URL publica, el reporte calcula:

```text
https://.../api/fulfillment/relay-ingest
```

## Validar URL generada

```powershell
python backend\sqx-edge-relay\tools\local_ingest_tunnel_check.py --ingest-url https://TU_URL_PUBLICA/api/fulfillment/relay-ingest --relay-secret <SQX_FULFILLMENT_RELAY_SECRET> --send-bundle
```

## Reglas

- Mantener el proceso de tunel abierto mientras se prueba staging.
- No usar URL antigua despues de reiniciar el tunel.
- No pegar secretos en consola compartida o commits.

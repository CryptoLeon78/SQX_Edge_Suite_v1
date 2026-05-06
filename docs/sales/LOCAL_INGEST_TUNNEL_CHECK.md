# Local Ingest Tunnel Check

Este runbook valida la URL que Render usara para enviar bundles firmados al backend local.

## Requisitos

- Backend local SQX corriendo.
- URL publica/tunnel apuntando al backend local.
- `SQX_FULFILLMENT_RELAY_SECRET` igual al que se pegara en Render.

## Check seco

```powershell
python backend\sqx-edge-relay\tools\local_ingest_tunnel_check.py --ingest-url https://tu-tunnel.example.com/api/fulfillment/relay-ingest --relay-secret <SQX_FULFILLMENT_RELAY_SECRET>
```

Este modo valida URL y `/api/health`, pero no envia bundle.

## Check firmado

```powershell
python backend\sqx-edge-relay\tools\local_ingest_tunnel_check.py --ingest-url https://tu-tunnel.example.com/api/fulfillment/relay-ingest --relay-secret <SQX_FULFILLMENT_RELAY_SECRET> --send-bundle
```

Este modo envia un bundle demo firmado. Usarlo solo cuando aceptes que se cree una request demo en la cola local.

## Evidencia

La evidencia se escribe en:

```text
backend/sqx-edge-relay/data/local_ingest_tunnel_check
```

## Criterio GO

- URL no placeholder.
- URL HTTPS, salvo pruebas locales con localhost.
- Health remoto responde OK.
- Si se usa `--send-bundle`, el ingest firmado responde OK.

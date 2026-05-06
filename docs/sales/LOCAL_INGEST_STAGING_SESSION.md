# Local Ingest Staging Session

Este runbook une backend local, tunnel e ingest check.

## Dry run

```powershell
python backend\sqx-edge-relay\tools\local_ingest_staging_session.py
```

No abre procesos persistentes.

## Sesion real

```powershell
python backend\sqx-edge-relay\tools\local_ingest_staging_session.py --start-backend --start-tunnel --relay-secret <SQX_FULFILLMENT_RELAY_SECRET> --send-bundle
```

La sesion:

- arranca backend local si no responde,
- lanza tunnel si hay proveedor disponible,
- detecta URL publica,
- calcula `/api/fulfillment/relay-ingest`,
- valida con bundle firmado si se usa `--send-bundle`.

## Resultado esperado

Un reporte `GO` incluye:

- health local OK,
- URL publica detectada,
- ingest URL calculada,
- check firmado OK.

## Despues

Copiar la URL de ingest a `SQX_LOCAL_INGEST_URL` en Render staging y mantener backend/tunnel vivos mientras duren las pruebas.

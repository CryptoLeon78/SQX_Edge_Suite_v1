# Commercial Release Candidate

Este runbook crea la compuerta final antes de una compra piloto real.

## Requisitos

- `checkout_live_readiness.py` en `GO`.
- ZIP portable generado con `release_checklist.ps1`.
- `ZIP SHA256` registrado.
- Clave publica de produccion real, sin placeholder.
- Checkout privado o enlace de test controlado.
- Rollback claro antes de tocar venta publica.

## Ejecutar RC

```powershell
python backend\sqx-edge-tool\tools\commercial_release_candidate.py --use-latest-readiness --zip dist\SQX_Edge_Tool_Portable_YYYYMMDD_HHMMSS.zip --pilot-purchase-confirmed
```

## Bloqueos esperados ahora

Es normal ver `NO-GO` hasta completar:

- `primary_checkout_url_missing_or_not_https`
- `checkout_live_readiness_not_go`
- `production_public_key_placeholder`
- `pilot_purchase_not_confirmed`

## pilot purchase

La compra piloto debe verificar:

- Pago privado o enlace limitado.
- Webhook Lemon recibido por Render.
- Dispatch hacia ingest local.
- Licencia Pro emitida o confirmada.
- ZIP portable abre correctamente.
- Licencia importada desbloquea funciones Pro.
- Cliente piloto recibe instrucciones y soporte.

## Rollback

Si algo falla:

- Despublica checkout links.
- Pausa webhook Lemon.
- Pausa worker Render.
- Vuelve a entrega manual firmada.
- Rota secretos si hubo exposicion.
- Entrega manualmente al cliente piloto si ya pago.

No abras venta publica hasta que esta RC devuelva `GO`.

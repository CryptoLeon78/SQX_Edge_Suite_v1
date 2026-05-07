# Template Pack 2 Controlled Publication

## Objetivo

Preparar la publicacion controlada de Template Pack 2 con checkout real, soporte, rollback y purchase drill antes de escalar ventas.

## Valores requeridos

- `SQX_TEMPLATE_PACK_2_CHECKOUT_URL`
- `SQX_TEMPLATE_PACK_2_PROVIDER_VARIANT_ID`
- `SQX_TEMPLATE_PACK_2_SUPPORT_EMAIL`
- `SQX_TEMPLATE_PACK_2_FALLBACK_URL` opcional

## Criterios GO

- Offer pack revisado.
- URL HTTPS real probada.
- Variant ID real confirmado.
- Inbox de soporte operativo.
- Macro de entrega preparada.
- Rollback listo.
- Purchase drill listo.
- Publicacion controlada aprobada.

## Purchase drill

- Confirmar que el checkout corresponde a `template_pack_2`.
- Confirmar precio `79 EUR`.
- Registrar compra pagada con referencia redacted.
- Generar ZIP add-on separado.
- Enviar macro de entrega.
- Confirmar ruta de reembolso o pausa.

## Comando recomendado

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_2_publication.py `
  --checkout-url "https://checkout.tu-proveedor.com/template-pack-2" `
  --provider-variant-id "variant_template_pack_2" `
  --support-email "soporte@tu-dominio.com" `
  --confirm-offer-pack-reviewed `
  --confirm-checkout-url-tested `
  --confirm-provider-variant-confirmed `
  --confirm-support-inbox-ready `
  --confirm-delivery-macro-ready `
  --confirm-rollback-ready `
  --confirm-purchase-drill-ready `
  --confirm-controlled-publication-approved `
  --no-write
```

Usar `--apply` solo cuando los valores sean definitivos y se quiera escribirlos en el manifest local.

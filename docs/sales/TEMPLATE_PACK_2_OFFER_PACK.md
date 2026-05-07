# Template Pack 2 Offer Pack

## Objetivo

Preparar la venta controlada del add-on Template Pack 2 sin activar todavia checkout real ni credenciales.

## Activos publicos

- `resources/pro-template-pack-2/offer/public_offer.md`
- `resources/pro-template-pack-2/offer/faq.md`
- `resources/pro-template-pack-2/offer/checkout_wiring.md`
- `resources/pro-template-pack-2/offer/delivery_email_macro.md`
- `resources/pro-template-pack-2/offer/support_macro.md`

## Checkout

- Proveedor principal: Lemon Squeezy.
- Fallback: Gumroad.
- Plan: `template_pack_2`.
- Precio: `79 EUR`.
- Modo: `one_time_addon`.
- Estado: draft listo para conectar URL y variant ID reales.

## Criterios GO

- Template Pack 2 assets listos.
- Copy y FAQ revisados.
- Draft de checkout preparado.
- Macro de entrega preparada.
- Macro de soporte preparada.
- Claims seguros revisados.

## Criterios NO-GO

- Falta plan `template_pack_2`.
- Falta precio o no coincide con `79 EUR`.
- Falta URL real para publicacion abierta.
- Falta soporte.
- Hay claims no permitidos.

## Comando recomendado

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_2_offer_pack.py `
  --confirm-template-pack-2-assets-ready `
  --confirm-offer-copy-reviewed `
  --confirm-faq-reviewed `
  --confirm-checkout-draft-ready `
  --confirm-delivery-macro-ready `
  --confirm-support-macro-ready `
  --confirm-safe-claims-reviewed
```

Para una publicacion abierta, repetir con `--require-live-checkout` y valores reales de checkout.

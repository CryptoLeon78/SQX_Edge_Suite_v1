# Template Pack 1 Public Offer

## Objetivo

Preparar la venta del add-on Template Pack 1 sin tocar todavia checkout real ni credenciales.

## Activos publicos

- `resources/pro-template-pack-1/offer/public_offer.md`
- `resources/pro-template-pack-1/offer/faq.md`
- `resources/pro-template-pack-1/offer/checkout_wiring.md`
- `resources/pro-template-pack-1/offer/delivery_email_macro.md`
- `resources/pro-template-pack-1/offer/support_macro.md`

## Checkout

- Proveedor principal: Lemon Squeezy.
- Fallback: Gumroad.
- Plan: `template_pack_1`.
- Precio: `49 EUR`.
- Modo: `one_time_addon`.
- Estado: draft listo para conectar URL y variant ID reales.

## Criterios GO

- Template Pack 1 delivery listo.
- Copy y FAQ revisados.
- Draft de checkout preparado.
- Macro de entrega preparada.
- Macro de soporte preparada.
- Claims seguros revisados.

## Criterios NO-GO

- Falta plan `template_pack_1`.
- Falta precio o no coincide con `49 EUR`.
- Falta URL real para publicacion abierta.
- Falta soporte.
- Hay claims prohibidos.

## Comando recomendado

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_1_offer.py `
  --confirm-template-pack-delivery-ready `
  --confirm-offer-copy-reviewed `
  --confirm-faq-reviewed `
  --confirm-checkout-draft-ready `
  --confirm-delivery-macro-ready `
  --confirm-support-macro-ready `
  --confirm-safe-claims-reviewed
```

Para una publicacion abierta, repetir con `--require-live-checkout` y valores reales de checkout.

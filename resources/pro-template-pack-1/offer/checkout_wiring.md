# Template Pack 1 - Checkout Wiring

## Estado

Draft listo para conectar a Lemon Squeezy o Gumroad.

## Variante

- Plan: `template_pack_1`
- Precio: `49 EUR`
- Tipo: `one_time_addon`
- Entrega: ZIP add-on separado

## Campos a completar antes de publicacion

- `providerVariantId`
- `checkoutUrl`
- `supportEmail`

## Flujo

1. Pago confirmado.
2. Ejecutar `template_pack_1_delivery.py`.
3. Adjuntar ZIP del pack.
4. Enviar macro de entrega.
5. Registrar evidencia local.

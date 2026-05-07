# Monetization M59 - Template Pack 2 Offer Pack

Estado: Done.

## Resultado

M59 prepara la venta controlada de Template Pack 2 como add-on separado para usuarios Pro.

## Entregables

- Config: `backend/sqx-edge-tool/config/template_pack_2_offer_pack.json`.
- Tool: `backend/sqx-edge-tool/tools/template_pack_2_offer_pack.py`.
- Resource dir: `resources/pro-template-pack-2/offer`.
- Sales doc: `docs/sales/TEMPLATE_PACK_2_OFFER_PACK.md`.
- Manifest state: `template_pack_2_offer_pack_ready`.

## Alcance

- Copy publico/controlado.
- FAQ de comprador.
- Draft de checkout.
- Macro de entrega.
- Macro de soporte.
- Gate de safe claims y checkout wiring.

## Politica

Template Pack 2 sigue siendo un add-on separado. El checkout queda en modo draft hasta completar URL, variant ID y soporte reales. No se guardan credenciales ni payloads de proveedor.

## Siguiente paso recomendado

M60 - preparar publicacion controlada de Template Pack 2 con URL real, soporte, rollback y purchase drill.

# Monetization Phase M50 - Template Pack 1 Public Add-On Offer And Checkout Wiring

Fecha: 2026-05-07.
Estado: Done.

## Objetivo

Preparar la oferta publica de Template Pack 1 como add-on, con copy revisado, FAQ, wiring de checkout, macro de entrega y soporte responsable.

## Entregables

- Estado `template_pack_1_public_offer_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_1_offer.json`.
- Recursos de oferta en `resources/pro-template-pack-1/offer`.
- Guia interna `docs/sales/TEMPLATE_PACK_1_PUBLIC_OFFER.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_1_offer.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_1_offer`.

## Decision

La oferta queda preparada en modo draft: el plan, precio, copy, FAQ y macros estan listos; URLs y variant IDs reales deben completarse antes de publicacion abierta.

## Criterios

- No publicar sin checkout real, soporte y macro revisados.
- No entregar sin pasar por `template_pack_1_delivery.py`.
- No mezclar el ZIP add-on dentro del ZIP base.
- Mantener claims centrados en productividad, orden y trazabilidad.

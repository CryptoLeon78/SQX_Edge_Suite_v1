# M52 - Template Pack 1 Controlled Purchase Drill

## Objetivo

Preparar y validar una compra controlada real de Template Pack 1 antes de escalar la publicacion del add-on.

## Entregables

- Configuracion `backend/sqx-edge-tool/config/template_pack_1_purchase_drill.json`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_1_purchase_drill.py`.
- Guia operativa `docs/sales/TEMPLATE_PACK_1_PURCHASE_DRILL.md`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_1_purchase_drill`.
- Manifiesto preparado con estado `template_pack_1_purchase_drill_ready`.

## Decision

La fase no inventa una compra real. El gate exige URL de checkout, provider variant ID, order ID, email de comprador, estado de pago, importe, moneda, confirmaciones de entrega/soporte y, si se pide, verificacion del ZIP add-on separado.

Politica de privacidad: `store_redacted_buyer_email_and_order_reference_only`.

Estado: Done.

## Siguiente Paso

M53: ejecutar el primer handoff real posterior a compra, con seguimiento de entrega, soporte y decision de escalar o pausar.

# M51 - Template Pack 1 Live Checkout Gate

## Objetivo

Preparar la publicacion controlada de Template Pack 1 con valores reales de checkout sin inventar datos de proveedor ni publicar un enlace falso.

## Entregables

- Configuracion `backend/sqx-edge-tool/config/template_pack_1_publication.json`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_1_publication.py`.
- Guia operativa `docs/sales/TEMPLATE_PACK_1_LIVE_CHECKOUT_PUBLICATION.md`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_1_publication`.
- Manifiesto preparado con estado `template_pack_1_live_checkout_gate_ready`.

## Decision

La aplicacion queda lista para aplicar URL real, provider variant ID y email de soporte cuando existan. El gate acepta valores por CLI o variables de entorno, valida HTTPS, placeholders, soporte y confirmaciones operativas, y puede aplicar los cambios al manifiesto solo con `--apply`.

Estado: Done.

## Siguiente Paso

M52: ejecutar una compra controlada real del add-on, registrar evidencia de pedido, entrega separada del ZIP y soporte inicial antes de ampliar la publicacion.

# M54 - Template Pack 1 Add-On Sales Register

Objetivo: consolidar un registro interno de ventas de Template Pack 1 antes de abrir mas trafico publico.

## Entregables

- Estado `template_pack_1_sales_register_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_1_sales_register.json`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_1_sales_register.py`.
- Guia operativa `docs/sales/TEMPLATE_PACK_1_SALES_REGISTER.md`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_1_sales_register`.
- Manifiesto preparado con politica de registro redactado y decision de escala.

## Decision

El registro de ventas no guarda emails en claro ni payloads crudos del proveedor. Solo conserva referencia redactada del comprador, order id, canal, importe, estado de entrega, soporte, refunds, fallos de fulfillment y decision operativa.

Politica de privacidad: `store_redacted_buyer_reference_order_status_support_metrics_and_scale_decision_only`.

`scale_limited` exige venta pagada, add-on entregado, cero soporte abierto, cero refunds y cero fallos de fulfillment. Si hay dudas, la decision responsable es `keep_tracking` o `pause_sales`.

Estado: Done.

Siguiente paso recomendado: M55, revisar cohorte de compradores del add-on y feedback real antes de ampliar trafico o crear Template Pack 2.

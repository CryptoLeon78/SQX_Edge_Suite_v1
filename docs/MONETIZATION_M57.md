# M57 - Template Pack 2 Initial Specs

Objetivo: ejecutar el plan M56 cuando la ruta elegida es Template Pack 2, definiendo alcance, activos, presets, soporte, entrega y siguiente fase antes de crear recursos comerciales.

## Entregables

- Estado `template_pack_2_specs_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_2_specs.json`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_2_specs.py`.
- Guia operativa `docs/sales/TEMPLATE_PACK_2_SPECS.md`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_2_specs`.
- Manifiesto preparado con politica de especificacion redactada para Pack 2.

## Decision

Template Pack 2 no se construye todavia como producto entregable. Primero queda definido como especificacion trazable derivada de feedback agregado y del action plan M56.

Politica de privacidad: `store_redacted_pack_2_scope_assets_support_delivery_and_next_phase_only`.

`draft_pack_2_assets` exige action plan GO, feedback mapeado, familias de activos, presets, soporte, entrega y cero riesgo de claims. Si Pack 1 necesita correccion previa se usa `iterate_pack_1_first`; si hay riesgo operativo se usa `pause_pack_2`.

Estado: Done.

Siguiente paso recomendado: M58, crear los recursos iniciales de Template Pack 2 o ejecutar la alternativa indicada por la especificacion.

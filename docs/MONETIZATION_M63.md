# M63 - Template Pack 2 Sales Register

## Objective

Prepare a redacted Template Pack 2 sales register for early buyer tracking before opening more traffic.

## Implemented

- Added `backend/sqx-edge-tool/config/template_pack_2_sales_register.json`.
- Added `backend/sqx-edge-tool/tools/template_pack_2_sales_register.py`.
- Added `docs/sales/TEMPLATE_PACK_2_SALES_REGISTER.md`.
- Added portable exclusions for sales-register evidence and internal tooling.
- Updated product manifest, roadmap, governance and static/contracts tests.

## Decision

Estado: Done.

Current state: `template_pack_2_sales_register_ready`.

Allowed register decisions: `keep_tracking`, `scale_limited` or `pause_sales`.

## Next Step

M64 - Template Pack 2 feedback cohort review and buyer signal quality.

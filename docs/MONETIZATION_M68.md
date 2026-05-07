# M68 - Post-Sale Improvement Loop

## Objective

Prepare a small post-sale improvement loop that turns first controlled buyer evidence into onboarding, support macro and public copy improvements before adding sales pressure.

## Implemented

- Added `backend/sqx-edge-tool/config/post_sale_improvement_loop.json`.
- Added `backend/sqx-edge-tool/tools/post_sale_improvement_loop.py`.
- Added `docs/sales/POST_SALE_IMPROVEMENT_LOOP.md`.
- Added portable exclusions for post-sale improvement evidence and internal tooling.
- Updated product manifest, roadmap, governance and static/contracts tests.

## Decision

Estado: Done.

Current state: `post_sale_improvement_loop_ready`.

Allowed improvement decisions: `ship_micro_updates`, `revise_onboarding`, `revise_support_macros`, `revise_public_copy` or `pause_sales`.

## Next Step

M69 - Apply the approved micro-updates to buyer onboarding, support macros and public copy, then prepare the next controlled buyer readiness check.

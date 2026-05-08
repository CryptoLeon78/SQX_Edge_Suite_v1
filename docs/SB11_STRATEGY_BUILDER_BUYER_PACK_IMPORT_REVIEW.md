# SB11 Strategy Builder Buyer Handoff Pack Import and Review

Phase SB11 lets Strategy Builder import the unified buyer handoff pack created in SB10 and convert it into a local review surface.

## Scope

- Add `buyerHandoffPackReview` to `app/js/modules/strategy-builder-core.js`.
- Extend `validateImportPayload` and `importPayload` to accept `sqx-edge.strategy-builder-buyer-handoff-pack`.
- Rebuild the nested Strategy Builder package through the same import pipeline used for normal packages.
- Force fresh operator review unless the caller explicitly passes an operator-reviewed option.
- Render a `sqx-edge.strategy-builder-buyer-handoff-pack-review` preview after import.
- Add a visible session audit entry named `Buyer Pack Import Review`.

## Guardrails

- No backend endpoint.
- No API call.
- No hidden localStorage write.
- No destination action is triggered.
- No Project Generator preset save.
- No SQX Views template save.
- No Strategy Cleaner folder scan.
- No `.sqx` file mutation.
- Imported buyer packs are review-only until the operator confirms manual review.

## Runtime Boundary

The existing `Importar JSON` control remains the entry point. If the JSON is a buyer handoff pack, the app validates the nested package and handoff coverage, rebuilds a blocked review package and shows the buyer pack review object in the preview panel.

The import does not jump to Project Generator, SQX Views or Strategy Cleaner. The operator must still execute every destination manually.

## Verification

- JS contracts assert buyer pack validation, review generation, forced re-review and UI import status.
- Static dashboard tests assert SB11 documentation, public contracts and roadmap alignment.
- E2E smoke imports a generated buyer pack and verifies preview-only behavior, session audit trace and no destination persistence.

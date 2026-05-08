# SB12 Strategy Builder Guided Buyer Session Checklist

Phase SB12 adds a preview-only checklist for running a buyer setup session from a Strategy Builder package, unified buyer pack or imported buyer pack review.

## Scope

- Add `guidedBuyerSessionChecklist` to `app/js/modules/strategy-builder-core.js`.
- Add `prepareBuyerSessionChecklist` to `app/js/modules/strategy-builder.js`.
- Add `Guia sesion comprador` to the Strategy Builder tab.
- Generate a `sqx-edge.strategy-builder-buyer-session-checklist` preview with:
  - manual review gate,
  - Project Generator prefill,
  - manual custom generation,
  - Project Generator preset draft,
  - SQX Views review,
  - Strategy Cleaner draft,
  - StrategyQuant validation.
- Use the latest package, buyer pack or buyer pack import review as source.
- Add a visible session audit entry named `Buyer Session Checklist`.

## Guardrails

- No backend endpoint.
- No API call.
- No hidden localStorage write.
- No destination action is triggered.
- No Project Generator generation.
- No Project Generator preset save.
- No SQX Views template save.
- No Strategy Cleaner folder scan.
- No `.sqx` file mutation.
- No profitability claim.
- The operator executes every step manually.

## Runtime Boundary

The checklist is an operator guide, not an execution engine. If the source is an imported buyer pack review that still requires manual review, destination steps are blocked until review is confirmed. If the source package is exportable, destination steps remain pending manual actions.

The checklist stays in the Strategy Builder preview and session audit only.

## Verification

- JS contracts assert checklist shape, review-required behavior, manual guardrails and UI preview behavior.
- Static dashboard tests assert SB12 documentation, runtime contracts and visible button.
- E2E smoke prepares a checklist from an imported buyer pack review and verifies no destination persistence.

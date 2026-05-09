# SB17 Strategy Builder Buyer Session Evidence Handoff Index

Phase SB17 adds a local evidence index for buyer Strategy Builder sessions. The goal is to show, in one reduced artifact, which handoff pieces exist before support, delivery or buyer review continues.

## Scope

- Add `handoffEvidenceIndex` to `app/js/modules/strategy-builder-core.js`.
- Add `prepareEvidenceHandoffIndex` to `app/js/modules/strategy-builder.js`.
- Add `Indice evidencia` to the Strategy Builder tab.
- Generate a `sqx-edge.strategy-builder-evidence-handoff-index` JSON artifact with:
  - package identity,
  - buyer handoff pack status,
  - Project Generator prefill and preset draft status,
  - SQX Views handoff status,
  - Strategy Cleaner draft status,
  - buyer session checklist status,
  - optional summary, printable notes, support case and support resolution status,
  - missing required handoffs,
  - privacy boundary and guardrails.
- Use reduced metadata only. The index does not embed the full Strategy Builder package, buyer identity, raw CSV, checkout evidence or license payload.
- Add a visible session audit entry named `Evidence Index`.

## Guardrails

- No backend endpoint.
- No API call.
- No hidden localStorage write.
- No remote ticket is created or changed.
- No destination action is triggered.
- No Project Generator generation.
- No Project Generator preset save.
- No SQX Views template save.
- No Strategy Cleaner folder scan.
- No `.sqx` file mutation.
- No buyer identity.
- No checkout payload.
- No license payload.
- No private keys.
- No raw CSV payloads.
- No profitability claim.

## Runtime Boundary

The evidence handoff index is a local operator artifact. It is a traceability snapshot, not a publication, support-ticket update, checkout action, license action or StrategyQuant validation.

The index marks `ready_for_buyer_handoff` only when the required local evidence pieces are present. It does not prove trading quality and it does not replace manual StrategyQuant validation.

## Verification

- JS contracts assert shape, missing-required behavior, guardrails and UI preview behavior.
- Static dashboard tests assert SB17 documentation, runtime contracts and visible button.
- E2E smoke opens Strategy Builder and exercises the buyer-session path without remote or hidden persistence.

# SB14 Strategy Builder Buyer Session Printable Operator Notes

Phase SB14 adds local, print-ready operator notes for buyer setup sessions. The notes are generated from the current buyer session summary/checklist and are designed for a support call, setup handoff or printed review sheet without exposing the full Strategy Builder package.

## Scope

- Add `buyerSessionOperatorNotes` to `app/js/modules/strategy-builder-core.js`.
- Add `prepareBuyerSessionNotes` to `app/js/modules/strategy-builder.js`.
- Add `Notas imprimibles` to the Strategy Builder tab.
- Generate a `sqx-edge.strategy-builder-buyer-session-notes` artifact with:
  - session scope,
  - next manual action,
  - handoff targets,
  - redaction boundary,
  - operator guardrails,
  - plain-text `print_text`.
- Use the latest buyer session summary, buyer session checklist, buyer pack import review, buyer pack or Strategy Builder package as source.
- Add a visible session audit entry named `Buyer Session Notes`.

## Guardrails

- No backend endpoint.
- No API call.
- No hidden localStorage write.
- No destination action is triggered.
- No automatic browser print dialog.
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

The notes are a local operator artifact, not an execution engine. When the browser supports downloads, SQX exports a `.txt` file. In test harnesses or restricted browser contexts, the same text is shown in the Strategy Builder preview.

The feature intentionally avoids `window.print()` so no modal print dialog interrupts the buyer session or automated checks.

## Verification

- JS contracts assert note shape, printable text, redaction and UI preview behavior.
- Static dashboard tests assert SB14 documentation, runtime contracts and visible button.
- E2E smoke prepares printable notes after a buyer session summary and verifies no destination persistence.

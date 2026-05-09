# SB15 Strategy Builder Buyer Session Support Case Bundle

Phase SB15 adds a local support-case bundle for buyer setup sessions. It packages the printable operator notes, support questions and a safe attachment manifest so an operator can handle a setup/support case without exposing the full Strategy Builder package by default.

## Scope

- Add `buyerSessionSupportCaseBundle` to `app/js/modules/strategy-builder-core.js`.
- Add `exportBuyerSupportCaseBundle` to `app/js/modules/strategy-builder.js`.
- Add `Bundle soporte` to the Strategy Builder tab.
- Generate a `sqx-edge.strategy-builder-buyer-session-support-case-bundle` JSON artifact with:
  - local case id,
  - asset and timeframe,
  - workflow state,
  - support priority,
  - printable operator notes,
  - section manifest,
  - support questions,
  - attachment manifest,
  - redaction markers,
  - guardrails.
- Use the latest buyer session notes, summary, checklist, buyer pack review, buyer pack or Strategy Builder package as source.
- Add a visible session audit entry named `Buyer Support Case`.

## Guardrails

- No backend endpoint.
- No API call.
- No hidden localStorage write.
- No remote ticket is created.
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
- No full Strategy Builder package by default.
- No profitability claim.

## Runtime Boundary

The support case is a local JSON handoff artifact. It is not a CRM connector, helpdesk API call or remote ticket automation. The attachment manifest explicitly marks the full Strategy Builder package as excluded and sensitive unless an operator redacts and attaches it manually.

When downloads are available, SQX exports a local `.json` file. In restricted contexts, the same bundle is shown in the Strategy Builder preview.

## Verification

- JS contracts assert bundle shape, case id, support questions, attachment manifest and UI preview behavior.
- Static dashboard tests assert SB15 documentation, runtime contracts and visible button.
- E2E smoke prepares a support case after printable notes and verifies no destination persistence or remote-ticket side effect.

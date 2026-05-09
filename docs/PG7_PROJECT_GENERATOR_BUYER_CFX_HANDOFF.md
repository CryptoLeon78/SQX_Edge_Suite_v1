# PG7 Project Generator Buyer .cfx Handoff

## Objective

PG7 adds a buyer-specific handoff note generator inside Project Generator so an operator can prepare a small Markdown delivery note for a `.cfx` custom project without leaving SQX Edge.

The goal is commercial polish and operational clarity: a buyer receives the file plus a concise checklist that explains what was configured, what must be verified in StrategyQuant X and which responsible limits apply.

## User Flow

1. Open `Project Generator`.
2. Fill `Custom libre` manually or load a starter/profile family.
3. Optionally enter a buyer/case name and delivery context.
4. Review the generated Markdown note in `Entrega comprador .cfx`.
5. Copy or download the `.md` handoff note.
6. Deliver the note together with the `.cfx` file through the approved manual buyer process.

## Runtime Boundaries

- No backend endpoint is added.
- No remote API call is made.
- No license payload, buyer identity database or checkout event is read.
- No `.cfx` is generated automatically by the handoff card.
- No folder is scanned by the handoff card.
- No profitability or financial-result claim is made.

## Contract

Pure helpers live in `app/js/modules/project-generator-config.js`:

- `normalizeBuyerCfxHandoffInput`
- `buyerCfxHandoffSummary`
- `buyerCfxHandoffMarkdown`
- `buyerCfxHandoffFilename`

The dashboard card lives in `app/SQX_Dashboard_v6.html` and is wired by `app/js/project-generator-main.js` through `app/js/modules/project-generator-bindings.js`.

## Verification

PG7 is accepted when:

- JS syntax passes.
- Project Generator JS contracts pass.
- Static dashboard tests detect the PG7 panel, functions and documentation.
- E2E opens Project Generator, renders the handoff note and captures visual evidence.

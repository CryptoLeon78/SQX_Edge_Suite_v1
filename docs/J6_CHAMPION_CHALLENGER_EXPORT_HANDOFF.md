# J6 Champion vs Challenger Export and Strategy Builder Handoff

Phase J6 closes the first native Champion vs Challenger track with a safe export contract and a future Strategy Builder bridge.

## Scope

- Extend `SQX.championChallenger` with `buildReviewExport(model)` and `buildStrategyBuilderHandoff(reviewOrModel)`.
- Add dashboard actions for `Exportar resumen` and `Handoff Builder`.
- Keep the export browser-local as JSON only.
- Show a compact handoff preview in the existing `Champion vs Challenger` tab.

## Export Contract

`buildReviewExport(model)` returns:

- `type`: `sqx-edge.champion-challenger-review`
- `version`: `1`
- `generated_at`: ISO timestamp
- `source`: `SQX Edge Champion vs Challenger`
- `redaction`: explicit raw CSV/localStorage/remote-call boundary
- `summary`: candidate, formal-ready, OOS-stable, EGT-compliant and warning counts
- `candidates`: ranked, normalized candidate summaries
- `next_action`: operator guidance for review or handoff

Candidate summaries include only normalized metrics, pass/fail checks, OOS summary fields and Regime/EGT evidence. Raw import rows and CSV payloads are excluded.

## Strategy Builder Handoff Contract

`buildStrategyBuilderHandoff(reviewOrModel)` returns:

- `type`: `sqx-edge.strategy-builder-handoff`
- `version`: `1`
- `source_review`: safe review summary counts
- `recommended_candidate`: first ranked candidate, if present
- `candidates`: reduced builder candidates with decision hints
- `builder_status`: `planned_contract`
- `guardrails`: operator and security constraints

This is not a live Strategy Builder implementation. It is the first stable bridge so a future Builder can consume reviewed candidates without depending on DOM state or raw CSV text.

## Security Boundaries

- No raw CSV payloads.
- No remote calls.
- No automatic localStorage writes.
- No buyer, license or customer data.
- No Top Picks restoration.
- No `Matriz Completa`, matrix tab or heatmap panel restoration.

## Verification

- Static dashboard tests assert the J6 docs, UI IDs and exported functions.
- JS UI contracts assert export and handoff payloads, redaction and preview behavior.
- E2E smoke asserts desktop/mobile handoff contracts and captures the updated tab.
- `git diff --check` remains required before commit.

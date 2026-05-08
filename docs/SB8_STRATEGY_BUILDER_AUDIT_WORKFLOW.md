# SB8 Strategy Builder Audit Trail and Buyer Workflow Polish

Phase SB8 makes the Strategy Builder buyer flow easier to trust by adding a visible session audit trail and buyer workflow steps.

## Scope

- Add `buyerWorkflowSummary` to `app/js/modules/strategy-builder-core.js`.
- Add `handoffAuditEntry` to `app/js/modules/strategy-builder-core.js`.
- Add visible workflow steps to the Strategy Builder tab.
- Add a visible handoff audit list for Project Generator, PG preset drafts, SQX Views, JSON import and JSON export.
- Keep the audit trail session-only and visible in the UI.

## Guardrails

- No hidden localStorage write.
- No backend endpoint.
- No API call.
- No automatic preset save.
- No automatic SQX Views template save.
- No automatic `.vw` download.
- No automatic Project Generator run.
- The operator must press every final destination action manually.

## Buyer Workflow

The UI shows the buyer journey as controlled steps:

1. Evidence source selected.
2. Manual review confirmed.
3. Package exportable.
4. Project Generator handoff available.
5. SQX Views validation available.
6. Operator runs StrategyQuant manually.

The last step remains pending on purpose because SQX Edge prepares local handoffs; it does not claim to execute StrategyQuant validation.

## Audit Trail

The audit list records the latest prepared handoffs in the current browser session:

- `Project Generator`
- `PG Preset Draft`
- `SQX Views`
- `Import JSON`
- `Export JSON`

Each entry is generated from the current package and carries guardrails including `visible_session_trace`, `no_local_storage_write`, `no_remote_call` and `operator_manual_next_step`.

## Verification

- JS contracts assert workflow summaries, audit entries, UI rendering and the session-only boundary.
- Static dashboard tests assert SB8 documentation, public contracts and visible UI mounts.
- E2E smoke covers workflow readiness, handoff audit rows and absence of Strategy Builder audit localStorage.

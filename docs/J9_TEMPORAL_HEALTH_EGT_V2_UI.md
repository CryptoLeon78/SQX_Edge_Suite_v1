# J9 Temporal Health and EGT v2 UI

Date: 2026-05-09

Status: implemented as compact Champion vs Challenger dashboard evidence. No export payload, Strategy Builder handoff, backend endpoint, persistence or buyer-facing claim is changed in J9.

## Scope

J9 wires the J8 helpers into the existing Champion vs Challenger tab:

- Temporal Health chips per candidate.
- EGT v2 verdict chips per candidate.
- Compact filters for `Health OK` and `EGT v2 OK`.
- Summary counters for Health and EGT v2 readiness.
- First-party historical regime blocks derived locally when enough symbol/OOS evidence exists.

## UI Contract

Each ranking row may render:

- `Health fresh`
- `Health recovered`
- `Health old_peak`
- `Health declining`
- `Health unknown`
- `EGT v2 STRONG`
- `EGT v2 COMPLIANT`
- `EGT v2 DEFENSIVE`
- `EGT v2 INSUFFICIENT`
- `EGT v2 RISK`
- `EGT v2 UNKNOWN`

The filters are visual only:

- `cvc-filter-health-ok`
- `cvc-filter-egt-v2-ok`

They narrow the visible ranking but do not rewrite imported data, mutate scores, export hidden state or promote a candidate automatically.

## Evidence Rules

- Temporal Health is computed from J3 OOS records through `computeTemporalHealth`.
- EGT v2 is computed through `assessEgtV2`.
- Regime blocks come from `buildRegimeBlocksForSymbol`, using first-party local historical series.
- Missing evidence remains `UNKNOWN`.
- `STRONG`, `COMPLIANT` and `DEFENSIVE` count as EGT v2 OK for UI filtering.
- `RISK`, `INSUFFICIENT` and `UNKNOWN` do not count as EGT v2 OK.

## Explicit Non-Scope

- No export payload changes.
- No Strategy Builder handoff changes.
- No backend endpoint.
- No remote calls.
- No raw CSV persistence.
- No automatic promotion decision.
- No `Top Picks` tab, Top Picks block, matrix tab, full matrix, heatmap tab or heatmap panel.

## Verification

- JS UI contracts assert chips, filters and safe rendering.
- Regime/core contracts assert helper behavior.
- Static dashboard tests assert new IDs and module exports.
- E2E screenshots verify desktop and mobile Champion vs Challenger rendering.

## Next Phase

`J10` should extend the redacted review export and Strategy Builder handoff with reduced Temporal Health and EGT v2 fields only.

# REMOTE-COHORT-FIX1 - Cohort Scope Reconciliation

## Summary

REMOTE-COHORT-FIX1 fixes the ambiguity found after the first live cohort
matrix: the alias registry can contain known or future testers that are not
part of the current REMOTE-8F monitored cohort. Those standby aliases must not
block the active cohort, but active aliases with missing anti-sharing evidence
must remain visible until their context is captured or approved.

## What Changed

- The operator matrix now accepts an ignored local scope file:
  `.local/remote_service/remote_cohort_matrix/remote_cohort_scope.local.json`.
- Each alias can be marked as:
  - `active`: monitored in the current REMOTE-8F cohort.
  - `standby`: known alias, not part of the current monitored cohort.
  - `excluded`: intentionally excluded from the current monitor.
- Summary counters now separate:
  - total aliases;
  - active aliases;
  - standby aliases;
  - active ready aliases;
  - active aliases needing attention.
- Standby aliases are not counted as active blockers.
- Active aliases still require Access OK, active grant, trusted anti-sharing
  context, browser-download smoke and no open incidents.

## Current Interpretation

The current local scope keeps the reported download-smoke cohort active:

- `CREATOR-IVAN`
- `TESTER-DRP`
- `TESTER-RILIS`
- `TESTER-BIBI`
- `TESTER-JL`

`TESTER-ESTHER` remains a known alias/grant in standby because that alias was
not part of the current cohort download-smoke evidence.

`TESTER-RILIS` remains active. If the matrix still reports missing
anti-sharing context for that alias, the fix must not force it green. The next
operator action is to recapture or approve the device/context and rerun the
matrix.

## Operator Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_cohort_matrix.ps1
```

JSON output:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_cohort_matrix.ps1 -Json
```

Optional custom scope:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_cohort_matrix.ps1 -Scope .local\remote_service\remote_cohort_matrix\remote_cohort_scope.local.json
```

## Privacy Boundary

Tracked docs and matrix output remain alias-only. Raw emails, raw IPs,
protected URLs, cookies, tokens, Cloudflare identifiers, grant keys, local
Windows paths and private support details stay in ignored local evidence.

## Gate Impact

REMOTE-COHORT-FIX1 does not expand testers, create grants, change Cloudflare,
send messages, trigger checkout or approve REMOTE-8G. It only makes REMOTE-8F
monitoring evidence harder to misread.

Before REMOTE-8F can be treated as fully clean, every `active` alias must be
`ready`, or the operator must explicitly document a separate exception in the
next decision gate.

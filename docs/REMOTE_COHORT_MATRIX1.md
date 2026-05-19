# REMOTE-COHORT-MATRIX1 - Live Alias Cohort Matrix

## Summary

REMOTE-COHORT-MATRIX1 adds an operator-only matrix for the active tester cohort
so Codex and the operator can speak about users by alias without confusing
creator, testers, grants, anti-sharing contexts, downloads or support state.

The matrix answers, per alias:

- `Access OK`: the alias is present in the latest cohort smoke evidence with
  access confirmed.
- `Grant OK`: the local entitlement grant is active.
- `Anti-sharing OK`: the identity has a trusted context and no pending/blocked
  context requiring operator action.
- `Downloads OK`: the latest browser-download smoke confirmed downloads for
  that alias.
- `Incidencias abiertas`: open or triaged support cases matched to the alias.
- `Monitoring scope`: whether the alias belongs to the current active cohort,
  is standby for a future/manual pass, or is excluded from the current monitor.

## Local Sources

The live matrix is generated from ignored local evidence only:

- `.local/remote_service/user_aliases.local.json`
- `.local/remote_service/remote_entitlements.local.json`
- `.local/remote_service/remote_access_control.local.json`
- `.local/remote_service/support_cases/support_cases.local.jsonl`
- `.local/remote_service/remote_cohort_evidence1/remote_cohort_download_smoke.local.json`
- `.local/remote_service/remote_cohort_matrix/remote_cohort_scope.local.json`

The generated live output is also ignored:

- `.local/remote_service/remote_cohort_matrix/remote_cohort_matrix.local.json`

## Operator Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_cohort_matrix.ps1
```

Use JSON when another tool or future evidence phase needs to consume it:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_cohort_matrix.ps1 -Json
```

## Privacy Boundary

Tracked docs and tool output use aliases, role, identity hash refs, context refs
and aggregate counts only. Raw emails, raw IPs, protected URLs, cookies, session
tokens, Cloudflare identifiers, grant keys, local Windows paths and private
support details must stay out of Git.

## Current Meaning

`REMOTE-COHORT-MATRIX1` is operational visibility, not an expansion gate. A
green row means the current alias is coherent for monitoring. It does not
create users, send invites, approve new grants, widen Cloudflare Access, modify
checkout or authorize the next cohort movement.

The next controlled decision remains REMOTE-8F / REMOTE-8G review.

## REMOTE-COHORT-FIX1 Scope Rule

`REMOTE-COHORT-FIX1` separates the alias registry from the active monitoring
cohort. Standby aliases remain visible but do not count as active blockers.
Active aliases still block the active cohort if Access, grant, anti-sharing,
downloads or open-incident signals are missing.

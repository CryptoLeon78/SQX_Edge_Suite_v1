# REMOTE-COHORT-FIX2 - Anti-Sharing Context Recapture

## Summary

REMOTE-COHORT-FIX2 adds a safe reconciliation pass for active aliases whose
Access/download smoke is OK but whose anti-sharing context is not persisted in
the local access-control store.

This phase does not forge or backfill a trusted device context. It produces an
operator action plan so the context can be recaptured by the real browser path
or reviewed with the anti-sharing admin tool if it appears as pending.
In short: the project must not force a green state from smoke notes alone.

## Current Result

The local reconciliation currently reports:

- Active aliases: `5`
- Ready aliases: `4`
- Needs action: `1`
- Recapture required: `1`
- Operator review required: `0`
- Repeat smoke required: `0`

The active alias requiring recapture is:

- `TESTER-RILIS`: human access/download smoke was reported OK, but no
  anti-sharing context is persisted for the alias identity ref.

## Operator Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_cohort_context_reconcile.ps1
```

JSON output:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_cohort_context_reconcile.ps1 -Json
```

## Manual Recapture Steps

For `TESTER-RILIS`:

1. Ask the tester to open the single customer link again.
2. The tester must complete Cloudflare Access normally.
3. On Welcome, the tester should press `Actualizar estado` or `Acceso DASHBOARD`.
4. Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_cohort_matrix.ps1
```

5. If the alias becomes ready, continue REMOTE-8F/8G review.
6. If a pending context appears, run the status tool and approve only after
   confirming the alias:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_access_control_status.ps1
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_access_control_admin.ps1 -Action approve-context -Identity <identity-ref> -Context <context-ref> -Note "REMOTE-COHORT-FIX2 approved after alias confirmation"
```

7. Rerun the matrix and the reconciliation command.

## Privacy Boundary

Tracked files contain aliases, counts, reasons and operator instructions only.
Raw emails, IPs, protected URLs, cookies, tokens, Cloudflare identifiers,
grant keys, local paths and private support details remain in ignored local
evidence only.

## Gate Impact

REMOTE-COHORT-FIX2 does not expand testers, create grants, modify Cloudflare,
send emails, start checkout or approve REMOTE-8G. It only turns the remaining
anti-sharing discrepancy into a repeatable, auditable operator action.

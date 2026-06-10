# REMOTE-OWNER1 Owner Access Recovery

## Status

`completed_owner_recovery_applied`

REMOTE-OWNER1 turns the creator lockout incident into a governed recovery path. The owner identity must use `internal_operator`, not `tester_free`, and owner contexts use a separate context limit from tester/buyer contexts.

## What Changed

- `backend/sqx-edge-tool/core/remote_access_control.py` keeps the default `maxTrustedContextsPerIdentity=2` for normal identities.
- The same policy now exposes `maxTrustedContextsPerInternalOperator=8` and reports `effectiveMaxTrustedContexts` in public-safe access-control payloads.
- `backend/sqx-edge-tool/core/remote_owner_access.py` adds local-only recovery helpers with backup/rollback.
- `backend/sqx-edge-tool/tools/remote_owner_access_recovery.py` and `tools/remote_owner_access_recovery.ps1` expose `status`, `recover` and `rollback`.
- The local owner grant was promoted from `tester_free` to `internal_operator`; the current context remained trusted.

## Local Recovery Evidence

- Schema: `remote-owner-access-recovery-v1`
- Local status after recovery: `ownerGrantActive=true`
- Entitlement kind after recovery: `internal_operator`
- Trusted owner contexts after recovery: `3`
- Backup id: `remote-owner-access-recovery-v1_20260527_153521`

Evidence stays local under ignored `.local/remote_service/` stores and backup folders. Tracked docs contain only short hash refs/status, never raw emails, raw IPs, device cookies, session tokens, grant keys, protected URLs or local evidence contents.

## Operator Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_owner_access_recovery.ps1 -Action status -Identity <identity-ref> -Json
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_owner_access_recovery.ps1 -Action recover -Identity <identity-ref> -Context <context-ref> -Note "REMOTE-OWNER1 owner recovery" -Json
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_owner_access_recovery.ps1 -Action rollback -BackupId <backup-id> -Json
```

`recover` creates a backup before changing local ignored stores, strips tester grant-key fields from the owner grant, writes `entitlementKind=internal_operator`, and optionally approves the selected context.

## Boundaries

- No Cloudflare mutation.
- No checkout/payment/grant expansion.
- No raw email in tracked docs or normal output.
- No global bypass of anti-sharing.
- No change to tester/buyer limit of 2 trusted contexts.
- No workspace, artifact, SQX, `data.db`, `user/projects`, jar, license or activation mutation.

## Verification

- `backend/sqx-edge-tool/test_remote_access_control.py` proves `internal_operator` receives the owner context limit while the normal identity limit remains 2.
- `backend/sqx-edge-tool/test_remote_access.py` proves recovery promotes an existing tester grant to `internal_operator`, removes tester grant-key fields, approves a context and does not return/store raw private values.

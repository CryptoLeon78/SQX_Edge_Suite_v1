# REMOTE-8B - Live Pilot Evidence Ingest

REMOTE-8B converts the first private live-user smoke into a redacted, local-only evidence decision. It does not publish a URL, invite more users, run checkout automation or store buyer/tester private data in Git.

The phase exists because REMOTE-8 proved the chain with a controlled local drill. REMOTE-8B proves that the same chain has been checked against the private Cloudflare Tunnel/Access environment with one approved real user.

## Evidence Rule

Raw evidence must live only under ignored local paths:

- `.local/remote_service/remote8b_live_pilot_evidence.local.json`
- `.local/remote_service/remote8b_live_pilot_evidence/`

Tracked docs may contain only the schema, the validator contract and public-safe summaries. Never commit:

- raw email addresses;
- private protected URLs;
- Cloudflare identifiers;
- payment payloads;
- session tokens;
- grant keys;
- support logs;
- local workspace paths;
- SQX local paths.

## Required Proofs

The private evidence JSON must confirm:

- `remote8DrillBaselineGo`
- `edgeAccessBlockedAnonymous`
- `cloudflareAccessPassed`
- `appSessionLoginPassed`
- `entitlementActive`
- `workspaceCreated`
- `artifactGenerated`
- `exportDownloaded`
- `revocationBlockedAccess`
- `restoreAllowedAccess`
- `secondUserIsolationChecked`
- `noWorkspaceLeakage`
- `supportEvidenceRedacted`
- `privateEvidenceStoredOutsideGit`

If any proof is missing or false, REMOTE-8B is `NO_GO` and expansion stays blocked.

## Tool

Before collecting live evidence, the operator may create a local tester entitlement for the approved identity. This writes only hashes into the ignored entitlement store:

```powershell
python backend\sqx-edge-tool\tools\remote_tester_grant.py `
  --email "<approved tester email>" `
  --grant-key "<private tester grant key>"
```

The command output must stay local. The raw email and grant key are never committed, and the dashboard asks for the private tester key only when a `tester_free` grant requires it. Paid users and internal operators do not need this tester key.

Use the local-only ingest tool:

```powershell
python backend\sqx-edge-tool\tools\remote_live_pilot_evidence.py `
  --evidence .local\remote_service\remote8b_live_pilot_evidence.local.json `
  --out-dir .local\remote_service\remote8b_live_pilot_evidence
```

The output is:

- `.local/remote_service/remote8b_live_pilot_evidence/remote8b_live_pilot_evidence.public.json`

The summary uses `remote-live-pilot-evidence-v1` and redacts the pilot identity to `emailRef` plus a short email hash reference. It also strips URLs, local paths and secrets from the public result.

## GO Status

The only GO status for this phase is:

- `GO_REMOTE8B_LIVE_PILOT_EVIDENCE_SAFE_NO_GIT_LEAK`

Local evidence recorded on 2026-05-17 returned this GO status with all required proofs true. The private source and public-safe summary remain under ignored `.local/remote_service/remote8b_live_pilot_evidence*` paths; no protected URL, raw identity, grant key, session token, Cloudflare identifier or local SQX path is tracked.

Even with GO, expansion remains blocked by design:

- `expansionGate.allowedToExpandBeyondOneUser = false`

The next phase must decide expansion explicitly after observing the first real user.

## Next Phase

`REMOTE-8C - First User Support Observation And Expansion Decision` should observe the first user support loop, tunnel stability, workspace behavior, artifact generation, revocation/restore confidence and any usability blockers before inviting 3-5 users.

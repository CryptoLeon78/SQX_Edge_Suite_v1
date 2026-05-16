# REMOTE-8 - Controlled Pilot Drill

## Summary

REMOTE-8 adds a local-only controlled pilot drill for the remote web Pro model. The drill proves the chain we need before inviting or expanding real users:

1. signed payment webhook activates `paid_subscription`;
2. app login creates a remote session after trusted identity;
3. server derives a workspace from the session identity;
4. a `.cfx` pilot artifact is generated inside the workspace;
5. the artifact is copied to exports and checksum-verified;
6. a second user receives a separate workspace and cannot see the first artifact;
7. cancellation blocks the active session through entitlement revalidation;
8. restore snapshot returns the pilot session to active state.

The drill writes evidence only under ignored `.local/remote_service/remote8_controlled_pilot/`. The committed code contains no live buyer, tester, URL, checkout or Cloudflare private data.

## Artifacts

- `backend/sqx-edge-tool/core/remote_pilot.py`
- `backend/sqx-edge-tool/tools/remote_controlled_pilot.py`
- `backend/sqx-edge-tool/test_remote_controlled_pilot.py`
- `remote-controlled-pilot-v1`
- ignored evidence root: `.local/remote_service/remote8_controlled_pilot/`

## Operator Command

```powershell
python backend\sqx-edge-tool\tools\remote_controlled_pilot.py
```

Optional deterministic evidence run:

```powershell
python backend\sqx-edge-tool\tools\remote_controlled_pilot.py --run-id remote8-private-smoke
```

The tool prints a public-safe summary and writes:

- `remote8_controlled_pilot.public.json`
- `remote8_controlled_pilot.local.json`
- local entitlement store;
- local payment webhook audit;
- local security policy;
- per-workspace manifest, logs, outputs and exports.

Only the public summary shape is safe to discuss in tracked docs. The local manifest and workspace files are evidence, not repo material.

## Public-Safe Result Contract

The public summary must include:

- `version = remote-controlled-pilot-v1`;
- `paymentWebhook.ok`;
- `login.ok`;
- `workspace.ok`;
- `artifactGeneration.filename` ending in `.cfx`;
- `exportDownload.sha256Matches`;
- `isolation.sameWorkspace = false`;
- `isolation.firstArtifactVisibleInSecondWorkspace = false`;
- `revocation.accessAllowedAfterCancel = false`;
- `restore.accessAllowedAfterRestore = true`;
- privacy flags confirming no raw email, session token, grant key, local path or secret is returned.

## Live Pilot Boundary

REMOTE-8 is the controlled drill and harness. It does not:

- charge a real buyer;
- send a real invitation;
- publish or paste a protected URL;
- create live Cloudflare Access users;
- expose local paths or private operator data;
- expand the cohort beyond one user.

The next phase is `REMOTE-8B - Live Pilot Evidence Ingest`: run the private real-user smoke with operator approval, then ingest only redacted evidence.

## Controlled Pilot Gate

Before any expansion beyond one live user:

- the drill must be GO;
- private live smoke must prove the same chain;
- entitlement cancellation/revocation must block access;
- restore evidence must exist;
- no workspace leakage can be observed;
- support evidence must remain redacted;
- operator must explicitly approve expansion.

## Test Evidence

Required verification:

```powershell
git diff --check
npm run test:js
python -m pytest backend\sqx-edge-tool -q
```

E2E screenshots are not required for REMOTE-8 because this phase adds backend/drill contracts and docs, not dashboard visual changes.

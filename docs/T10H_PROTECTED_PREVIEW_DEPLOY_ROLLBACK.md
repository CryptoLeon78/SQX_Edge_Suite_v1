# T10h Protected Preview Deploy Rollback

## Objective

T10h executed exactly one protected preview deployment attempt from the separated Vercel project and inspected the deployment target immediately before any tester URL was shared.

This phase is accepted as a rollback, not as a successful tester preview.

## External Action Performed

- Ran one Vercel CLI deployment from the private tester portal working tree.
- Requested `target=preview`.
- Used the separated project `sqx-edge-tester-preview`.
- Inspected the deployment result immediately.
- Removed the deployment immediately after Vercel reported `target = production`.

## Result

```text
NO_GO_TARGET_NOT_PREVIEW_GUARD_ROLLBACK
```

Observed deployment state:

- The deployment was created only for inspection.
- The requested target was preview.
- Vercel returned `target = production`.
- The T10b guard blocked the build with exit code 43.
- The deployment ended in build error before publication.
- The deployment was removed immediately.
- No tester URL was shared.
- No Vercel URL was committed.
- The separated Vercel project now reports no latest deployment.
- The separated Vercel project now reports no domains.

## Interpretation

The separated project is safer than the legacy project because the production-target guard blocked publication, but the deployment target mismatch still exists.

T10h proves the next move must be target-routing correction, not tester rollout.

## Required Next Step

T10i must correct or replace the Vercel preview deployment route before another deployment attempt.

Acceptable T10i routes:

1. Use Vercel dashboard/API to verify why CLI `target=preview` resolves to production on this account/project.
2. Test a Git-triggered non-production branch deployment only after a no-deploy proof confirms branch target mapping.
3. Use a custom Vercel environment or another hosting path only if Deployment Protection and no-production-alias guarantees can be proved before deployment.

Do not share any tester URL until a deployment returns `target = preview` and no production alias exists.

## Security Boundary

- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No Vercel URL was committed.
- No bypass/share URL was created.
- No active deployment remains.
- No tester URL was shared.

## Verification

T10h is accepted when:

- this document exists
- `scripts/vercel-protected-preview-rollback-proof.mjs` exists
- `package.json` exposes `proof:vercel-protected-preview-rollback`
- the rollback proof returns `GO_PROTECTED_PREVIEW_ROLLBACK_CLEAN`
- the deployment attempt result is recorded as `NO_GO_TARGET_NOT_PREVIEW_GUARD_ROLLBACK`
- the separated project has no latest deployment
- the separated project has no domains
- docs and roadmap point to T10i rather than tester rollout
- static tests assert the rollback contract
- backend tests pass
- `git diff --check` passes

# T10k CLI Default Preview Rollback

## Objective

T10k executed exactly one corrected CLI default preview deployment attempt without `--prod`, without `--target` and without `--skip-domain`.

This phase is accepted as a rollback, not as a successful tester preview.

## External Action Performed

- Ran one Vercel CLI deployment command from the private tester portal working tree.
- Used no `--prod`.
- Used no `--target`.
- Used no `--skip-domain`.
- Inspected the created deployment immediately.
- Removed the deployment immediately after Vercel reported `target = production`.
- Captured raw output only in local ignored backup evidence.
- Did not share or commit any Vercel URL.

## Result

```text
NO_GO_CLI_DEFAULT_PREVIEW_TARGET_PRODUCTION_ROLLBACK
```

Observed deployment state:

- Deployment id: present during inspection.
- Requested route: CLI default preview.
- Vercel returned `target = production`.
- The T10b guard blocked the build with exit code 43.
- The deployment ended in `ERROR`, not `READY`.
- Alias surface was observed before removal.
- The deployment was removed immediately.
- No tester URL was shared.
- No Vercel URL was committed.
- The separated Vercel project now reports no latest deployment.
- The separated Vercel project now reports no domains.

## Interpretation

T10k proves the problem is not limited to API target fields, omitted target requests, separated project setup, `--target=preview`, or `--skip-domain`.

The current Vercel route still resolves local CLI deployment attempts to production. The build-time guard is doing its job, but the route is not suitable for tester rollout.

The next move must be investigation or replacement, not another deployment attempt.

## Required Next Step

T10l must investigate or replace the Vercel route without another deployment attempt.

Acceptable T10l routes:

1. Inspect Vercel project settings/API for CLI deployment target behavior and branch/environment mapping.
2. Use the Vercel dashboard to identify why CLI default deployments resolve to production.
3. Create a new no-deploy proof for a different route only if it can prove target behavior before deployment.
4. Consider a different hosting route for tester preview if Vercel cannot provide a provable preview-only path.

Do not run another deployment until T10l produces a no-deploy GO.

## Security Boundary

- No active deployment remains.
- No tester URL was shared.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No Vercel URL was committed.
- No bypass/share URL was created.

## Verification

T10k is accepted when:

- this document exists
- `scripts/vercel-cli-default-preview-rollback-proof.mjs` exists
- `package.json` exposes `proof:vercel-cli-default-preview-rollback`
- the proof returns `GO_CLI_DEFAULT_PREVIEW_ROLLBACK_CLEAN`
- docs and roadmap point to T10l rather than another deployment attempt
- static tests assert the rollback contract
- backend tests pass
- `git diff --check` passes

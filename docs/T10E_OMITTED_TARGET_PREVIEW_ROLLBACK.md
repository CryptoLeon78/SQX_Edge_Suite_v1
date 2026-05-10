# T10e Omitted Target Preview Rollback

## Objective

T10e corrected the Vercel API preview request according to Vercel REST API behavior: omit `target` so the deployment should default to preview.

This phase is accepted as a rollback, not as a successful tester preview.

## External Action Performed

- Added `scripts/vercel-omitted-target-preview-proof.mjs`.
- Added `npm run proof:vercel-omitted-target-preview`.
- Ran the no-deploy proof and received `GO_OMITTED_TARGET_PREVIEW_PATH_READY`.
- Created one Vercel deployment through the REST API with no `target` field.
- Used the private `tester-preview` Git source.
- Inspected the created deployment immediately.
- Removed the deployment immediately after Vercel still reported `target = production`.

## Result

```text
NO_GO_TARGET_NOT_PREVIEW_ROLLED_BACK
```

Observed deployment state:

- The deployment was created only for inspection.
- The API request omitted `target`.
- The API still returned `target = production`.
- The deployment was still initializing when the unsafe target was detected.
- The deployment was removed immediately.
- No tester URL was shared.
- No Vercel URL was committed.
- The Vercel project now reports no latest deployment.
- The Vercel project now reports no domains.

## Interpretation

The current Vercel project must not be used for tester preview rollout.

T10, T10b, T10d and T10e show that automatic Git, explicit `target: "preview"` and omitted-target API deployment paths all produce an unsafe production target on this project.

## Required Next Step

T10f must recreate or separate the Vercel preview project before any tester URL is shared.

Acceptable T10f routes:

1. Create a new preview-only Vercel project dedicated to tester access, with no production aliases and no buyer-facing domains.
2. Reconnect the private Git repository from scratch and prove the first deployment target before keeping any deployment.
3. Use a manually reviewed Vercel dashboard correction only if a no-deploy proof confirms the corrected project state before another deployment.

Do not create another deployment on the current project ID.

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

T10e is accepted when:

- this document exists
- the omitted-target proof script exists
- `package.json` exposes `proof:vercel-omitted-target-preview`
- the deployment attempt result is recorded as `NO_GO_TARGET_NOT_PREVIEW_ROLLED_BACK`
- the unsafe deployment was removed
- the Vercel project has no latest deployment
- the Vercel project has no domains
- docs and roadmap point to T10f rather than another deployment attempt on the current project ID
- static tests assert the rollback contract
- backend tests pass
- `git diff --check` passes

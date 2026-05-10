# T10m Vercel Config Hardening

## Objective

T10m applies a narrow Vercel Project API correction without creating another deployment.

This phase is accepted as configuration hardening, not as a tester rollout and not as proof that the preview deployment target is fixed.

## External Action Performed

- Queried Vercel Project API for the separated tester preview project.
- Queried Vercel Project Domains API for the same project.
- Patched only documented project settings:
  - `autoAssignCustomDomains = false`
  - `previewDeploymentsDisabled = false`
- Did not run `vercel deploy`.
- Did not call the Vercel deployments creation API.
- Did not push a trigger commit to the private tester portal repo.
- Did not create, share or commit any Vercel URL.

## Result

```text
GO_CONFIG_HARDENED_NO_DEPLOY_TARGET_STILL_UNPROVEN
```

Observed corrected project state:

- Project name remains `sqx-edge-tester-preview`.
- Project automatic custom-domain assignment is disabled.
- Preview deployments are not disabled at project level.
- Project has no custom domains.
- Project has no live deployment.
- Project has no latest deployment.
- Deployment Protection remains required.
- No tester URL was created or shared.

Remaining route-risk signals:

- Previous Git, API, omitted-target and CLI default attempts returned `target = production`.
- `productionDeploymentsFastLane` may still be reported by the Project API and is not patched because no documented safe update field was found for this phase.
- A no-deploy configuration proof cannot prove the target value of a future deployment.

## Interpretation

T10m removes the most actionable documented risk found in T10l: automatic custom-domain assignment. It also explicitly keeps preview deployments enabled so the project is not silently routing around preview behavior.

This is a safer Vercel configuration, but it does not authorize a deployment. The next phase must still prove or replace the preview route before any tester URL exists.

## Required Next Step

T10n must perform one of these before any deployment:

1. Manual Vercel dashboard review of production branch, deployment targets and fast-lane behavior with private evidence.
2. A documented API-supported correction for the remaining route-risk field, if Vercel exposes one.
3. A replacement host/route proof that can demonstrate preview-only behavior without creating a public surface.

Do not run another deployment until T10n produces a no-deploy GO for the next route.

## Security Boundary

- No deployment was created.
- No active deployment remains.
- No tester URL was shared.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No Vercel URL was committed.
- No bypass/share URL was created.

## Verification

T10m is accepted when:

- this document exists
- `scripts/vercel-config-hardening-proof.mjs` exists
- `package.json` exposes `proof:vercel-config-hardening`
- `vercel.json` disables GitHub automatic aliasing with `github.autoAlias = false`
- the proof returns `GO_CONFIG_HARDENED_NO_DEPLOY_TARGET_STILL_UNPROVEN` after apply mode
- docs and roadmap point to T10n as no-deploy route proof/replacement
- static tests assert the hardening contract
- backend tests pass
- `git diff --check` passes

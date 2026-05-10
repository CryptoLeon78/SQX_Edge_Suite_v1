# T10l Vercel Route Investigation

## Objective

T10l investigates the Vercel preview route without creating another deployment.

This phase is accepted as a no-deploy investigation, not as a tester rollout.

## External Action Performed

- Queried Vercel Project API for the separated tester preview project.
- Queried Vercel Environment API for the same project.
- Did not run `vercel deploy`.
- Did not push a trigger commit to the private tester portal repo.
- Did not create, share or commit any Vercel URL.

## Result

```text
NO_GO_VERCEL_ROUTE_REQUIRES_MANUAL_TARGET_FIX_OR_REPLACEMENT
```

Observed project state:

- Project name: `sqx-edge-tester-preview`.
- Project has no live deployment.
- Project has no latest deployment.
- Project has no domains.
- Git source is linked through the Vercel Project API `link` object.
- Linked production branch is `main`.
- Intended preview branch is `tester-preview`.
- Deployment Protection remains verified.
- Environment variable count is zero.

Observed route-risk signals:

- `project.productionBranch` is missing while `link.productionBranch` is `main`.
- `project.targets` is empty.
- `autoAssignCustomDomains` is enabled.
- `productionDeploymentsFastLane` is enabled.
- Previous CLI/API/default routes repeatedly returned `target = production`.

## Interpretation

Vercel documentation says `vercel deploy` is the preview route and `vercel deploy --prod` is the production route. SQX evidence contradicts that expectation for this linked project: Git, explicit API, omitted target, `--target=preview` and CLI default attempts all returned production target.

The build-time guard has prevented publication, but it is only containment. It does not fix route mapping.

## Required Next Step

T10m must perform manual dashboard/API correction or define an alternative no-deploy route proof before any further deployment.

Acceptable T10m options:

1. Manually review Vercel dashboard project settings for production branch, environments, automatic domain assignment and deployment target behavior.
2. Use a Vercel API patch only if the exact field change is known and documented before execution.
3. Create a fresh route proof for a different Vercel project/provider only if it can prove target behavior before deployment.
4. Replace Vercel for tester preview if no preview-only path can be proven.

Do not run another deployment until T10m produces a no-deploy GO.

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

T10l is accepted when:

- this document exists
- `scripts/vercel-route-investigation-proof.mjs` exists
- `package.json` exposes `proof:vercel-route-investigation`
- the proof returns `NO_GO_VERCEL_ROUTE_REQUIRES_MANUAL_TARGET_FIX_OR_REPLACEMENT`
- docs and roadmap point to T10m as no-deploy correction/replacement
- static tests assert the investigation contract
- backend tests pass
- `git diff --check` passes

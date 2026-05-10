# T10n Vercel Route Decision

## Objective

T10n decides whether the hardened Vercel route can be approved without creating another deployment.

This phase is a no-deploy decision gate. It does not create a tester rollout and does not publish a URL.

## External Action Performed

- Queried Vercel Project API for the separated tester preview project.
- Queried Vercel Project Domains API for the same project.
- Did not run `vercel deploy`.
- Did not call the Vercel deployments creation API.
- Did not patch project settings.
- Did not push a trigger commit to the private tester portal repo.
- Did not create, share or commit any Vercel URL.

## Result

```text
NO_GO_CURRENT_VERCEL_ROUTE_REPLACEMENT_REQUIRED
```

Observed safe state after T10m:

- Project name remains `sqx-edge-tester-preview`.
- Automatic custom-domain assignment remains disabled.
- Preview deployments remain enabled at project level.
- Project has no custom domains.
- Project has no live deployment.
- Project has no latest deployment.
- Deployment Protection remains required.
- No tester URL was created or shared.

Blocking decision:

- Previous Git, explicit API, omitted-target API and CLI default attempts all returned `target = production`.
- Vercel still reports `productionDeploymentsFastLane`.
- No documented no-deploy API field proves the future deployment target.
- A future deployment target can only be observed by creating a deployment, which is disallowed until the route is proven or replaced.

## Interpretation

T10m made the existing Vercel project safer, but T10n cannot responsibly approve another deployment on the same route. The risk is not the current surface; the project has no public tester surface. The risk is that the next deployment attempt may again be classified as production before we can safely share or use it.

The current Vercel route is therefore rejected for tester rollout. The next phase must replace the route or obtain a manual provider-level proof that does not require creating a deployment.

## Required Next Step

T10o must prepare one of these options:

1. A manual Vercel dashboard/provider proof that the next deployment will be preview-only before running it.
2. A fresh staging route with a new project/provider and a no-deploy proof of preview-only behavior before first deployment.
3. A non-Vercel controlled tester route if Vercel cannot provide a reliable preview-only path.

Do not run another deployment until T10o produces a no-deploy GO for the selected route.

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

T10n is accepted when:

- this document exists
- `scripts/vercel-route-decision-proof.mjs` exists
- `package.json` exposes `proof:vercel-route-decision`
- the proof returns `NO_GO_CURRENT_VERCEL_ROUTE_REPLACEMENT_REQUIRED`
- docs and roadmap point to T10o as route replacement/proof before any deployment
- static tests assert the route decision contract
- backend tests pass
- `git diff --check` passes

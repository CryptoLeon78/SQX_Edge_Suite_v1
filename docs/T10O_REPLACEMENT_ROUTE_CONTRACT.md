# T10o Replacement Route Contract

## Objective

T10o selects the next safe route after T10n rejected the current Vercel route for tester rollout.

This phase is a no-deploy replacement-route contract. It does not create a project, does not link a provider, does not deploy, and does not publish a tester URL.

## External Action Performed

- Did not run `vercel deploy`.
- Did not call any deployment creation endpoint.
- Did not mutate Vercel project settings.
- Did not create a new external project.
- Did not push a trigger commit to the private tester portal repo.
- Did not create, share or commit any tester URL.
- Did not create tester accounts, passwords or renewal emails.

## Result

```text
GO_REPLACEMENT_ROUTE_CONTRACT_READY_NO_DEPLOY
```

Selected route:

```text
fresh_staging_route_with_no_deploy_preflight
```

Rejected route:

```text
current_vercel_route
```

## Decision

The current Vercel route remains rejected. T10n proved that the existing route cannot be approved without creating another deployment, and repeated previous attempts returned `target = production`.

T10o therefore selects a fresh staging route with a new project/provider and a no-deploy preflight before the first deployment. The next phase must not reuse the current route as the rollout path unless a provider-level proof arrives that changes the T10n decision.

## T10p Entry Requirements

T10p may start only after explicit approval for any external action it needs.

Required before any deployment:

- Explicit approval before creating or linking any external project.
- Deployment Protection must be enabled before any URL exists.
- No custom domains.
- No automatic production aliasing.
- No tester emails, tester accounts, passwords, tokens or secrets.
- Production branch must be `main`.
- The preview/tester branch must not be production.
- First deployment, if approved later, must still perform immediate target inspection and rollback on mismatch.

Forbidden in T10p until separately approved:

- No tester invite.
- No tester URL publication.
- No checkout, license issue or buyer-contact action.
- No database with real tester records.
- No public release announcement.

## Security Boundary

- No deployment was created.
- No external project was created.
- No active deployment remains.
- No tester URL was shared.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No Vercel URL was committed.
- No bypass/share URL was created.

## Verification

T10o is accepted when:

- this document exists
- `scripts/replacement-route-contract-proof.mjs` exists
- `package.json` exposes `proof:replacement-route-contract`
- the proof returns `GO_REPLACEMENT_ROUTE_CONTRACT_READY_NO_DEPLOY`
- docs and roadmap point to T10p as the fresh staging route preflight
- static tests assert the replacement route contract
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

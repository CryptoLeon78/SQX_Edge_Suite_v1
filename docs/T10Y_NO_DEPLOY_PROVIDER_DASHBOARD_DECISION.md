# T10y No-Deploy Provider Dashboard Decision

## Objective

T10y stops retrying Vercel CLI deployment after T10x proved that even an explicit `--target=preview` command returned `target = production`.

This phase is a no-deploy decision gate. It does not create a deployment, does not mutate Vercel settings, does not publish a tester URL and does not touch tester accounts.

## External Action Performed

- Did not run `vercel deploy`.
- Did not call any deployment creation endpoint.
- Did not mutate Vercel project settings.
- Did not create or remove any Vercel project.
- Did not link or relink GitHub.
- Did not push a trigger commit to the private tester portal repo.
- Did not create, share or commit any tester URL.
- Did not create tester accounts, passwords or renewal emails.
- Did not connect a production database.

## Result

```text
GO_PROVIDER_DASHBOARD_CORRECTION_DECISION_READY_NO_DEPLOY
```

Selected route:

```text
provider_dashboard_correction_before_any_deployment
```

Rejected routes:

```text
vercel_cli_default_deployment
vercel_cli_explicit_preview_target_deployment
current_vercel_cli_deployment_route
```

## Decision

The current Vercel CLI deployment route is paused for tester rollout. T10v and T10x both showed that the fresh staging project can still resolve a non-production `tester-preview` deployment as `production`.

The T10b guard contained the risk, but a guard is not a rollout strategy. It prevents publication after Vercel has already classified the build incorrectly.

T10y therefore selects a provider/dashboard correction path before any further deployment attempt. The next phase must produce manual or provider-level evidence that the staging project cannot classify `tester-preview` as production before another deployment is allowed.

## T10z Entry Requirements

T10z must stay no-deploy and produce a correction package or operator checklist with these minimum facts:

- Project: `sqx-edge-tester-staging`.
- Production branch must be `main`.
- Tester branch must remain `tester-preview`.
- CLI default and explicit preview-target routes remain rejected.
- Deployment Protection must remain enabled before any deployment exists.
- Custom domains must remain empty.
- Deployment count must remain `0`.
- No tester URL may be shared.
- No tester account, password, renewal email, checkout or license action may happen.

T10z may include dashboard screenshots, provider support notes, or a no-deploy settings export. It must not create a deployment.

## Security Boundary

- No deployment was created.
- No active deployment exists.
- No team domain exists.
- No tester URL was shared.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No bypass/share URL was created.
- No `.vercel/` local metadata was committed.

## Verification

T10y is accepted when:

- this document exists
- `scripts/no-deploy-provider-dashboard-decision-proof.mjs` exists
- `package.json` exposes `proof:no-deploy-provider-dashboard-decision`
- the proof returns `GO_PROVIDER_DASHBOARD_CORRECTION_DECISION_READY_NO_DEPLOY`
- docs and roadmap point to T10z as the no-deploy provider/dashboard correction package
- static tests assert that Vercel CLI deployment remains paused
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

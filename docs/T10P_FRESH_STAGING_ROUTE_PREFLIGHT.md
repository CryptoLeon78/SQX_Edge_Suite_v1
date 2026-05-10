# T10p Fresh Staging Route Preflight

## Objective

T10p turns the T10o replacement-route contract into a concrete no-deploy preflight for a fresh staging route.

This phase does not create or verify an external project. It defines the local gate that must pass before asking for an exact external-action approval to create, link or inspect any provider route.

## External Action Performed

- Did not run `vercel deploy`.
- Did not call any deployment creation endpoint.
- Did not call any provider API.
- Did not create a Vercel project or any alternative provider project.
- Did not link GitHub to a new provider project.
- Did not push a trigger commit to the private tester portal repo.
- Did not create, share or commit any tester URL.
- Did not create tester accounts, passwords or renewal emails.

## Result

```text
GO_FRESH_STAGING_ROUTE_PREFLIGHT_READY_NO_EXTERNAL_ACTION
```

Selected route:

```text
fresh_staging_route_with_no_deploy_preflight
```

Current route status:

```text
current_vercel_route_rejected
```

## Preflight Contract

The future staging route must satisfy these constraints before any deployment exists:

- It must use a fresh staging project or provider route, not the rejected current route.
- It must keep production branch as `main`.
- It must keep the tester/preview branch non-production.
- It must have Deployment Protection enabled before any URL exists.
- It must have no custom domains.
- It must have no automatic production aliasing.
- It must have no tester emails, accounts, passwords, tokens or secrets.
- It must not connect a production database.
- It must not send emails, invite testers, issue licenses or create checkout traffic.
- It must produce a provider-level or dashboard/API proof before the first deployment.

## Required Approval For The Next External Step

The next phase may ask for exact approval to do one of these external actions:

1. Create a fresh protected Vercel staging project without deployment.
2. Verify an already-created fresh staging project without deployment.
3. Select a non-Vercel protected staging provider route without deployment.

The approval must name the provider and the allowed action. A broad "continue" is not enough to deploy, publish a URL, invite testers, create accounts or connect real data.

## Forbidden Until Separately Approved

- No deployment.
- No URL publication.
- No tester invite.
- No tester account.
- No tester email in git.
- No password rotation.
- No renewal email.
- No production database.
- No checkout/license action.
- No public release announcement.

## Verification

T10p is accepted when:

- this document exists
- `scripts/fresh-staging-route-preflight-proof.mjs` exists
- `package.json` exposes `proof:fresh-staging-route-preflight`
- the proof returns `GO_FRESH_STAGING_ROUTE_PREFLIGHT_READY_NO_EXTERNAL_ACTION`
- docs and roadmap point to T10q as the first exact external-action approval gate
- static tests assert that no deploy/API/project/URL action is performed
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

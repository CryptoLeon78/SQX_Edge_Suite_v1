# T10u Staging Deployment Readiness Gate

## Objective

T10u prepares a no-deploy readiness gate before any deployment against `sqx-edge-tester-staging`.

This phase does not deploy. It defines the minimum conditions for a later single controlled staging deployment attempt and preserves the rollback requirement before any tester URL can be shared.

## Read-Only Checks Performed

- Verified the private tester portal working tree is on branch `tester-preview`.
- Verified ignored local Vercel metadata points to `sqx-edge-tester-staging`.
- Queried deployments for `sqx-edge-tester-staging`.
- Queried team domains.
- Queried project protection settings.
- Verified SSO Deployment Protection remains enabled.
- Verified Git fork protection remains enabled.
- Did not run `vercel deploy`.
- Did not call any deployment creation endpoint.
- Did not create a deployment.
- Did not publish or share any tester URL.
- Did not create tester accounts, passwords or renewal emails.
- Did not connect a production database.

## Result

```text
GO_STAGING_DEPLOYMENT_READINESS_GATE_NO_DEPLOY
```

Readiness snapshot:

- Project: `sqx-edge-tester-staging`.
- Project ID: `prj_A3VERjLXuzqb4f1adGmYjvg8aVVZ`.
- Team ID: `team_43avYcdXjtKKE2GtwkOwbNKa`.
- Private portal branch: `tester-preview`.
- Local Vercel link target: `sqx-edge-tester-staging`.
- SSO Deployment Protection: enabled.
- SSO deployment type: `all_except_custom_domains`.
- Git fork protection: enabled.
- Deployment count: `0`.
- Domains count: `0`.
- `.vercel/` remains ignored local metadata.

## Controlled Next Attempt

T10v may execute exactly one staging deployment attempt only if it keeps these controls:

- command shape: `vercel deploy --force --yes --format json`
- run from the private tester portal working tree
- linked project must be `sqx-edge-tester-staging`
- branch must be `tester-preview`
- inspect returned deployment target immediately
- inspect aliases and domains immediately
- rollback/delete immediately if target is not preview
- rollback/delete immediately if any production alias or custom domain appears
- do not share or commit any deployment URL
- do not invite testers
- do not create tester accounts

## Interpretation

The fresh staging project is ready for a controlled deployment attempt, but the project still has no deployment surface. The next phase is allowed to attempt one deployment only as an inspection event, not as a tester rollout.

The historical Vercel route returned `target=production` several times. That risk remains the reason T10v must inspect and rollback before any URL is shared.

## Security Boundary

- No deployment was created.
- No active deployment exists.
- No tester URL was shared.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No bypass/share URL was created.
- No `.vercel/` local metadata was committed.
- The previous rejected route remains rejected for rollout.

## Verification

T10u is accepted when:

- this document exists
- `scripts/staging-deployment-readiness-proof.mjs` exists
- `package.json` exposes `proof:staging-deployment-readiness`
- the proof returns `GO_STAGING_DEPLOYMENT_READINESS_GATE_NO_DEPLOY`
- docs and roadmap point to T10v as one controlled staging deployment attempt with target inspection and rollback
- static tests assert that no deploy/URL/tester action was performed in T10u
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

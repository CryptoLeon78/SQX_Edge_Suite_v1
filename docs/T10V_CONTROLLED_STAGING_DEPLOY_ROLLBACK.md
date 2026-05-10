# T10v Controlled Staging Deploy Rollback

## Objective

T10v executes exactly one controlled staging deployment attempt against `sqx-edge-tester-staging`, inspects the target immediately and rolls back on mismatch before any tester URL is shared.

## External Action Performed

- Ran one `vercel deploy --force --yes --format json` attempt from the private tester portal working tree.
- The private tester portal working tree was on branch `tester-preview`.
- The local Vercel link targeted `sqx-edge-tester-staging`.
- Vercel returned `target = production`.
- The T10b build guard blocked the build with exit code `43`.
- Removed the failed deployment immediately.
- Verified no deployments remain for `sqx-edge-tester-staging`.
- Verified no domains exist in the team.
- Verified SSO Deployment Protection remains enabled.
- Verified Git fork protection remains enabled.
- Did not share or commit any deployment URL.
- Did not invite testers.
- Did not create tester accounts, passwords or renewal emails.
- Did not connect a production database.

## Result

```text
NO_GO_STAGING_DEPLOYMENT_TARGET_PRODUCTION_ROLLBACK_CLEAN
```

Rollback snapshot:

- Project: `sqx-edge-tester-staging`.
- Project ID: `prj_A3VERjLXuzqb4f1adGmYjvg8aVVZ`.
- Team ID: `team_43avYcdXjtKKE2GtwkOwbNKa`.
- Private portal branch: `tester-preview`.
- Returned target: `production`.
- Guard status: `NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH`.
- Guard exit code: `43`.
- Failed deployment removed: yes.
- Deployment count after rollback: `0`.
- Domains count after rollback: `0`.
- Tester URL published: no.

## Interpretation

The fresh staging project still routes a non-production branch deployment as production. The T10b guard correctly prevented publication, and the failed deployment was deleted immediately.

This means the current Vercel CLI deployment route remains rejected for tester rollout. The next phase must not retry deployment. It must correct the provider-level target mapping or choose a different staging route with a no-deploy proof first.

## Required Next Step

T10w must investigate or correct the provider-level target mapping without another deployment attempt. Acceptable paths:

- fix the Vercel project or Git production-branch mapping from dashboard/provider settings
- use a Vercel Git preview route that proves `tester-preview` maps to preview before deployment
- replace Vercel deployment route with another protected staging provider
- keep tester rollout blocked

No tester URL may be shared until a deployment returns preview target and no production alias/custom domain exists.

## Security Boundary

- The failed deployment was removed.
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

T10v is accepted when:

- this document exists
- `scripts/controlled-staging-deploy-rollback-proof.mjs` exists
- `package.json` exposes `proof:controlled-staging-deploy-rollback`
- the proof returns `NO_GO_STAGING_DEPLOYMENT_TARGET_PRODUCTION_ROLLBACK_CLEAN`
- docs and roadmap point to T10w as a no-deploy provider-level target correction or replacement route
- static tests assert that no URL/tester account was published
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

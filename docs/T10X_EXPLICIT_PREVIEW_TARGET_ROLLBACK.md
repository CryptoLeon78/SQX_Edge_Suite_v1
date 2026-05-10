# T10x Explicit Preview Target Rollback

## Objective

T10x executes exactly one explicit preview-target deployment attempt with `vercel deploy --target=preview --force --yes --format json`, inspects the returned target immediately and rolls back on mismatch before any tester URL is shared.

## External Action Performed

- Ran one explicit preview-target Vercel CLI deployment attempt from the private tester portal working tree.
- The private tester portal working tree was on branch `tester-preview`.
- The local Vercel link targeted `sqx-edge-tester-staging`.
- The attempted command was `vercel deploy --target=preview --force --yes --format json`.
- Vercel returned `target = production` despite the explicit preview target.
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
NO_GO_EXPLICIT_PREVIEW_TARGET_RETURNED_PRODUCTION_ROLLBACK_CLEAN
```

Rollback snapshot:

- Project: `sqx-edge-tester-staging`.
- Project ID: `prj_A3VERjLXuzqb4f1adGmYjvg8aVVZ`.
- Team ID: `team_43avYcdXjtKKE2GtwkOwbNKa`.
- Private portal branch: `tester-preview`.
- Attempted target: `preview`.
- Returned target: `production`.
- Guard status: `NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH`.
- Guard exit code: `43`.
- Failed deployment removed: yes.
- Deployment count after rollback: `0`.
- Domains count after rollback: `0`.
- Tester URL published: no.

## Interpretation

The Vercel CLI route is rejected for tester rollout. Both the default CLI route and the explicit `--target=preview` route returned production target from `tester-preview`.

The T10b guard prevented publication and the failed deployment was deleted immediately. There is no active deployment surface.

## Required Next Step

T10y must stop retrying Vercel CLI deployment and choose one of these no-deploy paths:

- manually correct provider/dashboard target mapping before any new deployment attempt
- use a Git/PR preview provider path that proves preview target before deployment
- replace Vercel with another protected staging provider
- run the tester pilot locally/private-network only until a safe cloud route exists
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

T10x is accepted when:

- this document exists
- `scripts/explicit-preview-target-rollback-proof.mjs` exists
- `package.json` exposes `proof:explicit-preview-target-rollback`
- the proof returns `NO_GO_EXPLICIT_PREVIEW_TARGET_RETURNED_PRODUCTION_ROLLBACK_CLEAN`
- docs and roadmap point to T10y as a no-deploy route replacement or provider/dashboard correction decision
- static tests assert that no URL/tester account was published
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

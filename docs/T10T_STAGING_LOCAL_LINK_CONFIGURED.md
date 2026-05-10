# T10t Staging Local Link Configured

## Objective

T10t links the private tester portal working tree to `sqx-edge-tester-staging` without deployment and without publishing a URL.

This phase is a local Vercel CLI configuration step only. It does not deploy, does not create tester accounts and does not expose any tester surface.

## External Action Performed

- Ran `vercel link --yes --project sqx-edge-tester-staging --scope ivanaza8-3625s-projects` inside the private tester portal working tree.
- Updated the private working tree's ignored `.vercel/project.json` to point at `prj_A3VERjLXuzqb4f1adGmYjvg8aVVZ`.
- Verified `.vercel/` is ignored by git in the private tester portal repo.
- Queried deployments for `sqx-edge-tester-staging`.
- Queried team domains.
- Queried project protection settings.
- Did not run `vercel deploy`.
- Did not call any deployment creation endpoint.
- Did not connect production database settings.
- Did not commit `.vercel/project.json`.
- Did not publish or share any tester URL.
- Did not create tester accounts, passwords or renewal emails.

## Result

```text
GO_STAGING_LOCAL_LINK_CONFIGURED_NO_DEPLOY
```

Linked project:

```text
sqx-edge-tester-staging
```

Configuration snapshot:

- Project ID: `prj_A3VERjLXuzqb4f1adGmYjvg8aVVZ`.
- Team ID: `team_43avYcdXjtKKE2GtwkOwbNKa`.
- Local private portal link target: `sqx-edge-tester-staging`.
- Previous local link target: `sqx-edge-tester-preview`.
- SSO Deployment Protection: enabled.
- SSO deployment type: `all_except_custom_domains`.
- Git fork protection: enabled.
- Deployment count: `0`.
- Domains count: `0`.
- Git provider source was not changed in T10t.
- `.vercel/project.json` remains ignored local metadata.

## Interpretation

The private tester portal working tree now targets the fresh protected staging project for future Vercel commands. This removes the local CLI link to the rejected preview project, but it does not authorize a deployment or tester rollout.

The next deployment-capable step must still prove the target before any URL is shared. Any deployment mismatch must be rolled back immediately.

## Required Next Step

T10u must prepare a no-deploy staging deployment readiness gate before any deployment. It must preserve:

- no deployment
- no public/protected tester URL publication
- no tester accounts
- no tester emails in git
- no production database
- no custom domains
- production branch `main`
- tester branch non-production
- target inspection and rollback requirement for any later deployment

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
- The rejected current route remains rejected for rollout.

## Verification

T10t is accepted when:

- this document exists
- `scripts/staging-local-link-proof.mjs` exists
- `package.json` exposes `proof:staging-local-link`
- the proof returns `GO_STAGING_LOCAL_LINK_CONFIGURED_NO_DEPLOY`
- docs and roadmap point to T10u as a no-deploy deployment readiness gate
- static tests assert that no deploy/URL/tester action was performed
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

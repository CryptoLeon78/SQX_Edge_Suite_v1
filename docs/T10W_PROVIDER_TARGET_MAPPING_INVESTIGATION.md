# T10w Provider Target Mapping Investigation

## Objective

T10w investigates the provider-level target mapping without another deployment attempt after T10v proved that the default CLI staging route still returns `target = production`.

This phase does not deploy. It rejects the default CLI deployment route and prepares an explicit preview-target route as the next controlled gate.

## Read-Only / No-Deploy Actions Performed

- Inspected `sqx-edge-tester-staging` with `vercel project inspect`.
- Queried project protection settings.
- Queried deployments for `sqx-edge-tester-staging`.
- Queried team domains.
- Queried the Vercel connected app project object.
- Queried Vercel documentation and CLI help for `vercel deploy --target`.
- Ran `vercel pull --environment=preview --yes` to synchronize ignored local preview metadata only.
- Verified `.vercel/project.json` still targets `sqx-edge-tester-staging`.
- Verified `.vercel/` remains ignored local metadata.
- Did not run `vercel deploy`.
- Did not call any deployment creation endpoint.
- Did not create a deployment.
- Did not publish or share any tester URL.
- Did not read, commit or expose `.vercel/.env.preview.local`.
- Did not create tester accounts, passwords or renewal emails.
- Did not connect a production database.

## Findings

```text
NO_GO_DEFAULT_CLI_STAGING_ROUTE_REJECTED_EXPLICIT_PREVIEW_TARGET_PREPARED
```

Provider snapshot:

- Project: `sqx-edge-tester-staging`.
- Project ID: `prj_A3VERjLXuzqb4f1adGmYjvg8aVVZ`.
- Team ID: `team_43avYcdXjtKKE2GtwkOwbNKa`.
- Framework preset: `Other`.
- Project API framework: `null`.
- Project API live: `false`.
- Project API latestDeployment: `null`.
- Project API domains: `[]`.
- Deployment count: `0`.
- Domains count: `0`.
- SSO Deployment Protection: enabled.
- SSO deployment type: `all_except_custom_domains`.
- Git fork protection: enabled.
- Local preview metadata synchronized: yes.
- `.vercel/.env.preview.local` exists only as ignored local metadata and is not public evidence.

## Route Decision

The default CLI route remains rejected because T10v proved it returns production target from `tester-preview`.

The only Vercel CLI route worth one more controlled attempt is an explicit preview target command:

```text
vercel deploy --target=preview --force --yes --format json
```

This command is not executed in T10w. It is only prepared for T10x with the same controls as T10v:

- one attempt only
- inspect returned target immediately
- inspect aliases and domains immediately
- rollback/delete immediately if target is not preview
- rollback/delete immediately if any production alias or custom domain appears
- do not share or commit any deployment URL
- do not invite testers
- do not create tester accounts

## Required Next Step

T10x may execute exactly one explicit preview-target deployment attempt only with the command above and the rollback controls listed here.

If T10x still returns `target = production`, the Vercel deployment route must be abandoned or corrected manually from provider/dashboard settings before any further deployment attempt.

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
- `.vercel/.env.preview.local` remains private ignored local metadata.

## Verification

T10w is accepted when:

- this document exists
- `scripts/provider-target-mapping-investigation-proof.mjs` exists
- `package.json` exposes `proof:provider-target-mapping-investigation`
- the proof returns `NO_GO_DEFAULT_CLI_STAGING_ROUTE_REJECTED_EXPLICIT_PREVIEW_TARGET_PREPARED`
- docs and roadmap point to T10x as one explicit `--target=preview` controlled deployment attempt with rollback
- static tests assert that no deploy/URL/tester action was performed in T10w
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

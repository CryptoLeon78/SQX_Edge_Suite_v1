# T10z Provider Dashboard Correction Package

## Objective

T10z prepares the no-deploy provider/dashboard correction package required by T10y before any new deployment attempt.

This phase creates a manual operator checklist and acceptance contract. It does not apply provider changes, does not run a deployment and does not publish a tester URL.

## External Action Performed

- Queried current staging project deployment list.
- Queried current team domains list.
- Queried current staging project protection settings.
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
GO_PROVIDER_DASHBOARD_CORRECTION_PACKAGE_READY_NO_DEPLOY
```

Selected next gate:

```text
operator_provider_dashboard_correction_record_without_deployment
```

Current safe-state evidence:

- Project: `sqx-edge-tester-staging`.
- Project ID: `prj_A3VERjLXuzqb4f1adGmYjvg8aVVZ`.
- Team ID: `team_43avYcdXjtKKE2GtwkOwbNKa`.
- Private portal branch: `tester-preview`.
- Deployment count: `0`.
- Domains count: `0`.
- SSO Deployment Protection: `all_except_custom_domains`.
- Git fork protection: enabled.
- Vercel CLI deployment route: paused.
- Default CLI route: rejected.
- Explicit preview-target CLI route: rejected.

## Operator Checklist

The operator must complete this checklist in the provider dashboard or through provider support before another deployment attempt is approved:

1. Confirm the selected project is `sqx-edge-tester-staging`, not any legacy tester preview project.
2. Confirm the production branch is `main`.
3. Confirm `tester-preview` is not a production branch and cannot receive production target classification.
4. Confirm automatic custom-domain assignment remains disabled or impossible for this tester route.
5. Confirm no custom domains exist.
6. Confirm Deployment Protection remains enabled before any deployment exists.
7. Confirm the project still has zero deployments.
8. Record whether Vercel support or dashboard settings explain why previous non-production attempts returned `target=production`.
9. Record the exact correction made or the exact reason no correction is available.
10. Stop if the provider cannot prove that the next `tester-preview` deployment will not be classified as production.

## Required Evidence Format

The next phase must capture evidence privately or as public-safe redacted text:

```text
project=sqx-edge-tester-staging
production_branch=main
tester_branch=tester-preview
deployment_count=0
domains_count=0
deployment_protection=enabled
git_fork_protection=enabled
correction_status=corrected|provider_confirmed|blocked
next_deployment_allowed=yes|no
operator_initials=<redacted or local-only>
evidence_location=<private-only or redacted-public-pointer>
```

Public-safe committed evidence must not include screenshots with private account details, raw tester emails, deployment URLs, bypass links, secrets, tokens, inspector URLs or support-ticket private contents.

## T10aa Entry Requirements

T10aa may start only as a no-deploy evidence-recording phase unless the user explicitly approves a different exact external action.

T10aa must not run a deployment. It must record one of these outcomes:

- `GO_PROVIDER_DASHBOARD_CORRECTION_CONFIRMED_NO_DEPLOY`
- `NO_GO_PROVIDER_DASHBOARD_CORRECTION_BLOCKED`
- `NO_GO_PROVIDER_CANNOT_PROVE_PREVIEW_TARGET`

Only after a future GO evidence phase may a separate deployment attempt be proposed, and that attempt must still include immediate target inspection and rollback on mismatch.

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

T10z is accepted when:

- this document exists
- `scripts/provider-dashboard-correction-package-proof.mjs` exists
- `package.json` exposes `proof:provider-dashboard-correction-package`
- the proof returns `GO_PROVIDER_DASHBOARD_CORRECTION_PACKAGE_READY_NO_DEPLOY`
- docs and roadmap point to T10aa as a no-deploy provider/dashboard correction evidence record
- static tests assert that Vercel CLI deployment remains paused
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

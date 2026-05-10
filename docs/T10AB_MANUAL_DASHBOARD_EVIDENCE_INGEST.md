# T10ab Manual Dashboard Evidence Ingest

## Objective

T10ab ingests the manual Vercel dashboard evidence reported by Ivan for `sqx-edge-tester-staging` and decides whether the current Vercel tester route can continue before any new deployment attempt.

This phase does not deploy, does not mutate provider settings and does not publish a tester URL.

## External Action Performed

- Ingested manual dashboard evidence supplied by the operator in plain text.
- Did not run `vercel deploy`.
- Did not call any deployment creation endpoint.
- Did not mutate Vercel project settings.
- Did not create or remove any Vercel project.
- Did not link or relink GitHub.
- Did not push a trigger commit to the private tester portal repo.
- Did not create, share or commit any tester URL.
- Did not create tester accounts, passwords or renewal emails.
- Did not connect a production database.

## Manual Evidence Received

```text
project=sqx-edge-tester-staging
git_connected=no
repo=<none>
production_branch=not_visible
tester_preview_production_like=not_visible
domains_count=0
auto_alias_enabled=not_visible
deployment_protection=all_except_custom_domains
framework=other
build_command=<not_visible>
output_directory=<not_visible>
root_directory=not_visible
provider_explanation=<none>
correction_status=not_visible
next_deployment_allowed=unknown
```

## Result

```text
NO_GO_REPLACE_VERCEL_TESTER_ROUTE
```

## Interpretation

The current Vercel tester route is not approved for another deployment attempt.

Positive safety signals:

- Domains count is `0`.
- Deployment protection is reported as `all_except_custom_domains`.
- No repository is connected to the staging project.

Blocking gaps:

- Git is not connected, so there is no dashboard-visible Git branch contract for `tester-preview`.
- Production branch is not visible.
- `tester-preview` production-like status is not visible.
- Auto alias behavior is not visible.
- Build, output and root directory are not visible enough to prove route behavior.
- Provider explanation is `<none>`.
- Correction status is `not_visible`.
- Next deployment permission is `unknown`.

Because previous controlled attempts returned `target=production`, the burden of proof is now higher than a normal first deployment. Without a provider/dashboard correction or an auditable branch-target proof, a new Vercel deployment attempt would be operationally unsafe.

## Selected Next Gate

```text
T10ac_non_vercel_protected_tester_route_options_no_deploy
```

T10ac must compare and select a replacement tester route without deployment. Acceptable options:

- A non-Vercel protected tester route with private auth, explicit no-index posture and no public URL publication until verified.
- A local/private-network pilot route for the first testers, keeping distribution controlled while cloud hosting is re-evaluated.
- A new Vercel route only if provider support or dashboard evidence can prove the branch-target behavior before any deployment.

T10ac is still a no-deploy decision phase unless Ivan explicitly approves one exact external action in a later phase.

## Security Boundary

- No deployment was created.
- No active deployment exists from this phase.
- No tester URL was shared.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No bypass/share URL was created.
- No `.vercel/` local metadata was committed.

## Verification

T10ab is accepted when:

- this document exists
- `scripts/manual-dashboard-evidence-ingest-proof.mjs` exists
- `package.json` exposes `proof:manual-dashboard-evidence-ingest`
- the proof returns `NO_GO_REPLACE_VERCEL_TESTER_ROUTE`
- docs and roadmap point to T10ac as the no-deploy replacement route selection
- static tests assert that the current Vercel tester route remains rejected
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

# T10ajj Cloudflare Route Onboarding Decision

## Objective

T10ajj decides the next Cloudflare route/onboarding path after T10aji proved that the first Worker deploy cannot safely continue without a `workers.dev` account subdomain or a protected route/custom domain.

No provider mutation was performed in this phase.

## Official Sources Checked

- Cloudflare Workers `workers.dev`: https://developers.cloudflare.com/workers/configuration/routing/workers-dev/
- Cloudflare Workers Preview URLs: https://developers.cloudflare.com/workers/configuration/previews/
- Cloudflare Workers script subdomain API: https://developers.cloudflare.com/api/resources/workers/subresources/scripts/subresources/subdomain/

## Source Findings

- Cloudflare documents `workers.dev` as configurable in the dashboard.
- Cloudflare documents `workers.dev` URLs as publicly available when enabled.
- Cloudflare documents Cloudflare Access as the protection path for `workers.dev` and Preview URLs.
- Cloudflare documents `workers_dev = false` as the Wrangler configuration flag that disables the Worker `workers.dev` route on redeploy.
- Cloudflare documents `preview_urls = false` in Wrangler's local schema as the configuration flag for disabling Preview URLs.
- Cloudflare's public script subdomain API enables/disables a Worker on `workers.dev` after a script exists; it does not register the account-level `workers.dev` subdomain.

## Decision

```text
GO_CLOUDFLARE_ROUTE_ONBOARDING_DECISION_READY_NO_DEPLOY
```

Selected next path:

```text
custom_route_or_dashboard_workers_dev_onboarding_before_redeploy
```

The safer default is to avoid a public `workers.dev` route unless Cloudflare Access can be enabled and verified immediately. Therefore the template now sets:

```json
"workers_dev": false,
"preview_urls": false
```

This deliberately blocks another accidental public `workers.dev` deploy until T10ajk chooses one of the two controlled route options:

- custom route/domain under Cloudflare Access, preferred for tester rollout
- dashboard `workers.dev` onboarding plus immediate Cloudflare Access enablement and app JWT validation, acceptable only for a short protected pilot

## Live Cloudflare State

Read-only checks after T10aji cleanup still return:

```text
deployments=worker_not_found
versions=worker_not_found
secrets=worker_not_found
```

No Worker currently exists.

## Security Boundary Preserved

- No Cloudflare Worker was created.
- No Cloudflare deployment was created.
- No Cloudflare version was uploaded.
- No Cloudflare Access application was created.
- No Cloudflare Access policy was created.
- No GitHub repository was connected to Cloudflare.
- No Cloudflare token or account ID was committed.
- No raw Wrangler output was committed.
- No tester URL was published.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.

## Next Gate

```text
T10ajk_cloudflare_route_onboarding_or_access_precreate
```

T10ajk must either:

- configure a protected custom route/domain path before redeploy, or
- perform dashboard `workers.dev` onboarding and prepare immediate Access enablement before redeploy.

No new `wrangler deploy` should run until T10ajk records the chosen route and protection checklist.

## Verification

T10ajj is accepted when:

- this document exists
- `scripts/cloudflare-route-onboarding-decision-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-route-onboarding-decision`
- `wrangler.jsonc` sets `workers_dev` to `false`
- `wrangler.jsonc` sets `preview_urls` to `false`
- the proof returns `GO_CLOUDFLARE_ROUTE_ONBOARDING_DECISION_READY_NO_DEPLOY`
- no provider token, account ID, tester email or tester URL appears in tracked public files
- static tests and full pytest pass
- `git diff --check` passes

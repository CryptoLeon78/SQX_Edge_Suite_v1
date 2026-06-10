# T10ajk Cloudflare Route Access Precreate

## Objective

T10ajk attempts the next real Cloudflare route/access step after T10ajj hardened the Worker configuration with `workers_dev=false` and `preview_urls=false`.

The phase verifies the authenticated local Cloudflare control path, keeps the Worker absent, and decides whether a protected custom route/domain or `workers.dev` onboarding can be safely prepared before another deploy.

## Official Sources Checked

- Cloudflare Workers routes and domains: https://developers.cloudflare.com/workers/configuration/routing/
- Cloudflare Workers custom domains: https://developers.cloudflare.com/workers/configuration/routing/custom-domains/
- Cloudflare Workers `workers.dev`: https://developers.cloudflare.com/workers/configuration/routing/workers-dev/
- Cloudflare Access self-hosted applications: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/
- Cloudflare Access application types: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/

## Source Findings

- Cloudflare recommends production Workers use a route or custom domain instead of a `workers.dev` subdomain.
- A Worker custom domain requires an active Cloudflare zone and a Worker to invoke.
- A custom domain can be represented in Wrangler with a route object that includes `custom_domain=true`, but the route is created by deploy/API action.
- If `workers.dev` is disabled in the dashboard but not in Wrangler, Wrangler can re-enable it on a later deploy; keeping `workers_dev=false` in config is mandatory.
- Cloudflare Access protects self-hosted applications by matching an application hostname.
- Creating an Access application without a selected hostname/zone would not prove coverage for the future tester URL.

## Real Local Checks

```text
wrangler_auth_state=authenticated_redacted
worker_deployments_state=worker_not_found
worker_versions_state=worker_not_found
worker_secrets_state=worker_not_found
raw_cloudflare_identity_output_committed=false
```

The raw Wrangler identity output includes private account details and is intentionally not committed.

## Gate Result

```text
NO_GO_CLOUDFLARE_ROUTE_HOSTNAME_REQUIRED_T10AK_BLOCKED
```

T10ajk cannot safely precreate Cloudflare Access yet because no exact hostname or zone has been selected for the protected tester route.

## Selected Path

```text
preferred=protected_custom_domain
fallback=workers_dev_only_after_dashboard_onboarding_and_access_ready
```

The preferred route remains a protected custom domain under Cloudflare Access. `workers.dev` remains a fallback only for a short pilot and only if dashboard onboarding is completed and Access/app-auth coverage can be verified immediately.

## Public Template Changes

- `wrangler.jsonc` keeps `workers_dev=false`.
- `wrangler.jsonc` keeps `preview_urls=false`.
- No public `routes` entry is added until a private hostname/zone is selected.
- `cloudflare-route-access-precreate.example.json` records the safe private evidence shape.
- `cloudflare-route-access-precreate.local.json` is ignored and reserved for private non-sensitive evidence only.

## Manual Input Needed Before T10ak

T10ak remains blocked until one of these is true:

1. A Cloudflare-managed hostname/zone is selected privately for a custom domain route.
2. Dashboard `workers.dev` onboarding is completed privately and an Access application hostname can be matched before any tester sharing.

Do not commit the selected hostname, account ID, zone ID, tester URL, tester emails or Cloudflare tokens to the public/core repositories.

## Security Boundary Preserved

- No Cloudflare Worker was created.
- No Cloudflare deployment was created.
- No Cloudflare version was uploaded.
- No Cloudflare custom route/domain was created.
- No public `routes` entry was committed.
- No Cloudflare Access application was created.
- No Cloudflare Access policy was created.
- No GitHub repository was connected to Cloudflare.
- No Cloudflare token, account ID or zone ID was committed.
- No raw Wrangler output was committed.
- No tester URL was published.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.

## Next Gate

```text
T10ajl_cloudflare_hostname_zone_selection_or_workers_dev_onboarding
```

T10ajl must collect private hostname/zone evidence or confirm dashboard `workers.dev` onboarding before T10ak can create an Access application/policy and before any new deploy attempt.

## Verification

T10ajk is accepted when:

- this document exists
- `scripts/cloudflare-route-access-precreate-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-route-access-precreate`
- `cloudflare-route-access-precreate.example.json` exists and contains only public-safe placeholders
- `cloudflare-route-access-precreate.local.json` is ignored
- `wrangler.jsonc` keeps `workers_dev` set to `false`
- `wrangler.jsonc` keeps `preview_urls` set to `false`
- the proof returns `NO_GO_CLOUDFLARE_ROUTE_HOSTNAME_REQUIRED_T10AK_BLOCKED`
- no provider token, account ID, zone ID, tester email or tester URL appears in tracked public files
- static tests and full pytest pass
- `git diff --check` passes

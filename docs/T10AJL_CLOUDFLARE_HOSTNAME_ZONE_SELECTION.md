# T10ajl Cloudflare Hostname Zone Selection

## Objective

T10ajl tries to select the private Cloudflare hostname/zone evidence required by T10ajk before T10ak can create a Cloudflare Access application and policy.

This phase does not publish a route, create a Worker, create Access, invite testers or commit a hostname. It records the exact private evidence needed to unblock the next real provider step.

## Official Sources Checked

- Cloudflare Workers routes and domains: https://developers.cloudflare.com/workers/configuration/routing/
- Cloudflare Workers routes: https://developers.cloudflare.com/workers/configuration/routing/routes/
- Cloudflare Workers custom domains: https://developers.cloudflare.com/workers/configuration/routing/custom-domains/
- Cloudflare Workers `workers.dev`: https://developers.cloudflare.com/workers/configuration/routing/workers-dev/
- Cloudflare Access self-hosted applications: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/
- Cloudflare Access application types: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/

## Source Findings

- A production-like Worker route should use a custom domain or route in a Cloudflare zone rather than `workers.dev`.
- A self-hosted Access application protects an application hostname; the protected hostname must be known before Access coverage can be proven.
- Wrangler v4 exposes deployment commands, but not a safe public CLI path here to list/select zones without exposing private account context.
- `workers.dev` remains acceptable only as a short pilot fallback after dashboard onboarding and immediate Access/app-auth coverage checks.

## Gate Result

```text
NO_GO_PRIVATE_HOSTNAME_ZONE_EVIDENCE_REQUIRED_T10AK_BLOCKED
```

T10ak stays blocked because the public repository cannot choose or commit the real hostname/zone and no ignored local evidence file currently proves it.

## Private Evidence File

Use this public-safe template:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-hostname-zone-selection.example.json
```

Copy it privately to:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-hostname-zone-selection.local.json
```

The local file is ignored by git. It should contain only booleans and non-sensitive labels, not the hostname, account ID, zone ID, tester URL, tester emails or tokens.

## Evidence Required To Unlock T10ak

For the preferred custom domain path:

- `hostnameSelectedPrivately=true`
- `zoneSelectedPrivately=true`
- `hostnameBelongsToCloudflareZone=true`
- `accessHostnameCanBeMatched=true`
- `routeCanBeCreatedAfterDeploy=true`
- `accessPrecreateAllowed=true`

For the fallback `workers.dev` pilot path:

- `workersDevOnboardingComplete=true`
- `accessHostnameCanBeMatched=true`
- `accessPrecreateAllowed=true`
- `testerUrlPublished=false`

Both paths must keep:

- `testerUrlPublished=false`
- `testerEmailsIncluded=false`
- `t10akUnlocked=true` only after the evidence above is true

## Manual Operator Checklist

1. In Cloudflare, pick a Cloudflare-managed zone or complete account `workers.dev` onboarding.
2. Privately decide the hostname that will be protected by Access.
3. Confirm Access can match exactly that hostname before any tester sharing.
4. Fill only the boolean evidence in `cloudflare-hostname-zone-selection.local.json`.
5. Run `npm run proof:cloudflare-hostname-zone-selection`.
6. Continue to T10ak only if the proof returns `GO_CLOUDFLARE_HOSTNAME_ZONE_READY_T10AK_ALLOWED`.

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
- No hostname was committed.
- No tester URL was published.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.

## Next Gate

```text
T10ak_cloudflare_access_application_policy_creation
```

T10ak can only start after ignored local evidence proves a private hostname/zone or protected `workers.dev` onboarding path. If the proof still returns NO-GO, the next action is manual hostname/zone selection, not Access creation.

## Verification

T10ajl is accepted when:

- this document exists
- `scripts/cloudflare-hostname-zone-selection-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-hostname-zone-selection`
- `cloudflare-hostname-zone-selection.example.json` exists and contains only public-safe placeholders
- `cloudflare-hostname-zone-selection.local.json` is ignored
- `wrangler.jsonc` keeps `workers_dev` set to `false`
- `wrangler.jsonc` keeps `preview_urls` set to `false`
- the proof returns `NO_GO_PRIVATE_HOSTNAME_ZONE_EVIDENCE_REQUIRED_T10AK_BLOCKED` until local private evidence is provided
- no provider token, account ID, zone ID, hostname, tester email or tester URL appears in tracked public files
- static tests and full pytest pass
- `git diff --check` passes

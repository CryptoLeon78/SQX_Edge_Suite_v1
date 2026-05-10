# T10ajl Operator Unlock Kit

## Objective

Reduce the Cloudflare hostname/zone blocker to one private operator action before T10ak.

This phase does not create Cloudflare Access, deploy a Worker, create a route, publish a URL or create tester accounts. It adds a local helper that creates and validates the ignored evidence file used by `proof:cloudflare-hostname-zone-selection`.

## Operator Command

From `templates/SQX_Edge_Tester_Portal`:

```powershell
npm run prepare:cloudflare-hostname-zone-selection -- --write
```

This creates:

```text
cloudflare-hostname-zone-selection.local.json
```

The file is ignored by git. Keep it private and store only booleans or non-sensitive labels.

## Private Checklist

Preferred custom-domain path:

1. Confirm there is an active Cloudflare-managed zone.
2. Choose the protected hostname outside git.
3. Confirm the hostname belongs to that Cloudflare zone.
4. Confirm Cloudflare Access can match that hostname before tester sharing.
5. Confirm a Worker route/custom domain can be attached after deploy.
6. Set the matching boolean fields to `true`.
7. Keep `testerUrlPublished=false` and `testerEmailsIncluded=false`.

Fallback `workers.dev` pilot path:

1. Complete `workers.dev` onboarding outside git.
2. If no Worker exists yet, do not mark Access booleans as ready; use T10ajm to prepare the harmless shell target first.
3. Confirm Access can protect the selected Worker/application target before tester sharing.
4. Set `workersDevOnboardingComplete=true`, `workersDevShellTargetExists=true`, `workersDevAccessProtectionVerified=true`, `accessHostnameCanBeMatched=true` and `accessPrecreateAllowed=true` only after the shell target exists and can be protected.
5. Keep `testerUrlPublished=false` and `testerEmailsIncluded=false`.

## Guardrails

The helper and proof reject sensitive evidence fields such as:

- hostnames
- account IDs
- zone IDs
- tokens
- tester emails
- tester URLs
- private keys
- long hex-like secrets

## Unlock Condition

Run:

```powershell
npm run proof:cloudflare-hostname-zone-selection
```

Continue to T10ak only when it returns:

```text
GO_CLOUDFLARE_HOSTNAME_ZONE_READY_T10AK_ALLOWED
```

If it returns `NO_GO_PRIVATE_HOSTNAME_ZONE_EVIDENCE_REQUIRED_T10AK_BLOCKED`, the next real action is still private Cloudflare dashboard evidence, not Access creation.

## Official Sources

- Cloudflare Workers routes and domains: https://developers.cloudflare.com/workers/configuration/routing/
- Cloudflare Workers custom domains: https://developers.cloudflare.com/workers/configuration/routing/custom-domains/
- Cloudflare Access application types: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/

# T10am Controlled Real App Deploy Result

## Objective

T10am executes the one approved Cloudflare Wrangler deployment attempt for the real OpenNext tester portal and records the result without exposing tester access.

## Approval

The operator provided the exact T10al approval phrase before execution.

## Commands Executed

From `templates/SQX_Edge_Tester_Portal`:

```powershell
npm run proof:cloudflare-access-policy-boundary
npm run proof:cloudflare-workers-dev-access
npm run proof:cloudflare-hostname-zone-selection
npm run typecheck
npm run cf:build
npm exec -- wrangler deploy --config wrangler.jsonc
npm exec -- wrangler deployments list --config wrangler.jsonc
npm exec -- wrangler versions list --config wrangler.jsonc
```

## Result

```text
GO_REAL_APP_VERSION_UPLOADED_NO_PUBLIC_TARGET_NO_TESTER_URL
```

Wrangler accepted the deployment/upload and created a new Worker version/deployment record for the expected Worker name. Because `wrangler.jsonc` keeps `workers_dev=false`, `preview_urls=false` and no `routes` are committed, Wrangler reported no deploy targets. No tester URL was published.

## Access Smoke

The existing Cloudflare Access boundary proofs still pass after the upload:

- `proof:cloudflare-access-policy-boundary` returns `GO_ACCESS_APPLICATION_POLICY_BOUNDARY_VERIFIED_NO_APP_DEPLOY`.
- `proof:cloudflare-workers-dev-access` returns `GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_VERIFIED_NO_APP`.
- `proof:cloudflare-hostname-zone-selection` returns `GO_CLOUDFLARE_HOSTNAME_ZONE_READY_T10AK_ALLOWED`.

This is acceptable because the real app version was uploaded without opening a public route. It is not yet a tester-ready published URL.

## Rollback Decision

Rollback was not required because:

- No public deploy target was created.
- No custom/public route was added.
- No tester URL was shared.
- The protected Access evidence remains green.
- Anonymous app body exposure remains blocked by the current no-public-target boundary.

## Blocked Actions

- Do not share a tester URL yet.
- Do not create tester accounts yet.
- Do not send renewal or onboarding emails yet.
- Do not add a public route or custom domain without a separate exact approval gate.
- Do not commit hostnames, account IDs, Access IDs, deployment IDs, version IDs, tester emails, tokens or keys.

## Private Evidence Boundary

Runtime evidence is stored only as ignored local booleans in:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-real-app-deploy.local.json
```

The local file must not include URLs, hostnames, account IDs, Access IDs, policy IDs, deployment IDs, version IDs, tester emails, tokens or keys.

## Next Gate

```text
T10an_protected_tester_publication_target_gate
```

The next real step is to choose and verify the protected publication target before any tester receives access.

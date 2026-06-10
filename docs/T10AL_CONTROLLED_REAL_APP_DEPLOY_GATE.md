# T10al Controlled Real App Deploy Gate

## Objective

T10al prepares the exact gate for one future controlled deployment of the real OpenNext tester portal to the already protected Cloudflare Worker target.

This phase does not deploy the real app. It only defines the required approvals, checks, rollback and post-deploy verification.

## Current Protected Preconditions

The real deploy gate depends on these completed controls:

- T10ajn created only the harmless workers.dev shell target.
- T10ajo verified anonymous traffic is intercepted by Cloudflare Access before the shell body.
- T10ak verified the Access application/policy boundary from ignored local evidence.

## Exact Future Approval Phrase

The real deploy must not be executed unless the operator writes this exact approval in chat:

```text
AUTORIZO T10al-deploy-real-app: ejecutar un unico wrangler deploy --config wrangler.jsonc para sqx-edge-tester-portal-preview, verificar Access antes de publicar URL, y hacer rollback si falla.
```

## Exact Future Deploy Command

Run only after the exact approval phrase:

```powershell
npm exec -- wrangler deploy --config wrangler.jsonc
```

## Required Prechecks

Run from `templates/SQX_Edge_Tester_Portal` before the future deploy:

```powershell
npm run proof:cloudflare-access-policy-boundary
npm run proof:cloudflare-workers-dev-access
npm run proof:cloudflare-hostname-zone-selection
npm run cf:build
npm run typecheck
```

Required state:

- `proof:cloudflare-access-policy-boundary` returns `GO_ACCESS_APPLICATION_POLICY_BOUNDARY_VERIFIED_NO_APP_DEPLOY`.
- `proof:cloudflare-workers-dev-access` returns `GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_VERIFIED_NO_APP`.
- `proof:cloudflare-hostname-zone-selection` returns `GO_CLOUDFLARE_HOSTNAME_ZONE_READY_T10AK_ALLOWED`.
- `wrangler.jsonc` keeps `workers_dev=false`.
- `wrangler.jsonc` keeps `preview_urls=false`.
- `package.json` still has no direct `deploy` or `cf:deploy` script.

## Immediate Post-Deploy Checks

After the future deploy, before sharing any tester URL:

1. Probe anonymous access with redirects disabled.
2. Confirm Cloudflare Access intercepts before the app response.
3. Confirm no direct app body is visible anonymously.
4. Confirm the Worker deployment target is the expected protected Worker.
5. Confirm no custom/public domain was added.
6. Confirm no tester URL was sent.

## Rollback Rule

If any post-deploy check fails, rollback immediately with Wrangler deployment/version controls and do not share the URL.

Rollback acceptance requires:

- The unsafe deployment is no longer active.
- Anonymous traffic is blocked by Cloudflare Access again.
- No tester URL was published.
- The rollback evidence is recorded without hostnames, account IDs, Access IDs, URLs, emails, tokens or keys.

## Gate Result

```text
GO_CONTROLLED_REAL_APP_DEPLOY_GATE_READY_EXACT_APPROVAL_REQUIRED
```

## Blocked Actions

- No real app deployment in T10al.
- No tester URL sharing.
- No tester account creation.
- No renewal emails.
- No public route/domain publication.
- No Git-connected Cloudflare deploy automation.

## Next Gate

```text
T10am_controlled_real_app_deploy_and_access_smoke
```

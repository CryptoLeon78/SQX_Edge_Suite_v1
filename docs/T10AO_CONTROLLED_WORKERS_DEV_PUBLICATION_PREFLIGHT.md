# T10ao Controlled Workers.dev Publication Preflight

## Objective

T10ao prepares the controlled `workers.dev` publication step for the Cloudflare tester portal without publishing the tester URL, without creating tester accounts and without changing `wrangler.jsonc`.

This phase is the last local gate before the external action. It exists because the next action can expose a reachable Worker hostname if Cloudflare Access is not first in the request path.

## Current Safe State

- `wrangler.jsonc` keeps `workers_dev=false`.
- `wrangler.jsonc` keeps `preview_urls=false`.
- `wrangler.jsonc` has no committed `routes`.
- No package `deploy` or `cf:deploy` script exists.
- No tester URL has been shared.
- No tester account has been created.
- No tester email has been committed.
- No custom domain is committed.

## Required Prechecks

Run from `templates/SQX_Edge_Tester_Portal` immediately before any future publication:

```powershell
npm run proof:cloudflare-access-policy-boundary
npm run proof:cloudflare-workers-dev-access
npm run proof:cloudflare-real-app-deploy-result
npm run proof:cloudflare-protected-tester-publication-target
npm run proof:cloudflare-controlled-workers-dev-publication-preflight
npm run typecheck
npm run cf:build
```

## Exact Approval Required

Do not publish the tester target unless the operator writes this exact approval in chat:

```text
AUTORIZO T10ao-publish-protected-workers-dev: activar workers_dev=true solo para sqx-edge-tester-portal-preview, ejecutar un unico npm exec -- wrangler deploy --config wrangler.jsonc, verificar Cloudflare Access antes de compartir URL, y hacer rollback/desactivar si falla.
```

## Publication Command

Only after the exact approval phrase:

```powershell
npm exec -- wrangler deploy --config wrangler.jsonc
```

The publication step must be a single controlled deploy after changing only `workers_dev=true`. Keep `preview_urls=false` and no custom `routes`.

## Verification After Publication

Before sharing any tester URL:

1. Probe the Worker route anonymously with redirects disabled.
2. Confirm Cloudflare Access intercepts before any app body is returned.
3. Confirm the app still requires its own tester session after Access.
4. Confirm no preview URL or custom route was created.
5. Record only redacted local evidence outside Git.

## Rollback Rule

Rollback immediately if any of these are true:

- Anonymous traffic can see the app body.
- Cloudflare Access does not intercept first.
- `preview_urls` becomes enabled.
- A custom/public route is added unexpectedly.
- Tester URL is exposed before verification.
- The deploy output creates a public target that is not covered by Access.

Rollback acceptance requires restoring `workers_dev=false` or rolling back to the last safe Worker version and recording only redacted local evidence.

## Gate Result

```text
GO_CONTROLLED_WORKERS_DEV_PUBLICATION_PREFLIGHT_READY_EXACT_APPROVAL_REQUIRED
```

## Next Gate

```text
T10ap_controlled_workers_dev_publication_and_access_smoke
```

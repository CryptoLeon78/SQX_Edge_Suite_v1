# T10an Protected Tester Publication Target Gate

## Objective

T10an chooses the protected publication target for the Cloudflare tester portal after T10am uploaded the real app version without opening a public target.

This phase does not publish a tester URL, does not create tester accounts and does not change `wrangler.jsonc`.

## Selected Target

```text
workers_dev_access_protected_publication_target
```

The selected first tester target is the existing Cloudflare `workers.dev` Worker hostname protected by Cloudflare Access.

Reasons:

- No custom domain is currently available.
- T10ajo and T10ak verified Cloudflare Access coverage for the existing `workers.dev` shell boundary.
- T10am uploaded the real OpenNext app version without opening a public target.
- Keeping `workers_dev=false` until the exact publication action avoids accidental URL exposure.

## Current Safe State

- `wrangler.jsonc` keeps `workers_dev=false`.
- `wrangler.jsonc` keeps `preview_urls=false`.
- `wrangler.jsonc` has no committed `routes`.
- No tester URL has been shared.
- No tester account has been created.
- No tester email has been committed.
- No custom domain is committed.

## Required Prechecks Before Publication

Run from `templates/SQX_Edge_Tester_Portal` before any future protected publication:

```powershell
npm run proof:cloudflare-access-policy-boundary
npm run proof:cloudflare-workers-dev-access
npm run proof:cloudflare-real-app-deploy-result
npm run typecheck
npm run cf:build
```

Required state:

- Access boundary remains verified.
- Real app deploy result remains `GO_REAL_APP_VERSION_UPLOADED_NO_PUBLIC_TARGET_NO_TESTER_URL`.
- No package `deploy` or `cf:deploy` script exists.
- No URL, hostname, account ID, Access ID, deployment ID, version ID, tester email, token or key is committed.

## Exact Future Approval Phrase

Do not publish the tester target unless the operator writes this exact approval in chat:

```text
AUTORIZO T10ao-publish-protected-workers-dev: activar workers_dev=true solo para sqx-edge-tester-portal-preview, ejecutar un unico npm exec -- wrangler deploy --config wrangler.jsonc, verificar Cloudflare Access antes de compartir URL, y hacer rollback/desactivar si falla.
```

## Future Publication Action

Only after the exact approval phrase:

1. Change `wrangler.jsonc` to `workers_dev=true` while keeping `preview_urls=false` and no custom `routes`.
2. Run one controlled `npm exec -- wrangler deploy --config wrangler.jsonc`.
3. Probe the resulting route anonymously with redirects disabled.
4. Confirm Cloudflare Access intercepts before any app body is returned.
5. Confirm authenticated app routes still require app session auth after Access.
6. Do not share the URL until Access and app auth are both verified.

## Rollback Rule

Rollback immediately if any of these are true:

- Anonymous traffic can see the app body.
- Cloudflare Access does not intercept first.
- `preview_urls` becomes enabled.
- A custom/public route is added unexpectedly.
- Tester URL is exposed before verification.

Rollback acceptance requires restoring `workers_dev=false` or rolling back to the last safe Worker version and recording only redacted local evidence.

## Gate Result

```text
GO_PROTECTED_TESTER_PUBLICATION_TARGET_SELECTED_EXACT_APPROVAL_REQUIRED
```

## Next Gate

```text
T10ao_controlled_workers_dev_publication_preflight
```

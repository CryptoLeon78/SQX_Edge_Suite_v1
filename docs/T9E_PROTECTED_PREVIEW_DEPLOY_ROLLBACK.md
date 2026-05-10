# T9e Protected Preview Deploy Rollback

## Objective

T9e retries a protected preview deploy only after T9d verified Vercel Authentication Standard Protection.

The retry was intentionally guarded: if Vercel reported a production target or production aliases, the deployment had to be removed immediately and no URL could be shared.

## External Action Performed

Pre-deploy gates:

- `npm run preflight:vercel-preview` returned OK.
- `npm run audit:vercel-protection` returned `GO_PROTECTION_VERIFIED`.
- Vercel Authentication remained enabled with `ssoProtection.deploymentType = prod_deployment_urls_and_all_previews`.

Deploy command:

```text
vercel deploy
```

The command was run without `--prod` and with demo/admin flags disabled. Despite that, Vercel reported:

```text
target = production
production alias created = true
```

This violated the T9e preview-only boundary, so the deployment was removed immediately.

## Rollback Result

Rollback verification:

- Deployment is no longer inspectable.
- Project list shows latest production URL: none.
- Public alias check returned `404`.
- No Vercel URL is committed.
- No tester invite is sent.
- No renewal email is sent.
- No production database is connected.

T9e is accepted as a successful safety rollback, not as a successful tester preview.

## Finding

For this linked project, local CLI deploys are not safe enough for tester rollout because they produced a production target even without `--prod`.

The next attempt must not use the same local CLI deploy path. The safer next path is a Git/PR-based preview or a Vercel API deployment path that can prove `target = preview` before any URL is shared.

T9f is therefore tracked as Git/PR-based preview or API deployment proof before any tester URL is shared.

## Required Next Step

T9f should prepare a preview-only deployment path that cannot auto-alias production:

1. Prefer a Git-connected private tester portal repo and non-production branch preview.
2. Confirm the Vercel production branch is not the working preview branch.
3. Keep Vercel Authentication Standard Protection enabled.
4. Deploy from the branch/PR preview mechanism or an API path with explicit target inspection.
5. Roll back immediately if any production target or alias appears.

## Security Boundary

- No active deployment remains from T9e.
- No public/protected URL is committed.
- No raw tester emails are committed.
- No tester access is created.
- No emails are sent.
- No production database is connected.
- `.vercel` remains ignored local state.

## Verification

T9e is accepted when:

- this rollback document exists
- roadmap/governance point to T9f
- static tests assert the rollback contract
- full backend tests pass
- `git diff --check` passes

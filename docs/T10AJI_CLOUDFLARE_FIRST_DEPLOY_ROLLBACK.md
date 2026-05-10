# T10aji Cloudflare First Deploy Rollback

## Objective

T10aji executes the first controlled Cloudflare Worker deploy attempt after broad Txxx authorization, then inspects and cleans up immediately before any tester URL is shared.

## Result

```text
NO_GO_FIRST_WORKER_DEPLOY_ROLLED_BACK_WORKERS_DEV_SUBDOMAIN_REQUIRED
```

The deploy command uploaded Worker assets and created Worker versions/deployments, but Cloudflare refused to publish because the account does not have a `workers.dev` subdomain registered and no route/custom domain is configured.

Because post-attempt inspection showed deploy/version records with preview capability, the Worker was deleted immediately.

## Commands Executed

Prechecks:

```powershell
npm run proof:cloudflare-first-deploy-readiness
npm run cf:build
npm exec --yes -- wrangler deployments list --name sqx-edge-tester-portal-preview --json
npm exec --yes -- wrangler versions list --name sqx-edge-tester-portal-preview --json
```

First deploy attempt:

```powershell
npm exec --yes -- wrangler deploy --name sqx-edge-tester-portal-preview
```

Immediate cleanup:

```powershell
npm exec --yes -- wrangler delete sqx-edge-tester-portal-preview --force
```

Post-cleanup inspection:

```powershell
npm exec --yes -- wrangler deployments list --name sqx-edge-tester-portal-preview --json
npm exec --yes -- wrangler versions list --name sqx-edge-tester-portal-preview --json
npm exec --yes -- wrangler secret list --name sqx-edge-tester-portal-preview --format json
```

## Evidence Summary

```text
precheck_worker_state=worker_not_found
local_build=passed
deploy_command_started=true
deploy_command_exit_code=1
assets_uploaded=true
worker_versions_seen_after_attempt=true
worker_deployments_seen_after_attempt=true
preview_capability_seen_after_attempt=true
workers_dev_subdomain_required=true
tester_url_shared=false
cleanup_command_executed=true
post_cleanup_worker_state=worker_not_found
```

The raw Wrangler output included private account details and was not committed.

## Security Boundary Preserved

- No Cloudflare Worker remains after cleanup.
- No Cloudflare deployment remains after cleanup.
- No Cloudflare version remains after cleanup.
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

## Decision

Do not retry `wrangler deploy` until one of these is deliberately selected:

- register a Cloudflare `workers.dev` subdomain, then protect/share only after Cloudflare Access and app auth are verified
- configure a custom route/domain that can be protected by Cloudflare Access before any tester sharing
- choose a different provider/route if Cloudflare cannot satisfy the controlled tester-access boundary

## Next Gate

```text
T10ajj_cloudflare_route_onboarding_decision
```

T10ajj must decide the route/onboarding path before any new deploy attempt.

## Verification

T10aji is accepted when:

- this document exists
- `scripts/cloudflare-first-deploy-rollback-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-first-deploy-rollback`
- the proof returns `NO_GO_FIRST_WORKER_DEPLOY_ROLLED_BACK_WORKERS_DEV_SUBDOMAIN_REQUIRED`
- post-cleanup read-only checks return `worker_not_found`
- no provider token, account ID, tester email or tester URL appears in tracked public files
- static tests and full pytest pass
- `git diff --check` passes

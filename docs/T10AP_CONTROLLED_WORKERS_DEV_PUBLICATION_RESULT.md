# T10ap Controlled Workers.dev Publication Result

## Objective

T10ap executes the approved controlled `workers.dev` publication for the Cloudflare tester portal, verifies Cloudflare Access before any app body is visible and keeps tester URL sharing blocked.

This phase executed exactly one external deploy command after the exact approval phrase was provided.

## Executed Command

```powershell
npm exec -- wrangler deploy --config wrangler.jsonc
```

The deploy was executed once from `templates/SQX_Edge_Tester_Portal`.

## Result

```text
GO_CONTROLLED_WORKERS_DEV_PUBLICATION_ACCESS_PROTECTED_NO_URL_SHARED
```

Public-safe result:

- The real OpenNext Worker was deployed to the selected `workers.dev` target.
- Anonymous `/`, `/api/health` and `/portal` requests were intercepted by Cloudflare Access with redirects disabled.
- No anonymous app body was visible.
- No preview URL was enabled.
- No custom route was added.
- No tester URL was shared.
- No tester account was created.
- No tester email, hostname, URL, account ID, Access ID, deployment ID, version ID, token or key is committed.
- Rollback was not required.

## Local Evidence

The redacted local evidence file is intentionally ignored by Git:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-workers-dev-publication.local.json
```

It records only booleans and command-count evidence. It must not include hostnames, URLs, account IDs, Access IDs, deployment IDs, version IDs, tester emails, tokens or keys.

## Repository Safety

After the single successful deploy and Access smoke, the repository config was restored to the safe default:

```json
"workers_dev": false
```

No second deploy was run after restoring the local config. The remote publication result is recorded only through ignored redacted evidence.

## Next Gate

```text
T10aq_tester_access_handoff_without_public_url_leak
```

# T10af OpenNext Cloudflare Adapter Package

## Objective

T10af prepares the tester portal template for a local Cloudflare Workers/OpenNext package without any provider action.

This phase may add local package configuration, local scripts and local proof evidence. It does not create a Cloudflare project, does not connect GitHub to Cloudflare, does not create a Cloudflare Access application or policy, does not deploy and does not publish a tester URL.

## Official Sources Checked

- Cloudflare Workers Next.js guide: https://developers.cloudflare.com/workers/frameworks/framework-guides/nextjs/
- Cloudflare Workers automatic configuration guide: https://developers.cloudflare.com/workers/framework-guides/automatic-configuration/
- Cloudflare Wrangler install guide: https://developers.cloudflare.com/workers/wrangler/install-and-update/
- OpenNext Cloudflare adapter guide: https://opennext.js.org/cloudflare
- OpenNext Cloudflare get started guide: https://opennext.js.org/cloudflare/get-started

## Local Package Shape

Files added to `templates/SQX_Edge_Tester_Portal/`:

- `wrangler.jsonc`
- `open-next.config.ts`
- `.dev.vars.example`
- `scripts/opennext-cloudflare-adapter-proof.mjs`

Package scripts added:

- `proof:opennext-cloudflare-adapter`
- `cf:build`
- `cf:preview`
- `cf:typegen`

Package dev dependencies added:

- `@opennextjs/cloudflare`
- `wrangler`

## Safe Script Boundary

No Cloudflare deploy script is exposed in this phase.

Allowed local commands:

```powershell
npm run proof:opennext-cloudflare-adapter
npm run cf:build
npm run cf:preview
npm run cf:typegen
```

Forbidden until an explicit later approval:

- Cloudflare project creation.
- Cloudflare deployment creation.
- Cloudflare Access application creation.
- Cloudflare Access policy creation.
- GitHub repository connection to Cloudflare.
- Tester URL publication.
- Tester account creation.
- Renewal email delivery.
- Production database connection.

## Wrangler Configuration Boundary

The committed `wrangler.jsonc` contains only local Worker/OpenNext shape:

- `main` points to `.open-next/worker.js`.
- static assets point to `.open-next/assets`.
- `nodejs_compat` and `global_fetch_strictly_public` are enabled.
- `WORKER_SELF_REFERENCE` points to the same local Worker name.
- observability is enabled.

The file intentionally does not include account identifiers, zone identifiers, custom routes, custom domains, secrets, tester emails or provider-specific publication state.

## Local Environment Boundary

`.dev.vars.example` is committed with only:

```text
NEXTJS_ENV=development
```

`.dev.vars` remains ignored because it may contain local-only runtime values in a future smoke phase.

Generated Cloudflare/OpenNext artifacts remain ignored:

- `.open-next/`
- `.wrangler/`
- `cloudflare-env.d.ts`
- `.dev.vars*`

## Decision

```text
GO_OPENNEXT_CLOUDFLARE_ADAPTER_LOCAL_PACKAGE_READY_NO_DEPLOY
```

Next gate:

```text
T10ag_local_opennext_build_preview_smoke_no_provider_action
```

T10ag may run a local OpenNext build/preview smoke against the prepared package, still without provider project creation, deployment, Access policy creation or tester URL publication.

## Security Boundary

- No Cloudflare project was created.
- No Cloudflare deployment was created.
- No Cloudflare Access application or policy was created.
- No GitHub repository was connected to Cloudflare.
- No Cloudflare token or account ID was committed.
- No tester URL was shared.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.

## Verification

T10af is accepted when:

- this document exists
- `wrangler.jsonc` exists and contains only local OpenNext Worker shape
- `open-next.config.ts` exists and uses `defineCloudflareConfig()`
- `.dev.vars.example` exists while `.dev.vars` remains ignored
- no source file exports `runtime = "edge"`
- `package.json` includes `@opennextjs/cloudflare` and `wrangler` as dev dependencies
- `package.json` exposes local Cloudflare build/preview/typegen scripts but no Cloudflare deploy script
- `scripts/opennext-cloudflare-adapter-proof.mjs` returns `GO_OPENNEXT_CLOUDFLARE_ADAPTER_LOCAL_PACKAGE_READY_NO_DEPLOY`
- docs and roadmap point to T10ag as the local build/preview smoke phase
- typecheck and static tests pass
- sensitive scan finds no tester emails, secrets, provider tokens, deployment URLs or account IDs in touched public files
- `git diff --check` passes

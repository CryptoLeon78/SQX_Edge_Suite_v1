# T10ai Cloudflare Provider Project Preflight

## Objective

T10ai prepares the Cloudflare provider-project preflight for the tester portal after T10ag confirmed the local OpenNext/Workers smoke and T10ah blocked the `proxy.ts` migration for the current Cloudflare route.

This is a no-deploy, no-provider-action phase. It does not create a Cloudflare project, does not connect GitHub, does not create a Cloudflare Access application or policy, does not publish any tester URL and does not create tester accounts.

## Official Sources Checked

- Cloudflare Workers Next.js guide: https://developers.cloudflare.com/workers/framework-guides/web-apps/nextjs/
- Cloudflare Workers Wrangler deploy command: https://developers.cloudflare.com/workers/wrangler/commands/workers/
- Cloudflare Workers Wrangler configuration: https://developers.cloudflare.com/workers/wrangler/configuration/
- OpenNext Cloudflare CLI: https://opennext.js.org/cloudflare/cli
- Cloudflare Access One-time PIN: https://developers.cloudflare.com/cloudflare-one/identity/one-time-pin/

## Selected Shape

```text
provider=Cloudflare
runtime=cloudflare_workers_opennext_nextjs_runtime
project_name_proposal=sqx-edge-tester-portal-preview
worker_name_proposal=sqx-edge-tester-portal-preview
production_branch=main
tester_branch=tester-preview
access_gate=Cloudflare Access OTP or equivalent IdP
inner_gate=SQX tester auth/session/renewal/watermark/kill-switch
deploy_script=absent until exact approval
tester_url_publication=forbidden_until_go
```

## Local Contract

Allowed local-only commands before any external action:

- `npm install --no-package-lock`
- `npm run proof:cloudflare-provider-project-preflight`
- `npm run proof:opennext-cloudflare-adapter`
- `npm run proof:opennext-local-smoke`
- `npm run proof:next-proxy-migration`
- `npm run cf:build`
- `npx opennextjs-cloudflare preview`
- `npx wrangler whoami`

Forbidden until Ivan gives exact approval for that external action:

- `npx wrangler deploy`
- `npm run deploy`
- `npx opennextjs-cloudflare deploy`
- `npx wrangler pages deploy`
- Cloudflare project creation
- Cloudflare deployment creation
- Cloudflare Access application creation
- Cloudflare Access policy creation
- GitHub repository connection to Cloudflare
- tester URL publication
- tester account creation
- tester email commit
- renewal email delivery
- production database connection

## Required Cloudflare Settings Before Any URL

- Use the private tester portal repository only; never connect the public app repo as the tester source.
- Keep production branch as `main`.
- Use `tester-preview` as the only pilot branch.
- Keep custom domains absent until Access coverage is proven on the exact surface to be shared.
- Enable Cloudflare Access before any tester surface is shared.
- Use One-time PIN or an equivalent identity provider method.
- Store allowed tester emails only in Cloudflare/private provider configuration.
- Keep SQX app auth as the inner gate; Cloudflare Access is not a replacement for tester auth, renewal state, audit, watermark or kill switch.
- Inspect any future deployment for branch, target, Access coverage and accidental production/custom-domain exposure before sharing a URL.

## Result

```text
GO_CLOUDFLARE_PROVIDER_PROJECT_PREFLIGHT_READY_NO_DEPLOY
```

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

## Decision

Next gate:

```text
T10aj_cloudflare_project_shell_exact_approval_or_keep_local
```

T10aj may create or verify a Cloudflare project shell only if Ivan gives exact approval for that external action. If there is no exact approval, the track stays local and continues hardening docs/proofs.

## Verification

T10ai is accepted when:

- this document exists
- `scripts/cloudflare-provider-project-preflight-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-provider-project-preflight`
- the proof returns `GO_CLOUDFLARE_PROVIDER_PROJECT_PREFLIGHT_READY_NO_DEPLOY`
- `wrangler.jsonc` keeps local runtime config without account ID, zone ID, routes or custom domains
- no deploy script or deploy command fragment is exposed in `package.json`
- docs and roadmap point to T10aj as exact-approval provider shell or keep-local gate
- static tests and full pytest pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets, provider tokens, deployment URLs or account IDs in touched public files
- temporary npm/OpenNext/Wrangler artifacts are cleaned
- `git diff --check` passes

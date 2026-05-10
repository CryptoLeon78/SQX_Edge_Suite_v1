# T10ad Cloudflare Access Preflight

## Objective

T10ad prepares the Cloudflare Access preflight package selected by T10ac.

This is a no-deploy, no-provider-action phase. It defines the exact guardrails required before creating any Cloudflare project, connecting any repository, creating any Access policy, sharing any tester URL or inviting any tester.

## Official Sources Checked

- Cloudflare Pages Git integration: https://developers.cloudflare.com/pages/configuration/git-integration/
- Cloudflare Pages branch deployment controls: https://developers.cloudflare.com/pages/configuration/branch-build-controls/
- Cloudflare Pages preview deployments: https://developers.cloudflare.com/pages/configuration/preview-deployments/
- Cloudflare Access one-time PIN login: https://developers.cloudflare.com/cloudflare-one/identity/one-time-pin/
- Cloudflare Access policies: https://developers.cloudflare.com/cloudflare-one/policies/access/
- Cloudflare Next.js guide: https://developers.cloudflare.com/pages/framework-guides/nextjs/
- Cloudflare static Next.js guide: https://developers.cloudflare.com/pages/framework-guides/nextjs/deploy-a-static-nextjs-site/

## Proposed Provider Shape

```text
provider=Cloudflare
route=cloudflare_pages_preview_with_cloudflare_access_email_otp
project_name_proposal=sqx-edge-tester-portal-preview
production_branch=main
tester_branch=tester-preview
previewBranchControlMode=custom_branches_only
custom_domains=none_until_access_coverage_is_proven
tester_url_publication=forbidden_until_go
```

## Required Cloudflare Configuration

Cloudflare Pages:

- Create the project only after explicit approval for that exact external action.
- Connect only the private tester portal repository, never the public application repository.
- Production branch must be `main`.
- Tester branch must be `tester-preview`.
- Automatic production branch deployments should stay disabled until a dedicated production rollout exists.
- Preview branch control must use custom branches and include only `tester-preview` for the pilot.
- No custom domain may be added until Access coverage is proven on the exact surface that will be shared.
- Any preview deployment must be inspected for expected branch, no production alias and no unintended custom-domain exposure before sharing.

Cloudflare Access:

- Enable an Access policy before any tester surface is shared.
- Use One-time PIN or an equivalent identity provider method.
- Store allowed tester emails only in private/provider configuration, never in this public repository.
- Access policy must allow only approved tester identities and Ivan/operator identities.
- Denied, expired or removed testers must be removed from the Access allow list before the next renewal window.
- Cloudflare Access is an outer gate only; the portal's own tester auth, 15-day renewal state, audit trail, watermark and kill switch remain mandatory.

Indexing and URL exposure:

- Preview indexing must be checked for noindex posture before any tester URL is shared.
- The Pages production surface must remain unshared and unused during the tester pilot.
- If a `pages.dev` production surface is created by the provider, it must not be treated as approved tester access until separately protected or intentionally retired.

## Runtime Compatibility Gate

Current `templates/SQX_Edge_Tester_Portal` is a Next.js App Router project with route handlers and middleware. Cloudflare documentation separates static Next.js Pages deployment from full stack Server Side Rendered Next.js deployment.

Therefore, T10ae must run a local no-provider-action compatibility decision before any Cloudflare project is created:

- Decide whether the tester portal will be converted to static export for Cloudflare Pages.
- Or decide whether the Cloudflare route must use the Workers/Next.js runtime path instead of static Pages.
- Verify that auth/session, middleware, API route handlers, security headers and renewal/admin previews still work in the selected runtime model.
- Do not create a Cloudflare project until this compatibility decision is documented and tested.

## T10ae Entry Gate

```text
T10ae_cloudflare_runtime_compatibility_no_provider_action
```

T10ae must be local-only unless Ivan explicitly approves a specific external action later. It may inspect package scripts, Next.js config and Cloudflare docs, but it must not create a Cloudflare project, deployment, Access application, Access policy or URL.

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

T10ad is accepted when:

- this document exists
- `scripts/cloudflare-access-preflight-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-access-preflight`
- the proof returns `GO_CLOUDFLARE_ACCESS_PREFLIGHT_READY_NO_DEPLOY`
- docs and roadmap point to T10ae as the local runtime compatibility decision before any Cloudflare provider action
- static tests assert that no Cloudflare project, Access policy, deployment, tester URL or tester emails exist in public files
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

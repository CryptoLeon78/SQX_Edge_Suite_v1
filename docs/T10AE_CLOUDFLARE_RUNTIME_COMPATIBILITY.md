# T10ae Cloudflare Runtime Compatibility

## Objective

T10ae decides the Cloudflare runtime path for the tester portal before any Cloudflare provider action.

This is a local-only compatibility decision. It does not install Cloudflare dependencies, does not create a Cloudflare project, does not connect GitHub, does not create an Access policy, does not deploy and does not publish a tester URL.

## Official Sources Checked

- Cloudflare Workers Next.js guide: https://developers.cloudflare.com/workers/frameworks/framework-guides/nextjs/
- Cloudflare Pages Next.js guide: https://developers.cloudflare.com/pages/framework-guides/nextjs/
- Cloudflare static Next.js guide: https://developers.cloudflare.com/pages/framework-guides/nextjs/deploy-a-static-nextjs-site/
- Cloudflare Pages Functions: https://developers.cloudflare.com/pages/functions/
- Cloudflare Pages Functions middleware: https://developers.cloudflare.com/pages/functions/middleware/

## Local Inventory

The current tester portal template is not a plain static site.

Runtime-dependent files:

- `src/middleware.ts`
- `src/app/api/health/route.ts`
- `src/app/api/auth/login/route.ts`
- `src/app/api/auth/logout/route.ts`
- `src/app/api/tester/features/route.ts`
- `src/app/api/tester/renewal/route.ts`
- `src/app/api/admin/testers/route.ts`
- `src/app/api/cron/expire-testers/route.ts`

Runtime-dependent behavior:

- Session cookie handling.
- Login/logout route handlers.
- Protected-route middleware.
- Security headers.
- Kill switch and rate limiting.
- Tester entitlement and renewal API previews.
- Admin tester console API preview.
- Cron-style expiry dry run.

## Decision

```text
GO_CLOUDFLARE_WORKERS_OPENNEXT_RUNTIME_SELECTED_NO_PROVIDER_ACTION
```

Selected runtime path:

```text
cloudflare_workers_opennext_nextjs_runtime
```

Rejected runtime path:

```text
cloudflare_pages_static_export
```

Rationale:

- Static export would remove or bypass the current API route handlers.
- Static export would not preserve the current Next.js middleware gate as-is.
- The tester portal is an auth/session/admin/renewal surface, not just a brochure page.
- Cloudflare's current Next.js Workers guide is the better match for App Router, route handlers, middleware and full-stack behavior.

## T10af Entry Gate

```text
T10af_opennext_cloudflare_adapter_local_package_no_deploy
```

T10af may prepare local adapter files and dependencies for Cloudflare Workers/OpenNext, but it must remain no-deploy unless Ivan explicitly approves a later external action.

T10af must:

- Add or document the minimum OpenNext Cloudflare adapter package shape.
- Keep deploy scripts disabled or clearly separated from local build/preview scripts.
- Avoid committing Cloudflare tokens, account IDs, project IDs, tester emails or URLs.
- Keep `main` as production branch and `tester-preview` as tester branch in docs.
- Preserve Cloudflare Access OTP as an outer gate and app auth as the inner gate.
- Run typecheck and local static tests.
- Stop before any Cloudflare provider project, deployment, Access application, Access policy or GitHub provider connection.

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

T10ae is accepted when:

- this document exists
- `scripts/cloudflare-runtime-compatibility-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-runtime-compatibility`
- the proof returns `GO_CLOUDFLARE_WORKERS_OPENNEXT_RUNTIME_SELECTED_NO_PROVIDER_ACTION`
- docs and roadmap point to T10af as the local OpenNext/Cloudflare adapter package phase
- static tests assert that static export remains rejected while route handlers and middleware exist
- backend tests pass
- tester portal typecheck passes
- sensitive scan finds no tester emails, secrets or deployment URLs in touched public files
- `git diff --check` passes

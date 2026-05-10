# T2 Tester Portal Bootstrap

## Objective

T2 turns the T1 cloud tester architecture into a public-safe bootstrap template for the future private `SQX_Edge_Tester_Portal` repository.

This phase creates structure only. It does not deploy to Vercel, create a GitHub repository, create tester accounts, send emails, rotate passwords, publish URLs or add real tester data.

Explicit non-goals:

- No Vercel deployment.
- No tester accounts.
- No production database.

## Active Ownership

- Access/Security Gatekeeper: auth/session boundary, tester lifecycle placeholders, anti-distribution controls.
- Architecture/Docs: repo boundary, T-track roadmap, template map and loadable contract.
- Security/Distribution: no secrets, no real tester data, `.env.example` only.
- QA/Release: static contract tests and full backend test suite.

## Bootstrap Location

Template path:

`templates/SQX_Edge_Tester_Portal/`

This path is tracked as a safe starter kit. The actual private repository should be created only after explicit approval and then populated from this template.

## Template Map

| Path | Purpose |
| --- | --- |
| `README.md` | Private repo bootstrap instructions and non-goals. |
| `.gitignore` | Keeps `.env`, Vercel metadata, build output and dependencies out of git. |
| `.env.example` | Placeholder-only environment contract. |
| `package.json` | Next.js App Router dependency and script baseline. |
| `next.config.mjs` | Minimal hardened Next.js defaults. |
| `vercel.json` | Vercel framework marker and dry-run cron registration. |
| `src/app/page.tsx` | Public-safe entry/gate screen. |
| `src/app/portal/page.tsx` | Protected placeholder for future tester Pro surface. |
| `src/app/expired/page.tsx` | Expired/blocked tester screen placeholder. |
| `src/app/renewal/page.tsx` | Manual renewal pending screen placeholder. |
| `src/app/api/health/route.ts` | Non-sensitive health route. |
| `src/app/api/cron/expire-testers/route.ts` | Dry-run cron endpoint protected by `CRON_SECRET`. |
| `src/lib/access-contract.ts` | T1/T2 statuses, `tester_pro` entitlement helper and watermark helper. |
| `src/lib/security-headers.ts` | Baseline browser protection headers. |
| `src/middleware.ts` | Protected route gate and security-header application retained for current OpenNext/Cloudflare compatibility. |

## Security Boundary

The template intentionally contains:

- No real email addresses.
- No tester names.
- No database URLs.
- No passwords.
- No Vercel project IDs.
- No deployment URLs.
- No checkout, license or buyer evidence.

`.env.example` documents the future secret names, but every value is a placeholder.

## Alignment With Official Platform Defaults

The bootstrap follows the current official Next.js recommendation to use App Router, TypeScript and `next@latest react@latest react-dom@latest` for a new app starter. Vercel-specific behavior remains limited to `vercel.json`, protected cron placeholder and middleware-ready security boundaries.

References:

- Next.js installation: https://nextjs.org/docs/app/getting-started/installation
- Next.js on Vercel: https://vercel.com/frameworks/nextjs

## Verification

T2 is accepted when:

- The template contains the required Next.js/Vercel files.
- Secret placeholders remain placeholders.
- Protected routes are represented in middleware.
- The dry-run cron route requires `CRON_SECRET`.
- Governance, roadmap, README and changelog point to T2/T3 correctly.
- Static and backend tests pass.

## Next Phase

T3 should define the auth data contract before real login code exists:

- Tester table/schema.
- Password hash policy.
- Session cookie contract.
- Renewal token contract.
- Audit event schema.
- Secret ownership and private repo/data boundaries.

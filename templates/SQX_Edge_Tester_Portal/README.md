# SQX Edge Tester Portal Bootstrap

Private-repo bootstrap for the future Vercel-hosted tester portal.

This template is safe to keep in the public/core repository because it contains no real tester data, no credentials, no deployment URL and no production database configuration.

## Purpose

- Host a controlled `tester_pro` experience for up to 10 invited testers.
- Require per-tester identity rather than a shared password.
- Support the 15-day renewal model defined in T1.
- Keep all tester data, audit events and secrets in private infrastructure.
- Prepare Vercel App Router structure without deploying anything yet.

## Non-Goals

- No Vercel deployment.
- No tester accounts.
- No real emails.
- No production database.
- No payment or license issuing.
- No public/protected URL publication.

## Manual Private Repo Bootstrap

1. Create `SQX_Edge_Tester_Portal` as a private repository only after explicit approval.
2. Copy this template into that repository root.
3. Run `npm install` in the private repository.
4. Copy `.env.example` to `.env.local` and replace every placeholder with private values.
5. Keep Vercel Deployment Protection enabled as an extra layer.
6. Do not invite testers until T3-T8 are completed and verified.

## Required Env Placeholders

- `AUTH_SECRET`: signs future sessions.
- `TESTER_DB_URL`: private database connection string for tester records.
- `CRON_SECRET`: protects scheduled expiry/renewal routes.
- `EDGE_CONFIG`: optional Vercel Edge Config connection string for kill switch and non-secret flags.
- `WATERMARK_SALT`: supports stable per-tester watermark IDs without exposing raw internals.
- `PASSWORD_PEPPER`: optional defense-in-depth secret if the final hash implementation enables peppering.
- `T4_DEMO_LOGIN_ENABLED`: local prototype flag; keep `false` unless testing the demo flow privately.
- `T4_DEMO_TESTER_EMAIL`: placeholder demo email for local testing only.
- `T4_DEMO_ACCESS_CODE`: placeholder demo access code for local testing only; not a production password.
- `T5_DEMO_TESTER_PRO_ENABLED`: local entitlement flag; keep `false` unless validating gates privately.
- `T6_DEMO_RENEWAL_STATE`: local renewal state flag; keep `pending_renewal` unless validating lifecycle branches privately.
- `T7_DEMO_ADMIN_CONSOLE_ENABLED`: local admin preview flag; keep `false` unless validating operator screens privately.

## Current Skeleton

- `src/app/page.tsx`: public-safe gate screen.
- `src/app/login/page.tsx`: disabled-by-default demo login form.
- `src/app/portal/page.tsx`: protected placeholder surface.
- `src/app/admin/testers/page.tsx`: protected admin tester console preview.
- `src/app/expired/page.tsx`: expired/blocked tester state.
- `src/app/renewal/page.tsx`: renewal-review placeholder state.
- `src/app/api/health/route.ts`: non-sensitive health check.
- `src/app/api/auth/login/route.ts`: local demo login route that sets the session cookie only when explicitly enabled.
- `src/app/api/auth/logout/route.ts`: local demo logout route that clears the session cookie.
- `src/app/api/tester/features/route.ts`: server-side `tester_pro` feature gate prototype.
- `src/app/api/tester/renewal/route.ts`: server-side manual-preview renewal route for approve, deny and block decisions.
- `src/app/api/admin/testers/route.ts`: server-side operator-preview admin route for create, renew, deny, block and audit review.
- `src/app/api/cron/expire-testers/route.ts`: dry-run cron gate guarded by `CRON_SECRET`.
- `src/lib/access-contract.ts`: T1/T2 tester status and entitlement helpers.
- `src/lib/auth-data-contract.ts`: T3 password, session, renewal token and audit record contracts.
- `src/lib/session-prototype.ts`: T4 disabled-by-default session prototype helpers.
- `src/lib/entitlement-gates.ts`: T5 paid feature gate contract and demo-only entitlement evaluator.
- `src/lib/renewal-flow.ts`: T6 15-day expiry, renewal state and manual decision preview helpers.
- `src/lib/admin-console.ts`: T7 admin action preview helpers and demo tester rows.
- `src/lib/security-headers.ts`: baseline browser protection headers.
- `src/middleware.ts`: protected-route session gate and security headers.

## Next Phase

T8 can harden rate limiting, security headers, watermark, kill switch and deployment-protection checklist before any staging preview.

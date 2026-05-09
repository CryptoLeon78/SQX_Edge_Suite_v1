# T8 Tester Portal Security Hardening

## Objective

T8 hardens the tester portal template before any staging preview by adding rate-limit contracts, stronger security headers, visible tester watermark, global kill switch and a deployment-protection checklist.

T8 remains local and non-external. It does not deploy Vercel, create tester accounts, send emails, rotate passwords, connect a production database, publish URLs or mutate real tester records.

## Active Ownership

- Access/Security Gatekeeper: rate limiting, kill switch, watermark and protected route behavior.
- Backend/API: health route hardening summary and middleware denial contracts.
- Frontend/UI: visible watermark and protected portal hardening summary.
- Security/Distribution: no real tester identities, no secrets, no public URLs and no automatic external action.
- Architecture/Docs: roadmap, governance and living-contract updates.
- QA/Release: static tests, Next template typecheck, backend pytest, Playwright visual smoke and `git diff --check`.

## Implemented Template Files

| Path | Purpose |
| --- | --- |
| `src/lib/security-hardening.ts` | Defines `T8_GLOBAL_KILL_SWITCH_ENABLED`, rate-limit config, evaluator and visible watermark helper. |
| `src/lib/deployment-protection.ts` | Defines the required checklist before any Vercel preview or tester invite. |
| `src/middleware.ts` | Applies kill switch, rate-limit headers, 429/503 denial responses and security headers. |
| `src/lib/security-headers.ts` | Adds stronger browser protections and CSP directives. |
| `src/app/api/health/route.ts` | Reports T8 hardening state without exposing secrets or tester data. |
| `src/app/portal/page.tsx` | Shows visible demo tester watermark and hardening checklist count. |

## Hardening Env Contract

Defaults stay conservative:

- `T8_GLOBAL_KILL_SWITCH_ENABLED="false"`
- `T8_RATE_LIMIT_ENABLED="false"`
- `T8_RATE_LIMIT_MAX_REQUESTS="30"`
- `T8_RATE_LIMIT_WINDOW_SECONDS="60"`

The kill switch must be tested before pilot rollout. When enabled, non-exempt routes return `global_kill_switch_enabled` or redirect to the expired/access-review page.

Rate limiting is disabled by default in the public-safe template. When enabled privately, middleware returns `rate_limit_exceeded` with HTTP `429` for API requests and rate-limit response headers:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `Retry-After` on blocked requests

## Security Header Contract

T8 requires these headers:

- `X-Frame-Options = DENY`
- `X-Content-Type-Options = nosniff`
- `Referrer-Policy = strict-origin-when-cross-origin`
- `Permissions-Policy = camera=(), microphone=(), geolocation=()`
- `X-Robots-Tag = noindex, nofollow`
- `Strict-Transport-Security = max-age=31536000; includeSubDomains; preload`
- `Cross-Origin-Opener-Policy = same-origin`
- `Cross-Origin-Resource-Policy = same-origin`
- `Content-Security-Policy` with `form-action 'self'`, `frame-ancestors 'none'`, `base-uri 'self'` and `object-src 'none'`

## Watermark Contract

Protected tester surfaces must show a visible watermark generated through `buildVisibleWatermark`. The public-safe template uses only:

- `demo-tester-local-only`
- `tester@example.invalid`

Production must use per-tester identity and avoid hiding the watermark behind UI preferences.

## Deployment-Protection Checklist

`DEPLOYMENT_PROTECTION_CHECKLIST` requires:

- Vercel Deployment Protection enabled for preview and production
- tester auth enabled before sharing any URL
- kill switch tested before pilot
- rate limit tested before pilot
- no public indexing
- no tester invites or renewal emails without explicit approval
- no production database secrets committed
- watermark visible on protected tester surfaces

## Security Boundary

- No Vercel deployment.
- No tester account is created.
- No renewal email is sent.
- No production database is connected.
- No real tester identity is committed.
- No deployment or Vercel URL is published.
- No external action is automated.
- Health output exposes only hardening state and checklist names, never secrets.

## Verification

T8 is accepted when:

- `src/lib/security-hardening.ts` defines kill switch, rate-limit env and watermark helpers.
- `src/lib/deployment-protection.ts` defines `DEPLOYMENT_PROTECTION_CHECKLIST`.
- Middleware applies kill switch, rate limiting and security headers.
- Health route reports `phase = T8`.
- Static tests confirm no real secrets or public URLs were added.
- Playwright verifies login -> portal watermark/hardening summary.
- Next template typecheck passes.
- Full backend tests pass.

## Next Phase

T9 can prepare a Vercel preview staging run behind protection, but only with explicit approval for the exact external action.

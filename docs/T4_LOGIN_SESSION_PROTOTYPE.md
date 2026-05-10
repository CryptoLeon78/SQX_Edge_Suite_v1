# T4 Login Session Prototype

## Objective

T4 implements the first local login/session prototype in the tester portal template while preserving the T1-T3 safety boundaries.

This is not production authentication. It is a disabled-by-default demo flow that proves route structure, cookie handling, protected-route middleware and logout shape before real tester persistence exists.

T4 does not deploy Vercel, create tester accounts, create a private repository, send emails, publish URLs, rotate passwords, connect a production database or store real credentials.

## Active Ownership

- Access/Security Gatekeeper: session cookie, protected routes, disabled-by-default demo gate, no production credential claims.
- Backend/API: route handlers, form parsing, redirect behavior and future persistence boundary.
- Frontend/UI: login form, protected portal placeholder and logout button in the template only.
- Security/Distribution: no real secrets, no real tester data, no public URLs.
- QA/Release: static contracts, full backend suite and `git diff --check`.

## Implemented Template Files

| Path | Purpose |
| --- | --- |
| `src/app/login/page.tsx` | Local demo login form. |
| `src/app/api/auth/login/route.ts` | Route Handler that accepts form data, denies by default and sets a session cookie only if demo mode is explicitly enabled. |
| `src/app/api/auth/logout/route.ts` | Route Handler that clears the session cookie. |
| `src/lib/session-prototype.ts` | Shared prototype helpers for protected prefixes, cookie application, redirects, demo credential checks and audit-shaped results. |
| `src/middleware.ts` | Blocks protected routes without the T3 session cookie and redirects to `/login`. |
| `src/app/portal/page.tsx` | Adds a logout action to the protected placeholder. |

## Demo Mode Contract

The demo login is off by default:

- `T4_DEMO_LOGIN_ENABLED="false"`
- `T4_DEMO_TESTER_EMAIL="tester@example.invalid"`
- `T4_DEMO_ACCESS_CODE="replace-with-local-demo-access-code"`

When disabled, login attempts are redirected back to `/login` with `demo_login_disabled`.

When enabled privately for local smoke testing, the route creates an opaque random session ID and stores it in the cookie defined by T3:

- cookie name: `__Host-sqx_tester_session`
- `HttpOnly = true`
- `Secure = true`
- `SameSite = Strict`
- `Path = /`
- max age: 60 minutes

The demo access code is not production password auth and must not be reused as a buyer/tester password.

## Protected Routes

The middleware blocks these prefixes unless the prototype session cookie is present:

- `/portal`
- `/admin`
- `/api/tester`

Blocked requests redirect to `/login?next=<path>`.

T4 only checks for the prototype cookie presence because there is no database yet. T5/T6 must replace this with server-side entitlement and expiry validation before any tester rollout.

## Security Notes

- No password hashes from real users are stored.
- No raw session IDs are committed.
- No external Vercel URLs are published.
- No real tester email is committed.
- No localStorage/sessionStorage credential storage is introduced.
- All real auth remains gated behind T5-T8 and explicit deployment approval.

## References

- Next.js Route Handlers: https://nextjs.org/docs/app/building-your-application/routing/route-handlers
- Next.js NextResponse cookies: https://nextjs.org/docs/app/api-reference/functions/next-response
- Next.js Middleware: https://nextjs.org/docs/app/building-your-application/routing/middleware
- OWASP Session Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

## Verification

T4 is accepted when:

- Login, logout and session prototype files exist.
- Demo mode is disabled by default.
- Cookie settings match the T3 `__Host-` session contract.
- Middleware blocks protected routes and redirects to `/login`.
- Static tests confirm no real secret, production URL or tester data was introduced.
- Full backend tests pass.

## Next Phase

T5 should add `tester_pro` entitlement gates for paid options and keep them server-side, not just hidden in the UI.

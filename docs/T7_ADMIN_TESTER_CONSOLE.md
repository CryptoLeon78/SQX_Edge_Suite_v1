# T7 Admin Tester Console

## Objective

T7 adds a protected admin tester console to the public-safe tester portal template so an operator can review tester lifecycle state and preview create, renew, deny and block actions before any production persistence exists.

T7 remains local and non-external. It does not deploy Vercel, create tester accounts, send emails, rotate passwords, connect a production database, publish URLs or mutate real tester records.

## Active Ownership

- Access/Security Gatekeeper: admin route protection, operator-only actions, tester lifecycle boundaries and denial reasons.
- Backend/API: protected `/api/admin/testers` route and reusable admin action preview helpers.
- Frontend/UI: protected `/admin/testers` console page and read-only demo tester table.
- Security/Distribution: no real tester identities, no secrets, no public URLs and no automatic account creation.
- Architecture/Docs: roadmap, governance and living-contract updates.
- QA/Release: static tests, Next template typecheck, backend pytest, Playwright visual smoke and `git diff --check`.

## Implemented Template Files

| Path | Purpose |
| --- | --- |
| `src/lib/admin-console.ts` | Defines admin actions, demo tester rows and operator-preview action payloads. |
| `src/app/api/admin/testers/route.ts` | Protected API route for demo admin table and action previews. |
| `src/app/admin/testers/page.tsx` | Protected admin console preview with tester lifecycle rows and action buttons. |
| `src/lib/session-prototype.ts` | Extends protected prefixes to include `/api/admin`. |
| `src/app/portal/page.tsx` | Links protected tester portal to the admin preview page. |

## Admin Action Contract

T7 supports these operator-preview actions:

- `create_tester`
- `renew_15_days`
- `deny_tester`
- `block_tester`

The route returns `mode = operator-preview`, `noMutation = true` and `persistence = not_applied_in_template`.

By default, the API is disabled:

- `T7_DEMO_ADMIN_CONSOLE_ENABLED="false"`

When disabled, `/api/admin/testers` returns `demo_admin_console_disabled` with HTTP `403`, even if the local prototype session exists.

## Demo Tester Rows

The public-safe template uses only `.invalid` demo identities:

- `active.tester@example.invalid`
- `renewal.tester@example.invalid`
- `blocked.tester@example.invalid`

Each row includes status, expiration date, last audit event and a risk note. The table is static demo material and must not be treated as production operator state.

## Denial Reasons

The admin route returns structured denial reasons:

- `missing_session` with HTTP `401`
- `demo_admin_console_disabled` with HTTP `403`
- `unsupported_admin_action` with HTTP `400`

## Security Boundary

- No tester account is created.
- No renewal email is sent.
- No production database is connected.
- No real tester identity is committed.
- No deployment or Vercel URL is published.
- No action mutates local or remote state.
- `/api/admin` is protected by the prototype session gate.
- Production T8+ must add role-based operator identity and immutable audit persistence before any tester rollout.

## Verification

T7 is accepted when:

- `src/lib/admin-console.ts` exists and defines `ADMIN_TESTER_ACTIONS`.
- `/api/admin/testers` requires session and `T7_DEMO_ADMIN_CONSOLE_ENABLED="true"` before returning demo data.
- `/admin/testers` renders create, renew, deny, block and audit review as operator preview.
- Static tests confirm no real secrets or public URLs were added.
- Playwright verifies login -> portal -> admin console.
- Next template typecheck passes.
- Full backend tests pass.

## Next Phase

T8 should harden rate limiting, security headers, watermark, kill switch and deployment-protection checklist before any staging preview.

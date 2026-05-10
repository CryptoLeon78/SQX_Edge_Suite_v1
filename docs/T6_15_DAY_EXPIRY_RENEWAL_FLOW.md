# T6 15-Day Expiry Renewal Flow

## Objective

T6 adds a lifecycle-aware renewal flow to the tester portal template: every tester access cycle is limited to 15 days and any continuation must be approved manually by an operator. In short, this is the manual approve/deny flow for controlled testers.

T6 remains local and non-external. It does not deploy Vercel, create tester accounts, send renewal emails, rotate passwords, connect a production database, publish URLs or mutate real tester records.

## Active Ownership

- Access/Security Gatekeeper: expiry classification, manual approval/denial/blocking states and denial reasons.
- Backend/API: protected `/api/tester/renewal` route and reusable renewal helpers.
- Frontend/UI: protected renewal preview page inside the template.
- Security/Distribution: no real tester identities, no secrets, no public URLs and no automatic renewal.
- Architecture/Docs: roadmap, governance and living-contract updates.
- QA/Release: static tests, Next template typecheck, backend pytest and `git diff --check`.

## Implemented Template Files

| Path | Purpose |
| --- | --- |
| `src/lib/renewal-flow.ts` | Defines renewal states, 15-day extension helper, lifecycle classifier and manual decision preview. |
| `src/app/api/tester/renewal/route.ts` | Protected route for renewal status and manual-preview decisions. |
| `src/app/renewal/page.tsx` | Protected UI for approve, deny and block preview actions. |
| `src/app/portal/page.tsx` | Links the protected portal to renewal review and lists manual actions. |

## Renewal State Contract

T6 recognizes these states:

- `active`
- `pending_renewal`
- `expired`
- `denied`
- `blocked`

The default demo state is intentionally conservative:

- `T6_DEMO_RENEWAL_STATE="pending_renewal"`

An active tester remains valid only when:

- `plan = tester_pro`
- `status = active`
- `expiresAt > now`
- renewal cycle is `15` days

Expired, denied, blocked or pending testers must not receive feature access until an operator resolves the state in the future private database.

## Manual Decision Contract

The protected renewal route supports these operator decisions as previews:

- `approve_15_days`
- `deny`
- `block`

`approve_15_days` previews:

- next status: `active`
- next expiration: `now + 15 days`
- audit event: `renewal_approved`

`deny` previews:

- next status: `denied`
- audit event: `renewal_denied`

`block` previews:

- next status: `blocked`
- audit event: `tester_blocked`

The API response includes `mode = manual-preview`, `noMutation = true` and `persistence = not_applied_in_template`. The production version must persist decisions in a private tester database and write audit events.

## Denial Reasons

The renewal route returns structured denial reasons:

- `missing_session` with HTTP `401`
- `unsupported_decision` with HTTP `400`
- `renewal_pending_operator_approval` with HTTP `403`
- `tester_expired` with HTTP `403`
- `renewal_denied` with HTTP `403`
- `tester_blocked` with HTTP `403`

## Security Boundary

- No automatic renewal.
- No renewal email is sent.
- No tester account is created.
- No production database is connected.
- No real tester identity is committed.
- No deployment or Vercel URL is published.
- No localStorage/sessionStorage credential storage is introduced.
- UI preview does not grant paid functionality.

## Verification

T6 is accepted when:

- `src/lib/renewal-flow.ts` exists and defines `TESTER_RENEWAL_CYCLE_DAYS`, `pending_renewal`, `expired`, `denied`, `blocked`, `approve_15_days` and `manual-preview`.
- `/api/tester/renewal` requires a session and never mutates production data.
- `.env.example` keeps `T6_DEMO_RENEWAL_STATE="pending_renewal"`.
- Static tests confirm no real secrets or public URLs were added.
- Next template typecheck passes.
- Full backend tests pass.

## Next Phase

T7 should add an admin tester console for create, renew, deny, block and audit review, still behind private infrastructure and explicit deployment approval.

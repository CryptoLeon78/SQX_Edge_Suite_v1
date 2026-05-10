# T3 Tester Auth Data Contract

## Objective

T3 defines the future tester authentication data contract before login or database code exists. It keeps the T-track disciplined: model the records, policies and audit boundaries first; implement credentials and sessions later.

T3 is contract-only. It does not deploy Vercel, create a private repository, create tester accounts, write real passwords, send renewal emails, publish URLs or connect a production database.

## Active Ownership

- Access/Security Gatekeeper: tester identity, sessions, renewal tokens, audit events, password policy and abuse boundaries.
- Backend/API: future persistence shape, table names, record fields, helpers and server-side entitlement checks.
- Security/Distribution: no secrets in git, no plaintext passwords, no raw IP/user-agent storage requirement in public code.
- Architecture/Docs: roadmap and living contract alignment.
- QA/Release: static tests, full backend tests and no frontend E2E because no user-visible runtime changed.

## Required Records

| Record | Purpose | Public-Safe Contract |
| --- | --- | --- |
| `testers` | One row per invited tester identity. | `testerId`, normalized email, display name, status, plan, password hash metadata, expiry, failed login state and private notes pointer. |
| `tester_sessions` | Server-side session inventory. | Store only session ID hash, tester ID, expiry, revocation, last seen and hashed client fingerprints. |
| `tester_renewal_tokens` | Invite/password-set/renewal token inventory. | Store only token hash, one-use state, expiry, revocation and tester binding. |
| `tester_audit_events` | Security and lifecycle evidence. | Store structured event, actor, outcome, route, hashed IP/user-agent and private evidence pointer. |

The tracked template contains this as pure TypeScript contract in `templates/SQX_Edge_Tester_Portal/src/lib/auth-data-contract.ts`.

## Tester Status Contract

Allowed statuses stay aligned with T1/T2:

- `invited`
- `active`
- `pending_renewal`
- `expired`
- `denied`
- `blocked`

Access to paid/tester functionality requires all of:

- `status = active`
- `plan = tester_pro`
- `expires_at > now`
- unrevoked server-side session
- server-side entitlement check on every protected route

## Password Hash Policy

Password storage must follow OWASP Password Storage guidance:

- Never store plaintext passwords.
- Never use fast hashes such as SHA-256 for password storage.
- Preferred algorithm: `argon2id`.
- Minimum parameters for this contract: memory `19456 KiB`, iterations `2`, parallelism `1`.
- Store algorithm and parameters with the hash to support future upgrades.
- Optional pepper may be used only from an environment variable such as `PASSWORD_PEPPER`; the pepper must not be stored in the database or git.
- Password creation/reset responses must not reveal whether an email exists.

## Session Cookie Contract

Sessions must follow OWASP Session Management guidance:

- Cookie name: `__Host-sqx_tester_session`.
- Cookie stores an opaque session ID only; the database stores only a hash of that ID.
- `HttpOnly = true`
- `Secure = true`
- `SameSite = Strict`
- `Path = /`
- no `Domain` attribute
- do not store session IDs, JWTs, refresh tokens or credentials in `localStorage` or `sessionStorage`
- default session lifetime: 60 minutes before renewal/re-auth design is revisited

## Renewal Token Contract

Renewal, invite and password-set links follow OWASP Forgot Password guidance:

- Token values are random, high entropy and single-use.
- Store only token hashes.
- Default max age: 24 hours.
- Bind token to tester ID and purpose.
- Denied or blocked testers cannot use old tokens.
- Deny/block must revoke active sessions.
- User-facing responses must be consistent to reduce account enumeration.

## Audit Event Contract

Audit events must be structured and security-focused:

- `tester_invited`
- `password_set_requested`
- `password_set_completed`
- `login_succeeded`
- `login_failed`
- `session_created`
- `session_revoked`
- `tester_expired`
- `renewal_requested`
- `renewal_approved`
- `renewal_denied`
- `tester_blocked`
- `tester_unblocked`
- `watermark_rendered`
- `cron_expiry_dry_run`
- `cron_expiry_completed`

Audit events may store hashed IP and hashed user agent for abuse review, but public-safe code must not require raw IP, raw user agent, raw email in event payloads or private commercial notes. Sensitive evidence belongs in private storage referenced by `privateEvidenceRef`.

## Secret Boundary

Required future environment variables:

- `AUTH_SECRET`
- `TESTER_DB_URL`
- `CRON_SECRET`
- `EDGE_CONFIG`
- `WATERMARK_SALT`
- `PASSWORD_PEPPER` if peppering is enabled

Forbidden in git:

- plaintext passwords
- password hashes copied from real users
- raw invite or renewal tokens
- session IDs
- private database URLs
- Vercel project URLs or protected preview URLs
- raw tester lists
- raw IP or user-agent logs

## Template Changes In T3

T3 adds `src/lib/auth-data-contract.ts` to the portal template with:

- `PASSWORD_HASH_POLICY`
- `SESSION_COOKIE_CONTRACT`
- `RENEWAL_TOKEN_CONTRACT`
- `AUDIT_EVENT_TYPES`
- typed records for testers, sessions, renewal tokens and audit events
- pure helpers for status validation and active tester checks

These helpers are not authentication implementation. They are compile-time and review-time contracts for T4+.

## References

- OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- OWASP Session Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- OWASP Forgot Password Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

## Verification

T3 is accepted when:

- The contract document and template file exist.
- Password, session, renewal token and audit policies are explicit.
- Static tests confirm no real secrets or external URLs were added.
- Governance, roadmap, README and changelog point from T3 to T4.
- Full backend tests pass.

## Next Phase

T4 can implement a login/session prototype using this contract, still without inviting testers or deploying Vercel unless explicitly approved.


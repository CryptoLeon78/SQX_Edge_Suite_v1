# T1 Cloud Tester Architecture Contract

## Objective

T1 defines the architecture contract for a controlled Vercel-hosted tester portal that can give up to 10 invited testers access to the Pro experience through email plus password, with 15-day renewal cycles, manual approval/denial and strict anti-leakage controls.

T1 is design and governance only. It does not deploy Vercel, create a repository, add application runtime code, send emails, create tester accounts or expose paid features online.

## Recommended Repository Structure

| Repository | Visibility | Role | Allowed Contents |
| --- | --- | --- | --- |
| `SQX_Institutional_Core` | Private/controlled | Canonical product core and institutional source of truth. | App source, institutional workflows, analyzer assets, governance and verified branches. |
| `SQX_Edge_Suite_v1` | Public/controlled | Public-safe distribution, portable ZIP, docs, contracts and release traceability. | Redacted docs, buyer-safe README, release artifacts, public-safe tests. |
| `sqx-edge-commercial-private` | Private | Sensitive commercial/customer operating material. | Tester list, buyer logs, renewal decisions, email templates, private sales/support evidence. |
| `SQX_Edge_Tester_Portal` | Private, future T2 | Vercel-hosted tester portal. | Next.js app, auth/session UI, tester entitlement gates, audit UI and cloud E2E tests. |
| `SQX_Edge_Access_Service` | Optional future | Dedicated auth/licensing/audit service if the portal outgrows the monolith. | Only introduced after T2-T8 proves separation is needed. |

The current product remains portable-first. The Vercel layer is a controlled tester access surface, not a replacement for the local app until a later approved SaaS phase.

## Vercel Platform Assumptions

Use only official Vercel-supported controls:

- Deployment Protection and Password Protection can protect preview/production URLs, but they are not sufficient as per-tester identity management.
- Vercel Authentication can protect deployments for Vercel users, but the tester product still needs first-party tester accounts because testers are external buyers/users.
- Environment Variables hold secrets; no secrets go to git or `vercel.json` as literal values.
- Cron Jobs may run a daily expiry/renewal scanner, secured with an authorization secret.
- Middleware can enforce session checks and add security headers.
- Edge Config can hold non-secret global switches such as maintenance mode, tester pilot enabled/disabled and feature flags.

References:

- Vercel Deployment Protection: https://vercel.com/docs/deployment-protection/methods-to-protect-deployments/password-protection
- Vercel Authentication: https://vercel.com/docs/deployment-protection/methods-to-protect-deployments/vercel-authentication
- Vercel Environment Variables: https://vercel.com/docs/project-configuration/vercel-json
- Vercel Cron Jobs: https://vercel.com/docs/cron-jobs/manage-cron-jobs
- Vercel Edge Config: https://vercel.com/docs/edge-config/get-started

## Tester Access Model

Tester identity fields:

- `email`
- `display_name`
- `status`: `invited`, `active`, `pending_renewal`, `expired`, `denied`, `blocked`
- `plan`: `tester_pro`
- `expires_at`
- `renewal_cycle_days`: `15`
- `last_login_at`
- `failed_login_count`
- `notes_private_ref`: pointer to private commercial repo evidence, never raw private notes in public repo.

Session rules:

- Login requires email plus password.
- Passwords are hashed with a modern password hash; never plaintext.
- Sessions use secure HttpOnly cookies.
- Access requires `status = active`, `plan = tester_pro` and `expires_at > now`.
- Every tester-facing page checks the entitlement server-side or in middleware.
- All paid/tester features are feature-flagged through entitlement, not through hidden buttons only.

Renewal rules:

- Default cycle is 15 days.
- A daily scanner marks expired accounts as `pending_renewal` or `expired`.
- Renewal links are single-use, short-lived and tokenized.
- Renewal approval is manual: continue, deny or block.
- Denied/blocked testers cannot regain access through old links.

## User Flow

1. Operator creates tester in private admin tooling.
2. Tester receives an invite link.
3. Tester sets or receives initial password through a one-use token flow.
4. Tester logs in and sees the Pro tester portal.
5. Every page is watermarked with tester email and tester ID.
6. At day 15, access expires or moves to renewal review.
7. Operator approves renewal for another 15 days or denies access.
8. All login, renewal, export and blocked-access events are audit logged.

## Security And Anti-Leakage Controls

Required before any tester rollout:

- Rate limit login and renewal endpoints.
- Lock or delay after repeated failed attempts.
- Log IP, user agent, route, action, tester ID and timestamp.
- Add visible watermark with tester email/session ID on the portal.
- Add export/report watermark where feasible.
- Disable indexing through headers and metadata.
- Add security headers: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, HSTS for production, and restrictive CSP where compatible.
- Do not expose raw source files, internal docs, private sales data, license keys, signing keys, relay secrets or local-only tools.
- Use Vercel Deployment Protection as an additional layer, not as the only auth mechanism.
- Keep a global kill switch in Edge Config or equivalent non-secret config.
- Maintain a manual incident response: block tester, revoke sessions, rotate password, rotate deployment protection, review audit log.

## Threat Model

| Threat | Risk | Required Control |
| --- | --- | --- |
| Shared tester password | Unauthorized access spreads beyond 10 testers. | Per-user accounts, rotation, audit log, watermark, renewal approval. |
| Link forwarding | Non-tester opens the portal. | Session-bound login, one-use invite/renew tokens, deployment protection as extra layer. |
| Brute force login | Account takeover. | Rate limit, failed-attempt delay/lock, audit alerts. |
| Expired tester keeps access | Commercial leakage. | Server-side expiry check on every request, daily scanner, session invalidation. |
| Screenshots redistributed | Product leakage. | Visible watermark, legal/support wording, limited tester cohort. |
| Private secrets leaked to Vercel | Signing/license compromise. | No private keys in portal, Vercel env vars only for portal secrets, secret review gate. |
| Feature flags bypassed in UI | Free/blocked user sees paid functions. | Entitlement checked server-side/middleware, not only hidden UI. |
| Vercel preview URL leaked | Uncontrolled access. | Deployment Protection, first-party auth, no unprotected previews for tester branches. |
| Cron endpoint abused | Unauthorized expiry/renewal changes. | `CRON_SECRET` authorization check. |

## New Specialist Agent

Access/Security Gatekeeper:

- Owns tester auth, sessions, renewals, rate limits, audit events, watermarks, Vercel secrets, deployment protection and anti-distribution controls.
- Has veto over any cloud tester deployment, auth change, renewal automation, public URL or tester data migration.
- Required checks: unauthenticated access blocked, expired tester blocked, denied tester blocked, active `tester_pro` allowed, failed-login controls, audit event written, no secret in git, security headers present.

## Expanded Existing Agent Duties

- Frontend/UI: tester login, renewal states, final-user portal UX, watermark presentation, blocked/expired screens.
- Backend/API: tester records, password hashing, sessions, entitlement checks, renewal tokens, audit event persistence.
- QA/Release: cloud E2E matrix, preview deployment smoke, protected URL checks, tester lifecycle regression.
- Monetization/Product: tester terms, Pro feature exposure, renewal/denial wording, cohort rules and safe claims.
- Security/Distribution: secret review, anti-leakage gate, Vercel protection settings, incident response.
- Architecture/Docs: repo boundaries, cloud/local split, T-track roadmap, ADRs and contract tests.

## T-Track Roadmap

T1 - Cloud Tester Architecture Contract. Done when this document, governance and tests define the architecture without runtime changes.

T2 - Private Tester Portal Repo Bootstrap. Create private `SQX_Edge_Tester_Portal`, initial Next.js/Vercel structure, `.gitignore`, README and no real tester data.

T3 - Tester Auth Data Contract. Define schema, statuses, session model, token model, audit event contract and secret boundaries.

T4 - Login And Session Prototype. Implement email/password login, password hash, secure cookie and blocked unauthenticated routes.

T5 - Tester Pro Entitlements. Gate all paid options behind `tester_pro` entitlements and feature flags.

T6 - 15-Day Expiry And Renewal. Add expiry checks, renewal states and manual approval/denial flow.

T7 - Admin Tester Console. Create, pause, renew, deny, block and inspect audit events for testers.

T8 - Security Hardening Gate. Add rate limiting, headers, watermark, kill switch, deployment protection checklist and abuse response.

T9 - Vercel Preview Staging. Deploy preview with protected URL, env vars, smoke tests and no public indexing.

T10 - Controlled Internal Tester Pilot. One internal tester end-to-end before inviting external testers.

T11 - 10 Tester Rollout. Invite up to 10 testers with monitored access and manual renewal.

T12 - Monitoring And Abuse Review. Review audit logs, failed logins, access patterns, screenshots/export controls and continue/stop decision.

## Non-Goals For T1

- No Vercel deployment.
- No `SQX_Edge_Tester_Portal` repo creation.
- No database migration.
- No auth implementation.
- No email sending.
- No tester account creation.
- No production or preview URL publication.

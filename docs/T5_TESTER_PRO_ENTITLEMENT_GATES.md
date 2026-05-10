# T5 Tester Pro Entitlement Gates

## Objective

T5 adds explicit `tester_pro` feature gates to the tester portal template so paid/pro functionality is protected by server-side entitlement checks, not by hidden UI alone.

T5 remains local and non-external. It does not deploy Vercel, invite testers, create real users, connect a production database, send emails, rotate passwords or publish URLs.

## Active Ownership

- Access/Security Gatekeeper: entitlement decisions, paid-feature gate behavior and denial reasons.
- Backend/API: protected `/api/tester/features` route and reusable gate helpers.
- Frontend/UI: read-only feature list in the protected portal surface.
- Security/Distribution: no real tester identities, no buyer data, no secrets, no public URLs.
- QA/Release: static contracts, typecheck, full backend suite and `git diff --check`.

## Implemented Template Files

| Path | Purpose |
| --- | --- |
| `src/lib/entitlement-gates.ts` | Defines Pro feature IDs, demo entitlement flag and reusable gate evaluator. |
| `src/app/api/tester/features/route.ts` | Server-side route that returns 401 without session and 403 unless demo entitlement is explicitly enabled. |
| `src/app/portal/page.tsx` | Shows feature IDs as read-only placeholders and states that UI does not grant access. |

## Feature Gate Contract

T5 defines these paid/tester feature IDs:

- `sqx_dashboard_full`
- `strategy_builder`
- `project_generator`
- `views_creator`
- `buyer_handoff_exports`
- `support_case_bundle`

Access to these features requires:

- valid prototype session cookie
- demo entitlement flag enabled locally: `T5_DEMO_TESTER_PRO_ENABLED="true"`
- active entitlement with `plan = tester_pro`
- `status = active`
- `expiresAt > now`

By default `.env.example` keeps `T5_DEMO_TESTER_PRO_ENABLED="false"`, so even a local session cannot access Pro features until the operator deliberately enables the demo gate.

## Denial Reasons

The route returns structured denial reasons:

- `missing_session` with HTTP `401`
- `demo_entitlement_disabled` with HTTP `403`
- `tester_pro_inactive` with HTTP `403`

Future T6/T7 work can replace the demo evaluator with database-backed tester lifecycle checks without changing the feature-gate contract.

## Security Boundary

- UI visibility is informational only.
- `/api/tester/features` is the server-side gate.
- No real tester email is used.
- No license, checkout, buyer or support data is exposed.
- No production entitlement source is connected.
- No deploy or tester invite is performed.

## Verification

T5 is accepted when:

- `src/lib/entitlement-gates.ts` exists and defines `TESTER_PRO_FEATURES`.
- `/api/tester/features` requires session and entitlement.
- `.env.example` disables demo entitlements by default.
- Static tests confirm no real secrets or public URLs were added.
- Next template typecheck passes.
- Full backend tests pass.

## Next Phase

T6 should add 15-day expiry and manual renewal state flow, replacing demo-only entitlement freshness with lifecycle-aware decisions.


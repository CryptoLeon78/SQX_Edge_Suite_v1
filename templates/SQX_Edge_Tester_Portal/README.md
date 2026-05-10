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
- `T8_GLOBAL_KILL_SWITCH_ENABLED`: local kill-switch flag; keep `false` unless validating emergency shutoff privately.
- `T8_RATE_LIMIT_ENABLED`: local rate-limit flag; keep `false` unless validating request throttling privately.
- `T8_RATE_LIMIT_MAX_REQUESTS`: local rate-limit maximum request count.
- `T8_RATE_LIMIT_WINDOW_SECONDS`: local rate-limit window.

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
- `src/lib/security-hardening.ts`: T8 kill switch, rate-limit and watermark helpers.
- `src/lib/deployment-protection.ts`: T8 checklist for protected staging before any tester rollout.
- `src/lib/security-headers.ts`: baseline browser protection headers.
- `src/middleware.ts`: protected-route session gate and security headers.
- `scripts/vercel-preview-preflight.mjs`: T9 local preflight before retrying protected preview deploy.
- `scripts/vercel-protection-audit.mjs`: T9c go/no-go audit for Vercel Deployment Protection before deploy retry.
- `scripts/vercel-preview-path-proof.mjs`: T9f proof gate for Git/PR preview readiness without deploying.
- `scripts/vercel-target-guard.mjs`: T10b build-time guard that blocks production-target builds from non-production branches.
- `scripts/vercel-explicit-preview-proof.mjs`: T10c no-deploy proof for an explicit API preview request with `target: "preview"`.
- `scripts/vercel-omitted-target-preview-proof.mjs`: T10e no-deploy proof for the Vercel API preview path where `target` is omitted.
- `scripts/vercel-preview-project-separation-proof.mjs`: T10f no-deploy proof that the tester preview project is separated and has no public deployment surface.
- `scripts/vercel-linked-preview-project-proof.mjs`: T10g no-deploy proof that the separated preview project is linked to the private tester portal repo with protection and no public surface.
- `scripts/vercel-protected-preview-rollback-proof.mjs`: T10h no-deploy proof that the protected preview deployment rollback left no public surface.
- `scripts/vercel-cli-default-preview-route-proof.mjs`: T10i no-deploy proof that the next attempt uses the CLI default preview route without `--prod` or `--target`.
- `scripts/vercel-cli-default-preview-command-rollback-proof.mjs`: T10j no-deploy proof that the invalid `--skip-domain` preview command created no public surface.
- `scripts/vercel-cli-default-preview-rollback-proof.mjs`: T10k no-deploy proof that the corrected CLI default preview rollback left no public surface.
- `scripts/vercel-route-investigation-proof.mjs`: T10l no-deploy investigation of Vercel route settings after repeated production-target rollbacks.
- `scripts/vercel-config-hardening-proof.mjs`: T10m dry-run/apply proof for Vercel Project API hardening without deployment.
- `scripts/vercel-route-decision-proof.mjs`: T10n no-deploy decision gate that rejects the current Vercel route until a replacement or provider-level proof exists.
- `scripts/replacement-route-contract-proof.mjs`: T10o no-deploy replacement-route contract that selects a fresh staging route preflight before any deployment.

## Local Preflight

```powershell
npm run preflight:vercel-preview
```

This validates the public-safe template before any Vercel preview retry. The next deploy must first verify Deployment Protection from Vercel settings/API and must not attach production aliases.

```powershell
npm run audit:vercel-protection
```

This blocks deploy retry unless the linked Vercel project protection can be verified through API or an operator records the dashboard check privately. After T9d, the expected result is `GO_PROTECTION_VERIFIED` with Vercel Authentication Standard Protection.

```powershell
npm run proof:vercel-preview-path
```

This proves whether a Git/PR-based preview path is ready without running a deploy. It must return `GO_GIT_PREVIEW_PATH_READY` before any future preview URL is created or shared. A safe `NO_GO_GIT_PREVIEW_NOT_CONFIGURED` result means the private tester portal repository still needs to be connected to Vercel.

The proof accepts Vercel Project API Git connections exposed either as `gitRepository` or as `link`.

```powershell
npm run proof:vercel-explicit-preview
```

This proves the explicit API preview path without creating a deployment. It checks that Vercel still tracks `main` as production, `tester-preview` is non-production and the draft request uses `target: "preview"`. The expected no-deploy status is `GO_EXPLICIT_API_PREVIEW_PATH_READY`.

```powershell
npm run proof:vercel-omitted-target-preview
```

This proves the corrected API preview path without creating a deployment. Vercel documents omitted `target` as preview behavior, so this proof builds a draft request with no `target` field and requires `tester-preview` to remain non-production. The expected no-deploy status is `GO_OMITTED_TARGET_PREVIEW_PATH_READY`.

```powershell
npm run proof:vercel-preview-project-separation
```

This proves the T10f project separation without creating a deployment. It requires the separated preview project to exist, to be different from the legacy project, and to have no live deployment, no latest deployment, no domains and no Git link yet. The expected no-deploy status is `GO_PREVIEW_PROJECT_SEPARATED`.

```powershell
npm run proof:vercel-linked-preview-project
```

This proves the T10g linked preview project without creating a deployment. It requires `sqx-edge-tester-preview` to be linked to the private tester portal repository, `main` to be the production branch, `tester-preview` to remain non-production, Deployment Protection to be enabled, and no live deployment, no latest deployment and no domains. The expected no-deploy status is `GO_LINKED_PREVIEW_PROJECT_READY`.

```powershell
npm run proof:vercel-protected-preview-rollback
```

This proves the T10h rollback cleanup without creating a deployment. It requires the separated preview project to have no live deployment, no latest deployment and no domains after the guarded `target=production` attempt was removed. The expected no-deploy status is `GO_PROTECTED_PREVIEW_ROLLBACK_CLEAN`.

```powershell
npm run proof:vercel-cli-default-preview-route
```

This proves the T10i route correction without creating a deployment. It keeps `sqx-edge-tester-preview` linked, protected and surface-free, and approves only `vercel deploy --force --yes --format json --skip-domain` for the next inspection attempt. The expected no-deploy status is `GO_CLI_DEFAULT_PREVIEW_ROUTE_READY`.

T10j may execute exactly one CLI default preview deployment with immediate target inspection and rollback on mismatch.

T10k may execute exactly one CLI default preview deployment without `--skip-domain` after T10j command rollback.

```powershell
npm run proof:vercel-cli-default-preview-command-rollback
```

This proves the T10j command rollback cleanup without creating a deployment. It records that `--skip-domain` is invalid for preview deployments, keeps the project surface-free and approves only `vercel deploy --force --yes --format json` for the next inspection attempt. The expected no-deploy status is `GO_CLI_DEFAULT_PREVIEW_COMMAND_ROLLBACK_CLEAN`.

```powershell
npm run proof:vercel-cli-default-preview-rollback
```

This proves the T10k rollback cleanup without creating a deployment. It records that the corrected CLI default preview route still returned `target=production`, confirms the guard blocked publication and verifies the separated project has no latest deployment or domains. The expected no-deploy status is `GO_CLI_DEFAULT_PREVIEW_ROLLBACK_CLEAN`.

T10l must investigate or replace the Vercel route without another deployment attempt.

```powershell
npm run proof:vercel-route-investigation
```

This proves the T10l route investigation without creating a deployment. It records the no-deploy Vercel Project/Environment API findings and returns `NO_GO_VERCEL_ROUTE_REQUIRES_MANUAL_TARGET_FIX_OR_REPLACEMENT` until a manual correction or alternative route is proven.

T10m must perform manual dashboard/API correction or define an alternative no-deploy route proof; T10m is now completed as Project API hardening, and T10n still must prove or replace the route before deployment.

T10n must prove or replace the Vercel preview route before any deployment; T10n is now completed as a no-deploy route decision, and T10o must prepare the replacement or provider-level proof.

T10o must prepare a replacement route or manual provider-level proof before any deployment; T10o is now completed as a replacement-route contract, and T10p must create or verify the fresh staging route only with explicit approval.

```powershell
npm run proof:vercel-config-hardening
```

This dry-runs T10m Vercel config hardening without creating a deployment. Apply mode requires `T10M_APPLY=1` and patches only `autoAssignCustomDomains=false` and `previewDeploymentsDisabled=false`. The expected applied status is `GO_CONFIG_HARDENED_NO_DEPLOY_TARGET_STILL_UNPROVEN`.

```powershell
npm run proof:vercel-route-decision
```

This proves the T10n route decision without creating a deployment. It must return `NO_GO_CURRENT_VERCEL_ROUTE_REPLACEMENT_REQUIRED` for the current route until a replacement or manual provider-level proof exists.

```powershell
npm run proof:replacement-route-contract
```

This proves the T10o replacement-route contract without tokens, API calls, project creation or deployment. It must return `GO_REPLACEMENT_ROUTE_CONTRACT_READY_NO_DEPLOY` and leave the current Vercel route rejected for rollout.

## Next Phase

T10p must create or verify a fresh staging route only after explicit approval and before any deployment. T10h requested preview from `sqx-edge-tester-preview`, but Vercel returned `target=production`; the T10b guard blocked publication and the deployment was removed immediately. T10m hardened documented project settings, T10n rejects the current route for rollout because the deployment target remains unproven, and T10o selects `fresh_staging_route_with_no_deploy_preflight`. Do not share any tester URL until a deployment returns `target=preview` and no production alias exists.

T10i must correct or replace the Vercel preview deployment route before another deployment attempt.

T10 proved that a Git deployment from `tester-preview` can still report `target=production`, and an explicit API request with `target: "preview"` can return `target=production`. Do not create another deployment on the current project ID. The next route must prove that `production/tester-preview` fails before publication.

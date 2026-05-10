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
- `scripts/fresh-staging-route-preflight-proof.mjs`: T10p no-deploy/no-external-action gate for the fresh staging route requirements before asking for exact provider approval.
- `scripts/fresh-staging-route-access-check-proof.mjs`: T10q no-deploy access check that records explicit approval and blocks route creation until CLI/token write auth exists.
- `scripts/fresh-staging-project-created-proof.mjs`: T10r no-deploy proof that `sqx-edge-tester-staging` exists with no deployments, no domains, no Git link and no URL publication.
- `scripts/staging-protection-verified-proof.mjs`: T10s no-deploy proof that `sqx-edge-tester-staging` has SSO Deployment Protection and Git fork protection before any link, deployment or tester URL.
- `scripts/staging-local-link-proof.mjs`: T10t no-deploy proof that the private tester portal local CLI link targets `sqx-edge-tester-staging` while `.vercel/` remains ignored and no tester surface exists.
- `scripts/staging-deployment-readiness-proof.mjs`: T10u no-deploy readiness gate before one controlled staging deployment attempt with target and alias inspection.
- `scripts/controlled-staging-deploy-rollback-proof.mjs`: T10v proof that one controlled staging deployment attempt returned production target, was blocked by the guard and was removed.
- `scripts/provider-target-mapping-investigation-proof.mjs`: T10w no-deploy proof that rejects the default CLI route and prepares an explicit `--target=preview` route.
- `scripts/explicit-preview-target-rollback-proof.mjs`: T10x proof that the explicit preview-target route still returned production target, was blocked by the guard and was removed.
- `scripts/no-deploy-provider-dashboard-decision-proof.mjs`: T10y no-deploy decision that pauses Vercel CLI deployment and selects provider-dashboard correction before any new attempt.
- `scripts/provider-dashboard-correction-package-proof.mjs`: T10z no-deploy correction package with operator checklist and evidence format before any new attempt.
- `scripts/provider-dashboard-evidence-record-proof.mjs`: T10aa no-deploy evidence record that confirms CLI evidence cannot prove preview target safety without manual dashboard review.
- `scripts/manual-dashboard-evidence-ingest-proof.mjs`: T10ab no-deploy manual dashboard evidence ingest that rejects the current Vercel tester route and selects route replacement.
- `scripts/replacement-tester-route-options-proof.mjs`: T10ac no-deploy route comparison that selects Cloudflare Pages preview plus Cloudflare Access email OTP as the next candidate.
- `scripts/cloudflare-access-preflight-proof.mjs`: T10ad no-deploy Cloudflare Access preflight before any provider project, deployment or tester URL.
- `scripts/cloudflare-runtime-compatibility-proof.mjs`: T10ae local runtime compatibility proof that rejects static export and selects Cloudflare Workers/OpenNext.
- `scripts/opennext-cloudflare-adapter-proof.mjs`: T10af local OpenNext/Cloudflare adapter package proof that verifies safe scripts, `wrangler.jsonc`, `open-next.config.ts`, `.dev.vars.example` and no deploy surface.
- `scripts/opennext-local-smoke-proof.mjs`: T10ag local smoke proof that records native Windows preview NO-GO and WSL/Linux preview GO.

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

T10p must prepare the fresh staging route preflight before any external action; T10p is now completed as a local no-external-action gate, and T10q must request exact approval before creating or verifying any provider route.

T10q has recorded explicit approval for creating or verifying a fresh protected staging route without deployment, but write actions are blocked until Vercel CLI is authenticated non-interactively or a local `VERCEL_TOKEN` is provided.

T10r must authenticate Vercel CLI or provide a local `VERCEL_TOKEN` before creating or verifying the fresh staging project; T10r is now completed with the authenticated CLI path.

T10r has created and verified `sqx-edge-tester-staging` as a clean project shell without deployment, domains, Git link or tester URL. T10s must verify or enable protection/settings before any Git link or deployment.

T10s has verified `sqx-edge-tester-staging` protection/settings without deployment, Git link, URL publication, tester accounts or tester emails. SSO Deployment Protection is enabled with `all_except_custom_domains`, Git fork protection is enabled, and the project still has zero deployments and zero domains.

```powershell
npm run proof:staging-protection-verified
```

This proves the T10s protection gate without creating a deployment. It must return `GO_STAGING_PROTECTION_VERIFIED_NO_DEPLOY`.

T10t has linked the private tester portal working tree to `sqx-edge-tester-staging` through ignored local Vercel metadata only. The project still has zero deployments, zero domains and no published tester URL.

```powershell
npm run proof:staging-local-link
```

This proves the T10t local link gate without creating a deployment. It must return `GO_STAGING_LOCAL_LINK_CONFIGURED_NO_DEPLOY`.

T10u has prepared a no-deploy readiness gate for the next single staging deployment attempt. The project still has zero deployments, zero domains and no published tester URL.

```powershell
npm run proof:staging-deployment-readiness
```

This proves the T10u readiness gate without creating a deployment. It must return `GO_STAGING_DEPLOYMENT_READINESS_GATE_NO_DEPLOY`.

T10v executed one controlled staging deployment attempt. Vercel returned `target=production`, the T10b guard blocked publication with exit code `43`, and the failed deployment was removed immediately.

```powershell
npm run proof:controlled-staging-deploy-rollback
```

This proves the T10v rollback cleanup. It must return `NO_GO_STAGING_DEPLOYMENT_TARGET_PRODUCTION_ROLLBACK_CLEAN`.

T10w investigated provider-level target mapping without another deployment attempt. The default CLI route remains rejected, and the next safe Vercel route is an explicit preview target command.

```powershell
npm run proof:provider-target-mapping-investigation
```

This proves the T10w no-deploy investigation. It must return `NO_GO_DEFAULT_CLI_STAGING_ROUTE_REJECTED_EXPLICIT_PREVIEW_TARGET_PREPARED`.

T10x executed one explicit preview-target deployment attempt. Vercel still returned `target=production`, the T10b guard blocked publication with exit code `43`, and the failed deployment was removed immediately.

```powershell
npm run proof:explicit-preview-target-rollback
```

This proves the T10x rollback cleanup. It must return `NO_GO_EXPLICIT_PREVIEW_TARGET_RETURNED_PRODUCTION_ROLLBACK_CLEAN`.

```powershell
npm run proof:no-deploy-provider-dashboard-decision
```

This proves the T10y no-deploy decision. It must return `GO_PROVIDER_DASHBOARD_CORRECTION_DECISION_READY_NO_DEPLOY` and keep Vercel CLI deployment paused until T10z produces provider/dashboard correction evidence.

T10y must stop retrying Vercel CLI deployment before any provider/dashboard correction package exists.

T10z must prepare the no-deploy provider/dashboard correction package before any provider-dashboard evidence record can allow a later deployment proposal.

T10aa must record no-deploy provider/dashboard correction evidence before any deployment attempt.

```powershell
npm run proof:provider-dashboard-correction-package
```

This proves the T10z correction package. It must return `GO_PROVIDER_DASHBOARD_CORRECTION_PACKAGE_READY_NO_DEPLOY` and keep the next phase limited to no-deploy provider/dashboard correction evidence.

```powershell
npm run proof:provider-dashboard-evidence-record
```

This proves the T10aa read-only evidence record. It must return `NO_GO_PROVIDER_CANNOT_PROVE_PREVIEW_TARGET` until manual dashboard evidence is available or Vercel is replaced as the tester route.

T10ab must ingest manual dashboard evidence and select the next no-deploy replacement gate before any deployment attempt.

```powershell
npm run proof:manual-dashboard-evidence-ingest
```

This proves the T10ab manual dashboard evidence ingest. It must return `NO_GO_REPLACE_VERCEL_TESTER_ROUTE` until T10ac selects a protected non-Vercel tester route, a local/private-network pilot, or a newly proven Vercel route with provider evidence before deployment.

T10ac must compare and select a replacement tester route without deployment. T10ac must compare replacement tester routes without creating provider projects or deployments.

```powershell
npm run proof:replacement-tester-route-options
```

This proves the T10ac route decision. It must return `GO_CLOUDFLARE_ACCESS_OTP_ROUTE_SELECTED_NO_DEPLOY` and keep the next phase limited to a no-deploy Cloudflare Access preflight package.

T10ad must prepare a Cloudflare Access preflight package without creating a provider project or deployment. T10ad must prepare the Cloudflare Access preflight without creating projects, policies, deployments or URLs.

```powershell
npm run proof:cloudflare-access-preflight
```

This proves the T10ad preflight. It must return `GO_CLOUDFLARE_ACCESS_PREFLIGHT_READY_NO_DEPLOY` and keep the next phase limited to local Cloudflare runtime compatibility checks before any provider action.

T10ae must decide and test Cloudflare runtime compatibility locally before any provider action. T10ae must decide Cloudflare runtime compatibility locally before installing adapter dependencies or creating any provider surface.

```powershell
npm run proof:cloudflare-runtime-compatibility
```

This proves the T10ae runtime decision. It must return `GO_CLOUDFLARE_WORKERS_OPENNEXT_RUNTIME_SELECTED_NO_PROVIDER_ACTION`, reject static export while middleware/API route handlers exist, and keep T10af limited to local adapter packaging.

```powershell
npm run proof:opennext-cloudflare-adapter
```

This proves the T10af local adapter package. It must return `GO_OPENNEXT_CLOUDFLARE_ADAPTER_LOCAL_PACKAGE_READY_NO_DEPLOY`, keep Cloudflare deploy scripts absent and leave T10ag limited to local OpenNext build/preview smoke without provider action.

```powershell
npm run proof:opennext-local-smoke
```

This proves the T10ag local smoke decision. It must return `GO_OPENNEXT_LOCAL_LINUX_PREVIEW_SMOKE_NO_PROVIDER_ACTION`, keep native Windows preview marked as `NO_GO_NATIVE_WINDOWS_PREVIEW_ROUTE_500`, and leave T10ah limited to the Next.js `middleware` to `proxy` cleanup.

```powershell
npm run cf:build
npm run cf:preview
npm run cf:typegen
```

These commands are local-only package commands. Do not add or run a Cloudflare deploy command until a later phase is explicitly approved.

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

```powershell
npm run proof:fresh-staging-route-preflight
```

This proves the T10p fresh staging route preflight without tokens, API calls, project creation, Git linking or deployment. It must return `GO_FRESH_STAGING_ROUTE_PREFLIGHT_READY_NO_EXTERNAL_ACTION`.

```powershell
npm run proof:fresh-staging-route-access-check
```

This proves the T10q fresh staging route access check without deployment. It must return `NO_GO_FRESH_STAGING_ROUTE_CREATION_BLOCKED_BY_CLI_AUTH` until a write-capable Vercel path exists.

```powershell
npm run proof:fresh-staging-project-created
```

This proves the T10r fresh staging project creation without deployment. It must return `GO_FRESH_STAGING_PROJECT_CREATED_NO_DEPLOY` and keep the rejected route out of rollout.

## Next Phase

T10ah must migrate the Next.js `middleware` convention to `proxy` without provider action. T10h requested preview from `sqx-edge-tester-preview`, but Vercel returned `target=production`; the T10b guard blocked publication and the deployment was removed immediately. T10m hardened documented project settings, T10n rejects the current route for rollout because the deployment target remains unproven, T10o selects `fresh_staging_route_with_no_deploy_preflight`, T10p proves the local preflight gate, T10q confirms write auth, T10r creates the clean project shell, T10s verifies protection/settings, T10t configures the local private portal link, T10u prepares the no-deploy readiness gate, T10v confirms the default CLI route still returns production target, T10w prepares the explicit preview-target route, T10x confirms that route also returns production target, T10y pauses Vercel CLI deployment, T10z prepares the correction checklist, T10aa records the manual dashboard evidence gap, T10ab ingests manual dashboard evidence with `NO_GO_REPLACE_VERCEL_TESTER_ROUTE`, T10ac selects Cloudflare Pages preview plus Cloudflare Access email OTP as the next candidate, T10ad defines the Cloudflare Access preflight without provider action, T10ae selects Cloudflare Workers/OpenNext as runtime, T10af prepares the local adapter package and T10ag confirms WSL/Linux local preview health 200 while native Windows preview remains NO-GO. Do not share any tester URL until a deployment returns the expected non-production status and no production alias exists.

T10i must correct or replace the Vercel preview deployment route before another deployment attempt.

T10 proved that a Git deployment from `tester-preview` can still report `target=production`, and an explicit API request with `target: "preview"` can return `target=production`. Do not create another deployment on the current project ID. The next route must prove that `production/tester-preview` fails before publication.

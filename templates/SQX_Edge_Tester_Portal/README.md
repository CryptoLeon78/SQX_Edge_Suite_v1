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
- `cloudflare/worker-entry.js`: TL1d/TL2/TL3 Cloudflare rescue entry. It serves the protected tester login, portal, handoff checklist, copyable feedback packet flow and renewal information before falling back to OpenNext for non-rescue routes.
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
- `scripts/next-proxy-migration-proof.mjs`: T10ah proof that blocks migration to `proxy.ts` while OpenNext Cloudflare does not support Node Middleware.
- `scripts/cloudflare-provider-project-preflight-proof.mjs`: T10ai no-deploy Cloudflare provider-project preflight proof before any project, Access policy, Git link or tester URL.
- `scripts/cloudflare-project-shell-proof.mjs`: T10aj no-deploy Cloudflare project-shell gate proof that records the exact approval and blocks advancement until auth or manual shell verification exists.
- `scripts/cloudflare-auth-handoff-proof.mjs`: T10ajb no-deploy Cloudflare auth/manual evidence handoff proof before T10ajc shell evidence ingestion.
- `scripts/cloudflare-shell-evidence-ingest-proof.mjs`: T10ajc no-deploy evidence ingest gate that keeps T10ak blocked until the ignored local shell evidence proves a real shell and zero tester surface.
- `scripts/cloudflare-shell-evidence-capture-proof.mjs`: T10ajd no-deploy capture checklist proof for manual/authenticated shell evidence before rerunning T10ajc.
- `scripts/cloudflare-readonly-shell-capture-proof.mjs`: T10aje read-only capture proof recording that the proposed Worker does not exist after Wrangler authentication.
- `scripts/cloudflare-shell-creation-decision-proof.mjs`: T10ajf decision proof recording that no invisible shell path is accepted and the first Worker creation requires an exact approval gate for `wrangler deploy`.
- `scripts/cloudflare-first-deploy-approval-gate-proof.mjs`: T10ajg approval-gate proof recording the exact first deploy command, manual approval phrase, pre-checks, post-checks and cleanup criteria without running them.
- `scripts/cloudflare-first-deploy-readiness-proof.mjs`: T10ajh readiness proof recording the authenticated read-only prechecks, reproducible lockfile, successful local Cloudflare build and exact-approval block before any deploy.
- `scripts/cloudflare-first-deploy-rollback-proof.mjs`: T10aji rollback proof recording the first deploy attempt, workers.dev/route requirement and immediate Worker cleanup.
- `scripts/cloudflare-route-onboarding-decision-proof.mjs`: T10ajj no-deploy route decision proof that disables `workers_dev` and `preview_urls` until T10ajk chooses a protected Cloudflare route/onboarding path.
- `scripts/cloudflare-route-access-precreate-proof.mjs`: T10ajk route/access precreate proof that keeps Access blocked until a private hostname/zone or protected workers.dev onboarding evidence exists.
- `cloudflare-route-access-precreate.example.json`: public-safe evidence template for T10ajl; copy to ignored `cloudflare-route-access-precreate.local.json` only.
- `scripts/cloudflare-hostname-zone-selection-proof.mjs`: T10ajl hostname/zone evidence proof that unlocks T10ak only from ignored private evidence.
- `scripts/cloudflare-hostname-zone-selection-prepare.mjs`: T10ajl2 operator helper that creates/reviews the ignored hostname/zone evidence file and blocks sensitive local fields.
- `cloudflare-hostname-zone-selection.example.json`: public-safe T10ajl evidence template; copy to ignored `cloudflare-hostname-zone-selection.local.json` only.
- `scripts/cloudflare-workers-dev-shell-gate-proof.mjs`: T10ajm workers.dev shell gate proof for the no-domain/no-existing-Worker path.
- `scripts/cloudflare-workers-dev-shell-deploy-proof.mjs`: T10ajn proof for the shell-created / Access-pending state after the controlled workers.dev shell deploy.
- `scripts/cloudflare-workers-dev-access-proof.mjs`: T10ajo proof for the Access-protected shell state before any real app deploy.
- `scripts/cloudflare-access-policy-boundary-proof.mjs`: T10ak proof for the Access app/policy boundary before any real app deploy.
- `scripts/cloudflare-controlled-real-app-deploy-gate-proof.mjs`: T10al proof for the exact future real-app deploy gate; it does not deploy the app.
- `scripts/cloudflare-real-app-deploy-result-proof.mjs`: T10am proof for the approved real-app version upload with no public target and no tester URL.
- `scripts/cloudflare-protected-tester-publication-target-proof.mjs`: T10an proof selecting protected `workers.dev` plus Cloudflare Access as the tester publication target without publishing it.
- `scripts/cloudflare-controlled-workers-dev-publication-preflight-proof.mjs`: T10ao proof for the controlled `workers.dev` publication preflight without enabling `workers_dev`.
- `scripts/cloudflare-workers-dev-publication-result-proof.mjs`: T10ap proof for the approved `workers.dev` publication result using ignored redacted local evidence.
- `scripts/tester-access-handoff-proof.mjs`: T10aq proof for operator-only tester handoff without public URL or tester email leakage.
- `tester-access-handoff.example.json`: public-safe T10aq evidence template; copy to ignored `tester-access-handoff.local.json` only.
- `scripts/tester-account-activation-gate-proof.mjs`: T10ar proof for private tester account activation gate without Git URL, email or credential leakage.
- `tester-account-activation.example.json`: public-safe T10ar evidence template; copy to ignored `tester-account-activation.local.json` only.
- `scripts/tester-activation-evidence-ingest-proof.mjs`: T10as proof that ingests ignored private activation evidence and fails closed on sensitive local fields.
- `tester-activation-evidence-ingest.example.json`: public-safe T10as evidence shape; keep real activation evidence in ignored `tester-account-activation.local.json` only.
- `scripts/tester-url-share-approval-gate-proof.mjs`: T10at proof for private one-to-one tester URL sharing approval without committing the URL.
- `tester-url-share-approval.example.json`: public-safe T10at approval shape; copy to ignored `tester-url-share-approval.local.json` only.
- `scripts/tester-first-smoke-gate-proof.mjs`: T10au proof for private one-tester smoke evidence without committing URL, email, credentials or screenshots.
- `tester-first-smoke.example.json`: public-safe T10au smoke shape; copy to ignored `tester-first-smoke.local.json` only.
- `scripts/tester-cohort-expansion-gate-proof.mjs`: T10av proof for private micro-cohort expansion readiness without committing URL, identities, credentials, screenshots or feedback identities.
- `tester-cohort-expansion.example.json`: public-safe T10av expansion shape; copy to ignored `tester-cohort-expansion.local.json` only.
- `scripts/tester-feedback-intake-gate-proof.mjs`: T10aw proof for private feedback intake readiness without committing raw feedback, tester identities, URLs, credentials or screenshots.
- `tester-feedback-intake.example.json`: public-safe T10aw feedback intake shape; copy to ignored `tester-feedback-intake.local.json` only.
- `scripts/tester-feedback-triage-gate-proof.mjs`: T10ax proof for private feedback triage readiness without committing raw feedback, private bug details, tester identities, URLs, credentials or screenshots.
- `tester-feedback-triage.example.json`: public-safe T10ax triage shape; copy to ignored `tester-feedback-triage.local.json` only.
- `scripts/tester-action-plan-gate-proof.mjs`: T10ay proof for private tester action-plan readiness without committing raw feedback, private action details, tester identities, URLs, credentials or screenshots.
- `tester-action-plan.example.json`: public-safe T10ay action-plan shape; copy to ignored `tester-action-plan.local.json` only.
- `scripts/tester-action-execution-gate-proof.mjs`: T10az proof for private tester action execution readiness without committing raw feedback, private action details, private execution notes, tester identities, URLs, credentials or screenshots.
- `tester-action-execution.example.json`: public-safe T10az execution shape; copy to ignored `tester-action-execution.local.json` only.
- `scripts/tester-result-validation-gate-proof.mjs`: T10ba proof for private tester result-validation readiness without committing raw feedback, private action details, private execution notes, private result notes, tester identities, URLs, credentials or screenshots.
- `tester-result-validation.example.json`: public-safe T10ba result-validation shape; copy to ignored `tester-result-validation.local.json` only.
- `scripts/tester-iteration-decision-gate-proof.mjs`: T10bb proof for private tester iteration-decision readiness without committing raw feedback, private action details, private execution notes, private result notes, private decision notes, tester identities, URLs, credentials or screenshots.
- `tester-iteration-decision.example.json`: public-safe T10bb iteration-decision shape; copy to ignored `tester-iteration-decision.local.json` only.
- `scripts/tester-next-iteration-gate-proof.mjs`: T10bc proof for private tester next-iteration readiness without committing raw feedback, private action details, private execution notes, private result notes, private decision notes, private iteration plans, private support notes, tester identities, URLs, credentials or screenshots.
- `tester-next-iteration.example.json`: public-safe T10bc next-iteration shape; copy to ignored `tester-next-iteration.local.json` only.
- `scripts/tester-launch-candidate-proof.mjs`: TL1 macro proof for private tester launch readiness without committing tester URLs, emails, credentials, screenshots, raw feedback or private notes.
- `tester-launch-candidate.example.json`: public-safe TL1 launch-candidate shape; copy to ignored `tester-launch-candidate.local.json` only.
- `scripts/feedback-packet-capture.mjs`: TL4 local-only helper that captures a copied `SQX-FB-...` packet into ignored `.local/feedback-packets/` JSON for operator triage.
- `scripts/feedback-intake-rollup.mjs`: TL5 local-only helper that converts ignored feedback packet JSON into aggregate `tester-feedback-intake.local.json` evidence.
- `scripts/feedback-triage-rollup.mjs`: TL6 local-only helper that converts aggregate intake evidence into ignored triage priority/action evidence.
- `scripts/feedback-action-plan-rollup.mjs`: TL7 local-only helper that converts triage evidence into ignored action-plan evidence.
- `scripts/feedback-action-execution-rollup.mjs`: TL8 local-only helper that converts action-plan evidence into ignored execution evidence.
- `scripts/feedback-result-validation-rollup.mjs`: TL9 local-only helper that converts execution evidence into ignored result-validation evidence.
- `scripts/real-tool-delivery-prepare.mjs`: TL10 local-only helper that attaches the latest portable ZIP to the ignored Cloudflare asset bundle for protected tester download.
- `scripts/real-tool-delivery-proof.mjs`: TL10 no-deploy proof for the protected `/tool` page and `/download/sqx-edge-tool.zip` route.
- `cloudflare-access-policy-boundary.example.json`: public-safe T10ak evidence template; copy to ignored `cloudflare-access-policy-boundary.local.json` only.
- `cloudflare/shell-worker.js`: harmless locked shell Worker used only to create a target before Access is enabled.
- `wrangler.shell.example.jsonc`: dedicated shell Worker config with `workers_dev=true`; the real app config remains `workers_dev=false`.
- `cloudflare-shell-evidence.example.json`: public-safe template for manual shell evidence; copy to ignored `cloudflare-shell-evidence.local.json` only.

## Local Preflight

```powershell
npm run preflight:vercel-preview
```

This validates the public-safe template before any Vercel preview retry. The next deploy must first verify Deployment Protection from Vercel settings/API and must not attach production aliases.

## TL4 Operator Feedback Packet Capture

When a tester submits feedback and receives an `SQX-FB-...` packet, keep the raw packet out of Git. Paste it into an ignored local text file and capture it into local JSON:

```powershell
New-Item -ItemType Directory -Force .local | Out-Null
Set-Content .local\packet.txt "Reference: SQX-FB-1234ABCD`nCategory: workflow`nSeverity: friction`nSummary: Example private tester signal"
npm run operator:capture-feedback-packet -- --file .local\packet.txt
```

The output is written to ignored `.local/feedback-packets/`. If `publicSafe` is `false`, review the packet privately before producing any public-safe summary.

After capturing one or more packets, generate aggregate intake evidence:

```powershell
npm run operator:rollup-feedback-intake
npm run proof:tester-feedback-intake-gate
```

This writes ignored `tester-feedback-intake.local.json` plus `.local/feedback-intake-rollup.json`. Only aggregate counts and redacted categories are produced.

Then generate private triage evidence:

```powershell
npm run operator:rollup-feedback-triage
npm run proof:tester-feedback-triage-gate
```

This writes ignored `tester-feedback-triage.local.json` plus `.local/feedback-triage-rollup.json`. The public-safe action labels are derived only from categories and severities.

Then generate private action-plan evidence:

```powershell
npm run operator:rollup-feedback-action-plan
npm run proof:tester-action-plan-gate
```

This writes ignored `tester-action-plan.local.json` plus `.local/feedback-action-plan-rollup.json`. Public-safe action labels are derived from triage labels only.

Then generate private execution evidence:

```powershell
npm run operator:rollup-feedback-action-execution
npm run proof:tester-action-execution-gate
```

This writes ignored `tester-action-execution.local.json` plus `.local/feedback-action-execution-rollup.json`. The execution labels are public-safe and derived from action labels only.

Then generate private result-validation evidence:

```powershell
npm run operator:rollup-feedback-result-validation
npm run proof:tester-result-validation-gate
```

This writes ignored `tester-result-validation.local.json` plus `.local/feedback-result-validation-rollup.json`. Result labels stay public-safe and derived only from execution labels.

## TL10 Real Tool Delivery Path

The protected portal can expose the real portable tool through `/tool` and `/download/sqx-edge-tool.zip`. The ZIP itself is never committed. Prepare it locally after building a fresh portable package:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ..\..\backend\sqx-edge-tool\tools\package_portable.ps1 -RequireEmbeddedPython
npm run cf:build
npm run operator:prepare-real-tool-delivery
npm run proof:real-tool-delivery
```

This copies the latest `dist\SQX_Edge_Tool_Portable_*.zip` into ignored `.open-next/assets/downloads/SQX_Edge_Tool_Portable_Tester.zip` and writes ignored `.local/real-tool-delivery.local.json` with size/hash evidence. The proof also guards the Cloudflare Workers Assets 25 MiB individual file limit and requires `assets.run_worker_first=true` so the internal ZIP asset cannot bypass the protected Worker download handler. A Cloudflare deploy is still exact-approval-only.

For the live protected tester route, Cloudflare Access is the first identity gate. When Access forwards the authenticated tester email through `Cf-Access-Authenticated-User-Email`, the portal bridges that identity into an SQX session without asking for a second access code. The local demo access code remains only for local/non-Access tests.

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

This proves the T10ag local smoke decision. It must return `GO_OPENNEXT_LOCAL_LINUX_PREVIEW_SMOKE_NO_PROVIDER_ACTION`, keep native Windows preview marked as `NO_GO_NATIVE_WINDOWS_PREVIEW_ROUTE_500`, and leave T10ah limited to the Next.js `middleware` to `proxy` compatibility gate.

```powershell
npm run proof:cloudflare-provider-project-preflight
```

This proves the T10ai Cloudflare provider-project preflight. It must return `GO_CLOUDFLARE_PROVIDER_PROJECT_PREFLIGHT_READY_NO_DEPLOY`, keep deploy scripts absent and keep Cloudflare project creation, Access policy, Git link, tester URL and tester data as exact-approval-only actions.

```powershell
npm run proof:cloudflare-project-shell
```

This proves the T10aj Cloudflare project-shell gate without deploying or creating tester access. The expected safe status is `NO_GO_CLOUDFLARE_PROJECT_SHELL_NOT_VERIFIED_NO_AUTH_NO_DEPLOY_PATH` until Wrangler authentication or manual provider-shell evidence exists.

```powershell
npm run proof:cloudflare-auth-handoff
```

This proves the T10ajb handoff boundary. It must return `NO_GO_CLOUDFLARE_AUTH_HANDOFF_PENDING_MANUAL_LOGIN_OR_EVIDENCE`, keep `cloudflare-shell-evidence.local.json` ignored and leave T10ajc as the only evidence-ingestion gate before Access policy work.

```powershell
npm run proof:cloudflare-shell-evidence-ingest
```

This proves the T10ajc evidence ingest boundary. Without ignored local evidence, the expected status is `NO_GO_CLOUDFLARE_SHELL_EVIDENCE_MISSING_T10AK_BLOCKED`; T10ak remains blocked until the local evidence proves the Cloudflare shell exists and no deployment, Access policy, URL or tester data exists.

```powershell
npm run proof:cloudflare-shell-evidence-capture
```

This proves the T10ajd manual capture checklist. It must return `NO_GO_CLOUDFLARE_CAPTURE_PENDING_MANUAL_AUTH_OR_DASHBOARD_EVIDENCE` until Ivan completes the manual Cloudflare login/dashboard evidence capture outside git and reruns T10ajc.

```powershell
npm run proof:cloudflare-readonly-shell-capture
```

This proves the T10aje read-only capture result. It must return `NO_GO_CLOUDFLARE_WORKER_NOT_FOUND_T10AK_BLOCKED` until a real Cloudflare shell exists; it does not deploy or create Access.

```powershell
npm run proof:cloudflare-shell-creation-decision
```

This proves the T10ajf shell creation decision. It must return `NO_GO_NO_INVISIBLE_CLOUDFLARE_SHELL_PATH_ACCEPTED`, record that the first Worker cannot be created with `wrangler versions upload`, and leave T10ajg limited to preparing the exact `wrangler deploy` approval gate. It does not deploy, upload, create Access or publish a tester URL.

```powershell
npm run proof:cloudflare-first-deploy-approval-gate
```

This proves the T10ajg first deploy approval gate. It must return `GO_CLOUDFLARE_FIRST_DEPLOY_APPROVAL_GATE_READY_NO_PROVIDER_ACTION`, keep package deploy scripts absent and leave T10ajh as the only phase allowed to run the exact `npm exec --yes -- wrangler deploy --name sqx-edge-tester-portal-preview` command after explicit approval.

```powershell
npm ci
npm run proof:cloudflare-first-deploy-readiness
```

This proves the T10ajh first deploy readiness gate without creating a Worker. It must return `GO_CLOUDFLARE_FIRST_DEPLOY_READY_EXACT_APPROVAL_REQUIRED_NO_PROVIDER_MUTATION`, keep package deploy/upload/delete scripts absent, confirm the lockfile-driven Cloudflare toolchain and leave T10aji as the only phase allowed to run the exact deploy command after Ivan provides the exact approval phrase.

```powershell
npm run proof:cloudflare-first-deploy-rollback
```

This proves the T10aji first deploy rollback. It must return `NO_GO_FIRST_WORKER_DEPLOY_ROLLED_BACK_WORKERS_DEV_SUBDOMAIN_REQUIRED`, confirm the Worker was deleted after the route/subdomain failure and leave T10ajj responsible for choosing the Cloudflare route/onboarding path before any new deploy attempt.

```powershell
npm run proof:cloudflare-route-onboarding-decision
```

This proves the T10ajj route/onboarding decision without creating or deploying a Worker. It must return `GO_CLOUDFLARE_ROUTE_ONBOARDING_DECISION_READY_NO_DEPLOY`, confirm `workers_dev=false` and `preview_urls=false`, and leave T10ajk responsible for choosing a protected custom route/domain or completing dashboard `workers.dev` onboarding with Access prepared before any redeploy.

```powershell
npm run proof:cloudflare-route-access-precreate
```

This proves the T10ajk route/access precreate gate. The expected guarded result is `NO_GO_CLOUDFLARE_ROUTE_HOSTNAME_REQUIRED_T10AK_BLOCKED` until T10ajl records private hostname/zone evidence or protected dashboard `workers.dev` onboarding evidence. It must not create a Worker, route, Access application, policy, tester account or URL.

```powershell
npm run prepare:cloudflare-hostname-zone-selection -- --write
```

This creates or reviews the ignored `cloudflare-hostname-zone-selection.local.json` file. It must not contain a real hostname, zone ID, account ID, tester URL, tester emails, tokens or keys; set only booleans after private Cloudflare dashboard checks.

```powershell
npm run proof:cloudflare-hostname-zone-selection
```

This proves the T10ajl private hostname/zone evidence gate. Without ignored private evidence, the expected result is `NO_GO_PRIVATE_HOSTNAME_ZONE_EVIDENCE_REQUIRED_T10AK_BLOCKED`; with private evidence proving a Cloudflare-managed hostname/zone or protected `workers.dev` onboarding, it can return `GO_CLOUDFLARE_HOSTNAME_ZONE_READY_T10AK_ALLOWED`.

```powershell
npm run proof:cloudflare-workers-dev-shell-gate
```

This proves the T10ajm workers.dev shell gate for accounts with a workers.dev subdomain but no existing Worker to protect. It must return `GO_WORKERS_DEV_SHELL_GATE_READY_EXACT_DEPLOY_APPROVAL_REQUIRED` and keeps the next external action limited to the shell deploy, not the real app.

```powershell
npm run proof:cloudflare-workers-dev-shell-deploy
```

This proves the T10ajn shell-created state. Before Access is enabled, it returns `NO_GO_ACCESS_MANUAL_ENABLE_REQUIRED_SHELL_TARGET_EXISTS`; after ignored local evidence confirms Access protection, it returns `GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_READY_FOR_T10AK`.

```powershell
npm run proof:cloudflare-workers-dev-access
```

This proves the T10ajo Access-protected shell state. It must return `GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_VERIFIED_NO_APP` before T10ak records or verifies the Access app/policy boundary. It still does not deploy the real app or publish a tester URL.

```powershell
npm run proof:cloudflare-access-policy-boundary
```

This proves the T10ak Access app/policy boundary from ignored local evidence. It must return `GO_ACCESS_APPLICATION_POLICY_BOUNDARY_VERIFIED_NO_APP_DEPLOY` before a later controlled deploy gate can be prepared. It still does not deploy the real app or publish a tester URL.

```powershell
npm run proof:cloudflare-controlled-real-app-deploy-gate
```

This proves the T10al exact-approval gate for a future real app deploy. It must return `GO_CONTROLLED_REAL_APP_DEPLOY_GATE_READY_EXACT_APPROVAL_REQUIRED` and still does not deploy the real app or publish a tester URL.

```powershell
npm run proof:cloudflare-real-app-deploy-result
```

This proves the T10am approved deploy result from ignored local booleans. It must return `GO_REAL_APP_VERSION_UPLOADED_NO_PUBLIC_TARGET_NO_TESTER_URL` before T10an can choose a protected publication target. It must not include hostnames, URLs, account IDs, Access IDs, deployment IDs, version IDs, tester emails, tokens or keys.

```powershell
npm run proof:cloudflare-protected-tester-publication-target
```

This proves the T10an publication-target gate. It must return `GO_PROTECTED_TESTER_PUBLICATION_TARGET_SELECTED_EXACT_APPROVAL_REQUIRED`, keep `workers_dev=false`, and leave publication blocked until T10ao receives exact approval.

```powershell
npm run proof:cloudflare-controlled-workers-dev-publication-preflight
```

This proves the T10ao controlled `workers.dev` publication preflight. It must return `GO_CONTROLLED_WORKERS_DEV_PUBLICATION_PREFLIGHT_READY_EXACT_APPROVAL_REQUIRED`, keep `workers_dev=false`, and leave publication blocked until T10ap receives exact approval.

```powershell
npm run proof:cloudflare-workers-dev-publication-result
```

This proves the T10ap controlled `workers.dev` publication result from ignored local evidence. It must return `GO_CONTROLLED_WORKERS_DEV_PUBLICATION_ACCESS_PROTECTED_NO_URL_SHARED` and must not include hostnames, URLs, account IDs, Access IDs, deployment IDs, version IDs, tester emails, tokens or keys.

```powershell
npm run proof:tester-access-handoff
```

This proves the T10aq operator handoff gate. It must return `GO_TESTER_ACCESS_HANDOFF_READY_NO_PUBLIC_URL_LEAK` and still does not create testers, email testers or publish the protected URL.

```powershell
npm run proof:tester-account-activation-gate
```

This proves the T10ar private tester account activation gate. It must return `GO_PRIVATE_TESTER_ACCOUNT_ACTIVATION_GATE_READY_NO_GIT_LEAK` and still does not create accounts, send invites, publish the protected URL or commit tester emails/credentials.

```powershell
npm run proof:tester-activation-evidence-ingest
```

This proves the T10as private activation evidence ingest. Without ignored local evidence it returns `NO_GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_MISSING`; with safe private evidence it returns `GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_SAFE_NO_GIT_LEAK` without publishing the protected URL.

```powershell
npm run proof:tester-url-share-approval-gate
```

This proves the T10at private URL sharing approval gate. Without ignored local approval evidence it returns `NO_GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_MISSING`; with safe private approval it returns `GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_READY_NO_GIT_LEAK` without publishing or committing the protected URL.

```powershell
npm run proof:tester-first-smoke-gate
```

This proves the T10au private first-tester smoke gate. Without ignored local smoke evidence it returns `NO_GO_PRIVATE_FIRST_TESTER_SMOKE_EVIDENCE_MISSING`; with safe private smoke evidence it returns `GO_PRIVATE_FIRST_TESTER_SMOKE_PASSED_NO_GIT_LEAK` without committing the protected URL, tester identity or screenshots.

```powershell
npm run proof:tester-cohort-expansion-gate
```

This proves the T10av private tester cohort expansion gate. Without ignored local expansion evidence it returns `NO_GO_PRIVATE_TESTER_COHORT_EXPANSION_EVIDENCE_MISSING`; with safe private readiness evidence it returns `GO_PRIVATE_TESTER_COHORT_EXPANSION_READY_NO_GIT_LEAK` without committing tester URLs, identities, credentials, screenshots or feedback identities.

```powershell
npm run proof:tester-feedback-intake-gate
```

This proves the T10aw private tester feedback intake gate. Without ignored local feedback evidence it returns `NO_GO_PRIVATE_TESTER_FEEDBACK_INTAKE_EVIDENCE_MISSING`; with safe private intake evidence it returns `GO_PRIVATE_TESTER_FEEDBACK_INTAKE_READY_NO_GIT_LEAK` without committing raw feedback, tester identities, URLs, credentials or screenshots.

```powershell
npm run proof:tester-feedback-triage-gate
```

This proves the T10ax private tester feedback triage gate. Without ignored local triage evidence it returns `NO_GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_EVIDENCE_MISSING`; with safe private triage evidence it returns `GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_READY_NO_GIT_LEAK` without committing raw feedback, private bug details, tester identities, URLs, credentials or screenshots.

```powershell
npm run proof:tester-action-plan-gate
```

This proves the T10ay private tester action-plan gate. Without ignored local action-plan evidence it returns `NO_GO_PRIVATE_TESTER_ACTION_PLAN_EVIDENCE_MISSING`; with safe private action-plan evidence it returns `GO_PRIVATE_TESTER_ACTION_PLAN_READY_NO_GIT_LEAK` without committing raw feedback, private action details, tester identities, URLs, credentials or screenshots.

```powershell
npm run proof:tester-action-execution-gate
```

This proves the T10az private tester action execution gate. Without ignored local execution evidence it returns `NO_GO_PRIVATE_TESTER_ACTION_EXECUTION_EVIDENCE_MISSING`; with safe private execution evidence it returns `GO_PRIVATE_TESTER_ACTION_EXECUTION_READY_NO_GIT_LEAK` without committing raw feedback, private action details, private execution notes, tester identities, URLs, credentials or screenshots.

```powershell
npm run proof:tester-result-validation-gate
```

This proves the T10ba private tester result-validation gate. Without ignored local result evidence it returns `NO_GO_PRIVATE_TESTER_RESULT_VALIDATION_EVIDENCE_MISSING`; with safe private result evidence it returns `GO_PRIVATE_TESTER_RESULT_VALIDATION_READY_NO_GIT_LEAK` without committing raw feedback, private action details, private execution notes, private result notes, tester identities, URLs, credentials or screenshots.

```powershell
npm run proof:tester-iteration-decision-gate
```

This proves the T10bb private tester iteration-decision gate. Without ignored local decision evidence it returns `NO_GO_PRIVATE_TESTER_ITERATION_DECISION_EVIDENCE_MISSING`; with safe private decision evidence it returns `GO_PRIVATE_TESTER_ITERATION_DECISION_READY_NO_GIT_LEAK` without committing raw feedback, private action details, private execution notes, private result notes, private decision notes, tester identities, URLs, credentials or screenshots.

```powershell
npm run proof:tester-next-iteration-gate
```

This proves the T10bc private tester next-iteration gate. Without ignored local next-iteration evidence it returns `NO_GO_PRIVATE_TESTER_NEXT_ITERATION_EVIDENCE_MISSING`; with safe private next-iteration evidence it returns `GO_PRIVATE_TESTER_NEXT_ITERATION_READY_NO_GIT_LEAK` without committing raw feedback, private action details, private execution notes, private result notes, private decision notes, private iteration plans, private support notes, tester identities, URLs, credentials or screenshots.

```powershell
npm run proof:tester-launch-candidate
```

This proves the TL1 tester launch candidate as one macro go/no-go. Without ignored private launch evidence it returns `NO_GO_TESTER_LAUNCH_PRIVATE_EVIDENCE_MISSING`; with safe private evidence it returns `GO_TESTER_LAUNCH_CANDIDATE_READY_NO_GIT_LEAK` without committing tester URLs, emails, credentials, screenshots, raw feedback or private notes.

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

T10ah blocks the Next.js `middleware` to `proxy` migration for the current Cloudflare route because `proxy.ts` uses Node Middleware and OpenNext Cloudflare does not support it yet. T10h requested preview from `sqx-edge-tester-preview`, but Vercel returned `target=production`; the T10b guard blocked publication and the deployment was removed immediately. T10m hardened documented project settings, T10n rejects the current route for rollout because the deployment target remains unproven, T10o selects `fresh_staging_route_with_no_deploy_preflight`, T10p proves the local preflight gate, T10q confirms write auth, T10r creates the clean project shell, T10s verifies protection/settings, T10t configures the local private portal link, T10u prepares the no-deploy readiness gate, T10v confirms the default CLI route still returns production target, T10w prepares the explicit preview-target route, T10x confirms that route also returns production target, T10y pauses Vercel CLI deployment, T10z prepares the correction checklist, T10aa records the manual dashboard evidence gap, T10ab ingests manual dashboard evidence with `NO_GO_REPLACE_VERCEL_TESTER_ROUTE`, T10ac selects Cloudflare Pages preview plus Cloudflare Access email OTP as the next candidate, T10ad defines the Cloudflare Access preflight without provider action, T10ae selects Cloudflare Workers/OpenNext as runtime, T10af prepares the local adapter package, T10ag confirms WSL/Linux local preview health 200 while native Windows preview remains NO-GO, T10aji rolls back the first Worker deploy attempt, T10ajj disables accidental workers.dev/preview publication, T10ajk keeps Access precreate blocked until a private hostname/zone exists, and T10ajl prepares the ignored evidence gate. Do not share any tester URL until a deployment returns the expected protected route and Access/app auth are verified.

T10i must correct or replace the Vercel preview deployment route before another deployment attempt.

T10 proved that a Git deployment from `tester-preview` can still report `target=production`, and an explicit API request with `target: "preview"` can return `target=production`. Do not create another deployment on the current project ID. The next route must prove that `production/tester-preview` fails before publication.

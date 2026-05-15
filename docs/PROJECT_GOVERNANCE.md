# SQX Edge Project Governance

Documento vivo para coordinar agentes especializados, ownership por area y reglas de fase antes de continuar con M46.

## Current State

- Current phase completed: UX-NAV sidebar navigation polish inside the Mining Control pass.
- Current implementation phase: PG-RESET-CFX - Reset Plan Mining also resets the Project Generator generated `.cfx` session/list so stale outputs from previous plans do not remain operationally visible.
- Current UX surface decision: Strategy Builder tab and visible CVC handoff are retired from the dashboard shell; existing SB modules/docs remain internal historical contracts until a future renamed workflow is approved.
- Current scoring surface decision: Template Maker is the active Capa 1 scoring and C2 generation surface, now including certification, structural diversity and mandatory C2 traceability before C2; Capa 2 comparison/relationships belong to Champion vs Challenger, including portfolio relationships.
- Current product/commercial state: `next_controlled_commercial_movement_from_m98_decision_ready`.
- Current maintenance rule: every new phase backup must be versioned and paired with a retention check using `docs/maintenance/BACKUP_RETENTION_POLICY.md`.
- Local diagnostic material rule: `material de diagnostico/` is an ignored, local-only inbox for bug samples, CSV/SQX/View evidence and files the operator wants Codex to inspect during troubleshooting. Never commit, package or distribute it.
- SQX internal diagnostic rule: `material de diagnostico/internos_sqx/` may be used only to derive sanitized detection signatures and fixtures; never commit proprietary/internal SQX source files from that folder.
- Branding source rule: generated originals under `material de diagnostico/imagenes_prompts/` remain local-only; only cleaned, optimized derivatives under `app/assets/brand/` may become tracked product assets.
- Template Maker C2 traceability rule: every generated C2 template name and internal `StrategyName` must include asset, BlockSetting, base indicator, NumCluster, direction, timeframe and source strategy so the operator can trace origin to final template without relying on memory.
- Exit Policy Gate: every generated SQX/C2 artifact must preserve the detected exit methods, policy version, removed/disabled exits, randomized exits, overrides and unknown-exit decision. Template Maker C2 must not export an active unknown exit without explicit override.
- BlockSettings Source Gate: every mining, generated `.cfx` or Template Maker C2 output must preserve `family`, `canonicalId`, `filename`, `sha256`, `layer`, `timeframeRule` and origin. Legacy labels such as `BS_Tendencia` are aliases only; default generation must resolve to the official v6 `.sqb` in `backend/sqx-edge-tool/resources/blocksettings/`, with older v4/v5/v7 files retained only as explicit legacy compatibility.
- Timeframe Trace Gate: when an asset card exposes multiple timeframes, the user must confirm one timeframe before the idea enters Plan Mining or Project Generator. The resulting mining/prefill must preserve selected timeframe, available timeframes, source card and resolved BlockSetting trace.
- Generated CFX Session Gate: Reset Plan Mining defines a new generation session for Project Generator. The `.cfx generados` list must hide outputs older than that reset and clear the in-memory UI/log context, while preserving physical files on disk unless a separate cleanup action explicitly deletes them.
- Modal Traceability Gate: every active modal must declare owner, source data, destination data, impact, failure modes and user-visible trace before it can mutate local state. Critical reset/delete/import/restore actions must use the unified decision surface or an equivalent traceable modal, not a blind native prompt.
- Active UX-NAV tab: `Mining Control`; temporarily paused for MODAL-TRACE modal governance and traceability hardening. Resume Mining Control after this phase unless the operator says `Adelante con el siguiente tab`.
- Parallel commercial option remains parked: M100 - execute exactly the M99-approved controlled commercial movement, only after explicit operator decision.
- Governance baseline: G7 - Backup Retention And Artifact Steward Gate.
- Previous governance baseline: G6 - Institutional Dashboard Quick Actions Gate.
- Earlier governance baseline: G5 - Institutional Core Synchronized Gate.
- Earlier governance baseline: G4 - Institutional Core Repository Gate.
- Earlier governance baseline: G3 - Internal Automation and Agent Gate.
- Earlier governance baseline: G2 - Governance Lookup Before Work.
- Historical governance baseline: G1 - Specialist Agent Operating Model.

## Historical State Anchors

- Current phase completed: TL1 - Tester Launch Candidate. Historical anchor only; superseded by TL12.
- Next implementation phase: operator fills private TL1 evidence and runs `proof:tester-launch-candidate`. Historical anchor only; superseded by TL12.
- Current phase completed: T10l - Vercel Route Investigation. Historical anchor only; superseded by T10m.
- Next implementation phase: T10m - manual/API Vercel correction or alternative no-deploy route proof before any further deployment. Historical anchor only; superseded by T10n.
- Current phase completed: T10m - Vercel Config Hardening. Historical anchor only; superseded by T10n.
- Next implementation phase: T10n - no-deploy preview target proof or Vercel route replacement before any further deployment. Historical anchor only; superseded by T10o.
- Current phase completed: T10n - Vercel Route Decision. Historical anchor only; superseded by T10o.
- Next implementation phase: T10o - replacement route or provider-level no-deploy proof before any deployment. Historical anchor only; superseded by T10p.
- Current phase completed: T10o - Replacement Route Contract. Historical anchor only; superseded by T10p.
- Next implementation phase: T10p - create or verify a fresh staging route only after explicit approval and before any deployment. Historical anchor only; superseded by T10q.
- Current phase completed: T10p - Fresh Staging Route Preflight. Historical anchor only; superseded by T10q.
- Next implementation phase: T10q - request exact approval to create or verify a fresh protected staging route without deployment. Historical anchor only; superseded by T10r.
- Current phase completed: T10q - Fresh Staging Route Access Check. Historical anchor only; superseded by T10r.
- Next implementation phase: T10r - authenticate Vercel CLI or provide local `VERCEL_TOKEN`, then create or verify `sqx-edge-tester-staging` without deployment. Historical anchor only; superseded by T10s.
- Current phase completed: T10r - Fresh Staging Project Created. Historical anchor only; superseded by T10s.
- Next implementation phase: T10s - verify or enable protection/settings for `sqx-edge-tester-staging` before any Git link or deployment. Historical anchor only; superseded by T10t.
- Current phase completed: T10s - Staging Protection Verified. Historical anchor only; superseded by T10t.
- Next implementation phase: T10t - link or configure staging without deployment and without publishing a URL. Historical anchor only; superseded by T10u.
- Current phase completed: T10t - Staging Local Link Configured. Historical anchor only; superseded by T10u.
- Next implementation phase: T10u - prepare a no-deploy staging deployment readiness gate before any deployment. Historical anchor only; superseded by T10v.
- Current phase completed: T10u - Staging Deployment Readiness Gate. Historical anchor only; superseded by T10v.
- Next implementation phase: T10v - execute one controlled staging deployment attempt with immediate target/alias inspection and rollback on mismatch. Historical anchor only; superseded by T10w.
- Current phase completed: T10v - Controlled Staging Deploy Rollback. Historical anchor only; superseded by T10w.
- Next implementation phase: T10w - investigate/correct provider-level target mapping without another deployment attempt or replace the staging route. Historical anchor only; superseded by T10x.
- Current phase completed: T10w - Provider Target Mapping Investigation. Historical anchor only; superseded by T10x.
- Next implementation phase: T10x - execute one explicit preview-target deployment attempt with immediate target/alias inspection and rollback on mismatch. Historical anchor only; superseded by T10y.
- Current phase completed: T10x - Explicit Preview Target Rollback. Historical anchor only; superseded by T10y.
- Next implementation phase: T10y - stop retrying Vercel CLI deployment and choose a no-deploy route replacement or provider/dashboard correction decision. Historical anchor only; superseded by T10z.
- Current phase completed: T10y - No-Deploy Provider Dashboard Decision. Historical anchor only; superseded by T10z.
- Next implementation phase: T10z - prepare the no-deploy provider/dashboard correction package before any deployment attempt. Historical anchor only; superseded by T10aa.
- Current phase completed: T10z - Provider Dashboard Correction Package. Historical anchor only; superseded by T10aa.
- Next implementation phase: T10aa - record no-deploy provider/dashboard correction evidence before any deployment attempt. Historical anchor only; superseded by T10ab.
- Current phase completed: T10aa - Provider Dashboard Evidence Record. Historical anchor only; superseded by T10ab.
- Next implementation phase: T10ab - ingest manual dashboard evidence or replace the Vercel tester route before any deployment attempt. Historical anchor only; superseded by T10ac.
- Current phase completed: T10ab - Manual Dashboard Evidence Ingest. Historical anchor only; superseded by T10ac.
- Next implementation phase: T10ac - compare and select a protected non-Vercel tester route or local/private-network pilot without deployment. Historical anchor only; superseded by T10ad.
- Current phase completed: T10ac - Replacement Tester Route Options. Historical anchor only; superseded by T10ad.
- Next implementation phase: T10ad - prepare a no-deploy Cloudflare Access preflight package before any provider project, deployment or tester URL. Historical anchor only; superseded by T10ae.
- Current phase completed: T10ad - Cloudflare Access Preflight. Historical anchor only; superseded by T10ae.
- Next implementation phase: T10ae - decide and test Cloudflare runtime compatibility locally before any provider project, deployment or tester URL. Historical anchor only; superseded by T10af.
- Current phase completed: T10ae - Cloudflare Runtime Compatibility. Historical anchor only; superseded by T10af.
- Next implementation phase: T10af - prepare the local OpenNext/Cloudflare Workers adapter package without deployment or provider action. Historical anchor only; superseded by T10ag.
- Current phase completed: T10af - OpenNext Cloudflare Adapter Package. Historical anchor only; superseded by T10ag.
- Next implementation phase: T10ag - run the local OpenNext build/preview smoke without provider action. Historical anchor only; superseded by T10ah.
- Current phase completed: T10ag - OpenNext Local Smoke. Historical anchor only; superseded by T10ah.
- Next implementation phase: T10ah - evaluate and block the Next.js middleware-to-proxy migration for the current Cloudflare route. Historical anchor only; superseded by T10ai.
- Current phase completed: T10ah - Next Proxy Migration Gate. Historical anchor only; superseded by T10ai.
- Next implementation phase: T10ai - prepare the Cloudflare provider-project preflight without deployment or tester URL. Historical anchor only; superseded by T10aj.
- Current phase completed: T10ai - Cloudflare Provider Project Preflight. Historical anchor only; superseded by T10aj.
- Next implementation phase: T10aj - create or verify a Cloudflare project shell only with exact approval, otherwise keep the route local. Historical anchor only; superseded by T10ak.
- Current phase completed: T10aj - Cloudflare Project Shell Gate. Historical anchor only; superseded by T10ajb.
- Next implementation phase: T10ajb - resolve Cloudflare authentication or manually verify/create the provider shell without deployment. Historical anchor only; superseded by T10ajc.
- Current phase completed: T10ajb - Cloudflare Auth Handoff. Historical anchor only; superseded by T10ajc.
- Next implementation phase: T10ajc - ingest authenticated or manual Cloudflare shell evidence without deployment before T10ak. Historical anchor only; superseded by T10ajd.
- Current phase completed: T10ajc - Cloudflare Shell Evidence Ingest. Historical anchor only; superseded by T10ajd.
- Next implementation phase: T10ajd - capture real Cloudflare shell evidence manually/authenticated before T10ak. Historical anchor only; superseded by T10aje.
- Current phase completed: T10ajd - Cloudflare Shell Evidence Capture Checklist. Historical anchor only; superseded by T10aje.
- Next implementation phase: T10aje - execute manual Cloudflare login/dashboard evidence capture outside git, then rerun T10ajc ingest. Historical anchor only; superseded by T10ajf.
- Current phase completed: T10aje - Cloudflare Read-Only Shell Capture. Historical anchor only; superseded by T10ajf.
- Next implementation phase: T10ajf - choose exact no-deploy Cloudflare shell creation path or authorize one controlled deploy later. Historical anchor only; superseded by T10ajg.
- Current phase completed: T10ajf - Cloudflare Shell Creation Decision. Historical anchor only; superseded by T10ajg.
- Next implementation phase: T10ajg - prepare exact approval gate for the first Cloudflare Worker deploy/shell creation without tester URL sharing. Historical anchor only; superseded by T10ajh.
- Current phase completed: T10ajg - Cloudflare First Deploy Approval Gate. Historical anchor only; superseded by T10ajh.
- Next implementation phase: T10ajh - verify first Cloudflare Worker deploy readiness without deploy while waiting for exact approval. Historical anchor only; superseded by T10aji.
- Current phase completed: T10ajh - Cloudflare First Deploy Readiness. Historical anchor only; superseded by T10aji.
- Next implementation phase: T10aji - execute the first Cloudflare Worker deploy/shell creation only after approval and rollback if unsafe. Historical anchor only; superseded by T10ajj.
- Current phase completed: T10aji - Cloudflare First Deploy Rollback. Historical anchor only; superseded by T10ajj.
- Next implementation phase: T10ajj - decide/register the Cloudflare route or workers.dev onboarding path before any new deploy attempt. Historical anchor only; superseded by T10ajk.
- Current phase completed: T10ajj - Cloudflare Route Onboarding Decision. Historical anchor only; superseded by T10ajk.
- Next implementation phase: T10ajk - configure a protected Cloudflare custom route/domain or complete dashboard workers.dev onboarding with immediate Access precreate before any new deploy attempt. Historical anchor only; superseded by T10ajl.
- Current phase completed: T10ajk - Cloudflare Route Access Precreate. Historical anchor only; superseded by T10ajl.
- Next implementation phase: T10ajl - select private Cloudflare hostname/zone or complete workers.dev onboarding evidence before T10ak Access creation. Historical anchor only; superseded by T10ak.
- Current phase completed: T10ajl - Cloudflare Hostname Zone Selection. Historical anchor only; superseded by T10ajl2.
- Next implementation phase: T10ajl2 - prepare the local operator unlock kit for private Cloudflare hostname/zone evidence before T10ak. Historical anchor only; superseded by T10ajm.
- Current phase completed: T10ajl2 - Cloudflare Operator Unlock Kit. Historical anchor only; superseded by T10ajm.
- Next implementation phase: T10ajm - prepare the workers.dev shell gate because no custom domain and no Worker target exist yet. Historical anchor only; superseded by T10ajn.
- Current phase completed: T10ajm - Workers.dev Shell Gate. Historical anchor only; superseded by T10ajn.
- Next implementation phase: T10ajn - deploy the harmless workers.dev shell only with exact approval, then enable/verify Cloudflare Access before any tester URL. Historical anchor only; superseded by T10ajo.
- Current phase completed: T10ajn - Controlled Workers.dev Shell Deploy. Historical anchor only; superseded by T10ajo.
- Next implementation phase: T10ajo - enable or verify Cloudflare Access on the existing workers.dev shell via dashboard or Access API token before any real app deploy. Historical anchor only; superseded by T10ak.
- Current phase completed: T10ajo - Workers.dev Access Verified. Historical anchor only; superseded by T10ak.
- Next implementation phase: T10ak - record or verify the Cloudflare Access application/policy boundary for the protected workers.dev shell before any real app deploy. Historical anchor only; superseded by T10al.
- Current phase completed: T10ak - Access Policy Boundary. Historical anchor only; superseded by T10al.
- Next implementation phase: T10al - prepare the exact controlled real app deploy gate after Access app/policy boundary verification. Historical anchor only; superseded by T10am.
- Current phase completed: T10al - Controlled Real App Deploy Gate. Historical anchor only; superseded by T10am.
- Next implementation phase: T10am - execute one controlled real app deploy only with exact approval, immediate Access smoke and rollback on mismatch. Historical anchor only; superseded by T10an.
- Current phase completed: T10am - Controlled Real App Deploy Result. Historical anchor only; superseded by T10an.
- Next implementation phase: T10an - choose and verify the protected tester publication target before any URL or tester account. Historical anchor only; superseded by T10ao.
- Current phase completed: T10an - Protected Tester Publication Target Gate. Historical anchor only; superseded by T10ao.
- Next implementation phase: T10ao - controlled workers.dev publication and Access smoke only with exact approval. Historical anchor only; superseded by T10ap.
- Current phase completed: T10ao - Controlled Workers.dev Publication Preflight. Historical anchor only; superseded by T10ap.
- Next implementation phase: T10ap - controlled workers.dev publication and Access smoke only with exact approval. Historical anchor only; superseded by T10aq.
- Current phase completed: T10ap - Controlled Workers.dev Publication Result. Historical anchor only; superseded by T10aq.
- Next implementation phase: T10aq - tester access handoff without public URL leak. Historical anchor only; superseded by T10ar.
- Current phase completed: T10aq - Tester Access Handoff No URL Leak. Historical anchor only; superseded by T10ar.
- Next implementation phase: T10ar - private tester account activation gate without Git URL/email leak. Historical anchor only; superseded by T10as.
- Current phase completed: T10ar - Private Tester Account Activation Gate. Historical anchor only; superseded by T10as.
- Next implementation phase: T10as - private tester activation evidence ingest without Git URL/email leak. Historical anchor only; superseded by T10at.
- Current phase completed: T10as - Private Tester Activation Evidence Ingest. Historical anchor only; superseded by T10at.
- Next implementation phase: T10at - private tester URL share approval gate without Git URL/email leak. Historical anchor only; superseded by T10au.
- Current phase completed: T10at - Private Tester URL Share Approval Gate. Historical anchor only; superseded by T10au.
- Next implementation phase: T10au - private first tester smoke gate without Git URL/email leak. Historical anchor only; superseded by T10av.
- Current phase completed: T10au - Private First Tester Smoke Gate. Historical anchor only; superseded by T10av.
- Next implementation phase: T10av - private tester cohort expansion gate without Git URL/email leak. Historical anchor only; superseded by T10aw.
- Current phase completed: T10av - Private Tester Cohort Expansion Gate. Historical anchor only; superseded by T10aw.
- Next implementation phase: T10aw - private tester feedback intake gate without Git URL/email leak. Historical anchor only; superseded by T10ax.
- Current phase completed: T10aw - Private Tester Feedback Intake Gate. Historical anchor only; superseded by T10ax.
- Next implementation phase: T10ax - private tester feedback triage gate without Git URL/email leak. Historical anchor only; superseded by T10ay.
- Current phase completed: T10ax - Private Tester Feedback Triage Gate. Historical anchor only; superseded by T10ay.
- Next implementation phase: T10ay - private tester action plan gate without Git URL/email leak. Historical anchor only; superseded by T10az.
- Current phase completed: T10ay - Private Tester Action Plan Gate. Historical anchor only; superseded by T10az.
- Next implementation phase: T10az - private tester action execution gate without Git URL/email leak. Historical anchor only; superseded by T10ba.
- Current phase completed: T10az - Private Tester Action Execution Gate. Historical anchor only; superseded by T10ba.
- Next implementation phase: T10ba - private tester result validation gate without Git URL/email leak. Historical anchor only; superseded by T10bb.
- Current phase completed: T10ba - Private Tester Result Validation Gate. Historical anchor only; superseded by T10bb.
- Next implementation phase: T10bb - private tester iteration decision gate without Git URL/email leak. Historical anchor only; superseded by T10bc.
- Current phase completed: T10bb - Private Tester Iteration Decision Gate. Historical anchor only; superseded by T10bc.
- Next implementation phase: T10bc - private tester next iteration gate without Git URL/email leak. Historical anchor only; superseded by T10bd.
- Current phase completed: T10bc - Private Tester Next Iteration Gate. Historical anchor only; superseded by T10bd.
- Current phase completed: TL1 - Tester Launch Candidate. Macro launch-candidate anchor; freezes further T10 micro-gates until a real blocker requires one.

## Specialist Agents

| Agent | Scope | Primary Ownership | Required Checks |
| --- | --- | --- | --- |
| Frontend/UI | Dashboard, responsive UI, tabs, JS modules, visual state. | `app/SQX_Dashboard_v6.html`, `app/css`, `app/js`, `tests/js`, `tests/ui_e2e`. | JS contracts, Python static tests, E2E screenshots when UI changes. |
| Backend/API | Local Flask API, core business logic, manifests, local persistence. | `backend/sqx-edge-tool/api`, `backend/sqx-edge-tool/core`, `backend/sqx-edge-tool/config`, backend tests. | Backend pytest suite, API tests, manifest/static tests when contracts change. |
| QA/Release | Portable ZIP, release checklist, audit, START/STOP, SHA256 evidence. | `backend/sqx-edge-tool/tools/package_portable.ps1`, `audit_distribution.ps1`, `release_checklist.ps1`, launchers, `dist` evidence. | Full pytest, JS contracts, `git diff --check`, release checklist for ZIP phases. |
| Monetization/Product | Pro offer, pricing, support, renewal, buyer journey, safe claims. | `docs/MONETIZATION_ROADMAP.md`, `docs/MONETIZATION_M*.md`, `docs/sales`, product manifest, README. | Commercial docs tests, safe-claims review, roadmap/status alignment. |
| Security/Distribution | Secrets, license material, relay exposure, packaging exclusions. | `.gitignore`, product manifest security, packaging/audit scripts, relay settings, license manager. | Packaging tests, audit rules, sensitive-file staged review. |
| Architecture/Docs | Load order, module contracts, ADRs, ownership matrix, roadmap hygiene. | `docs/ARCHITECTURE.md`, `docs/PROJECT_GOVERNANCE.md`, `docs/decisions`, roadmap docs, module contracts. | Static docs tests, load-order contracts, roadmap consistency checks. |
| Backup/Artifact Steward | Backup versioning, retention, local disk pressure, reproducible artifact cleanup and cleanup manifests. | `backups/` manifests, `docs/maintenance/`, `.gitignore`, generated `output/`, `.pytest_cache/`, `analysis_output/` and backup pruning decisions. | Retention policy check, safe path verification before deletion, protected-evidence review with QA/Release and Security/Distribution. |
| Access/Security Gatekeeper | Tester auth, sessions, renewals, cloud access, anti-distribution controls and Vercel security. | Future `SQX_Edge_Tester_Portal`, `templates/SQX_Edge_Tester_Portal/`, `docs/T1_CLOUD_TESTER_ARCHITECTURE_CONTRACT.md`, `docs/T2_TESTER_PORTAL_BOOTSTRAP.md`, `docs/T3_TESTER_AUTH_DATA_CONTRACT.md`, `docs/T4_LOGIN_SESSION_PROTOTYPE.md`, `docs/T5_TESTER_PRO_ENTITLEMENT_GATES.md`, `docs/T6_15_DAY_EXPIRY_RENEWAL_FLOW.md`, `docs/T7_ADMIN_TESTER_CONSOLE.md`, `docs/T8_TESTER_PORTAL_SECURITY_HARDENING.md`, `docs/T9_PROTECTED_VERCEL_PREVIEW_PREFLIGHT.md`, `docs/T9B_VERCEL_PREVIEW_DEPLOY_ROLLBACK.md`, `docs/T9C_VERCEL_DEPLOYMENT_PROTECTION_GATE.md`, `docs/T9D_VERCEL_AUTH_PROTECTION_VERIFIED.md`, `docs/T9E_PROTECTED_PREVIEW_DEPLOY_ROLLBACK.md`, `docs/T9F_PREVIEW_PATH_PROOF.md`, `docs/T9G_PRIVATE_GIT_PREVIEW_SOURCE.md`, `docs/T10_INTERNAL_PREVIEW_ROLLBACK.md`, `docs/T10B_VERCEL_TARGET_GUARD.md`, `docs/T10C_EXPLICIT_API_PREVIEW_PATH.md`, `docs/T10D_EXPLICIT_API_PREVIEW_ROLLBACK.md`, `docs/T10E_OMITTED_TARGET_PREVIEW_ROLLBACK.md`, `docs/T10F_SEPARATED_PREVIEW_PROJECT.md`, `docs/T10G_LINKED_PREVIEW_PROJECT_PROOF.md`, `docs/T10H_PROTECTED_PREVIEW_DEPLOY_ROLLBACK.md`, `docs/T10I_CLI_DEFAULT_PREVIEW_ROUTE.md`, `docs/T10J_CLI_DEFAULT_PREVIEW_COMMAND_ROLLBACK.md`, `docs/T10K_CLI_DEFAULT_PREVIEW_ROLLBACK.md`, `docs/T10L_VERCEL_ROUTE_INVESTIGATION.md`, `docs/T10M_VERCEL_CONFIG_HARDENING.md`, `docs/T10N_VERCEL_ROUTE_DECISION.md`, `docs/T10O_REPLACEMENT_ROUTE_CONTRACT.md`, `docs/T10P_FRESH_STAGING_ROUTE_PREFLIGHT.md`, `docs/T10Q_FRESH_STAGING_ROUTE_ACCESS_CHECK.md`, `docs/T10R_FRESH_STAGING_PROJECT_CREATED.md`, `docs/T10S_STAGING_PROTECTION_VERIFIED.md`, `docs/T10T_STAGING_LOCAL_LINK_CONFIGURED.md`, `docs/T10U_STAGING_DEPLOYMENT_READINESS_GATE.md`, `docs/T10V_CONTROLLED_STAGING_DEPLOY_ROLLBACK.md`, `docs/T10W_PROVIDER_TARGET_MAPPING_INVESTIGATION.md`, `docs/T10X_EXPLICIT_PREVIEW_TARGET_ROLLBACK.md`, `docs/T10Y_NO_DEPLOY_PROVIDER_DASHBOARD_DECISION.md`, `docs/T10Z_PROVIDER_DASHBOARD_CORRECTION_PACKAGE.md`, `docs/T10AA_PROVIDER_DASHBOARD_EVIDENCE_RECORD.md`, tester access contracts, Vercel env/protection docs, audit and watermark policies. | Unauthenticated blocked, expired/denied/blocked tester blocked, active `tester_pro` allowed, admin operator preview protected, rate limit and audit contracts, no secrets in git, security headers and deployment protection reviewed. |

## Phase Namespaces

Use clear prefixes so technical, commercial and release phases do not collide:

Use prefixed phase IDs for new work.

- `Mxx`: monetization and commercial product phases.
- `Axx`: architecture, modularization and technical structure phases.
- `Rxx`: release, packaging and distribution phases.
- `Sxx`: security and distribution hardening phases.
- `Qxx`: test, QA and observability hardening phases.
- `Gxx`: governance, ownership and decision-process phases.
- `Vxx`: SQX view/template generation and StrategyQuant operator tools.
- `PGxx`: Project Generator user workflows and reusable generation helpers.
- `Jxx`: Jose-derived selective integrations, especially Champion vs Challenger, adapted to SQX architecture and security rules.
- `SBxx`: Strategy Builder and "only one platform" workflow phases.
- `Txx`: cloud tester access, Vercel portal, tester auth, 15-day renewal, audit and anti-distribution phases.
- `TLxx`: tester launch macro decisions. Prefer this over more T10 micro-gates when the work is operational launch readiness.

Legacy references such as "Phase 46" in the modularization track remain historical. New work should use the prefix in titles and commits when practical.

## Operational Rule

G2 - Governance Lookup Before Work:

- Before every work phase/message, consult `docs/PROJECT_GOVERNANCE.md` or the Specialist Agents ownership matrix.
- Declare active ownership, expected touched areas and required checks before implementation when work is more than a direct answer.
- If specialized agents are available and the user asks for agent consultation, use them for bounded review or execution tasks that match the ownership matrix.
- If no specialized agent is needed, explicitly use Project Governance as the source of ownership and verification discipline.

G3 - Internal Automation and Agent Gate:

- Use specialist agents for bounded review, risk checks or parallel implementation slices only when their output materially reduces uncertainty or protects an ownership boundary.
- Automate internal work only when it reduces repeated manual checks, protects contracts, creates reproducible evidence or prevents drift between docs, tests, manifests and release scripts.
- Keep real-world commercial actions manual unless the user explicitly approves the exact action: traffic, emails, checkout publication, buyer contact, license issue, refunds, support promises and public release publication.
- Every new internal automation must declare its risk level, output location, privacy boundary and required verification before commit.
- If an automation touches buyer-facing content, commercial gates, private evidence, relay, licenses, packaging or distribution, include Security/Distribution and QA/Release ownership in the phase.

G4 - Institutional Core Repository Gate:

- Treat `https://github.com/CryptoLeon78/SQX_Institutional_Core.git` as a first-class operational repository for SQX Edge, with local remote name `institutional`.
- Keep `origin` (`https://github.com/CryptoLeon78/SQX_Edge_Suite_v1.git`) and `institutional` as separate publish targets; commit locally once per verified phase, then push each remote deliberately.
- Before a phase that will push, fetch `origin` and `institutional` and check whether `main` can fast-forward both remotes.
- Never force-push `institutional/main` and never overwrite institutional-only files, workflows, analyzer assets or operating docs through a blind mirror push.
- If `institutional/main` has diverged from local `main`, stop normal dual-push discipline and run an explicit G5 institutional sync phase that preserves institutional-only assets before enabling routine pushes there.
- A successful push to `origin` does not imply a successful push to `institutional`; report both outcomes separately.

G5 - Institutional Core Synchronized Gate:

- `institutional/main` is reconciled through a merge commit, not a force push, so both repository histories remain traceable.
- Institutional-only assets are preserved in the public working tree: `.github/CODEOWNERS`, institutional workflows, `DISCIPLINA_OPERATIVA.md`, `app/css/analyzer.css` and `app/js/modules/analyzer.js`.
- The institutional analyzer is exposed as a normal SQX tab (`Analyzer C2`) through the manifest, dashboard load order, module registry and `main.js` initialization.
- Continue fetching both remotes before every push; once both `origin/main` and `institutional/main` point at the same verified merge commit, routine dual pushes are allowed again.

G6 - Institutional Dashboard Quick Actions Gate:

- `institutional/feat/dashboard-quick-actions` is selectively integrated as native SQX UI without restoring removed Top Picks or Matrix surfaces.
- Asset detail/category rows expose quick actions to promote a candidate into Mining Control or prefill Project Generator custom inputs.
- Mining Control includes a compact operational health panel and graph-style funnel visualization while preserving editable counts and local-only state.
- Required checks: JS syntax/contracts, static dashboard tests, backend pytest, `git diff --check` and E2E screenshots for Mining Control and Project Generator prefill flow.

G7 - Backup Retention And Artifact Steward Gate:

- Every backup must use a phase-scoped, timestamped name and declare whether it is source backup, release evidence, private evidence or cleanup manifest.
- After creating any new backup, run the retention check in `docs/maintenance/BACKUP_RETENTION_POLICY.md`: measure `backups/`, identify superseded or obsolete backups and keep only the required recent/protected set.
- Before deleting backup or generated artifact directories, resolve absolute paths and verify they stay inside the workspace or the explicitly named target directory.
- Do not delete `dist/`, private/commercial material, license material or release evidence unless QA/Release plus Security/Distribution ownership explicitly marks it obsolete or superseded.
- For aggressive cleanup, leave a manifest in `backups/cleanup-<phase>-YYYYMMDD-HHMMSS/` before deletion and summarize freed space in the phase result.

UX-NAV Tab Optimization Gate:

- UX-NAV is now a sequential tab-by-tab optimization track documented in `docs/UX_NAV_TAB_OPTIMIZATION_PLAN.md`.
- Only one active tab can be optimized at a time; the current active tab is `Template Maker` until this polish is accepted.
- Treat every operator message during an active tab pass as feedback for that same tab unless the operator explicitly changes the active scope.
- Do not begin the next tab until the operator says exactly: `Adelante con el siguiente tab`.
- Defer global tab reordering, tab removal/merging beyond active scope and final navigation flow until all individual tab passes are complete.

## Internal Automation Risk Levels

| Level | Allowed By Default | Examples | Extra Gate |
| --- | --- | --- | --- |
| 0 - Read/report | Yes. | Static audits, roadmap consistency checks, local tool discovery, test summaries. | Normal phase verification. |
| 1 - Local evidence | Yes, if excluded or intentionally tracked. | Redacted JSON reports, local monitor evidence, checksums, internal run logs. | Declare output path and package exclusion. |
| 2 - Buyer-facing preparation | Only with explicit phase scope. | Draft release notes, buyer handoff packs, Pro docs, public copy. | Monetization/Product plus Security/Distribution review. |
| 3 - External action | No automatic execution. | Publishing release, sending email, enabling checkout, issuing license, inviting buyers. | Explicit user approval for the exact action. |

## Agent And Command Matrix

| Ownership | Default Checks | Escalate To Agents When |
| --- | --- | --- |
| Frontend/UI | `node .\tests\js\module_contracts.mjs`, static dashboard tests, E2E screenshots when visual behavior changes. | Tab wiring, responsive layout, dashboard contracts or user-visible state changes are non-trivial. |
| Backend/API | `backend\sqx-edge-tool\venv\Scripts\python.exe -m pytest backend\sqx-edge-tool backend\sqx-edge-relay`, API/static tests. | New endpoints, persistence contracts, manifests or local automation tools move. |
| QA/Release | `release_checklist.ps1` for ZIP/release phases, `audit_distribution.ps1`, SHA256 and extracted ZIP smoke. | Packaging, portable runtime, release notes, dist evidence or CI/release publication changes. |
| Monetization/Product | Safe-claims review, roadmap/status alignment, private/public commercial boundary check. | Commercial movement, buyer-facing assets, pricing/support positioning or sales gates move. |
| Security/Distribution | Sensitive-file staged review, manifest exclusions, package/audit deny-lists. | Licenses, keys, buyer logs, relay, checkout evidence, commercial-private docs or generated packages are touched. |
| Architecture/Docs | Architecture/load-order docs, governance docs, contract map consistency. | Module boundaries, roadmap structure, phase taxonomy or governance rules move. |
| Access/Security Gatekeeper | Cloud auth threat model, tester lifecycle tests, secret review, deployment-protection review, audit/watermark contracts. | Any Vercel tester portal, auth/session, renewal, tester data, cloud URL, password rotation or anti-distribution behavior moves. |
| Backup/Artifact Steward | Backup retention policy, cleanup manifest review, safe deletion checks and disk pressure report. | Backups exceed normal working size, generated artifacts accumulate, a phase creates large backups, or the operator asks to lighten the workspace. |

## Local Tooling Notes

- Required and present for normal work: Git, Python virtualenv, pytest, Node/npm, PowerShell and `rg`.
- Optional but useful for upcoming release/CI automation: GitHub CLI `gh`, especially for inspecting Actions, creating releases and managing PR/release metadata.
- Playwright remains on-demand for frontend visual/E2E work; install temporarily only when UI behavior needs browser validation.
- MetaTrader5 tooling is only needed for real-data A58/A62 style phases, not for governance, packaging or commercial monitor phases.
- Tunnels such as ngrok/cloudflared should remain out of the default path until relay staging work explicitly needs them.
- Backup retention is a standing maintenance routine; use `docs/maintenance/BACKUP_RETENTION_POLICY.md` whenever a phase creates backups or cleanup touches ignored artifacts.

## Phase Workflow

Every implementation phase must follow this loop:

1. Consult Project Governance or the Specialist Agents ownership matrix before every work phase/message.
2. Confirm working tree state.
3. Create a versioned backup before changing files and record its scope.
4. Run the backup retention check from `docs/maintenance/BACKUP_RETENTION_POLICY.md`; prune obsolete ignored backups/artifacts only when safe and leave a manifest for aggressive cleanup.
5. Define active agent ownership and expected touched areas.
6. Apply the G3 automation risk level if the phase adds tools, evidence, gates or external actions.
7. Implement narrowly against the phase objective.
8. Update docs, manifests and tests in the same phase when contracts move.
9. Run required checks for touched areas.
10. Run E2E screenshots when frontend behavior or `manifest-data.js` changes.
11. Clean temporary Playwright/npm artifacts and re-run the retention check if new heavy artifacts were generated.
12. Commit once per phase after verification.
13. Push immediately after every successful commit unless the user explicitly asks to hold the push or the remote is unavailable.
14. For Institutional Core, push separately to `institutional` only when the remote is aligned or after an explicit sync phase; never use `--force` to satisfy routine discipline.

## M46 Entry Criteria

M46 is accepted when these criteria are true:

- Customer cockpit source of truth: local `customer_success_renewal` evidence plus `customer_cockpit.json` metadata.
- Data privacy boundary: no license payloads, private keys, raw checkout events or relay secrets in the UI.
- Ownership: Product defines fields, Backend owns persistence/API, Frontend owns cockpit UI, Security owns redaction/exclusions, QA owns tests.
- GO/NO-GO criteria: customers listed, renewal window visible, activation/support state visible, expansion opportunity visible, safe claims preserved.
- Test plan: JS contracts, backend pytest, static tests, E2E screenshots if cockpit UI is added.

## Living Contracts Index

- Frontend load order: `docs/ARCHITECTURE.md` and `backend/sqx-edge-tool/test_dashboard_static.py`.
- Dashboard quick actions: `app/js/dashboard.js`, `app/css/dashboard.css`, `app/SQX_Dashboard_v6.html` and `backend/sqx-edge-tool/test_dashboard_static.py`.
- Manifest mirror: `backend/sqx-edge-tool/tools/build_frontend_manifest.py` and `app/js/manifest-data.js`.
- BlockSettings source contract: real `.sqb` files live in `backend/sqx-edge-tool/resources/blocksettings/`, are indexed by `backend/sqx-edge-tool/tools/build_blocksettings_manifest.py`, and produce `backend/sqx-edge-tool/config/blocksettings_manifest.json`. Project Generator must patch generated `.cfx` `<Blocks>` from that source, not from legacy display names.
- BlockSettings Info contract: `backend/sqx-edge-tool/config/ui_manifest.json` field `blockSettingsInfo`, mirrored into `app/js/manifest-data.js`, rendered by `app/js/dashboard.js` inside tab id `filtros`.
- Product/commercial state: `backend/sqx-edge-tool/config/product_manifest.json`.
- Portable distribution: `package_portable.ps1`, `audit_distribution.ps1`, `release_checklist.ps1`.
- Commercial gates: `backend/sqx-edge-tool/tools/*` and `docs/sales/*`.
- Internal automation gate: this document, especially G3 risk levels, agent matrix and local tooling notes.
- Backup retention and artifact cleanup: `docs/maintenance/BACKUP_RETENTION_POLICY.md`, `docs/maintenance/ARTIFACT_CLEANUP_20260514.md` and ignored manifests under `backups/cleanup-*`.
- CI baseline: `.github/workflows/tests.yml` and `requirements-dev.txt`.
- Public application repository: `https://github.com/CryptoLeon78/SQX_Edge_Suite_v1.git` (local remote `origin`).
- Institutional Core repository: `https://github.com/CryptoLeon78/SQX_Institutional_Core.git` (local remote `institutional`; synced by G5 merge, preserving institutional-only files and analyzer assets).
- Private commercial boundary: `docs/PRIVATE_COMMERCIAL_DOCS.md`, `docs/PRIVATE_COMMERCIAL_SPLIT_PLAN.md`, `docs/private_commercial_manifest.json` and `private_commercial_split.py`.
- Private commercial repository: `https://github.com/CryptoLeon78/sqx-edge-commercial-private` (private, baseline commit `ed79719`).
- Public commercial pointers: `docs/PUBLIC_COMMERCIAL_POINTERS.md`; public `docs/MONETIZATION_*`, `docs/sales/*` and Pro resource packs are redacted pointers.
- Roadmap state: `docs/MODULARIZATION_NEXT_STEPS.md` plus private commercial roadmap copies.
- T10o replacement route contract: `docs/T10O_REPLACEMENT_ROUTE_CONTRACT.md`, `templates/SQX_Edge_Tester_Portal/scripts/replacement-route-contract-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10p fresh staging route preflight: `docs/T10P_FRESH_STAGING_ROUTE_PREFLIGHT.md`, `templates/SQX_Edge_Tester_Portal/scripts/fresh-staging-route-preflight-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10q fresh staging route access check: `docs/T10Q_FRESH_STAGING_ROUTE_ACCESS_CHECK.md`, `templates/SQX_Edge_Tester_Portal/scripts/fresh-staging-route-access-check-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10r fresh staging project created: `docs/T10R_FRESH_STAGING_PROJECT_CREATED.md`, `templates/SQX_Edge_Tester_Portal/scripts/fresh-staging-project-created-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10s staging protection verified: `docs/T10S_STAGING_PROTECTION_VERIFIED.md`, `templates/SQX_Edge_Tester_Portal/scripts/staging-protection-verified-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10t staging local link configured: `docs/T10T_STAGING_LOCAL_LINK_CONFIGURED.md`, `templates/SQX_Edge_Tester_Portal/scripts/staging-local-link-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10u staging deployment readiness gate: `docs/T10U_STAGING_DEPLOYMENT_READINESS_GATE.md`, `templates/SQX_Edge_Tester_Portal/scripts/staging-deployment-readiness-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10v controlled staging deploy rollback: `docs/T10V_CONTROLLED_STAGING_DEPLOY_ROLLBACK.md`, `templates/SQX_Edge_Tester_Portal/scripts/controlled-staging-deploy-rollback-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10w provider target mapping investigation: `docs/T10W_PROVIDER_TARGET_MAPPING_INVESTIGATION.md`, `templates/SQX_Edge_Tester_Portal/scripts/provider-target-mapping-investigation-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10x explicit preview target rollback: `docs/T10X_EXPLICIT_PREVIEW_TARGET_ROLLBACK.md`, `templates/SQX_Edge_Tester_Portal/scripts/explicit-preview-target-rollback-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10y no-deploy provider dashboard decision: `docs/T10Y_NO_DEPLOY_PROVIDER_DASHBOARD_DECISION.md`, `templates/SQX_Edge_Tester_Portal/scripts/no-deploy-provider-dashboard-decision-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10z provider dashboard correction package: `docs/T10Z_PROVIDER_DASHBOARD_CORRECTION_PACKAGE.md`, `templates/SQX_Edge_Tester_Portal/scripts/provider-dashboard-correction-package-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10aa provider dashboard evidence record: `docs/T10AA_PROVIDER_DASHBOARD_EVIDENCE_RECORD.md`, `templates/SQX_Edge_Tester_Portal/scripts/provider-dashboard-evidence-record-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ab manual dashboard evidence ingest: `docs/T10AB_MANUAL_DASHBOARD_EVIDENCE_INGEST.md`, `templates/SQX_Edge_Tester_Portal/scripts/manual-dashboard-evidence-ingest-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ah Next proxy migration gate: `docs/T10AH_NEXT_PROXY_MIGRATION.md`, `templates/SQX_Edge_Tester_Portal/src/middleware.ts`, `templates/SQX_Edge_Tester_Portal/scripts/next-proxy-migration-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ai Cloudflare provider-project preflight: `docs/T10AI_CLOUDFLARE_PROVIDER_PROJECT_PREFLIGHT.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-provider-project-preflight-proof.mjs`, `templates/SQX_Edge_Tester_Portal/wrangler.jsonc` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10aj Cloudflare project shell gate: `docs/T10AJ_CLOUDFLARE_PROJECT_SHELL.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-project-shell-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajb Cloudflare auth handoff: `docs/T10AJB_CLOUDFLARE_AUTH_HANDOFF.md`, `templates/SQX_Edge_Tester_Portal/cloudflare-shell-evidence.example.json`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-auth-handoff-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajc Cloudflare shell evidence ingest: `docs/T10AJC_CLOUDFLARE_SHELL_EVIDENCE_INGEST.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-shell-evidence-ingest-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajd Cloudflare shell evidence capture checklist: `docs/T10AJD_CLOUDFLARE_SHELL_EVIDENCE_CAPTURE.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-shell-evidence-capture-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10aje Cloudflare read-only shell capture: `docs/T10AJE_CLOUDFLARE_READONLY_SHELL_CAPTURE.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-readonly-shell-capture-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajf Cloudflare shell creation decision: `docs/T10AJF_CLOUDFLARE_SHELL_CREATION_DECISION.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-shell-creation-decision-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajg Cloudflare first deploy approval gate: `docs/T10AJG_CLOUDFLARE_FIRST_DEPLOY_APPROVAL_GATE.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-first-deploy-approval-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajh Cloudflare first deploy readiness: `docs/T10AJH_CLOUDFLARE_FIRST_DEPLOY_READINESS.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-first-deploy-readiness-proof.mjs`, `templates/SQX_Edge_Tester_Portal/package-lock.json` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10aji Cloudflare first deploy rollback: `docs/T10AJI_CLOUDFLARE_FIRST_DEPLOY_ROLLBACK.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-first-deploy-rollback-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajj Cloudflare route onboarding decision: `docs/T10AJJ_CLOUDFLARE_ROUTE_ONBOARDING_DECISION.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-route-onboarding-decision-proof.mjs`, `templates/SQX_Edge_Tester_Portal/wrangler.jsonc` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajk Cloudflare route access precreate: `docs/T10AJK_CLOUDFLARE_ROUTE_ACCESS_PRECREATE.md`, `templates/SQX_Edge_Tester_Portal/cloudflare-route-access-precreate.example.json`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-route-access-precreate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajl Cloudflare hostname zone selection: `docs/T10AJL_CLOUDFLARE_HOSTNAME_ZONE_SELECTION.md`, `docs/T10AJL_OPERATOR_UNLOCK_KIT.md`, `templates/SQX_Edge_Tester_Portal/cloudflare-hostname-zone-selection.example.json`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-hostname-zone-selection-proof.mjs`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-hostname-zone-selection-prepare.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajm Workers.dev shell gate: `docs/T10AJM_WORKERS_DEV_SHELL_GATE.md`, `templates/SQX_Edge_Tester_Portal/cloudflare/shell-worker.js`, `templates/SQX_Edge_Tester_Portal/wrangler.shell.example.jsonc`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-workers-dev-shell-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajn Controlled Workers.dev shell deploy: `docs/T10AJN_CONTROLLED_WORKERS_DEV_SHELL_DEPLOY.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-workers-dev-shell-deploy-proof.mjs`, ignored `cloudflare-hostname-zone-selection.local.json` evidence and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ajo Workers.dev Access verified: `docs/T10AJO_WORKERS_DEV_ACCESS_VERIFIED.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-workers-dev-access-proof.mjs`, ignored `cloudflare-hostname-zone-selection.local.json` evidence and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ak Access policy boundary: `docs/T10AK_ACCESS_POLICY_BOUNDARY.md`, `templates/SQX_Edge_Tester_Portal/cloudflare-access-policy-boundary.example.json`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-access-policy-boundary-proof.mjs`, ignored `cloudflare-access-policy-boundary.local.json` evidence and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10al Controlled real app deploy gate: `docs/T10AL_CONTROLLED_REAL_APP_DEPLOY_GATE.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-controlled-real-app-deploy-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10am Controlled real app deploy result: `docs/T10AM_CONTROLLED_REAL_APP_DEPLOY_RESULT.md`, ignored `templates/SQX_Edge_Tester_Portal/cloudflare-real-app-deploy.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-real-app-deploy-result-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10an Protected tester publication target gate: `docs/T10AN_PROTECTED_TESTER_PUBLICATION_TARGET_GATE.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-protected-tester-publication-target-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ao Controlled workers.dev publication preflight: `docs/T10AO_CONTROLLED_WORKERS_DEV_PUBLICATION_PREFLIGHT.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-controlled-workers-dev-publication-preflight-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ap Controlled workers.dev publication result: `docs/T10AP_CONTROLLED_WORKERS_DEV_PUBLICATION_RESULT.md`, ignored `templates/SQX_Edge_Tester_Portal/cloudflare-workers-dev-publication.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-workers-dev-publication-result-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10aq Tester access handoff no URL leak: `docs/T10AQ_TESTER_ACCESS_HANDOFF_NO_URL_LEAK.md`, `templates/SQX_Edge_Tester_Portal/tester-access-handoff.example.json`, ignored `tester-access-handoff.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-access-handoff-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ar Private tester account activation gate: `docs/T10AR_PRIVATE_TESTER_ACCOUNT_ACTIVATION_GATE.md`, `templates/SQX_Edge_Tester_Portal/tester-account-activation.example.json`, ignored `tester-account-activation.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-account-activation-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10as Private tester activation evidence ingest: `docs/T10AS_PRIVATE_TESTER_ACTIVATION_EVIDENCE_INGEST.md`, `templates/SQX_Edge_Tester_Portal/tester-activation-evidence-ingest.example.json`, ignored `tester-account-activation.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-activation-evidence-ingest-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10at Private tester URL share approval gate: `docs/T10AT_PRIVATE_TESTER_URL_SHARE_APPROVAL_GATE.md`, `templates/SQX_Edge_Tester_Portal/tester-url-share-approval.example.json`, ignored `tester-url-share-approval.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-url-share-approval-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10au Private first tester smoke gate: `docs/T10AU_PRIVATE_FIRST_TESTER_SMOKE_GATE.md`, `templates/SQX_Edge_Tester_Portal/tester-first-smoke.example.json`, ignored `tester-first-smoke.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-first-smoke-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10av Private tester cohort expansion gate: `docs/T10AV_PRIVATE_TESTER_COHORT_EXPANSION_GATE.md`, `templates/SQX_Edge_Tester_Portal/tester-cohort-expansion.example.json`, ignored `tester-cohort-expansion.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-cohort-expansion-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10aw Private tester feedback intake gate: `docs/T10AW_PRIVATE_TESTER_FEEDBACK_INTAKE_GATE.md`, `templates/SQX_Edge_Tester_Portal/tester-feedback-intake.example.json`, ignored `tester-feedback-intake.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-feedback-intake-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ax Private tester feedback triage gate: `docs/T10AX_PRIVATE_TESTER_FEEDBACK_TRIAGE_GATE.md`, `templates/SQX_Edge_Tester_Portal/tester-feedback-triage.example.json`, ignored `tester-feedback-triage.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-feedback-triage-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ay Private tester action plan gate: `docs/T10AY_PRIVATE_TESTER_ACTION_PLAN_GATE.md`, `templates/SQX_Edge_Tester_Portal/tester-action-plan.example.json`, ignored `tester-action-plan.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-action-plan-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10az Private tester action execution gate: `docs/T10AZ_PRIVATE_TESTER_ACTION_EXECUTION_GATE.md`, `templates/SQX_Edge_Tester_Portal/tester-action-execution.example.json`, ignored `tester-action-execution.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-action-execution-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ba Private tester result validation gate: `docs/T10BA_PRIVATE_TESTER_RESULT_VALIDATION_GATE.md`, `templates/SQX_Edge_Tester_Portal/tester-result-validation.example.json`, ignored `tester-result-validation.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-result-validation-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10bb Private tester iteration decision gate: `docs/T10BB_PRIVATE_TESTER_ITERATION_DECISION_GATE.md`, `templates/SQX_Edge_Tester_Portal/tester-iteration-decision.example.json`, ignored `tester-iteration-decision.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-iteration-decision-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10bc Private tester next iteration gate: `docs/T10BC_PRIVATE_TESTER_NEXT_ITERATION_GATE.md`, `templates/SQX_Edge_Tester_Portal/tester-next-iteration.example.json`, ignored `tester-next-iteration.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-next-iteration-gate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- TL1 Tester launch candidate: `docs/TL1_TESTER_LAUNCH_CANDIDATE.md`, `templates/SQX_Edge_Tester_Portal/tester-launch-candidate.example.json`, ignored `tester-launch-candidate.local.json`, `templates/SQX_Edge_Tester_Portal/scripts/tester-launch-candidate-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ac replacement tester route options: `docs/T10AC_REPLACEMENT_TESTER_ROUTE_OPTIONS.md`, `templates/SQX_Edge_Tester_Portal/scripts/replacement-tester-route-options-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ad Cloudflare Access preflight: `docs/T10AD_CLOUDFLARE_ACCESS_PREFLIGHT.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-access-preflight-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ae Cloudflare runtime compatibility: `docs/T10AE_CLOUDFLARE_RUNTIME_COMPATIBILITY.md`, `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-runtime-compatibility-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10af OpenNext Cloudflare adapter package: `docs/T10AF_OPENNEXT_CLOUDFLARE_ADAPTER_PACKAGE.md`, `templates/SQX_Edge_Tester_Portal/wrangler.jsonc`, `templates/SQX_Edge_Tester_Portal/open-next.config.ts`, `templates/SQX_Edge_Tester_Portal/.dev.vars.example`, `templates/SQX_Edge_Tester_Portal/scripts/opennext-cloudflare-adapter-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- T10ag OpenNext local smoke: `docs/T10AG_OPENNEXT_LOCAL_SMOKE.md`, `templates/SQX_Edge_Tester_Portal/scripts/opennext-local-smoke-proof.mjs` and `templates/SQX_Edge_Tester_Portal/package.json`.
- External repo comparison: `docs/EXTERNAL_REPO_COMPARISON_JOSE.md`, `docs/J1_CHAMPION_CHALLENGER_CONTRACT.md`, `docs/J2_CHAMPION_CHALLENGER_CORE.md`, `docs/J3_CHAMPION_CHALLENGER_OOS.md`, `docs/J4_CHAMPION_CHALLENGER_UI.md`, `docs/J5_CHAMPION_CHALLENGER_REGIME_EGT.md`, `docs/J6_CHAMPION_CHALLENGER_EXPORT_HANDOFF.md`, `docs/J7_TEMPORAL_HEALTH_EGT_V2_CONTRACT.md`, `docs/J8_TEMPORAL_HEALTH_EGT_V2_HELPERS.md`, `docs/J9_TEMPORAL_HEALTH_EGT_V2_UI.md`, `docs/J10_TEMPORAL_HEALTH_EGT_V2_HANDOFF.md`, `docs/J11_DIRECTIONAL_COHERENCE_SCORE.md`, `app/js/modules/champion-challenger-core.js`, `app/js/modules/champion-challenger.js`, `app/js/modules/champion-challenger-regime.js`, `tests/js/contracts/champion_challenger_core_contracts.mjs`, `tests/js/contracts/champion_challenger_ui_contracts.mjs`, `tests/js/contracts/champion_challenger_regime_contracts.mjs`, `backend/sqx-edge-tool/tools/plan_quality_advisor.py`, `backend/sqx-edge-tool/tools/multi_timeframe_scoring.py`, `backend/sqx-edge-tool/tools/multi_timeframe_metric_gate.py`, `backend/sqx-edge-tool/tools/first_party_metric_source.py`, `backend/sqx-edge-tool/tools/multi_timeframe_source_intake.py`, `backend/sqx-edge-tool/tools/multi_timeframe_plan_artifacts.py`, `backend/sqx-edge-tool/tools/ohlc_metric_builder.py`, `backend/sqx-edge-tool/tools/real_mtf_pipeline_run.py`, `backend/sqx-edge-tool/tools/dukas_mt5_ohlc_download.py`, `backend/sqx-edge-tool/tools/mt5_ipc_diagnostic.py`, `backend/sqx-edge-tool/core/mtf_evidence.py` and `app/js/modules/mtf-evidence.js`.
- Strategy Builder / Only One Platform track: `docs/SB1_STRATEGY_BUILDER_DISCOVERY.md`, `docs/SB2_STRATEGY_BUILDER_WORKFLOW.md`, `docs/SB3_STRATEGY_BUILDER_PROTOTYPE.md`, `docs/SB4_STRATEGY_BUILDER_IMPORT_EXPORT.md`, `docs/SB5_STRATEGY_BUILDER_PROJECT_GENERATOR_PREFILL.md`, `docs/SB6_STRATEGY_BUILDER_PRESET_HANDOFF.md`, `docs/SB7_STRATEGY_BUILDER_VIEWS_HANDOFF.md`, `docs/SB8_STRATEGY_BUILDER_AUDIT_WORKFLOW.md`, `docs/SB9_STRATEGY_BUILDER_CLEANER_HANDOFF.md`, `docs/SB10_STRATEGY_BUILDER_BUYER_HANDOFF_PACK.md`, `docs/SB11_STRATEGY_BUILDER_BUYER_PACK_IMPORT_REVIEW.md`, `docs/SB12_STRATEGY_BUILDER_BUYER_SESSION_CHECKLIST.md`, `docs/SB13_STRATEGY_BUILDER_BUYER_SESSION_SUMMARY_EXPORT.md`, `docs/SB14_STRATEGY_BUILDER_BUYER_SESSION_PRINTABLE_NOTES.md`, `docs/SB15_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_CASE_BUNDLE.md`, `docs/SB16_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_RESOLUTION_CHECKLIST.md`, `docs/SB17_STRATEGY_BUILDER_EVIDENCE_HANDOFF_INDEX.md`, `app/js/modules/strategy-builder-core.js`, `app/js/modules/strategy-builder.js`, starting from the J6 handoff, Project Generator profiles, SQX Views packs, MTF evidence, Strategy Cleaner boundaries, unified buyer handoff packs, guided buyer session checklists, redacted buyer session summaries, printable operator notes, local support-case bundles, support resolution checklists and reduced evidence handoff indexes.
- UX-NAV2 Mining Control / Project Generator trim: `Pipeline State` is now surfaced as `Mining Control`; Project Generator no longer exposes starter profiles, objective families or the `Entrega comprador .cfx` panel.
- Retired Project Generator buyer handoff track: `docs/PG7_PROJECT_GENERATOR_BUYER_CFX_HANDOFF.md` remains historical documentation only; the active UI/code path was removed from Project Generator in UX-NAV2.
- Cloud Tester Access track: `docs/T1_CLOUD_TESTER_ARCHITECTURE_CONTRACT.md`, `docs/T2_TESTER_PORTAL_BOOTSTRAP.md`, `docs/T3_TESTER_AUTH_DATA_CONTRACT.md`, `docs/T4_LOGIN_SESSION_PROTOTYPE.md`, `docs/T5_TESTER_PRO_ENTITLEMENT_GATES.md`, `docs/T6_15_DAY_EXPIRY_RENEWAL_FLOW.md`, `docs/T7_ADMIN_TESTER_CONSOLE.md`, `docs/T8_TESTER_PORTAL_SECURITY_HARDENING.md`, `docs/T9_PROTECTED_VERCEL_PREVIEW_PREFLIGHT.md`, `docs/T9B_VERCEL_PREVIEW_DEPLOY_ROLLBACK.md`, `docs/T9C_VERCEL_DEPLOYMENT_PROTECTION_GATE.md`, `docs/T9D_VERCEL_AUTH_PROTECTION_VERIFIED.md`, `docs/T9E_PROTECTED_PREVIEW_DEPLOY_ROLLBACK.md`, `docs/T9F_PREVIEW_PATH_PROOF.md`, `docs/T9G_PRIVATE_GIT_PREVIEW_SOURCE.md`, `docs/T10_INTERNAL_PREVIEW_ROLLBACK.md`, `docs/T10B_VERCEL_TARGET_GUARD.md`, `docs/T10C_EXPLICIT_API_PREVIEW_PATH.md`, `docs/T10D_EXPLICIT_API_PREVIEW_ROLLBACK.md`, `docs/T10E_OMITTED_TARGET_PREVIEW_ROLLBACK.md`, `docs/T10F_SEPARATED_PREVIEW_PROJECT.md`, `docs/T10G_LINKED_PREVIEW_PROJECT_PROOF.md`, `docs/T10H_PROTECTED_PREVIEW_ROLLBACK.md`, `docs/T10I_CLI_DEFAULT_PREVIEW_ROUTE.md`, `docs/T10J_CLI_DEFAULT_PREVIEW_COMMAND_ROLLBACK.md`, `docs/T10K_CLI_DEFAULT_PREVIEW_ROLLBACK.md`, `docs/T10L_VERCEL_ROUTE_INVESTIGATION.md`, `docs/T10M_VERCEL_CONFIG_HARDENING.md`, `docs/T10N_VERCEL_ROUTE_DECISION.md`, `docs/T10O_REPLACEMENT_ROUTE_CONTRACT.md`, `docs/T10P_FRESH_STAGING_ROUTE_PREFLIGHT.md`, `docs/T10Q_FRESH_STAGING_ROUTE_ACCESS_CHECK.md`, `docs/T10R_FRESH_STAGING_PROJECT_CREATED.md`, `docs/T10S_STAGING_PROTECTION_VERIFIED.md`, `docs/T10T_STAGING_LOCAL_LINK_CONFIGURED.md`, `docs/T10U_STAGING_DEPLOYMENT_READINESS_GATE.md`, `docs/T10V_CONTROLLED_STAGING_DEPLOY_ROLLBACK.md`, `docs/T10W_PROVIDER_TARGET_MAPPING_INVESTIGATION.md`, `docs/T10X_EXPLICIT_PREVIEW_TARGET_ROLLBACK.md`, `docs/T10Y_NO_DEPLOY_PROVIDER_DASHBOARD_DECISION.md`, `docs/T10Z_PROVIDER_DASHBOARD_CORRECTION_PACKAGE.md`, `docs/T10AA_PROVIDER_DASHBOARD_EVIDENCE_RECORD.md`, `templates/SQX_Edge_Tester_Portal/`; private `SQX_Edge_Tester_Portal` repo; Access/Security Gatekeeper ownership; Vercel Deployment Protection, tester auth, 15-day renewal, admin operator preview, audit, watermark and kill-switch contracts.
- Cloud Tester Access replacement decisions: `docs/T10AB_MANUAL_DASHBOARD_EVIDENCE_INGEST.md`, `docs/T10AC_REPLACEMENT_TESTER_ROUTE_OPTIONS.md`, `docs/T10AD_CLOUDFLARE_ACCESS_PREFLIGHT.md`, `docs/T10AE_CLOUDFLARE_RUNTIME_COMPATIBILITY.md`, `docs/T10AF_OPENNEXT_CLOUDFLARE_ADAPTER_PACKAGE.md`, `docs/T10AG_OPENNEXT_LOCAL_SMOKE.md`, `docs/T10AH_NEXT_PROXY_MIGRATION.md`, `docs/T10AI_CLOUDFLARE_PROVIDER_PROJECT_PREFLIGHT.md`, `docs/T10AJ_CLOUDFLARE_PROJECT_SHELL.md`, `docs/T10AJB_CLOUDFLARE_AUTH_HANDOFF.md`, `docs/T10AJC_CLOUDFLARE_SHELL_EVIDENCE_INGEST.md`, `docs/T10AJD_CLOUDFLARE_SHELL_EVIDENCE_CAPTURE.md`, `docs/T10AJE_CLOUDFLARE_READONLY_SHELL_CAPTURE.md`, `docs/T10AJF_CLOUDFLARE_SHELL_CREATION_DECISION.md`, `docs/T10AJG_CLOUDFLARE_FIRST_DEPLOY_APPROVAL_GATE.md`, `docs/T10AJH_CLOUDFLARE_FIRST_DEPLOY_READINESS.md`, `docs/T10AJI_CLOUDFLARE_FIRST_DEPLOY_ROLLBACK.md`, `docs/T10AJJ_CLOUDFLARE_ROUTE_ONBOARDING_DECISION.md`, `docs/T10AJK_CLOUDFLARE_ROUTE_ACCESS_PRECREATE.md`, `docs/T10AJL_CLOUDFLARE_HOSTNAME_ZONE_SELECTION.md`, `docs/T10AJL_OPERATOR_UNLOCK_KIT.md`, Cloudflare Access preflight planning and no-deploy route selection before any tester URL.
- Real-data validation and release evidence: `docs/A59_REAL_DATA_VALIDATION.md`, `docs/A60_MT5_ACTIVE_TERMINAL_MODE.md`, `docs/A61_MT5_IPC_DIAGNOSTIC.md`, `docs/A62_RECENT_BARS_REAL_MTF_GO.md`, `docs/R44_A63_PORTABLE_AFTER_REAL_MTF_GO.md`, `docs/R45_CONTROLLED_PUBLICATION_PLAN.md` and `docs/R47_CONTROLLED_COMMERCIAL_RELEASE.md`.
- M97 commercial execution gate: `docs/MONETIZATION_M97.md`, `docs/sales/APPROVED_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M96_DECISION_EXECUTION.md`, `backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m96_decision_execution.json`, `backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m96_decision_execution.py` and `backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution/`.
- M98 commercial execution monitor: `docs/MONETIZATION_M98.md`, `docs/sales/APPROVED_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M96_DECISION_EXECUTION_MONITOR.md`, `backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m96_decision_execution_monitor.json`, `backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m96_decision_execution_monitor.py` and `backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution_monitor/`.
- M99 commercial next movement decision: `docs/MONETIZATION_M99.md`, `docs/sales/NEXT_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M98_DECISION.md`, `backend/sqx-edge-tool/config/next_controlled_commercial_movement_from_m98_decision.json`, `backend/sqx-edge-tool/tools/next_controlled_commercial_movement_from_m98_decision.py` and `backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m98_decision/`.

## Security Notes

- Never commit `backend/sqx-edge-tool/config/license.json`.
- Never package private keys, signed customer licenses, fulfillment events, relay data, `.env` files, backups, `material de diagnostico/` or internal release tools.
- Any new internal M46+ or A58+ operator tool must be added to product manifest exclusions, packaging exclusions, audit deny-lists, release checklist assertions and tests.
- Any new `tools/*`, `data/*`, `docs/sales/*` or Pro resource must declare one of: public, public redaction pointer, private-only, or excluded from portable packaging.
- Move buyer logs, commercial gates, pricing experiments, support scripts and checkout evidence to a private repository before wider public distribution.
- Keep `docs/private-commercial/`, `commercial-private/` and `private-commercial/` local-only staging folders ignored by git.
- Keep `material de diagnostico/` local-only and ignored by git; use it only as diagnostic input when reproducing bugs or comparing user-provided examples. If a diagnostic sample becomes a permanent test fixture, create a sanitized copy under `tests/fixtures/` instead of moving the original folder into git.
- Do not deploy tester access, create tester accounts, publish Vercel URLs, rotate tester passwords or send renewal emails without explicit user approval for that exact external action.

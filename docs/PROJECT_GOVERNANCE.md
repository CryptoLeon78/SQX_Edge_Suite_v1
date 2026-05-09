# SQX Edge Project Governance

Documento vivo para coordinar agentes especializados, ownership por area y reglas de fase antes de continuar con M46.

## Current State

- Current phase completed: T9c - Vercel Deployment Protection Gate NO-GO.
- Current product/commercial state: `next_controlled_commercial_movement_from_m98_decision_ready`.
- Next implementation phase: T9d - enable or verify Vercel Authentication/Password Protection before retrying preview deploy, M100 - execute exactly the M99-approved controlled commercial movement, R46 - publish the verified GitHub Release only with explicit approval, V10 - SQX Views pack comparison, or SB18 - Strategy Builder buyer evidence export polish.
- Governance baseline: G6 - Institutional Dashboard Quick Actions Gate.
- Previous governance baseline: G5 - Institutional Core Synchronized Gate.
- Earlier governance baseline: G4 - Institutional Core Repository Gate.
- Earlier governance baseline: G3 - Internal Automation and Agent Gate.
- Earlier governance baseline: G2 - Governance Lookup Before Work.
- Historical governance baseline: G1 - Specialist Agent Operating Model.

## Specialist Agents

| Agent | Scope | Primary Ownership | Required Checks |
| --- | --- | --- | --- |
| Frontend/UI | Dashboard, responsive UI, tabs, JS modules, visual state. | `app/SQX_Dashboard_v6.html`, `app/css`, `app/js`, `tests/js`, `tests/ui_e2e`. | JS contracts, Python static tests, E2E screenshots when UI changes. |
| Backend/API | Local Flask API, core business logic, manifests, local persistence. | `backend/sqx-edge-tool/api`, `backend/sqx-edge-tool/core`, `backend/sqx-edge-tool/config`, backend tests. | Backend pytest suite, API tests, manifest/static tests when contracts change. |
| QA/Release | Portable ZIP, release checklist, audit, START/STOP, SHA256 evidence. | `backend/sqx-edge-tool/tools/package_portable.ps1`, `audit_distribution.ps1`, `release_checklist.ps1`, launchers, `dist` evidence. | Full pytest, JS contracts, `git diff --check`, release checklist for ZIP phases. |
| Monetization/Product | Pro offer, pricing, support, renewal, buyer journey, safe claims. | `docs/MONETIZATION_ROADMAP.md`, `docs/MONETIZATION_M*.md`, `docs/sales`, product manifest, README. | Commercial docs tests, safe-claims review, roadmap/status alignment. |
| Security/Distribution | Secrets, license material, relay exposure, packaging exclusions. | `.gitignore`, product manifest security, packaging/audit scripts, relay settings, license manager. | Packaging tests, audit rules, sensitive-file staged review. |
| Architecture/Docs | Load order, module contracts, ADRs, ownership matrix, roadmap hygiene. | `docs/ARCHITECTURE.md`, `docs/PROJECT_GOVERNANCE.md`, `docs/decisions`, roadmap docs, module contracts. | Static docs tests, load-order contracts, roadmap consistency checks. |
| Access/Security Gatekeeper | Tester auth, sessions, renewals, cloud access, anti-distribution controls and Vercel security. | Future `SQX_Edge_Tester_Portal`, `templates/SQX_Edge_Tester_Portal/`, `docs/T1_CLOUD_TESTER_ARCHITECTURE_CONTRACT.md`, `docs/T2_TESTER_PORTAL_BOOTSTRAP.md`, `docs/T3_TESTER_AUTH_DATA_CONTRACT.md`, `docs/T4_LOGIN_SESSION_PROTOTYPE.md`, `docs/T5_TESTER_PRO_ENTITLEMENT_GATES.md`, `docs/T6_15_DAY_EXPIRY_RENEWAL_FLOW.md`, `docs/T7_ADMIN_TESTER_CONSOLE.md`, `docs/T8_TESTER_PORTAL_SECURITY_HARDENING.md`, `docs/T9_PROTECTED_VERCEL_PREVIEW_PREFLIGHT.md`, `docs/T9B_VERCEL_PREVIEW_DEPLOY_ROLLBACK.md`, `docs/T9C_VERCEL_DEPLOYMENT_PROTECTION_GATE.md`, tester access contracts, Vercel env/protection docs, audit and watermark policies. | Unauthenticated blocked, expired/denied/blocked tester blocked, active `tester_pro` allowed, admin operator preview protected, rate limit and audit contracts, no secrets in git, security headers and deployment protection reviewed. |

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
- Asset detail/category rows expose quick actions to promote a candidate into Plan Mining or prefill Project Generator custom inputs.
- Pipeline State includes a compact operational health panel and graph-style funnel visualization while preserving editable counts and local-only state.
- Required checks: JS syntax/contracts, static dashboard tests, backend pytest, `git diff --check` and E2E screenshots for Pipeline State and Project Generator prefill flow.

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

## Local Tooling Notes

- Required and present for normal work: Git, Python virtualenv, pytest, Node/npm, PowerShell and `rg`.
- Optional but useful for upcoming release/CI automation: GitHub CLI `gh`, especially for inspecting Actions, creating releases and managing PR/release metadata.
- Playwright remains on-demand for frontend visual/E2E work; install temporarily only when UI behavior needs browser validation.
- MetaTrader5 tooling is only needed for real-data A58/A62 style phases, not for governance, packaging or commercial monitor phases.
- Tunnels such as ngrok/cloudflared should remain out of the default path until relay staging work explicitly needs them.

## Phase Workflow

Every implementation phase must follow this loop:

1. Consult Project Governance or the Specialist Agents ownership matrix before every work phase/message.
2. Confirm working tree state.
3. Create a backup before changing files.
4. Define active agent ownership and expected touched areas.
5. Apply the G3 automation risk level if the phase adds tools, evidence, gates or external actions.
6. Implement narrowly against the phase objective.
7. Update docs, manifests and tests in the same phase when contracts move.
8. Run required checks for touched areas.
9. Run E2E screenshots when frontend behavior or `manifest-data.js` changes.
10. Clean temporary Playwright/npm artifacts.
11. Commit once per phase after verification.
12. Push immediately after every successful commit unless the user explicitly asks to hold the push or the remote is unavailable.
13. For Institutional Core, push separately to `institutional` only when the remote is aligned or after an explicit sync phase; never use `--force` to satisfy routine discipline.

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
- Product/commercial state: `backend/sqx-edge-tool/config/product_manifest.json`.
- Portable distribution: `package_portable.ps1`, `audit_distribution.ps1`, `release_checklist.ps1`.
- Commercial gates: `backend/sqx-edge-tool/tools/*` and `docs/sales/*`.
- Internal automation gate: this document, especially G3 risk levels, agent matrix and local tooling notes.
- CI baseline: `.github/workflows/tests.yml` and `requirements-dev.txt`.
- Public application repository: `https://github.com/CryptoLeon78/SQX_Edge_Suite_v1.git` (local remote `origin`).
- Institutional Core repository: `https://github.com/CryptoLeon78/SQX_Institutional_Core.git` (local remote `institutional`; synced by G5 merge, preserving institutional-only files and analyzer assets).
- Private commercial boundary: `docs/PRIVATE_COMMERCIAL_DOCS.md`, `docs/PRIVATE_COMMERCIAL_SPLIT_PLAN.md`, `docs/private_commercial_manifest.json` and `private_commercial_split.py`.
- Private commercial repository: `https://github.com/CryptoLeon78/sqx-edge-commercial-private` (private, baseline commit `ed79719`).
- Public commercial pointers: `docs/PUBLIC_COMMERCIAL_POINTERS.md`; public `docs/MONETIZATION_*`, `docs/sales/*` and Pro resource packs are redacted pointers.
- Roadmap state: `docs/MODULARIZATION_NEXT_STEPS.md` plus private commercial roadmap copies.
- External repo comparison: `docs/EXTERNAL_REPO_COMPARISON_JOSE.md`, `docs/J1_CHAMPION_CHALLENGER_CONTRACT.md`, `docs/J2_CHAMPION_CHALLENGER_CORE.md`, `docs/J3_CHAMPION_CHALLENGER_OOS.md`, `docs/J4_CHAMPION_CHALLENGER_UI.md`, `docs/J5_CHAMPION_CHALLENGER_REGIME_EGT.md`, `docs/J6_CHAMPION_CHALLENGER_EXPORT_HANDOFF.md`, `docs/J7_TEMPORAL_HEALTH_EGT_V2_CONTRACT.md`, `docs/J8_TEMPORAL_HEALTH_EGT_V2_HELPERS.md`, `docs/J9_TEMPORAL_HEALTH_EGT_V2_UI.md`, `docs/J10_TEMPORAL_HEALTH_EGT_V2_HANDOFF.md`, `docs/J11_DIRECTIONAL_COHERENCE_SCORE.md`, `app/js/modules/champion-challenger-core.js`, `app/js/modules/champion-challenger.js`, `app/js/modules/champion-challenger-regime.js`, `tests/js/contracts/champion_challenger_core_contracts.mjs`, `tests/js/contracts/champion_challenger_ui_contracts.mjs`, `tests/js/contracts/champion_challenger_regime_contracts.mjs`, `backend/sqx-edge-tool/tools/plan_quality_advisor.py`, `backend/sqx-edge-tool/tools/multi_timeframe_scoring.py`, `backend/sqx-edge-tool/tools/multi_timeframe_metric_gate.py`, `backend/sqx-edge-tool/tools/first_party_metric_source.py`, `backend/sqx-edge-tool/tools/multi_timeframe_source_intake.py`, `backend/sqx-edge-tool/tools/multi_timeframe_plan_artifacts.py`, `backend/sqx-edge-tool/tools/ohlc_metric_builder.py`, `backend/sqx-edge-tool/tools/real_mtf_pipeline_run.py`, `backend/sqx-edge-tool/tools/dukas_mt5_ohlc_download.py`, `backend/sqx-edge-tool/tools/mt5_ipc_diagnostic.py`, `backend/sqx-edge-tool/core/mtf_evidence.py` and `app/js/modules/mtf-evidence.js`.
- Strategy Builder / Only One Platform track: `docs/SB1_STRATEGY_BUILDER_DISCOVERY.md`, `docs/SB2_STRATEGY_BUILDER_WORKFLOW.md`, `docs/SB3_STRATEGY_BUILDER_PROTOTYPE.md`, `docs/SB4_STRATEGY_BUILDER_IMPORT_EXPORT.md`, `docs/SB5_STRATEGY_BUILDER_PROJECT_GENERATOR_PREFILL.md`, `docs/SB6_STRATEGY_BUILDER_PRESET_HANDOFF.md`, `docs/SB7_STRATEGY_BUILDER_VIEWS_HANDOFF.md`, `docs/SB8_STRATEGY_BUILDER_AUDIT_WORKFLOW.md`, `docs/SB9_STRATEGY_BUILDER_CLEANER_HANDOFF.md`, `docs/SB10_STRATEGY_BUILDER_BUYER_HANDOFF_PACK.md`, `docs/SB11_STRATEGY_BUILDER_BUYER_PACK_IMPORT_REVIEW.md`, `docs/SB12_STRATEGY_BUILDER_BUYER_SESSION_CHECKLIST.md`, `docs/SB13_STRATEGY_BUILDER_BUYER_SESSION_SUMMARY_EXPORT.md`, `docs/SB14_STRATEGY_BUILDER_BUYER_SESSION_PRINTABLE_NOTES.md`, `docs/SB15_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_CASE_BUNDLE.md`, `docs/SB16_STRATEGY_BUILDER_BUYER_SESSION_SUPPORT_RESOLUTION_CHECKLIST.md`, `docs/SB17_STRATEGY_BUILDER_EVIDENCE_HANDOFF_INDEX.md`, `app/js/modules/strategy-builder-core.js`, `app/js/modules/strategy-builder.js`, starting from the J6 handoff, Project Generator profiles, SQX Views packs, MTF evidence, Strategy Cleaner boundaries, unified buyer handoff packs, guided buyer session checklists, redacted buyer session summaries, printable operator notes, local support-case bundles, support resolution checklists and reduced evidence handoff indexes.
- Project Generator buyer handoff track: `docs/PG7_PROJECT_GENERATOR_BUYER_CFX_HANDOFF.md`, `app/js/modules/project-generator-config.js`, `app/js/modules/project-generator-bindings.js`, `app/js/project-generator-main.js` and the `Entrega comprador .cfx` panel in `app/SQX_Dashboard_v6.html`.
- Cloud Tester Access track: `docs/T1_CLOUD_TESTER_ARCHITECTURE_CONTRACT.md`, `docs/T2_TESTER_PORTAL_BOOTSTRAP.md`, `docs/T3_TESTER_AUTH_DATA_CONTRACT.md`, `docs/T4_LOGIN_SESSION_PROTOTYPE.md`, `docs/T5_TESTER_PRO_ENTITLEMENT_GATES.md`, `docs/T6_15_DAY_EXPIRY_RENEWAL_FLOW.md`, `docs/T7_ADMIN_TESTER_CONSOLE.md`, `docs/T8_TESTER_PORTAL_SECURITY_HARDENING.md`, `docs/T9_PROTECTED_VERCEL_PREVIEW_PREFLIGHT.md`, `docs/T9B_VERCEL_PREVIEW_DEPLOY_ROLLBACK.md`, `docs/T9C_VERCEL_DEPLOYMENT_PROTECTION_GATE.md`, `templates/SQX_Edge_Tester_Portal/`; future private `SQX_Edge_Tester_Portal` repo; Access/Security Gatekeeper ownership; Vercel Deployment Protection, tester auth, 15-day renewal, admin operator preview, audit, watermark and kill-switch contracts.
- Real-data validation and release evidence: `docs/A59_REAL_DATA_VALIDATION.md`, `docs/A60_MT5_ACTIVE_TERMINAL_MODE.md`, `docs/A61_MT5_IPC_DIAGNOSTIC.md`, `docs/A62_RECENT_BARS_REAL_MTF_GO.md`, `docs/R44_A63_PORTABLE_AFTER_REAL_MTF_GO.md`, `docs/R45_CONTROLLED_PUBLICATION_PLAN.md` and `docs/R47_CONTROLLED_COMMERCIAL_RELEASE.md`.
- M97 commercial execution gate: `docs/MONETIZATION_M97.md`, `docs/sales/APPROVED_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M96_DECISION_EXECUTION.md`, `backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m96_decision_execution.json`, `backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m96_decision_execution.py` and `backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution/`.
- M98 commercial execution monitor: `docs/MONETIZATION_M98.md`, `docs/sales/APPROVED_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M96_DECISION_EXECUTION_MONITOR.md`, `backend/sqx-edge-tool/config/approved_controlled_commercial_movement_from_m96_decision_execution_monitor.json`, `backend/sqx-edge-tool/tools/approved_controlled_commercial_movement_from_m96_decision_execution_monitor.py` and `backend/sqx-edge-tool/data/approved_controlled_commercial_movement_from_m96_decision_execution_monitor/`.
- M99 commercial next movement decision: `docs/MONETIZATION_M99.md`, `docs/sales/NEXT_CONTROLLED_COMMERCIAL_MOVEMENT_FROM_M98_DECISION.md`, `backend/sqx-edge-tool/config/next_controlled_commercial_movement_from_m98_decision.json`, `backend/sqx-edge-tool/tools/next_controlled_commercial_movement_from_m98_decision.py` and `backend/sqx-edge-tool/data/next_controlled_commercial_movement_from_m98_decision/`.

## Security Notes

- Never commit `backend/sqx-edge-tool/config/license.json`.
- Never package private keys, signed customer licenses, fulfillment events, relay data, `.env` files, backups or internal release tools.
- Any new internal M46+ or A58+ operator tool must be added to product manifest exclusions, packaging exclusions, audit deny-lists, release checklist assertions and tests.
- Any new `tools/*`, `data/*`, `docs/sales/*` or Pro resource must declare one of: public, public redaction pointer, private-only, or excluded from portable packaging.
- Move buyer logs, commercial gates, pricing experiments, support scripts and checkout evidence to a private repository before wider public distribution.
- Keep `docs/private-commercial/`, `commercial-private/` and `private-commercial/` local-only staging folders ignored by git.
- Do not deploy tester access, create tester accounts, publish Vercel URLs, rotate tester passwords or send renewal emails without explicit user approval for that exact external action.

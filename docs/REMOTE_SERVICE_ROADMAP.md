# REMOTE SERVICE ROADMAP

## Decision

SQX Edge moves from a user-installed portable product to a hosted Pro service. The final user accesses the app through a protected link, validates email, must have an active paid entitlement and does not install Python, ZIPs, launchers or local dependencies.

The first pilot runs on the operator laptop 24/7 behind Cloudflare Tunnel and Cloudflare Access. SQX paths, `data.db`, templates, BlockSettings and generated artifacts live on the server side. The browser is only the authenticated user interface.

## Product Model

- Primary channel: `remote_service`.
- Access: paid subscription plus validated email.
- Provisioning: checkout webhook activates, renews or cancels access automatically.
- Tester grants: approved testers can receive complete `tester_free` access without payment, but they must authenticate and remain auditable like paid users.
- User isolation: mandatory workspace per user.
- Runtime: laptop-hosted gateway and backend during pilot.
- SQX scope: the remote app prepares `.cfx`, `.vw`, Template Maker outputs, Strategy Control evidence, Champion vs Challenger reviews and exports. It does not expose visual remote control of StrategyQuant X in this phase.
- Legacy portable: internal fallback and rollback path only; not the user-facing commercial flow.
- Repository posture: before active sales, `origin` and `institutional` should be private unless the operator explicitly chooses a public-source commercial strategy.

## Remote Phases

### REMOTE-0 - Documentation And Governance

Record the strategic pivot, add the Remote Service Gate, update architecture, README, privacy/security copy and static tests. No runtime behavior changes.

### REMOTE-1 - Laptop Server Baseline

Turn the operator laptop into a controlled server: auto-start backend/gateway after reboot, health checks, SQX path validation, `data.db` validation, template validation, output validation and watchdog.

Artifacts:

- `docs/REMOTE_1_LAPTOP_SERVER_BASELINE.md`
- `tools/remote_service_preflight.ps1`
- `tools/remote_service_start_server.ps1`
- `tools/remote_service_watchdog.ps1`
- `tools/remote_service_install_startup_task.ps1`

### REMOTE-2 - Cloudflare Tunnel And Domain

Publish the laptop through a custom domain with Cloudflare Tunnel. Do not open router ports. Keep Cloudflare Access in front of the service and prove that unauthenticated requests cannot reach dashboard or API.

Artifacts:

- `docs/REMOTE_2_CLOUDFLARE_TUNNEL_ACCESS.md`
- `docs/examples/remote_tunnel.local.example.json`
- `tools/remote_tunnel_preflight.ps1`
- `tools/remote_tunnel_run.ps1`
- `tools/remote_tunnel_smoke.ps1`
- `tools/remote_tunnel_install_startup_task.ps1`

### REMOTE-RUNBOOK1 - Operator Start/Stop

Give the operator a one-click routine for the active Windows laptop host without returning to the old portable mental model. `START_SQX_EDGE_REMOTE.bat` opens a visible HTA monitor, starts the localhost backend and Cloudflare Tunnel with hidden service operations, waits for Cloudflare Tunnel registration, then shows Backend/Tunnel health. `STOP_SQX_EDGE_REMOTE.bat` opens the same monitor, suppresses startup OK notifications and stops only repo-owned backend/tunnel processes. Monitor actions are guarded so `Arrancar` is disabled when everything is OK and `Detener` is disabled when nothing is running. The monitor uses manual `Refrescar` instead of automatic polling to avoid PowerShell flashes or UI freezes. Legacy `START_SQX_EDGE.bat` and `STOP_SQX_EDGE.bat` must not remain in repository root during the remote pilot.

Artifacts:

- `docs/REMOTE_RUNBOOK1_OPERATOR_START_STOP.md`
- `START_SQX_EDGE_REMOTE.bat`
- `STOP_SQX_EDGE_REMOTE.bat`
- `tools/remote_operator_start.ps1`
- `tools/remote_operator_stop.ps1`
- `tools/remote_operator_status.ps1`
- `tools/remote_operator_monitor.hta`
- `tools/remote_operator_probe.ps1`

Next route:

- Use this runbook before REMOTE-ACCEPT1 browser evidence.
- If either Backend or Tunnel is not green, do not invite testers or continue acceptance evidence.

### REMOTE-OPS1 - Laptop Production Readiness Drill

Before inviting more testers or turning REMOTE-8H into any real movement, validate the laptop as a production-like host without executing expansion. This drill consolidates REMOTE-1 and REMOTE-2 evidence plus app-session, workspace, artifact, revocation and restore smoke into a redacted summary.

Artifacts:

- `docs/REMOTE_OPS1_LAPTOP_READINESS_DRILL.md`
- `docs/examples/remote_ops1_laptop_readiness.local.example.json`
- `backend/sqx-edge-tool/core/remote_ops1_laptop_readiness.py`
- `backend/sqx-edge-tool/tools/remote_ops1_laptop_readiness.py`
- ignored evidence root `.local/remote_service/remote_ops1_laptop_readiness*`
- `Laptop Production Readiness Drill Gate`

Next route:

- `GO_REMOTE_OPS1_LAPTOP_READY` routes back to REMOTE-8H private package evidence.
- `NO_GO_REMOTE_OPS1_LAPTOP_READINESS_BLOCKED` routes to blocker fixes before any tester expansion.
- REMOTE-OPS1 never creates users, grants, checkout links, emails, public URL sharing or automation jobs.

### REMOTE-OPS1B - Cloudflare Operator Handoff

Turns the remaining Cloudflare blocker into a local-only operator handoff. It creates ignored handoff/config templates, verifies `cloudflared` status, keeps placeholders in Git and tells the operator exactly how to finish Tunnel + Access privately.

Artifacts:

- `docs/REMOTE_OPS1B_CLOUDFLARE_OPERATOR_HANDOFF.md`
- `docs/examples/cloudflared-config.local.example.yml`
- `tools/remote_tunnel_operator_handoff.ps1`
- generated ignored files under `.local/remote_service/`

Next route:

- `GO_REMOTE2_TUNNEL_ACCESS_READY_NO_GIT_LEAK` plus anonymous Access smoke allows REMOTE-OPS1 to flip `tunnelPreflightGo` and `accessAnonymousBlocked`.
- `GO_REMOTE_OPS1_LAPTOP_READY` is still required before returning to REMOTE-8H private package evidence.

### REMOTE-2B - Tester Grants And Repository Privacy

Lock the pre-auth product decisions that REMOTE-3 must respect: approved testers get full `tester_free` access without payment but with the same authentication/audit path as paid users, and the working repositories should become private before active sales.

Artifacts:

- `docs/REMOTE_2B_TESTER_GRANTS_REPO_PRIVACY.md`

### REMOTE-3 - Paid Auth And Webhook

Implement first-party user sessions, tester-free grants and checkout webhook activation. Access requires email validation, active entitlement, non-blocked status and valid session. Entitlements include `paid_subscription`, `tester_free` and `internal_operator`. Webhooks must be signed, audited and idempotent.

Artifacts started in REMOTE-3A:

- `docs/REMOTE_3A_REMOTE_ACCESS_FOUNDATION.md`
- `docs/examples/remote_entitlements.local.example.json`
- `backend/sqx-edge-tool/core/remote_access.py`
- `GET /api/remote/access/status`
- `backend/sqx-edge-tool/test_remote_access.py`

Artifacts added in REMOTE-3B:

- `docs/REMOTE_3B_APP_SESSION_GRANT_KEY.md`
- `remote-session-v1`
- `__Host-sqx_remote_session`
- `SQX_REMOTE_SESSION_SECRET`
- `POST /api/remote/session/login`
- `GET /api/remote/session/status`
- `POST /api/remote/session/logout`
- tester-free direct app-session creation after Cloudflare Access when entitlement is active; `grantKeyHash` remains a legacy/enforced fallback only when a grant explicitly requires it
- entitlement revalidation on every app-session status check

Artifacts added in REMOTE-3C:

- `docs/REMOTE_3C_PAID_WEBHOOK_PROTECTED_WRITE.md`
- `backend/sqx-edge-tool/core/remote_payments.py`
- `remote-payment-webhook-v1`
- `SQX_REMOTE_PAYMENT_WEBHOOK_SECRET`
- `POST /api/remote/payment/webhook`
- `POST /api/remote/protected/write-pilot`
- `remote-write-pilot-v1`
- idempotent activation/cancellation/expiration/blocking of `paid_subscription` grants;
- protected write audit proof using the app session;
- no workspace-wide mutation until REMOTE-4 derives workspace server-side.

Next REMOTE-4 scope:

- derive workspace from the signed session, never from browser payloads;
- bind uploads, generated `.cfx`, exports, logs and config to that workspace;
- start migrating mutating endpoints behind the remote session and workspace gates.

### REMOTE-SUG1 - Deployment Hardening Review

Evaluate the tester hosting suggestion without changing the active runtime. Adopt zero-ingress, Cloudflare Access/Tunnel, persistence, backups, restart recovery and audit ideas. Keep the active pilot on Windows because SQX resources, PowerShell runbooks, `data.db`, templates and paths are already aligned there.

Artifacts:

- `docs/REMOTE_SUG1_DEPLOYMENT_HARDENING_REVIEW.md`

Operational reinforcement for REMOTE-1/2:

- laptop sleep/lid/power behavior must be reviewed before pilot expansion;
- watchdog and Cloudflare Tunnel restart recovery must remain tested;
- `.local/remote_service/`, workspaces, entitlement data, outputs and logs need backup/restore evidence before adding more users;
- Docker/Ubuntu is deferred until REMOTE-9 compatibility gates prove it does not break SQX resource access.

### REMOTE-4 - Workspace Isolation

Create server-side workspaces per user. All mutable endpoints must derive `workspace_id` from session, never from client input. Generated `.cfx`, views, uploads, strategy imports, exports, logs and config live in the user's workspace.

Artifacts added in REMOTE-4:

- `docs/REMOTE_4_WORKSPACE_ISOLATION.md`
- `backend/sqx-edge-tool/core/remote_workspaces.py`
- `remote-workspace-v1`
- `SQX_REMOTE_WORKSPACES_ROOT`
- `GET /api/remote/workspace/status`
- workspace-aware `POST /api/remote/protected/write-pilot`
- per-workspace layout: `config`, `uploads`, `outputs`, `exports`, `logs`, `tmp`
- per-workspace `workspace_manifest.local.json`
- per-workspace `logs/audit.local.jsonl`

### REMOTE-5 - Remote UX

Replace install/license screens with Pro access state, server readiness, privacy/security notice and support window. Hide internal SQX paths from basic users while still showing operational readiness and traceability.

Artifacts added in REMOTE-5:

- `docs/REMOTE_5_REMOTE_UX.md`
- dashboard Home `remote-pro-panel`
- `app/js/modules/home.js` remote service status model and renderer
- `app/js/dashboard.js` Home remote panel init
- status sources: `GET /api/remote/access/status`, `GET /api/remote/session/status`, `GET /api/remote/workspace/status` and `GET /api/health`
- `Remote UX Disclosure Gate`

### REMOTE-6 - Security And Abuse Controls

Add rate limits, audit logs, visible watermark, kill switch, backup/restore policy, session revocation and blocked-user enforcement. Document incident response for tunnel, payment, webhook and data-isolation issues.

Artifacts added in REMOTE-6:

- `docs/REMOTE_6_SECURITY_ABUSE_CONTROLS.md`
- `backend/sqx-edge-tool/core/remote_security.py`
- `remote-security-v1`
- `SQX_REMOTE_SECURITY_POLICY_PATH`
- `GET /api/remote/security/status`
- `GET /api/remote/security/audit/recent`
- `X-SQX-Remote-Security-Version`
- `Remote Security Abuse Gate`
- dashboard Home security item and `remote-session-watermark`
- session revocation and identity-hash blocking in `backend/sqx-edge-tool/core/remote_access.py`
- redacted workspace audit reader in `backend/sqx-edge-tool/core/remote_workspaces.py`

Next REMOTE-7 scope:

- rewrite buyer-facing offer around web Pro monthly/annual access;
- update onboarding, FAQ and support copy for no-install users;
- align sales docs with authenticated paid access and tester-free grants;
- keep portable/ZIP as internal fallback only.

### REMOTE-7 - Monetization Rewrite

Update offer, onboarding, FAQ, support copy, sales docs and buyer flow to web Pro monthly/annual access. Keep support add-ons and template packs, but remove install/setup as the core promise.

Artifacts added in REMOTE-7:

- `docs/REMOTE_7_MONETIZATION_REWRITE.md`
- `docs/COMMERCIAL_README.md`
- `docs/PUBLIC_ROADMAP.md`
- `Remote Monetization Rewrite Gate`
- product manifest remote commercial contract: `web_pro_monthly`, `web_pro_annual`, `support_assist`, `tester_free` and `internal_fallback`

Next REMOTE-8 scope:

- run one paid/internal user through entitlement, login, workspace, artifact generation, export/download and revocation;
- verify support evidence stays redacted;
- prove workspace isolation before expanding beyond the first user;
- keep portable/ZIP as internal fallback only.

### REMOTE-8 - Controlled Pilot

Run one paid/internal user end to end: payment webhook, login, workspace creation, `.cfx` generation, export/download, revocation and restore. Expand to 3-5 users only after no workspace leakage, no tunnel instability and no entitlement bypass.

Artifacts added in REMOTE-8:

- `docs/REMOTE_8_CONTROLLED_PILOT.md`
- `backend/sqx-edge-tool/core/remote_pilot.py`
- `backend/sqx-edge-tool/tools/remote_controlled_pilot.py`
- `backend/sqx-edge-tool/test_remote_controlled_pilot.py`
- `remote-controlled-pilot-v1`
- ignored evidence root `.local/remote_service/remote8_controlled_pilot/`
- `Controlled Pilot Gate`

Next REMOTE-8B scope:

- run the same flow against the private live tunnel/access environment with one real approved user;
- ingest only redacted private evidence;
- verify cancellation/revocation and restore using operator-owned evidence;
- do not expand to 3-5 users until the private live smoke is GO.

### REMOTE-8B - Live Pilot Evidence Ingest

Records one real live-user smoke after explicit operator approval. No checkout link, protected URL, raw email, Cloudflare identifier, payment payload, support log or workspace path may be committed.

Artifacts added in REMOTE-8B:

- `docs/REMOTE_8B_LIVE_PILOT_EVIDENCE.md`
- `backend/sqx-edge-tool/core/remote_live_pilot.py`
- `backend/sqx-edge-tool/tools/remote_live_pilot_evidence.py`
- `backend/sqx-edge-tool/test_remote_live_pilot.py`
- `docs/examples/remote8b_live_pilot_evidence.local.example.json`
- `remote-live-pilot-evidence-v1`
- ignored evidence root `.local/remote_service/remote8b_live_pilot_evidence*`
- `Live Pilot Evidence Gate`

Next REMOTE-8C scope:

- observe the first real user support loop before inviting more users;
- review tunnel stability, app session behavior, workspace isolation, artifact generation/export and revocation/restore;
- decide explicitly whether to stay at one user, fix blockers or expand to 3-5 users.

## WAIT Workstream During REMOTE-8C

WAIT phases are value work allowed while the 24-hour REMOTE-8C observation window runs. They must not expand testers, publish checkout, create grants, send emails or bypass pilot gates.

Status board:

| WAIT | Status | Scope |
| --- | --- | --- |
| WAIT-1 | Completed | Welcome bridge, honest Trust Center and living value backlog. |
| WAIT-2 | Completed | Direct tester Welcome access after Cloudflare, status/next-suggestion cadence and new specialist agents. |
| WAIT-3 | Pending | Trust Evidence Pack: self-assessment evidence, redacted security/privacy summaries and external scan preparation. |
| WAIT-4 | Pending | Commercial onboarding polish: buyer welcome story, first-session microcopy and early-access demo flow. |
| WAIT-5 | Pending | Support/readiness pack: tester support scripts, incident copy, rollback explainer and remote status handoff. |

Count: `2/5` WAIT phases completed after WAIT-2. At the moment WAIT-2 started, `1/5` were complete.

### WAIT-1 - Welcome + Trust Center During REMOTE-8C

WAIT-1 is allowed while REMOTE-8C runs because it does not expand testers, grants, checkout or permissions. It improves buyer/tester confidence by adding a welcome bridge, a Trust Center and a living value backlog.

Artifacts:

- `docs/REMOTE_VALUE_BACKLOG.md`
- Welcome / Trust surface in the dashboard shell.
- `Trust Claims Gate` in governance.

Rules:

- No fictitious auditing company.
- No fake third-party certificates.
- No absolute safety claims.
- External evidence can be referenced only as real scan/audit sources or planned future checks.
- Planned external evidence candidates are MDN HTTP Observatory for HTTP posture, OWASP ZAP Baseline for passive security scanning and real response-header checks on the protected service.

### WAIT-2 - Welcome Direct Tester Access + Operational Cadence

WAIT-2 keeps the same REMOTE-8C safety boundary but removes the duplicated tester-key step from the Welcome flow. Approved `tester_free` users still need Cloudflare Access plus an active entitlement and revocable app session, but the Welcome screen should say `OK todo validado` and offer a protagonist `Acceso DASHBOARD` button instead of asking for another key.

Additional discipline:

- every update should include current state and the next recommended movement when useful;
- I+D / Research Scout, Web & RRSS Creative, Sales & Commercial and Asset Cards Curator are part of the Specialist Agents matrix;
- Asset Cards Curator changes require explicit operator confirmation before any card data, score, rating, timeframe or mapping is modified;
- tester direct access does not broaden the cohort and does not publish protected URLs.

### REMOTE-ACCEPT1 - Real Browser Acceptance Gate

REMOTE-ACCEPT1 is the real-browser stabilization gate created after first tester feedback showed the Welcome copy and `Acceso DASHBOARD` behavior could still feel confusing despite automated tests.

Artifacts added in REMOTE-ACCEPT1:

- `docs/REMOTE_ACCEPT1_BROWSER_ACCEPTANCE.md`
- `docs/examples/remote_accept1_browser_acceptance.local.example.json`
- `backend/sqx-edge-tool/core/remote_browser_acceptance.py`
- `backend/sqx-edge-tool/tools/remote_accept1_browser_acceptance.py`
- `backend/sqx-edge-tool/test_remote_browser_acceptance.py`
- `remote-browser-acceptance-v1`
- ignored evidence root `.local/remote_service/remote_accept1_browser_acceptance*`
- `Real Browser Acceptance Gate`

Acceptance focus:

- Cloudflare Access passes with the approved tester identity;
- Welcome title reads `Bienvenido a` / `SQX Edge Suite`;
- identity copy says the user is validated and can press `Acceso DASHBOARD`;
- no internal wording like `falta crear la sesion de app` is shown;
- one click on `Acceso DASHBOARD` opens the dashboard without bounce-back;
- closing and reopening the browser does not create a persistent app-session expectation;
- evidence is redacted and local-only.

### REMOTE-8C - First User Support Observation And Expansion Decision

Watches the first approved user after REMOTE-8B and turns private support evidence into a GO/NO-GO decision for a tiny cohort expansion. It does not automate invites or payments.

Artifacts added in REMOTE-8C:

- `docs/REMOTE_8C_FIRST_USER_OBSERVATION.md`
- `backend/sqx-edge-tool/core/remote_first_user_observation.py`
- `backend/sqx-edge-tool/tools/remote_first_user_observation.py`
- `backend/sqx-edge-tool/test_remote_first_user_observation.py`
- `docs/examples/remote8c_first_user_observation.local.example.json`
- `remote-first-user-observation-v1`
- ignored evidence root `.local/remote_service/remote8c_first_user_observation*`
- `First User Observation Gate`

Next REMOTE-8D scope:

- prepare a manual tiny cohort activation package for 3-5 users only after REMOTE-8C GO;
- define exact communication, entitlement, support, rollback and pause-rule steps;
- do not create users, send links or change grants automatically.

### REMOTE-8D - Tiny Cohort Activation Package

Prepares the manual package for a 3-5 user cohort after REMOTE-8C, without executing invites, checkout, grants or emails.

Artifacts added in REMOTE-8D:

- `docs/REMOTE_8D_TINY_COHORT_ACTIVATION.md`
- `backend/sqx-edge-tool/core/remote_tiny_cohort_activation.py`
- `backend/sqx-edge-tool/tools/remote_tiny_cohort_activation.py`
- `backend/sqx-edge-tool/test_remote_tiny_cohort_activation.py`
- `docs/examples/remote8d_tiny_cohort_activation.local.example.json`
- `remote-tiny-cohort-activation-v1`
- ignored evidence root `.local/remote_service/remote8d_tiny_cohort_activation*`
- `Tiny Cohort Activation Package Gate`

Next REMOTE-8E scope:

- record the exact manual execution only after the operator approves the REMOTE-8D package;
- verify who was activated, what entitlement class was used and what private message was sent without committing raw emails or private links;
- keep rollback and pause rules active before any further expansion.

### REMOTE-8E - Tiny Cohort Manual Execution Record

Records the exact manual 3-5 user execution after the operator approves the REMOTE-8D package. It validates activated users, entitlement class, private handoff, manual counts and zero automation without committing identities, private URLs, message bodies or local paths.

Artifacts added in REMOTE-8E:

- `docs/REMOTE_8E_TINY_COHORT_EXECUTION.md`
- `backend/sqx-edge-tool/core/remote_tiny_cohort_execution.py`
- `backend/sqx-edge-tool/tools/remote_tiny_cohort_execution.py`
- `backend/sqx-edge-tool/test_remote_tiny_cohort_execution.py`
- `docs/examples/remote8e_tiny_cohort_execution.local.example.json`
- `remote-tiny-cohort-execution-v1`
- ignored evidence root `.local/remote_service/remote8e_tiny_cohort_execution*`
- `Tiny Cohort Manual Execution Record Gate`

Next REMOTE-8F scope:

- monitor the activated tiny cohort before any further expansion;
- keep rollback and pause rules active while support, generation, tunnel, workspace and entitlement signals are observed;
- decide whether to stay, fix blockers, roll back or prepare the next controlled movement.

### REMOTE-8F - Tiny Cohort Monitoring And Pause/Rollback Watch

Watches the 3-5 user cohort after REMOTE-8E and converts private monitoring evidence into a public-safe readiness summary. It must not expand traffic, automate onboarding or widen sales until monitoring evidence is clean and explicitly approved in a later decision phase.

Artifacts added in REMOTE-8F:

- `docs/REMOTE_8F_TINY_COHORT_MONITORING.md`
- `backend/sqx-edge-tool/core/remote_tiny_cohort_monitoring.py`
- `backend/sqx-edge-tool/tools/remote_tiny_cohort_monitoring.py`
- `backend/sqx-edge-tool/test_remote_tiny_cohort_monitoring.py`
- `docs/examples/remote8f_tiny_cohort_monitoring.local.example.json`
- `remote-tiny-cohort-monitoring-v1`
- ignored evidence root `.local/remote_service/remote8f_tiny_cohort_monitoring*`
- `Tiny Cohort Monitoring Gate`

Next REMOTE-8G scope:

- review the clean or blocked monitoring summary as an operator decision;
- choose one of: continue observing, fix blockers, roll back or prepare one next controlled movement;
- keep automation off until the selected next movement receives its own explicit gate.

### REMOTE-8G - Tiny Cohort Decision Review

Turns REMOTE-8F monitoring into a human decision and does not execute traffic, checkout, grants, emails or onboarding automatically. It accepts clean or blocked monitoring, but only clean monitoring can prepare a next controlled movement package.

Artifacts added in REMOTE-8G:

- `docs/REMOTE_8G_TINY_COHORT_DECISION_REVIEW.md`
- `backend/sqx-edge-tool/core/remote_tiny_cohort_decision_review.py`
- `backend/sqx-edge-tool/tools/remote_tiny_cohort_decision_review.py`
- `backend/sqx-edge-tool/test_remote_tiny_cohort_decision_review.py`
- `docs/examples/remote8g_tiny_cohort_decision_review.local.example.json`
- `remote-tiny-cohort-decision-review-v1`
- ignored evidence root `.local/remote_service/remote8g_tiny_cohort_decision_review*`
- `Tiny Cohort Decision Review Gate`

Next REMOTE-8H scope:

- prepare the exact package for the selected next controlled movement only if REMOTE-8G selected `prepare_next_controlled_movement`;
- otherwise route to continued monitoring, blocker fix plan or rollback package;
- keep actual execution in a separate later gate.

### REMOTE-8H - Next Controlled Movement Package

Prepares the exact next movement package after the active decision gate. In the current loop, REMOTE-8L is the source that routes back here with `prepare_next_controlled_movement`; legacy REMOTE-8G evidence is accepted only for older tiny-cohort records. It still does not execute traffic, checkout, grants, emails, onboarding or public URL sharing automatically.

Artifacts added in REMOTE-8H:

- `docs/REMOTE_8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE.md`
- `backend/sqx-edge-tool/core/remote_next_controlled_movement_package.py`
- `backend/sqx-edge-tool/tools/remote_next_controlled_movement_package.py`
- `backend/sqx-edge-tool/test_remote_next_controlled_movement_package.py`
- `docs/examples/remote8h_next_controlled_movement_package.local.example.json`
- `remote-next-controlled-movement-package-v1`
- ignored evidence root `.local/remote_service/remote8h_next_controlled_movement_package*`
- `Next Controlled Movement Package Gate`
- active source bridge: `GO_REMOTE8L_POST_MONITORING_DECISION_REVIEW_READY` + `prepare_next_controlled_movement`
- legacy source bridge: `GO_REMOTE8G_TINY_COHORT_DECISION_REVIEW_READY` + `prepare_next_controlled_movement`

Next REMOTE-8I scope:

- approve or reject execution of the prepared package;
- keep execution separate from package preparation;
- if approved, produce a later execution record rather than mutating access automatically.

### REMOTE-8I - Next Controlled Movement Execution Approval

Approves, rejects or defers execution of the REMOTE-8H package and still does not execute automatically without a separate execution record.

Artifacts added in REMOTE-8I:

- `docs/REMOTE_8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVAL.md`
- `backend/sqx-edge-tool/core/remote_next_controlled_movement_execution_approval.py`
- `backend/sqx-edge-tool/tools/remote_next_controlled_movement_execution_approval.py`
- `backend/sqx-edge-tool/test_remote_next_controlled_movement_execution_approval.py`
- `docs/examples/remote8i_next_controlled_movement_execution_approval.local.example.json`
- `remote-next-controlled-movement-execution-approval-v1`
- ignored evidence root `.local/remote_service/remote8i_next_controlled_movement_execution_approval*`
- `Next Controlled Movement Execution Approval Gate`

Next REMOTE-8J scope:

- if REMOTE-8I approved execution, record the manual execution;
- keep raw identities, protected URLs, grants, handoff copy and local paths private/ignored;
- prove counts match the approved package and automation remains off.

### REMOTE-8J - Manual Execution Record

Records the manual execution authorized by REMOTE-8I and remains redacted, auditable and non-automated.

Artifacts added in REMOTE-8J:

- `docs/REMOTE_8J_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION.md`
- `backend/sqx-edge-tool/core/remote_next_controlled_movement_manual_execution.py`
- `backend/sqx-edge-tool/tools/remote_next_controlled_movement_manual_execution.py`
- `backend/sqx-edge-tool/test_remote_next_controlled_movement_manual_execution.py`
- `docs/examples/remote8j_next_controlled_movement_manual_execution.local.example.json`
- `remote-next-controlled-movement-manual-execution-v1`
- ignored evidence root `.local/remote_service/remote8j_next_controlled_movement_manual_execution*`
- `Next Controlled Movement Manual Execution Gate`

### REMOTE-8K - Post Execution Monitoring

Observes the REMOTE-8J manual execution before any further movement or traffic expansion. It does not invite new users, widen traffic, automate onboarding, send emails, change grants or publish private URLs.

Artifacts added in REMOTE-8K:

- `docs/REMOTE_8K_NEXT_CONTROLLED_MOVEMENT_MONITORING.md`
- `backend/sqx-edge-tool/core/remote_next_controlled_movement_monitoring.py`
- `backend/sqx-edge-tool/tools/remote_next_controlled_movement_monitoring.py`
- `backend/sqx-edge-tool/test_remote_next_controlled_movement_monitoring.py`
- `docs/examples/remote8k_next_controlled_movement_monitoring.local.example.json`
- `remote-next-controlled-movement-monitoring-v1`
- ignored evidence root `.local/remote_service/remote8k_next_controlled_movement_monitoring*`
- `Next Controlled Movement Monitoring Gate`

Next REMOTE-8L scope:

- convert REMOTE-8K monitoring into a human decision;
- keep identities, protected URLs, support notes and local paths private/ignored;
- keep traffic, checkout, email, grant and campaign automation at zero until a later approved movement.

### REMOTE-8L - Post Monitoring Decision Review

Turns REMOTE-8K monitoring into a human decision and does not execute traffic, checkout, grants, emails, onboarding or public URL sharing automatically. It accepts clean or blocked REMOTE-8K monitoring, but only clean monitoring with `prepare_next_decision_review` and zero blockers can prepare another controlled movement package.

Artifacts added in REMOTE-8L:

- `docs/REMOTE_8L_POST_MONITORING_DECISION_REVIEW.md`
- `backend/sqx-edge-tool/core/remote_post_monitoring_decision_review.py`
- `backend/sqx-edge-tool/tools/remote_post_monitoring_decision_review.py`
- `backend/sqx-edge-tool/test_remote_post_monitoring_decision_review.py`
- `docs/examples/remote8l_post_monitoring_decision_review.local.example.json`
- `remote-post-monitoring-decision-review-v1`
- ignored evidence root `.local/remote_service/remote8l_post_monitoring_decision_review*`
- `Post Monitoring Decision Review Gate`

Next route after REMOTE-8L:

- `continue_monitoring` returns to REMOTE-8K observation.
- `fix_blockers` creates a blocker fix plan, with no access mutation.
- `rollback_last_movement` creates a manual rollback package, with no automatic rollback.
- `prepare_next_controlled_movement` routes back to REMOTE-8H package preparation for exactly one movement.

### REMOTE-9 - Containerization / Dedicated Linux Host

Future hardening route only. Consider Ubuntu Server/Docker after auth, workspace isolation, generation paths and backup/restore are proven on the Windows pilot. Do not add a root `Dockerfile`, root `docker-compose.yml` or root `.dockerignore` until SQX resource compatibility, `data.db` access, `.cfx` generation and workspace persistence are verified.

## Required Gates

- `Remote Service Gate`: every remote mutation needs authenticated user, active entitlement, server-derived workspace, audit event and rate-limit boundary.
- `Tester Free Access Gate`: approved testers may have complete app access without payment only through Cloudflare-authenticated identity, explicit `tester_free` entitlement, authenticated app session, audit trail and operator-managed grant. A private grant key can remain configured as a legacy/enforced fallback, but the default Welcome flow must not ask testers for a second key after Cloudflare validation.
- `Remote Session Gate`: app sessions must use `remote-session-v1`, `__Host-sqx_remote_session` as a browser-session cookie, private `SQX_REMOTE_SESSION_SECRET`, secure cookie flags, no persistent `Max-Age`/`Expires`, entitlement revalidation and privacy redaction.
- `Payment Webhook Entitlement Gate`: payment events must use `remote-payment-webhook-v1`, private `SQX_REMOTE_PAYMENT_WEBHOOK_SECRET`, exact-body HMAC verification, idempotent `processedWebhookEvents`, redacted identity and audit-only local logs.
- `Workspace Isolation Gate`: workspace ids must be derived from the active app session only; browser-supplied workspace ids, paths and local SQX resources are ignored or rejected.
- `Remote UX Disclosure Gate`: remote dashboard surfaces may show access state, entitlement class, short workspace id and server readiness, but must not render raw SQX paths, `data.db` paths, output folders, workspace roots, session tokens, grant keys, private URLs, Cloudflare identifiers or raw emails.
- `Remote Security Abuse Gate`: remote endpoints must apply `remote-security-v1` rate limits, kill switch, session revocation, identity-hash blocking, redacted audit visibility and watermark without returning policy paths, raw emails, tokens, local paths or provider secrets.
- `Remote Monetization Rewrite Gate`: buyer-facing material must present protected web Pro monthly/annual access, optional support, authenticated tester-free grants and no-install onboarding; portable ZIP, launchers and offline licenses stay internal fallback only.
- `Controlled Pilot Gate`: pilot work must prove entitlement, login, workspace, artifact generation/export, revocation, restore, isolation and redacted evidence before inviting or expanding users.
- `Live Pilot Evidence Gate`: private live pilot evidence must pass `remote-live-pilot-evidence-v1`, stay local/ignored, redact identity/URL/path/secrets and keep expansion beyond one user blocked until explicit REMOTE-8C approval.
- `First User Observation Gate`: first-user support evidence must pass `remote-first-user-observation-v1`, stay local/ignored, prove at least 24 clean hours, zero unresolved support/security/workspace/generation incidents and keep all expansion actions manual.
- `Real Browser Acceptance Gate`: real-browser acceptance evidence must pass `remote-browser-acceptance-v1`, stay local/ignored, prove one-click `Acceso DASHBOARD`, no Welcome bounce-back, no persistent app-session expectation after browser close and no raw email, protected URL, cookie, token, Cloudflare id or local path leakage.
- `Status + Next Suggestion Cadence Gate`: implementation updates should state current status and the next recommended movement without widening scope. Final summaries must include the real state after all actions and Codex's recommended next project movement based on that state.
- `Specialist Agent Autonomy Gate`: relevant governance agents may be applied as needed; Asset Cards Curator requires explicit operator confirmation before card-data changes.
- `Tiny Cohort Activation Package Gate`: tiny cohort activation packages must pass `remote-tiny-cohort-activation-v1`, require REMOTE-8C GO, keep identities/URLs local, validate 3-5 candidates and keep invites, grants, emails, checkout and URL sharing at zero.
- `Tiny Cohort Manual Execution Record Gate`: manual execution records must pass `remote-tiny-cohort-execution-v1`, require REMOTE-8D GO, keep identities/URLs/messages local, match manual counts to 3-5 activated users and keep automation metrics at zero before monitoring.
- `Tiny Cohort Monitoring Gate`: monitoring evidence must pass `remote-tiny-cohort-monitoring-v1`, require REMOTE-8E GO, prove at least 24 clean hours, 3-5 monitored users, stable access/session/workspace/generation/export/support signals and zero incidents before any next movement review.
- `Tiny Cohort Decision Review Gate`: decision evidence must pass `remote-tiny-cohort-decision-review-v1`, review REMOTE-8F clean/blocked monitoring, keep rationale and identities local, keep execution metrics at zero and require a separate next phase before anything is executed.
- `Next Controlled Movement Package Gate`: package evidence must pass `remote-next-controlled-movement-package-v1`, require REMOTE-8G GO with `prepare_next_controlled_movement`, cap user expansion to 1-2 recipients, keep candidates/copy/URLs local and keep execution metrics at zero.
- `Next Controlled Movement Execution Approval Gate`: approval evidence must pass `remote-next-controlled-movement-execution-approval-v1`, require REMOTE-8H GO, allow only approve/reject/defer, keep decision notes and identities local and keep execution metrics at zero.
- `Next Controlled Movement Manual Execution Gate`: manual execution evidence must pass `remote-next-controlled-movement-manual-execution-v1`, require REMOTE-8I approval, match manual counts to the approved package and keep automation metrics at zero before monitoring.
- `Next Controlled Movement Monitoring Gate`: post-execution monitoring evidence must pass `remote-next-controlled-movement-monitoring-v1`, require REMOTE-8J GO, prove at least 24 clean hours, keep private monitoring evidence local and keep support/security/workspace/generation/export incidents at zero before any decision review.
- `Post Monitoring Decision Review Gate`: decision evidence must pass `remote-post-monitoring-decision-review-v1`, review REMOTE-8K clean/blocked monitoring, keep rationale and identities local, keep execution metrics at zero and only route to REMOTE-8H when REMOTE-8K is clean, requested decision review and has zero blockers.
- `Deployment Hardening Review Gate`: hosting suggestions must be reviewed against active REMOTE gates before implementation.
- `Containerization Deferral Gate`: Docker/Linux must remain future hardening until SQX compatibility, workspace isolation and backup/restore are proven.
- `Laptop Production Readiness Drill Gate`: REMOTE-OPS1 must prove laptop, backend, SQX resources, Cloudflare Tunnel/Access, app session, workspace, artifact generation, revocation and restore readiness from ignored local evidence before any next controlled movement can proceed.
- `Repository Privacy Gate`: before active sales, `origin` and `institutional` should be private or the operator must explicitly accept public-source commercial exposure.
- `Workspace Isolation Gate`: no endpoint accepts arbitrary workspace paths or user ids from browser payloads.
- `Tunnel Exposure Gate`: local backend must not be reachable directly from the public internet.
- `Webhook Entitlement Gate`: payment events must be signature-verified, idempotent and auditable before access changes.
- `Fallback Portable Gate`: portable packaging may remain as internal rollback only and must not reappear in final-user onboarding unless explicitly approved.

## Acceptance Criteria For Pilot

- User can access from browser with no installation.
- Cloudflare Access and app auth both block anonymous access.
- Approved tester-free users can access complete features through auth without payment while remaining auditable and revocable.
- Paid active user can generate and download a `.cfx`.
- Cancelled or blocked user cannot generate or download.
- Two users cannot see each other's outputs, imports, logs or config.
- Rebooted laptop restores tunnel, backend and gateway automatically.
- Public copy says "controlled, audited and isolated environment", not "zero risk".

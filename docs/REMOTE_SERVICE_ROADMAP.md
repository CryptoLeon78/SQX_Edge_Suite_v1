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
- tester-free grant-key verification by `grantKeyHash`
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

Future controlled phase. It turns REMOTE-8F monitoring into a human decision and does not execute traffic, checkout, grants, emails or onboarding automatically.

### REMOTE-9 - Containerization / Dedicated Linux Host

Future hardening route only. Consider Ubuntu Server/Docker after auth, workspace isolation, generation paths and backup/restore are proven on the Windows pilot. Do not add a root `Dockerfile`, root `docker-compose.yml` or root `.dockerignore` until SQX resource compatibility, `data.db` access, `.cfx` generation and workspace persistence are verified.

## Required Gates

- `Remote Service Gate`: every remote mutation needs authenticated user, active entitlement, server-derived workspace, audit event and rate-limit boundary.
- `Tester Free Access Gate`: approved testers may have complete app access without payment only through an explicit `tester_free` entitlement, authenticated session, audit trail and operator-managed grant.
- `Remote Session Gate`: app sessions must use `remote-session-v1`, `__Host-sqx_remote_session`, private `SQX_REMOTE_SESSION_SECRET`, secure cookie flags, entitlement revalidation and privacy redaction.
- `Payment Webhook Entitlement Gate`: payment events must use `remote-payment-webhook-v1`, private `SQX_REMOTE_PAYMENT_WEBHOOK_SECRET`, exact-body HMAC verification, idempotent `processedWebhookEvents`, redacted identity and audit-only local logs.
- `Workspace Isolation Gate`: workspace ids must be derived from the active app session only; browser-supplied workspace ids, paths and local SQX resources are ignored or rejected.
- `Remote UX Disclosure Gate`: remote dashboard surfaces may show access state, entitlement class, short workspace id and server readiness, but must not render raw SQX paths, `data.db` paths, output folders, workspace roots, session tokens, grant keys, private URLs, Cloudflare identifiers or raw emails.
- `Remote Security Abuse Gate`: remote endpoints must apply `remote-security-v1` rate limits, kill switch, session revocation, identity-hash blocking, redacted audit visibility and watermark without returning policy paths, raw emails, tokens, local paths or provider secrets.
- `Remote Monetization Rewrite Gate`: buyer-facing material must present protected web Pro monthly/annual access, optional support, authenticated tester-free grants and no-install onboarding; portable ZIP, launchers and offline licenses stay internal fallback only.
- `Controlled Pilot Gate`: pilot work must prove entitlement, login, workspace, artifact generation/export, revocation, restore, isolation and redacted evidence before inviting or expanding users.
- `Live Pilot Evidence Gate`: private live pilot evidence must pass `remote-live-pilot-evidence-v1`, stay local/ignored, redact identity/URL/path/secrets and keep expansion beyond one user blocked until explicit REMOTE-8C approval.
- `First User Observation Gate`: first-user support evidence must pass `remote-first-user-observation-v1`, stay local/ignored, prove at least 24 clean hours, zero unresolved support/security/workspace/generation incidents and keep all expansion actions manual.
- `Tiny Cohort Activation Package Gate`: tiny cohort activation packages must pass `remote-tiny-cohort-activation-v1`, require REMOTE-8C GO, keep identities/URLs local, validate 3-5 candidates and keep invites, grants, emails, checkout and URL sharing at zero.
- `Tiny Cohort Manual Execution Record Gate`: manual execution records must pass `remote-tiny-cohort-execution-v1`, require REMOTE-8D GO, keep identities/URLs/messages local, match manual counts to 3-5 activated users and keep automation metrics at zero before monitoring.
- `Tiny Cohort Monitoring Gate`: monitoring evidence must pass `remote-tiny-cohort-monitoring-v1`, require REMOTE-8E GO, prove at least 24 clean hours, 3-5 monitored users, stable access/session/workspace/generation/export/support signals and zero incidents before any next movement review.
- `Deployment Hardening Review Gate`: hosting suggestions must be reviewed against active REMOTE gates before implementation.
- `Containerization Deferral Gate`: Docker/Linux must remain future hardening until SQX compatibility, workspace isolation and backup/restore are proven.
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

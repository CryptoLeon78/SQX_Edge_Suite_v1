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

Next REMOTE-5 scope:

- surface Pro access state and workspace readiness in the dashboard;
- show controlled privacy/security copy to the authenticated user;
- hide raw SQX/server paths from basic users while preserving operational status;
- prepare migration of `.cfx` generation endpoints behind the workspace gate.

### REMOTE-5 - Remote UX

Replace install/license screens with Pro access state, server readiness, privacy/security notice and support window. Hide internal SQX paths from basic users while still showing operational readiness and traceability.

### REMOTE-6 - Security And Abuse Controls

Add rate limits, audit logs, visible watermark, kill switch, backup/restore policy, session revocation and blocked-user enforcement. Document incident response for tunnel, payment, webhook and data-isolation issues.

### REMOTE-7 - Monetization Rewrite

Update offer, onboarding, FAQ, support copy, sales docs and buyer flow to web Pro monthly/annual access. Keep support add-ons and template packs, but remove install/setup as the core promise.

### REMOTE-8 - Controlled Pilot

Run one paid/internal user end to end: payment webhook, login, workspace creation, `.cfx` generation, export/download, revocation and restore. Expand to 3-5 users only after no workspace leakage, no tunnel instability and no entitlement bypass.

### REMOTE-9 - Containerization / Dedicated Linux Host

Future hardening route only. Consider Ubuntu Server/Docker after auth, workspace isolation, generation paths and backup/restore are proven on the Windows pilot. Do not add a root `Dockerfile`, root `docker-compose.yml` or root `.dockerignore` until SQX resource compatibility, `data.db` access, `.cfx` generation and workspace persistence are verified.

## Required Gates

- `Remote Service Gate`: every remote mutation needs authenticated user, active entitlement, server-derived workspace, audit event and rate-limit boundary.
- `Tester Free Access Gate`: approved testers may have complete app access without payment only through an explicit `tester_free` entitlement, authenticated session, audit trail and operator-managed grant.
- `Remote Session Gate`: app sessions must use `remote-session-v1`, `__Host-sqx_remote_session`, private `SQX_REMOTE_SESSION_SECRET`, secure cookie flags, entitlement revalidation and privacy redaction.
- `Payment Webhook Entitlement Gate`: payment events must use `remote-payment-webhook-v1`, private `SQX_REMOTE_PAYMENT_WEBHOOK_SECRET`, exact-body HMAC verification, idempotent `processedWebhookEvents`, redacted identity and audit-only local logs.
- `Workspace Isolation Gate`: workspace ids must be derived from the active app session only; browser-supplied workspace ids, paths and local SQX resources are ignored or rejected.
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

# REMOTE SERVICE ROADMAP

## Decision

SQX Edge moves from a user-installed portable product to a hosted Pro service. The final user accesses the app through a protected link, validates email, must have an active paid entitlement and does not install Python, ZIPs, launchers or local dependencies.

The first pilot runs on the operator laptop 24/7 behind Cloudflare Tunnel and Cloudflare Access. SQX paths, `data.db`, templates, BlockSettings and generated artifacts live on the server side. The browser is only the authenticated user interface.

## Product Model

- Primary channel: `remote_service`.
- Access: paid subscription plus validated email.
- Provisioning: checkout webhook activates, renews or cancels access automatically.
- User isolation: mandatory workspace per user.
- Runtime: laptop-hosted gateway and backend during pilot.
- SQX scope: the remote app prepares `.cfx`, `.vw`, Template Maker outputs, Strategy Control evidence, Champion vs Challenger reviews and exports. It does not expose visual remote control of StrategyQuant X in this phase.
- Legacy portable: internal fallback and rollback path only; not the user-facing commercial flow.

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

### REMOTE-3 - Paid Auth And Webhook

Implement first-party user sessions and checkout webhook activation. Access requires email validation, active paid entitlement, non-blocked status and valid session. Webhooks must be signed, audited and idempotent.

### REMOTE-4 - Workspace Isolation

Create server-side workspaces per user. All mutable endpoints must derive `workspace_id` from session, never from client input. Generated `.cfx`, views, uploads, strategy imports, exports, logs and config live in the user's workspace.

### REMOTE-5 - Remote UX

Replace install/license screens with Pro access state, server readiness, privacy/security notice and support window. Hide internal SQX paths from basic users while still showing operational readiness and traceability.

### REMOTE-6 - Security And Abuse Controls

Add rate limits, audit logs, visible watermark, kill switch, backup/restore policy, session revocation and blocked-user enforcement. Document incident response for tunnel, payment, webhook and data-isolation issues.

### REMOTE-7 - Monetization Rewrite

Update offer, onboarding, FAQ, support copy, sales docs and buyer flow to web Pro monthly/annual access. Keep support add-ons and template packs, but remove install/setup as the core promise.

### REMOTE-8 - Controlled Pilot

Run one paid/internal user end to end: payment webhook, login, workspace creation, `.cfx` generation, export/download, revocation and restore. Expand to 3-5 users only after no workspace leakage, no tunnel instability and no entitlement bypass.

## Required Gates

- `Remote Service Gate`: every remote mutation needs authenticated user, active entitlement, server-derived workspace, audit event and rate-limit boundary.
- `Workspace Isolation Gate`: no endpoint accepts arbitrary workspace paths or user ids from browser payloads.
- `Tunnel Exposure Gate`: local backend must not be reachable directly from the public internet.
- `Webhook Entitlement Gate`: payment events must be signature-verified, idempotent and auditable before access changes.
- `Fallback Portable Gate`: portable packaging may remain as internal rollback only and must not reappear in final-user onboarding unless explicitly approved.

## Acceptance Criteria For Pilot

- User can access from browser with no installation.
- Cloudflare Access and app auth both block anonymous access.
- Paid active user can generate and download a `.cfx`.
- Cancelled or blocked user cannot generate or download.
- Two users cannot see each other's outputs, imports, logs or config.
- Rebooted laptop restores tunnel, backend and gateway automatically.
- Public copy says "controlled, audited and isolated environment", not "zero risk".

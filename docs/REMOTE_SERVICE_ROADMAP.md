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

ROOT-PREVIEW1 adds the production sharing boundary: `/` is a public-safe
commercial preview, `/dashboard` is the protected app entry, and
`tools/remote_link_preview_smoke.ps1` verifies that split before links are
shared with testers or buyers.

CANONICAL-LINK1 fixes the buyer/tester-facing link policy: the only URL to
communicate externally is `https://sqxedgesuite.org/`. That root URL is served
by the public-safe Cloudflare Worker preview and contains the CTA into the
protected dashboard. `app.sqxedgesuite.org/dashboard` is infrastructure behind
Cloudflare Access, and `go.sqxedgesuite.org` is only a technical alias/fallback
for preview diagnostics, not a second commercial link.

REMOTE-ASSET1 fixes the clean-session dashboard asset boundary: the protected
dashboard HTML now points CSS/JS/vendor/non-public assets to `/dashboard/...`
and the backend serves those prefixed paths from the same dashboard surface.
This prevents authenticated `/dashboard` HTML from rendering without CSS/JS in
incognito/tester browsers when root asset paths have a different Access context
or no app session cache.

Current verification: on 2026-05-18 the operator verified the fix in an
incognito browser and an external tester redacted as `tester-ref-asset1`
reported that the dashboard renders correctly and works after Cloudflare
Access. The incident is documented in
`docs/REMOTE_ASSET1_PROTECTED_DASHBOARD_ASSET_INCIDENT.md`.

Artifacts:

- `docs/REMOTE_OPS1B_CLOUDFLARE_OPERATOR_HANDOFF.md`
- `docs/REMOTE_ASSET1_PROTECTED_DASHBOARD_ASSET_INCIDENT.md`
- `docs/examples/cloudflared-config.local.example.yml`
- `tools/remote_tunnel_operator_handoff.ps1`
- `tools/remote_link_preview_smoke.ps1`
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

### REMOTE-PERSIST1A - Workspace State Persistence

First multi-user persistence bridge. Plan Mining and Strategy Control state now
use the active server-derived workspace as remote source of truth, with the
browser keeping only a compatibility cache.

Artifacts added in REMOTE-PERSIST1A:

- `docs/REMOTE_PERSIST1A_WORKSPACE_STATE.md`
- `backend/sqx-edge-tool/core/remote_workspace_state.py`
- `remote-workspace-state-v1`
- per-workspace `config/workspace_state.sqlite`
- `GET /api/remote/state/bootstrap`
- `POST /api/remote/state/save`
- `GET /api/remote/state/status`
- `app/js/modules/remote-state.js`

Current scope:

- `sqx_plan_user_v1`
- `sqx_pipeline_state_v1`
- `sqx_strategies_user_v1`
- `sqx_strategies_deleted_v1`
- `sqx_view_creator_presets_v1` (added by REMOTE-PERSIST1E)

Still blocking multi-user expansion after REMOTE-PERSIST1A:

- Template Maker IndexedDB must move to workspace persistence. Completed later
  by REMOTE-PERSIST1C.
- Control Panel backup/restore must become workspace-scoped. Completed later by
  REMOTE-PERSIST1D.
- SQX Views/user presets need a remote persistence decision. Completed later by
  REMOTE-PERSIST1E.

### REMOTE-PERSIST1B - Workspace Outputs For Project Generator

Project Generator `.cfx` artifacts now use the active server-derived workspace
when a remote app session exists. Remote generation can no longer write to the
shared configured `output_dir` or accept browser-supplied `output` overrides.

Artifacts added in REMOTE-PERSIST1B:

- `docs/REMOTE_PERSIST1B_WORKSPACE_OUTPUTS.md`
- `backend/sqx-edge-tool/core/remote_workspace_outputs.py`
- `remote-workspace-output-v1`
- per-workspace `outputs/*.cfx`
- workspace-scoped behavior for `GET /api/output`
- workspace-scoped behavior for `POST /api/generate`
- workspace-scoped behavior for `POST /api/generate-custom`
- workspace-scoped behavior for `POST /api/generate-all`
- remote block for `POST /api/open-folder`

Acceptance:

- Local Project Generator output behavior remains compatible.
- Remote sessions write only to `<workspace>/outputs`.
- Remote responses expose `workspace://outputs`, not Windows paths.
- Remote `output` overrides return `remote_output_override_blocked`.
- Two identities cannot see each other's generated `.cfx` files.

Still blocking multi-user expansion after REMOTE-PERSIST1B:

- Control Panel backup/restore must become workspace-scoped. Completed later by
  REMOTE-PERSIST1D.
- SQX Views/user presets need a remote persistence decision. Completed later by
  REMOTE-PERSIST1E.

### REMOTE-PERSIST1C - Template Maker Workspace State

Template Maker strategies, certification state and settings now use the active
server-derived workspace as remote source of truth. Browser IndexedDB remains
only a compatibility cache for local/offline operation.

Artifacts added in REMOTE-PERSIST1C:

- `docs/REMOTE_PERSIST1C_TEMPLATE_MAKER_STATE.md`
- `backend/sqx-edge-tool/core/remote_template_maker_state.py`
- `backend/sqx-edge-tool/test_remote_template_maker_state.py`
- `remote-template-maker-state-v1`
- per-workspace `config/template_maker.sqlite`
- `GET /api/remote/template-maker/bootstrap`
- `POST /api/remote/template-maker/save`
- `GET /api/remote/template-maker/status`
- Template Maker bridge methods: `buildRemoteSnapshot`, `applyRemoteSnapshot`,
  `bootstrapRemoteState`, `saveRemoteState` and
  `getRemotePersistenceStatus`

Acceptance:

- Two remote identities must keep separate Template Maker records.
- Remote bootstrap must hydrate Template Maker from the workspace snapshot.
- An empty workspace snapshot must clear stale browser cache.
- Remote responses must not expose Windows paths or raw identities.
- Local/offline Template Maker remains compatible without a remote session.

Still blocking multi-user expansion after REMOTE-PERSIST1C:

- SQX Views/user presets need a remote persistence decision. Completed later by
  REMOTE-PERSIST1E.

### REMOTE-PERSIST1D - Workspace State Backups And Restore

Control Panel state backup/restore now keeps snapshots inside the active
server-derived workspace for remote sessions. Local operator backups remain in
the historical local folder.

Artifacts added in REMOTE-PERSIST1D:

- `docs/REMOTE_PERSIST1D_STATE_BACKUPS.md`
- `remote-state-backup-v1`
- per-workspace `config/state_backups/state_backup_*.json`
- workspace-aware `POST /api/state/backup`
- workspace-aware `GET /api/state/backups`
- workspace-aware `GET /api/state/restore/<filename>`
- `backend/sqx-edge-tool/test_remote_state_backups.py`

Acceptance:

- Remote sessions can list and restore only their own workspace snapshots.
- Remote requests without app session return `remote_session_required`.
- Backend filters sensitive/non-allowed state keys before writing snapshots.
- Restore resyncs allowed keys through the remote state bridge.
- Local operator backup/restore remains compatible.

Former blocker after REMOTE-PERSIST1D:

- SQX Views/user presets needed a remote persistence decision. Completed by
  REMOTE-PERSIST1E.

### REMOTE-PERSIST1E - SQX Views Workspace Presets

SQX Views user presets now use the active server-derived workspace as source of
truth. The browser keeps `localStorage` only as a compatibility cache.

Artifacts added in REMOTE-PERSIST1E:

- `docs/REMOTE_PERSIST1E_SQX_VIEWS_PRESETS.md`
- `sqx_view_creator_presets_v1`
- `remote-workspace-state-v1`
- workspace-scoped SQX Views presets in `config/workspace_state.sqlite`
- `app/js/modules/view-creator.js` remote save bridge with source
  `sqx-views-presets`

Acceptance:

- Remote bootstrap restores SQX Views presets into the browser compatibility
  cache.
- Saving, importing or deleting SQX Views presets persists them to the active
  workspace.
- Backend ignores non-allowlisted state keys and does not return local paths or
  raw identities.
- Two remote identities cannot see each other's SQX Views presets.

Remaining multi-user expansion blockers after REMOTE-PERSIST1E:

- REMOTE-8C first-user observation/support evidence must still return GO.
- Credential-sharing, support-intake and operator rollback gates remain active.

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

### REMOTE-SEC2 - Credential Sharing Control

Add strict anti-sharing above Cloudflare Access and app sessions. The app now binds remote sessions to a trusted context derived from hashed identity, server-issued device cookie, Cloudflare IP signal and browser signal.

Artifacts added in REMOTE-SEC2:

- `docs/REMOTE_SEC2_CREDENTIAL_SHARING_CONTROL.md`
- `remote-access-control-v1`
- `__Host-sqx_device_id`
- `backend/sqx-edge-tool/core/remote_access_control.py`
- `GET /api/remote/access-control/status`
- `POST /api/remote/access-control/request-approval`
- `tools/remote_access_control_status.ps1`
- `tools/remote_access_control_admin.ps1`
- local ignored stores `.local/remote_service/remote_access_control.local.json` and `.local/remote_service/remote_access_events.local.jsonl`
- Welcome gate pending/blocked context messaging and redacted approval request.

Policy:

- strict mode from the start;
- 2 trusted contexts per identity by default;
- third or revoked contexts cannot open the dashboard until operator approval;
- copied sessions used from another context are blocked;
- raw emails, IPs, device IDs, cookies, tokens, protected URLs and local paths stay out of Git and public JSON.

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
| WAIT-3 / REMOTE-SUPPORT1 | Completed | Safe Control Panel incident intake, redacted local support cases and operator support summary helper. |
| WAIT-4 | Completed | Trust Evidence Pack: self-assessment evidence, redacted security/privacy summaries and external scan preparation. |
| WAIT-5 | Completed | Commercial onboarding polish: stronger buyer welcome story, first-session dashboard guide and early-access Pro copy. |

Count: `5/5` WAIT phases completed after WAIT-5. At the moment WAIT-2 started, `1/5` were complete.

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

### WAIT-3 / REMOTE-SUPPORT1 - Safe Support Intake During REMOTE-8C

REMOTE-SUPPORT1 is allowed while REMOTE-8C runs because it does not change authentication, Cloudflare Access, grants, checkout, protected URLs or cohort size. It adds a support intake surface to `Control Panel`, stores cases only in ignored local evidence and gives the operator a public-safe support summary before any expansion decision.

Artifacts:

- `support-incident-v1`
- `POST /api/support/incidents`
- `backend/sqx-edge-tool/core/support_incidents.py`
- `backend/sqx-edge-tool/tools/remote_support_status.py`
- `tools/remote_support_status.ps1`
- ignored evidence root `.local/remote_service/support_cases/`
- `Support Intake Gate`

Rules:

- The form can attach the existing redacted support diagnostic, but never raw strategy files, local paths, license payloads or browser cookies.
- Open support items or blocker cases must keep REMOTE-8C expansion blocked until the operator resolves them and updates private evidence manually.
- Case status changes are operator-only through `tools/remote_support_status.ps1 -SetStatusCase ... -Status resolved|triaged|dismissed`.
- The intake must not send email, create external tickets, publish GitHub issues or mark `supportLoopObserved` automatically.

### WAIT-4 - Trust Evidence Pack

WAIT-4 is allowed while REMOTE-8C runs because it does not change authentication,
Cloudflare Access, grants, checkout, protected URLs or cohort size. It turns the
Trust Center into a buyer/tester-readable evidence pack with self-assessment,
privacy statement, safety checklist and external scan preparation.

Artifacts:

- `docs/WAIT4_TRUST_EVIDENCE_PACK.md`
- Trust Center `Evidence Pack` cards in the Welcome surface.
- Static contracts requiring `WAIT-4 | Completed` and safe claims.

Rules:

- Evidence shown to users must be public-safe and redacted.
- External scans remain `planned` until real results exist.
- No fake external certificate, fake auditing company or risk-free language.
- WAIT-4 does not satisfy REMOTE-8C by itself and does not allow expansion.

### WAIT-5 - Commercial Onboarding Polish

WAIT-5 closes the WAIT workstream while REMOTE-8C remains the active expansion gate. It strengthens the buyer/tester first impression without changing Cloudflare Access, grants, checkout, sessions, workspaces or tester cohort size.

Artifacts:

- `docs/WAIT5_ONBOARDING_POLISH.md`
- Welcome commercial story with `Primera sesión Pro`.
- Dashboard `Primeros 10 minutos` guide.
- `Commercial Onboarding Claims Gate` in governance.

Rules:

- The customer-facing entry remains the single canonical link `https://sqxedgesuite.org/`.
- Copy can be commercially stronger, but only around productivity, structure, traceability and reduced operational error.
- No profitability promises, fake external certifications, fake auditors, risk-free claims, automated checkout, new grants or tester expansion.
- The dashboard guide may route users to existing tabs only; it must not create new permissions or bypass REMOTE-8C.

### REMOTE-ACCEPT1 - Real Browser Acceptance Gate

REMOTE-ACCEPT1 is the real-browser stabilization gate created after first tester feedback showed the Welcome copy and `Acceso DASHBOARD` behavior could still feel confusing despite automated tests.

Current public-safe status: ignored local evidence returned `GO_REMOTE_ACCEPT1_BROWSER_ACCEPTANCE_CLEAN`. This validates the real browser Welcome/Dashboard path, but does not allow tester expansion without REMOTE-8C observation.

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

Current public-safe status after REMOTE-ACCEPT1: observation has resumed with clean Welcome/Dashboard, app-session/entitlement and tunnel stability signals recorded in ignored local evidence. Expansion remains blocked until the full 24-hour window and support-loop review are complete.

Current public-safe decision on 2026-05-18: ignored local evidence first returned `GO_REMOTE8C_STAY_ONE_USER_DECISION_RECORDED` after 38.0 clean observation hours, support-loop review, zero missing signals, zero open support items and zero unresolved blockers. The operator then explicitly changed the private decision to `expand_3_5`; the rerun returned `GO_REMOTE8C_TINY_COHORT_EXPANSION_READY` only to prepare REMOTE-8D. It did not invite users, create grants, send emails, publish checkout or share protected URLs.

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

- prepare a manual tiny cohort activation package for 3-5 users only after an explicit REMOTE-8C/decision rerun with `expand_3_5`;
- define exact communication, entitlement, support, rollback and pause-rule steps;
- do not create users, send links or change grants automatically.

### REMOTE-8D - Tiny Cohort Activation Package

Prepares the manual package for a 3-5 user cohort after REMOTE-8C, without executing invites, checkout, grants or emails.

Current public-safe status on 2026-05-18: ignored local evidence returned `GO_REMOTE8D_TINY_COHORT_ACTIVATION_PACKAGE_READY` with 3 `tester_free` candidates, full feature scope, all checks present, zero automation blockers and zero invites/grants/checkout links/emails/public URLs created.

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

Current status on 2026-05-18: REMOTE-ASSET1 is resolved and no longer blocks
REMOTE-8E. The operator confirmed 5 users were manually added to Cloudflare
Access, privately guided through first access and observed without problems.
Ignored local evidence returned
`GO_REMOTE8E_TINY_COHORT_MANUAL_EXECUTION_RECORDED` with 5 redacted
`tester_free` users, matching manual counts and zero automation. No raw emails,
protected URLs or private handoff text are committed.

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

Current status on 2026-05-18: REMOTE-8F monitoring is started but not clean.
Ignored local evidence returns `NO_GO_REMOTE8F_TINY_COHORT_MONITORING_BLOCKED`
because the 24h observation window is not complete and workspace isolation,
artifact generation and export/download signals are still pending. This is a
controlled hold state, not a failure requiring rollback.

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
- `Workspace State Persistence Gate`: remote user state must persist in the active workspace, backed by per-workspace storage, with browser storage treated only as cache. Expansion beyond the first controlled user is blocked until Plan Mining, Strategy Control, Project Generator outputs, Template Maker and backup/restore are workspace-scoped or explicitly classified as local-only.
- `Template Maker Workspace State Gate`: remote Template Maker state must use `remote-template-maker-state-v1` in per-workspace `template_maker.sqlite`; browser IndexedDB is only a compatibility cache and cannot be the multi-user source of truth.
- `Control Panel Workspace Backup Gate`: remote `/api/state/*` backup/restore must use `remote-state-backup-v1` under the active workspace `state_backups` directory, filter non-allowed keys and return no local paths.
- `Project Generator Workspace Output Gate`: active remote app sessions must route `/api/generate`, `/api/generate-custom`, `/api/generate-all` and `/api/output` to `remote-workspace-output-v1` in `<workspace>/outputs`; browser-provided remote `output` overrides are blocked; public JSON uses `workspace://outputs` and never returns operator filesystem paths.
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

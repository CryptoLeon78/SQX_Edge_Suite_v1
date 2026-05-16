# REMOTE-SUG1 - Deployment Hardening Review

## Summary

REMOTE-SUG1 evaluates the tester proposal for hosting SQX Edge on a dedicated local server with Cloudflare Zero Trust, Docker and Ubuntu Server.

Decision: **Windows pilot first, Docker/Linux later**.

The proposal is valuable because it reinforces the security and operational shape we already want: zero ingress, Cloudflare Access before the app, persistent state, restart recovery and auditable backups. The Docker/Ubuntu part is deferred because the current pilot depends on StrategyQuant X resources, Windows paths, PowerShell runbooks and local compatibility evidence already validated on the operator laptop.

## Adopted Now

- Zero ingress: no router port forwarding, no public direct access to the laptop, no exposed public IP as an app boundary.
- Cloudflare Tunnel remains the only public path into the service.
- Cloudflare Access remains the mandatory perimeter gate before any app body is visible.
- Backend keeps binding to `127.0.0.1` behind the tunnel.
- REMOTE-1/2 runbooks must include power/sleep prevention, restart recovery, tunnel recovery and health checks.
- Runtime state, entitlement data, workspaces, generated artifacts and logs must have backup/restore evidence before pilot expansion.
- Secrets stay outside Git: tunnel tokens, hostnames, Access IDs, tester emails, grant keys, session secrets and payment/webhook secrets.

## Deferred

- Root `Dockerfile`, root `docker-compose.yml` and root `.dockerignore`.
- Ubuntu Server 24.04 as the active pilot OS.
- `cloudflared` as a container inside the core app deployment.
- Docker volumes as the primary persistence layer for the active pilot.
- Linux-only service management with `systemd`/cron as the active REMOTE-1 implementation.

## Why Docker/Linux Is Deferred

- StrategyQuant X is currently treated as a Windows/local resource in the project evidence.
- The active API and tooling already rely on server-side paths such as `config.json`, `sqx_path`, `sqx_data_db`, templates and output folders.
- Current operational scripts are PowerShell and Windows Task Scheduler based.
- Docker isolation could hide or complicate access to SQX resources, `data.db`, generated `.cfx` outputs, local diagnostic files and future workspace folders.
- A generic Dockerfile with `CMD ["python", "main.py"]` does not match the current backend entrypoint.
- Containerization does not replace the required REMOTE-3/4 gates: app sessions, payment entitlements, workspace isolation, audit and protected write endpoints.

## Future REMOTE-9 Direction

Docker/Linux can be revisited after the remote service proves:

- paid/tester auth works end to end;
- server-derived workspace isolation is complete;
- `.cfx`, `.vw`, Template Maker and Strategy Control artifacts can be generated in isolated workspaces;
- backup/restore is tested from real workspace data;
- SQX resources can be exposed to a container safely or moved behind a Windows worker boundary.

REMOTE-9 may choose one of two future models:

- Linux/Docker hosts the web backend while a Windows worker owns SQX resources.
- Full Linux/Docker hosts only sanitized backend resources if SQX dependency is removed or abstracted.

Until REMOTE-9 is explicitly approved, the active deployment remains **Windows laptop + localhost Flask API + Cloudflare Tunnel + Cloudflare Access + app session**.

## Governance Impact

REMOTE-SUG1 adds two rules:

- `Deployment Hardening Review Gate`: every hosting proposal must be compared against active REMOTE gates before implementation.
- `Containerization Deferral Gate`: Docker/Linux is not added to the root deployment until SQX compatibility, persistence, workspace isolation and backup/restore are proven.

The source proposal remains local-only under `material de diagnostico/propuestas/` and must not be committed.

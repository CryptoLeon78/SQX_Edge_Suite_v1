# REMOTE-RUNBOOK1 - Operator Start/Stop

## Summary

REMOTE-RUNBOOK1 restores a clear operator workflow for the remote service. The user-facing product remains protected web access; these launchers are only for the operator laptop that hosts SQX Edge Suite.

## One-Click Operator Launchers

Start the remote service from the repository root:

```bat
START_SQX_EDGE_REMOTE.bat
```

Stop the remote service from the repository root:

```bat
STOP_SQX_EDGE_REMOTE.bat
```

The launchers use `mshta.exe` to open a small visible HTA monitor instead of leaving CMD/PowerShell command windows in front of the operator. Service operations run hidden while the monitor shows Backend and Tunnel status plus Ollama readiness, SQX 142 compatibility status and SQX 142 performance status with local intelligence (active profile, view coverage, Live Guard, latest evidence and next recommendation), and provides guarded `Arrancar`, `Detener`, `Refrescar` and `Cerrar monitor` buttons. The monitor does not poll automatically; use `Refrescar` when a manual status check is needed.

Button guard rules:

- `Arrancar` is disabled and shown as `En marcha` when Backend, Tunnel and Ollama are all OK.
- `Detener` is disabled and shown as `Detenido` when no service is running.
- While a start/stop operation is running, action buttons temporarily show `Espere...` to avoid duplicate sessions or accidental double clicks.
- After `Arrancar`, the monitor starts/checks Backend, triggers Flask-mediated Ollama autostart via `/api/agent/status`, waits for Cloudflare Tunnel registration and performs a delayed final check before showing the final state. `Refrescar` remains a manual confirmation button, not part of the normal start requirement.
- `STOP_SQX_EDGE_REMOTE.bat` suppresses the startup OK notification and ends with `Estado: servicios detenidos. Backend/Tunnel cerrados.` when both services are closed.

The launchers call PowerShell helpers:

- `tools/remote_operator_status.ps1`
- `tools/remote_operator_monitor.hta`
- `tools/remote_operator_probe.ps1`
- `tools/remote_operator_start.ps1`
- `tools/remote_operator_stop.ps1`

## What START Does

1. Checks `http://127.0.0.1:5050/api/health`.
2. Starts `tools/remote_service_start_server.ps1` if the backend is not healthy.
3. Calls `http://127.0.0.1:5050/api/agent/status` so Flask connects or autostarts Ollama before tester readiness.
4. Starts `tools/remote_tunnel_run.ps1` with the ignored local Cloudflare config if the tunnel is not running.
5. Verifies backend health, Ollama status and a `cloudflared` process using `cloudflared-config.local.yml`.
6. Writes operator logs only under ignored `.local/remote_service/`.
7. Shows a green `OK todo en marcha` state in the visual monitor when Backend, Tunnel and Ollama are ready.
8. Shows SQX 142 runtime/process compatibility from `/api/sqx142/compat/status`; this is operator guidance and does not expose local state to remote users.
9. Shows SQX 142 performance profile/disk/smoke/Live Guard status from `/api/sqx142/performance/status`; this is operator-only guidance and does not expose local paths to remote users.

## What STOP Does

1. Stops only processes belonging to this repo backend or the ignored Cloudflare tunnel config.
2. Verifies the backend is no longer healthy.
3. Verifies the tunnel process is no longer running.

## Security Boundaries

- The backend remains bound to `127.0.0.1:5050`.
- `/api/sqx142/compat/status` is local-operator-only and returns redacted status without local paths.
- `/api/sqx142/performance/status` is local-operator-only and returns redacted profile/resource/smoke status without local paths.
- The tunnel uses `.local/remote_service/cloudflared-config.local.yml`, which stays ignored.
- No protected URL, hostname, Cloudflare account id, tunnel id, Access id, token, email or SQX local path is written to Git.
- Legacy `START_SQX_EDGE.bat` and `STOP_SQX_EDGE.bat` are not allowed at repository root during the remote pilot. They remain only under `packaging/` or inside generated portable fallback ZIPs.

## Operator Flow Before Testers

1. Double click `START_SQX_EDGE_REMOTE.bat`.
2. Confirm the visual monitor shows Backend OK, Tunnel OK, Ollama OK and review the SQX 142 compatibility and performance lines.
3. Open the protected private URL in Chrome.
4. Complete Cloudflare Access.
5. Use `Acceso DASHBOARD`.
6. Run REMOTE-ACCEPT1 private browser evidence before expanding testers.

To close the service after a support window, double click `STOP_SQX_EDGE_REMOTE.bat`.

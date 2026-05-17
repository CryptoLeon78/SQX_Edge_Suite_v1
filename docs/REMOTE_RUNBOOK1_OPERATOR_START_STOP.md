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

The launchers use `mshta.exe` to open a small visible HTA monitor instead of leaving CMD/PowerShell command windows in front of the operator. Service operations run hidden while the monitor shows Backend and Tunnel status and provides guarded `Arrancar`, `Detener`, `Refrescar` and `Cerrar monitor` buttons. The monitor does not poll automatically; use `Refrescar` when a manual status check is needed.

Button guard rules:

- `Arrancar` is disabled and shown as `En marcha` when Backend and Tunnel are both OK.
- `Detener` is disabled and shown as `Detenido` when no service is running.
- While a start/stop operation is running, action buttons temporarily show `Espere...` to avoid duplicate sessions or accidental double clicks.
- After `Arrancar`, the monitor waits for Cloudflare Tunnel registration and performs a delayed final check before showing the final state. `Refrescar` remains a manual confirmation button, not part of the normal start requirement.
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
3. Starts `tools/remote_tunnel_run.ps1` with the ignored local Cloudflare config if the tunnel is not running.
4. Verifies backend health and a `cloudflared` process using `cloudflared-config.local.yml`.
5. Writes operator logs only under ignored `.local/remote_service/`.
6. Shows a green `OK todo en marcha` state in the visual monitor when both services are ready.

## What STOP Does

1. Stops only processes belonging to this repo backend or the ignored Cloudflare tunnel config.
2. Verifies the backend is no longer healthy.
3. Verifies the tunnel process is no longer running.

## Security Boundaries

- The backend remains bound to `127.0.0.1:5050`.
- The tunnel uses `.local/remote_service/cloudflared-config.local.yml`, which stays ignored.
- No protected URL, hostname, Cloudflare account id, tunnel id, Access id, token, email or SQX local path is written to Git.
- Legacy `START_SQX_EDGE.bat` and `STOP_SQX_EDGE.bat` are not allowed at repository root during the remote pilot. They remain only under `packaging/` or inside generated portable fallback ZIPs.

## Operator Flow Before Testers

1. Double click `START_SQX_EDGE_REMOTE.bat`.
2. Confirm the visual monitor shows Backend OK and Tunnel OK.
3. Open the protected private URL in Chrome.
4. Complete Cloudflare Access.
5. Use `Acceso DASHBOARD`.
6. Run REMOTE-ACCEPT1 private browser evidence before expanding testers.

To close the service after a support window, double click `STOP_SQX_EDGE_REMOTE.bat`.

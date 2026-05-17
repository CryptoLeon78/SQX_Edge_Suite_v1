# REMOTE-2 - Cloudflare Tunnel And Access

## Summary

REMOTE-2 pone una frontera Cloudflare delante del servidor local REMOTE-1 sin abrir puertos del router. La ruta objetivo es:

```mermaid
flowchart TD
  U["Usuario Pro en navegador"] --> ACCESS["Cloudflare Access"]
  ACCESS --> TUNNEL["Cloudflare Tunnel"]
  TUNNEL --> LOCAL["http://127.0.0.1:5050"]
  LOCAL --> API["SQX Edge backend local"]
```

Esta fase prepara y valida el camino de dominio + Tunnel + Access. Los valores privados quedan fuera de Git: hostname, zone id, account id, tunnel id, Access app id, policy id, tokens, emails y URLs reales.

## Current Public-Safe Status

Status: `GO_REMOTE2_TUNNEL_ACCESS_READY_NO_GIT_LEAK`.

Validated on 2026-05-17:

- anonymous traffic is redirected to Cloudflare Access before any SQX Edge body is visible;
- an approved identity can complete Access authentication and load the remote dashboard;
- the backend still rejects public-host requests that do not carry the trusted Access identity header;
- private hostname, account, tunnel, policy and user evidence stays only in ignored local files.

## Added Tools

- `tools/remote_tunnel_preflight.ps1`: valida `cloudflared`, REMOTE-1, target local, evidencia privada ignorada y que Access/Tunnel estan listos.
- `tools/remote_tunnel_operator_handoff.ps1`: genera instrucciones privadas locales y plantilla de config ignorada para terminar login, tunel, ruta DNS y Access sin filtrar datos al repo.
- `tools/remote_tunnel_run.ps1`: arranca el tunel con config local ignorada solo si el preflight devuelve GO.
- `tools/remote_tunnel_smoke.ps1`: prueba anonima contra la URL protegida y espera que Cloudflare Access bloquee antes de exponer cuerpo de app.
- `tools/remote_tunnel_install_startup_task.ps1`: registra el tunel en Windows Task Scheduler cuando el operador lo decida.
- `docs/examples/remote_tunnel.local.example.json`: plantilla publica segura para crear `.local/remote_service/cloudflare_tunnel.local.json`.
- `docs/examples/cloudflared-config.local.example.yml`: plantilla publica segura para crear `.local/remote_service/cloudflared-config.local.yml`.

## Private Evidence File

Copy:

```text
docs/examples/remote_tunnel.local.example.json
```

to:

```text
.local/remote_service/cloudflare_tunnel.local.json
```

Only booleans are needed. Do not paste real hostnames, emails, account IDs, tunnel IDs, Access IDs, tokens, screenshots or URLs into tracked files.

## Operator Sequence

1. Confirm REMOTE-1 strict readiness:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_service_preflight.ps1 -RequireSqxReady
```

2. Install/authenticate `cloudflared` locally and create the tunnel in the operator Cloudflare account.
3. Create a private hostname route for the tunnel.
4. Create Cloudflare Access application and policy before sharing any URL.
5. Fill `.local/remote_service/cloudflare_tunnel.local.json` with boolean evidence only.
5.1. Use the local handoff when the Cloudflare state is incomplete:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_operator_handoff.ps1 -CloudflaredPath C:\Tools\cloudflared\cloudflared.exe
```

6. Run preflight:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_preflight.ps1 -RequireEvidence
```

7. Run anonymous Access smoke with the private protected URL:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_smoke.ps1 -ProtectedUrl "<private protected url>"
```

8. Only after both checks pass, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_run.ps1
```

For day-to-day operator use after REMOTE-RUNBOOK1, prefer:

```bat
START_SQX_EDGE_REMOTE.bat
```

It starts the localhost backend and tunnel with hidden service consoles and shows a visual Backend/Tunnel monitor.

## GO / NO-GO

GO status:

```text
GO_REMOTE2_TUNNEL_ACCESS_READY_NO_GIT_LEAK
```

NO-GO status:

```text
NO_GO_REMOTE2_PRIVATE_TUNNEL_ACCESS_EVIDENCE_MISSING
```

NO-GO is expected until the operator has private Cloudflare domain/tunnel/Access evidence. This is intentional; the public repo must never become the source of secrets or private URLs.

## Security Boundary

- No router ports are opened.
- The local backend remains bound to `127.0.0.1`.
- Cloudflare Access must intercept anonymous users before any SQX Edge body is visible.
- A backend `local_api_only` JSON response is not accepted as Access protection; it means Cloudflare forwarded anonymous traffic to the backend and Access is still missing or mis-scoped.
- The app-level auth/session layer remains required after Access in REMOTE-3+.
- The public repository must not contain hostnames, tunnel IDs, Access IDs, account IDs, tokens, emails or private screenshots.

## Handoff To REMOTE-3

REMOTE-3 can begin when:

- `remote_tunnel_preflight.ps1 -RequireEvidence` returns GO.
- `remote_tunnel_smoke.ps1` confirms anonymous traffic is blocked by Access.
- The tunnel can be started/restarted without weakening the local-only backend.
- No private URL or provider identifier has entered Git.

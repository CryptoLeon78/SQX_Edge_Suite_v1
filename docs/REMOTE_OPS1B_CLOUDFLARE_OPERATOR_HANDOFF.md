# REMOTE-OPS1B - Cloudflare Operator Handoff

## Summary

REMOTE-OPS1B converts the remaining REMOTE-OPS1 blocker into a repeatable operator handoff. The backend, SQX 142 alignment, workspaces and local readiness are already green; the remaining work is private Cloudflare evidence: authenticated `cloudflared`, a tunnel route, a protected hostname and an Access policy that blocks anonymous traffic before SQX Edge is visible.

This phase does not create users, grants, checkout links, emails or tester expansion. It also does not store hostnames, Cloudflare IDs, emails or tokens in Git.

## Artifacts

- `tools/remote_tunnel_operator_handoff.ps1` writes ignored local handoff files under `.local/remote_service/`.
- `docs/examples/cloudflared-config.local.example.yml` shows the safe shape of the local tunnel config.
- `.local/remote_service/cloudflare_tunnel_operator_handoff.local.md` is generated locally and ignored.
- `.local/remote_service/cloudflared-config.local.yml.template` is generated locally and ignored.

## Operator Flow

Run the handoff generator:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_operator_handoff.ps1 -CloudflaredPath <LOCAL_CLOUDFLARED_EXE>
```

If the generated local handoff says the origin certificate is missing, authenticate:

```powershell
<LOCAL_CLOUDFLARED_EXE> tunnel login
```

Then create or reuse one tunnel, route the private hostname, create the local ignored config, configure a Cloudflare Access self-hosted application and test:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_preflight.ps1 -CloudflaredPath <LOCAL_CLOUDFLARED_EXE> -RequireEvidence
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_smoke.ps1 -ProtectedUrl "https://<private protected hostname>"
python backend\sqx-edge-tool\tools\remote_ops1_laptop_readiness.py --evidence .local\remote_service\remote_ops1_laptop_readiness.local.json --out-dir .local\remote_service\remote_ops1_laptop_readiness
```

## Evidence To Mark Locally

Only after the real private checks pass, update `.local/remote_service/cloudflare_tunnel.local.json` booleans:

- `hostnameConfiguredPrivately`
- `customDomainOwnedPrivately`
- `cloudflaredAuthenticatedPrivately`
- `tunnelCreatedPrivately`
- `tunnelRouteConfiguredPrivately`
- `cloudflareAccessApplicationCreatedPrivately`
- `cloudflareAccessPolicyCreatedPrivately`
- `accessBlocksAnonymous`
- `accessAllowsApprovedIdentity`

Then update REMOTE-OPS1 local evidence:

- `tunnelPreflightGo`
- `accessAnonymousBlocked`

The readiness validator must remain redacted and public-safe.

Expected private GO chain:

- `GO_REMOTE2_TUNNEL_ACCESS_READY_NO_GIT_LEAK` from `remote_tunnel_preflight.ps1`.
- `GO_REMOTE_OPS1_LAPTOP_READY` from `remote_ops1_laptop_readiness.py`.

## Safety Boundary

- The tunnel target remains `http://127.0.0.1:5050`.
- Router ports stay closed.
- Cloudflare Access must block anonymous users before any dashboard/API body is visible.
- The local backend remains protected by app session, entitlement and workspace gates after Access.
- Tracked files may contain only placeholders and public documentation links.

## Official References

- Cloudflare locally-managed tunnel CLI flow: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/get-started/create-local-tunnel/
- Cloudflare Tunnel routing: https://developers.cloudflare.com/tunnel/routing/
- Cloudflare Access self-hosted applications: https://developers.cloudflare.com/cloudflare-one/applications/configure-apps/self-hosted-apps/
- Cloudflare Access policies: https://developers.cloudflare.com/cloudflare-one/policies/access/

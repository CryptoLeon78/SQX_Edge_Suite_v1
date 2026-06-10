# T10ajn Controlled Workers.dev Shell Deploy

## Objective

T10ajn performs the first real Cloudflare provider mutation after the no-domain decision: create only the harmless `workers.dev` shell Worker target.

This phase intentionally does not deploy the real OpenNext tester portal, does not publish a tester URL, does not create tester accounts and does not commit the generated workers.dev hostname.

## External Action Performed

From `templates/SQX_Edge_Tester_Portal`:

```powershell
npm exec -- wrangler deploy --config wrangler.shell.example.jsonc
```

Result:

```text
WORKERS_DEV_SHELL_TARGET_CREATED
```

The deployed target returned the locked shell response:

```text
404 SQX Edge tester shell locked. No application is published here.
```

## Access Automation Result

Cloudflare Access was not enabled automatically in this phase.

The local Wrangler OAuth token can deploy Workers, but a direct Cloudflare Access Apps API call returned authentication/permission failure for Access APIs. The missing capability is an API path with `Access: Apps and Policies Write`, or a manual dashboard action.

## Current Gate Result

```text
NO_GO_ACCESS_MANUAL_ENABLE_REQUIRED_SHELL_TARGET_EXISTS
```

The shell target exists, but T10ak remains blocked until Cloudflare Access protection is enabled and verified on the shell target.

## Manual Access Enable Steps

Use the Cloudflare dashboard, without sharing the URL with testers:

1. Cloudflare Dashboard > Workers & Pages.
2. Open the Worker named `sqx-edge-tester-portal-preview`.
3. Settings > Domains & Routes.
4. For the `workers.dev` route, click `Enable Cloudflare Access`.
5. Allow only the operator/tester emails approved for the pilot.
6. Save.
7. Verify an anonymous browser request redirects to Cloudflare Access or is blocked before the shell response.
8. Only after that, update ignored local evidence booleans; never commit the hostname or tester URL.

## Ignored Local Evidence

Update only this ignored file:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-hostname-zone-selection.local.json
```

Required private booleans after Access is enabled:

- `workersDevShellTargetExists=true`
- `workersDevAccessProtectionVerified=true`
- `accessHostnameCanBeMatched=true`
- `accessPrecreateAllowed=true`
- `t10akUnlocked=true`
- `testerUrlPublished=false`
- `testerEmailsIncluded=false`

## Verification

Run:

```powershell
npm run proof:cloudflare-workers-dev-shell-deploy
npm run proof:cloudflare-hostname-zone-selection
```

Expected before manual Access enable:

```text
NO_GO_ACCESS_MANUAL_ENABLE_REQUIRED_SHELL_TARGET_EXISTS
NO_GO_PRIVATE_HOSTNAME_ZONE_EVIDENCE_REQUIRED_T10AK_BLOCKED
```

Expected after manual Access enable and ignored evidence update:

```text
GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_READY_FOR_T10AK
GO_CLOUDFLARE_HOSTNAME_ZONE_READY_T10AK_ALLOWED
```

## Security Boundary Preserved

- Real app deployment remains blocked.
- Tester URL publication remains blocked.
- Tester account creation remains blocked.
- Main `wrangler.jsonc` still keeps `workers_dev=false`.
- Shell `workers_dev=true` exists only in `wrangler.shell.example.jsonc`.
- No Cloudflare hostname, account ID, zone ID, token, tester email or tester URL is committed.

## Next Gate

```text
T10ajo_workers_dev_access_manual_enable_evidence
```

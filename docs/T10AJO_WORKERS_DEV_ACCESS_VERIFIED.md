# T10ajo Workers.dev Access Verified

## Objective

T10ajo verifies that the existing harmless `workers.dev` shell is now protected by Cloudflare Access before any real tester app deployment.

This phase does not deploy the real OpenNext tester portal, does not publish a tester URL, does not create tester accounts and does not commit the generated workers.dev hostname.

## Manual Operator Action Confirmed

The operator enabled Cloudflare Access manually on the existing shell Worker target after T10ajn.

The private target remains outside git. Public evidence records only the control result, not the hostname, account ID, Access app ID, policy ID, tester URL or tester emails.

## Anonymous Probe Result

The local anonymous HTTP probe against the private workers.dev target returned:

```text
302 Cloudflare Access redirect
```

The probe did not receive the shell body directly:

```text
directShellBody=false
```

This confirms Cloudflare Access intercepts unauthenticated traffic before the shell response.

## Ignored Local Evidence

The ignored local file was updated only with booleans:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-hostname-zone-selection.local.json
```

Required private booleans after verification:

- `workersDevShellTargetExists=true`
- `workersDevAccessProtectionVerified=true`
- `accessHostnameCanBeMatched=true`
- `accessPrecreateAllowed=true`
- `t10akUnlocked=true`
- `testerUrlPublished=false`
- `testerEmailsIncluded=false`

## Gate Result

```text
GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_VERIFIED_NO_APP
```

T10ak is now allowed as a verification/record phase for the Cloudflare Access application and policy boundary, still before deploying the real app.

## Security Boundary Preserved

- Real app deployment remains blocked until the next explicit approved deployment gate.
- Tester URL publication remains blocked.
- Tester account creation remains blocked.
- Main `wrangler.jsonc` still keeps `workers_dev=false`.
- The shell target is protected by Access before any real app is considered.
- No Cloudflare hostname, account ID, zone ID, Access app ID, Access policy ID, token, tester email or tester URL is committed.

## Verification

Run from `templates/SQX_Edge_Tester_Portal`:

```powershell
npm run proof:cloudflare-workers-dev-access
npm run proof:cloudflare-workers-dev-shell-deploy
npm run proof:cloudflare-hostname-zone-selection
```

Expected:

```text
GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_VERIFIED_NO_APP
GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_READY_FOR_T10AK
GO_CLOUDFLARE_HOSTNAME_ZONE_READY_T10AK_ALLOWED
```

## Next Gate

```text
T10ak_cloudflare_access_application_policy_creation_or_verification
```

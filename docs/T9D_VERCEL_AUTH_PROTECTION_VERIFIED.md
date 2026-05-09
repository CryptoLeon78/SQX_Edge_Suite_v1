# T9d Vercel Authentication Protection Verified

## Objective

T9d enables and verifies Vercel Authentication on the linked tester portal project before any new deploy retry.

This phase changes Vercel project protection settings, but it does not deploy, publish a URL, invite testers, send emails, rotate passwords, connect a production database or share access externally.

## External Action Performed

The linked project `sqx-edge-tester-portal` was updated through the Vercel Project API using the local authenticated Vercel CLI token only in process memory.

Applied project protection:

```text
ssoProtection.deploymentType = prod_deployment_urls_and_all_previews
```

This is Vercel Authentication with Standard Protection, which protects preview deployments and generated deployment URLs while leaving production domains outside the protected scope.

No token value was printed, committed or stored in the repository.

## Verified State

The local protection audit was executed with the token supplied only as temporary `VERCEL_TOKEN`:

```powershell
npm run audit:vercel-protection
```

Result:

```text
status = GO_PROTECTION_VERIFIED
ssoProtectionEnabled = true
ssoDeploymentType = prod_deployment_urls_and_all_previews
passwordProtectionEnabled = false
live = false
latestDeployment = none
domains = 0
externalDeployAllowed = true
```

Vercel project listing still shows no latest production URL for `sqx-edge-tester-portal`.

## Security Boundary

- No deploy was executed in T9d.
- No Vercel URL is committed.
- No raw tester emails are committed.
- No tester invite is sent.
- No renewal email is sent.
- No production database is connected.
- `.vercel` remains ignored local state.
- The local Vercel CLI token is used only in memory and is not added to `.env`, docs or git.

## Next Step

T9e should perform a preview-only deploy retry with strict inspection:

1. run `preflight:vercel-preview`
2. run `audit:vercel-protection` and require `GO_PROTECTION_VERIFIED`
3. deploy through a preview-only path
4. inspect deployment target and aliases before sharing any URL
5. rollback immediately if Vercel reports production target or production aliases
6. keep every URL out of public git docs

## Verification

T9d is accepted when:

- Vercel Authentication Standard Protection is enabled
- `audit:vercel-protection` returns `GO_PROTECTION_VERIFIED`
- no deployment is active before T9e
- static tests assert the T9d contract
- full backend tests pass
- `git diff --check` passes

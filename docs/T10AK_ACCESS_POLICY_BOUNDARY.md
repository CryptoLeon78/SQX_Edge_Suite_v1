# T10ak Access Policy Boundary

## Objective

T10ak records and verifies the Cloudflare Access application/policy boundary for the protected `workers.dev` shell before any real tester app deployment.

This phase does not deploy the real OpenNext tester portal, does not publish a tester URL, does not create tester accounts and does not commit Cloudflare hostnames, Access IDs, policy IDs or tester emails.

## Boundary Confirmed Privately

The Access boundary is accepted only when ignored local evidence confirms:

- The Access application exists.
- The Access application matches the existing workers.dev shell target.
- The Access policy exists.
- The Access policy uses email identity.
- The Access policy allows only the approved pilot users.
- Anonymous traffic redirects to Cloudflare Access before the shell body.
- The shell body is blocked for anonymous users.

The local anonymous probe from T10ajo already confirmed:

```text
302 Cloudflare Access redirect
directShellBody=false
```

## Ignored Local Evidence

Use only this ignored file for private Access boundary evidence:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-access-policy-boundary.local.json
```

Public-safe example:

```text
templates/SQX_Edge_Tester_Portal/cloudflare-access-policy-boundary.example.json
```

The local file must store booleans and labels only. It must not include hostnames, URLs, account IDs, Access app IDs, Access policy IDs, tester emails, tokens or keys.

## Gate Result

Without ignored local boundary evidence:

```text
NO_GO_ACCESS_POLICY_BOUNDARY_EVIDENCE_REQUIRED
```

With private Access app/policy boundary evidence:

```text
GO_ACCESS_APPLICATION_POLICY_BOUNDARY_VERIFIED_NO_APP_DEPLOY
```

The next phase may prepare one controlled real app deployment gate, but the real app is still not deployed by T10ak.

## Blocked Actions

- No real app deployment.
- No tester URL sharing.
- No tester account creation.
- No renewal emails.
- No public route/domain publication.
- No Git-connected Cloudflare deploy automation.

## Verification

Run from `templates/SQX_Edge_Tester_Portal`:

```powershell
npm run proof:cloudflare-access-policy-boundary
npm run proof:cloudflare-workers-dev-access
npm run proof:cloudflare-hostname-zone-selection
```

Expected:

```text
GO_ACCESS_APPLICATION_POLICY_BOUNDARY_VERIFIED_NO_APP_DEPLOY
GO_ACCESS_PROTECTED_WORKERS_DEV_SHELL_VERIFIED_NO_APP
GO_CLOUDFLARE_HOSTNAME_ZONE_READY_T10AK_ALLOWED
```

## Next Gate

```text
T10al_controlled_real_app_deploy_gate
```

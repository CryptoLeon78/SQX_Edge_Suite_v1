# T9c Vercel Deployment Protection Gate

## Objective

T9c turns the T9b rollback into a reproducible go/no-go gate before any new Vercel preview attempt.

This phase does not deploy, publish a URL, invite testers, send emails, connect a production database or change Vercel project protection settings. It only verifies the current project safety state and adds a script that blocks deploy retry unless protection is proven.

## Live Project State Checked

The linked Vercel project was inspected through the authenticated Vercel app and CLI context:

- Project name: `sqx-edge-tester-portal`.
- Framework: `nextjs`.
- Live deployment: false.
- Latest deployment: none.
- Domains: none.

This confirms the T9b rollback left no active deployment surface.

## Protection State

The available project read tools confirm deployment absence, but they do not expose the detailed `ssoProtection` or `passwordProtection` project fields needed for a full Deployment Protection verdict.

T9c result:

- Deployment Protection verdict: `NO_GO_PROTECTION_NOT_VERIFIED`.
- External deploy allowed: false.
- Required before retry: verify Vercel Authentication or Password Protection for preview deployments from dashboard/API.

Official Vercel behavior used by this gate:

- Standard Protection protects generated deployment URLs and previews, but not production domains.
- All Deployments protects every URL, including production domains, when plan/add-on supports it.
- Vercel Authentication can be managed on the project with `ssoProtection.deploymentType`.
- Password Protection can be managed on the project with `passwordProtection.deploymentType`.

## Added Audit Script

T9c adds:

```text
templates/SQX_Edge_Tester_Portal/scripts/vercel-protection-audit.mjs
```

Run it from the template root:

```powershell
npm run audit:vercel-protection
```

The script:

- requires the local Vercel project link in `.vercel/project.json`
- refuses to approve external deploys without `VERCEL_TOKEN`
- queries the Vercel project API when `VERCEL_TOKEN` exists
- accepts only `ssoProtection` or `passwordProtection`
- accepts deployment types `preview`, `prod_deployment_urls_and_all_previews` or `all`
- reports `GO_PROTECTION_VERIFIED` only when protection is present
- reports `NO_GO_PROTECTION_NOT_VERIFIED` otherwise

## Local Audit Result

Current local execution result:

```text
status = NO_GO_PROTECTION_NOT_VERIFIED
reason = VERCEL_TOKEN is not available to query project protection settings through the Vercel API
externalDeployAllowed = false
```

This is the desired safe state until protection can be proven.

## Required Manual/API Unblock

Before any new deploy attempt:

1. Open Vercel project settings for `sqx-edge-tester-portal`.
2. Go to Deployment Protection.
3. Enable Vercel Authentication or Password Protection for preview deployments at minimum.
4. Prefer Standard Protection for previews and generated deployment URLs; use All Deployments only when plan/add-on supports protecting production domains too.
5. Provide a private `VERCEL_TOKEN` locally, outside git, if API verification should be automated.
6. Run `npm run audit:vercel-protection`.
7. Continue only if the script returns `GO_PROTECTION_VERIFIED`.

## Security Boundary

- No raw tester emails are committed.
- No tester invite is sent.
- No renewal email is sent.
- No public/protected Vercel URL is committed.
- No production database is connected.
- `.vercel` remains ignored local state.
- Deployment retry is blocked until protection is verified.

## Verification

T9c is accepted when:

- this gate document exists
- `audit:vercel-protection` exists and returns a safe NO-GO without `VERCEL_TOKEN`
- static tests assert the T9c contract
- Next template typecheck passes
- full backend tests pass
- `git diff --check` passes

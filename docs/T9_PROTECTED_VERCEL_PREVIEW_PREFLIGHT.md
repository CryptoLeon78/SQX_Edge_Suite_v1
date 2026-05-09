# T9 Protected Vercel Preview Preflight

## Objective

T9 starts the protected Vercel preview staging step with explicit user approval for the external action. The first live preflight reached Vercel CLI authentication and stopped before deploy because the local token is invalid.

This is a controlled NO-GO for deployment, not a failed safety outcome. No preview URL was created, no tester account was created, no emails were sent and no production database was connected.

## Active Ownership

- Access/Security Gatekeeper: protected preview gates, kill switch, rate limit, watermark and no tester rollout.
- Security/Distribution: Vercel auth state, deployment protection, no public URL committed and no secrets in git.
- Backend/API: health and middleware hardening readiness.
- QA/Release: preflight script, static tests, typecheck, backend pytest and `git diff --check`.
- Architecture/Docs: roadmap/governance status and exact unblock instructions.

## External Action Attempted

Approved action:

- Prepare and attempt protected Vercel preview staging for `templates/SQX_Edge_Tester_Portal`.

Preflight command executed locally:

```powershell
npx --yes vercel whoami
```

Observed blocker:

```text
Error: The specified token is not valid. Use `vercel login` to generate a new token.
```

Result:

- Deployment status: `NO_GO_AUTH_BLOCKED`
- Preview URL: not created
- Tester invites: not sent
- Renewal emails: not sent
- Real tester emails: not used
- Secrets committed: no

## Added Preflight Script

T9 adds:

```text
templates/SQX_Edge_Tester_Portal/scripts/vercel-preview-preflight.mjs
```

Run it from the template root:

```powershell
npm run preflight:vercel-preview
```

The script validates:

- demo login, Pro entitlement and admin console flags remain disabled by default
- T8 kill switch and rate-limit env keys exist
- deployment-protection checklist exists
- middleware includes kill switch, rate-limit and security headers
- `vercel.json` remains a Next.js project with cron definitions
- `.vercel/project.json` is not committed into the public template

## Required Manual Unblock

Before reattempting deploy:

1. Run `npx vercel login` locally or configure a valid Vercel token outside git.
2. Link the private/staging Vercel project from the template root.
3. Verify Vercel Deployment Protection is enabled for preview deployments.
4. Keep preview URL out of public git docs.
5. Keep `T4_DEMO_LOGIN_ENABLED`, `T5_DEMO_TESTER_PRO_ENABLED` and `T7_DEMO_ADMIN_CONSOLE_ENABLED` disabled unless validating privately behind protection.
6. Do not invite testers or send renewal emails in T9.

## Exact Deploy Command After Unblock

From `templates/SQX_Edge_Tester_Portal`:

```powershell
npx vercel deploy --target=preview
```

Only after the preview is created and verified behind protection should the deployment URL be shared privately with the operator. It must not be committed to the public repository.

## Security Boundary

- No Vercel deploy was completed in this phase because authentication blocked safely.
- No tester account is created.
- No tester email list is committed.
- No renewal email is sent.
- No production database is connected.
- No preview URL is committed.
- No public/protected URL is published in repository docs.

## Verification

T9 preflight is accepted when:

- the invalid-token blocker is documented
- `preflight:vercel-preview` passes
- static tests include T9 contracts
- Next template typecheck passes
- full backend tests pass
- `git diff --check` passes

## Next Phase

T9b should authenticate Vercel, link the staging project if needed, verify Deployment Protection and run the preview deploy. This requires a valid local Vercel login/token at execution time.

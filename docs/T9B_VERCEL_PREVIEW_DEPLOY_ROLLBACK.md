# T9b Vercel Preview Deploy Rollback

## Objective

T9b authenticated Vercel and attempted the explicitly approved protected preview deploy for the tester portal. The CLI created a deployment, but Vercel treated it as `target = production` and attached production aliases. This violated the intended preview-only boundary, so the deployment was removed immediately.

This phase is accepted as a security-controlled rollback, not as a successful tester preview.

## External Actions Performed

- Authenticated Vercel CLI as the local Vercel user.
- Linked `templates/SQX_Edge_Tester_Portal` to project slug `sqx-edge-tester-portal`.
- Ran the local preflight script successfully.
- Attempted deploy with `vercel deploy --target=preview`.
- Observed Vercel report `target = production` and create production aliases.
- Removed the created deployment immediately with `vercel remove`.
- Verified the deployment was no longer inspectable and the public alias returned `404`.

## Current Vercel State

- Project exists: `sqx-edge-tester-portal`.
- Active deployment: none.
- Latest production URL: none.
- Tester invites: not sent.
- Renewal emails: not sent.
- Real tester emails: not committed.
- Production database: not connected.
- Public preview/prod URL in git: none.

## Why This Was Rolled Back

The project objective was protected preview staging, not production aliasing. Because the CLI deployment attached production aliases, the safest action was immediate removal before any tester workflow continued.

## Guardrail Added

`scripts/vercel-preview-preflight.mjs` now allows local `.vercel/project.json` only when `.vercel` is ignored and changes its deploy recommendation to manual/dashboard/API preview after Deployment Protection is verified.

The project link files remain local machine state and must not be committed.

## Tester Email Boundary

The user provided five tester emails for future phases. They are treated as private tester PII:

- Do not commit raw emails.
- Do not place them in public docs.
- Do not send invites in T9b.
- Do not include them in Vercel environment variables.
- Use only private, ignored storage or a future private database when T10/T11 explicitly needs tester onboarding.

## Required Next Step

T9c should verify Deployment Protection from the Vercel dashboard/API before any new deploy attempt. A safe next deploy must prove one of:

- the deployment is protected before any URL is shared, or
- the deployment is not externally reachable without authenticated Vercel access.

No tester invite or email send should occur until T10/T11 after a protected preview is verified.

## Verification

T9b is accepted when:

- Vercel deploy rollback is documented.
- The public alias check returned `404` after removal.
- The Vercel project has no active deployment URL.
- `.vercel` is ignored and local project state is not staged.
- Preflight passes with local `.vercel/project.json` present.
- Static tests, typecheck and backend tests pass.

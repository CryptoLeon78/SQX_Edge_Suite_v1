# T9f Preview Path Proof Gate

## Objective

T9f replaces the unsafe local Vercel CLI deploy retry path with a reproducible proof gate for a Git/PR-based preview route.

The phase does not deploy, does not create repositories, does not invite testers, does not send emails and does not publish or commit any Vercel URL.

## Why This Exists

T9e proved that running a local CLI deploy from the linked tester portal project can still produce a production target and production alias even when the command is run without `--prod`.

Because the tester portal is security-sensitive, the next rollout path must be able to prove these properties before any URL is shared:

- Vercel Authentication or Password Protection is enabled.
- The Vercel project is connected to Git.
- The intended preview branch is not the Vercel production branch.
- The path is driven by Git/PR preview mechanics, not by the unsafe local CLI deploy route.
- The proof script never prints tokens, raw repository URLs, raw tester emails or deployment URLs.

## New Local Gate

Template script:

```powershell
npm run proof:vercel-preview-path
```

Implementation:

- `templates/SQX_Edge_Tester_Portal/scripts/vercel-preview-path-proof.mjs`
- package script: `proof:vercel-preview-path`

The script reads local `.vercel/project.json`, requires `VERCEL_TOKEN` only from the environment, queries the Vercel Project API, verifies deployment protection, verifies Git integration and compares `T9F_PREVIEW_BRANCH` against the Vercel production branch.

Default preview branch:

```text
tester-preview
```

Blocked branch names:

```text
main, master, production, prod
```

## Expected Statuses

- `GO_GIT_PREVIEW_PATH_READY`: protection is verified, Git integration exists and the preview branch is not production.
- `NO_GO_PROJECT_NOT_LINKED`: local Vercel project link is missing.
- `NO_GO_TOKEN_NOT_AVAILABLE`: local token was not provided.
- `NO_GO_PREVIEW_BRANCH_RESERVED`: preview branch name is production-like.
- `NO_GO_API_PROJECT_AUDIT_FAILED`: Vercel API query failed.
- `NO_GO_PROTECTION_NOT_VERIFIED`: deployment protection is not proven.
- `NO_GO_GIT_PREVIEW_NOT_CONFIGURED`: the Vercel project is not Git-connected.
- `NO_GO_PREVIEW_BRANCH_MATCHES_PRODUCTION`: intended preview branch matches production.

## Current Result

T9f is accepted as a safe proof gate, not as a tester rollout.

The safe operational expectation before T9g is:

```text
NO_GO_GIT_PREVIEW_NOT_CONFIGURED
```

That result means the project may be protected, but a private Git/PR preview path has not yet been connected and proven.

## Required Next Step

T9g should connect or prepare a private Git preview source before any tester URL is shared:

1. Create or connect a private tester portal repository only after explicit approval.
2. Keep the Vercel production branch separate from the intended preview branch.
3. Rerun `npm run proof:vercel-preview-path` until it returns `GO_GIT_PREVIEW_PATH_READY`.
4. Only then create a Git/PR preview and inspect the deployment target before sharing any URL.

Contributor access is not required for local work right now. If later automation needs PRs, CI or releases, use a least-privilege GitHub bot/user or collaborator role rather than sharing personal credentials.

## Security Boundary

- No Vercel deploy is executed.
- No active deployment is created.
- No tester invite is sent.
- No renewal email is sent.
- No production database is connected.
- No raw tester emails are committed.
- No Vercel token is committed.
- No public/protected URL is committed.

## Verification

T9f is accepted when:

- this document exists
- `proof:vercel-preview-path` exists in the tester portal package
- the proof script blocks unsafe/no-Git states
- README, governance and roadmap point to T9g
- static tests assert the T9f contract
- full backend tests pass
- `git diff --check` passes

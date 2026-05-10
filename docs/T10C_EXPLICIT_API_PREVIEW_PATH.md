# T10c Explicit API Preview Path

## Objective

T10c defines a no-deploy proof for an explicit Vercel API preview path before any tester URL is created or shared.

This phase is accepted as a proof and guardrail, not as a live tester preview.

## Finding

The Vercel Project API reports the tester project Git integration with `productionBranch = main`.

That means the dashboard/API configuration is nominally safe, but T10 and T10b proved the Git-triggered deployment path can still report `target = production` from `tester-preview`.

## Implementation

- Added `scripts/vercel-explicit-preview-proof.mjs`.
- Added `npm run proof:vercel-explicit-preview`.
- The proof inspects the Vercel project through API.
- The proof accepts `tester-preview` only when it is not the production branch.
- The proof builds a draft deployment request with `target: "preview"`.
- The proof does not call the deployment endpoint.
- The proof does not create, fetch, persist or share a Vercel URL.

## Expected GO Status

```text
GO_EXPLICIT_API_PREVIEW_PATH_READY
```

The GO status means T10d may execute the explicit API preview path under inspection.

It does not mean testers can be invited yet.

## Required Next Step

T10d may execute one explicit API preview deployment only if all of the following hold:

- `proof:vercel-explicit-preview` returns `GO_EXPLICIT_API_PREVIEW_PATH_READY`.
- The request uses `target: "preview"`.
- The resulting deployment is inspected before any URL is shared.
- If Vercel reports `target = production`, the deployment is removed immediately.
- If Vercel reports `target = preview`, Deployment Protection and tester auth must still be verified before handoff.

## Security Boundary

- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No Vercel URL was committed.
- No bypass/share URL was created.
- No deployment was created in T10c.
- The private tester portal repo was not pushed in T10c to avoid another Git-triggered production-target build.

## Verification

T10c is accepted when:

- this document exists
- the explicit preview proof script exists
- `package.json` exposes `proof:vercel-explicit-preview`
- the proof contains `target: "preview"`
- the proof records `externalDeployAttempted: false`
- static tests assert the proof contract
- backend tests pass
- `git diff --check` passes

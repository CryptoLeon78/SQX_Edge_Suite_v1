# T10f Separated Preview Project

## Objective

T10f creates a separate Vercel project for tester preview work before any tester URL is shared.

This phase is accepted as a safe separation step, not as a deployment or tester rollout.

## External Action Performed

- Created a new Vercel project named `sqx-edge-tester-preview`.
- Did not deploy the tester portal.
- Did not link or publish a tester URL.
- Did not add domains.
- Did not create tester accounts.
- Kept the previous project `sqx-edge-tester-portal` as the legacy unsafe project until a later cleanup decision.

## Verified Project State

```text
GO_PREVIEW_PROJECT_SEPARATED
```

Observed preview-project state:

- Project name: `sqx-edge-tester-preview`.
- Legacy project name: `sqx-edge-tester-portal`.
- Project separation: preview project and legacy project are different projects.
- Live deployment: false.
- Latest deployment: none.
- Domains: none.
- Git connection: not linked yet.
- Framework: not configured yet.

## Why This Matters

T10, T10d and T10e showed that the legacy project can convert Git, explicit API and omitted-target API attempts into unsafe `target = production` deployments.

T10f stops retrying deployments on that project and creates a clean preview-only surface for the next controlled setup phase.

## Required Next Step

T10g must link the private tester portal repository to `sqx-edge-tester-preview`, verify production branch and deployment protection settings, and keep the result as no-deploy proof before any URL is created or shared.

Do not deploy from the separated project until T10g proves:

1. the linked Git source is the private tester portal repository
2. the production branch is not `tester-preview`
3. Vercel Deployment Protection is still enabled or explicitly verified
4. `tester-preview` remains a non-production branch
5. no production aliases or buyer-facing domains exist

## Security Boundary

- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No Vercel URL was committed.
- No bypass/share URL was created.
- No active deployment exists.
- No tester URL was shared.

## Verification

T10f is accepted when:

- this document exists
- `scripts/vercel-preview-project-separation-proof.mjs` exists
- `package.json` exposes `proof:vercel-preview-project-separation`
- the proof returns `GO_PREVIEW_PROJECT_SEPARATED`
- the separated project has no latest deployment
- the separated project has no domains
- docs and roadmap point to T10g as the next setup phase
- static tests assert the separation contract
- backend tests pass
- `git diff --check` passes

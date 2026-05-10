# T10g Linked Preview Project Proof

## Objective

T10g links the private tester portal repository to the separated Vercel preview project and proves the resulting configuration without creating a deployment or sharing a URL.

This phase is accepted as a no-deploy Git-link proof, not as a tester rollout.

## External Action Performed

- Linked the private tester portal working tree locally to `sqx-edge-tester-preview`.
- Connected the GitHub repository `CryptoLeon78/SQX_Edge_Tester_Portal` to the separated Vercel project.
- Did not run `vercel deploy`.
- Did not push a post-connect trigger commit to the private tester portal repo.
- Did not create a deployment.
- Did not add domains.
- Did not share a tester URL.

## Verified Project State

```text
GO_LINKED_PREVIEW_PROJECT_READY
```

Observed preview-project state:

- Project name: `sqx-edge-tester-preview`.
- Git provider: GitHub.
- Git repository owner: `CryptoLeon78`.
- Git repository: private tester portal repository.
- Production branch: `main`.
- Intended preview branch: `tester-preview`.
- Preview branch is production: false.
- Deployment Protection: Vercel SSO protection is enabled.
- Live deployment: false.
- Latest deployment: none.
- Domains: none.

## Required Next Step

T10h must execute exactly one protected preview deployment from the separated project, inspect the deployment target immediately, and remove it immediately if the target is not preview or if any production alias appears.

Do not share a tester URL until T10h proves:

1. deployment target is preview
2. no production aliases exist
3. Deployment Protection is active
4. no tester accounts or emails are involved
5. the URL is recorded only in private/local evidence if needed

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

T10g is accepted when:

- this document exists
- `scripts/vercel-linked-preview-project-proof.mjs` exists
- `package.json` exposes `proof:vercel-linked-preview-project`
- the proof returns `GO_LINKED_PREVIEW_PROJECT_READY`
- the separated project is linked to the private tester portal repository
- production branch resolves to `main`
- `tester-preview` is not production
- Vercel Deployment Protection is enabled
- the separated project has no latest deployment
- the separated project has no domains
- docs and roadmap point to T10h as the next deployment inspection phase
- static tests assert the linked-preview contract
- backend tests pass
- `git diff --check` passes

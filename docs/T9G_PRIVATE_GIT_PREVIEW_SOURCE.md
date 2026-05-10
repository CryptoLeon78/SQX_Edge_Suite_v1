# T9g Private Git Preview Source

## Objective

T9g connects a private Git source for the Vercel tester portal so future previews can be created through branch/PR mechanics instead of the unsafe local CLI deploy route found in T9e.

This phase is a controlled infrastructure connection, not a tester rollout.

## External Actions Performed

- Created private GitHub repository `CryptoLeon78/SQX_Edge_Tester_Portal`.
- Copied the public-safe tester portal template into a separate local working copy.
- Committed the private portal baseline.
- Pushed `main` and `tester-preview` before connecting Vercel, so the connection itself did not require a post-connect branch push.
- Connected the existing Vercel project `sqx-edge-tester-portal` to the private GitHub repository with `vercel git connect`.

No manual Vercel deploy command was run.

## Verified State

- GitHub repository privacy: private.
- GitHub default branch: `main`.
- Preview branch prepared: `tester-preview`.
- Vercel protection: `GO_PROTECTION_VERIFIED`.
- Vercel Git source: linked through the Vercel Project API `link` object.
- Vercel production branch: `main`.
- Intended preview branch: `tester-preview`.
- Preview proof gate: `GO_GIT_PREVIEW_PATH_READY`.
- Latest deployment after the connection: none.
- Custom domains after the connection: zero.

## Gate Update

T9f originally checked `project.gitRepository`. Vercel CLI 53.3.1 connected the GitHub repository successfully, but the Project API exposed that connection as `project.link`.

The proof script now accepts either shape:

- `project.gitRepository`
- `project.link`

It still blocks if the preview branch is production-like or matches the Vercel production branch.

## Security Boundary

- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No Vercel token was committed.
- No `.env` or `.env.local` file was copied to the private repo.
- No public/protected Vercel URL was committed.
- No preview URL was shared.
- No post-connect push was made to trigger an automatic Vercel deployment.

## Required Next Step

T10 should run one internal tester pilot before inviting external testers.

T10 must be explicit about the external action it performs. The expected safe route is:

1. Trigger a Git preview from `tester-preview` only.
2. Inspect the generated Vercel deployment target before sharing anything.
3. Confirm Vercel Authentication still protects the deployment.
4. Use one internal operator/tester first.
5. Do not invite the external tester list until the internal pilot is accepted.

## Verification

T9g is accepted when:

- this document exists
- governance and roadmap point to T10
- the private repo is verified as private
- the proof gate returns `GO_GIT_PREVIEW_PATH_READY`
- the project has no active/latest deployment after connection
- no raw tester emails or secrets are committed
- static tests assert the T9g contract
- full backend tests pass
- `git diff --check` passes

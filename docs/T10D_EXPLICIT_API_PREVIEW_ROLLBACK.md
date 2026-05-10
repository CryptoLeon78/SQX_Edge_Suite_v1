# T10d Explicit API Preview Rollback

## Objective

T10d executed one explicit Vercel API preview deployment attempt and inspected the deployment target before any tester URL was shared.

This phase is accepted as a rollback, not as a successful tester preview.

## External Action Performed

- Created one Vercel deployment through the REST API.
- Sent an explicit request with `target: "preview"`.
- Used the private `tester-preview` Git source.
- Inspected the created deployment immediately.
- Removed the deployment immediately after Vercel reported `target = production`.

## Result

```text
NO_GO_TARGET_NOT_PREVIEW_ROLLED_BACK
```

Observed deployment state:

- The deployment was created only for inspection.
- The API returned `target = production`.
- The deployment was still initializing when the unsafe target was detected.
- The deployment was removed immediately.
- No tester URL was shared.
- No Vercel URL was committed.
- The Vercel project now reports no latest deployment.
- The Vercel project now reports no domains.

## Interpretation

T10, T10b and T10d now prove the problem is not limited to CLI deployment or automatic Git push behavior.

Even the explicit API path with `target: "preview"` can return `target = production` for this Vercel project.

The safe next step is not another deployment attempt.

## Required Next Step

T10e must fix or recreate the Vercel preview deployment path before any tester URL is shared.

Acceptable T10e routes:

1. Recreate the Vercel project from the private Git repository with `main` as production branch, then prove preview behavior before deploying.
2. Open/check Vercel dashboard branch tracking and environment settings manually, then re-run only a no-deploy proof.
3. Create a separate non-production Vercel project dedicated to tester preview, with no production aliases and no buyer-facing domains.

Do not push another trigger commit and do not create another deployment on the current project until T10e resolves the target mismatch.

## Security Boundary

- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No Vercel URL was committed.
- No bypass/share URL was created.
- No active deployment remains.
- No tester URL was shared.

## Verification

T10d is accepted when:

- this document exists
- the deployment attempt result is recorded as `NO_GO_TARGET_NOT_PREVIEW_ROLLED_BACK`
- the unsafe deployment was removed
- the Vercel project has no latest deployment
- the Vercel project has no domains
- docs and roadmap point to T10e rather than another deploy attempt
- static tests assert the rollback contract
- backend tests pass
- `git diff --check` passes

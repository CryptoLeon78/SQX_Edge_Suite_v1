# T10 Internal Preview Target Rollback

## Objective

T10 attempted the first internal tester pilot by triggering a Git-based deployment from the private `tester-preview` branch.

The phase is accepted as a safety rollback, not as a successful internal pilot.

## External Actions Performed

- Created a private-only marker commit in `CryptoLeon78/SQX_Edge_Tester_Portal` on `tester-preview`.
- Pushed `tester-preview` to trigger the first Git-based Vercel deployment.
- Inspected the deployment before sharing any URL.
- Removed the deployment immediately after Vercel reported a production target.

No tester invite was created, no email was sent and no tester URL was shared.

## Finding

Vercel created a Git deployment from `tester-preview`, but the deployment metadata reported:

```text
target = production
source = git
githubCommitRef = tester-preview
githubRepoVisibility = private
```

This violates the T10 requirement that the internal pilot must be a preview/non-production deployment.

## Rollback Result

Rollback verification:

- The deployment is no longer inspectable.
- The Vercel project reports no latest deployment.
- The Vercel project reports no domains.
- The public project alias returns `404`.
- No Vercel URL is committed.
- No raw tester emails are committed.
- No tester accounts are created.
- No renewal emails are sent.
- No production database is connected.

## Required Next Step

T10b must fix the Vercel preview target mapping before any tester URL is shared.

The next attempt should not push another change to `tester-preview` until one of these is true:

1. Vercel Git settings prove non-production branches create preview targets.
2. A safe API deployment path can prove `target = preview` before aliasing.
3. Automatic Git deployments are intentionally paused or constrained while the mapping is corrected.

## Security Boundary

- The private repo remains private.
- The trigger commit contains no secrets and no tester data.
- The deployment URL was not shared.
- No bypass/share link was created.
- No access token was committed.
- The local token used by the Node audit script is stale; Vercel CLI and the Vercel connector were used only for inspection/removal.

## Verification

T10 is accepted when:

- this rollback document exists
- governance and roadmap point to T10b
- the Vercel project has no active/latest deployment
- static tests assert the rollback contract
- full backend tests pass
- `git diff --check` passes

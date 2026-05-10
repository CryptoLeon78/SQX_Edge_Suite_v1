# T10b Vercel Target Guard

## Objective

T10b adds a build-time guard so the tester portal cannot publish a production-target deployment from a non-production branch while the Vercel Git target mapping remains incorrect.

This phase is accepted as a containment fix, not as a successful tester preview.

## External Actions Performed

- Added `scripts/vercel-target-guard.mjs` to the public-safe tester portal template.
- Added the same guard to the private tester portal repository.
- Added `prebuild` so Vercel runs the guard before `next build`.
- Pushed the private `tester-preview` branch to verify the guard under real Vercel Git conditions.
- Removed the resulting failed deployment after verification, keeping the project without active deployment or domains.

## Guard Behavior

Allowed:

- local builds
- Vercel preview builds from `tester-preview`
- Vercel production builds from `main`

Blocked:

```text
VERCEL_ENV = production
VERCEL_GIT_COMMIT_REF = tester-preview
```

Blocked status:

```text
NO_GO_PRODUCTION_TARGET_FROM_NON_PRODUCTION_BRANCH
```

## Verification Result

The controlled private push proved the guard works:

- Vercel still attempted `target = production` from `tester-preview`.
- The guard ran during `prebuild`.
- The guard exited with code `43`.
- The deployment ended in `ERROR`, not `READY`.
- The failed deployment was removed.
- The project now reports no latest deployment.
- The project now reports no domains.

## Required Next Step

T10c should resolve the underlying Vercel mapping before trying to share a tester URL.

Acceptable next routes:

1. Correct Vercel project Git settings so `tester-preview` creates `target = preview`.
2. Disable or constrain automatic Git deployment while the mapping is unresolved.
3. Use an explicit API deployment path only if it can prove `target = preview` before any alias or URL handoff.

Do not push another trigger commit to `tester-preview` unless the expected outcome is intentionally a blocked `ERROR` deployment or the mapping has been corrected.

## Security Boundary

- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No Vercel URL was committed.
- No bypass/share URL was created.
- No production-ready deployment remains.

## Verification

T10b is accepted when:

- this document exists
- the guard is present in the template and private repo
- package `prebuild` runs the guard
- local guard tests cover local, preview, production/main and production/tester-preview
- Vercel build logs show the guard blocked the unsafe production target
- the failed deployment is removed
- the Vercel project has no active/latest deployment
- static tests assert the guard contract
- full backend tests pass
- `git diff --check` passes

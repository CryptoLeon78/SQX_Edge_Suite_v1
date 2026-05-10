# T10j CLI Default Preview Command Rollback

## Objective

T10j executed the single approved CLI default preview command shape from T10i and inspected whether a deployment was created.

This phase is accepted as a command rollback, not as a tester rollout.

## External Action Performed

- Ran one Vercel CLI deployment command from the private tester portal working tree.
- Used no `--prod`.
- Used no `--target`.
- Included `--skip-domain` as approved by T10i.
- Captured raw output only in local ignored backup evidence.
- Did not share or commit any Vercel URL.

## Result

```text
NO_GO_CLI_DEFAULT_PREVIEW_COMMAND_INVALID
```

Observed command state:

- Vercel rejected the command before creating a deployment.
- Deployment id: missing.
- Deployment target: not available.
- Deployment ready state: not available.
- Rollback was not needed because no deployment existed.
- No tester URL was created.
- No tester URL was shared.
- No Vercel URL was committed.

Observed CLI error:

```text
The --skip-domain option can only be used with production deployments.
```

## Interpretation

T10i correctly removed `--prod` and `--target`, but `--skip-domain` is not valid for preview deployments.

The separated project remains clean. The next attempt must use the Vercel CLI default preview route without `--skip-domain`.

## Required Next Step

T10k may execute exactly one CLI default preview deployment with this command shape:

```text
vercel deploy --force --yes --format json
```

Mandatory absences:

- No `--prod`.
- No `--target`.
- No `--skip-domain`.

T10k must:

1. inspect the resulting deployment target immediately
2. remove the deployment immediately if target is not preview
3. remove the deployment immediately if any production alias appears
4. avoid sharing or committing any Vercel URL
5. record only redacted public evidence

Do not push a trigger commit to the private tester portal repo for this test.

## Security Boundary

- No deployment was created.
- No tester URL was created or shared.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.
- No Vercel URL was committed.
- No bypass/share URL was created.

## Verification

T10j is accepted when:

- this document exists
- `scripts/vercel-cli-default-preview-command-rollback-proof.mjs` exists
- `package.json` exposes `proof:vercel-cli-default-preview-command-rollback`
- the proof returns `GO_CLI_DEFAULT_PREVIEW_COMMAND_ROLLBACK_CLEAN`
- docs and roadmap point to T10k as the corrected deployment inspection phase
- static tests assert the command rollback contract
- backend tests pass
- `git diff --check` passes

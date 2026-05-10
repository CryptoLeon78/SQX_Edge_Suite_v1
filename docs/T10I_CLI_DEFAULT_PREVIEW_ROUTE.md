# T10i CLI Default Preview Route Proof

## Objective

T10i corrects the next Vercel preview route without creating a deployment.

Official Vercel deployment guidance distinguishes the default CLI preview route from production deployment: `vercel deploy` creates a preview deployment, while production requires `--prod`. T10i therefore replaces the failed `--target=preview` route with the default CLI preview route and keeps the deployment action for a separate inspection phase.

This phase is accepted as a no-deploy route proof, not as a tester rollout.

## Route Decision

Approved next attempt shape:

```text
vercel deploy --force --yes --format json --skip-domain
```

Mandatory absences:

- No `--prod`.
- No `--target`.
- No production alias.
- No tester URL shared before target inspection.

Mandatory immediate checks for T10j:

- Created deployment must report `target = preview`.
- Created deployment must not receive a production alias.
- Deployment Protection must remain active.
- Any mismatch must trigger immediate removal before any tester URL is shared.

## Proof Result

```text
GO_CLI_DEFAULT_PREVIEW_ROUTE_READY
```

The proof verifies:

- local working tree is linked to `sqx-edge-tester-preview`
- separated project has no live deployment
- separated project has no latest deployment
- separated project has no domains
- Git source remains linked
- production branch remains `main`
- intended preview branch remains `tester-preview`
- Deployment Protection is still verified
- approved command shape omits `--prod` and `--target`
- no deployment is created by this proof

## Interpretation

T10h showed that `--target=preview` is not acceptable for this account/project because Vercel returned `target = production`.

T10i does not prove that the next deployment will be preview. It proves that the next attempt must use the official CLI default preview route, and that the attempt must be inspected and rolled back immediately if the target is not preview.

## Required Next Step

T10j may execute exactly one CLI default preview deployment from the private tester portal working tree.

T10j must:

1. run the approved command shape without `--prod` and without `--target`
2. inspect the resulting deployment target immediately
3. remove the deployment immediately if target is not preview
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

T10i is accepted when:

- this document exists
- `scripts/vercel-cli-default-preview-route-proof.mjs` exists
- `package.json` exposes `proof:vercel-cli-default-preview-route`
- the proof returns `GO_CLI_DEFAULT_PREVIEW_ROUTE_READY`
- docs and roadmap point to T10j as the single deployment inspection phase
- static tests assert the route contract
- backend tests pass
- `git diff --check` passes

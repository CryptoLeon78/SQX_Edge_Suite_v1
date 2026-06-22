# T10ai Cloudflare Provider-Project Preflight

## Objective

T10ai prepares the Cloudflare provider-project preflight for the tester portal: it confirms the selected runtime, proposes a project name and branch strategy, and gates all provider creation, deployment, and tester URL publication behind explicit approval.

This phase remains local-only. It does not create a Cloudflare project, does not connect GitHub to Cloudflare, does not create a Cloudflare Access application or policy, does not deploy and does not publish a tester URL.

## Why This Phase Exists

T10ah confirmed that the tester portal build works with the Cloudflare Workers/OpenNext runtime and that the `middleware.ts` convention is the correct request gate. Before any provider project can be created, a structured preflight must capture:

- the agreed runtime and project name proposal
- the branch mapping (production: `main`, tester: `tester-preview`)
- the Access policy requirement before any tester URL is shared
- the demo/CI worker that already exists for build verification
- the confirmed absence of all tester-rollout externalizations

## Changes

- `scripts/cloudflare-provider-project-preflight-proof.mjs` was added as the T10ai preflight contract.
- `package.json` exposes `proof:cloudflare-provider-project-preflight`.
- No Cloudflare project was created.
- No Cloudflare deployment was created.
- No Cloudflare Access application or policy was created for the tester rollout.
- No GitHub repository was connected to Cloudflare for the tester rollout.
- No tester URL was shared.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.

## Result

```text
GO_CLOUDFLARE_PROVIDER_PROJECT_PREFLIGHT_READY_NO_DEPLOY
```

## Decisions Captured

| Field | Value |
| --- | --- |
| `selectedRuntime` | `cloudflare_workers_opennext_nextjs_runtime` |
| `providerProjectNameProposal` | `sqx-edge-tester-portal-preview` |
| `productionBranch` | `main` |
| `testerBranch` | `tester-preview` |
| `accessPolicyRequiredBeforeTesterUrl` | `true` |
| `buildPreviewWorkerExistsForCiVerification` | `true` |
| `demoAccessApplicationAlreadyLiveOnTradingAccount` | `true` |

## Security Boundary

- No Cloudflare project was created.
- No Cloudflare deployment was created.
- No Cloudflare Access application or policy was created.
- No GitHub repository was connected to Cloudflare.
- No Cloudflare token or account ID was committed.
- No tester URL was shared.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.

## Prohibited Until Rollout Gate

The following externalizations are prohibited until the explicit rollout approval gate is passed:

- Creating or linking the tester rollout Cloudflare project
- Creating a Cloudflare deployment for the tester rollout
- Publishing a tester URL
- Creating tester accounts
- Committing tester emails
- Sending renewal emails
- Connecting the production database

## Next Gate

```text
create_or_link_tester_rollout_provider_project_only_after_explicit_approval
```

The tester rollout project must only be created or linked after the user provides explicit approval for that exact external action, as required by G3 risk level 3.

## Verification

T10ai is accepted when:

- this document exists
- `scripts/cloudflare-provider-project-preflight-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-provider-project-preflight`
- the proof returns `GO_CLOUDFLARE_PROVIDER_PROJECT_PREFLIGHT_READY_NO_DEPLOY` and exits 0
- `wrangler.jsonc` and `open-next.config.ts` are present
- all tester externalizations remain false
- typecheck passes
- no Cloudflare project, deployment, Access policy, tester URL, tester account, tester email or production database state is introduced
- sensitive scan finds no tester emails, secrets, provider tokens, deployment URLs or account IDs in touched public files
- `git diff --check` passes

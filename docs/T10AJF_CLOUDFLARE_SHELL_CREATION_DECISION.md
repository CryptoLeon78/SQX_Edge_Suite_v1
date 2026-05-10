# T10ajf Cloudflare Shell Creation Decision

## Objective

T10ajf decides whether SQX can create a Cloudflare Workers shell without deployment or whether any real shell creation must be treated as an upload/deploy-class external action requiring explicit approval.

No provider mutation was performed in this phase.

## Official Sources Checked

- Cloudflare Workers Versions and Deployments: https://developers.cloudflare.com/workers/configuration/versions-and-deployments/
- Cloudflare Workers Gradual Deployments: https://developers.cloudflare.com/workers/configuration/versions-and-deployments/gradual-deployments/
- Cloudflare Workers Preview URLs: https://developers.cloudflare.com/workers/configuration/previews/
- Wrangler Workers commands: https://developers.cloudflare.com/workers/wrangler/commands/workers/
- Workers Builds configuration: https://developers.cloudflare.com/workers/ci-cd/builds/configuration/

## Findings

Cloudflare separates Worker versions from deployments:

- `wrangler deploy` uploads and immediately deploys the Worker to traffic.
- `wrangler versions upload` uploads a new Worker version without immediately deploying it to production traffic.
- Cloudflare explicitly documents a first-upload limit: a new Workers project must be created first with C3 or `wrangler deploy`; using `wrangler versions upload` for the first upload will fail.
- Cloudflare preview documentation says version upload can return preview URLs.
- Workers Builds use `wrangler versions upload` as a preview deploy command.
- T10aje read-only checks confirmed `sqx-edge-tester-portal-preview` does not currently exist.

## Decision

```text
NO_GO_NO_INVISIBLE_CLOUDFLARE_SHELL_PATH_ACCEPTED
```

There is no accepted path to create a useful Cloudflare Worker shell that is both:

- real in the provider, and
- guaranteed to create no uploaded version, deployment-class artifact, preview URL or serving surface.

Therefore, the next phase must not silently create a Worker. It must prepare an exact approval gate for one controlled external action.

## Recommended Next Path

```text
T10ajg_first_worker_deploy_approval_gate
```

T10ajg should prepare the exact command, expected output, rollback/cleanup criteria and post-checks for the first Worker creation action. It must not run the deployment until Ivan explicitly approves that exact action.

Candidate route to evaluate in T10ajg:

```text
npm run cf:build
npm exec --yes -- wrangler deploy --name sqx-edge-tester-portal-preview
```

This is not approved yet. It may create a Worker, deployment, version and serving surface. Any resulting URL must remain private and unshared, and T10ajg must define immediate read-only inspection plus cleanup/rollback expectations before any later execution phase runs it.

## T10ak Status

T10ak remains blocked. Cloudflare Access application/policy work can only start after a real Worker shell exists and is verified.

## Security Boundary Preserved

- No Cloudflare project was created.
- No Cloudflare deployment was created.
- No Cloudflare version was uploaded.
- No Cloudflare Access application was created.
- No Cloudflare Access policy was created.
- No GitHub repository was connected to Cloudflare.
- No Cloudflare token or account ID was committed.
- No tester URL was published.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.

## Verification

T10ajf is accepted when:

- this document exists
- `scripts/cloudflare-shell-creation-decision-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-shell-creation-decision`
- the proof returns `NO_GO_NO_INVISIBLE_CLOUDFLARE_SHELL_PATH_ACCEPTED`
- no deploy or upload script is added
- no provider token, account ID, tester email or tester URL appears in tracked files
- static tests and full pytest pass
- `git diff --check` passes

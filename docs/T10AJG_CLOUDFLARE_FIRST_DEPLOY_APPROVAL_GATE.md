# T10ajg Cloudflare First Deploy Approval Gate

## Objective

T10ajg prepares the exact approval gate for the first Cloudflare Worker deploy/shell creation.

No provider mutation was performed in this phase.

## Official Sources Checked

- Cloudflare Workers Versions and Deployments: https://developers.cloudflare.com/workers/configuration/versions-and-deployments/
- Cloudflare Workers Preview URLs: https://developers.cloudflare.com/workers/configuration/previews/
- Wrangler commands: https://developers.cloudflare.com/workers/wrangler/commands/

## Source Findings

- Cloudflare documents that the first upload of a new Worker must use C3 or `wrangler deploy`; `wrangler versions upload` fails for the first upload.
- `wrangler deploy` creates a Worker version and deploys it to traffic.
- Preview URLs can be public when enabled, and Cloudflare Access can be used to protect preview URLs.
- Wrangler exposes read-only inspection commands for deployments and versions, and exposes a Worker delete command with `--force` for cleanup.

## Gate Result

```text
GO_CLOUDFLARE_FIRST_DEPLOY_APPROVAL_GATE_READY_NO_PROVIDER_ACTION
```

This is a preparation gate only. It does not authorize execution by itself.

## Exact Manual Approval Required For T10ajh

T10ajh may run the first deploy only if Ivan explicitly approves this exact action:

```text
Autorizo T10ajh: ejecutar exactamente `npm exec --yes -- wrangler deploy --name sqx-edge-tester-portal-preview` desde `templates/SQX_Edge_Tester_Portal` despues de `npm run cf:build`, sin compartir URL tester y con inspeccion/cleanup inmediato si aparece una superficie publica no aceptada.
```

Any materially different command, Worker name, route, domain, Access policy, Git integration, tester account or URL-sharing action requires a new approval.

## Exact Command Set For T10ajh

Local pre-checks:

```powershell
cd templates\SQX_Edge_Tester_Portal
npm run proof:cloudflare-first-deploy-approval-gate
npm exec --yes -- wrangler whoami
npm exec --yes -- wrangler deployments list --name sqx-edge-tester-portal-preview --json
npm exec --yes -- wrangler versions list --name sqx-edge-tester-portal-preview --json
npm exec --yes -- wrangler secret list --name sqx-edge-tester-portal-preview --format json
```

Local build:

```powershell
npm run cf:build
```

First deploy, only after exact approval:

```powershell
npm exec --yes -- wrangler deploy --name sqx-edge-tester-portal-preview
```

Immediate post-checks:

```powershell
npm exec --yes -- wrangler deployments list --name sqx-edge-tester-portal-preview --json
npm exec --yes -- wrangler versions list --name sqx-edge-tester-portal-preview --json
npm exec --yes -- wrangler secret list --name sqx-edge-tester-portal-preview --format json
```

Emergency cleanup candidate if the first deploy creates an unsafe or unprotectable surface:

```powershell
npm exec --yes -- wrangler delete sqx-edge-tester-portal-preview --force
```

Cleanup is also an external destructive provider action. It is only allowed inside T10ajh if the just-created Worker must be removed immediately to prevent an unsafe tester surface. If anything is ambiguous, stop and ask Ivan.

## GO Criteria Before Running The Deploy

- Wrangler is authenticated to the intended Cloudflare account.
- T10aje still indicates the Worker does not already exist, or T10ajh records fresh read-only evidence before proceeding.
- `npm run proof:cloudflare-first-deploy-approval-gate` passes.
- `npm run cf:build` succeeds locally.
- No deploy script has been added to `package.json`.
- Ivan provides the exact approval phrase above.
- No tester URL is shared, copied into docs, committed or sent to testers.

## NO-GO Criteria

- Cloudflare account identity is unclear.
- Local build fails.
- The deploy command differs from the exact approved command.
- A custom domain, route, Git integration, Access policy, tester account, email or URL publication is requested in the same step.
- A provider token, account ID, tester email or URL would need to be committed.
- Any post-deploy output suggests a public surface cannot be inspected or cleaned up immediately.

## T10ak Status

T10ak remains blocked. Cloudflare Access application/policy work can only start after T10ajh verifies the real Worker shell and records that no tester URL was shared.

## Manual Help Ivan May Need To Provide

If T10ajh runs into an interactive Cloudflare prompt, Ivan only needs to:

1. Confirm the browser/login prompt belongs to Cloudflare.
2. Keep any generated URL private.
3. Tell Codex whether the deploy completed, failed, or needs cleanup.

## Security Boundary Preserved

- No Cloudflare Worker was created.
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

T10ajg is accepted when:

- this document exists
- `scripts/cloudflare-first-deploy-approval-gate-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-first-deploy-approval-gate`
- the proof returns `GO_CLOUDFLARE_FIRST_DEPLOY_APPROVAL_GATE_READY_NO_PROVIDER_ACTION`
- no deploy or upload script is added
- no provider token, account ID, tester email or tester URL appears in tracked public files
- static tests and full pytest pass
- `git diff --check` passes

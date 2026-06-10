# T10ajm Workers.dev Shell Gate

## Objective

T10ajm adapts the Cloudflare route after confirming there is no custom domain and no existing Worker to protect with Cloudflare Access.

The realistic path is a controlled `workers.dev` pilot:

1. Keep the real OpenNext tester portal undeployed.
2. Prepare a harmless shell Worker whose only job is to create the Cloudflare target.
3. Deploy that shell only in the next phase, with exact operator approval.
4. Enable Cloudflare Access on the shell target before any tester URL is shared.
5. Replace the shell with the real app only after Access and app auth are both verified.

This phase does not deploy a Worker, create Access, publish a tester URL, create tester accounts, commit hostnames or commit Cloudflare account data.

## Why This Exists

Cloudflare Access protects an application target. With no custom domain and no Worker yet, there is no target to select in the dashboard. The safe sequence is therefore not "mark Access ready"; it is "create a non-app shell target first, then protect it, then deploy the app".

## Prepared Shell Artifacts

- `templates/SQX_Edge_Tester_Portal/cloudflare/shell-worker.js`
- `templates/SQX_Edge_Tester_Portal/wrangler.shell.example.jsonc`
- `templates/SQX_Edge_Tester_Portal/scripts/cloudflare-workers-dev-shell-gate-proof.mjs`

The shell Worker returns a locked/no-app response with conservative security headers. It contains no dashboard code, no tester logic, no credentials, no tester emails and no private route data.

## Exact Next External Action

The next phase may create the shell Worker only with exact approval for the external action. The command must be run from `templates/SQX_Edge_Tester_Portal`:

```powershell
npm exec -- wrangler deploy --config wrangler.shell.example.jsonc
```

After the shell exists, the operator must immediately verify in Cloudflare dashboard that Access can be enabled for the selected Worker target before any tester URL is shared.

## Local Proof

Run from `templates/SQX_Edge_Tester_Portal`:

```powershell
npm run proof:cloudflare-workers-dev-shell-gate
```

Expected result for this phase:

```text
GO_WORKERS_DEV_SHELL_GATE_READY_EXACT_DEPLOY_APPROVAL_REQUIRED
```

## Official Sources Checked

- Cloudflare Workers `workers.dev`: https://developers.cloudflare.com/workers/configuration/routing/workers-dev/
- Cloudflare Wrangler deploy commands: https://developers.cloudflare.com/workers/wrangler/commands/
- Cloudflare Access application types, including Workers as self-hosted applications: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/
- Cloudflare self-hosted public applications: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/
- Cloudflare Access "Require Access protection": https://developers.cloudflare.com/cloudflare-one/access-controls/access-settings/require-access-protection/

## Security Boundary Preserved

- No real tester portal was deployed.
- No Cloudflare Worker was created by this phase.
- No Cloudflare Access application was created by this phase.
- No Cloudflare Access policy was created by this phase.
- No tester URL was published.
- No tester accounts were created.
- No tester emails were committed.
- No Cloudflare hostname, account ID, zone ID or token was committed.
- Main `wrangler.jsonc` keeps `workers_dev=false` and `preview_urls=false`.
- The shell `workers_dev=true` setting exists only in the dedicated shell config.

## Next Gate

```text
T10ajn_controlled_workers_dev_shell_deploy
```

T10ajn is the first phase allowed to create the shell Worker, and only after exact approval. T10ak remains blocked until the shell target exists and Cloudflare Access protection is verified.

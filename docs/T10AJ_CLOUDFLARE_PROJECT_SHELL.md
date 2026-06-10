# T10aj Cloudflare Project Shell Gate

## Objective

T10aj records Ivan's exact approval to create or verify the Cloudflare shell named `sqx-edge-tester-portal-preview`, while preserving the non-negotiable boundary: no deployment, no Cloudflare Access application or policy, no tester URL publication and no tester accounts.

## Exact Approval Captured

```text
T10aj: crear o verificar el shell del proyecto Cloudflare sqx-edge-tester-portal-preview, sin deploy, sin Access policy todavia, sin URL tester publicada y sin crear testers.
```

## Official Sources Checked

- Cloudflare Workers Wrangler commands: https://developers.cloudflare.com/workers/wrangler/commands/workers/
- Cloudflare Workers Wrangler command index: https://developers.cloudflare.com/workers/wrangler/commands/
- Cloudflare Workers framework auto-configuration: https://developers.cloudflare.com/workers/framework-guides/automatic-configuration/
- Cloudflare Workers Wrangler configuration: https://developers.cloudflare.com/workers/wrangler/configuration/

## Provider Reality Check

The local probe was limited to authentication and command-shape checks:

```text
npm exec --yes wrangler@latest -- whoami
result=not_authenticated

npm exec --yes wrangler@latest -- deploy --help
deploy_command=publishes_worker
dry_run_available=true

npm exec --yes wrangler@latest -- setup --help
setup_command=configures_project_files
provider_shell_creation=false
```

Cloudflare documents `wrangler deploy` as the command that deploys a Worker to Cloudflare. Its `--dry-run` compiles without deploying, and `wrangler setup --dry-run` can prepare local configuration, but neither is a verified no-deploy provider-shell creation path.

## Result

```text
NO_GO_CLOUDFLARE_PROJECT_SHELL_NOT_VERIFIED_NO_AUTH_NO_DEPLOY_PATH
```

The Cloudflare project shell was not created or verified because:

- Wrangler is not authenticated locally.
- No `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` or equivalent local provider credentials are present.
- The available no-deploy CLI path configures local files; it does not prove that a Cloudflare provider project shell exists.
- Creating a Worker through `wrangler deploy` would violate the explicit no-deploy boundary.

## Security Boundary Preserved

- No Cloudflare project was created.
- No Cloudflare deployment was created.
- No Cloudflare Access application was created.
- No Cloudflare Access policy was created.
- No GitHub repository was connected to Cloudflare.
- No Cloudflare token or account ID was committed.
- No tester URL was published.
- No tester accounts were created.
- No tester emails were committed.
- No renewal emails were sent.
- No production database was connected.

## Remaining T10xx Plan

```text
T10ajb: resolve Cloudflare authentication or manually verify/create the provider shell without deployment.
T10ak: create Cloudflare Access application and policy only with exact approval after shell verification.
T10al: execute one controlled Workers deployment only after shell + Access policy are verified.
T10am: run protected-route E2E smoke before sharing any URL.
T10an: prepare private tester onboarding packet without committing tester emails or URL.
T11: roll out to up to 10 testers with monitored access and manual renewal.
T12: monitor abuse, failed logins, access patterns and continue/stop decision.
```

## Next Gate

```text
T10ajb_cloudflare_auth_or_manual_shell_verification_no_deploy
```

T10ak must remain blocked until `sqx-edge-tester-portal-preview` is verified as a real Cloudflare shell with no deployment and no shared tester surface.

## Verification

T10aj is accepted when:

- this document exists
- `scripts/cloudflare-project-shell-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-project-shell`
- the proof returns `NO_GO_CLOUDFLARE_PROJECT_SHELL_NOT_VERIFIED_NO_AUTH_NO_DEPLOY_PATH`
- roadmap/governance memorize the remaining T10xx and Txx gates
- no deploy script is added
- no provider token, account ID, tester email or tester URL appears in tracked files
- static tests and full pytest pass
- `git diff --check` passes

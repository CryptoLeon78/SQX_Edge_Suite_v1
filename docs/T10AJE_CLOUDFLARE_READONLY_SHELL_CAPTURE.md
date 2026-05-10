# T10aje Cloudflare Read-Only Shell Capture

## Objective

T10aje executes the safe part of the manual/authenticated Cloudflare evidence capture: authenticate Wrangler, inspect the proposed Worker name and decide whether T10ak can remain blocked or be proposed.

This phase does not create a Worker, does not deploy, does not create Cloudflare Access, does not publish a tester URL and does not create testers.

## Auth Result

```text
wrangler_login=success
wrangler_whoami=authenticated
```

The raw `whoami` output included private account details and was not committed.

## Read-Only Provider Checks

```text
npm exec --yes wrangler@latest -- deployments list --name sqx-edge-tester-portal-preview --json
result=worker_not_found
cloudflare_error_code=10007

npm exec --yes wrangler@latest -- versions list --name sqx-edge-tester-portal-preview --json
result=worker_not_found
cloudflare_error_code=10007

npm exec --yes wrangler@latest -- secret list --name sqx-edge-tester-portal-preview --format json
result=worker_not_found
```

Cloudflare reports that `sqx-edge-tester-portal-preview` does not exist on the authenticated account.

## Result

```text
NO_GO_CLOUDFLARE_WORKER_NOT_FOUND_T10AK_BLOCKED
```

T10ak stays blocked because there is no provider shell to protect with Access yet.

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

## Next Gate

```text
T10ajf_choose_shell_creation_path_or_controlled_deploy_approval
```

T10ajf must decide between:

- finding an exact no-deploy Cloudflare shell creation path that creates no serving Worker and no tester surface, or
- requesting explicit approval for one controlled deployment later, only after Access/security gates are redesigned around the fact that Cloudflare Workers shell creation appears tied to deploy/upload.

## Verification

T10aje is accepted when:

- this document exists
- `scripts/cloudflare-readonly-shell-capture-proof.mjs` exists
- `package.json` exposes `proof:cloudflare-readonly-shell-capture`
- the proof returns `NO_GO_CLOUDFLARE_WORKER_NOT_FOUND_T10AK_BLOCKED`
- no deploy script is added
- no provider token, account ID, tester email or tester URL appears in tracked files
- static tests and full pytest pass
- `git diff --check` passes

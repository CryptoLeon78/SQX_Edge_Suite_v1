# T10aq Tester Access Handoff No URL Leak

## Objective

T10aq prepares the controlled tester access handoff after the protected `workers.dev` publication, without committing or sharing the tester URL from the public repository.

This phase does not create tester accounts, does not email testers, does not publish the URL and does not run a Cloudflare deployment.

## Handoff Boundary

The tester URL may only be handled manually by the operator outside Git after all checks below are true:

- T10ap publication result is `GO_CONTROLLED_WORKERS_DEV_PUBLICATION_ACCESS_PROTECTED_NO_URL_SHARED`.
- Cloudflare Access still intercepts anonymous traffic before any app body is visible.
- App-level login/session protection remains enabled after Access.
- The tester list is managed outside the public repo.
- No tester URL, hostname, Access ID, account ID, deployment ID, version ID, tester email, password, token or key is committed.

## Private Local Handoff File

If the operator needs a local checklist, create this ignored file only:

```text
templates/SQX_Edge_Tester_Portal/tester-access-handoff.local.json
```

It may contain redacted booleans only. It must not contain:

- URL or hostname.
- Tester emails or passwords.
- Account IDs, Access IDs, deployment IDs or version IDs.
- Tokens, API keys, private keys or session cookies.

## Manual Handoff Steps

1. Confirm Cloudflare Access blocks anonymous traffic.
2. Confirm the app still requires tester login after Cloudflare Access.
3. Prepare tester accounts in the private/auth data path only.
4. Send the URL manually through a private channel only after the tester identity is ready.
5. Record public-safe status only as booleans in ignored local evidence.
6. Do not paste the URL in GitHub, README, docs, screenshots, issues, commits or this chat unless explicitly needed for a private manual operation.

## Acceptance

```text
GO_TESTER_ACCESS_HANDOFF_READY_NO_PUBLIC_URL_LEAK
```

This means the project is ready for a private operator handoff, not that testers have been invited.

## Next Gate

```text
T10ar_private_tester_account_activation_gate
```

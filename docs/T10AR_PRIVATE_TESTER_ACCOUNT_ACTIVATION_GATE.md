# T10ar Private Tester Account Activation Gate

## Objective

T10ar prepares the private tester account activation gate after T10aq, without committing tester emails, passwords, URLs, hostnames, account IDs, Access IDs, tokens or support-channel details.

This phase does not create tester accounts, does not send invitations, does not publish the tester URL and does not run a Cloudflare deployment.

## Activation Boundary

Tester accounts may only be activated outside Git after all checks below are true:

- T10aq handoff result is `GO_TESTER_ACCESS_HANDOFF_READY_NO_PUBLIC_URL_LEAK`.
- Cloudflare Access still intercepts anonymous traffic before any app body is visible.
- App login/session protection still applies after Cloudflare Access.
- Password setup or reset flow is private and never stores plaintext passwords.
- The 15-day tester renewal cadence is scheduled in the private operator workflow.
- The operator has a private support channel ready before the URL is shared.
- No tester email, URL, hostname, password, token, API key, Access ID, account ID, deployment ID or version ID is committed.

## Private Local Activation File

If the operator needs an activation checklist, create this ignored file only:

```text
templates/SQX_Edge_Tester_Portal/tester-account-activation.local.json
```

It may contain public-safe booleans and counts only. It must not contain:

- Tester emails, names, passwords or reset links.
- URL or hostname.
- Account IDs, Access IDs, deployment IDs or version IDs.
- Tokens, API keys, private keys or session cookies.
- Chat, support or distribution channel URLs.

## Manual Activation Steps

1. Confirm Access blocks anonymous traffic.
2. Confirm app-level login is still required after Access.
3. Create tester accounts only in the private auth/provider path.
4. Set or send passwords through a private one-to-one channel only.
5. Schedule 15-day renewal review before sharing access.
6. Prepare support and revocation notes outside Git.
7. Record only redacted booleans/counts in the ignored local activation file.
8. Share the tester URL only after the private account and support path are ready.

## Acceptance

```text
GO_PRIVATE_TESTER_ACCOUNT_ACTIVATION_GATE_READY_NO_GIT_LEAK
```

This means the project is ready for private account activation handling, not that testers have been invited or that credentials have been sent.

## Next Gate

```text
T10as_private_tester_activation_evidence_ingest
```

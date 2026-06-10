# T10as Private Tester Activation Evidence Ingest

## Objective

T10as ingests the ignored local evidence for private tester activation after T10ar, while keeping tester emails, passwords, URLs, hostnames, account IDs, Access IDs, tokens and support-channel details out of Git.

This phase does not create tester accounts, does not send invitations, does not publish the tester URL, does not rotate passwords and does not run a Cloudflare deployment.

## Local Evidence Boundary

The only accepted local activation evidence path is:

```text
templates/SQX_Edge_Tester_Portal/tester-account-activation.local.json
```

That file is ignored by Git and may contain only public-safe booleans and small counts. It must not contain:

- Tester emails, names, passwords, reset links or access codes.
- URL, hostname, domain, route or workers.dev address.
- Account IDs, Access IDs, deployment IDs, version IDs or policy IDs.
- Tokens, API keys, private keys, cookies or session values.
- Chat, support, distribution or meeting links.

## Accepted Fields

The evidence file may use only these fields:

- `phase`: `T10ar` or `T10as`.
- Boolean checks: `accessStillInterceptsAnonymous`, `appSessionStillRequiredAfterAccess`, `privateAuthProviderSelected`, `privateTesterAccountsPrepared`, `passwordDeliveryChannelPrivate`, `renewalCadenceScheduled`, `supportChannelReadyPrivately`, `revocationPathReadyPrivately`, `testerAccountsCreatedPrivately`, `testerInvitesSentPrivately`, `testerUrlSharedPrivately`, `publicRepoContainsTesterEmails`, `publicRepoContainsTesterUrl`, `publicRepoContainsCredentials`, `publicRepoContainsProviderIds`.
- Count checks: `activatedTesterCount`, `pendingTesterCount`, `invitedTesterCount`.

Counts must be non-negative integers no greater than 50.

## Expected Results

Without the ignored local evidence file, the expected guarded result is:

```text
NO_GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_MISSING
```

With safe local evidence and no public leak, the expected result is:

```text
GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_SAFE_NO_GIT_LEAK
```

Unsafe evidence must fail closed and stop the phase.

## Operator Meaning

`GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_SAFE_NO_GIT_LEAK` means private activation evidence is safe enough to proceed to the next URL-sharing approval gate. It does not mean tester URL sharing has happened, and it does not authorize public publication.

## Next Gate

```text
T10at_private_tester_url_share_approval_gate
```

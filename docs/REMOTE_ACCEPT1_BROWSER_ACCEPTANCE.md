# REMOTE-ACCEPT1 - Real Browser Acceptance Gate

## Summary

REMOTE-ACCEPT1 is a short stabilization gate before adding more testers. It checks the real browser experience after Cloudflare Access and before continuing REMOTE-8C expansion decisions.

This phase exists because automated tests can prove contracts, but the first tester flow must also feel clean in a real browser.

## What The Underlined Welcome Text Means

The old text "falta crear la sesion de app" meant:

- Cloudflare Access already identified the user.
- The local entitlement store already found an active permission.
- SQX Edge Suite still had to create its own private app session and workspace before loading the dashboard.

It did not mean the user did something wrong, but it sounded like an internal technical failure. The Welcome copy must now say:

`Identidad y permiso validados. Pulsa Acceso DASHBOARD para abrir tu workspace privado.`

The user-facing rule is simple: if the screen says `OK identidad validada`, the next action is only `Acceso DASHBOARD`.

## Manual Acceptance Checklist

Run this checklist in the real protected URL before inviting or expanding testers:

1. Open a private/incognito browser window.
2. Enter through Cloudflare Access with the approved tester email.
3. Confirm the Welcome title renders as:
   - `Bienvenido a`
   - `SQX Edge Suite`
4. Confirm the identity card says the user is validated and does not expose internal wording like `falta crear la sesion de app`.
5. Click `Acceso DASHBOARD` once.
6. Confirm the Welcome screen does not reappear immediately.
7. Confirm the dashboard is usable and the remote status/workspace state is visible without raw email, token, Cloudflare id or local server path.
8. Close the browser completely.
9. Reopen the protected URL in a fresh browser session.
10. Confirm the app session is not silently treated as permanently open after browser close.
11. Confirm Cloudflare Access can still authenticate normally.
12. Confirm logout or session reset, if used, clears the app session cleanly.

## Evidence

Private evidence belongs only in:

`.local/remote_service/remote_accept1_browser_acceptance.local.json`

Do not commit screenshots, emails, protected URLs, cookies, tokens, Cloudflare ids or local paths.

Use the tracked template:

`docs/examples/remote_accept1_browser_acceptance.local.example.json`

## Acceptance

REMOTE-ACCEPT1 is considered acceptable only if:

- the Welcome copy is understandable for a non-technical tester;
- `Acceso DASHBOARD` works with one click after identity validation;
- the Welcome gate does not bounce back immediately;
- closing the browser does not create a long-lived app-session expectation;
- the evidence is redacted and stored outside Git;
- no tester expansion, checkout, grant creation or public URL sharing happens in this phase.

## Next Action

If REMOTE-ACCEPT1 passes, continue REMOTE-8C observation with much higher confidence. If it fails, fix the browser flow before any WAIT or expansion work.

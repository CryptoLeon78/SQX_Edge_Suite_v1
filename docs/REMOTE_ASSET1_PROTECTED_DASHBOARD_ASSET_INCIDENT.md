# REMOTE-ASSET1 - Protected Dashboard Asset Incident

## Summary

REMOTE-ASSET1 records the first tester/incognito dashboard rendering incident:
Cloudflare Access authentication succeeded and `/dashboard` returned the app
HTML, but the browser rendered raw, unstyled content because runtime CSS/JS
assets were not loaded under the same protected dashboard surface.

This pattern is now part of REMOTE traceability:

`/dashboard HTML OK` does not mean the remote app is healthy unless protected
CSS, JS, vendor files and non-public assets are also OK.

## Symptom

- Operator normal browser: dashboard appeared correct, likely because cached
  assets masked the issue.
- Operator incognito browser: dashboard showed raw HTML and default browser
  controls.
- External tester report: same raw dashboard view after Cloudflare Access
  authentication passed.

## Cause

The protected `/dashboard` HTML referenced assets with root-relative runtime
surfaces such as `css/...`, `js/...` and `vendor/...`. In clean browser
sessions those requests could be evaluated differently from the authenticated
dashboard entry, causing the dashboard HTML to load while CSS/JS did not.

## Fix

The backend now rewrites the protected dashboard entry so runtime assets load
through `/dashboard/...`:

- `/dashboard/css/...`
- `/dashboard/js/...`
- `/dashboard/vendor/...`
- `/dashboard/assets/...`

The backend also serves those prefixed asset paths from the same dashboard
asset root. Public social-preview assets remain separate and public-safe.

## Verification

Completed on 2026-05-18:

- Operator incognito browser: dashboard renders correctly.
- External tester redacted as `tester-ref-asset1`: dashboard renders correctly
  and works after Cloudflare Access authentication.
- Local backend check: `/dashboard/css/dashboard.css` returns `200` with
  `text/css`.
- Cloudflare boundary smoke remains clean: root preview public, `/dashboard`
  protected, public-safe brand assets cacheable and no app body visible to
  anonymous users.

## Regression Rule

Every remote browser acceptance or tester-expansion phase must treat the
following as a required smoke pattern:

1. `/dashboard` returns protected app HTML only after Access.
2. `/dashboard/css/dashboard.css` returns CSS.
3. `/dashboard/js/main.js` or another boot script returns JavaScript.
4. No raw app body is visible anonymously.
5. Public root/link-preview still exposes only product metadata and brand
   imagery.

## REMOTE-8E Impact

This incident is closed before REMOTE-8E. It does not by itself authorize
REMOTE-8E execution. REMOTE-8E is still not recorded as GO. REMOTE-8E still
requires explicit operator approval and private evidence that 3-5 users were
activated manually with matching manual counts and zero automation.

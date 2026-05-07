# Post-Sale Micro Updates And Next Buyer Readiness

Use this after M68 is GO and the approved micro-updates have been applied to buyer-facing material.

## Applied Micro-Updates

- `START_HERE.md` includes a first-value path for a basic buyer.
- `license_activation_walkthrough.md` includes a quick Pro-active status check.
- `support_contact_template.md` asks for the exact stuck step, license status and first-value status.
- `support_macro.md` asks for first-value state and blocks sensitive material.
- Public copy states the first operational promise without financial-result claims.

## Command

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\post_sale_micro_updates.py `
  --use-latest-improvement-loop `
  --applied-updates 5 `
  --onboarding-updates 2 `
  --support-macro-updates 2 `
  --public-copy-updates 1 `
  --safe-claims-updates 0 `
  --next-buyer-steps 5 `
  --support-risk 0 `
  --claims-risk 0 `
  --decision next_controlled_buyer_ready `
  --priority medium `
  --owner operator `
  --next-review M70 `
  --update-summary "Applied first-value onboarding, activation check, support template and public-copy micro-updates." `
  --readiness-notes "Share only a private controlled link with the next buyer and keep support same-day." `
  --confirm-post-sale-improvement-go `
  --confirm-start-here-updated `
  --confirm-license-walkthrough-updated `
  --confirm-support-macros-updated `
  --confirm-public-copy-updated `
  --confirm-safe-claims-preserved `
  --confirm-next-buyer-check-recorded
```

## Next Controlled Buyer Check

Before sharing another private checkout link:

1. Confirm ZIP, license issue path and support email are ready.
2. Confirm the buyer receives `START_HERE.md` and the license walkthrough.
3. Confirm support asks for exact step and first-value status.
4. Confirm public copy still avoids financial-result promises.
5. Confirm the next review owner and pause rule are known.

Use `pause_sales` instead of `next_controlled_buyer_ready` if support risk, refund risk, fulfillment risk or claims risk appears.

## Privacy Boundary

Store only counts, readiness notes and operational decisions. Do not store buyer names, emails, raw support messages, checkout payloads, signed licenses, private keys or secrets.

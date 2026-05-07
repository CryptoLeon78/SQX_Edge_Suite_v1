# Post-Sale Improvement Loop

Use this note after the first controlled buyer log is GO. The goal is not to scale sales immediately. The goal is to turn the first buyer experience into small buyer-safe updates.

## Command

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\post_sale_improvement_loop.py `
  --use-latest-first-buyer-log `
  --onboarding-updates 1 `
  --support-macro-updates 1 `
  --public-copy-updates 0 `
  --safe-claims-updates 0 `
  --followup-actions 1 `
  --support-risk 0 `
  --claims-risk 0 `
  --decision ship_micro_updates `
  --priority medium `
  --owner operator `
  --next-review M69 `
  --improvement-summary "Tighten START_HERE and support macro from first buyer questions." `
  --review-notes "Keep the page private until the buyer confirms first value." `
  --confirm-first-buyer-log-go `
  --confirm-onboarding-reviewed `
  --confirm-support-macros-reviewed `
  --confirm-public-copy-reviewed `
  --confirm-safe-claims-reviewed `
  --confirm-owner-assigned `
  --confirm-next-review-recorded
```

## Decisions

- `ship_micro_updates`: apply small onboarding/support/copy improvements before more traffic.
- `revise_onboarding`: buyer instructions need another pass.
- `revise_support_macros`: support templates need clearer replies.
- `revise_public_copy`: public wording created wrong expectations.
- `pause_sales`: unresolved support, refund, fulfillment or claims risk exists.

## Privacy Boundary

Store only aggregated action counts, owner, next review and short operational summaries. Do not store buyer names, email, raw messages, checkout payloads, licenses, private keys, signed files or secrets.

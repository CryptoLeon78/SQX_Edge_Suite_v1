# Next Controlled Buyer Readiness Check

Use this before sharing another private checkout link. The goal is one calm buyer, not wider traffic.

## Command

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\next_controlled_buyer_readiness.py `
  --use-latest-micro-updates `
  --buyer-slots 1 `
  --private-link-status ready_private_link `
  --checkout-ready `
  --license-delivery-ready `
  --delivery-package-ready `
  --support-capacity-hours 24 `
  --followup-window-hours 48 `
  --open-support-items 0 `
  --claims-risk 0 `
  --decision share_private_link `
  --owner operator `
  --readiness-notes "Share one private checkout link only; pause if support, refund, delivery or claims risk appears." `
  --confirm-post-sale-micro-updates-go `
  --confirm-private-link-reviewed `
  --confirm-checkout-readiness-reviewed `
  --confirm-license-delivery-ready `
  --confirm-support-capacity-ready `
  --confirm-safe-claims-reviewed `
  --confirm-pause-rule-reviewed `
  --confirm-followup-window-recorded
```

## Decisions

- `share_private_link`: share one private checkout link with one controlled buyer.
- `hold_for_fix`: do not share yet; fix onboarding, checkout, license delivery or support readiness.
- `pause_sales`: stop if support, fulfillment, refund, checkout or claims risk appears.

## Readiness Rules

- Exactly one buyer slot.
- Private link ready but not public.
- ZIP, license delivery and support instructions ready.
- Same-day support capacity available.
- Follow-up window recorded.
- Safe claims and pause rule reviewed.

## Privacy Boundary

Store only readiness counts, status, owner and operational notes. Do not store buyer names, emails, raw checkout payloads, signed licenses, private keys, support messages or secrets.

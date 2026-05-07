# Template Pack 1 Live Checkout Publication

## Purpose

This runbook connects real checkout values for Template Pack 1 without committing fake URLs or provider IDs.

## Required Values

- `SQX_TEMPLATE_PACK_1_CHECKOUT_URL`: real hosted checkout URL.
- `SQX_TEMPLATE_PACK_1_PROVIDER_VARIANT_ID`: provider variant or product ID for Template Pack 1.
- `SQX_TEMPLATE_PACK_1_SUPPORT_EMAIL`: support inbox that buyers can contact.
- `SQX_TEMPLATE_PACK_1_FALLBACK_URL`: optional fallback checkout URL.

## Dry Run

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_1_publication.py `
  --checkout-url "https://checkout.your-provider.com/template-pack-1" `
  --provider-variant-id "tpl_pack_1_real_id" `
  --support-email "support@yourdomain.com" `
  --confirm-offer-reviewed `
  --confirm-checkout-url-tested `
  --confirm-provider-variant-confirmed `
  --confirm-support-inbox-ready `
  --confirm-delivery-macro-ready `
  --confirm-rollback-ready `
  --confirm-controlled-publication-approved `
  --no-write
```

## Apply

Run the same command with `--apply` only after the dry run returns `GO`. The tool updates the Template Pack 1 plan checkout URL, provider variant ID, support email and `templatePack1LiveCheckout` manifest block.

## Rollback

- Pause or unpublish the provider checkout link.
- Pause webhook/relay if orders are arriving incorrectly.
- Keep manual signed-license fulfillment available.
- Review first 5 sales before scaling public traffic.

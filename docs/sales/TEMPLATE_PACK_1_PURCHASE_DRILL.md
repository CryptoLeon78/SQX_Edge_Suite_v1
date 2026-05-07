# Template Pack 1 Purchase Drill

## Purpose

Use this runbook for the first controlled Template Pack 1 purchase before sending public traffic to the add-on.

## Required Evidence

- Checkout URL used.
- Provider variant ID.
- Provider order ID.
- Buyer email, stored only as redacted evidence by the gate.
- Payment status: `paid`, `succeeded` or `completed`.
- Amount `49.00` and currency `EUR`.
- Add-on ZIP delivery path, when package verification is required.
- Delivery email, support inbox and refund/pause path ready.

## Delivery Package

Generate the separate add-on ZIP with:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_1_delivery.py `
  --customer-email "buyer@example.com" `
  --order-id "real-order-id" `
  --confirm-buyer-onboarding-gate-go `
  --confirm-addon-order-confirmed `
  --confirm-readme-included `
  --confirm-profiles-validated `
  --confirm-support-boundaries-included `
  --confirm-safe-claims-reviewed `
  --package
```

## Purchase Drill Gate

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_1_purchase_drill.py `
  --checkout-url "https://checkout.your-provider.com/template-pack-1" `
  --provider-variant-id "real-provider-variant-id" `
  --provider-order-id "real-order-id" `
  --buyer-email "buyer@example.com" `
  --payment-status "paid" `
  --amount "49.00" `
  --currency "EUR" `
  --delivery-package-path "backend\sqx-edge-tool\data\template_pack_1_delivery\SQX_Template_Pack_1_YYYYMMDD_HHMMSS.zip" `
  --confirm-live-checkout-values-confirmed `
  --confirm-controlled-purchase-paid `
  --confirm-provider-order-recorded `
  --confirm-delivery-package-ready `
  --confirm-delivery-email-ready `
  --confirm-support-inbox-ready `
  --confirm-safe-claims-reviewed `
  --confirm-refund-or-pause-ready `
  --require-delivery-package
```

## GO Criteria

- Payment is confirmed by the provider.
- Delivery package is a separate add-on ZIP.
- Support inbox is ready.
- Refund or pause path is ready.
- No financial-result claims are used.

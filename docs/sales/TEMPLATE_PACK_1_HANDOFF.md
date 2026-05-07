# Template Pack 1 Post-Purchase Handoff

## Purpose

Use this runbook after the controlled purchase drill returns `GO`. It confirms delivery, first support contact and the decision to scale, hold or pause Template Pack 1 sales.

## Required Evidence

- Purchase drill evidence file.
- Buyer reference, stored redacted by the gate.
- Provider order ID.
- Handoff owner.
- Support ticket or support thread ID.
- First response time in hours.
- Unresolved support item count.
- Refund risk flags.
- Scale decision: `scale_limited`, `hold_review` or `pause_sales`.
- Short handoff notes with no raw provider payloads.

## Gate

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_1_handoff.py `
  --use-latest-purchase-drill `
  --buyer-email "buyer@example.com" `
  --provider-order-id "real-order-id" `
  --handoff-owner "Ivan" `
  --support-ticket-id "support-thread-001" `
  --first-response-hours 2 `
  --unresolved-support-items 0 `
  --refund-risk-flags 0 `
  --scale-decision "hold_review" `
  --handoff-notes "Buyer received the add-on and first support window is open." `
  --confirm-purchase-drill-go `
  --confirm-delivery-sent `
  --confirm-buyer-acknowledged `
  --confirm-support-window-opened `
  --confirm-first-value-confirmed `
  --confirm-support-notes-recorded `
  --confirm-safe-claims-reviewed `
  --confirm-scale-or-pause-decision-recorded
```

## Decision Rules

- Use `scale_limited` only when there are no unresolved support items and no refund risk.
- Use `hold_review` while confidence is forming.
- Use `pause_sales` when delivery, support or buyer outcome is unclear.
- Do not promise financial results in handoff notes or support copy.

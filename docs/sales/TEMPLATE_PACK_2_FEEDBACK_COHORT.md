# Template Pack 2 Feedback Cohort Review

Este review convierte las primeras ventas y soporte de Template Pack 2 en una decision tranquila antes de abrir mas trafico.

## Datos minimos

- Sales register M63 en `GO`.
- Numero de compradores revisados.
- Numero de feedback items agregados.
- Bugs bloqueantes, friccion de activacion, gaps de documentacion y feature requests.
- Senales positivas, soporte abierto y refunds.
- Decision: `expand_traffic`, `iterate_offer`, `prepare_pack_3` o `pause_sales`.

## Comando base

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_2_feedback_cohort.py `
  --use-latest-sales-register `
  --buyer-count 1 `
  --feedback-count 2 `
  --blocking-bugs 0 `
  --activation-friction 0 `
  --docs-gaps 1 `
  --feature-requests 1 `
  --positive-signals 2 `
  --open-support-items 0 `
  --refund-count 0 `
  --roadmap-decision iterate_offer `
  --feedback-themes "Buyer asks for clearer setup notes and likes the multi-timeframe profiles." `
  --review-notes "Keep traffic controlled while improving copy and docs. No raw buyer messages stored." `
  --confirm-sales-register-go `
  --confirm-feedback-reviewed `
  --confirm-support-reviewed `
  --confirm-safe-claims-reviewed `
  --confirm-roadmap-decision-recorded
```

## Reglas de decision

- `expand_traffic`: solo con suficientes compradores, feedback y cero soporte/refund/friccion.
- `iterate_offer`: decision normal si hay mejoras de copy, docs, activacion o material de soporte.
- `prepare_pack_3`: solo con senales positivas claras y sin riesgo operativo.
- `pause_sales`: si aparecen bugs, refunds, soporte abierto o riesgo de claims.

## Privacidad

Guarda temas agregados, no mensajes crudos. No pegues correos completos, payloads del proveedor ni datos personales en `feedback-themes` o `review-notes`.

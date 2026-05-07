# Template Pack 1 Feedback Cohort Review

Esta revision decide si Template Pack 1 puede recibir mas trafico, si conviene iterar la oferta o si hay base real para Template Pack 2.

## Datos minimos

- Registro M54 en `GO`.
- Numero de compradores revisados.
- Numero de items de feedback.
- Bugs bloqueantes, friccion de activacion, gaps de documentacion y solicitudes de features.
- Senales positivas.
- Soporte abierto y refunds.
- Decision: `expand_traffic`, `iterate_offer`, `build_template_pack_2` o `pause_sales`.

## Comando base

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_1_feedback_cohort.py `
  --use-latest-sales-register `
  --buyer-count 3 `
  --feedback-count 4 `
  --blocking-bugs 0 `
  --activation-friction 0 `
  --docs-gaps 1 `
  --feature-requests 2 `
  --positive-signals 3 `
  --open-support-items 0 `
  --refund-count 0 `
  --roadmap-decision iterate_offer `
  --feedback-themes "clear install, wants extra asset presets, improve docs" `
  --review-notes "Cohort reviewed with safe claims and no unresolved support." `
  --confirm-sales-register-go `
  --confirm-feedback-reviewed `
  --confirm-support-reviewed `
  --confirm-safe-claims-reviewed `
  --confirm-roadmap-decision-recorded
```

## Reglas de decision

- `expand_traffic`: solo si no hay friccion operativa ni refunds.
- `iterate_offer`: decision por defecto si hay mejoras de docs, copy, onboarding o features.
- `build_template_pack_2`: solo con senales positivas claras y soporte controlado.
- `pause_sales`: usar ante bugs bloqueantes, soporte abierto, refunds o riesgo de claims.

## Privacidad

No pegues conversaciones completas, emails, capturas de pedidos ni payloads de checkout. Resume temas y metricas; el comprador debe seguir estando redactado o agregado.

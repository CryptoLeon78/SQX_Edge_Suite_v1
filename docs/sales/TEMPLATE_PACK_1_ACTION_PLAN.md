# Template Pack 1 Action Plan

Este gate convierte el feedback de cohorte en una siguiente fase ejecutable.

## Datos minimos

- Feedback cohort M55 en `GO`.
- Plan elegido: `offer_iteration`, `traffic_expansion`, `template_pack_2` o `pause_sales`.
- Owner del plan.
- Prioridad.
- Numero de acciones concretas.
- Impacto de soporte, distribucion y claims.
- Siguiente fase M57.

## Comando base

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_1_action_plan.py `
  --use-latest-feedback-cohort `
  --action-plan template_pack_2 `
  --action-owner Ivan `
  --priority high `
  --action-count 4 `
  --support-impact 1 `
  --distribution-impact 1 `
  --claims-risk 0 `
  --next-phase M57_template_pack_2_specs `
  --action-summary "Define Pack 2 scope, asset presets, docs improvements and delivery checklist." `
  --plan-notes "Cohort supports Pack 2 planning without unresolved support or claims risk." `
  --confirm-feedback-cohort-go `
  --confirm-action-owner-assigned `
  --confirm-support-impact-reviewed `
  --confirm-safe-claims-reviewed `
  --confirm-distribution-impact-reviewed `
  --confirm-next-phase-recorded
```

## Reglas

- `offer_iteration` debe ir a `M57_offer_iteration`.
- `traffic_expansion` debe ir a `M57_traffic_expansion` y tener bajo impacto de soporte.
- `template_pack_2` debe ir a `M57_template_pack_2_specs`.
- `pause_sales` debe ir a `M57_pause_and_fix`.

## Privacidad

No pegues mensajes completos de compradores, emails, capturas ni datos de pago. Resume acciones y riesgos de forma agregada.

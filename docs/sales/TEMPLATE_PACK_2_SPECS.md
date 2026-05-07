# Template Pack 2 Specs

Este gate evita crear un segundo pack por impulso. Template Pack 2 solo avanza si el plan M56 y el feedback agregado justifican alcance, soporte y entrega.

## Datos minimos

- Action plan M56 en `GO` con `template_pack_2`.
- Familias de activos.
- Numero de presets previstos.
- Temas de feedback mapeados.
- Horas o alcance de soporte.
- Modelo de entrega.
- Siguiente fase.

## Comando base

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_2_specs.py `
  --use-latest-action-plan `
  --spec-decision draft_pack_2_assets `
  --asset-families 2 `
  --preset-count 8 `
  --feedback-themes-mapped 3 `
  --support-scope-hours 2 `
  --claims-risk 0 `
  --delivery-model "separate_addon_zip_after_pack_2_gate" `
  --next-phase M58_template_pack_2_assets `
  --scope-summary "Pack 2 focuses on additional asset presets and clearer starter profiles." `
  --support-boundaries "Support covers import, first run and package structure; no financial performance promises." `
  --confirm-action-plan-go `
  --confirm-buyer-feedback-mapped `
  --confirm-scope-defined `
  --confirm-safe-claims-reviewed `
  --confirm-support-boundaries-defined `
  --confirm-delivery-model-defined `
  --confirm-next-phase-recorded
```

## Reglas

- `draft_pack_2_assets`: avanzar a `M58_template_pack_2_assets`.
- `iterate_pack_1_first`: avanzar a `M58_pack_1_iteration`.
- `pause_pack_2`: avanzar a `M58_pause_pack_2`.

## Privacidad

No pegues feedback crudo, emails, capturas ni datos de pago. Resume alcance, temas y riesgos en forma agregada.

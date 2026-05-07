# Template Pack 1 Delivery

## Objetivo

Entregar Template Pack 1 como add-on separado, con evidencia de que el comprador recibe material claro, seguro y con soporte acotado.

## Contenido

- `README.md`
- `profiles/edge-discovery-momentum.json`
- `profiles/risk-controlled-continuation.json`
- `profiles/mean-reversion-lab.json`
- `presets/strategy_import_template_pack_1.csv`
- `checklists/delivery_checklist.md`
- `checklists/support_boundaries.md`

## Criterios GO

- Buyer onboarding support gate revisado.
- Orden del add-on confirmada.
- ZIP del pack generado.
- Perfiles JSON validados.
- CSV revisado.
- Limites de soporte incluidos.
- Claims seguros revisados.

## Criterios NO-GO

- Falta comprador u order id.
- Falta pack ZIP.
- Falta cualquier archivo requerido.
- Hay claims prohibidos.
- El comprador espera resultados financieros.
- El soporte requerido ya corresponde a `Setup Assist`.

## Comando recomendado

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\template_pack_1_delivery.py `
  --customer-email cliente@example.com `
  --order-id ORDER-TP1-001 `
  --confirm-buyer-onboarding-gate-go `
  --confirm-addon-order-confirmed `
  --confirm-pack-zip-ready `
  --confirm-readme-included `
  --confirm-profiles-validated `
  --confirm-support-boundaries-included `
  --confirm-safe-claims-reviewed `
  --package
```

La evidencia y el ZIP generado se guardan en `backend/sqx-edge-tool/data/template_pack_1_delivery` y no deben viajar dentro del ZIP base de SQX Edge.

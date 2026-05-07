# Buyer-Ready Checkout Release Closeout

Este cierre deja una venta controlada preparada para una persona de nivel basico: descarga, descomprime, doble click, licencia, soporte y rollback.

## Datos minimos

- Feedback cohort M64 en `GO`.
- ZIP portable revisado o ruta de entrega confirmada.
- `START_SQX_EDGE.bat` y `STOP_SQX_EDGE.bat` comprobados.
- Flujo de licencia Pro listo para entrega manual firmada.
- Ruta de soporte visible y entendible.
- Copy de checkout y claims revisados.
- Rollback claro: pausar checkout, pausar webhook/worker y volver a fulfillment manual.

## Comando base

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\buyer_ready_checkout_closeout.py `
  --use-latest-feedback-cohort `
  --buyer-steps 6 `
  --release-channel "controlled_private_link" `
  --support-label "priority email support" `
  --decision keep_private_pilot `
  --closeout-notes "Buyer path reviewed: download, unzip, double click, license import, support and rollback are documented." `
  --confirm-feedback-cohort-go `
  --confirm-checkout-copy-reviewed `
  --confirm-portable-release-reviewed `
  --confirm-license-delivery-reviewed `
  --confirm-support-path-reviewed `
  --confirm-safe-claims-reviewed `
  --confirm-rollback-reviewed
```

## Reglas de decision

- `open_controlled_sales`: solo si todo esta revisado y el soporte/rollback estan operativos.
- `keep_private_pilot`: la ruta esta preparada, pero el trafico sigue limitado.
- `iterate_buyer_pack`: hay que mejorar copy, onboarding, soporte o entrega.
- `pause_sales`: hay riesgo operativo, claims, soporte, licencia, refunds o release.

## Privacidad

No guardes emails completos de compradores, payloads de proveedor, claves privadas, licencias firmadas ni secretos. El closeout solo registra estado operativo agregado y notas sin datos personales.

# Monetization M32 - Render Staging Purchase Drill

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Ejecutar una prueba de compra staging completa contra Render: webhook Lemon demo, cola remota, dispatch del relay y evidencia posterior.

## Entregables

- Estado `relay_render_staging_purchase_drill_ready`.
- Tool `backend/sqx-edge-relay/tools/render_staging_purchase_drill.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-relay/data/render_staging_purchase_drill`.
- Consumo de ultimo apply gate M31 o fichero explicito.
- Envio opt-in de webhook demo con `--send-webhook`.
- Dispatch opt-in con `--dispatch`.
- Trazabilidad de `/relay/queue`, `/relay/webhook/lemon` y `/relay/dispatch`.
- Guia `docs/sales/RENDER_STAGING_PURCHASE_DRILL.md`.

## Decision

La prueba mutante exige flags explicitos. Sin `--send-webhook` y `--dispatch`, el resultado queda `NO-GO` para evitar contaminar staging por accidente.

## Uso

```powershell
python backend\sqx-edge-relay\tools\render_staging_purchase_drill.py --use-latest-apply-gate --base-url https://tu-relay-staging.onrender.com --send-webhook --dispatch
```

Variables esperadas en entorno local:

```text
SQX_RELAY_OPERATOR_TOKEN=...
SQX_LEMON_WEBHOOK_SECRET=...
```

## Siguiente Paso

M33 debe preparar el paso de conexion real de checkout: checklist de Lemon Squeezy, URLs definitivas, variantes y criterio de rollback antes de venta publica.

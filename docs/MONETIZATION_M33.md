# Monetization M33 - Checkout Live Readiness

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar la conexion real de checkout validando Lemon Squeezy, URLs definitivas, variantes, soporte, evidencia staging y plan de rollback antes de venta publica.

## Entregables

- Estado `checkout_live_readiness_ready`.
- Tool `backend/sqx-edge-tool/tools/checkout_live_readiness.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/checkout_live_readiness`.
- Validacion de checkout HTTPS.
- Validacion de `providerVariantId` para `pro_monthly`, `pro_annual` y `setup_assist`.
- Validacion de email de soporte.
- Consumo de evidencia M32 `render_staging_purchase_drill`.
- Checklist de rollback.
- Guia `docs/sales/CHECKOUT_LIVE_READINESS.md`.

## Decision

M33 no publica enlaces ni activa webhooks. La fase bloquea si faltan URLs reales, variantes, email de soporte o evidencia staging `GO`.

## Uso

```powershell
python backend\sqx-edge-tool\tools\checkout_live_readiness.py --relay-base-url https://tu-relay.onrender.com --support-email soporte@tu-dominio.com --use-latest-purchase-drill
```

Revision seca sin evidencia GO:

```powershell
python backend\sqx-edge-tool\tools\checkout_live_readiness.py --allow-no-go-purchase-drill --no-write
```

## Siguiente Paso

M34 debe preparar la publicacion controlada: actualizar URLs reales, crear release candidate comercial y ejecutar una compra piloto con licencia emitida.

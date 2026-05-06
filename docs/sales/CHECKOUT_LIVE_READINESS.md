# Checkout Live Readiness

Este runbook valida si SQX Edge esta listo para publicar checkout real.

## Requisitos

- M32 `Render Staging Purchase Drill` en `GO`.
- URL publica HTTPS del relay.
- Checkout URL real de Lemon Squeezy.
- `providerVariantId` real para cada plan.
- Email de soporte operativo.
- ZIP portable final validado.

## Ejecutar readiness

```powershell
python backend\sqx-edge-tool\tools\checkout_live_readiness.py --relay-base-url https://tu-relay.onrender.com --support-email soporte@tu-dominio.com --use-latest-purchase-drill
```

La herramienta valida:

- `primaryUrl` HTTPS.
- URL de webhook `/relay/webhook/lemon`.
- `providerVariantId` de `pro_monthly`, `pro_annual` y `setup_assist`.
- Email de soporte.
- Evidencia M32.
- Plan de rollback.

## Bloqueos esperados hasta configurar Lemon

Es normal ver `NO-GO` mientras falten:

- `primary_checkout_url_missing_or_not_https`
- `pro_monthly_provider_variant_id_missing`
- `pro_annual_provider_variant_id_missing`
- `setup_assist_provider_variant_id_missing`
- `support_email_missing_or_invalid`

## Rollback

Si una venta real falla:

- Despublica o desactiva los checkout links.
- Pausa el webhook Lemon hacia `/relay/webhook/lemon`.
- Pausa el worker del relay.
- Revisa `/relay/queue` y reintenta manualmente lo necesario.
- Vuelve a entrega manual firmada hasta resolver la causa.
- Rota `SQX_LEMON_WEBHOOK_SECRET` si hubo exposicion.

No conectes el webhook real ni publiques los enlaces hasta que esta compuerta devuelva `GO`.

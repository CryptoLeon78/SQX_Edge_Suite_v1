# Limited Public Launch

Este runbook abre una venta publica pequena y controlada solo cuando el piloto ya esta probado.

## Requisitos

- `pilot_purchase_kit.py` en `GO`.
- ZIP portable final validado.
- Checkout HTTPS real configurado.
- Variant IDs reales para `pro_monthly`, `pro_annual` y `setup_assist`.
- Email de soporte operativo.
- Bandeja de soporte revisada y lista.
- Responsable de rollback disponible durante la ventana.
- First sale cap recomendado: `5`.

## Dry Run

```powershell
python backend\sqx-edge-tool\tools\limited_public_launch.py --allow-no-go-pilot --no-write
```

Bloqueos esperados hasta completar la operativa real:

- `pilot_purchase_kit_missing` o `pilot_purchase_kit_not_go`
- `primary_checkout_url_missing_or_not_https`
- `provider_variant_missing_pro_monthly`
- `provider_variant_missing_pro_annual`
- `provider_variant_missing_setup_assist`
- `support_email_missing_or_invalid`
- `launch_window_missing`
- `rollback_owner_missing`
- `public_checkout_not_confirmed`
- `support_inbox_not_confirmed`

## Flujo Real

1. Configurar checkout publico limitado.
2. Mantener first sale cap en `5` hasta revisar soporte.
3. Ejecutar:

```powershell
python backend\sqx-edge-tool\tools\limited_public_launch.py --use-latest-pilot-kit --support-email soporte@example.com --first-sale-cap 5 --launch-window "2026-05-07 10:00-14:00 Europe/Madrid" --rollback-owner "Ivan" --confirm-public-checkout --confirm-support-inbox
```

4. Publicar solo el enlace limitado.
5. Vigilar Lemon/Gumroad, Render relay, cola local y support inbox.
6. Confirmar primera activacion Pro real.
7. Registrar order id, license id, ZIP SHA256 y resultado de soporte.

## Criterios GO

- Piloto M35 en `GO`.
- Checkout primario HTTPS.
- Variantes reales configuradas.
- Support inbox confirmado.
- First sale cap entre `1` y `25`, recomendado `5`.
- Ventana de lanzamiento definida.
- Rollback owner definido.
- Checkout publico confirmado.

## Rollback

- Despublicar o pausar checkout.
- Pausar webhook Lemon si los eventos duplican o fallan.
- Pausar worker Render si el dispatch falla repetidamente.
- Cambiar a fulfillment manual para clientes pagados.
- Reembolsar si no se puede entregar dentro del SLA de soporte.

No escales a venta abierta hasta revisar las primeras ventas y activaciones.

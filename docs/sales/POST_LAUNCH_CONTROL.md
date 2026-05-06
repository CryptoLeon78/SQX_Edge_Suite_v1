# Post Launch Control

Este runbook convierte las primeras ventas en una decision operativa auditable.

## Requisitos

- `limited_public_launch.py` en `GO`.
- ZIP portable final identificado.
- Ventas pagadas revisadas.
- Activaciones Pro confirmadas.
- Support tickets clasificados.
- Refunds y fallos de fulfillment revisados.
- Decision owner disponible.
- Ventana de revision definida.

## Dry Run

```powershell
python backend\sqx-edge-tool\tools\post_launch_control.py --allow-no-go-launch --no-write
```

Bloqueos esperados hasta tener ventas reales:

- `limited_public_launch_missing` o `limited_public_launch_not_go`
- `no_paid_sales_recorded`
- `post_launch_metrics_missing`
- `activations_below_paid_sales`
- `unresolved_support_tickets`
- `failed_fulfillment_present`
- `review_window_missing`
- `decision_owner_missing`
- `metrics_not_reviewed`
- `support_sla_not_confirmed`

## Flujo Real

1. Contar ventas pagadas.
2. Confirmar activaciones Pro importadas correctamente.
3. Contar support tickets y tickets sin resolver.
4. Revisar refunds y fallos de fulfillment.
5. Elegir decision:

- `continue_limited`: seguir con limite de ventas.
- `scale_public`: abrir mas visibilidad.
- `pause_sales`: pausar checkout y corregir.
- `rollback`: cerrar venta y volver a fulfillment manual o refund.

6. Ejecutar:

```powershell
python backend\sqx-edge-tool\tools\post_launch_control.py --use-latest-limited-launch --sales-count 5 --activation-count 5 --support-ticket-count 1 --unresolved-ticket-count 0 --refund-count 0 --failed-fulfillment-count 0 --review-window "2026-05-07 18:00 Europe/Madrid" --decision-owner "Ivan" --scale-decision continue_limited --confirm-metrics-reviewed --confirm-support-sla
```

## Criterios GO

- M36 en `GO`.
- Al menos una venta pagada.
- Activaciones cubren ventas no reembolsadas.
- Cero support tickets sin resolver.
- Cero fallos de fulfillment.
- Refund rate dentro de tolerancia.
- Metricas revisadas.
- SLA de soporte confirmado.

## Reglas De Escalado

- `scale_public` solo con al menos 3 ventas, cero tickets sin resolver y cero fallos de fulfillment.
- `continue_limited` si la venta funciona pero soporte aun necesita mas datos.
- `pause_sales` si hay friccion de activacion, entrega o soporte.
- `rollback` si no se puede entregar de forma fiable a clientes pagados.

No escales por entusiasmo; escala por evidencia.

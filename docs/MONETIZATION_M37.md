# Monetization M37 - Post Launch Control

Fecha: 2026-05-06

Estado: Done.

## Objetivo

Preparar el control posterior al lanzamiento limitado: ventas reales, activaciones, support tickets, refunds, fallos de fulfillment y decision de escalar, continuar limitado, pausar o hacer rollback.

## Entregables

- Estado `post_launch_control_ready`.
- Tool `backend/sqx-edge-tool/tools/post_launch_control.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/post_launch_control`.
- Consumo de evidencia M36 `limited_public_launch`.
- Validacion de ventas pagadas, activaciones, tickets, refunds, fallos de fulfillment, review window y decision owner.
- Decisiones permitidas: `continue_limited`, `scale_public`, `pause_sales`, `rollback`.
- Guia `docs/sales/POST_LAUNCH_CONTROL.md`.

## Decision

M37 no permite escalar a venta publica si hay activaciones pendientes, support tickets sin resolver, fallos de fulfillment o metricas sin revisar.

## Uso

```powershell
python backend\sqx-edge-tool\tools\post_launch_control.py --use-latest-limited-launch --sales-count 5 --activation-count 5 --support-ticket-count 1 --unresolved-ticket-count 0 --refund-count 0 --failed-fulfillment-count 0 --review-window "2026-05-07 18:00 Europe/Madrid" --decision-owner "Ivan" --scale-decision continue_limited --confirm-metrics-reviewed --confirm-support-sla
```

Revision seca:

```powershell
python backend\sqx-edge-tool\tools\post_launch_control.py --allow-no-go-launch --no-write
```

## Siguiente Paso

M38 debe preparar el sistema de feedback comercial: clasificacion de incidencias, versionado de mejoras y decision de precio/copy antes de escalar mas.

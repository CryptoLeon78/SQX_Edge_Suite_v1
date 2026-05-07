# Post Release Monitor

Este runbook convierte las primeras horas posteriores a una release visible en una decision operativa: mantener, pausar, hotfix, rollback o `scale_public`.

## Requisitos

- `release_publication_record.py` en `GO`.
- Descargas revisadas.
- Ventas revisadas.
- Activaciones revisadas.
- Tickets de soporte triados.
- Incidencias severas revisadas.
- Errores de activacion revisados.
- Refunds revisados.
- Fallos de fulfillment revisados.
- Rollback disponible.
- Ruta de hotfix disponible.

## Dry Run

```powershell
python backend\sqx-edge-tool\tools\post_release_monitor.py --allow-no-go-publication --no-write
```

Bloqueos esperados hasta tener evidencia real:

- `release_publication_record_missing` o `release_publication_record_not_go`
- `post_release_decision_missing_or_invalid`
- `support_not_triaged`
- `support_tickets_open`
- `severe_incidents_open`
- `activation_error_rate_high`
- `refund_rate_high`
- `fulfillment_failures_open`
- `rollback_not_available`
- `hotfix_path_not_ready`

## Flujo Real

```powershell
python backend\sqx-edge-tool\tools\post_release_monitor.py --use-latest-release-publication-record --downloads 25 --paid-sales 3 --activations 3 --support-tickets-open 0 --severe-incidents-open 0 --activation-errors 0 --refunds 0 --fulfillment-failures-open 0 --hours-since-release 24 --decision maintain_public --decision-owner "Ivan" --confirm-support-triaged --confirm-rollback-available --confirm-hotfix-path-ready
```

Para escalar:

```powershell
python backend\sqx-edge-tool\tools\post_release_monitor.py --use-latest-release-publication-record --downloads 100 --paid-sales 5 --activations 5 --hours-since-release 48 --decision scale_public --decision-owner "Ivan" --confirm-support-triaged --confirm-rollback-available --confirm-hotfix-path-ready
```

## Acciones Permitidas

- `maintain_public`: mantener la release visible.
- `pause_public`: pausar difusion o checkout.
- `hotfix_required`: preparar fix sin rollback completo.
- `rollback`: retirar release o volver a paquete anterior.
- `scale_public`: ampliar difusion solo con senales suficientes.

No escales si no puedes explicar activaciones, tickets, refunds y rollback con datos concretos.

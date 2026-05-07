# Monetization M43 - Post Release Monitor

Fecha: 2026-05-07

Estado: Done.

## Objetivo

Preparar monitorizacion post-release para decidir mantener, pausar, lanzar hotfix, rollback o `scale_public` despues de una publicacion visible.

## Entregables

- Estado `post_release_monitor_ready`.
- Tool `backend/sqx-edge-tool/tools/post_release_monitor.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/post_release_monitor`.
- Consumo de evidencia M42 `release_publication_record`.
- Validacion de descargas, ventas, activaciones, tickets, incidencias, refunds, fulfillment failures, `activation_error_rate_high`, soporte, hotfix y rollback.
- Guia `docs/sales/POST_RELEASE_MONITOR.md`.

## Decision

M43 no declara `GO` si quedan incidencias severas, tickets sin triaje, fallos de activacion altos, refunds altos, fulfillment fallido o rollback no disponible.

## Uso

```powershell
python backend\sqx-edge-tool\tools\post_release_monitor.py --use-latest-release-publication-record --downloads 25 --paid-sales 3 --activations 3 --hours-since-release 24 --decision maintain_public --decision-owner "Ivan" --confirm-support-triaged --confirm-rollback-available --confirm-hotfix-path-ready
```

Revision seca:

```powershell
python backend\sqx-edge-tool\tools\post_release_monitor.py --allow-no-go-publication --no-write
```

## Siguiente Paso

M44 debe preparar el ciclo de hotfix/rollback release: paquete de decision, notas de hotfix, rollback checklist y evidencia de cierre.

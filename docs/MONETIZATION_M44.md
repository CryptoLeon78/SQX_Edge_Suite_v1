# Monetization M44 - Hotfix Rollback Release

Fecha: 2026-05-07

Estado: Done.

## Objetivo

Preparar el ciclo de hotfix/rollback release despues de una senal post-release: accion, owner, notas, comunicacion, verificacion y cierre.

## Entregables

- Estado `hotfix_rollback_release_ready`.
- Tool `backend/sqx-edge-tool/tools/hotfix_rollback_release.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/hotfix_rollback_release`.
- Consumo de evidencia M43 `post_release_monitor`.
- Validacion de accion `close_no_action`, `pause_and_watch`, `hotfix` o `rollback`.
- Bloqueos para `rollback_target_missing`, `hotfix_notes_missing`, `customer_comms_not_ready`, soporte, verificacion y evidencia de cierre.
- Guia `docs/sales/HOTFIX_ROLLBACK_RELEASE.md`.

## Decision

M44 no declara `GO` si no hay owner, referencia de incidente cuando aplica, notas de hotfix/rollback, comunicacion a clientes, macro de soporte, plan de verificacion y evidencia de cierre.

## Uso

```powershell
python backend\sqx-edge-tool\tools\hotfix_rollback_release.py --use-latest-post-release-monitor --action hotfix --action-owner "Ivan" --incident-id INC-001 --hotfix-version v1.0.1 --post-action-decision monitor --confirm-hotfix-notes-ready --confirm-customer-comms-ready --confirm-support-macro-ready --confirm-verification-plan-ready --confirm-release-package-ready --confirm-closure-evidence-ready
```

Rollback:

```powershell
python backend\sqx-edge-tool\tools\hotfix_rollback_release.py --use-latest-post-release-monitor --action rollback --action-owner "Ivan" --incident-id INC-001 --rollback-target v1.0.0 --post-action-decision close --confirm-rollback-checklist-ready --confirm-customer-comms-ready --confirm-support-macro-ready --confirm-verification-plan-ready --confirm-closure-evidence-ready
```

Revision seca:

```powershell
python backend\sqx-edge-tool\tools\hotfix_rollback_release.py --allow-no-go-monitor --no-write
```

## Siguiente Paso

M45 debe preparar customer success/renewal loop: seguimiento de clientes Pro, renovaciones, plantillas, soporte prioritario y oportunidades de upsell sin promesas financieras.

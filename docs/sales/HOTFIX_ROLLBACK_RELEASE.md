# Hotfix Rollback Release

Este runbook evita improvisar cuando una release necesita pausarse, corregirse o retirarse.

## Requisitos

- `post_release_monitor.py` revisado.
- Accion elegida: `close_no_action`, `pause_and_watch`, `hotfix` o `rollback`.
- Owner asignado.
- Referencia de incidente cuando aplica.
- Notas de hotfix si hay hotfix.
- Target de rollback si hay rollback.
- Comunicacion a clientes preparada.
- Macro de soporte preparada.
- Plan de verificacion preparado.
- Evidencia de cierre preparada.

## Dry Run

```powershell
python backend\sqx-edge-tool\tools\hotfix_rollback_release.py --allow-no-go-monitor --no-write
```

Bloqueos esperados hasta tener decision real:

- `post_release_monitor_missing` o `post_release_monitor_not_go`
- `hotfix_rollback_action_missing_or_invalid`
- `action_owner_missing`
- `incident_reference_missing`
- `hotfix_notes_missing`
- `rollback_target_missing`
- `customer_comms_not_ready`
- `support_macro_not_ready`
- `verification_plan_not_ready`
- `closure_evidence_not_ready`

## Hotfix

```powershell
python backend\sqx-edge-tool\tools\hotfix_rollback_release.py --use-latest-post-release-monitor --action hotfix --action-owner "Ivan" --incident-id INC-001 --hotfix-version v1.0.1 --post-action-decision monitor --confirm-hotfix-notes-ready --confirm-customer-comms-ready --confirm-support-macro-ready --confirm-verification-plan-ready --confirm-release-package-ready --confirm-closure-evidence-ready
```

## Rollback

```powershell
python backend\sqx-edge-tool\tools\hotfix_rollback_release.py --use-latest-post-release-monitor --action rollback --action-owner "Ivan" --incident-id INC-001 --rollback-target v1.0.0 --post-action-decision close --confirm-rollback-checklist-ready --confirm-customer-comms-ready --confirm-support-macro-ready --confirm-verification-plan-ready --confirm-closure-evidence-ready
```

## Cierre

- Registrar accion ejecutada.
- Guardar evidencia JSON/Markdown.
- Actualizar notas de release o hotfix.
- Avisar a clientes afectados.
- Mantener soporte atento hasta confirmar que no reaparecen incidencias.

No cierres una incidencia comercial sin dejar una prueba repetible de que el usuario basico queda protegido.

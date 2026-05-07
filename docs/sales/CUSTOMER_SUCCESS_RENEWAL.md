# Customer Success Renewal

Este runbook convierte una venta Pro en una relacion operativa: activacion, primer valor, soporte, renovacion y expansion responsable.

## Requisitos

- `hotfix_rollback_release.py` revisado.
- Cliente identificado por `customer_id` o email.
- Plan registrado: `pro_monthly`, `pro_annual` o `setup_assist`.
- Owner de customer success asignado.
- Onboarding checklist listo.
- Activacion Pro confirmada.
- Soporte triado y sin tickets abiertos para declarar `GO`.
- Check-ins de valor registrados.
- Contacto de renovacion preparado si la renovacion esta cerca.
- Notas de exito y claims seguros revisados.
- Oferta preparada si se propone `upsell_templates` u `offer_setup_assist`.

## Dry Run

```powershell
python backend\sqx-edge-tool\tools\customer_success_renewal.py --allow-no-go-hotfix --no-write
```

Bloqueos esperados hasta tener evidencia real:

- `hotfix_rollback_release_missing` o `hotfix_rollback_release_not_go`
- `customer_reference_missing`
- `plan_missing_or_invalid`
- `success_owner_missing`
- `customer_success_decision_missing_or_invalid`
- `onboarding_checklist_not_ready`
- `activation_not_confirmed`
- `support_not_triaged`
- `support_tickets_open`
- `activation_errors_open`
- `renewal_contact_not_ready`
- `success_notes_missing`
- `safe_claims_not_reviewed`
- `template_pack_offer_not_ready`
- `setup_assist_offer_not_ready`

## Renewal Review

```powershell
python backend\sqx-edge-tool\tools\customer_success_renewal.py --use-latest-hotfix-rollback-release --customer-id CUST-001 --customer-email buyer@example.com --plan pro_monthly --success-owner "Ivan" --decision renew --days-to-renewal 10 --value-checkins-completed 2 --confirm-onboarding-checklist-ready --confirm-activation-confirmed --confirm-support-triaged --confirm-renewal-contact-ready --confirm-success-notes-ready --confirm-safe-claims-reviewed
```

## Expansion Review

```powershell
python backend\sqx-edge-tool\tools\customer_success_renewal.py --use-latest-hotfix-rollback-release --customer-id CUST-001 --plan pro_annual --success-owner "Ivan" --decision upsell_templates --days-to-renewal 25 --value-checkins-completed 2 --confirm-onboarding-checklist-ready --confirm-activation-confirmed --confirm-support-triaged --confirm-renewal-contact-ready --confirm-success-notes-ready --confirm-safe-claims-reviewed --confirm-template-pack-offer-ready
```

## Decision

- `maintain_pro`: mantener cliente activo sin cambio comercial.
- `renew`: preparar renovacion mensual/anual.
- `upsell_templates`: ofrecer pack de plantillas solo con oferta preparada.
- `offer_setup_assist`: ofrecer servicio guiado si hay friccion de setup.
- `improve_onboarding`: mejorar docs, instrucciones o primer uso antes de vender mas.
- `pause_or_refund_review`: revisar riesgo de refund, pausa o excepcion de soporte.

No uses esta fase para prometer rendimiento financiero. Sirve para medir activacion, soporte, friccion, retencion y oportunidades responsables.

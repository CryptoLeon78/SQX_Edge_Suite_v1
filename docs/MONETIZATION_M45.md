# Monetization M45 - Customer Success Renewal Loop

Fecha: 2026-05-07

Estado: Done.

## Objetivo

Preparar el seguimiento de usuarios Pro despues de compra, activacion y soporte para mejorar retencion, detectar bloqueos y decidir renovacion o expansion sin prometer resultados financieros.

## Entregables

- Estado `customer_success_renewal_ready`.
- Tool `backend/sqx-edge-tool/tools/customer_success_renewal.py`.
- Evidencia JSON/Markdown en `backend/sqx-edge-tool/data/customer_success_renewal`.
- Consumo de evidencia M44 `hotfix_rollback_release`.
- Validacion de cliente, plan, owner, onboarding, activacion, soporte, check-ins de valor, renovacion y claims seguros.
- Bloqueos para `customer_reference_missing`, `activation_not_confirmed`, `support_tickets_open`, `renewal_contact_not_ready`, `safe_claims_not_reviewed` y ofertas de expansion sin preparar.
- Guia `docs/sales/CUSTOMER_SUCCESS_RENEWAL.md`.

## Decision

M45 no declara `GO` si no hay cliente identificado, owner, onboarding, activacion, soporte triado, notas de exito, claims seguros y decision de renovacion/expansion registrada. Las oportunidades de upsell requieren oferta preparada y senales de valor suficientes.

## Uso

```powershell
python backend\sqx-edge-tool\tools\customer_success_renewal.py --use-latest-hotfix-rollback-release --customer-id CUST-001 --customer-email buyer@example.com --plan pro_monthly --success-owner "Ivan" --decision renew --days-to-renewal 10 --value-checkins-completed 2 --confirm-onboarding-checklist-ready --confirm-activation-confirmed --confirm-support-triaged --confirm-renewal-contact-ready --confirm-success-notes-ready --confirm-safe-claims-reviewed
```

Oferta de plantillas:

```powershell
python backend\sqx-edge-tool\tools\customer_success_renewal.py --use-latest-hotfix-rollback-release --customer-id CUST-001 --plan pro_annual --success-owner "Ivan" --decision upsell_templates --days-to-renewal 25 --value-checkins-completed 2 --confirm-onboarding-checklist-ready --confirm-activation-confirmed --confirm-support-triaged --confirm-renewal-contact-ready --confirm-success-notes-ready --confirm-safe-claims-reviewed --confirm-template-pack-offer-ready
```

Revision seca:

```powershell
python backend\sqx-edge-tool\tools\customer_success_renewal.py --allow-no-go-hotfix --no-write
```

## Siguiente Paso

M46 podria convertir esta evidencia en un cockpit comercial ligero: cartera de clientes, renovaciones proximas, tickets abiertos, oportunidades de plantillas y decisiones de soporte.

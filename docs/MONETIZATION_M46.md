# Monetization M46 - Commercial Customer Cockpit

Fecha: 2026-05-07

Estado: Done.

## Objetivo

Crear un cockpit comercial interno, ligero y redactado para revisar usuarios Pro, renovaciones, soporte, activacion y oportunidades de expansion sin convertir SQX Edge en un CRM pesado.

## Entregables

- Estado `customer_cockpit_ready`.
- Endpoint read-only `GET /api/customer-cockpit`.
- Agregador `backend/sqx-edge-tool/core/customer_cockpit.py`.
- Configuracion `backend/sqx-edge-tool/config/customer_cockpit.json`.
- Modulo frontend `app/js/modules/customer-cockpit.js`.
- Panel `Customer Success` en Inicio.
- Contratos JS, tests backend/staticos y E2E con capturas.

## Decision

M46 solo muestra resumen operativo redactado:

- Cliente como referencia segura, no payload completo.
- Plan, owner, renovacion, tickets, activacion, decision y oportunidad.
- Sin licencia JSON, claves privadas, eventos checkout crudos, relay secrets ni archivos de entrega.

## Uso

1. Genera evidencia con `customer_success_renewal.py`.
2. Abre Inicio.
3. Pulsa `Actualizar` en `Customer Success`.
4. Revisa clientes, renovaciones, tickets y oportunidades.

Si no hay evidencia, el cockpit muestra estado vacio y queda preparado para datos reales.

## Siguiente Paso

M47 debe endurecer onboarding y soporte para comprador basico: descarga, instalacion, activacion de licencia, FAQ, macro de soporte, SLA realista y criterio de pausa/refund.

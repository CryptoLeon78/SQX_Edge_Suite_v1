# Customer Cockpit

El cockpit comercial es una vista interna para revisar usuarios Pro sin exponer datos sensibles.

## Fuente De Datos

- Evidencia local `backend/sqx-edge-tool/data/customer_success_renewal/customer_success_renewal_*.json`.
- Configuracion segura `backend/sqx-edge-tool/config/customer_cockpit.json`.
- Endpoint read-only `GET /api/customer-cockpit`.

## Datos Permitidos

- Referencia de cliente redactada.
- Plan Pro.
- Owner de customer success.
- Activacion confirmada o pendiente.
- Dias hasta renovacion.
- Tickets abiertos y errores de activacion.
- Riesgo de refund agregado.
- Decision: renovar, mantener, mejorar onboarding, plantillas, Setup Assist o revisar pausa/refund.

## Datos Prohibidos

- Payload de licencia.
- Private keys.
- Eventos checkout crudos.
- Secretos del relay.
- Archivos de entrega al cliente.

## Operacion

1. Revisar cockpit antes de contactar renovacion.
2. Resolver activaciones o tickets antes de proponer upsell.
3. Ofrecer plantillas o Setup Assist solo si hay valor observado.
4. Mantener claims seguros: productividad, orden, trazabilidad y reduccion de errores operativos.

No usar esta vista para prometer resultados financieros.

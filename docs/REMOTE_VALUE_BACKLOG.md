# REMOTE VALUE BACKLOG

Este backlog memoriza ideas de valor que pueden avanzar mientras REMOTE-8C observa al primer usuario. No ejecuta expansion, no crea usuarios, no toca grants y no sustituye las gates REMOTE.

## WAIT-1 - Welcome + Trust Center

Estado: completado en WAIT-1.

Objetivo:

- Suavizar el primer impacto tras Cloudflare Access con una pantalla puente de bienvenida.
- Explicar identidad, permiso, sesion de app, workspace, seguridad y privacidad antes de operar.
- Mostrar un Trust Center honesto, con autoevaluaciones SQX y evidencias reales o planificadas.

Decisiones fijadas:

- No crear empresa auditora ficticia.
- No emitir certificados como si fueran externos.
- No prometer seguridad absoluta.
- Usar lenguaje de controles, evidencia, autoevaluacion y auditorias externas pendientes o futuras.

Artefactos previstos:

- SQX Edge Suite Security Self-Assessment.
- Privacy & Data Handling Statement.
- Remote Service Safety Checklist.
- Evidencias REMOTE redacted.
- Futuras comprobaciones: MDN HTTP Observatory, OWASP ZAP Baseline y revisiones de headers reales.

## WAIT-2 - Welcome Direct Tester Access + Operational Cadence

Estado: completado en WAIT-2.

Objetivo:

- Hacer que el tester aprobado pase de Cloudflare Access a la app sin introducir una segunda clave tester en la pantalla de bienvenida.
- Mostrar `OK todo validado` y un CTA protagonista `Acceso DASHBOARD`.
- Añadir copy de valor: productividad, estructura, trazabilidad y reduccion de errores operativos, sin prometer rentabilidad.
- Formalizar que cada mensaje operativo incluya estado y siguiente sugerencia cuando aporte claridad.
- Registrar nuevos agentes: I+D / Research Scout, Web & RRSS Creative, Sales & Commercial y Asset Cards Curator.

Limites:

- No ampliar testers.
- No crear nuevos grants.
- No publicar checkout ni URLs nuevas.
- No cambiar tarjetas de activos sin confirmacion explicita del operador.

## WAIT-4 - Trust Evidence Pack

Estado: completado en WAIT-4.

Objetivo:

- Convertir el Trust Center en un paquete de evidencias claro para comprador Pro y tester.
- Mostrar self-assessment, privacy statement, safety checklist y escaneos externos planificados.
- Separar lo implementado de lo pendiente sin fingir certificaciones externas.

Artefactos:

- `docs/WAIT4_TRUST_EVIDENCE_PACK.md`.
- Bloque `Evidence Pack` en la pantalla Welcome / Trust.
- Contratos estaticos para impedir claims falsos.

## WAIT-5 - Onboarding Comercial Y Primera Sesion Pro

Estado: completado en WAIT-5.

Objetivo:

- Hacer que el primer impacto del usuario aprobado se sienta Pro, claro y comercial sin tocar permisos ni cohortes.
- Explicar SQX Edge Suite como plataforma para ordenar el flujo StrategyQuant X: Workflow, Mining Control, SQX Views, Project Generator, Template Maker, Strategy Control y Champion vs Challenger.
- Añadir una guia `Primeros 10 minutos` dentro del dashboard para orientar al comprador/tester sin crear nuevos tabs.
- Mantener REMOTE-8C como gate de observacion antes de ampliar usuarios.

Decisiones fijadas:

- Tono comercial fuerte, pero honesto.
- Superficie: Welcome + Dashboard.
- CTA principal: `Acceso DASHBOARD`.
- Early Access Pro no crea checkout, no crea grants y no amplia testers.

Artefactos:

- `docs/WAIT5_ONBOARDING_POLISH.md`.
- Bloque `Primera sesión Pro` en Welcome.
- Panel `Primeros 10 minutos` en Control Panel / Inicio.
- `Commercial Onboarding Claims Gate` en gobernanza.

## Ideas Pendientes

- Generar PDFs internos de autoevaluacion para compradores Pro sin fingir emisor tercero.
- Crear una vista de soporte para copiar un resumen redacted del estado remoto.
- Mejorar mensajes de error de sesion, entitlement, workspace y revocacion.
- Preparar copy comercial para early access, compradores fundadores y soporte opcional.
- Definir una auditoria externa real futura si el producto pasa de piloto a venta activa.

## Reglas De Seguridad Comercial

- Las afirmaciones comerciales deben centrarse en productividad, metodologia, trazabilidad y reduccion de errores operativos.
- Las afirmaciones de seguridad deben ser verificables: control implementado, evidencia local redacted o auditoria externa real.
- Cualquier documento con apariencia de certificado debe indicar si es autoevaluacion interna SQX o informe externo real.
- Las evidencias privadas permanecen en `.local/remote_service/` y nunca entran en Git.

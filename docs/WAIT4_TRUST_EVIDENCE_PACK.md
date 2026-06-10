# WAIT-4 - Trust Evidence Pack

## Summary

WAIT-4 convierte el Trust Center de bienvenida en un paquete de evidencias
honesto para compradores Pro y testers. No amplia usuarios, no crea grants, no
publica checkout y no toca Cloudflare Access. Su funcion es explicar que
controles existen, que evidencias internas tenemos, que queda pendiente y como
se prepararan futuras verificaciones externas reales.

## Public-Safe Scope

- Customer-facing canonical link: `https://sqxedgesuite.org/`.
- Protected app target: infraestructura interna detras de Cloudflare Access.
- Evidence posture: self-assessment SQX, privacy statement, safety checklist
  and planned external scans.
- Claims posture: no certificados ficticios, no auditor externo simulado, no
  promesas de riesgo cero y no promesas de rentabilidad.
- Explicit rule: No fake external certificate, no fake issuer and no simulated
  third-party audit.

## Evidence Pack

### SQX Edge Suite Security Self-Assessment

Estado: interno, public-safe summary.

Controles cubiertos:

- Cloudflare Access delante del dashboard protegido.
- Sesion de app con entitlement activo.
- Workspace aislado derivado del servidor.
- Control anti-comparticion por contexto aprobado.
- Revocacion, rate limit, kill switch y watermark remoto.
- Soporte con diagnostico redacted y almacenamiento local ignorado.

### Privacy & Data Handling Statement

Estado: interno, public-safe summary.

Declaracion:

- El usuario final trabaja por enlace y no instala dependencias locales.
- La app no debe mostrar rutas SQX internas, tokens, cookies, emails completos,
  IPs completas, Cloudflare IDs ni carpetas servidor.
- Las evidencias crudas viven en `.local/remote_service/` y nunca entran en Git.
- Los casos de soporte se guardan como referencias redacted.

### Remote Service Safety Checklist

Estado: operativo, ligado a gates REMOTE.

Checklist:

- Access anonimo bloqueado antes de mostrar dashboard.
- Acceso aprobado valida identidad y permiso.
- Sesion de app no se asume persistente despues de cerrar navegador.
- Workspace creado desde identidad validada.
- Generacion/export usa workspace del usuario.
- Incidencias abiertas bloquean expansion.
- REMOTE-8C debe cerrar ventana limpia antes de ampliar testers.

### External Evidence Preparation

Estado: pendiente/planificado.

Fuentes reales previstas:

- MDN HTTP Observatory: postura HTTP y headers.
- OWASP ZAP Baseline: escaneo pasivo/controlado.
- Revision manual de headers y rutas publicas/protegidas.

Regla: estas fuentes se mostraran como `planned` hasta que exista un resultado
real y redacted. No se etiquetaran como certificacion ni auditoria externa.

## UI Contract

El Trust Center de bienvenida debe mostrar:

- `Evidence Pack`.
- `Self-assessment`.
- `Privacy statement`.
- `Safety checklist`.
- `External scans planned`.
- Fecha de ultima revision.
- Frase explicita: `Sin certificados ficticios`.

## Governance Contract

WAIT-4 queda bajo:

- `Trust Claims Gate`.
- `Public Canonical Link Gate`.
- `Support Intake Gate`.
- `First User Observation Gate`.

## Next Route

Despues de WAIT-4, la siguiente fase segura mientras REMOTE-8C sigue abierta es
WAIT-5: pulir onboarding comercial y primera sesion, sin ampliar testers ni
crear grants.

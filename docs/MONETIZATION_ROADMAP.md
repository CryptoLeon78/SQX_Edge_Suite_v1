# SQX Edge Monetization Roadmap

Documento vivo para convertir SQX Edge Suite en una herramienta Pro comercial, con servicios y plantillas alrededor del producto.

## Decision Base

La estrategia elegida es vender:

- La aplicacion como herramienta Pro.
- Suscripcion mensual/anual como modelo principal.
- Soporte opcional como complemento.
- Servicios, plantillas y packs alrededor de la herramienta.

## Phase M1 - Monetization Model

Objetivo: definir que se vende, a quien, con que promesa y con que precios iniciales.

Entregables:

- Propuesta de valor.
- Segmentos de usuario.
- Planes Free/Pro.
- Pricing inicial recomendado.
- Servicios opcionales.
- Packs de plantillas/presets.
- Riesgos y validaciones antes de construir licencias.

Estado: Done.

## Phase M2 - Licensing And Access

Objetivo: definir como se activan funciones Pro sin romper el uso portable ni complicar al usuario basico.

Opciones a evaluar:

- Licencia local firmada.
- Activacion online opcional.
- Modo demo.
- Periodo trial.
- Renovacion mensual/anual.
- Limite por equipo.
- Recuperacion sencilla de licencia.

Recomendacion inicial: licencia local firmada con validacion offline, preparada para activacion online futura.

Estado: Done.

Decision M2:

- Licencia local firmada.
- Activacion manual por archivo en la primera version.
- Validacion offline para uso diario.
- 1 equipo por licencia con reset manual de soporte.
- Sin trial automatico inicial; demos mediante licencias temporales manuales.
- Enforcement real en backend para funciones Pro.
- Expiracion sin borrado de datos del usuario.

## Phase M3 - Distribution

Objetivo: preparar canales de entrega y venta.

Opciones:

- GitHub Releases para builds publicos.
- Lemon Squeezy, Gumroad o Stripe Payment Links para venta.
- ZIP portable actual como primer canal.
- Instalador Windows mas adelante.
- Pagina de descarga simple.

Recomendacion inicial: ZIP portable + Lemon Squeezy o Gumroad + GitHub Releases.

Estado: Done.

Decision M3:

- Lemon Squeezy como canal principal de cobro, suscripcion y licencia.
- ZIP portable como artefacto principal.
- GitHub Releases para builds publicos o controlados.
- Gumroad como alternativa para validar packs/plantillas.
- Stripe Payment Links solo si construimos fulfillment/licensing propio.
- Paddle como opcion futura si el producto escala.
- Primera beta de pago con entrega manual de licencia firmada.

## Phase M4 - Product Packaging

Objetivo: separar claramente funciones Free, Pro e internas.

Lineas de trabajo:

- Feature gating Free/Pro.
- Mensajes de upgrade.
- Pantalla de licencia.
- Modo demo.
- Ocultar herramientas internas del paquete final.
- Ajustar release checklist para builds Free/Pro.

Estado: Done.

Decision M4:

- `product_manifest.json` define producto, features, access levels y perfiles Free/Pro/Internal.
- Build actual queda como `internal` para no romper desarrollo.
- Backend expone estado de licencia y chequeo de feature flags.
- Frontend muestra panel de licencia en Inicio.
- Las licencias sin firma no activan Pro.
- Enforcement fuerte en endpoints queda preparado para M6.

## Phase M5 - Branding And Go-To-Market

Objetivo: preparar la app para ensenarla y venderla.

Entregables:

- Nombre comercial.
- Landing page.
- Capturas.
- Video demo corto.
- README comercial.
- Changelog publico.
- Roadmap publico.
- Casos de uso.

Estado: Done.

Decision M5:

- SQX Edge Pro queda como nombre comercial principal.
- El copy de upgrade vive en `product_manifest.json`.
- Inicio muestra un panel de licencia con valor Pro, bullets y precios.
- Se crean README comercial, roadmap publico y guion base de landing/demo.
- La comunicacion evita promesas financieras y vende productividad/trazabilidad.

## Phase M6 - Security And Distribution Audit

Objetivo: asegurar que el paquete comercial no expone archivos, endpoints o capacidades peligrosas.

Checklist:

- Archivos excluidos del ZIP.
- Configs locales.
- Rutas personales.
- Datos sensibles.
- Endpoints que abren carpetas o escriben archivos.
- Checksums de release.
- Versionado.
- Separacion dev/user.

Estado: Done.

Decision M6:

- La API queda con boundary local explicito (`local_api_only`) ademas de CORS local.
- Endpoints Pro de escritura aplican enforcement backend con `require_feature`.
- El ZIP portable excluye `config.json`, `config/license.json`, `.env`, backups, outputs, dev envs y release tooling interno.
- `audit_distribution.ps1` revisa paquete, genera reporte y checksum SHA256.
- `release_checklist.ps1` ejecuta la auditoria antes de validar el ZIP final.
- La firma criptografica real de licencias queda como riesgo residual para una fase posterior.

## Phase M7 - Support And Diagnostics

Objetivo: reducir friccion de soporte sin capturar datos sensibles.

Opciones:

- Boton generar diagnostico local.
- Logs exportables.
- Reporte sin estrategias ni rutas privadas por defecto.
- Consentimiento claro si algun dia hay telemetria.

Recomendacion inicial: diagnostico local exportable, sin telemetria automatica.

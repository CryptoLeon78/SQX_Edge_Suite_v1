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

Estado: Done.

Decision M7:

- Se crea `GET /api/support/diagnostics` con payload redacted.
- Inicio incluye boton `Generar diagnostico`.
- El JSON descargado excluye rutas personales, licencia, estrategias y localStorage.
- El diagnostico resume version, runtime, build, config checks, manifests y distribucion.
- La fase mantiene soporte manual sin telemetria automatica.

## Phase M8 - Offline Signed License Activation

Objetivo: activar SQX Edge Pro con licencia local firmada y verificacion offline.

Entregables:

- Verificacion RSA-SHA256 sin dependencias externas.
- Importacion de licencia firmada a `config/license.json`.
- Limpieza de licencia local.
- Estado `pro_active` cuando la licencia es valida.
- Rechazo de licencias manipuladas.
- Tool dev para firmar licencias fuera del ZIP.

Estado: Done.

Decision M8:

- El backend verifica `rsa_sha256_pkcs1_v1_5` (`RS256`) con public key en `product_manifest.json`.
- La private key queda fuera del repo y fuera del ZIP portable.
- `POST /api/license/import` instala solo licencias firmadas validas.
- `POST /api/license/clear` limpia la licencia local.
- Una licencia Pro valida habilita `project_generator.generate` y `strategy_cleaner.apply`.
- Una licencia expirada o manipulada no borra datos, pero vuelve a features Free.

## Phase M9 - Production License Key Management

Objetivo: preparar la gestion de claves para venta Pro sin exponer secretos en repo, backups ni ZIP portable.

Entregables:

- Tool local `license_keypair.ps1` para generar claves RSA compatibles con `license_signer.py`.
- Politica de clave privada fuera de git y fuera de paquetes.
- Exclusiones reforzadas en `.gitignore`, empaquetado, auditoria y release checklist.
- Manifiesto con `licensing.keyManagement`.
- Documentacion del flujo manual de emision de licencias.

Estado: Done.

Decision M9:

- La public key se distribuye en `product_manifest.json`.
- La private key se guarda solo en ubicacion privada local.
- Las herramientas internas de firma/generacion no viajan en el ZIP final.
- Antes de vender publicamente hay que reemplazar la public key placeholder por una clave de produccion real.

## Phase M10 - Manual Pro License Issuer

Objetivo: emitir licencias Pro firmadas con menos friccion y menos riesgo de error manual.

Entregables:

- Tool interno `license_issue.py`.
- Generacion de payload y firma en un solo comando.
- Campos comerciales: cliente, email, plan, pedido, fechas, soporte y limite de equipos.
- Exclusiones de ZIP/auditoria para el issuer y artefactos locales.
- Documentacion operativa para primeras ventas manuales.

Estado: Done.

Decision M10:

- El flujo manual recomendado pasa por `license_issue.py`.
- `license_signer.py` queda como primitiva tecnica de firma.
- El issuer queda fuera del paquete portable de cliente.
- La siguiente fase natural es conectar este flujo a fulfillment de venta o preparar pagina/checkout real.

## Phase M11 - Checkout And Manual Fulfillment

Objetivo: preparar checkout real y entrega manual segura para primeras ventas Pro.

Entregables:

- `upgrade.checkout` en `product_manifest.json`.
- Enlace de checkout preparado en el panel Licencia, oculto hasta tener URL real.
- Script interno `prepare_customer_delivery.ps1`.
- Runbook de ventas y entrega.
- Documentacion de setup Lemon Squeezy/Gumroad.

Estado: Done.

Decision M11:

- Lemon Squeezy queda como canal principal.
- Gumroad queda como fallback ligero.
- La licencia Pro real sigue siendo nuestro JSON firmado offline.
- El cliente recibe ZIP portable + licencia JSON + instrucciones.
- La siguiente fase natural es webhook/automatizacion de fulfillment.

## Phase M12 - Local Fulfillment Automation Bridge

Objetivo: preparar una automatizacion asistida para pasar de evento de checkout a entrega, sin exponer aun un endpoint publico.

Entregables:

- `fulfillment_request.py` para normalizar eventos de proveedor.
- `fulfill_from_request.ps1` para emitir licencia y preparar entrega.
- Politica de firma `X-Signature` + `HMAC SHA256`.
- Exclusion del ZIP para requests/eventos/tools internos.
- Documentacion operativa del puente de automatizacion.

Estado: Done.

Decision M12:

- La automatizacion inicial sera local y con cola asistida.
- Lemon Squeezy sigue siendo la fuente principal de eventos.
- Primero se guarda/verifica el evento; despues se normaliza; despues se cumple.
- La siguiente fase natural es un receiver privado con deduplicacion.

## Phase M13 - Private Receiver And Persistent Queue

Objetivo: habilitar un receiver privado local con persistencia y deduplicacion real de eventos.

Entregables:

- Receiver `POST /api/fulfillment/webhook/lemon`.
- Cola persistente de `events`, `requests` y `processed`.
- Deduplicacion por `provider_event_id`.
- Endpoints de listado, detalle y proceso.
- Documentacion operativa del receiver.

Estado: Done.

Decision M13:

- El receiver usa `SQX_LEMON_WEBHOOK_SECRET`.
- La cola sigue siendo local y privada.
- El operador conserva control manual del paso final de fulfillment.
- La siguiente fase natural es exponerlo de forma controlada con receiver privado/tunel y reintentos.

## Phase M14 - Operator States And Retry Cockpit

Objetivo: dar al operador una forma clara de revisar la cola, cambiar estados y reintentar fulfillment desde el propio dashboard.

Entregables:

- Estado operativo por request (`queued`, `needs_review`, `failed`, `completed`, `ignored`).
- Contador de intentos y ultimo error persistidos en cada request.
- Endpoint `POST /api/fulfillment/request-status`.
- Resumen de cola y receiver en `GET /api/fulfillment/requests`.
- Panel de fulfillment en Inicio para refrescar, ignorar, recolar y procesar.

Estado: Done.

Decision M14:

- El reintento sigue siendo manual y consciente, pero ahora queda trazado.
- El dashboard interno actua como queue cockpit ligero para operador.
- Los requests no se eliminan al fallar; conservan `attempt_count`, `last_error` y ultimo recibo.
- El siguiente paso natural es M15: receiver remoto controlado o integracion webhook segura hacia esta cola privada.

## Phase M15 - Trusted Relay Ingest

Objetivo: aceptar bundles firmados por un relay remoto controlado sin abrir directamente la API local a internet.

Entregables:

- `POST /api/fulfillment/relay-ingest`
- Secreto dedicado `SQX_FULFILLMENT_RELAY_SECRET`
- Header dedicado `X-SQX-Relay-Signature`
- Tool interna `relay_bundle.py`
- Exclusion del ZIP para `relay_event_*.json` y tooling del relay

Estado: Done.

Decision M15:

- El relay verifica Lemon fuera del backend local.
- El backend local solo confia en bundles firmados por el relay.
- La deduplicacion sigue ocurriendo por `provider_event_id`.
- La siguiente fase natural es M16: desplegar o disenar el relay remoto real con cola/reintentos propios.

## Phase M16 - Deployable Remote Relay Service

Objetivo: materializar el relay remoto dentro del repo como servicio separado y desplegable.

Entregables:

- Proyecto `backend/sqx-edge-relay`
- Cola remota con `pending`, `sent` y `failed`
- Endpoints de health, queue, dispatch y requeue
- Target configurable por `SQX_LOCAL_INGEST_URL`
- Exclusion del relay del ZIP portable final

Estado: Done.

Decision M16:

- El relay pasa a ser una pieza de infraestructura separada del producto portable.
- El relay conserva cola y reintentos propios antes del ingest local.
- El siguiente paso natural es M17: automatizar worker/scheduler del relay o elegir despliegue real.

## Phase M17 - Relay Deployment Hardening

Objetivo: preparar el relay para operar con mas seguridad y menos intervencion manual.

Entregables:

- Estado `relay_deployment_ready`.
- Endpoint `GET /relay/config-check`.
- Proteccion opcional de endpoints operativos con `SQX_RELAY_OPERATOR_TOKEN`.
- Plantilla `.env.example` para despliegue.
- Worker `dispatch_worker.py` y `run-worker.bat`.
- Documentacion de readiness y operacion supervisada.

Estado: Done.

Decision M17:

- Lemon Squeezy mantiene entrada publica por webhook firmado.
- Cola, detalle, dispatch y requeue quedan protegibles con token.
- El dispatch pasa a poder ejecutarse como `supervised_dispatch_loop`.
- El siguiente paso natural es M18: observabilidad, logs rotables y prueba E2E de fulfillment completo.

## Phase M18 - Relay Observability And Simulation

Objetivo: hacer observable el relay remoto y poder validar el flujo comercial sin eventos reales.

Entregables:

- Estado `relay_observability_ready`.
- Eventos JSONL en `data/observability/logs/relay_events.jsonl`.
- Snapshots de cola en `data/observability/snapshots`.
- Endpoints `GET /relay/observability` y `POST /relay/observability/snapshot`.
- Simulador `simulate_purchase_flow.py`.
- Contratos y tests del flujo webhook -> cola -> dispatch -> snapshot.

Estado: Done.

Decision M18:

- Los logs operativos se guardan en JSONL y redactan secretos.
- Los snapshots capturan cola, configuracion y eventos recientes.
- La simulacion permite validar compra -> relay -> ingest local sin depender de Lemon en vivo.
- El siguiente paso natural es M19: preparar despliegue real por proveedor y supervisor.

## Phase M19 - Production Relay Deployment Package

Objetivo: dejar el relay listo para decidir proveedor y desplegar con checks previos.

Entregables:

- Estado `relay_production_deploy_ready`.
- Dockerfile y `.dockerignore`.
- `deployment_check.py`.
- Plantillas Docker Compose, Render, Railway, Fly.io y systemd.
- Guia `RELAY_DEPLOYMENT_GUIDE.md`.
- Contratos y tests para archivos de despliegue y preflight.

Estado: Done.

Decision M19:

- Docker es la ruta principal de despliegue.
- Render/Railway/Fly.io/VPS quedan como caminos documentados con plantilla.
- Los secretos se validan por preflight y nunca se versionan.
- El siguiente paso natural es M20: staging real con proveedor elegido y webhook test.

## Phase M20 - Relay Staging Validation Kit

Objetivo: preparar validacion staging real antes de conectar ventas.

Entregables:

- Estado `relay_staging_ready`.
- `.env.staging.example`.
- `staging_smoke.py`.
- Checklist `RELAY_STAGING_CHECKLIST.md`.
- Tests para smoke remoto firmado.

Estado: Done.

Decision M20:

- El proveedor se elige en la siguiente fase operativa.
- El proyecto ya puede validar una URL staging con health, config, observability, snapshot y webhook firmado.
- El siguiente paso natural es M21: desplegar staging real en el proveedor elegido y capturar evidencia go/no-go.

## Phase M21 - Render Staging Execution Readiness

Objetivo: elegir proveedor recomendado y preparar evidencia go/no-go para staging real.

Entregables:

- Estado `relay_staging_execution_ready`.
- Render como proveedor recomendado para primer staging.
- `render.staging.yaml.example`.
- `staging_evidence.py`.
- Runbook `RELAY_RENDER_STAGING_RUNBOOK.md`.

Estado: Done.

Decision M21:

- Render queda como recomendacion principal para staging inicial.
- Sin URL staging real, la decision debe quedar en NO-GO.
- La evidencia se genera en JSON y Markdown para auditoria.
- El siguiente paso natural es ejecutar el deploy real en Render y adjuntar evidencia.

## Phase M22 - Render API Preflight

Objetivo: validar API key, owner/workspace y blueprint staging antes de crear recursos.

Entregables:

- Estado `relay_render_api_preflight_ready`.
- `render_api_preflight.py`.
- Variables `RENDER_API_KEY`, `RENDER_OWNER_ID` y `SQX_RENDER_STAGING_BLUEPRINT`.
- Guia `RENDER_API_PREFLIGHT.md`.
- Tests para bloqueo sin credenciales y validacion mock de blueprint.

Estado: Done.

Decision M22:

- No se usa password de cuenta en scripts.
- Render API key es el mecanismo seguro para avanzar.
- El siguiente paso natural es ejecutar el preflight con API key real y validar el blueprint contra el workspace.

## Phase M23 - Render Credential Handshake

Objetivo: preparar un handshake seguro y auditable de credenciales Render antes de crear servicios reales.

Entregables:

- Estado `relay_render_credentials_handshake_ready`.
- `render_credentials_handshake.py`.
- Politica `api_key_only_no_account_password`.
- Evidencia local ignorada por git.
- Guia `RENDER_CREDENTIAL_HANDSHAKE.md`.

Estado: Done.

Decision M23:

- Si aparece password de cuenta Render en entorno, la decision es `NO-GO`.
- El deploy real solo avanza con `RENDER_API_KEY`, `RENDER_OWNER_ID` y blueprint validado.
- La evidencia del handshake queda en `backend/sqx-edge-relay/data/render_preflight_evidence`.

## Phase M24 - Render Staging Gate

Objetivo: crear una compuerta GO/NO-GO que impida avanzar a staging vivo sin credenciales, URL y smoke remoto validados.

Entregables:

- Estado `relay_render_staging_gate_ready`.
- `render_staging_gate.py`.
- Evidencia local en `backend/sqx-edge-relay/data/render_staging_gate`.
- Integracion con handshake Render y `staging_evidence.py`.
- Guia `RENDER_STAGING_GATE.md`.

Estado: Done.

Decision M24:

- Sin handshake Render `GO`, la compuerta devuelve `NO-GO`.
- Sin URL staging, la compuerta devuelve `NO-GO`.
- Antes de conectar pagos reales, `staging_evidence.py` debe devolver `GO`.

## Phase M25 - Render Staging Launch Pack

Objetivo: preparar un paquete de lanzamiento auditable para el despliegue manual/controlado en Render.

Entregables:

- Estado `relay_render_staging_launch_pack_ready`.
- `render_staging_launch_pack.py`.
- SHA256 del blueprint staging.
- Lista de variables Render requeridas.
- Comandos de operador post-deploy.
- Evidencia local en `backend/sqx-edge-relay/data/render_staging_launch_pack`.
- Guia `RENDER_STAGING_LAUNCH_PACK.md`.

Estado: Done.

Decision M25:

- El lanzamiento real sigue bloqueado si el staging gate no devuelve `GO`.
- Las variables secretas se configuran en Render, no en git.
- El launch pack es el documento operativo para ejecutar M26 con credenciales y URL reales.

## Phase M26 - Render Staging Secrets Kit

Objetivo: generar y auditar secretos fuertes para configurar staging en Render sin versionarlos.

Entregables:

- Estado `relay_render_staging_secrets_kit_ready`.
- `render_staging_secrets_kit.py`.
- `.env` local con secretos staging dentro de `backend/sqx-edge-relay/data/`.
- Evidencia JSON/Markdown redactada.
- Bloqueo de placeholders, valores cortos y passwords de cuenta Render.
- Guia `RENDER_STAGING_SECRETS_KIT.md`.

Estado: Done.

Decision M26:

- Los secretos staging se generan localmente y se pegan en Render/Lemon manualmente.
- La URL `SQX_LOCAL_INGEST_URL` sigue siendo un bloqueo hasta tener tunnel/endpoint real.
- Estos secretos deben rotarse antes de produccion.

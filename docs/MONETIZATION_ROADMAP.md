# SQX Edge Monetization Roadmap

Documento vivo para convertir SQX Edge Suite en una herramienta Pro comercial, con servicios y plantillas alrededor del producto.

## Current Status

- Last updated: 2026-05-07.
- Completed through: M70 - Next Controlled Buyer Readiness Check.
- Current state: `next_controlled_buyer_readiness_ready`.
- Governance baseline before M46: G1 - Specialist Agent Operating Model.
- Latest verified portable ZIP before M47: `dist/SQX_Edge_Tool_Portable_20260507_075847.zip`.
- Latest ZIP SHA256: `FE573CADCB79E2D93E1D1491BADC35DF0295C37DD08017AF3A9C784581E47E09`.
- Next recommended phase: M71 - Next Controlled Buyer Outcome Record.

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

## Phase M27 - Local Ingest Tunnel Readiness

Objetivo: validar la URL que Render usara para enviar bundles firmados al backend local.

Entregables:

- Estado `relay_local_ingest_tunnel_check_ready`.
- `local_ingest_tunnel_check.py`.
- Validacion de HTTPS, health remoto y path `/api/fulfillment/relay-ingest`.
- Envio opcional de bundle demo firmado con `--send-bundle`.
- Evidencia local en `backend/sqx-edge-relay/data/local_ingest_tunnel_check`.
- Guia `LOCAL_INGEST_TUNNEL_CHECK.md`.

Estado: Done.

Decision M27:

- `SQX_LOCAL_INGEST_URL` no se pega en Render hasta que health y politica de URL pasen.
- El bundle firmado demo es opt-in para no contaminar la cola durante pruebas secas.
- La siguiente fase real es obtener URL/tunnel real y ejecutar el check con `--send-bundle`.

## Phase M28 - Local Ingest Tunnel Launcher

Objetivo: preparar el lanzamiento del tunel publico hacia el backend local y detectar proveedores disponibles.

Entregables:

- Estado `relay_local_ingest_tunnel_launcher_ready`.
- `local_ingest_tunnel_launcher.py`.
- Deteccion de `cloudflared`, `ngrok` y `npx localtunnel`.
- Validacion de backend local en `/api/health`.
- Lanzamiento opt-in con `--start`.
- Parseo de URL publica y calculo de `/api/fulfillment/relay-ingest`.
- Guia `LOCAL_INGEST_TUNNEL_LAUNCHER.md`.

Estado: Done.

Decision M28:

- No se arranca ningun tunel por defecto.
- `cloudflared` es el proveedor recomendado si esta instalado.
- El siguiente paso real es instalar/usar un proveedor y ejecutar `--start` con el backend local encendido.

## Phase M29 - Local Ingest Staging Session

Objetivo: orquestar backend local, tunel publico e ingest check firmado desde una unica evidencia.

Entregables:

- Estado `relay_local_ingest_staging_session_ready`.
- `local_ingest_staging_session.py`.
- Arranque opt-in de backend con `--start-backend`.
- Arranque opt-in de tunel con `--start-tunnel`.
- Check firmado opcional con `--send-bundle`.
- Evidencia local en `backend/sqx-edge-relay/data/local_ingest_staging_session`.
- Guia `LOCAL_INGEST_STAGING_SESSION.md`.

Estado: Done.

Decision M29:

- El comando por defecto no abre procesos persistentes.
- Una sesion `GO` exige backend sano, URL publica detectada e ingest check correcto si hay tunnel.
- El siguiente paso real es ejecutar la sesion con backend/tunel reales y pasar la URL a Render.

## Phase M30 - Local Ingest Render Handoff

Objetivo: convertir una sesion local GO o una URL de ingest explicita en un paquete listo para configurar Render staging.

Entregables:

- Estado `relay_local_ingest_render_handoff_ready`.
- `local_ingest_render_handoff.py`.
- `.env` local con `SQX_LOCAL_INGEST_URL` y valores worker.
- Evidencia JSON/Markdown.
- Consumo de `--use-latest-session` o `--ingest-url`.
- Guia `LOCAL_INGEST_RENDER_HANDOFF.md`.

Estado: Done.

Decision M30:

- Si se usa evidencia de sesion, por defecto debe ser `GO`.
- El handoff no contiene secretos de firma, solo URL y valores no sensibles de worker.
- La siguiente fase real es pegar los valores en Render y ejecutar el staging gate contra URL Render real.

## Phase M31 - Render Staging Apply Gate

Objetivo: validar que los valores del handoff local se han aplicado en Render staging y que el gate remoto devuelve `GO`.

Entregables:

- Estado `relay_render_staging_apply_gate_ready`.
- `render_staging_apply_gate.py`.
- Confirmacion obligatoria `--confirm-env-applied`.
- Consumo de `local_ingest_render_handoff_*.json`.
- Ejecucion de `render_staging_gate.py` con URL staging real.
- Evidencia local en `backend/sqx-edge-relay/data/render_staging_apply_gate`.
- Guia `RENDER_STAGING_APPLY_GATE.md`.

Estado: Done.

Decision M31:

- La herramienta no cambia Render por API ni guarda secretos.
- El `GO` requiere handoff M30 `GO`, valores confirmados y gate remoto `GO`.
- La siguiente fase real es una compra staging completa con webhook demo, cola y dispatch hacia ingest local.

## Phase M32 - Render Staging Purchase Drill

Objetivo: probar el flujo de compra staging contra Render con webhook demo, cola remota y dispatch hacia ingest local.

Entregables:

- Estado `relay_render_staging_purchase_drill_ready`.
- `render_staging_purchase_drill.py`.
- Consumo de apply gate M31.
- Envio opt-in de webhook demo con `--send-webhook`.
- Dispatch opt-in con `--dispatch`.
- Evidencia antes/despues de `/relay/queue`.
- Evidencia local en `backend/sqx-edge-relay/data/render_staging_purchase_drill`.
- Guia `RENDER_STAGING_PURCHASE_DRILL.md`.

Estado: Done.

Decision M32:

- Las operaciones mutantes requieren flags explicitos.
- El `GO` requiere apply gate M31 `GO`, webhook aceptado, cola accesible y dispatch sin fallo.
- La siguiente fase real es preparar conexion de checkout real con Lemon Squeezy, variantes definitivas y rollback.

## Phase M33 - Checkout Live Readiness

Objetivo: validar que el checkout real puede publicarse sin perder trazabilidad ni rollback.

Entregables:

- Estado `checkout_live_readiness_ready`.
- `checkout_live_readiness.py`.
- Validacion de `primaryUrl` HTTPS.
- Validacion de relay publico HTTPS y webhook `/relay/webhook/lemon`.
- Validacion de `providerVariantId` para `pro_monthly`, `pro_annual` y `setup_assist`.
- Validacion de email de soporte.
- Consumo de evidencia M32.
- Evidencia local en `backend/sqx-edge-tool/data/checkout_live_readiness`.
- Guia `CHECKOUT_LIVE_READINESS.md`.

Estado: Done.

Decision M33:

- La herramienta no publica checkout ni activa webhooks.
- El `GO` requiere URLs reales, variantes reales, soporte valido y M32 `GO`.
- La siguiente fase real es preparar una release candidate comercial y compra piloto controlada.

## Phase M34 - Commercial Release Candidate

Objetivo: consolidar ZIP portable, hash, readiness, clave publica, compra piloto y rollback en una compuerta comercial.

Entregables:

- Estado `commercial_release_candidate_ready`.
- `commercial_release_candidate.py`.
- Validacion de ZIP portable y `ZIP SHA256`.
- Consumo de evidencia M33.
- Bloqueo de public key placeholder.
- Confirmacion explicita de compra piloto.
- Evidencia local en `backend/sqx-edge-tool/data/commercial_release_candidate`.
- Guia `COMMERCIAL_RELEASE_CANDIDATE.md`.

Estado: Done.

Decision M34:

- La venta publica sigue bloqueada hasta tener RC `GO`.
- La compra piloto debe ser explicita y trazable.
- El siguiente paso real es actualizar URLs/variant IDs reales y ejecutar la compra piloto privada.

## Phase M35 - Pilot Purchase Kit

Objetivo: preparar y auditar una compra piloto privada con orden, licencia firmada, entrega final e importacion Pro verificada.

Entregables:

- Estado `pilot_purchase_kit_ready`.
- `pilot_purchase_kit.py`.
- Consumo de evidencia M34.
- Comandos guiados para `license_issue.py` y `prepare_customer_delivery.ps1`.
- Evidencia local en `backend/sqx-edge-tool/data/pilot_purchase_kit`.
- Guia `PILOT_PURCHASE_KIT.md`.

Estado: Done.

Decision M35:

- La compra piloto no queda en `GO` sin order id, licencia firmada, manifest de entrega e importacion Pro confirmada.
- El kit no publica checkout ni toca proveedor; convierte los pasos manuales en evidencia auditable.
- El siguiente paso real es usar una compra piloto `GO` para abrir una venta publica limitada.

## Phase M36 - Limited Public Launch

Objetivo: abrir una venta publica pequena, controlada y reversible despues de una compra piloto verificada.

Entregables:

- Estado `limited_public_launch_ready`.
- `limited_public_launch.py`.
- Consumo de evidencia M35.
- Validacion de checkout HTTPS, variantes, soporte, first sale cap, launch window y rollback owner.
- Evidencia local en `backend/sqx-edge-tool/data/limited_public_launch`.
- Guia `LIMITED_PUBLIC_LAUNCH.md`.

Estado: Done.

Decision M36:

- La venta publica limitada no queda en `GO` sin piloto `GO`, soporte preparado y checkout confirmado.
- El limite inicial recomendado es `5` ventas antes de revisar soporte y activaciones.
- El siguiente paso real es post-launch control: registrar primeras ventas, incidencias y decision de escalar o pausar.

## Phase M37 - Post Launch Control

Objetivo: convertir las primeras ventas y activaciones en una decision auditable de escalado, pausa o rollback.

Entregables:

- Estado `post_launch_control_ready`.
- `post_launch_control.py`.
- Consumo de evidencia M36.
- Validacion de ventas, activaciones, support tickets, refunds, fallos de fulfillment, review window y decision owner.
- Evidencia local en `backend/sqx-edge-tool/data/post_launch_control`.
- Guia `POST_LAUNCH_CONTROL.md`.

Estado: Done.

Decision M37:

- No se escala a venta publica con tickets sin resolver, activaciones pendientes o fulfillment fallido.
- `scale_public` exige al menos 3 ventas, cero tickets sin resolver y cero fallos de fulfillment.
- El siguiente paso real es clasificar feedback, priorizar mejoras y decidir si se ajustan precio/copy antes de escalar.

## Phase M38 - Commercial Feedback Loop

Objetivo: clasificar feedback comercial y decidir version, precio, copy y siguiente accion antes de escalar mas.

Entregables:

- Estado `commercial_feedback_loop_ready`.
- `commercial_feedback_loop.py`.
- Consumo de evidencia M37.
- Clasificacion de bugs, friccion de activacion, documentacion, features, precio, copy y senales positivas.
- Evidencia local en `backend/sqx-edge-tool/data/commercial_feedback_loop`.
- Guia `COMMERCIAL_FEEDBACK_LOOP.md`.

Estado: Done.

Decision M38:

- No se cambia precio ni copy sin feedback revisado, roadmap actualizado y owner de release notes.
- Bugs severos y friccion de activacion bloquean escalar la oferta hasta tener fix o docs.
- El siguiente paso real es preparar pagina/oferta publica controlada con copy revisado y FAQ comercial.

## Phase M39 - Public Offer Pack

Objetivo: convertir feedback revisado en una oferta publica controlada, clara y segura para comprador basico.

Entregables:

- Estado `public_offer_pack_ready`.
- `public_offer_pack.py`.
- Consumo de evidencia M38.
- Validacion de headline, subheadline, FAQ, release notes, buyer steps, soporte, checkout y claims seguros.
- Evidencia local en `backend/sqx-edge-tool/data/public_offer_pack`.
- Guia `PUBLIC_OFFER_PACK.md`.

Estado: Done.

Decision M39:

- No se publica oferta si faltan instrucciones de comprador, FAQ, release notes o checkout.
- Los claims financieros prohibidos bloquean la publicacion.
- El siguiente paso real es preparar assets de lanzamiento y draft de GitHub Release/pagina publica.

## Phase M40 - Launch Assets Kit

Objetivo: preparar activos finales para publicar una oferta o release visible.

Entregables:

- Estado `launch_assets_kit_ready`.
- `launch_assets_kit.py`.
- Consumo de evidencia M39.
- Validacion de ZIP, SHA256, capturas desktop/mobile, copy corto/largo, README comercial, support macro y GitHub Release draft.
- Evidencia local en `backend/sqx-edge-tool/data/launch_assets_kit`.
- Guia `LAUNCH_ASSETS_KIT.md`.

Estado: Done.

Decision M40:

- No se publica sin ZIP final, checksum, capturas, copy y checklist de publicacion.
- El siguiente paso real es un public release gate con tag, release draft final y rollback operativo.

## Phase M41 - Public Release Gate

Objetivo: bloquear la publicacion visible hasta tener tag, GitHub Release, ZIP, SHA256, soporte y rollback confirmados.

Entregables:

- Estado `public_release_gate_ready`.
- `public_release_gate.py`.
- Consumo de evidencia M40.
- Validacion de `release_tag`, URL HTTPS de GitHub Release, ZIP adjunto, SHA256 publicado, checkout, soporte y rollback.
- Evidencia local en `backend/sqx-edge-tool/data/public_release_gate`.
- Guia `PUBLIC_RELEASE_GATE.md`.

Estado: Done.

Decision M41:

- No se publica release publica sin release revisada, ZIP adjunto y SHA256 publicado.
- Soporte y rollback deben tener owner antes de abrir una ventana publica.
- El siguiente paso real es ejecutar una publicacion controlada y registrar evidencia post-release.

## Phase M42 - Release Publication Record

Objetivo: registrar evidencia post-publicacion de tag, GitHub Release, ZIP, SHA256, descarga, soporte y rollback.

Entregables:

- Estado `release_publication_record_ready`.
- `release_publication_record.py`.
- Consumo de evidencia M41.
- Validacion de release publicada, tag creado, ZIP local, `.sha256`, descarga probada y notas visibles.
- Evidencia local en `backend/sqx-edge-tool/data/release_publication_record`.
- Guia `RELEASE_PUBLICATION_RECORD.md`.

Estado: Done.

Decision M42:

- La publicacion no se considera cerrada sin checksum coincidente y descarga probada.
- Soporte y rollback deben permanecer abiertos durante la ventana inicial.
- El siguiente paso real es monitorizar incidencias, activaciones y descargas post-release.

## Phase M43 - Post Release Monitor

Objetivo: monitorizar la ventana posterior a una release visible y decidir mantener, pausar, hotfix, rollback o escalar.

Entregables:

- Estado `post_release_monitor_ready`.
- `post_release_monitor.py`.
- Consumo de evidencia M42.
- Validacion de descargas, ventas, activaciones, tickets, incidencias, refunds, fulfillment failures y rollback.
- Evidencia local en `backend/sqx-edge-tool/data/post_release_monitor`.
- Guia `POST_RELEASE_MONITOR.md`.

Estado: Done.

Decision M43:

- No se escala con tickets abiertos, incidencias severas, `activation_error_rate_high`, refunds altos o rollback no disponible.
- `scale_public` exige ventana minima y senal comercial minima.
- El siguiente paso real es preparar el flujo de hotfix/rollback para cerrar incidentes sin improvisar.

## Phase M44 - Hotfix Rollback Release

Objetivo: preparar el paquete operativo para pausar, corregir, hacer rollback o cerrar una incidencia post-release.

Entregables:

- Estado `hotfix_rollback_release_ready`.
- `hotfix_rollback_release.py`.
- Consumo de evidencia M43.
- Validacion de accion, owner, incidente, notas, target de rollback, comunicacion, soporte, verificacion y cierre.
- Evidencia local en `backend/sqx-edge-tool/data/hotfix_rollback_release`.
- Guia `HOTFIX_ROLLBACK_RELEASE.md`.

Estado: Done.

Decision M44:

- No hay hotfix sin notas, version, paquete y plan de verificacion.
- No hay rollback sin `rollback_target_missing` resuelto, checklist y comunicacion preparada.
- El siguiente paso real es customer success/renewal loop para convertir usuarios Pro en relaciones sostenibles.

## Phase M45 - Customer Success Renewal Loop

Objetivo: preparar el seguimiento de usuarios Pro despues de compra, activacion y soporte para mejorar retencion sin prometer resultados financieros.

Entregables:

- Checklist de onboarding del comprador Pro.
- Registro de activacion, soporte inicial, bloqueos y resolucion.
- Seguimiento de renovacion mensual/anual.
- Senales de expansion: plantillas, Setup Assist y soporte prioritario.
- Decision auditada de mantener, mejorar, pausar oferta o preparar siguiente release comercial.

Estado: Done.

Decision M45:

- No hay decision de renovacion sin cliente, owner, onboarding, activacion y soporte triado.
- Las oportunidades de expansion exigen oferta preparada y claims seguros revisados.
- El siguiente paso real es M46: cockpit comercial ligero para ver renovaciones, tickets y oportunidades en una sola vista.

## Phase M46 - Commercial Customer Cockpit

Objetivo: convertir la evidencia de customer success en un cockpit interno ligero para revisar clientes Pro, renovaciones, soporte, activacion y oportunidades responsables.

Entregables:

- Estado `customer_cockpit_ready`.
- Endpoint read-only `GET /api/customer-cockpit`.
- Agregador `backend/sqx-edge-tool/core/customer_cockpit.py`.
- Configuracion segura `backend/sqx-edge-tool/config/customer_cockpit.json`.
- Modulo frontend `app/js/modules/customer-cockpit.js`.
- Panel Inicio `Customer Success` con clientes redactados, renovaciones, tickets y oportunidades.
- Contratos JS, tests backend/staticos y E2E con capturas.

Estado: Done.

Decision M46:

- El cockpit muestra resumen operativo redactado; no muestra payloads de licencia, claves privadas, eventos checkout crudos ni secretos de relay.
- La fuente real prioritaria son evidencias locales `customer_success_renewal`; sin datos reales, el cockpit queda listo con estado vacio.
- El siguiente paso real es M47: pack de datos y plantillas para comprador Pro.

## Phase M47 - Pro Buyer Data And Template Pack

Objetivo: preparar datos y plantillas reales para compradores Pro, incluidos en el portable, sin exponer material sensible ni prometer resultados financieros.

Entregables:

- Estado `pro_buyer_pack_ready`.
- Configuracion `backend/sqx-edge-tool/config/pro_buyer_pack.json`.
- Recursos buyer-facing `resources/pro-buyer-pack`.
- Universo inicial de 28 Forex, 4 indices y oro.
- CSV importable compatible con el tab Estrategias.
- Plantillas de activacion, soporte, Project Generator y primer valor.
- Validador interno `backend/sqx-edge-tool/tools/pro_buyer_pack.py`.

Estado: Done.

Decision M47:

- El pack buyer-facing viaja en el portable.
- La herramienta interna y la evidencia `backend/sqx-edge-tool/data/pro_buyer_pack` no se empaquetan.
- El siguiente paso real es M48: buyer onboarding y support gate para usuario basico.

## Phase M48 - Basic Buyer Onboarding And Support Gate

Objetivo: preparar una entrada basica para comprador Pro, con compra confirmada, ZIP, licencia, instrucciones, FAQ, soporte inicial y criterios de pausa/reembolso.

Entregables:

- Estado `buyer_onboarding_support_gate_ready`.
- Configuracion `backend/sqx-edge-tool/config/buyer_onboarding_support_gate.json`.
- Recursos buyer-facing en `resources/pro-buyer-pack/onboarding`.
- Guia interna `docs/sales/BUYER_ONBOARDING_SUPPORT_GATE.md`.
- Validador interno `backend/sqx-edge-tool/tools/buyer_onboarding_support_gate.py`.
- Evidencia local excluida de ZIP en `backend/sqx-edge-tool/data/buyer_onboarding_support_gate`.

Estado: Done.

Decision M48:

- El onboarding basico viaja en el portable.
- El gate interno valida que compra, ZIP, licencia, guia, FAQ, soporte y claims seguros estan listos antes de entregar.
- La evidencia y herramienta interna no se empaquetan.
- El siguiente paso real es M49: empaquetar Template Pack 1 como add-on comercial controlado.

## Phase M49 - Pro Template Pack 1 Packaging And Delivery

Objetivo: empaquetar Template Pack 1 como add-on comercial separado del ZIP base, con perfiles reales, entrega controlada, claims seguros y soporte acotado.

Entregables:

- Estado `template_pack_1_delivery_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_1.json`.
- Recursos buyer-facing en `resources/pro-template-pack-1`.
- Guia interna `docs/sales/TEMPLATE_PACK_1_DELIVERY.md`.
- Validador y packager interno `backend/sqx-edge-tool/tools/template_pack_1_delivery.py`.
- Evidencia local excluida de ZIP en `backend/sqx-edge-tool/data/template_pack_1_delivery`.

Estado: Done.

Decision M49:

- Template Pack 1 no viaja en el ZIP base.
- Se entrega como ZIP add-on separado despues de validar buyer onboarding, orden del add-on, perfiles, soporte y claims seguros.
- La herramienta interna y la evidencia local no se empaquetan.
- El siguiente paso real es M50: preparar oferta publica y checkout del add-on.

## Phase M50 - Template Pack 1 Public Add-On Offer And Checkout Wiring

Objetivo: preparar la oferta publica de Template Pack 1 como add-on, con copy revisado, FAQ, wiring de checkout, macro de entrega y soporte responsable.

Entregables:

- Estado `template_pack_1_public_offer_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_1_offer.json`.
- Recursos de oferta en `resources/pro-template-pack-1/offer`.
- Guia interna `docs/sales/TEMPLATE_PACK_1_PUBLIC_OFFER.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_1_offer.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_1_offer`.

Estado: Done.

Decision M50:

- La oferta queda lista en modo draft.
- El plan `template_pack_1`, precio `49 EUR`, copy, FAQ y macros quedan conectados al manifiesto.
- La publicacion abierta queda bloqueada hasta tener URL, variant ID y email de soporte reales.
- El siguiente paso real es M51: conectar valores reales de checkout y publicar de forma controlada.

## Phase M51 - Template Pack 1 Live Checkout Values And Controlled Publication Gate

Objetivo: preparar la conexion de valores reales de checkout del add-on sin commitear enlaces falsos ni publicar antes de validar soporte, rollback y entrega.

Entregables:

- Estado `template_pack_1_live_checkout_gate_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_1_publication.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_1_LIVE_CHECKOUT_PUBLICATION.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_1_publication.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_1_publication`.

Estado: Done.

Decision M51:

- Los valores reales se aceptan por CLI o variables de entorno.
- El gate valida URL HTTPS, provider variant ID, email de soporte, placeholders, dependencia M50 y confirmaciones de rollback.
- `--apply` queda disponible para escribir los valores reales en el manifiesto solo despues de un GO.
- El siguiente paso real es M52: compra controlada del add-on con evidencia de pedido, entrega y soporte inicial.

## Phase M52 - Template Pack 1 Controlled Purchase Drill

Objetivo: preparar y validar una compra controlada real de Template Pack 1 antes de escalar la publicacion del add-on.

Entregables:

- Estado `template_pack_1_purchase_drill_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_1_purchase_drill.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_1_PURCHASE_DRILL.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_1_purchase_drill.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_1_purchase_drill`.

Estado: Done.

Decision M52:

- El gate exige checkout URL, provider variant ID, order ID, buyer email, estado de pago, importe, moneda y confirmaciones operativas.
- La evidencia redacta el email del comprador y no guarda payloads crudos del proveedor.
- Puede verificar el ZIP add-on separado cuando se pasa `--require-delivery-package`.
- El siguiente paso real es M53: handoff real posterior a compra, soporte inicial y decision de escalar o pausar.

## Phase M53 - Template Pack 1 Post-Purchase Handoff And Scale Decision

Objetivo: preparar el handoff posterior a la primera compra controlada de Template Pack 1, con entrega, soporte inicial, primer valor y decision de escalar o pausar.

Entregables:

- Estado `template_pack_1_handoff_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_1_handoff.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_1_HANDOFF.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_1_handoff.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_1_handoff`.

Estado: Done.

Decision M53:

- El gate exige purchase drill GO, entrega enviada, comprador informado, soporte abierto, primer valor confirmado y notas de soporte.
- La decision queda restringida a `scale_limited`, `hold_review` o `pause_sales`.
- La evidencia redacta el email del comprador y no guarda payloads crudos del proveedor.
- El siguiente paso real es M54: consolidar un registro/panel ligero de ventas add-on antes de abrir mas trafico.

## Phase M54 - Template Pack 1 Add-On Sales Register

Objetivo: consolidar un registro interno de ventas de Template Pack 1 antes de abrir mas trafico publico.

Entregables:

- Estado `template_pack_1_sales_register_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_1_sales_register.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_1_SALES_REGISTER.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_1_sales_register.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_1_sales_register`.

Estado: Done.

Decision M54:

- El registro conserva referencia redactada de comprador, order id, canal, importe, delivery/support status, refunds, fallos de fulfillment y decision.
- No guarda emails en claro ni payloads crudos del proveedor.
- `scale_limited` exige venta pagada, entrega confirmada, cero soporte abierto, cero refunds y cero fallos.
- El siguiente paso real es M55: revisar cohorte de compradores del add-on y feedback real antes de ampliar trafico o crear Template Pack 2.

## Phase M55 - Template Pack 1 Feedback Cohort Review

Objetivo: revisar la primera cohorte de compradores de Template Pack 1 antes de ampliar trafico o crear Template Pack 2.

Entregables:

- Estado `template_pack_1_feedback_cohort_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_1_feedback_cohort.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_1_FEEDBACK_COHORT.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_1_feedback_cohort.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_1_feedback_cohort`.

Estado: Done.

Decision M55:

- La revision conserva metricas agregadas, temas de feedback, soporte, refunds, senales positivas y decision de roadmap.
- No guarda mensajes crudos, emails en claro ni payloads de proveedor.
- `expand_traffic` exige compradores suficientes, feedback suficiente, cero bugs bloqueantes, cero friccion de activacion, cero soporte abierto y cero refunds.
- `build_template_pack_2` exige senales positivas claras y ausencia de riesgo operativo.
- El siguiente paso real es M56: convertir el feedback en plan accionable de iteracion de oferta o Template Pack 2.

## Phase M56 - Template Pack 1 Iteration Or Pack 2 Action Plan

Objetivo: convertir la decision de cohorte M55 en un plan accionable para iterar la oferta, ampliar trafico, preparar Template Pack 2 o pausar ventas.

Entregables:

- Estado `template_pack_1_action_plan_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_1_action_plan.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_1_ACTION_PLAN.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_1_action_plan.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_1_action_plan`.

Estado: Done.

Decision M56:

- El plan conserva owner, prioridad, numero de acciones, impacto de soporte/distribucion/claims y siguiente fase.
- No guarda mensajes crudos de comprador ni payloads de proveedor.
- El plan debe derivar de la decision M55 y apuntar a `M57_offer_iteration`, `M57_template_pack_2_specs`, `M57_traffic_expansion` o `M57_pause_and_fix`.
- El siguiente paso real es M57: ejecutar el plan elegido.

## Phase M57 - Template Pack 2 Initial Specs

Objetivo: ejecutar el plan M56 cuando la ruta elegida es Template Pack 2, definiendo alcance, activos, presets, soporte, entrega y siguiente fase antes de crear recursos comerciales.

Entregables:

- Estado `template_pack_2_specs_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_2_specs.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_2_SPECS.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_2_specs.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_2_specs`.

Estado: Done.

Decision M57:

- Template Pack 2 queda como especificacion trazable antes de crear recursos buyer-facing.
- `draft_pack_2_assets` exige action plan GO, feedback mapeado, familias de activos, presets, soporte, entrega y cero riesgo de claims.
- Si Pack 1 necesita correccion previa se usa `iterate_pack_1_first`; si hay riesgo operativo se usa `pause_pack_2`.
- El siguiente paso real es M58: crear recursos iniciales de Template Pack 2 o ejecutar la alternativa indicada por la especificacion.

## Phase M58 - Template Pack 2 Initial Assets

Objetivo: convertir las specs M57 en recursos iniciales reales para Template Pack 2 como add-on separado.

Entregables:

- Estado `template_pack_2_assets_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_2_assets.json`.
- Recursos buyer-facing en `resources/pro-template-pack-2`.
- Guia interna `docs/sales/TEMPLATE_PACK_2_ASSETS.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_2_assets.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_2_assets`.

Estado: Done.

Decision M58:

- Template Pack 2 queda materializado con 3 perfiles JSON, 8 presets CSV y checklists de entrega/soporte/claims.
- El pack se entrega como ZIP add-on separado y no forma parte del portable principal.
- No contiene licencias, claves privadas, payloads de proveedor ni eventos crudos.
- El siguiente paso real es M59: preparar oferta controlada de Template Pack 2 con copy publico, FAQ, checkout draft y macros.

## Phase M59 - Template Pack 2 Offer Pack

Objetivo: preparar venta controlada de Template Pack 2 con copy, FAQ, checkout draft, delivery macro y support macro antes de activar checkout real.

Entregables:

- Estado `template_pack_2_offer_pack_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_2_offer_pack.json`.
- Recursos en `resources/pro-template-pack-2/offer`.
- Guia interna `docs/sales/TEMPLATE_PACK_2_OFFER_PACK.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_2_offer_pack.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_2_offer_pack`.

Estado: Done.

Decision M59:

- Template Pack 2 queda con oferta controlada lista para revisar.
- Checkout queda en draft hasta completar URL, variant ID y soporte reales.
- La fase no guarda credenciales, licencias, claves privadas ni payloads de proveedor.
- El siguiente paso real es M60: preparar publicacion controlada con checkout real, soporte, rollback y purchase drill.

## Phase M60 - Template Pack 2 Controlled Publication

Objetivo: preparar publicacion controlada de Template Pack 2 con URL real, soporte, rollback y purchase drill antes de escalar ventas.

Entregables:

- Estado `template_pack_2_controlled_publication_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_2_publication.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_2_CONTROLLED_PUBLICATION.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_2_publication.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_2_publication`.

Estado: Done.

Decision M60:

- El checkout real queda validable mediante URL HTTPS, variant ID y soporte.
- El purchase drill queda como checklist previo a la primera venta controlada.
- La escritura de valores reales en manifest requiere `--apply`.
- El siguiente paso real es M61: ejecutar purchase drill controlado con evidencia redacted.

## Phase M61 - Template Pack 2 Controlled Purchase Drill

Objetivo: preparar y validar una compra controlada real de Template Pack 2 antes de escalar la publicacion del add-on.

Entregables:

- Estado `template_pack_2_purchase_drill_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_2_purchase_drill.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_2_PURCHASE_DRILL.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_2_purchase_drill.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_2_purchase_drill`.

Estado: Done.

Decision M61:

- El gate exige checkout URL, provider variant ID, order ID, buyer email, estado de pago, importe, moneda y confirmaciones operativas.
- La evidencia redacta el email del comprador y no guarda payloads crudos del proveedor.
- Puede verificar el ZIP add-on separado cuando se pasa `--require-delivery-package`.
- El siguiente paso real es M62: handoff posterior a compra, soporte inicial y decision de escalar o pausar Template Pack 2.

## Phase M62 - Template Pack 2 Post-Purchase Handoff

Objetivo: preparar el handoff posterior a la primera compra controlada de Template Pack 2, con entrega, soporte inicial, primer valor y decision de escalar o pausar.

Entregables:

- Estado `template_pack_2_handoff_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_2_handoff.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_2_HANDOFF.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_2_handoff.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_2_handoff`.

Estado: Done.

Decision M62:

- El gate exige purchase drill GO, entrega enviada, comprador informado, soporte abierto, primer valor confirmado y notas de soporte.
- La decision queda restringida a `scale_limited`, `hold_review` o `pause_sales`.
- La evidencia redacta el email del comprador y no guarda payloads crudos del proveedor.
- El siguiente paso real es M63: registro de ventas y cohorte temprana de Template Pack 2 antes de ampliar trafico.

## Phase M63 - Template Pack 2 Sales Register

Objetivo: consolidar un registro interno de ventas de Template Pack 2 antes de abrir mas trafico publico.

Entregables:

- Estado `template_pack_2_sales_register_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_2_sales_register.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_2_SALES_REGISTER.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_2_sales_register.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_2_sales_register`.

Estado: Done.

Decision M63:

- El registro conserva referencia redactada de comprador, order id, canal, importe, delivery/support status, refunds, fallos de fulfillment y decision.
- No guarda emails en claro ni payloads crudos del proveedor.
- `scale_limited` exige venta pagada, entrega confirmada, cero soporte abierto, cero refunds y cero fallos.
- El siguiente paso real es M64: revisar cohorte temprana y feedback real de Template Pack 2 antes de ampliar trafico.

## Phase M64 - Template Pack 2 Feedback Cohort Review

Objetivo: revisar la cohorte temprana de compradores de Template Pack 2 antes de ampliar trafico publico.

Entregables:

- Estado `template_pack_2_feedback_cohort_ready`.
- Configuracion `backend/sqx-edge-tool/config/template_pack_2_feedback_cohort.json`.
- Guia interna `docs/sales/TEMPLATE_PACK_2_FEEDBACK_COHORT.md`.
- Gate interno `backend/sqx-edge-tool/tools/template_pack_2_feedback_cohort.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/template_pack_2_feedback_cohort`.

Estado: Done.

Decision M64:

- La revision conserva metricas agregadas, temas de feedback, soporte, refunds, senales positivas y decision de roadmap.
- No guarda mensajes crudos, emails en claro ni payloads de proveedor.
- `expand_traffic` exige compradores suficientes, feedback suficiente, cero bugs bloqueantes, cero friccion de activacion, cero soporte abierto y cero refunds.
- `prepare_pack_3` exige senales positivas claras y ausencia de riesgo operativo.
- El siguiente paso real es M65: cierre buyer-ready de checkout, release, soporte y entrega para primeras ventas controladas.

## Phase M65 - Buyer-Ready Checkout Release Closeout

Objetivo: cerrar checkout, release, soporte, entrega de licencia y rollback con una ruta entendible para compradores basicos antes de abrir ventas controladas.

Entregables:

- Estado `buyer_ready_checkout_release_closeout_ready`.
- Configuracion `backend/sqx-edge-tool/config/buyer_ready_checkout_closeout.json`.
- Guia interna `docs/sales/BUYER_READY_CHECKOUT_RELEASE.md`.
- Gate interno `backend/sqx-edge-tool/tools/buyer_ready_checkout_closeout.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/buyer_ready_checkout_closeout`.

Estado: Done.

Decision M65:

- El cierre exige feedback cohort GO, copy revisado, portable revisado, licencia/entrega revisada, soporte visible, claims seguros y rollback.
- La evidencia guarda solo estado operativo agregado, sin emails completos, licencias firmadas, secretos ni payloads de proveedor.
- `open_controlled_sales` queda reservado para una venta controlada con soporte/rollback operativo.
- El siguiente paso real es M66: preparar pagina/checklist publico de comprador y cadencia tranquila de primera venta.

## Phase M66 - Public Buyer Page Checklist And First-Sale Cadence

Objetivo: preparar una pagina/checklist publico de comprador y una cadencia tranquila de primera venta antes de ampliar distribucion.

Entregables:

- Estado `public_buyer_page_cadence_ready`.
- Configuracion `backend/sqx-edge-tool/config/public_buyer_page_cadence.json`.
- Guia interna `docs/sales/PUBLIC_BUYER_PAGE_CADENCE.md`.
- Gate interno `backend/sqx-edge-tool/tools/public_buyer_page_cadence.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/public_buyer_page_cadence`.

Estado: Done.

Decision M66:

- El gate exige closeout M65 GO, copy publico revisado, precios/terminos revisados, pasos de comprador, soporte, cadencia de primera venta, claims seguros y rollback.
- La evidencia no guarda compradores, emails, licencias firmadas, secretos ni payloads del proveedor.
- `publish_private_page` queda limitado a enlace privado/controlado con cadencia y soporte revisados.
- El siguiente paso real es M67: registrar primer comprador controlado con activacion, soporte y revision post-venta ligera.

## Phase M67 - First Controlled Buyer Operating Log And Post-Sale Review

Objetivo: registrar la primera venta controlada con activacion, soporte, feedback y decision post-venta ligera antes de sumar mas presion comercial.

Entregables:

- Estado `first_controlled_buyer_log_ready`.
- Configuracion `backend/sqx-edge-tool/config/first_controlled_buyer_log.json`.
- Guia interna `docs/sales/FIRST_CONTROLLED_BUYER_LOG.md`.
- Gate interno `backend/sqx-edge-tool/tools/first_controlled_buyer_log.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/first_controlled_buyer_log`.

Estado: Done.

Decision M67:

- El gate exige page cadence M66 GO, venta registrada, entrega confirmada, activacion revisada, soporte revisado, feedback revisado, claims seguros y decision post-venta.
- La evidencia no guarda emails completos, licencias firmadas, payloads de proveedor, claves ni mensajes crudos.
- `continue_private_sales` exige primer valor confirmado, cero soporte abierto, cero refunds y cero fallos de fulfillment.
- El siguiente paso real es M68: preparar un bucle pequeno de mejora post-venta para onboarding, soporte y copy publico.

## Phase M68 - Post-Sale Improvement Loop

Objetivo: convertir la primera experiencia de comprador controlado en mejoras pequenas de onboarding, macros de soporte, copy publico y safe claims antes de sumar trafico.

Entregables:

- Estado `post_sale_improvement_loop_ready`.
- Configuracion `backend/sqx-edge-tool/config/post_sale_improvement_loop.json`.
- Guia interna `docs/sales/POST_SALE_IMPROVEMENT_LOOP.md`.
- Gate interno `backend/sqx-edge-tool/tools/post_sale_improvement_loop.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/post_sale_improvement_loop`.

Estado: Done.

Decision M68:

- El gate exige M67 GO, onboarding revisado, macros de soporte revisadas, copy publico revisado, safe claims revisados, owner y siguiente revision.
- La evidencia guarda solo acciones agregadas, owner, siguiente revision y resumen operativo, sin mensajes crudos ni datos personales.
- `ship_micro_updates` queda bloqueado si hay claims risk, soporte abierto, refunds o fallos de fulfillment.
- El siguiente paso real es M69: aplicar las micro-mejoras aprobadas y preparar el siguiente comprador controlado.

## Phase M69 - Apply Post-Sale Micro Updates

Objetivo: aplicar las micro-mejoras aprobadas a onboarding, activacion, soporte y copy publico, y dejar listo el check del siguiente comprador controlado.

Entregables:

- Estado `post_sale_micro_updates_ready`.
- Configuracion `backend/sqx-edge-tool/config/post_sale_micro_updates.json`.
- Guia interna `docs/sales/POST_SALE_MICRO_UPDATES.md`.
- Gate interno `backend/sqx-edge-tool/tools/post_sale_micro_updates.py`.
- Micro-mejoras aplicadas en `START_HERE.md`, `license_activation_walkthrough.md`, `support_contact_template.md`, `support_macro.md`, `COMMERCIAL_README.md` y `PUBLIC_BUYER_PAGE_CADENCE.md`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/post_sale_micro_updates`.

Estado: Done.

Decision M69:

- El gate exige M68 GO, marcadores buyer-facing aplicados, safe claims preservados y pasos minimos para el siguiente comprador.
- La evidencia guarda solo conteos, owner, notas de readiness y decision, sin datos personales ni mensajes crudos.
- `next_controlled_buyer_ready` queda bloqueado si falta onboarding, soporte, copy publico, safe claims o si hay claims risk.
- El siguiente paso real es M70: ejecutar el readiness check del siguiente comprador controlado antes de compartir otro enlace privado.

## Phase M70 - Next Controlled Buyer Readiness Check

Objetivo: comprobar readiness formal antes de compartir otro enlace privado con un unico comprador controlado.

Entregables:

- Estado `next_controlled_buyer_readiness_ready`.
- Configuracion `backend/sqx-edge-tool/config/next_controlled_buyer_readiness.json`.
- Guia interna `docs/sales/NEXT_CONTROLLED_BUYER_READINESS.md`.
- Gate interno `backend/sqx-edge-tool/tools/next_controlled_buyer_readiness.py`.
- Evidencia local excluida en `backend/sqx-edge-tool/data/next_controlled_buyer_readiness`.

Estado: Done.

Decision M70:

- El gate exige M69 GO, un unico slot de comprador, enlace privado listo, checkout revisado, licencia/entrega listas, soporte disponible, safe claims y regla de pausa.
- La evidencia guarda solo conteos, estados y notas operativas, sin datos personales, payloads de checkout ni licencias firmadas.
- `share_private_link` queda bloqueado si falta enlace privado listo, hay mas de un slot, soporte abierto, claims risk o M69 no esta GO.
- El siguiente paso real es M71: registrar el resultado del siguiente comprador controlado y decidir repetir, pausar o ampliar con cuidado.

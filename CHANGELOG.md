# Changelog

## 2026-05-07 - Template Pack 2 purchase drill

- Anade M61 con compra controlada de Template Pack 2.
- Anade `template_pack_2_purchase_drill.py` para validar pedido, pago, entrega, soporte y refund/pause.
- Actualiza estado comercial a `template_pack_2_purchase_drill_ready`.
- Mantiene evidencia redactada y fuera del ZIP portable.

## 2026-05-07 - Template Pack 2 controlled publication

- Anade M60 con puerta de publicacion controlada para Template Pack 2.
- Anade `template_pack_2_publication.py` para validar checkout URL, variant ID, soporte, rollback y purchase drill.
- Actualiza estado comercial a `template_pack_2_controlled_publication_ready`.
- Mantiene la escritura de valores reales detras de `--apply`.

## 2026-05-07 - Template Pack 2 offer pack

- Anade M59 con oferta controlada para Template Pack 2.
- Anade `template_pack_2_offer_pack.py` para validar copy, FAQ, checkout draft, macros, soporte y safe claims.
- Actualiza estado comercial a `template_pack_2_offer_pack_ready`.
- Mantiene checkout en modo draft hasta completar URL, variant ID y soporte reales.

## 2026-05-07 - Template Pack 2 assets

- Anade M58 con recursos iniciales reales para Template Pack 2.
- Anade `template_pack_2_assets.py` para validar perfiles, presets CSV, soporte, safe claims y empaquetado add-on separado.
- Actualiza estado comercial a `template_pack_2_assets_ready`.
- Mantiene Template Pack 2 fuera del ZIP portable principal y listo como add-on separado.

## 2026-05-07 - Template Pack 2 specs

- Anade M57 con especificacion inicial de Template Pack 2 derivada del action plan M56.
- Anade `template_pack_2_specs.py` para validar alcance, familias de activos, presets, soporte, entrega, claims y siguiente fase.
- Actualiza estado comercial a `template_pack_2_specs_ready`.
- Mantiene Pack 2 como especificacion trazable antes de crear recursos comerciales.

## 2026-05-07 - Template Pack 1 action plan

- Anade M56 con plan accionable para iterar oferta, ampliar trafico, preparar Template Pack 2 o pausar ventas.
- Anade `template_pack_1_action_plan.py` para validar owner, prioridad, acciones, soporte, claims, distribucion y siguiente fase.
- Actualiza estado comercial a `template_pack_1_action_plan_ready`.
- Mantiene el plan como evidencia redactada sin mensajes crudos de comprador ni payloads de proveedor.

## 2026-05-07 - Template Pack 1 feedback cohort

- Anade M55 con revision de cohorte y feedback real para Template Pack 1.
- Anade `template_pack_1_feedback_cohort.py` para validar compradores, feedback, bugs, friccion, soporte, refunds y decision de roadmap.
- Actualiza estado comercial a `template_pack_1_feedback_cohort_ready`.
- Bloquea escalado o Template Pack 2 sin senales positivas, soporte controlado y claims seguros.

## 2026-05-07 - Template Pack 1 sales register

- Anade M54 con registro interno de ventas add-on para Template Pack 1.
- Anade `template_pack_1_sales_register.py` para validar venta, entrega, soporte, refunds, fulfillment y decision de escala.
- Actualiza estado comercial a `template_pack_1_sales_register_ready`.
- Mantiene referencia de comprador redactada, evidencia local fuera del ZIP base y decision responsable antes de abrir mas trafico.

## 2026-05-07 - Template Pack 1 handoff

- Anade M53 con gate de handoff post-compra para Template Pack 1.
- Anade `template_pack_1_handoff.py` para validar entrega, soporte inicial, primer valor y decision de escalar o pausar.
- Actualiza estado comercial a `template_pack_1_handoff_ready`.
- Mantiene datos de comprador redactados y evidencia local fuera del ZIP base.

## 2026-05-07 - Template Pack 1 purchase drill

- Anade M52 con gate de compra controlada para Template Pack 1.
- Anade `template_pack_1_purchase_drill.py` para validar pedido, pago, entrega separada, soporte y rollback.
- Actualiza estado comercial a `template_pack_1_purchase_drill_ready`.
- Mantiene evidencia de comprador redactada y el gate fuera del ZIP base.

## 2026-05-07 - Governance lookup discipline

- Anade G2 como regla operativa: consultar Project Governance o matriz de agentes antes de cada fase/mensaje de trabajo.
- Actualiza Project Governance, roadmap, ADR y README para reflejar ownership activo y checks esperados.
- Refuerza el contrato estatico de gobernanza.

## 2026-05-07 - Template Pack 1 live checkout gate

- Anade M51 con gate de publicacion controlada para Template Pack 1.
- Anade `template_pack_1_publication.py` para validar URL real, provider variant ID, email de soporte y rollback.
- Actualiza estado comercial a `template_pack_1_live_checkout_gate_ready`.
- Mantiene la publicacion bloqueada hasta recibir valores reales del proveedor.

## 2026-05-07 - Template Pack 1 public offer

- Anade M50 con oferta publica draft de Template Pack 1, FAQ, checkout wiring y macros de entrega/soporte.
- Anade `template_pack_1_offer.py` para validar copy, plan, precio, draft de checkout y claims seguros.
- Actualiza estado comercial a `template_pack_1_public_offer_ready`.
- Mantiene el add-on fuera del ZIP base y listo para conectar checkout real.

## 2026-05-07 - Template Pack 1 delivery

- Anade Template Pack 1 como add-on separado con perfiles JSON, CSV resumen, checklist y limites de soporte.
- Anade `template_pack_1_delivery.py` para validar y empaquetar el add-on.
- Actualiza estado comercial a `template_pack_1_delivery_ready`.
- Refuerza empaquetado para excluir el add-on del ZIP base y generar entrega separada.

## 2026-05-07 - Buyer onboarding support gate

- Anade recursos M48 de onboarding para comprador Pro basico.
- Anade `buyer_onboarding_support_gate.py` para validar compra, ZIP, licencia, instrucciones, FAQ, soporte y claims seguros.
- Actualiza estado comercial a `buyer_onboarding_support_gate_ready`.
- Refuerza empaquetado para excluir la herramienta interna y evidencia local.

## 2026-05-07 - Pro buyer data and template pack

- Anade `resources/pro-buyer-pack` con universo de activos, CSV importable y plantillas de activacion, soporte y primer valor.
- Anade `pro_buyer_pack.py` para validar el pack antes de publicar un ZIP comercial.
- Actualiza estado comercial a `pro_buyer_pack_ready`.
- Refuerza empaquetado para excluir la herramienta interna y evidencia local.

## 2026-05-07 - Commercial customer cockpit

- Anade endpoint read-only `GET /api/customer-cockpit`.
- Anade agregador redactado `customer_cockpit.py` para evidencia de customer success.
- Anade panel `Customer Success` en Inicio con clientes, renovaciones, tickets y oportunidades.
- Actualiza estado comercial a `customer_cockpit_ready`.

## 2026-05-07 - Specialist agent governance

- Anade `docs/PROJECT_GOVERNANCE.md` con agentes especializados, ownership, namespaces de fase y criterios de entrada M46.
- Anade ADR-0001 para registrar el modelo de gobernanza por agentes.
- Refuerza `.gitignore` para excluir `config/license.json` local.
- Actualiza roadmap y README con la baseline `G1`.

## 2026-05-07 - Customer success renewal loop

- Anade `customer_success_renewal.py` para revisar onboarding, activacion, soporte, renovacion y expansion responsable.
- Bloquea decisiones sin cliente, owner, activacion confirmada, soporte triado, notas de exito y claims seguros.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/customer_success_renewal`.
- Actualiza manifiesto a `customer_success_renewal_ready`.

## 2026-05-07 - Status and roadmap refresh

- Actualiza el estado visible del proyecto hasta M44 `hotfix_rollback_release_ready`.
- Registra el ultimo ZIP portable verificado y su SHA256 en README y roadmaps.
- Marca M45 como siguiente paso recomendado: customer success y renewal loop.
- Refresca el roadmap publico para reflejar el estado comercial real sin promesas financieras.

## 2026-05-06 - Launch assets kit

- Anade `launch_assets_kit.py` para validar ZIP, SHA256, capturas, copy, README comercial y release draft.
- Bloquea publicacion sin capturas desktop/mobile, support macro o checklist de publicacion.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/launch_assets_kit`.
- Actualiza manifiesto a `launch_assets_kit_ready`.

## 2026-05-06 - Public offer pack

- Anade `public_offer_pack.py` para validar copy, FAQ, release notes, buyer steps y pagina publica.
- Bloquea claims financieros prohibidos y oferta publica incompleta.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/public_offer_pack`.
- Actualiza manifiesto a `public_offer_pack_ready`.

## 2026-05-06 - Commercial feedback loop

- Anade `commercial_feedback_loop.py` para clasificar feedback y decidir version, precio, copy y siguiente accion.
- Bloquea cambios de oferta si falta feedback revisado, roadmap actualizado o owner de release notes.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/commercial_feedback_loop`.
- Actualiza manifiesto a `commercial_feedback_loop_ready`.

## 2026-05-06 - Post launch control

- Anade `post_launch_control.py` para revisar primeras ventas, activaciones, soporte, refunds y fallos.
- Bloquea escalado publico si hay tickets sin resolver, activaciones pendientes o fulfillment fallido.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/post_launch_control`.
- Actualiza manifiesto a `post_launch_control_ready`.

## 2026-05-06 - Limited public launch gate

- Anade `limited_public_launch.py` para validar una venta publica limitada tras el piloto.
- Bloquea `GO` sin piloto valido, checkout HTTPS, variantes reales, soporte, first sale cap y rollback owner.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/limited_public_launch`.
- Actualiza manifiesto a `limited_public_launch_ready`.

## 2026-05-06 - Pilot purchase kit

- Anade `pilot_purchase_kit.py` para preparar compra piloto privada con orden, licencia, entrega e importacion verificada.
- Consume evidencia M34 y bloquea `GO` si falta licencia firmada, manifest de entrega o confirmacion Pro en app.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/pilot_purchase_kit`.
- Actualiza manifiesto a `pilot_purchase_kit_ready`.

## 2026-05-06 - Commercial release candidate

- Anade `commercial_release_candidate.py` para validar ZIP, SHA256, readiness, clave publica y compra piloto.
- Bloquea venta publica si falta evidencia M33 `GO`, compra piloto o clave publica final.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/commercial_release_candidate`.
- Actualiza manifiesto a `commercial_release_candidate_ready`.

## 2026-05-06 - Checkout live readiness

- Anade `checkout_live_readiness.py` para validar URLs Lemon, variantes, soporte y rollback antes de venta publica.
- Bloquea si faltan `providerVariantId`, checkout HTTPS, relay HTTPS o evidencia M32 `GO`.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-tool/data/checkout_live_readiness`.
- Actualiza manifiesto a `checkout_live_readiness_ready`.

## 2026-05-06 - Render staging purchase drill

- Anade `render_staging_purchase_drill.py` para probar webhook, cola y dispatch en Render staging.
- Exige flags explicitos `--send-webhook` y `--dispatch` para operaciones mutantes.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-relay/data/render_staging_purchase_drill`.
- Actualiza manifiesto a `relay_render_staging_purchase_drill_ready`.

## 2026-05-06 - Render staging apply gate

- Anade `render_staging_apply_gate.py` para validar la aplicacion final de variables en Render.
- Exige handoff M30 `GO`, confirmacion manual y `render_staging_gate.py` remoto `GO`.
- Genera evidencia JSON/Markdown en `backend/sqx-edge-relay/data/render_staging_apply_gate`.
- Actualiza manifiesto a `relay_render_staging_apply_gate_ready`.

## 2026-05-06 - Local ingest Render handoff

- Anade `local_ingest_render_handoff.py` para convertir sesion local GO en variables listas para Render.
- Genera evidencia JSON/Markdown y `.env` local con `SQX_LOCAL_INGEST_URL`.
- Puede consumir la ultima sesion M29 o una URL explicita.
- Actualiza manifiesto a `relay_local_ingest_render_handoff_ready`.

## 2026-05-06 - Local ingest staging session

- Anade `local_ingest_staging_session.py` para orquestar backend local, tunel e ingest check.
- Mantiene arranque de backend/tunel como opt-in con `--start-backend` y `--start-tunnel`.
- Genera evidencia unica para la sesion previa a Render staging.
- Actualiza manifiesto a `relay_local_ingest_staging_session_ready`.

## 2026-05-06 - Local ingest tunnel launcher

- Anade `local_ingest_tunnel_launcher.py` para detectar `cloudflared`, `ngrok` o `localtunnel`.
- Valida el backend local en `/api/health` antes de lanzar tunel.
- Puede arrancar tunel con `--start` y parsear la URL publica de ingest.
- Actualiza manifiesto a `relay_local_ingest_tunnel_launcher_ready`.

## 2026-05-06 - Local ingest tunnel check

- Anade `local_ingest_tunnel_check.py` para validar `SQX_LOCAL_INGEST_URL` antes de configurarlo en Render.
- Comprueba politica HTTPS, `/api/health` y bundle firmado opcional hacia `/api/fulfillment/relay-ingest`.
- Guarda evidencia local en `backend/sqx-edge-relay/data/local_ingest_tunnel_check`.
- Actualiza manifiesto a `relay_local_ingest_tunnel_check_ready`.

## 2026-05-06 - Render staging secrets kit

- Anade `render_staging_secrets_kit.py` para generar secretos fuertes de staging.
- Escribe `.env` local ignorado por git y evidencia redactada.
- Bloquea placeholders, valores cortos y passwords de cuenta Render en entorno.
- Actualiza manifiesto a `relay_render_staging_secrets_kit_ready`.

## 2026-05-06 - Render staging launch pack

- Anade `render_staging_launch_pack.py` para preparar blueprint, SHA256, variables y comandos de staging.
- Integra el estado del Render staging gate en una evidencia unica.
- Guarda evidencia local en `backend/sqx-edge-relay/data/render_staging_launch_pack`.
- Actualiza manifiesto a `relay_render_staging_launch_pack_ready`.

## 2026-05-06 - Render staging gate

- Anade `render_staging_gate.py` como compuerta GO/NO-GO antes del despliegue vivo.
- Exige handshake Render `GO`, URL staging y evidencia remota `GO`.
- Guarda evidencia local en `backend/sqx-edge-relay/data/render_staging_gate`.
- Actualiza manifiesto a `relay_render_staging_gate_ready`.

## 2026-05-06 - Render credential handshake

- Anade `render_credentials_handshake.py` para validar politica de credenciales antes del deploy real.
- Bloquea el uso de password de cuenta Render mediante `RENDER_PASSWORD` o `RENDER_ACCOUNT_PASSWORD`.
- Guarda evidencia local JSON/Markdown ignorada por git.
- Actualiza manifiesto a `relay_render_credentials_handshake_ready`.

## 2026-05-06 - Render API preflight

- Anade `render_api_preflight.py` para validar API key, owner/workspace y blueprint staging.
- Amplia `.env.staging.example` con variables Render API.
- Documenta el flujo seguro sin usar password de cuenta en scripts.
- Actualiza manifiesto a `relay_render_api_preflight_ready`.

## 2026-05-06 - Render staging evidence pack

- Recomienda Render como primer proveedor de staging para el relay.
- Anade `render.staging.yaml.example`.
- Anade `staging_evidence.py` para generar decision GO/NO-GO en JSON y Markdown.
- Actualiza manifiesto a `relay_staging_execution_ready`.

## 2026-05-06 - Relay staging validation kit

- Anade `.env.staging.example` para entorno staging.
- Anade `staging_smoke.py` para validar health, config, observability, snapshot y webhook firmado.
- Anade checklist go/no-go de staging.
- Actualiza manifiesto a `relay_staging_ready`.

## 2026-05-06 - Production relay deployment package

- Anade Dockerfile, `.dockerignore` y plantillas de despliegue para el relay.
- Anade `deployment_check.py` para preflight de produccion.
- Documenta Render, Railway, Fly.io y VPS/systemd en la guia de despliegue.
- Actualiza manifiesto a `relay_production_deploy_ready`.

## 2026-05-06 - Relay observability and simulation

- Anade eventos JSONL y snapshots de cola para el relay remoto.
- Expone `GET /relay/observability` y `POST /relay/observability/snapshot`.
- Anade `simulate_purchase_flow.py` para probar compra -> relay -> dispatch -> snapshot.
- Actualiza manifiesto a `relay_observability_ready`.

## 2026-05-06 - Relay deployment hardening

- Anade `GET /relay/config-check` para validar configuracion sin exponer secretos.
- Protege endpoints operativos con `SQX_RELAY_OPERATOR_TOKEN` cuando esta configurado.
- Anade `.env.example`, `dispatch_worker.py` y `run-worker.bat` para operacion supervisada.
- Actualiza manifiesto, contratos y documentacion a estado `relay_deployment_ready`.

## 2026-05-06 - Deployable remote relay service

- Anade `backend/sqx-edge-relay` como servicio remoto separado del ZIP portable.
- Implementa cola remota con `pending`, `sent`, `failed`, dispatch y requeue.
- Conecta Lemon webhook -> relay bundle -> ingest local firmado.
- Refuerza packaging para excluir el relay del paquete final de cliente.

## 2026-05-06 - Trusted relay ingest

- Anade `POST /api/fulfillment/relay-ingest` para bundles firmados por relay remoto.
- Anade `relay_bundle.py` para preparar bundles de prueba y validar el flujo de relay.
- Refuerza exclusiones del ZIP con `relay_event_*.json` y tooling interno del relay.
- Actualiza la documentacion de M15 y las notas operativas del relay.

## 2026-05-06 - Operator retry cockpit

- Anade estados operativos y contador de intentos persistidos por request de fulfillment.
- Anade `POST /api/fulfillment/request-status` y resumen enriquecido en la cola local.
- Anade panel de fulfillment en Inicio para refrescar, procesar, ignorar y recolar requests.
- Separa la normalizacion compartida en `core/fulfillment_normalizer.py` para mantener el ZIP portable limpio.

## 2026-05-06 - Private receiver and queue

- Anade receiver privado local para webhooks de Lemon Squeezy.
- Persiste `events`, `requests` y `processed` con deduplicacion por `provider_event_id`.
- Expone endpoints locales para listar, inspeccionar y procesar requests.
- Documenta la fase M13 y la operativa del receiver.

## 2026-05-06 - Fulfillment automation bridge

- Anade `fulfillment_request.py` para validar firma y normalizar eventos de Lemon Squeezy.
- Anade `fulfill_from_request.ps1` para convertir una request en licencia firmada y entrega final.
- Refuerza exclusiones del ZIP para requests, eventos y tools internos de automatizacion.
- Documenta la fase M12 y las notas de automatizacion futura.

## 2026-05-06 - Checkout and fulfillment

- Prepara `upgrade.checkout` para Lemon Squeezy con Gumroad como fallback.
- Anade enlace de checkout en el panel Licencia, oculto hasta configurar URL real.
- Anade `prepare_customer_delivery.ps1` para preparar ZIP + licencia + instrucciones por cliente.
- Documenta M11 y runbook de entrega comercial.

## 2026-05-06 - Manual license issuer

- Anade `license_issue.py` para emitir licencias Pro firmadas en un solo comando.
- Permite cliente, email, plan, pedido, fechas, soporte y limite de equipos.
- Refuerza exclusiones de ZIP/auditoria para el issuer y artefactos locales de licencias.
- Documenta la fase M10 para primeras ventas manuales.

## 2026-05-06 - License key management

- Anade `license_keypair.ps1` para generar claves RSA offline compatibles con el firmador interno.
- Documenta M9 con el flujo manual de emision de licencias Pro.
- Refuerza `.gitignore`, empaquetado, auditoria y checklist contra claves privadas/licencias firmadas.
- Actualiza `product_manifest.json` con politica `never_commit_never_ship`.
- Regenera el ZIP portable y valida la API portable con health OK.

## 2026-05-05 - Release polish

- Anade `RELEASE_SQX_EDGE.bat` para ejecutar el checklist de entrega con doble click.
- El checklist puede exigir Git limpio con `-RequireCleanGit`.
- El release genera `dist/SQX_release_summary.txt` con ZIP, fecha, tamano y estado Git.
- El ZIP portable excluye el BAT de release interno para no confundir al usuario final.

## 2026-05-04 - Entrega profesional

Version entregable de SQX Edge Suite v1.

### Incluido

- Diseno `Premium SaaS Dark v2` con fase `Design Pro`.
- Pagina `Inicio` como cockpit operativo por defecto.
- Navegacion visual refinada para desktop y mobile.
- Tab `Estrategias` con eliminacion de cualquier estrategia visible.
- Restauracion de estrategias base eliminadas de la vista.
- Importacion, consolidacion y exportacion de estrategias.
- Project Generator con asistente de arranque y controles visuales refinados.
- Scripts analiticos y endpoints de backup integrados.
- Tests E2E opcionales con Playwright.
- Empaquetado portable con Python embebido.
- Launchers de un click: `START_SQX_EDGE.bat` y `STOP_SQX_EDGE.bat`.

### Verificacion

- Suite normal: `24 passed, 2 skipped`.
- E2E opcional con Playwright: cubre Inicio, Estrategias, eliminar/restaurar y mobile.
- ZIP portable validado en extraccion limpia.
- Runtime portable validado importando `flask` y `api.server`.

### Paquete

El ZIP final se genera en:

```text
dist/SQX_Edge_Tool_Portable_*.zip
```
# 2026-05-07 - Hotfix rollback release kit

- Anade `hotfix_rollback_release.py` para preparar acciones de hotfix, rollback, pausa o cierre.
- Valida owner, incidente, notas, target de rollback, comunicacion a clientes, soporte, verificacion y evidencia de cierre.
- Refuerza empaquetado, auditoria y checklist para excluir la nueva herramienta interna.
- Documenta M44 y el runbook de hotfix/rollback post-release.

# 2026-05-07 - Post release monitor

- Anade `post_release_monitor.py` para decidir mantener, pausar, hotfix, rollback o `scale_public`.
- Valida descargas, ventas, activaciones, tickets, incidencias severas, refunds y fallos de fulfillment.
- Refuerza empaquetado, auditoria y checklist para excluir la nueva herramienta interna.
- Documenta M43 y el runbook de monitorizacion post-release.

# 2026-05-06 - Release publication record

- Anade `release_publication_record.py` para registrar evidencia post-publicacion.
- Valida GitHub Release publicada, tag, ZIP, SHA256 coincidente, descarga probada, soporte y rollback.
- Refuerza empaquetado, auditoria y checklist para excluir la nueva herramienta interna.
- Documenta M42 y el runbook de evidencia de release publicada.

# 2026-05-06 - Public release gate

- Anade `public_release_gate.py` como compuerta final antes de publicar GitHub Release.
- Valida tag, URL HTTPS de release, ZIP adjunto, SHA256 publicado, soporte y rollback.
- Refuerza exclusiones del ZIP portable para la nueva herramienta interna.
- Documenta M41 y el runbook de publicacion controlada.

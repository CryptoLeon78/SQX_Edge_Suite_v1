# Changelog

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

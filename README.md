# SQX Edge Suite v1

Servicio web Pro para organizar el pipeline SQX Edge, generar Custom Projects `.cfx` para StrategyQuant X, crear views, preparar templates y mantener trazabilidad sin instalacion local del usuario final.

## Estado Actual

- Estado interno: UX-NAV pasa a optimizacion tab por tab; el tab activo es Workflow y el reordenamiento global queda aplazado hasta completar las optimizaciones individuales.
- Estado comercial: CANONICAL-LINK1 fija `https://sqxedgesuite.org/` como unico enlace externo; REMOTE-8C sigue siendo el GO obligatorio antes de ampliar testers.
- Estado de despliegue: Windows laptop + API localhost + Cloudflare Tunnel sigue siendo la ruta activa; el dashboard protegido queda como destino interno detras del CTA del dominio raiz.
- Ancla historica: Estado comercial: REMOTE-OPS1 valida el portatil como host Pro antes de cualquier siguiente movimiento real con testers o compradores.
- Ancla historica: Estado comercial: REMOTE-8H cycle bridge conecta la decision REMOTE-8L con el paquete de siguiente movimiento sin ejecutar expansion.
- Ancla historica: Estado de despliegue: REMOTE-SUG1 revisa la sugerencia Docker/Ubuntu del tester y mantiene el piloto activo en Windows laptop + API localhost + Cloudflare Tunnel.
- Ultimo commit base verificado antes de S5/M-pre: `d7c0757`.
- Distribucion principal: enlace unico comercial `https://sqxedgesuite.org/`; el usuario final no descarga ZIP, no ejecuta launchers y no instala Python.
- URL de acceso comunicable: `https://sqxedgesuite.org/`. El dashboard protegido bajo Cloudflare Access es infraestructura interna y no se presenta como segundo enlace al cliente.
- Fallback interno conservado: `dist/SQX_Edge_Tool_Portable_Tester_20260512_184709.zip` con SHA256 `247797085555789B3CE07E7BC7E72AC7F08B0AB7FFF8C552DB9719964EFA4CE3`.
- Siguiente paso recomendado: validar el preview de `https://sqxedgesuite.org/` en Telegram/Discord/X, mantener `app.sqxedgesuite.org` como infraestructura interna y continuar REMOTE-8C hasta cerrar la ventana limpia antes de ampliar testers.
- Ancla historica: Siguiente paso recomendado: rellenar evidencia privada REMOTE-OPS1 en `.local/remote_service/remote_ops1_laptop_readiness.local.json`; si devuelve GO, volver a REMOTE-8H private package evidence.
- Ancla historica: Siguiente paso recomendado: rellenar evidencia privada REMOTE-8H desde una decision REMOTE-8L `prepare_next_controlled_movement` y pedir aprobacion REMOTE-8I antes de ejecutar nada.
- Ultima mejora funcional: `dukas_mt5_ohlc_download.py --recent-bars` descarga 33 activos x 4 timeframes desde MT5; A56 devuelve GO con A55/A53/A54 en verde.

## Limpieza Local

Para retirar caches, builds y artefactos generados sin tocar runtime portable, venv, licencias ni evidencia privada:

```powershell
powershell -ExecutionPolicy Bypass -File tools\clean_workspace.ps1 -Aggressive
```

El modo agresivo conserva el ZIP tester mas reciente en `dist/` y elimina ZIPs/builds antiguos que se pueden regenerar.

## SQX Edge Pro

El proyecto se presenta como una edicion comercial Pro de acceso web con suscripcion mensual/anual, soporte opcional y packs de plantillas alrededor de la metodologia.

Oferta inicial prevista:

- SQX Edge Pro Mensual: acceso web protegido con email validado, sesion Pro y workspace aislado.
- SQX Edge Pro Anual: acceso web protegido con email validado, sesion Pro y workspace aislado.
- Soporte opcional: acompanamiento, configuracion operativa y revisiones de metodologia.
- Template Pack 1: pack comercial separado.

Aviso responsable: SQX Edge Pro no promete rentabilidad ni resultados financieros. La propuesta es productividad, orden, trazabilidad y reduccion de errores operativos dentro de StrategyQuant X.

Documentos comerciales:

- `docs/COMMERCIAL_README.md`
- `docs/PRIVATE_COMMERCIAL_DOCS.md`
- `docs/PRIVATE_COMMERCIAL_SPLIT_PLAN.md`
- `docs/PUBLIC_COMMERCIAL_POINTERS.md`
- `docs/private_commercial_manifest.json`
- `docs/MONETIZATION_ROADMAP.md`
- `docs/PUBLIC_ROADMAP.md`
- `docs/PROJECT_GOVERNANCE.md` consulta obligatoria antes de fases/mensajes de trabajo; incluye G4 para tratar `SQX_Institutional_Core` como repo original/first-class mediante el remoto `institutional`, sin `force push` ni espejo destructivo.
- `DISCIPLINA_OPERATIVA.md` estandar de sincronizacion y calidad para el equipo institucional.
- `resources/pro-buyer-pack/README.md`
- `resources/pro-buyer-pack/onboarding/START_HERE.md`
- `docs/sales/TEMPLATE_PACK_1_DELIVERY.md`
- `docs/sales/TEMPLATE_PACK_1_PUBLIC_OFFER.md`
- `docs/sales/TEMPLATE_PACK_1_LIVE_CHECKOUT_PUBLICATION.md`
- `docs/sales/TEMPLATE_PACK_1_PURCHASE_DRILL.md`
- `docs/sales/TEMPLATE_PACK_1_HANDOFF.md`
- `docs/sales/TEMPLATE_PACK_1_SALES_REGISTER.md`
- `docs/sales/TEMPLATE_PACK_1_FEEDBACK_COHORT.md`
- `docs/sales/TEMPLATE_PACK_1_ACTION_PLAN.md`
- `docs/sales/TEMPLATE_PACK_2_SPECS.md`
- `docs/sales/TEMPLATE_PACK_2_PURCHASE_DRILL.md`
- `docs/sales/TEMPLATE_PACK_2_HANDOFF.md`
- `docs/sales/TEMPLATE_PACK_2_SALES_REGISTER.md`
- `docs/sales/TEMPLATE_PACK_2_FEEDBACK_COHORT.md`
- `docs/sales/BUYER_READY_CHECKOUT_RELEASE.md`
- `docs/sales/PUBLIC_BUYER_PAGE_CADENCE.md`
- `docs/sales/FIRST_CONTROLLED_BUYER_LOG.md`
- `docs/sales/POST_SALE_IMPROVEMENT_LOOP.md`
- `docs/sales/POST_SALE_MICRO_UPDATES.md`
- `docs/sales/NEXT_CONTROLLED_BUYER_READINESS.md`
- `docs/sales/NEXT_CONTROLLED_BUYER_OUTCOME.md`
- `docs/sales/CONTROLLED_DISTRIBUTION_STEP.md`
- `docs/sales/CONTROLLED_DISTRIBUTION_REVIEW.md`
- `docs/sales/NEXT_BUYER_FACING_ASSET.md`
- `docs/sales/PRIVATE_ASSET_REVIEW.md`
- `docs/sales/CONTROLLED_PUBLICATION_GATE.md`
- `docs/sales/LIMITED_PUBLICATION_DRAFT.md`
- `docs/sales/OPERATOR_PUBLICATION_REVIEW.md`
- `docs/sales/MANUAL_LIMITED_PUBLICATION_RECORD.md`
- `docs/sales/MANUAL_PUBLICATION_MONITOR.md`
- `docs/sales/CONTROLLED_TRAFFIC_EXPANSION_REVIEW.md`

Nota de seguridad comercial: los documentos de venta interna, buyer logs, gates privados, evidencias de checkout/soporte y plantillas operativas ya fueron migrados al repositorio privado `CryptoLeon78/sqx-edge-commercial-private`. El repo publico conserva arquitectura, releases, claims seguros y punteros de trazabilidad; `docs/MONETIZATION_*`, `docs/sales/*` y los packs Pro bajo `resources/` son stubs publicos redactados.

Acceso remoto Pro previsto:

- REMOTE-0 fija el roadmap de servicio remoto en `docs/REMOTE_SERVICE_ROADMAP.md`.
- Ancla historica: Estado comercial: REMOTE-0 inicia el giro oficial a acceso web Pro.
- REMOTE-1 fija la base de portatil servidor en `docs/REMOTE_1_LAPTOP_SERVER_BASELINE.md`.
- REMOTE-2 fija el tunel protegido en `docs/REMOTE_2_CLOUDFLARE_TUNNEL_ACCESS.md`.
- CANONICAL-LINK1 fija `https://sqxedgesuite.org/` como unico enlace comercial y de soporte; los subdominios de app/preview quedan como infraestructura interna o fallback tecnico.
- REMOTE-2B fija acceso completo `tester_free` para testers aprobados y recomienda privatizar `origin` e `institutional` antes de venta en `docs/REMOTE_2B_TESTER_GRANTS_REPO_PRIVACY.md`.
- REMOTE-3A fija la base backend `remote-access-v1`, endpoint `/api/remote/access/status`, ejemplo local de entitlements y privacidad de repos verificada en `docs/REMOTE_3A_REMOTE_ACCESS_FOUNDATION.md`.
- REMOTE-3B fija la sesion de app `remote-session-v1`, cookie `__Host-sqx_remote_session`, endpoints `/api/remote/session/login`, `/api/remote/session/status`, `/api/remote/session/logout` y verificacion de clave tester en `docs/REMOTE_3B_APP_SESSION_GRANT_KEY.md`.
- REMOTE-3C fija el webhook de pago firmado `remote-payment-webhook-v1`, secreto privado `SQX_REMOTE_PAYMENT_WEBHOOK_SECRET`, endpoint `/api/remote/payment/webhook`, endpoint piloto `/api/remote/protected/write-pilot` y altas/cancelaciones idempotentes en `docs/REMOTE_3C_PAID_WEBHOOK_PROTECTED_WRITE.md`.
- REMOTE-4 fija el workspace aislado `remote-workspace-v1`, endpoint `/api/remote/workspace/status`, `SQX_REMOTE_WORKSPACES_ROOT` privado y el write-pilot auditado dentro del workspace en `docs/REMOTE_4_WORKSPACE_ISOLATION.md`.
- REMOTE-PERSIST1A fija persistencia remota de Plan Mining, Pipeline State y Strategy Control en `remote-workspace-state-v1` dentro de `<workspace>/config/workspace_state.sqlite`.
- REMOTE-PERSIST1B fija outputs de Project Generator en `remote-workspace-output-v1`, con `.cfx` por usuario en `<workspace>/outputs` y bloqueo de `output` remoto manual para evitar colisiones entre usuarios.
- REMOTE-PERSIST1C fija Template Maker como estado workspace-scoped en `remote-template-maker-state-v1`, con estrategias/configuracion por usuario en `<workspace>/config/template_maker.sqlite` y IndexedDB solo como cache de compatibilidad.
- REMOTE-PERSIST1D fija backups/restores de Control Panel en `remote-state-backup-v1`, con snapshots por usuario en `<workspace>/config/state_backups` y filtrado backend de claves sensibles.
- REMOTE-PERSIST1E fija presets propios de SQX Views en `remote-workspace-state-v1`, con `sqx_view_creator_presets_v1` por usuario en `<workspace>/config/workspace_state.sqlite` y `localStorage` solo como cache de compatibilidad.
- CFX-BASE142 repara los templates base `Capa1_Long.cfx` y `Capa2_Base.cfx` para que abran en SQX 142 con recursos/broker resolubles y sin sesiones fantasma `Futures_Commodities1` antes de ajustar parametros default.
- REMOTE-5 fija el panel `remote-pro-panel` en Home, consumiendo `/api/remote/access/status`, `/api/remote/session/status`, `/api/remote/workspace/status` y `/api/health` para mostrar acceso Pro, readiness remoto, workspace corto y privacidad en `docs/REMOTE_5_REMOTE_UX.md`.
- REMOTE-6 fija `remote-security-v1`, endpoint `/api/remote/security/status`, endpoint `/api/remote/security/audit/recent`, `SQX_REMOTE_SECURITY_POLICY_PATH`, rate limits, kill switch, revocacion, bloqueo por hash, watermark remoto y auditoria redaccionada en `docs/REMOTE_6_SECURITY_ABUSE_CONTROLS.md`.
- REMOTE-SEC2 fija `remote-access-control-v1`, cookie de dispositivo `__Host-sqx_device_id`, 2 contextos confiables por identidad, bloqueo de sesiones copiadas a otro contexto y aprobacion operador para contextos extra en `docs/REMOTE_SEC2_CREDENTIAL_SHARING_CONTROL.md`.
- REMOTE-7 fija la oferta web Pro mensual/anual, el onboarding sin instalacion, FAQ, soporte, acceso `tester_free` y portable como fallback interno en `docs/REMOTE_7_MONETIZATION_REWRITE.md`.
- REMOTE-8 fija `remote-controlled-pilot-v1`, herramienta `backend/sqx-edge-tool/tools/remote_controlled_pilot.py`, evidencia ignorada `.local/remote_service/remote8_controlled_pilot/` y `Controlled Pilot Gate` en `docs/REMOTE_8_CONTROLLED_PILOT.md`.
- REMOTE-8B fija `remote-live-pilot-evidence-v1`, herramienta `backend/sqx-edge-tool/tools/remote_live_pilot_evidence.py`, ejemplo `docs/examples/remote8b_live_pilot_evidence.local.example.json`, evidencia ignorada `.local/remote_service/remote8b_live_pilot_evidence*` y `Live Pilot Evidence Gate` en `docs/REMOTE_8B_LIVE_PILOT_EVIDENCE.md`.
- REMOTE-8C fija `remote-first-user-observation-v1`, herramienta `backend/sqx-edge-tool/tools/remote_first_user_observation.py`, ejemplo `docs/examples/remote8c_first_user_observation.local.example.json`, evidencia ignorada `.local/remote_service/remote8c_first_user_observation*` y `First User Observation Gate` en `docs/REMOTE_8C_FIRST_USER_OBSERVATION.md`.
- REMOTE-SUPPORT1 añade intake seguro de incidencias en Control Panel con `support-incident-v1`, endpoint `/api/support/incidents`, helper `tools/remote_support_status.ps1` y evidencia local ignorada `.local/remote_service/support_cases/`.
- REMOTE-8D fija `remote-tiny-cohort-activation-v1`, herramienta `backend/sqx-edge-tool/tools/remote_tiny_cohort_activation.py`, ejemplo `docs/examples/remote8d_tiny_cohort_activation.local.example.json`, evidencia ignorada `.local/remote_service/remote8d_tiny_cohort_activation*` y `Tiny Cohort Activation Package Gate` en `docs/REMOTE_8D_TINY_COHORT_ACTIVATION.md`.
- REMOTE-8E fija `remote-tiny-cohort-execution-v1`, herramienta `backend/sqx-edge-tool/tools/remote_tiny_cohort_execution.py`, ejemplo `docs/examples/remote8e_tiny_cohort_execution.local.example.json`, evidencia ignorada `.local/remote_service/remote8e_tiny_cohort_execution*` y `Tiny Cohort Manual Execution Record Gate` en `docs/REMOTE_8E_TINY_COHORT_EXECUTION.md`.
- REMOTE-8F fija `remote-tiny-cohort-monitoring-v1`, herramienta `backend/sqx-edge-tool/tools/remote_tiny_cohort_monitoring.py`, ejemplo `docs/examples/remote8f_tiny_cohort_monitoring.local.example.json`, evidencia ignorada `.local/remote_service/remote8f_tiny_cohort_monitoring*` y `Tiny Cohort Monitoring Gate` en `docs/REMOTE_8F_TINY_COHORT_MONITORING.md`.
- REMOTE-8G fija `remote-tiny-cohort-decision-review-v1`, herramienta `backend/sqx-edge-tool/tools/remote_tiny_cohort_decision_review.py`, ejemplo `docs/examples/remote8g_tiny_cohort_decision_review.local.example.json`, evidencia ignorada `.local/remote_service/remote8g_tiny_cohort_decision_review*` y `Tiny Cohort Decision Review Gate` en `docs/REMOTE_8G_TINY_COHORT_DECISION_REVIEW.md`.
- REMOTE-8H fija `remote-next-controlled-movement-package-v1`, herramienta `backend/sqx-edge-tool/tools/remote_next_controlled_movement_package.py`, ejemplo `docs/examples/remote8h_next_controlled_movement_package.local.example.json`, evidencia ignorada `.local/remote_service/remote8h_next_controlled_movement_package*` y `Next Controlled Movement Package Gate` en `docs/REMOTE_8H_NEXT_CONTROLLED_MOVEMENT_PACKAGE.md`; el ciclo actual usa REMOTE-8L como fuente y conserva REMOTE-8G solo como compatibilidad historica.
- REMOTE-8I fija `remote-next-controlled-movement-execution-approval-v1`, herramienta `backend/sqx-edge-tool/tools/remote_next_controlled_movement_execution_approval.py`, ejemplo `docs/examples/remote8i_next_controlled_movement_execution_approval.local.example.json`, evidencia ignorada `.local/remote_service/remote8i_next_controlled_movement_execution_approval*` y `Next Controlled Movement Execution Approval Gate` en `docs/REMOTE_8I_NEXT_CONTROLLED_MOVEMENT_EXECUTION_APPROVAL.md`.
- REMOTE-8J fija `remote-next-controlled-movement-manual-execution-v1`, herramienta `backend/sqx-edge-tool/tools/remote_next_controlled_movement_manual_execution.py`, ejemplo `docs/examples/remote8j_next_controlled_movement_manual_execution.local.example.json`, evidencia ignorada `.local/remote_service/remote8j_next_controlled_movement_manual_execution*` y `Next Controlled Movement Manual Execution Gate` en `docs/REMOTE_8J_NEXT_CONTROLLED_MOVEMENT_MANUAL_EXECUTION.md`.
- REMOTE-8K fija `remote-next-controlled-movement-monitoring-v1`, herramienta `backend/sqx-edge-tool/tools/remote_next_controlled_movement_monitoring.py`, ejemplo `docs/examples/remote8k_next_controlled_movement_monitoring.local.example.json`, evidencia ignorada `.local/remote_service/remote8k_next_controlled_movement_monitoring*` y `Next Controlled Movement Monitoring Gate` en `docs/REMOTE_8K_NEXT_CONTROLLED_MOVEMENT_MONITORING.md`.
- REMOTE-8L fija `remote-post-monitoring-decision-review-v1`, herramienta `backend/sqx-edge-tool/tools/remote_post_monitoring_decision_review.py`, ejemplo `docs/examples/remote8l_post_monitoring_decision_review.local.example.json`, evidencia ignorada `.local/remote_service/remote8l_post_monitoring_decision_review*` y `Post Monitoring Decision Review Gate` en `docs/REMOTE_8L_POST_MONITORING_DECISION_REVIEW.md`.
- REMOTE-OPS1 fija `remote-ops1-laptop-readiness-v1`, herramienta `backend/sqx-edge-tool/tools/remote_ops1_laptop_readiness.py`, ejemplo `docs/examples/remote_ops1_laptop_readiness.local.example.json`, evidencia ignorada `.local/remote_service/remote_ops1_laptop_readiness*` y `Laptop Production Readiness Drill Gate` en `docs/REMOTE_OPS1_LAPTOP_READINESS_DRILL.md`.
- REMOTE-OPS1B - Cloudflare Operator Handoff fija `docs/REMOTE_OPS1B_CLOUDFLARE_OPERATOR_HANDOFF.md`, `tools/remote_tunnel_operator_handoff.ps1`, `docs/examples/cloudflared-config.local.example.yml` y archivos locales ignorados `.local/remote_service/cloudflare_tunnel_operator_handoff.local.md` / `.local/remote_service/cloudflared-config.local.yml.template`.
- REMOTE-SUG1 incorpora las mejores ideas de hardening de la propuesta tester en `docs/REMOTE_SUG1_DEPLOYMENT_HARDENING_REVIEW.md`: zero ingress, Cloudflare Access/Tunnel, persistencia, backup y resiliencia. Docker/Linux queda como ruta futura REMOTE-9, no como requisito actual para testers ni compradores.
- La comunicacion de seguridad y privacidad vive en `docs/REMOTE_SERVICE_SECURITY_PRIVACY_COPY.md`.
- El piloto corre en portatil 24/7 mediante dominio propio, Cloudflare Tunnel y Cloudflare Access.
- Los testers aprobados podran usar todas las funcionalidades sin pago mientras su grant `tester_free` este activo, pero siempre autenticados, auditados y revocables como cualquier usuario.
- Recomendacion comercial: convertir `SQX_Edge_Suite_v1` y `SQX_Institutional_Core` a repos privados antes de activar ventas, salvo decision explicita de mantener una estrategia public-source.
- Estado de repos: `SQX_Edge_Suite_v1` e `SQX_Institutional_Core` verificados como privados por GitHub CLI el 2026-05-16.
- Cada usuario pagado tendra workspace aislado para config, imports, outputs, exports y auditoria.
- El navegador no selecciona rutas locales de SQX; las rutas SQX, `data.db`, templates y BlockSettings se gestionan en el servidor.
- La comunicacion al usuario se basa en entorno controlado, auditado y aislado; no se promete riesgo cero.

Operativa local REMOTE-1:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_service_preflight.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_service_watchdog.ps1 -Once -NoStart
```

Operativa privada REMOTE-2:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_operator_handoff.ps1 -CloudflaredPath C:\Tools\cloudflared\cloudflared.exe
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_preflight.ps1 -RequireEvidence
powershell -NoProfile -ExecutionPolicy Bypass -File tools\remote_tunnel_smoke.ps1 -ProtectedUrl "<private protected url>"
```

Arranque operador REMOTE-RUNBOOK1:

```bat
START_SQX_EDGE_REMOTE.bat
STOP_SQX_EDGE_REMOTE.bat
```

`START_SQX_EDGE_REMOTE.bat` abre un monitor visual visible de Backend/Tunnel, arranca los servicios en segundo plano y muestra `OK todo en marcha` cuando el portatil esta listo para el enlace protegido. `STOP_SQX_EDGE_REMOTE.bat` abre el mismo monitor y detiene solo el backend/tunel de este proyecto.

Operativa privada REMOTE-OPS1:

```powershell
Copy-Item docs\examples\remote_ops1_laptop_readiness.local.example.json .local\remote_service\remote_ops1_laptop_readiness.local.json
python backend\sqx-edge-tool\tools\remote_ops1_laptop_readiness.py --evidence .local\remote_service\remote_ops1_laptop_readiness.local.json
```

REMOTE-OPS1 no ejecuta expansion, no invita usuarios, no cambia grants, no envia emails y no publica enlaces. Solo valida que el portatil esta preparado para volver a REMOTE-8H con evidencia privada.

Nota de despliegue REMOTE-SUG1: no se debe anadir `Dockerfile`, `docker-compose.yml` ni `.dockerignore` en la raiz del proyecto durante el piloto Windows. La ruta activa sigue siendo portatil Windows con SQX local, backend en `127.0.0.1`, Cloudflare Tunnel y Cloudflare Access. Docker/Linux queda aparcado como hardening futuro cuando la compatibilidad con SQX, workspaces y backups este probada.

Portal tester Pro previsto (historico):

- T1 define un futuro repo privado `SQX_Edge_Tester_Portal` para alojar en Vercel una experiencia tester Pro controlada.
- T2 deja un bootstrap seguro en `templates/SQX_Edge_Tester_Portal/`, listo para copiar a un repo privado cuando lo autoricemos.
- T3 define contratos de testers, password hashing Argon2id, cookie `__Host-sqx_tester_session`, tokens de renovacion de un uso, eventos de auditoria y limites de secretos.
- T4 anade un prototipo local de login/sesion desactivado por defecto con middleware para rutas protegidas y logout.
- T5 anade gates `tester_pro` de servidor para features Pro: dashboard completo, Strategy Builder, Project Generator, Views, handoff exports y soporte.
- T6 anade caducidad de 15 dias, estados `pending_renewal`/`expired`/`denied`/`blocked` y preview manual approve/deny/block sin mutar datos reales.
- T7 anade consola admin protegida para preview de crear, renovar, denegar, bloquear y revisar auditoria sin persistir datos reales.
- T8 anade rate-limit contract, headers reforzados, watermark visible, kill switch y checklist de Deployment Protection antes de cualquier preview.
- T9 intento el preflight externo de Vercel con autorizacion explicita; el deploy quedo bloqueado por token local invalido y se anadio script de preflight reproducible.
- T9b autentico Vercel, intento deploy y lo elimino al detectar alias de produccion; no hay deployment activo ni URL publica operativa.
- T9c anade `audit:vercel-protection` y deja el estado `NO_GO_PROTECTION_NOT_VERIFIED` hasta verificar Deployment Protection por API/dashboard.
- T9d activa/verifica Vercel Authentication Standard Protection y deja `GO_PROTECTION_VERIFIED` sin desplegar ni publicar URL.
- T9e reintento preview con proteccion activa; T9e reintenta deploy sin `--prod`, Vercel vuelve a reportar produccion y se elimina inmediatamente; no queda deployment activo ni URL publica operativa.
- T9f anade `proof:vercel-preview-path` para bloquear cualquier avance hasta que exista una ruta Git/PR preview privada, protegida y separada de produccion.
- T9g crea el repo privado `SQX_Edge_Tester_Portal`, prepara `main` y `tester-preview`, conecta Vercel por GitHub y verifica `GO_GIT_PREVIEW_PATH_READY` sin deploy manual.
- T10 intento preview interno desde `tester-preview`. T10 dispara el primer piloto interno desde `tester-preview`, detecta `target=production`, elimina el deployment y deja T10b como correccion obligatoria antes de compartir URL.
- T10b anade `vercel-target-guard.mjs` al `prebuild`, bloquea `production/tester-preview` con codigo 43, elimina el deployment fallido y deja el proyecto sin deployment activo ni dominios.
- T10c define una ruta API preview explicita sin desplegar; T10c anade `proof:vercel-explicit-preview`, confirma por API `productionBranch=main` y prepara una ruta explicita con `target: "preview"` sin desplegar ni compartir URL.
- T10d ejecuta una unica preview API explicita, detecta que Vercel devuelve `target=production`, elimina el deployment y deja T10e como correccion obligatoria antes de compartir URL.
- T10e anade `proof:vercel-omitted-target-preview`; T10e intento preview API con `target` omitido, detecta que Vercel vuelve a devolver `target=production`, elimina el deployment y deja T10f como recreacion/separacion obligatoria.
- T10f anade `proof:vercel-preview-project-separation`; T10f separo un proyecto preview Vercel nuevo sin deployment, sin dominios y sin Git link, y deja T10g como link/proof obligatorio antes de publicar cualquier URL.
- T10g anade `proof:vercel-linked-preview-project`. T10g linko el repo privado del portal tester al proyecto preview separado, confirma `main` como production branch, `tester-preview` como no-produccion, Deployment Protection activo y sin deployment ni dominios.
- T10h anade `proof:vercel-protected-preview-rollback`. T10h intento una preview protegida desde el proyecto separado, detecta `target=production`, confirma que el guard T10b bloqueo el build con codigo 43, elimina el deployment y deja T10i como correccion obligatoria.
- T10i anade `proof:vercel-cli-default-preview-route`; T10i para corregir o reemplazar la ruta preview de Vercel antes de otro intento de deployment adopta `vercel deploy` sin `--prod` ni `--target`, conserva el proyecto sin deployment/dominios y deja T10j como intento unico con rollback inmediato.
- T10i corrigio la siguiente ruta preview hacia `vercel deploy` por defecto como prueba sin deployment.
- T10j anade `proof:vercel-cli-default-preview-command-rollback`; T10j para ejecutar una unica preview CLI default detecta que `--skip-domain` solo vale para produccion, no crea deployment ni URL, y deja T10k como intento corregido sin `--skip-domain`.
- T10j ejecuto el comando CLI default aprobado y lo cerro sin deployment creado.
- T10k anade `proof:vercel-cli-default-preview-rollback`; T10k ejecuta una preview CLI default sin `--skip-domain`, Vercel vuelve a reportar `target=production`, el guard bloquea con codigo 43, se elimina el deployment y T10l queda como investigacion sin deploy.
- T10k ejecuto una preview CLI default corregida y la cerro como rollback seguro.
- T10l anade `proof:vercel-route-investigation`; investiga Vercel sin deploy, detecta `project.productionBranch` ausente, `project.targets` vacio y senales de ruta produccion, y deja T10m como correccion/reemplazo sin deploy previo.
- T10l investigo Vercel sin deploy y dejo T10m para correccion manual/API o ruta alternativa antes de cualquier deployment.
- T10m endurecio la configuracion Vercel por API sin deploy y dejo T10n para proof no-deploy de target/ruta antes de cualquier deployment.
- T10m anade `proof:vercel-config-hardening`; aplica por API `autoAssignCustomDomains=false` y `previewDeploymentsDisabled=false` sin deploy, mantiene el proyecto sin dominios/deployments y deja T10n como proof/reemplazo de ruta antes de cualquier deployment.
- T10n anade `proof:vercel-route-decision`; confirma sin deploy que la ruta Vercel actual no debe usarse para rollout y deja T10o como reemplazo/proof provider-level antes de cualquier deployment.
- T10n rechaza la ruta Vercel actual y deja T10o para ruta alternativa o proof manual/provider-level antes de cualquier deployment.
- T10o anade `proof:replacement-route-contract`; selecciona `fresh_staging_route_with_no_deploy_preflight`, mantiene rechazada la ruta Vercel actual y deja T10p solo con aprobacion explicita antes de crear/verificar cualquier ruta externa.
- T10o deja lista una ruta alternativa contractual sin deploy y T10p para crear/verificar una ruta staging nueva queda condicionado a aprobacion explicita.
- T10p anade `proof:fresh-staging-route-preflight`; deja preparado el gate local sin API/deploy/proyecto/URL y reserva T10q para una aprobacion exacta de accion externa sin deployment.
- T10p deja listo el preflight local de ruta staging fresca y T10q para pedir aprobacion exacta queda como siguiente gate externo sin deployment.
- T10q anade `proof:fresh-staging-route-access-check`; registra aprobacion explicita, verifica lectura Vercel por app conectada y bloquea creacion/verificacion porque la CLI espera login interactivo y no hay `VERCEL_TOKEN`.
- T10q registra aprobacion explicita y T10r para autenticar Vercel CLI queda completado antes de crear/verificar la ruta staging.
- T10r anade `proof:fresh-staging-project-created`; crea/verifica `sqx-edge-tester-staging` sin deploy, sin dominios, sin Git link y sin URL publicada, dejando T10s como gate de proteccion/settings.
- T10s anade `proof:staging-protection-verified`; confirma SSO Deployment Protection `all_except_custom_domains`, Git fork protection, cero deployments y cero dominios antes de cualquier Git link o deploy.
- T10t anade `proof:staging-local-link`; enlaza localmente el repo privado del portal tester a `sqx-edge-tester-staging` mediante metadata ignorada, manteniendo cero deployments, cero dominios y ninguna URL publicada.
- T10u anade `proof:staging-deployment-readiness`; prepara el gate no-deploy para un unico deployment staging controlado con inspeccion de target/aliases y rollback obligatorio antes de compartir cualquier URL.
- T10v anade `proof:controlled-staging-deploy-rollback`; ejecuta un unico intento staging, Vercel devuelve `target=production`, el guard bloquea y se elimina el deployment fallido sin publicar URL.
- T10w anade `proof:provider-target-mapping-investigation`; rechaza la ruta CLI default y prepara `vercel deploy --target=preview --force --yes --format json` como unico siguiente intento controlado.
- T10x anade `proof:explicit-preview-target-rollback`; prueba la ruta explicita `--target=preview`, Vercel vuelve a devolver `target=production`, el guard bloquea y se elimina el deployment fallido.
- T10x prueba `--target=preview` como intento unico y queda cerrado como rollback limpio.
- T10y anade `proof:no-deploy-provider-dashboard-decision`; T10y para dejar de reintentar Vercel CLI pausa la ruta y selecciona correccion provider-dashboard sin deploy antes de cualquier nuevo intento.
- T10z para preparar el paquete/checklist provider-dashboard sin deploy quedo como siguiente paso de T10y.
- T10z anade `proof:provider-dashboard-correction-package`; deja checklist y formato de evidencia para correccion provider-dashboard sin deploy antes de cualquier nuevo intento.
- T10aa para registrar evidencia provider-dashboard sin deploy quedo como siguiente paso de T10z.
- T10aa anade `proof:provider-dashboard-evidence-record`; confirma por CLI cero deployments/dominios/proteccion activa, pero deja `NO_GO_PROVIDER_CANNOT_PROVE_PREVIEW_TARGET` hasta revision manual de dashboard. T10ab para ingerir evidencia manual de dashboard queda cerrado en la siguiente fase.
- T10ab anade `proof:manual-dashboard-evidence-ingest`; ingiere evidencia manual de dashboard, confirma Git no conectado, production branch no visible, correccion no visible y `next_deployment_allowed=unknown`, por lo que decide `NO_GO_REPLACE_VERCEL_TESTER_ROUTE`. T10ac para comparar y seleccionar una ruta tester protegida queda completado sin deploy.
- T10ac anade `proof:replacement-tester-route-options`; compara rutas no-Vercel y selecciona Cloudflare Pages preview + Cloudflare Access email OTP como candidata, sin crear proyecto, deploy, URL ni politicas externas. T10ad para preparar el preflight Cloudflare Access queda completado sin accion externa.
- T10ad anade `proof:cloudflare-access-preflight`; define ramas, Access OTP, no custom domains, no URL y una barrera T10ae de compatibilidad runtime Next.js antes de crear nada en Cloudflare. T10ae para resolver la compatibilidad runtime Cloudflare localmente queda completado sin proveedor.
- T10ae anade `proof:cloudflare-runtime-compatibility`; inventaria middleware y 7 API route handlers, rechaza static export y selecciona Cloudflare Workers/OpenNext como runtime candidato sin instalar dependencias ni tocar proveedor.
- T10af anade `proof:opennext-cloudflare-adapter`; prepara `wrangler.jsonc`, `open-next.config.ts`, `.dev.vars.example`, `@opennextjs/cloudflare`, `wrangler` y scripts locales `cf:build`, `cf:preview`, `cf:typegen` sin exponer `cf:deploy` ni crear recursos Cloudflare.
- T10ag anade `proof:opennext-local-smoke`; confirma que el build OpenNext genera worker/assets y que preview WSL/Linux devuelve `/api/health` 200, mientras preview nativo Windows queda como `NO_GO_NATIVE_WINDOWS_PREVIEW_ROUTE_500`.
- T10ah anade `proof:next-proxy-migration`; documenta que `proxy.ts` queda bloqueado para esta ruta porque OpenNext/Cloudflare no soporta Node Middleware, conserva `middleware.ts` y mantiene la fase sin deploy ni recursos Cloudflare.
- T10ai anade `proof:cloudflare-provider-project-preflight`; prepara contrato Cloudflare Workers/OpenNext + Access OTP sin deploy, sin proyecto, sin politica Access, sin Git link y sin URL tester.
- T10aj anade `proof:cloudflare-project-shell`; registra el NO-GO seguro por falta de autenticacion Wrangler/ruta shell sin deploy y memoriza T10ajb-T10an/T11/T12.
- T10ajb anade `proof:cloudflare-auth-handoff`; documenta login/API token local, crea ejemplo de evidencia Cloudflare sin secretos e ignora `cloudflare-shell-evidence.local.json` para T10ajc.
- T10ajc anade `proof:cloudflare-shell-evidence-ingest`; ingiere evidencia local si existe, devuelve NO-GO seguro porque aun no existe y mantiene T10ak bloqueada.
- T10ajd anade `proof:cloudflare-shell-evidence-capture`; deja checklist manual/autenticado exacto para rellenar evidencia local ignorada y rerun de T10ajc.
- T10aje anade `proof:cloudflare-readonly-shell-capture`; con Wrangler autenticado, Cloudflare devuelve `worker_not_found` para deployments/versions/secrets del worker propuesto.
- T10ajf anade `proof:cloudflare-shell-creation-decision`; documenta que `wrangler versions upload` no sirve para el primer Worker y que el siguiente gate T10ajg debe preparar un `wrangler deploy` exacto, sin ejecutarlo ni compartir URL.
- T10ajg anade `proof:cloudflare-first-deploy-approval-gate`; deja la frase de aprobacion, comando exacto, prechecks, postchecks y cleanup para T10ajh sin crear recursos Cloudflare.
- T10ajh anade `proof:cloudflare-first-deploy-readiness`; instala dependencias locales, versiona `package-lock.json`, confirma `npm run cf:build` y mantiene el deploy bloqueado hasta aprobacion exacta.
- T10aji anade `proof:cloudflare-first-deploy-rollback`; intenta el primer deploy, detecta requisito de subdominio/ruta Cloudflare, elimina el Worker y deja T10ajj como decision de ruta antes de reintento.
- T10ajj anade `proof:cloudflare-route-onboarding-decision`; decide custom route/domain protegido como opcion preferente, desactiva `workers_dev` y `preview_urls`, mantiene el Worker inexistente y deja T10ajk como ruta/onboarding + Access antes de cualquier redeploy.
- T10ajk anade `proof:cloudflare-route-access-precreate`; verifica Wrangler autenticado con Worker inexistente, crea ejemplo local seguro para evidencia de ruta/Access y mantiene T10ak bloqueado hasta que T10ajl seleccione hostname/zona privada o onboarding `workers.dev`.
- T10ajl anade `proof:cloudflare-hostname-zone-selection`; prepara evidencia local ignorada para hostname/zona o `workers.dev` protegido, mantiene `workers_dev=false` y `preview_urls=false`, y mantiene T10ak bloqueado hasta que esa evidencia privada devuelva GO.
- T10ajl2 anade `prepare:cloudflare-hostname-zone-selection`; crea/revisa el archivo local ignorado y bloquea campos sensibles como hostname, zone ID, emails, URL, tokens o claves antes de permitir T10ak.
- T10ajm anade `proof:cloudflare-workers-dev-shell-gate`; al no haber dominio ni Worker existente, prepara un shell Worker 404/no-app con config dedicada `workers_dev=true`, mantiene la app real con `workers_dev=false`, y deja T10ajn como unico paso externo para crear el target antes de Access.
- T10ajn anade `proof:cloudflare-workers-dev-shell-deploy`; crea el shell target con Wrangler, verifica respuesta 404/no-app, bloquea T10ak porque Access API requiere permisos `Access: Apps and Policies Write` o habilitacion manual en dashboard.
- T10ajo anade `proof:cloudflare-workers-dev-access`; verifica que Cloudflare Access intercepta el shell `workers.dev` antes del cuerpo 404/no-app y desbloquea T10ak como fase de registro/verificacion de app/policy, sin deploy real ni URL tester.
- T10ak anade `proof:cloudflare-access-policy-boundary`; registra/verifica con evidencia local ignorada que Access app/policy protege el shell y permite solo usuarios piloto aprobados, sin deploy real, URL tester ni emails en Git.
- T10al prepara el gate exacto de deploy real controlado y anade `proof:cloudflare-controlled-real-app-deploy-gate`; deja frase de aprobacion exacta, comando futuro, prechecks, smoke post-deploy y rollback, sin ejecutar deploy real ni publicar URL tester.
- T10am anade `proof:cloudflare-real-app-deploy-result`; ejecuta el deploy autorizado, registra que la version real queda subida sin target publico, mantiene Access en verde y bloquea URL/testers hasta T10an.
- T10an selecciona `workers.dev` protegido por Cloudflare Access como target tester y anade `proof:cloudflare-protected-tester-publication-target`; mantiene `workers_dev=false` hasta aprobacion exacta T10ao.
- T10ao prepara el preflight de publicacion controlada y anade `proof:cloudflare-controlled-workers-dev-publication-preflight`; mantiene `workers_dev=false`, URL/testers bloqueados y mueve el deploy real a T10ap con aprobacion exacta.
- T10ap publica el target `workers.dev` con un unico deploy autorizado, verifica Cloudflare Access antes de cualquier cuerpo de app y anade `proof:cloudflare-workers-dev-publication-result`; mantiene URL/testers bloqueados.
- T10aq prepara handoff controlado de acceso tester y anade `proof:tester-access-handoff`; mantiene URL, emails, cuentas y canales privados fuera de Git.
- T10ar prepara el gate privado de activacion de cuentas tester y anade `proof:tester-account-activation-gate`; mantiene URL, emails, credenciales, invitaciones y evidencias reales fuera de Git.
- T10as ingiere evidencia privada de activacion tester con `proof:tester-activation-evidence-ingest`; el resultado esperado sin archivo local es `NO_GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_ACTIVATION_EVIDENCE_SAFE_NO_GIT_LEAK`.
- T10at prepara el gate privado para compartir URL tester con `proof:tester-url-share-approval-gate`; el resultado esperado sin aprobacion local es `NO_GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_URL_SHARE_APPROVAL_READY_NO_GIT_LEAK`.
- T10au prepara el gate de primer smoke privado tester con `proof:tester-first-smoke-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_FIRST_TESTER_SMOKE_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_FIRST_TESTER_SMOKE_PASSED_NO_GIT_LEAK`.
- T10av prepara el gate de expansion privada a micro-cohorte tester con `proof:tester-cohort-expansion-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_COHORT_EXPANSION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_COHORT_EXPANSION_READY_NO_GIT_LEAK`.
- T10aw prepara intake privado de feedback tester con `proof:tester-feedback-intake-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_FEEDBACK_INTAKE_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_FEEDBACK_INTAKE_READY_NO_GIT_LEAK`.
- T10ax prepara triage privado de feedback tester con `proof:tester-feedback-triage-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_FEEDBACK_TRIAGE_READY_NO_GIT_LEAK`.
- T10ay prepara action plan privado de feedback tester con `proof:tester-action-plan-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_ACTION_PLAN_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_ACTION_PLAN_READY_NO_GIT_LEAK`.
- T10az prepara ejecucion privada de acciones tester con `proof:tester-action-execution-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_ACTION_EXECUTION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_ACTION_EXECUTION_READY_NO_GIT_LEAK`.
- T10ba prepara validacion privada de resultados tester con `proof:tester-result-validation-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_RESULT_VALIDATION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_RESULT_VALIDATION_READY_NO_GIT_LEAK`.
- T10bb prepara decision privada de iteracion tester con `proof:tester-iteration-decision-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_ITERATION_DECISION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_ITERATION_DECISION_READY_NO_GIT_LEAK`.
- T10bc prepara siguiente iteracion privada tester con `proof:tester-next-iteration-gate`; el resultado esperado sin evidencia local es `NO_GO_PRIVATE_TESTER_NEXT_ITERATION_EVIDENCE_MISSING` y el GO seguro es `GO_PRIVATE_TESTER_NEXT_ITERATION_READY_NO_GIT_LEAK`.
- TL1 resume el lanzamiento tester con `proof:tester-launch-candidate`; el resultado esperado sin evidencia local es `NO_GO_TESTER_LAUNCH_PRIVATE_EVIDENCE_MISSING` y el GO seguro es `GO_TESTER_LAUNCH_CANDIDATE_READY_NO_GIT_LEAK`.
- El acceso sera por usuario tester, email y password, con ciclo de renovacion de 15 dias y aprobacion/denegacion manual.
- Vercel Deployment Protection sera capa adicional, no sustituto de auth propia por tester.
- El nuevo ownership `Access/Security Gatekeeper` cubre auth, sesiones, expiracion, auditoria, watermarks, secretos Vercel y proteccion anti-distribucion.
- No se crearan testers, se enviaran emails ni se publicaran URLs Vercel sin autorizacion explicita.

Export privado preparado:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\private_commercial_split.py
```

El export se genera en `commercial-private/sqx-edge-commercial-private/`, carpeta ignorada por git.

El export privado local ya fue inicializado como repo git en `main` con commit `ed79719 Initial private commercial export` y publicado en el repo privado `CryptoLeon78/sqx-edge-commercial-private`.

Activacion Pro prevista:

- El usuario recibe un JSON de licencia firmado.
- Lo pega en Inicio -> Licencia -> Cargar licencia.
- La API local verifica la firma offline y guarda `backend/sqx-edge-tool/config/license.json`.
- La licencia y la clave privada de firma nunca se incluyen en el ZIP portable.

SQX Views:

- El tab `SQX Views` genera archivos `.vw` para Databank sin depender de Python externo.
- La fuente prototipo Tkinter quedo migrada al flujo nativo del dashboard y archivada en backup previo de V5.
- Free incluye el preset `EGT Core`; Pro desbloquea el catalogo completo y presets avanzados.
- Incluye ejemplos buyer-ready para primera revision, robustez, riesgo y auditoria completa.
- Incluye packs por perfil de comprador para evaluacion Free, Setup Assist Pro, comprador centrado en riesgo y entrega de auditoria.
- Incluye packs por familia de activo y flujos de validacion para revisar Forex, indices, oro, intake, robustez, riesgo y auditoria.
- Puedes guardar presets propios en el navegador y moverlos entre instalaciones con packs JSON exportables/importables.
- La importacion de packs SQX Views muestra preview de presets, metricas, columnas estimadas y reemplazos antes de fusionar.
- Workflow y Estrategias incluyen accesos directos para abrir SQX Views con vistas recomendadas ya preparadas.
- La vista descargada puede cargarse en StrategyQuant X desde Databank -> Load View.

Project Generator:

- `Custom libre` permite crear `.cfx` fuera de Mining Control con asset, timeframe, blocksetting, direccion y capa propios.
- Incluye presets locales reutilizables y exportacion/importacion JSON para mover configuraciones propias entre instalaciones.
- La importacion de packs custom muestra preview de presets, assets, capas y reemplazos antes de fusionarlos con los guardados locales.
- Las tarjetas de activo/categoria pueden prefijar un Custom Project desde acciones rapidas sin ejecutar generacion automatica.

Mining Control:

- Incluye acciones rapidas para anadir candidatos a Mining Control desde activo/categoria.
- Muestra salud operativa compacta y funnel visual editable sin recuperar tabs eliminados como Top Picks o Matriz.

Herramientas analiticas:

- `plan_quality_advisor.py` revisa el plan actual contra el baseline H1 disponible, propone alternativas diversificadas y puede anadir evidencia multi-timeframe si se le entrega una carpeta de metricas.
- `multi_timeframe_scoring.py` calcula scores por timeframe y consenso ponderado a partir de metricas JSON ya generadas. No descarga datos, no modifica HTML y esta pensado como paso controlado antes de exponer multi-TF en la UI.
- `multi_timeframe_metric_gate.py` valida carpetas de metricas `asset_metrics[_TF].json` con cobertura, completitud, activos desconocidos, compatibilidad del scorer y hashes SHA256 antes de aceptarlas como fuente propia.
- `first_party_metric_source.py` genera el bundle H1 first-party desde `app/js/scores-data.js`, escribe manifiesto de procedencia y ejecuta el gate sin fabricar timeframes no disponibles.
- `multi_timeframe_source_intake.py` prepara una carpeta de intake H1/M30/M15/H4, puede anadir H1 first-party y bloquea M15/M30/H4 si no existen metricas reales.
- `multi_timeframe_plan_artifacts.py` genera reportes del Plan Quality Advisor con evidencia MTF solo si A53 devuelve GO; si no, escribe un NO_GO trazable.
- `ohlc_metric_builder.py` convierte CSV OHLC revisables (`ASSET_TF.csv`) en metricas multi-timeframe compatibles con A53/A54.
- `real_mtf_pipeline_run.py` orquesta A55 -> A53 -> A54 y devuelve GO solo si la cadena completa con datos reales queda validada.

## Acceso Web Pro

Flujo objetivo para usuario final:

1. El cliente paga o renueva la suscripcion.
2. El webhook activa su email validado.
3. El cliente entra por el enlace protegido.
4. Cloudflare Access y la autenticacion propia validan su sesion.
5. La app abre su workspace aislado en el servidor.
6. El cliente usa Workflow, Activos, Mining Control, SQX Views, Project Generator, Template Maker, Strategy Control y Champion vs Challenger desde el navegador.

El usuario final no instala Python, no descomprime ZIPs, no ejecuta `START_SQX_EDGE.bat` y no configura rutas SQX locales. Las rutas SQX, templates, `data.db`, BlockSettings y outputs se gestionan en el servidor remoto controlado.

Mensaje base de seguridad: SQX Edge Pro opera en un entorno autenticado, auditado y aislado por workspace. No se promete riesgo cero; se comunica control operativo, trazabilidad y privacidad razonable.

## Entrega Comercial Controlada

Estado real: REMOTE-0 documenta el pivote; la entrega comercial controlada pasa a acceso web Pro asistido. No esta planteado aun como lanzamiento masivo autoservicio.

Antes de activar a un comprador:

1. Confirmar pago activo y email validado.
2. Crear o verificar workspace aislado.
3. Confirmar que Cloudflare Tunnel, Access, backend, rutas SQX servidor y output estan en verde.
4. Mantener claims seguros: productividad, orden, trazabilidad y reduccion de errores operativos; nunca prometer rentabilidad.
5. Registrar incidencias de acceso, generacion, soporte y decision de ampliar/pausar antes de mas trafico.

## Fallback Interno Portable

El portable queda como herramienta interna de rollback, soporte o diagnostico. No es el flujo comercial principal.

Launcher interno desde la carpeta `packaging/` o desde el ZIP portable generado:

```bat
packaging\START_SQX_EDGE.bat
```

Ese launcher arranca la API local con Python embebido, espera a `http://127.0.0.1:5050/api/health` y abre `app\SQX_Dashboard_v6.html`.

Para cerrar la API local:

```bat
packaging\STOP_SQX_EDGE.bat
```

## Tests y CI

Dependencias de desarrollo:

```bat
python -m pip install -r requirements-dev.txt
```

Validacion local recomendada:

```bat
python -m pytest
```

Contratos JS:

```powershell
Get-ChildItem tests/js/contracts -Filter *.mjs | Sort-Object Name | ForEach-Object { node $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
```

GitHub Actions ejecuta el baseline en cada push/PR a `main`: compilacion Python, pytest, contratos JS y `git diff --check`.

## Estructura

```text
.
├── app/                         Dashboard HTML, CSS y JS
│   ├── SQX_Dashboard_v6.html
│   ├── css/
│   └── js/
├── backend/sqx-edge-tool/        API Flask, CLI, config, templates y tests
├── analysis/                     Scripts analiticos y outputs regenerables
├── data/                         Datasets base versionados
├── docs/                         Documentacion y conceptos visuales
├── packaging/                    Launchers internos y empaquetado
├── START_SQX_EDGE_REMOTE.bat     Launcher operador remoto
└── STOP_SQX_EDGE_REMOTE.bat
```

## Manifiestos Dinamicos

Los datos principales viven en JSON dentro de `backend/sqx-edge-tool/config/`:

- `plan.json`
- `assets.json`
- `strategies.json`
- `ui_manifest.json`
- `generator_profiles.json`
- `instruments.json`

Para regenerar el manifiesto frontend:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\build_frontend_manifest.py
```

El resultado se escribe en `app\js\manifest-data.js`.

## Project Generator

- `Generacion masiva` mantiene el flujo original: genera `.cfx` desde los minings del plan.
- `Custom libre` permite crear un proyecto fuera del plan con nombre, asset, timeframe, blocksetting, direccion y capa propios.
- El custom libre usa el template configurado de la capa seleccionada, o un template opcional indicado en el formulario.
- Los presets custom se guardan en el navegador local para reutilizar combinaciones frecuentes sin reescribir campos.
- Los presets custom se pueden exportar/importar como packs JSON para moverlos entre instalaciones.
- La API local expone `/api/generate-custom` y aplica la misma licencia Pro que `/api/generate`.

## Plan Quality Advisor

Herramienta backend para revisar el plan actual contra los scores objetivos del dashboard y generar una propuesta diversificada:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\plan_quality_advisor.py
```

Para integraciones o auditoria:

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe backend\sqx-edge-tool\tools\plan_quality_advisor.py --json
```

Es una guia de revision, no una orden automatica de reemplazo. La version actual usa el baseline H1 disponible en `app/js/scores-data.js`; el scoring multi-timeframe queda planificado como fase A48.

## Backend

La configuracion local vive en:

```text
backend/sqx-edge-tool/config.json
```

Ese archivo esta ignorado por Git para no subir rutas personales. Si falta el Python embebido, preparalo una vez con:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\bootstrap_embedded_python.ps1
```

## Tests

```powershell
backend\sqx-edge-tool\venv\Scripts\python.exe -m pytest backend\sqx-edge-tool
```

Los tests E2E de interfaz son opcionales. Si quieres activarlos en desarrollo:

```powershell
npm install --no-save --package-lock=false playwright
$env:SQX_E2E_SCREENSHOTS='1'
backend\sqx-edge-tool\venv\Scripts\python.exe -m pytest backend\sqx-edge-tool
```

Si Playwright no esta instalado, esos tests se saltan automaticamente.

## Empaquetado Interno Fallback

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\package_portable.ps1 -RequireEmbeddedPython
```

El ZIP portable se crea en `dist/` e incluye el Python embebido. Desde REMOTE-0 se conserva como fallback interno, no como onboarding comercial del usuario final.

## Checklist de fallback

Para preparar una entrega interna con pruebas, ZIP portable y validacion del ZIP extraido:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\release_checklist.ps1
```

El checklist ejecuta contratos JS, suite Python, `git diff --check`, empaquetado portable, extraccion temporal, import de API con Python embebido y health check local. Al terminar muestra el ZIP listo en `dist/`.

Tambien puedes lanzar el modo estricto con doble click desde:

```text
RELEASE_SQX_EDGE.bat
```

Ese modo exige Git limpio antes de empaquetar y deja un resumen en `dist/SQX_release_summary.txt`.

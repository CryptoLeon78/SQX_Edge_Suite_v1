# SQX Edge Suite v1

Dashboard y herramienta local para organizar el pipeline SQX Edge, generar Custom Projects `.cfx` para StrategyQuant X y limpiar estrategias `.sqx` post-mining.

## Estado Actual

- Estado interno: T10ajl2 deja preparado el kit local de desbloqueo Cloudflare; T10ak sigue bloqueado hasta que la evidencia local ignorada devuelva GO, sin publicar Worker, Access, URL ni testers.
- Estado comercial: M99 completada con decision local del siguiente movimiento comercial controlado desde evidencia M98.
- Ultimo commit base verificado antes de S5/M-pre: `d7c0757`.
- Ultimo ZIP portable verificado: `dist/SQX_Edge_Tool_Portable_20260509_102131.zip`.
- SHA256 del ZIP: `18EC98981D8B52535E1FE26EA47876588FA2EB8321DD2A9706CBD30B6A0B7E5D`.
- Siguiente paso recomendado: ejecutar `prepare:cloudflare-hostname-zone-selection -- --write`, rellenar evidencia privada T10ajl y ejecutar T10ak solo cuando `proof:cloudflare-hostname-zone-selection` devuelva GO, M100 para ejecutar exactamente el movimiento comercial controlado aprobado por M99, V10 para comparativa de packs SQX Views, SB18 para pulir export de evidencia comprador o R46 solo con autorizacion explicita para publicar GitHub Release.
- Ultima mejora funcional: `dukas_mt5_ohlc_download.py --recent-bars` descarga 33 activos x 4 timeframes desde MT5; A56 devuelve GO con A55/A53/A54 en verde.

## SQX Edge Pro

El proyecto esta preparando una edicion comercial Pro con suscripcion mensual/anual, soporte opcional y packs de plantillas alrededor de la herramienta.

Oferta inicial prevista:

- SQX Edge Free: descarga portable para probar el flujo.
- SQX Edge Pro Mensual: 24 EUR/mes.
- SQX Edge Pro Anual: 199 EUR/ano.
- Setup Assist: instalacion y configuracion guiada.
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

Portal tester Pro previsto:

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

- `Custom libre` permite crear `.cfx` fuera del plan mining con asset, timeframe, blocksetting, direccion y capa propios.
- Incluye presets locales reutilizables, exportacion/importacion JSON, perfiles starter y familias por objetivo para usuarios que quieren empezar sin configurar todo desde cero.
- La importacion de packs custom muestra preview de presets, assets, capas y reemplazos antes de fusionarlos con los guardados locales.
- Las tarjetas de activo/categoria pueden prefijar un Custom Project desde acciones rapidas sin ejecutar generacion automatica.
- `Entrega comprador .cfx` prepara notas Markdown copiables/descargables con configuracion, archivos referenciados, checklist y limites responsables.

Pipeline State:

- Incluye acciones rapidas para anadir candidatos al Plan Mining desde activo/categoria.
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

## Entrega Final

Paquete recomendado para usuario final:

```text
dist/SQX_Edge_Tool_Portable_20260509_102131.zip
```

Uso para usuario basico:

1. Descomprime el ZIP en una carpeta normal, por ejemplo `C:\SQX_Edge`.
2. Haz doble click en `START_SQX_EDGE.bat`.
3. Espera unos segundos: se arranca la API local y se abre el dashboard.
4. Usa la app desde el navegador que se abre.
5. Para cerrar la API local, haz doble click en `STOP_SQX_EDGE.bat`.

No hace falta instalar Python. El ZIP incluye un runtime portable dentro de `backend\sqx-edge-tool\runtime\python`.

Problemas frecuentes:

- Si Windows muestra SmartScreen, pulsa `Mas informacion` y despues `Ejecutar de todas formas`.
- Si no abre el dashboard, ejecuta `STOP_SQX_EDGE.bat` y vuelve a abrir `START_SQX_EDGE.bat`.
- Si la API no conecta, revisa que el puerto `5050` no este ocupado por otra aplicacion.
- No muevas archivos internos del ZIP descomprimido; abre siempre desde `START_SQX_EDGE.bat`.
- Si StrategyQuant X esta en una ruta distinta, configuralo desde el tab `Project Generator`.

## Entrega Comercial Controlada

Estado real: preparado para demos Pro asistidas, early access, compradores fundadores y primeras ventas manuales con soporte. No esta planteado aun como lanzamiento masivo autoservicio.

Antes de entregar a un comprador:

1. Usar el ZIP verificado `SQX_Edge_Tool_Portable_20260509_102131.zip`.
2. Confirmar SHA256 `18EC98981D8B52535E1FE26EA47876588FA2EB8321DD2A9706CBD30B6A0B7E5D`.
3. Entregar la licencia Pro firmada por separado, nunca dentro del ZIP.
4. Mantener claims seguros: productividad, orden, trazabilidad y reduccion de errores operativos; nunca prometer rentabilidad.
5. Registrar incidencias de instalacion, activacion, soporte y decision de repetir/pausar antes de ampliar trafico.

## Inicio Rapido

Para usuario basico, doble click en:

```bat
START_SQX_EDGE.bat
```

Ese launcher arranca la API local con Python embebido, espera a `http://127.0.0.1:5050/api/health` y abre `app\SQX_Dashboard_v6.html`.

Para cerrar la API local:

```bat
STOP_SQX_EDGE.bat
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
├── START_SQX_EDGE.bat            Acceso directo de un click
└── STOP_SQX_EDGE.bat
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
- Las familias por objetivo agrupan perfiles custom para comprador inicial, validacion intradia, revision de riesgo o muestra Pro completa.
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

## Empaquetado

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\package_portable.ps1 -RequireEmbeddedPython
```

El ZIP portable se crea en `dist/` e incluye el Python embebido para que el usuario final pueda abrir `START_SQX_EDGE.bat` sin instalar nada.

## Checklist de entrega

Para preparar una entrega completa con pruebas, ZIP portable y validacion del ZIP extraido:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File backend\sqx-edge-tool\tools\release_checklist.ps1
```

El checklist ejecuta contratos JS, suite Python, `git diff --check`, empaquetado portable, extraccion temporal, import de API con Python embebido y health check local. Al terminar muestra el ZIP listo en `dist/`.

Tambien puedes lanzar el modo estricto con doble click desde:

```text
RELEASE_SQX_EDGE.bat
```

Ese modo exige Git limpio antes de empaquetar y deja un resumen en `dist/SQX_release_summary.txt`.

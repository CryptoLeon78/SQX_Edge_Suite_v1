# Local AI Agent Roadmap

## Estado

- Phase G8 - Local AI Agent Governance Gate: aplicado.
- Phase A64 - Backend Agent Core: aplicado en modo operador local.
- Phase WFCO-AI1 - Edge Factory Agent Dock: aplicado.
- Phase WFCO-AI2 - perfiles especializados: aplicado como perfiles de etapa y subperfiles declarados.
- Phase LOCAL-AI-INBOX1 - bandeja local: aplicada bajo `.local/agent_inbox/`.
- Phase REMOTE-AI-TESTER1 - piloto IA para testers autenticados: aplicado con subset seguro.
- Phase SQX142-143-BACKPORT1 - compatibilidad SQX local: aplicado como capability interna local-only.
- Phase SQX142-PERF1 - rendimiento SQX local: aplicado como capability interna local-only.
- Phase G8-SQX-AGENT-SKILLS1 - guardianes SQX de agentes/skills: aplicado antes de `RETEST 0` con perfiles local-only, skills actualizadas y handoffs ignorados.
- Phase G8-SQX-ACADEMIC-LOPEZ1 - consulta academica SQX: aplicada como skill/perfil local-only para MC, OOS, data snooping y backtest overfitting antes de Fase 6 `MC`.

## Contrato V1

El agente IA local es una ayuda guiada para el operador y, desde REMOTE-AI-TESTER1, para usuarios remotos autenticados con sesion de app activa y entitlement permitido (`tester_free`, paid o interno) en modo tester seguro. Usa Ollama en `http://127.0.0.1:11434` con `qwen3.5:latest` y fallback `qwen2.5-coder:3b`, sin API externa ni llamadas directas desde el navegador. El backend intenta levantar `ollama serve` automaticamente al arrancar el servidor, al consultar `/api/agent/status` y al pulsar `Arrancar` en el monitor local del operador.

Reglas:

- El navegador habla con Flask; Flask habla con Ollama.
- El LLM solo propone acciones estructuradas.
- La policy backend valida cada accion contra un catalogo allowlisted.
- Toda accion de navegacion o escritura exige confirmacion explicita.
- No se persisten prompts, respuestas ni historial completo.
- La auditoria local registra solo accion, riesgo, resultado y timestamp.
- El usuario remoto autenticado solo recibe capacidades `read` y `navigate`; no ve monitor local, bandeja `.local/agent_inbox/` ni acciones `mark_step:*`.
- El usuario remoto autenticado no recibe la capability `sqx142_compat_help` ni el estado `/api/sqx142/compat/status`.
- El usuario remoto autenticado no recibe la capability `sqx142_performance_help` ni el estado `/api/sqx142/performance/status`.
- El monitor Backend/Tunnel/Ollama es local-only para el creador/operador que levanta los servers.
- Preguntas como `que eres capaz de hacer?` usan una respuesta fija de capacidades, independiente de Ollama y de la etapa activa.
- Preguntas locales sobre SQX 142, build 143, build 144, backport o compatibilidad usan `fixed_sqx142_compat` y el ledger antes que una respuesta libre del LLM.
- Preguntas locales sobre rendimiento, minados, retests, MonteCarlo, databanks o perfiles JVM usan `fixed_sqx142_performance` y `docs/SQX142_PERFORMANCE_ROADMAP.md` antes que una respuesta libre del LLM.
- Preguntas locales sobre C1-CONFIG1, `RETEST 0`, guardianes, skills, handoffs, docs o matriz de tests usan respuestas fijas `fixed_sqx_c1_config`, `fixed_sqx_test_guardian`, `fixed_sqx_docs_curator` o `fixed_sqx_agent_skills` antes que respuesta libre del LLM.
- Preguntas locales sobre criterio academico, Lopez de Prado, OOS, MC, contaminacion, data snooping, PBO o Deflated Sharpe usan `fixed_sqx_academic_lopez` y fuentes academicas antes que respuesta libre del LLM.
- `SQX Test Guardian` y `SQX Docs Curator` son perspectivas internas para lectura, planificacion, dry-run y revision; no son ejecutores autonomos de mutaciones.
- `SQX Academic Lopez` es una perspectiva interna de lectura/criterio; no ejecuta cambios, no decide permisos y no sustituye confirmacion metodologica del operador.

Prohibido en V1:

- Emails, grants, checkout, Cloudflare, URLs protegidas y cambios de permisos.
- Publicacion, despliegue, invitaciones, borrados y scripts comerciales externos.
- Ejecutar comandos generados por el LLM.
- Devolver rutas locales, emails, tokens, cookies o protected URLs.

## Implementacion

- Backend: `backend/sqx-edge-tool/core/agent/`.
- Config: `backend/sqx-edge-tool/config/agent_profiles.json`.
- Endpoints:
  - `GET /api/agent/status`
  - `GET /api/agent/capabilities`
  - `POST /api/agent/plan`
  - `POST /api/agent/confirm`
  - `POST /api/agent/execute`
  - `POST /api/agent/translate-source-code`
  - `GET /api/sqx142/compat/status` local-only para operador
  - `GET /api/sqx142/performance/status` local-only para operador
- Frontend: `app/js/modules/agent-guide.js`.
- UI principal: dock dentro de Edge Factory, no nuevo tab.
- Resumen: panel compacto en Control Panel.
- Bandeja local: `.local/agent_inbox/incoming`, `processed`, `summaries`.
- Handoffs locales: `.local/agent_handoffs/`, ignorado por Git, solo para resumenes de subagentes/decisiones/checks sin prompts completos ni evidencia privada.

## SQX 142 Source Code Translator

El `.sxp` de build 144 `SQExtension-SourceCode-Translator.sxp` es un ZIP con `extend/ResultsPlugins/Source Code Translator/index.html`. La variante local para SQX 142 se reconstruye con `backend/sqx-edge-tool/tools/build_sqx142_source_translator.py` y queda en `.local/sqx_extensions/SQExtension-SourceCode-Translator-Ollama-SQX142.sxp`, pero SQX 142 no lo expone de forma fiable como Result Plugin separado desde `user/extend/ResultsPlugins`.

La integracion visible y validada en SQX 142 vive dentro del tab nativo `Source Code`, parcheando `internal/plugins/ResultsSourceCode` para mostrar el boton `Local Ollama Translator` y el panel `Source Code Translator · Local Ollama`.

Reglas de compatibilidad:

- `user/extend/ResultsPlugins/Source Code Translator/index.html` se conserva como artefacto de diagnostico/paquete, no como punto de aparicion garantizado en SQX 142.
- El punto de aparicion operativo es `Strategy/result -> Source Code -> Local Ollama Translator`.
- La variante local elimina `api.openai.com`, el campo de API key y los modelos cloud.
- El navegador de SQX llama solo a `http://127.0.0.1:5050/api/agent/translate-source-code`.
- Flask media la peticion y llama a Ollama local; el HTML de SQX nunca habla directamente con Ollama.
- El modo `translate` traduce codigo SQX pegado o cargado desde el Result Plugin.
- El modo `fix` corrige el codigo traducido usando feedback textual; capturas quedan como mejora posterior.
- Para traduccion se usa `translationModel` (`qwen2.5-coder:1.5b` en el host validado) y `translationMaxTokens` para evitar timeouts por generaciones largas.
- Si `localhost:8080` muestra la UI nueva pero la app local no, aplicar `docs/maintenance/SQX142_ELECTRON_CACHE_RUNBOOK.md`: Electron puede mantener cache vieja aunque el servidor SQX ya entregue bundles nuevos.

Smoke validado:

- `POST /api/agent/translate-source-code` devuelve `200 OK` con Ollama local y sin API externa.
- Los bundles servidos por SQX contienen `Local Ollama Translator`, `Source Code Translator · Local Ollama`, `/api/agent/translate-source-code`, fallback `$.ajax` y `.source-code-local-translator`.
- Tras mover la cache Electron a backup y reiniciar SQX, la app local muestra el traductor dentro de `Source Code`.

## Perfiles

Perfiles de etapa Edge Factory:

- `session`: acceso, workspace, servicio, descargas.
- `asset`: asset, timeframe, direccion y BlockSetting.
- `capa1-generate`: generacion Capa 1.
- `capa1-analyze`: certificacion Capa 1.
- `c2-template`: Template C2 trazable.
- `capa2-generate`: generacion Capa 2.
- `capa2-analyze`: revision Capa 2.
- `portfolio`: shortlist diversa.
- `sqx142-compat`: estado local SQX 142/143/144, runtime, procesos, ledger y limites de backport.
- `sqx142-performance`: perfil JVM activo, disco, procesos, views de rendimiento, evidencias clave, Live Guard, recomendacion activa y reglas de calidad sin ejecutar cambios.
- `sqx-c1-config`: estado C1-CONFIG1, ledger local, promocion selectiva y salto controlado hacia `RETEST 0`.
- `sqx-test-guardian`: matriz de checks, riesgos de regresion, dry-runs seguros y limites de no-mutacion.
- `sqx-docs-curator`: coherencia README/governance/roadmap/changelog/manifest y privacidad documental.
- `sqx-academic-lopez`: revision academica local de OOS, MC, data snooping, backtest overfitting, multiple testing, PBO/DSR y contaminacion de validacion.
- `sqx-agent-skills`: capa de skills, handoffs, subagentes permitidos, autonomia y limites.

Subperfiles declarados para evolucion posterior:

- Project Generator, Template Maker, Mining Control, SQX Views, Strategy Control, Champion vs Challenger, BlockSettings Info y Control Panel.

## Criterios De Aceptacion

- Si Ollama no esta arrancado, la app no rompe y el agente cae a recomendacion heuristica.
- Si Ollama esta instalado pero no arrancado, el backend intenta autostart y reporta `provider.autoStart`.
- Pulsar `Arrancar` en el monitor operador dispara `/api/agent/status`, intenta conectar Ollama y no marca listo para testers hasta que Backend, Tunnel y Ollama estan OK.
- La inteligencia SQX142-PERF1 es pasiva bajo demanda: se actualiza al arrancar/refrescar el monitor, consultar `/api/agent/status` o detectar SQX abierto; no mantiene un proceso residente adicional.
- Live Guard observa logs/crashes/API/procesos mientras SQX esta abierto y solo propone o aplica reparacion segura tras cierre de SQX.
- `/api/agent/*` responde a operador local y a sesiones remotas autenticadas con entitlement permitido; bloquea anonimato, sesiones inactivas y usuarios sin entitlement.
- Remote tester capabilities excluye bandeja local, `mark_step:*`, escritura y monitor.
- Remote tester capabilities excluye `sqx142_compat_help` y cualquier estado del monitor local.
- Remote tester capabilities excluye `sqx142_performance_help`, `fixed_sqx142_performance` y cualquier estado de rendimiento local.
- Remote tester capabilities excluye `sqx_c1_config_help`, `sqx_test_guardian_help`, `sqx_docs_curator_help`, `sqx_academic_lopez_help`, `sqx_agent_skills_help` y cualquier estado/handoff local de guardianes SQX.
- Las respuestas publicas no contienen rutas locales, emails, tokens ni protected URLs.
- El dock no crea un tab primario nuevo.
- Confirmar una recomendacion de navegacion abre la herramienta permitida.
- Cancelar no cambia estado.
- La bandeja local no se incluye en Git.

## Siguiente Evolucion

V2 puede habilitar dry-runs de herramientas internas con contratos seguros. V3 puede habilitar generacion `.cfx` confirmada. Cualquier ampliacion mas alla del subset tester seguro requiere fase nueva, evidencia privada y actualizacion de gates remotos.

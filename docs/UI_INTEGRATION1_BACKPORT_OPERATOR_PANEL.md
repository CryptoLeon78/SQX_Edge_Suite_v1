# UI-INTEGRATION1 Backport Operator Panel

Estado: `completed_ui_panel_local_only`.

Este bloque expone en Edge Factory los contratos cerrados del track SQX142/144 backport. Es una integracion UI de operador, no un cambio de engine ni una automatizacion dentro de SQX.

## Superficie Integrada

- Panel: `Backport Operator Panel` dentro de `tab-workflow`, junto a Portfolio Lab y Portfolio Master Contract.
- Version UI: `ui-integration1-backport-operator-panel-v1`.
- Core frontend: `app/js/modules/edge-factory.js`.
- Binding UI: `app/js/modules/edge-factory-ui.js`.
- HTML/CSS: `app/SQX_Dashboard_v6.html` y `app/css/dashboard.css`.
- Contrato JS: `tests/js/contracts/edge_factory_contracts.mjs`.

## Contratos Consumidos

| Modo | Endpoint | Tipo |
| --- | --- | --- |
| MCP-like status | `GET /api/sqx142/mcp-like/status` | read-only |
| Results Plugin readiness | `GET /api/sqx142/mcp-like/results-plugin-readiness` | read-only |
| Correlation Filter external | `POST /api/sqx142/correlation-filter/external` | external_readonly |
| Monte Carlo benchmarks | `POST /api/sqx142/monte-carlo/benchmarks` | external_readonly |
| MT5 data intake probe | `POST /api/sqx142/mt5-data-intake/probe` | probe_no_import |
| Copy-only migration checklist | `POST /api/sqx142/migration/copy-only-checklist` | checklist_only_no_copy |

## Comportamiento

- Usa `SQX_CONFIG.apiBase()` y rutas Flask existentes bajo `/api/sqx142/*`.
- Permite pegar CSV/JSON controlado y construir payloads compatibles para los cuatro contratos `POST`.
- Ofrece muestras locales para formato, marcadas como input de operador o ejemplo de payload, sin desbloquear decisiones reales.
- Guarda en `localStorage` solo el ultimo readback y un historial corto bajo `backportOperatorPanel`.
- Exporta JSON/CSV devuelto por la API cuando existe `csvExport`.
- Renderiza guards y privacidad: runtime SQX, `data.db`, `user/projects`, remote/tester y tokens/campos privados.

## Limites

- No arranca SQX, Java, MT5 ni terminal externo.
- No ejecuta `run_project`, `project/start`, retests, Migration Tool ni importacion directa.
- No escribe en `data.db`, `user/projects`, databanks, settings, logs ni archivos de instalacion SQX.
- No expone rutas locales crudas, tokens, credenciales, nombres privados ni evidencias locales.
- No cambia la conclusion de BACKPORT9: `SQX142/144 backport track closed`.

## Verificacion

- `node tests/js/contracts/edge_factory_contracts.mjs` -> `edge factory contracts ok`.
- Playwright local `file:///app/SQX_Dashboard_v6.html` -> `visible=true`, `selectVisible=true`, `runVisible=true`, `hasVersion=true`.
- Evidencia local ignorada: `.local/sqx142_144_backport/ui_integration1_backport_operator_panel_20260526_203000.json`.

## Siguiente Decision Recomendada

`UI-INTEGRATION2 Backport Panel Browser Smoke` para abrir el dashboard local, verificar visualmente el panel y ejecutar llamadas contra Flask solo si el backend local esta levantado como operador.

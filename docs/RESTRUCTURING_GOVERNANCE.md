# Reestructuracion Gobernada SQX Edge Suite v1

Marker: `sqx-edge.restructuring-governance-v1`

Current phase: `A65 Boundary Guard`

Status: `completed_boundary_guard`

Last updated: 2026-06-04

## Purpose

Este registro gobierna una reestructuracion por fases pequenas, trazada en Git y gbrain, sin refactor masivo ni cambio de comportamiento por defecto. A64 solo crea inventario, ownership inicial y log de fases; A65 clasifica fronteras antes de cualquier movimiento. Ninguna de estas fases mueve archivos, borra contenido, cambia imports, cambia build/load order ni toca runtime SQX.

## Live Gates Preserved

- `REMOTE-8K Post Execution Monitoring` sigue siendo el siguiente gate remoto; no hay expansion nueva antes de monitorizacion limpia y evidencia privada.
- Portfolio Master sigue bloqueado hasta recibir inputs reales: governed Lab output, natural Forward CSV/equity/returns, account context y broker context.
- `SQX142-AW-AI2` esta construido como `sqx142-ai-wizard-studio-v2`, pendiente de install/manual roundtrip con SQX cerrado.
- Readiness QXPRO queda como ruta privada de operador, no redistribucion publica.
- No SQX runtime launch.
- No `data.db` writes.
- No `user/projects` writes.
- No `run_project`, Migration Tool, jars internos, licencia, activacion, bypass ni claims de rentabilidad o riesgo cero.
- No physical moves during A65.
- No deletes during A65.

## Top-Level Inventory Snapshot

Snapshot A64 de paths tracked principales, generado para orientar fases futuras sin mover nada.

| Path | Tracked files | Ownership inicial | A64 policy |
| --- | ---: | --- | --- |
| `docs/` | 448 | Governance, runbooks, canonical and historical docs | Clasificar canonicos vs historicos en A66; no movimiento masivo. |
| `backend/` | 409 | Flask/API, core SQX helpers, config, backend tools | No cambios de imports ni behavior en A64. |
| `templates/` | 139 | SQX project/template artifacts | Mantener estables hasta gates explicitos. |
| `app/` | 63 | Dashboard/frontend modules and assets | No load-order, nav, CSS or visible UI changes in A64. |
| `resources/` | 52 | Packaged resources and distributable inputs | Clasificacion futura antes de mover. |
| `tests/` | 44 | Regression, contracts and state consistency | Baseline de verificacion por fase. |
| `tools/` | 43 | Operator wrappers, local runbooks and gated helpers | Ownership map en A67 antes de mover wrappers. |
| `integrations/` | 16 | SQX142 supported extension surfaces | No runtime/install actions in A64. |
| `analysis/` | 6 | Analysis helpers and evidence tooling | Clasificar en A65/A67. |
| `.github/` | 4 | CI/workflow support | No cambios en A64. |
| `packaging/` | 2 | Packaging helpers | Clasificar con tooling ownership. |
| `Presentaciones Proyecto/` | 2 | Presentation assets | Conservar hasta politica docs/assets. |
| `data/DatabankExport.csv` | 1 | Visible data sample/export | A65 decide si queda sample publico, se redacciona o se reubica. |
| Root launchers | 4 | `GENERAR_GUIA_VISUAL_CUSTOM_PROJECT.bat`, `RELEASE_SQX_EDGE.bat`, `START_SQX_EDGE_REMOTE.bat`, `STOP_SQX_EDGE_REMOTE.bat` | No movimientos; A67 decide wrappers/aliases. |
| Root docs/config | 9 | `.gitattributes`, `.gitignore`, `CHANGELOG.md`, `DISCIPLINA_OPERATIVA.md`, `README.md`, `package-lock.json`, `package.json`, `pytest.ini`, `requirements-dev.txt` | No movimientos; ownership explicito antes de rehome. |

Ignored/local/private/generated roots observed on disk stay outside the public restructuring inventory unless a later gate explicitly classifies them: `.local/`, `.pytest_cache/`, `artifacts/`, `backups/`, `dist/`, `license_keys/`, `licenses_private/`, `material de diagnostico/`, `node_modules/`, `output/`, `tmp/` and copy folders.

## A65 Boundary Classification

A65 Boundary Guard completed as a docs-only classification pass. It used root-level metadata, `.gitignore` rules and targeted safe scans; it did not inspect private evidence contents, did not dump ignored folders and did not move or delete files.

| Boundary class | Paths / patterns | Decision | Next owner |
| --- | --- | --- | --- |
| Canonical tracked source | `app/`, `backend/`, `integrations/`, `templates/` | Treat as product/runtime surface. No physical moves until a later phase provides wrappers, import checks and focal tests. | A67/A68 |
| Canonical tracked governance/docs | `docs/`, `README.md`, `CHANGELOG.md`, `DISCIPLINA_OPERATIVA.md` | Keep tracked. A66 will classify canonical vs historical docs before any docs rehome. | A66 |
| Tracked tooling/config | `tools/`, root BAT launchers, `package*.json`, `pytest.ini`, `requirements-dev.txt`, `.github/`, `.gitattributes`, `.gitignore` | Keep stable. A67 maps ownership and wrapper compatibility before movement. | A67 |
| Tracked analysis/assets | `analysis/`, `resources/`, `packaging/`, `Presentaciones Proyecto/` | Keep tracked. Needs owner and purpose classification before any relocation. | A66/A67 |
| Visible public-safe sample | `data/DatabankExport.csv` | Keep tracked for now as a small SQX export sample, not private operator evidence and not Portfolio Master input. A65 scan found no email, URL, local Windows path, full IP, token, secret, license payload or private-key pattern. | A66/A68 |
| Ignored generated/regenerable | `node_modules/`, `.pytest_cache/`, `artifacts/`, `tmp/`, `dist/`, `output/`, generated ZIP/log/image/csv caches | Stay ignored. Do not commit generated outputs unless a later phase promotes a sanitized fixture explicitly. | A65 guard |
| Ignored private/operator | `.local/`, `license_keys/`, `licenses_private/`, `private_keys/`, private/commercial evidence roots and ignored backend data evidence | Stay ignored/private. Do not inspect, dump, import to gbrain or commit contents. | A65 guard |
| Ignored backups/copies | `backups/`, copy folders, `*_backup_*`, `.bak`, `.old`, backup HTML snapshots | Stay ignored. No delete in A65; cleanup requires a separate evidence-backed housekeeping gate. | Future cleanup gate |

## A65 Boundary Decisions

- `data/DatabankExport.csv` remains tracked as a visible public-safe sample/export fixture under guard; it is not a governed Lab output, natural Forward CSV, equity/returns series, account context or broker context for Portfolio Master.
- Ignored private/operator roots remain excluded from repo, docs dumps and gbrain write-back. A65 records classes, not contents.
- Generated and backup roots remain non-canonical. Their presence does not authorize cleanup, deletion, packaging or sync.
- Any future physical move must start from this boundary table, update references/wrappers, run focal tests and keep one domain per commit.

## Phase Register A64-A69

| Phase | Status | Goal | Boundaries | Done criteria |
| --- | --- | --- | --- | --- |
| A64 Structure Register Bootstrap | completed | Crear registro, mapa top-level, ownership inicial y log de fases. | Docs-only inventory; no physical moves, no runtime changes. | Punteros y manifest actualizados, tests base, gbrain log, commit y push. |
| A65 Boundary Guard | completed | Clasificar ignorados, generados, privados y casos visibles como `data/DatabankExport.csv`. | No borrados ni moves sin evidencia; privacidad primero. | Tabla de clases, acciones propuestas y tests focales. |
| A66 Docs Canonicalization | next | Definir docs canonicos vs historicos con indice. | No mover masivamente `docs/`; primero indexar. | Indice aprobado y referencias canonicas claras. |
| A67 Tooling Ownership Map | pending | Documentar ownership de scripts raiz, `tools/`, wrappers y runbooks. | No mover wrappers sin compatibilidad o alias. | Mapa de tooling, owners y riesgos por dominio. |
| A68 Low-Risk Physical Moves | pending | Mover solo candidatos seguros, un dominio por commit. | Mantener wrappers/referencias antiguas cuando haga falta. | Un movimiento pequeno, tests focales y rollback claro. |
| A69 Major Refactor Decision Gate | pending | Decidir si procede separar tests/backend/frontend de forma mayor. | Solo tras `REMOTE-8K` y roundtrip de `SQX142-AW-AI2`. | Decision registrada; si no hay GO, se aparca. |

## Phase Log

| Date | Phase | Status | Paths touched | Verification | Commit | Push | gbrain |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-06-04 | A64 Structure Register Bootstrap | completed_docs_only_inventory | `docs/RESTRUCTURING_GOVERNANCE.md`, `README.md`, `docs/PROJECT_GOVERNANCE.md`, `docs/MODULARIZATION_NEXT_STEPS.md`, `CHANGELOG.md`, `docs/state_consistency_manifest.json` | `git diff --check`; docs-state pytest; local agent pytest; JS module contracts; privacy scan OK | A64 closeout commit in Git history | `origin/codex/sqx142-143-backport` | `projects/sqx-edge-suite-v1` A64 closeout entry |
| 2026-06-04 | A65 Boundary Guard | completed_boundary_guard | `docs/RESTRUCTURING_GOVERNANCE.md`, `README.md`, `docs/PROJECT_GOVERNANCE.md`, `docs/MODULARIZATION_NEXT_STEPS.md`, `CHANGELOG.md`, `docs/state_consistency_manifest.json` | `git diff --check`; docs-state pytest; `data/DatabankExport.csv` privacy scan; changed-doc privacy scan OK | A65 closeout commit in Git history | `origin/codex/sqx142-143-backport` | `projects/sqx-edge-suite-v1` A65 closeout entry |

## Subagent Protocol

Subagents may review structure/architecture, docs/privacy and tests/verification in parallel read-only. Codex integrates, mutates files, runs checks and owns final commit/push. Subagents do not move files, edit repo state, stage, commit, push or write gbrain.

## Verification Baseline

- `git status --short`
- `git diff --check`
- `python -m pytest backend\sqx-edge-tool\test_docs_state_consistency.py -q`
- Privacy scan over changed docs/diff for local paths, emails, tokens, protected URLs, keys, licenses, private evidence, full IPs and risk-zero/profitability claims.
- If a future phase changes frontend/load order: `npm run test:js`; `npm run test:e2e` only for visible dashboard/nav/CSS changes.
- If a future phase changes backend/imports: `python -m compileall backend` and focal pytest for the touched area.

## No-Go

- No physical moves during A64.
- No physical moves during A65.
- No deletes during A65.
- No SQX runtime launch.
- No `data.db` writes.
- No `user/projects` writes.
- No Portfolio Master artifact generation before real inputs.
- No new remote expansion before `REMOTE-8K` monitoring closeout.
- No public dump of `.local/`, licenses, emails, tokens, protected URLs, private evidence or sensitive local folders.

## Gbrain Write-Back

Each phase closure updates the existing gbrain page `projects/sqx-edge-suite-v1`; no duplicate page is created. The log records date, phase, scope, tests, commit/push and next step. A64 writes a curated summary only, not a bulk import of `docs/`.

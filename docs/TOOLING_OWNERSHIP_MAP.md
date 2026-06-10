# SQX Tooling Ownership Map

Marker: `sqx-edge.tooling-ownership-map-v1`

Phase: `A67 Tooling Ownership Map`

Status: `completed_tooling_ownership_map`

Last updated: 2026-06-04

## Purpose

A67 documents ownership for root scripts, `tools/`, wrappers, backend tools, runbooks and verification surfaces before any future physical move. It is a map and policy pass only. No tools moved during A67. No wrappers moved during A67. No scripts executed during A67. No services started during A67.

## Ownership Lookup Order

Use this order before changing, moving or replacing any tool:

1. `docs/TOOLING_OWNERSHIP_MAP.md` for owner family, allowed actions and required checks.
2. `docs/RESTRUCTURING_GOVERNANCE.md` for active A64-A69 phase boundaries.
3. The runbook or phase doc named by the tool family.
4. The backend tool/test pair when a wrapper delegates to `backend/sqx-edge-tool/tools/`.
5. `docs/state_consistency_manifest.json` for literal guard markers.

## Root Entrypoints

| Surface | Paths | Owner family | A67 decision | Move gate |
| --- | --- | --- | --- | --- |
| Remote operator start/stop | `START_SQX_EDGE_REMOTE.bat`, `STOP_SQX_EDGE_REMOTE.bat` | Remote service operator surface | Keep root-level compatibility entrypoints. | A68 may only move if root shims remain and remote runbook is updated. |
| Release entrypoint | `RELEASE_SQX_EDGE.bat` | Packaging/release | Keep root-level compatibility entrypoint. | Requires packaging tests and release checklist review before any relocation. |
| Visual guide helper | `GENERAR_GUIA_VISUAL_CUSTOM_PROJECT.bat` | Project Generator/operator guide | Keep root-level compatibility entrypoint. | Requires custom-project visual guide test and README pointer update before relocation. |
| Package/test config | `package.json`, `package-lock.json`, `pytest.ini`, `requirements-dev.txt` | Verification/toolchain config | Keep at root. | No move planned; changes require JS/Python verification. |

## Top-Level `tools/`

Tracked top-level `tools/` currently contains 43 operator-facing files: 22 remote wrappers, 19 SQX142 wrappers, 1 readiness wrapper and 1 cleanup helper.

| Family | Paths / examples | Owner family | A67 decision | Required checks before move/change |
| --- | --- | --- | --- | --- |
| Remote operator/service/tunnel/support | `tools/remote_*.ps1`, `tools/remote8c_observation_status.ps1`, `tools/remote_operator_monitor.hta` | REMOTE service/access/tunnel | Keep as operator wrappers. Do not start tunnel/server or mutate grants in A67. | Remote focal pytest named by changed wrapper plus docs-state; no external actions without explicit gate. |
| SQX142 compatibility/performance/project/readiness | `tools/sqx142_*.ps1`, `tools/sqx_readiness_kit.ps1` | SQX142 local/operator tooling | Keep as lab/operator wrappers. Do not launch SQX or mutate `data.db`/`user/projects` in A67. | Matching `backend/sqx-edge-tool/test_sqx142_*.py` or readiness/packaging test plus docs-state. |
| Workspace cleanup helper | `tools/clean_workspace.ps1` | Local housekeeping | Keep guarded and local. No cleanup in A67. | Separate cleanup gate, dry-run output and privacy review before use. |

## Backend Tooling

`backend/sqx-edge-tool/tools/` currently has 125 tracked tool scripts. These are backend-owned implementation tools, not operator-stable entrypoints unless wrapped by `tools/` or a runbook.

| Family | Examples / patterns | Owner family | A67 decision | Required checks before move/change |
| --- | --- | --- | --- | --- |
| Remote/commercial gates | `remote_*`, `controlled_*`, `approved_*`, `next_*`, `manual_*`, `public_*`, `private_*` | Remote/commercial governance | Keep colocated with backend tests/config. | Matching `test_remote_*`, `test_m9*`, `test_m98*`, `test_m99*` or focal gate tests. |
| SQX142/local lab tooling | `sqx142_*`, `cfx_*`, `dukas_*`, `mt5_*`, `ohlc_*`, `real_*` | SQX142 local intelligence/data tooling | Keep backend-owned. | Matching SQX142/MTF/real-data tests; no SQX runtime or project writes without gate. |
| Template/portfolio/MTF methodology | `template_*`, `multi_*`, `plan_*`, `first_party_*` | Methodology/tooling | Keep backend-owned. | Matching template/MTF/plan quality tests. |
| License/fulfillment/release/packaging | `license_*`, `fulfillment_*`, `fulfill_*`, `package_*`, `release_*`, `audit_*`, `bootstrap_*` | Packaging/license/release | Keep backend-owned; do not package private material in A67. | Packaging/license/fulfillment tests and privacy scan. |
| Build/manifest helpers | `build_*`, `blocksettings`, `view`, product manifest helpers | Manifest/build tooling | Keep backend-owned. | Manifest/build focal tests and docs-state. |

## Additional Wrapper Surfaces

| Surface | Paths | Owner family | A67 decision |
| --- | --- | --- | --- |
| Backend BAT launchers | `backend/sqx-edge-tool/run*.bat`, `backend/sqx-edge-relay/run-*.bat` | Local backend/relay runtime | Keep in owning backend folders. No service starts in A67. |
| Backend PowerShell tools | `backend/sqx-edge-tool/tools/*.ps1` | Packaging/license/backend support | Keep with backend tools. No key generation, packaging or fulfillment in A67. |
| Packaging BATs | `packaging/START_SQX_EDGE.bat`, `packaging/STOP_SQX_EDGE.bat` | Packaging/runtime bundle | Keep in packaging. No relocation before A68 wrapper plan. |
| Readiness kit BAT/PS1 | `resources/sqx-readiness-kit/01_Comprobador/*.bat`, `resources/sqx-readiness-kit/01_Comprobador/tools/*.ps1` | Readiness QXPRO/private operator kit | Keep in resource package. No install/uninstall actions in A67. |
| CI workflows | `.github/workflows/*.yml`, `.github/CODEOWNERS` | CI/ownership | Keep in `.github`. Changes require CI/test impact review. |

## Runbook Links

| Runbook / doc | Tool family |
| --- | --- |
| `docs/REMOTE_RUNBOOK1_OPERATOR_START_STOP.md` | Remote operator start/stop wrappers. |
| `docs/REMOTE_SERVICE_ROADMAP.md` | Remote service, access, tunnel and support wrappers. |
| `docs/SQX142_PERFORMANCE_ROADMAP.md` | SQX142 performance and Live Guard wrappers. |
| `docs/SQX142_CUSTOM_TASK_CONFIG_ROADMAP.md` | SQX142 task config gate wrappers. |
| `docs/maintenance/SQX142_PROJECT_RESOURCE_REPAIR_RUNBOOK.md` | Project resource repair wrapper. |
| `docs/maintenance/SQX142_PROJECT_LOAD_STABILIZER_RUNBOOK.md` | Project load stabilizer wrapper. |
| `docs/maintenance/SQX142_ELECTRON_CACHE_RUNBOOK.md` | Electron cache refresh wrapper. |
| `docs/sales/SALES_FULFILLMENT_RUNBOOK.md` | Fulfillment and sales tooling. |

## Move Policy

A67 authorizes documentation only. A later A68 move must include:

- one tool family per commit;
- old entrypoint preserved as shim or explicit compatibility break approved in governance;
- runbook and README pointer update;
- focal tests for the owner family;
- `git diff --check`;
- docs-state pytest;
- privacy scan;
- rollback path.

## No-Go

- No tools moved during A67.
- No wrappers moved during A67.
- No scripts executed during A67.
- No services started during A67.
- No scheduled tasks installed during A67.
- No cleanup executed during A67.
- No SQX runtime launch.
- No `data.db` writes.
- No `user/projects` writes.
- No Cloudflare/grant/checkout/email actions.
- No private key, license payload, token, protected URL or private evidence committed.

## A67 Closeout

A67 Tooling Ownership Map completed as `sqx-edge.tooling-ownership-map-v1`. The next restructuring phase is `A68 Low-Risk Physical Moves`, but only for a single low-risk domain with compatibility shims, focal tests and rollback.

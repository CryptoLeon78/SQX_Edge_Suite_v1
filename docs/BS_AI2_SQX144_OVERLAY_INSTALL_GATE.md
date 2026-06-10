# BS-AI2 SQX144 Overlay Install Gate

Marker: `bs-ai2-sqx144-overlay-install-gate-v1`

Status: `operator_manual_bsai_overlay_visual_smoke_confirmed`

Date: 2026-06-06

## Scope

BS-AI2 installs the BS-AI1 BlockSettings overlay into the confirmed SQX144 Full host web surface after the BS-AI1 backend and versioning contract passed. This phase is installation only: it does not run SQX, does not create projects, does not generate candidates and does not mutate SQX data stores.

Confirmed host posture:

- SQX144 Full / `sqx144_full` remains the confirmed primary local host.
- SQX142 Codex/QXPRO remains preserved diagnostic/methodology material, not fallback.
- SQX143 remains historical.
- SQX144 144.2953 remains governed separately by `SQX144-FULL-UPDATE2`.

## Install Evidence

Command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\sqx144_blocksettings_ai_overlay.ps1 install -Apply
```

Result:

- `ok=true`
- `status=installed`
- `version=sqx144-blocksettings-ai-overlay-v1`
- `backupRef=sqx144_bsai_overlay_20260606_122052`
- `privacy.localPathsReturned=false`
- `privacy.tokensReturned=false`
- `privacy.licenseMaterialReturned=false`

Preflight immediately before install:

- `installed=false`
- `sourcesPresent=true`
- `assetsPresent=false`
- `processCount=0`
- `blockers=[]`
- `writesDataDb=false`
- `writesUserProjects=false`
- `runsSqxTasks=false`

Post-install status:

- `installed=true`
- `assetsPresent=true`
- `sourcesPresent=true`
- `processCount=0`
- `blockers=[]`

Static installed-asset verification:

- `jsIncludeCount=1`
- `cssIncludeCount=1`
- `jsHashMatch=true`
- `cssHashMatch=true`
- `sourceJsHash=FBB26F411956FCFF57914482A739CAD7F73BAC8F03DBE20E254752A50332F7BC`
- `targetJsHash=FBB26F411956FCFF57914482A739CAD7F73BAC8F03DBE20E254752A50332F7BC`
- `sourceCssHash=3A39C60E6EEB814792FF411E81F53AE20DFE200159F21CFF6943DDBD951F0970`
- `targetCssHash=3A39C60E6EEB814792FF411E81F53AE20DFE200159F21CFF6943DDBD951F0970`

## Boundaries

BS-AI2 preserves the BS-AI1 versioning contract:

- Official v6/v7 `.sqb` resources remain outside the BS-AI write path.
- Capa2 default remains `BS_Filtros_v6`; D1 remains `BS_Filtros_v6_D1`.
- `BS_Filtros_v7_*` still requires `explicitBaseCanonicalId`.
- Candidates still use `BSAI_*` under `.local/blocksettings_ai/candidates/`.
- Candidates remain `promotionState=local_candidate`.

BS-AI2 did not:

- launch SQX;
- execute SQX tasks;
- write SQX `data.db`;
- write SQX `user/projects`;
- mutate databanks;
- handle license/activation material;
- use Migration Tool;
- copy engine/binarios/internals;
- promote SQX144 144.2953;
- make profitability or risk-zero claims.

## Manual Visual Smoke

Operator-owned smoke result:

- The operator manually opened the confirmed SQX144 Full host and AlgoWizard.
- The `BS-AI` launcher/panel was visually present.
- The overlay did not expose local paths, raw XML or secrets.
- No project creation/import was requested as part of this smoke.
- The operator left SQX closed after the smoke.
- Follow-up wrapper status reports `processCount=0`.

BS-AI2 is therefore closed as `operator_manual_bsai_overlay_visual_smoke_confirmed`.

Next recommended phase: BS-AI3 can run a local backend/overlay candidate smoke that creates a `BSAI_*` candidate and generated Capa1/Capa2 download pair, still without importing into SQX `user/projects`, writing `data.db` or mutating databanks.

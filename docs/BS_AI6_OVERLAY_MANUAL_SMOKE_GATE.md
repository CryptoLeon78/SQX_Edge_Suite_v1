# BS-AI6 Overlay Manual Smoke Gate

Marker: `bs-ai6-overlay-manual-smoke-gate-v1`

Status: `operator_panel_smoke_confirmed_download_links_verified_no_import`

Date: 2026-06-06

## Scope

BS-AI6 validates the installed SQX144 Full `BS-AI` panel from AlgoWizard. The smoke checks the visible controls, H1 explicit-v7 generation, D1 default generation and browser download links for the same local BS-AI flow proven in BS-AI5, without importing anything into SQX.

The operator opened SQX144 Full manually and Codex executed only the `BS-AI` panel controls. SQX remained on the AlgoWizard screen with `No strategies loaded`; no generated artifact was imported into SQX.

## Smoke Evidence

Wrapper status:

- `installed=true`
- `assetsPresent=true`
- `sourcesPresent=true`
- `processCount=7`
- `tokensReturned=false`
- `licenseMaterialReturned=false`
- `localPathsReturned=false`

Static contracts:

- `blocksettings ai overlay contracts ok`
- `blocksettings ai overlay manual smoke contracts ok`

Visual result:

- `manualPanelSmokeCompleted=true`
- `sqxProcessDetected=true`
- `launcherVisible=true`
- `panelVisible=true`
- `noLocalPathsVisible=true`
- `noRawXmlVisible=true`
- `noSecretsVisible=true`
- `noStrategiesLoadedVisible=true`

Private evidence:

- `.local/blocksettings_ai/smoke/bsai6_overlay_manual_smoke_gate_20260606_140427.json`
- `.local/blocksettings_ai/smoke/bsai6_overlay_manual_smoke_confirmed_20260606_153449.json`

Screenshots:

- `bsai6_sqx_before_clicks_20260606_152427.png`
- `bsai6_h1_after_generate_precise_20260606_152632.png`
- `bsai6_d1_base_clear_check_20260606_152940.png`
- `bsai6_d1_after_generate_low_20260606_153218.png`

## Expected Panel Controls

The installed overlay source exposes the manual smoke controls:

- `sqx-edge-bsai-launcher`
- `sqx-edge-bsai-panel`
- `sqx-edge-bsai-close`
- `sqx-edge-bsai-prompt`
- `sqx-edge-bsai-asset`
- `sqx-edge-bsai-timeframe`
- `sqx-edge-bsai-direction`
- `sqx-edge-bsai-base`
- `sqx-edge-bsai-plan`
- `sqx-edge-bsai-save`
- `sqx-edge-bsai-generate`
- `sqx-edge-bsai-output`

Download link behavior remains API-mediated:

- candidate link uses `apiUrl(state.candidate.downloadUrl)`
- project links use `apiUrl(item.downloadUrl)`
- `/api/...` backend download URLs are resolved through the local API origin

## Panel Smoke Results

H1 explicit v7 branch:

- prompt: `filtros H1 con ADX para AUDCAD largo`
- asset: `AUDCAD`
- timeframe: `H1`
- direction: `Long`
- explicit base: `BS_Filtros_v7_H1`
- candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r002`
- candidate download returned HTTP `200`
- project links visible in the panel
- Capa1: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r002_L_Capa1.cfx`
  - download returned HTTP `200`
  - `sha256=5209FDE1E9E0839697F2BA3BD7E89670543D95CE3A4DD092D79765ED97C90EC3`
  - ZIP valid with `config.xml`
- Capa2: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r002_L_Capa2.cfx`
  - download returned HTTP `200`
  - `sha256=81AFB49DF91E86640D0C71234720FAE8FFA682D14BAFC0E9DF1A1C6BE91F4E68`
  - ZIP valid with `config.xml`

D1 default branch:

- prompt: `filtros D1 con ADX para AUDCAD largo`
- asset: `AUDCAD`
- timeframe: `D1`
- direction: `Long`
- explicit base: blank
- candidate: `BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r002`
- candidate download returned HTTP `200`
- project links visible in the panel
- Capa1: `BSAI_AUDCAD_D1_BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r002_L_Capa1.cfx`
  - download returned HTTP `200`
  - `sha256=B8F426D543D3A5E3CA23B84D3904AC27B7373C51F5046D6D03E8BF15CF2FAA62`
  - ZIP valid with `config.xml`
- Capa2: `BSAI_AUDCAD_D1_BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r002_L_Capa2.cfx`
  - download returned HTTP `200`
  - `sha256=017FEE93811C2D9776A6405721BF05EB961DC104BC2248A5DF69C2CC446DB402`
  - ZIP valid with `config.xml`

Official BlockSettings:

- `officialBlockSettingsHashesUnchanged=true`
- `BS_Filtros_v7_H1` was used only by explicit H1 selection
- D1 default used `BS_Filtros_v6_D1`

## Boundaries

BS-AI6 smoke did not:

- import generated artifacts into SQX;
- write SQX `data.db`;
- write SQX `user/projects`;
- mutate databanks;
- run SQX tasks;
- launch SQX from scripts;
- handle license/activation material;
- use Migration Tool;
- promote SQX144 144.2953;
- promote any BSAI candidate into the official manifest.

Guard fields:

- `noSqxImport=true`
- `noDataDbWrite=true`
- `noUserProjectsWrite=true`
- `noDatabankMutation=true`
- `noSqxTasks=true`
- `noLicenseMaterial=true`
- `noMigrationTool=true`
- `no1442953Promotion=true`

SQX was left open for the operator after the smoke. No close/kill action was performed by Codex.

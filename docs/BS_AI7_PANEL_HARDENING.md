# BS-AI7 Panel Hardening

Marker: `bs-ai7-panel-hardening-v1`

Status: `operator_panel_hardening_smoke_confirmed_no_import`

Date: 2026-06-06

## Scope

BS-AI7 hardens the installed SQX144 Full `BS-AI` panel before any import workflow. The change targets real UI friction observed in BS-AI6: stale result reuse, unclear active candidate trace, clipped Capa1/Capa2 download names and policy-label ambiguity.

This phase does not import generated artifacts into SQX. It updates the overlay source, installs it through the guarded SQX144 overlay wrapper while SQX is closed, repeats local API smoke for H1 explicit-v7 plus D1 default, and then performs an operator-approved visual panel smoke in SQX144 AlgoWizard.

## Panel Hardening

The overlay now:

- clears previous candidate/project output when prompt, asset, timeframe, direction or explicit base changes;
- resets the local BS-AI session when any demand field changes;
- exposes `Nueva sesion / Limpiar` through `sqx-edge-bsai-reset`;
- disables `Guardar .sqb` until the current demand has a valid plan;
- disables `Generar .cfx` unless the active candidate belongs to the current form signature;
- ignores late API responses if the operator changes the form while a request is in flight;
- shows `Candidato activo`, `Base usada` and `Politica` in the output panel;
- labels download links as `Candidato .sqb`, `Capa1` and `Capa2`;
- wraps long candidate/project filenames so the panel does not hide the full artifact name.

The visible policy labels are:

- `v7 explicito` when `explicitBaseCanonicalId` is set or a v7 base is used;
- `D1 default v6_D1` when D1 resolves through the default blank-base policy;
- `default v6/v6_D1` for the normal v6 policy.

During the first visual smoke, the panel correctly resolved D1 to `BS_Filtros_v6_D1` but labelled it as `v7 explicito` because the UI checked the substring `explicit` inside a default/no-explicit source policy. The installed source was corrected and reinstalled: v7 is now labelled only when the selected/requested base contains `_v7`, while D1/default v6_D1 is classified explicitly.

## Install Evidence

Wrapper status before install:

- `installed=true`
- `assetsPresent=true`
- `sourcesPresent=true`
- `processCount=0`

Wrapper plan:

- `writesDataDb=false`
- `writesUserProjects=false`
- `runsSqxTasks=false`
- `writesSqxHost=true`
- `requiresApply=true`

Initial install:

- command: `tools\sqx144_blocksettings_ai_overlay.ps1 install -Apply`
- status: `installed`
- backup: `sqx144_bsai_overlay_20260606_160442`

Wrapper status after install:

- `installed=true`
- `assetsPresent=true`
- `sourcesPresent=true`
- `processCount=0`

Policy-label fix reinstall:

- command: `tools\sqx144_blocksettings_ai_overlay.ps1 install -Apply`
- status: `installed`
- backup: `sqx144_bsai_overlay_20260606_191153`
- preflight blockers: none
- post-install `processCount=0`
- backend catalog endpoint returned HTTP 200 before visual smoke

## Local Smoke Results

Private evidence:

- `.local/blocksettings_ai/smoke/bsai7_panel_hardening_api_smoke_20260606_160613.json`

Static contracts:

- `blocksettings ai overlay contracts ok`
- `blocksettings ai overlay manual smoke contracts ok`
- `blocksettings ai overlay hardening contracts ok`

API smoke H1 explicit-v7:

- prompt: `filtros H1 con ADX para AUDCAD largo`
- asset: `AUDCAD`
- timeframe: `H1`
- direction: `long`
- explicit base: `BS_Filtros_v7_H1`
- base resolved: `BS_Filtros_v7_H1`
- candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r003`
- Capa1: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r003_L_Capa1.cfx`
- Capa2: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r003_L_Capa2.cfx`
- candidate `.sqb` and both `.cfx` downloads are ZIP-valid with `config.xml`

API smoke D1 default:

- prompt: `filtros D1 con ADX para AUDCAD largo`
- asset: `AUDCAD`
- timeframe: `D1`
- direction: `long`
- explicit base: blank
- base resolved: `BS_Filtros_v6_D1`
- candidate: `BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r003`
- Capa1: `BSAI_AUDCAD_D1_BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r003_L_Capa1.cfx`
- Capa2: `BSAI_AUDCAD_D1_BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r003_L_Capa2.cfx`
- candidate `.sqb` and both `.cfx` downloads are ZIP-valid with `config.xml`

Official BlockSettings:

- `officialBlockSettingsHashesUnchanged=true`
- `BS_Filtros_v7_H1` is still explicit-selection only
- D1 blank-base flow still uses `BS_Filtros_v6_D1`

## Visual Smoke Results

Visual smoke was executed from the SQX144 AlgoWizard `BS-AI` panel after the operator closed SQX for reinstall. SQX was then opened visibly only for this panel smoke; no import, project load, SQX task or host-store mutation was performed.

Private evidence:

- screenshots under `.local/blocksettings_ai/smoke/screenshots/bsai7_reinstall_*`
- downloads under `.local/blocksettings_ai/smoke/downloads_bsai7_reinstall_20260606_192400/`
- download verification: `.local/blocksettings_ai/smoke/downloads_bsai7_reinstall_20260606_192400/bsai7_reinstall_download_verification.json`

Visual smoke H1 explicit-v7:

- prompt: `filtros H1 con ADX para AUDCAD largo`
- asset: `AUDCAD`
- timeframe: `H1`
- direction: `long`
- explicit base: `BS_Filtros_v7_H1`
- candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005`
- base shown: `BS_Filtros_v7_H1`
- policy shown: `v7 explicito`
- Capa1: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa1.cfx`
- Capa2: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r005_L_Capa2.cfx`

State invalidation smoke:

- changing the demand from H1/v7 toward D1 cleared previous Capa1/Capa2 links;
- output changed to `Cambios pendientes`;
- `Guardar .sqb` and `Generar .cfx` were disabled until a fresh plan/candidate matched the current form.

Visual smoke D1 default:

- prompt: `filtros D1 con ADX para AUDCAD largo`
- asset: `AUDCAD`
- timeframe: `D1`
- direction: `long`
- explicit base: blank
- candidate: `BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r005`
- base shown: `BS_Filtros_v6_D1`
- policy shown: `D1 default v6_D1`
- Capa1: `BSAI_AUDCAD_D1_BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r005_L_Capa1.cfx`
- Capa2: `BSAI_AUDCAD_D1_BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r005_L_Capa2.cfx`

Download verification:

- candidate H1 `.sqb`, candidate D1 `.sqb`, H1 Capa1/Capa2 `.cfx` and D1 Capa1/Capa2 `.cfx` returned HTTP 200;
- all six downloaded files are ZIP-valid and contain `config.xml`;
- SQX remained on the AlgoWizard editor surface with `No strategies loaded`.

## Boundaries

BS-AI7 did not:

- import generated artifacts into SQX;
- write SQX `data.db`;
- write SQX `user/projects`;
- mutate databanks;
- run SQX tasks;
- handle license/activation material;
- use Migration Tool;
- promote SQX144 144.2953;
- promote any BSAI candidate into the official manifest.

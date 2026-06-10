# BS-AI5 Project Pair Smoke

Marker: `bs-ai5-project-pair-smoke-v1`

Status: `pass_explicit_v7_and_d1_default_project_pairs_generated`

Date: 2026-06-06

## Scope

BS-AI5 validates local `.cfx` project-pair generation for two BS-AI candidates created during BS-AI4:

1. explicit v7 filter candidate;
2. D1 default filter candidate.

The smoke generates separate Capa1/Capa2 downloadable pairs through the local BS-AI backend. It does not import projects into SQX, does not write SQX `data.db`, does not write SQX `user/projects`, does not mutate databanks and does not run SQX tasks.

## Inputs

Explicit v7 branch:

- asset: `AUDCAD`
- timeframe: `H1`
- direction: `long`
- candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r001`
- candidate base: `BS_Filtros_v7_H1`
- source version policy: `explicit_base_preserve_official_v6_v7`

D1 default branch:

- asset: `AUDCAD`
- timeframe: `D1`
- direction: `long`
- candidate: `BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r001`
- candidate base: `BS_Filtros_v6_D1`
- source version policy: `filters_default_v6_v6_d1_v7_explicit_only`

## Explicit V7 Project Pair

Project:

- `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r001_L`

Generated files:

- Capa1: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r001_L_Capa1.cfx`
  - download: `/api/output/download/BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r001_L_Capa1.cfx`
  - `sha256=9E1C30467FE6F7BC0EDA6AC7889C6092D53ECE5277D4444E7EF11A3CC2CD6D84`
  - `size=730517`
  - ZIP valid with `config.xml`
- Capa2: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r001_L_Capa2.cfx`
  - download: `/api/output/download/BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r001_L_Capa2.cfx`
  - `sha256=F4CDB64A44072B04BE4F9801512B4A8B734BA866243127F231285B7CD195F530`
  - `size=626069`
  - ZIP valid with `config.xml`

BlockSettings trace:

- Capa1 remains official: `BS_Volatilidad_v6_intraday_v6`
- Capa2 uses local candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r001`
- Capa2 base remains official: `BS_Filtros_v7_H1`
- Capa2 source version policy: `explicit_base_preserve_official_v6_v7`

## D1 Default Project Pair

Project:

- `BSAI_AUDCAD_D1_BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r001_L`

Generated files:

- Capa1: `BSAI_AUDCAD_D1_BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r001_L_Capa1.cfx`
  - download: `/api/output/download/BSAI_AUDCAD_D1_BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r001_L_Capa1.cfx`
  - `sha256=3791BD6653A12F2B0C81C31B996000D0844C407366CF7258EFDE4CAA176714AF`
  - `size=730499`
  - ZIP valid with `config.xml`
- Capa2: `BSAI_AUDCAD_D1_BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r001_L_Capa2.cfx`
  - download: `/api/output/download/BSAI_AUDCAD_D1_BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r001_L_Capa2.cfx`
  - `sha256=1E7D8694BE05B84E094CB358A3E77C1EE1DDCA254012CACB7FF367535FBEF3B8`
  - `size=626491`
  - ZIP valid with `config.xml`

BlockSettings trace:

- Capa1 remains official: `BS_Volatilidad_v6`
- Capa2 uses local candidate: `BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r001`
- Capa2 base remains official: `BS_Filtros_v6_D1`
- Capa2 source version policy: `filters_default_v6_v6_d1_v7_explicit_only`

## Guards

Verified:

- `officialBlockSettingsHashesUnchanged=true`
- `sensitiveSqxSnapshotUnchanged=true`
- `noDataDbWrite=true`
- `noUserProjectsWrite=true`
- `noSqxUserDataWrite=true`
- `explicitV7Capa2UsesCandidate=true`
- `explicitV7BasePreserved=true`
- `d1DefaultCapa2UsesCandidate=true`
- `d1DefaultBasePreserved=true`
- `capa1OfficialForBoth=true`
- `projectDownloadsOk=true`
- `noSqxImport=true`
- `noSqxTaskExecution=true`

Private evidence:

- `.local/blocksettings_ai/smoke/bsai5_project_pair_smoke_20260606_114509.json`

## Boundaries

BS-AI5 did not:

- import generated artifacts into SQX;
- write SQX `data.db`;
- write SQX `user/projects`;
- mutate databanks;
- run SQX tasks;
- launch SQX;
- handle license/activation material;
- use Migration Tool;
- promote SQX144 144.2953;
- promote any BSAI candidate into the official manifest.

Next recommended phase: BS-AI6 overlay-driven manual browser smoke can trigger the same local API flow from the SQX144 `BS-AI` panel and verify the user-facing controls/download links, still without importing into SQX.

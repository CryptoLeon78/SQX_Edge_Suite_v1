# BS-AI3 Local Candidate Project Smoke

Marker: `bs-ai3-local-candidate-project-smoke-v1`

Status: `pass_local_candidate_and_project_pair_generated`

Date: 2026-06-06

## Scope

BS-AI3 validates the BS-AI backend flow after BS-AI2 visual confirmation:

1. read the local BlockSettings AI catalog;
2. create a local BS-AI session;
3. plan a version-safe candidate;
4. save a `BSAI_*` candidate `.sqb`;
5. download the candidate through the local API;
6. generate a Capa1/Capa2 `.cfx` pair for browser download;
7. verify official BlockSettings and SQX host data/project/databank boundaries remain unchanged.

The smoke is local only. It does not import into SQX and does not run SQX tasks.

## Smoke Input

Accepted smoke input:

- asset: `AUDCAD`
- timeframe: `H1`
- direction: `long`
- intent: `filtros H1 con ADX`
- layer: Capa2 filter candidate

A preliminary `EURUSD` smoke reached candidate creation but project generation was blocked by the existing data-range guard: `Cross-broker retest data range does not overlap requested period for EURUSD_darwinex`. That blocked attempt did not generate a project pair. The accepted BS-AI3 pass is the `AUDCAD` smoke below.

## Candidate Result

- `artifactId=BSAI_Filtros_L2_H1_from_BS_Filtros_v6_r002`
- `filename=BSAI_Filtros_L2_H1_from_BS_Filtros_v6_r002.sqb`
- `baseCanonicalId=BS_Filtros_v6`
- `sourceVersionPolicy=filters_default_v6_v6_d1_v7_explicit_only`
- `candidateRevision=r002`
- `promotionState=local_candidate`
- `downloadUrl=/api/blocksettings/ai/download/BSAI_Filtros_L2_H1_from_BS_Filtros_v6_r002`
- `sha256=05233D45171EF9E12FBBE2246EA5549A46178748B7483B13B730F398481527D5`

Candidate ZIP verification:

- `.sqb` is a ZIP.
- `config.xml` is present.
- API download returned non-empty content.

## Project Pair Result

Project name:

- `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v6_r002_L`

Generated files:

- Capa1: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v6_r002_L_Capa1.cfx`
  - download: `/api/output/download/BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v6_r002_L_Capa1.cfx`
  - `sha256=16F15C6D427218B540DE1D783E1994EE7EE8B3F709849D8EED39E4AA49A8D2E3`
  - `size=730514`
- Capa2: `BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v6_r002_L_Capa2.cfx`
  - download: `/api/output/download/BSAI_AUDCAD_H1_BSAI_Filtros_L2_H1_from_BS_Filtros_v6_r002_L_Capa2.cfx`
  - `sha256=A79A61E0B409CD6A5F4D4713CA3E2A4DE7E1683315D6B0B8A111818B5D7CCE79`
  - `size=626032`

BlockSettings trace:

- Capa1 remains official: `BS_Volatilidad_v6_intraday_v6`
- Capa2 uses local candidate: `BSAI_Filtros_L2_H1_from_BS_Filtros_v6_r002`
- Capa2 candidate source scope: `local_candidate`
- Capa2 base remains official: `BS_Filtros_v6`
- v7 filters were not selected.

## Guards

Verified:

- `officialBlockSettingsHashesUnchanged=true`
- `sensitiveSqxSnapshotUnchanged=true`
- `candidateZipHasConfigXml=true`
- `candidateApiDownloadOk=true`
- `projectDownloadsOk=true`
- `noDataDbWrite=true`
- `noUserProjectsWrite=true`
- `noDatabankMutation=true`
- `noSqxImport=true`
- `noSqxTaskExecution=true`

Post-smoke wrapper status:

- `installed=true`
- `assetsPresent=true`
- `sourcesPresent=true`
- `processCount=0`

Private evidence:

- `.local/blocksettings_ai/smoke/bsai3_local_candidate_project_smoke_20260606_111752.json`

## Boundaries

BS-AI3 did not:

- import generated projects into SQX;
- write SQX `data.db`;
- write SQX `user/projects`;
- mutate databanks;
- run SQX tasks;
- launch SQX;
- handle license/activation material;
- use Migration Tool;
- promote SQX144 144.2953;
- promote the BSAI candidate into the official manifest.

Next recommended phase: BS-AI4 can test an explicit v7-selection smoke and a D1 default smoke, proving `BS_Filtros_v7_*` still requires `explicitBaseCanonicalId` while D1 defaults to `BS_Filtros_v6_D1`.

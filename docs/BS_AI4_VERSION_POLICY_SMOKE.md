# BS-AI4 Version Policy Smoke

Marker: `bs-ai4-version-policy-smoke-v1`

Status: `pass_explicit_v7_and_d1_default_verified`

Date: 2026-06-06

## Scope

BS-AI4 validates the live BS-AI backend versioning contract after BS-AI3:

1. `BS_Filtros_v7_*` cannot be selected by alias/request alone.
2. `BS_Filtros_v7_*` can be used only with `explicitBaseCanonicalId`.
3. D1 filter requests without an explicit version resolve to `BS_Filtros_v6_D1`.
4. Official `.sqb` files remain immutable.
5. No SQX import, project generation or SQX host data/project/databank mutation happens during this smoke.

This phase is local backend smoke only. It creates local `BSAI_*` candidates, not `.cfx` projects.

## Catalog Policy Confirmed

The local catalog reported:

- `capa2Default=BS_Filtros_v6`
- `capa2D1Default=BS_Filtros_v6_D1`
- `filtersV7=explicitBaseCanonicalId_only`
- `officialResourcesImmutable=true`

## Smoke Matrix

### Non-Explicit V7 Block

Input:

- prompt: `filtros H1 con ADX para AUDCAD largo smoke BS-AI4`
- requested blocksetting: `BS_Filtros_v7_H1`
- `explicitBaseCanonicalId` absent

Result:

- `ok=false`
- `error=filters_v7_requires_explicit_base_canonical_id`
- no candidate promoted or generated from this blocked request

### Explicit V7 Selection

Input:

- asset: `AUDCAD`
- timeframe: `H1`
- direction: `long`
- prompt: `filtros H1 con ADX`
- `explicitBaseCanonicalId=BS_Filtros_v7_H1`

Result:

- `artifactId=BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r001`
- `filename=BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r001.sqb`
- `baseCanonicalId=BS_Filtros_v7_H1`
- `baseVariant=v7_h1`
- `sourceVersionPolicy=explicit_base_preserve_official_v6_v7`
- `candidateRevision=r001`
- `promotionState=local_candidate`
- `downloadUrl=/api/blocksettings/ai/download/BSAI_Filtros_L2_H1_from_BS_Filtros_v7_H1_r001`
- `sha256=2EE3F9A30E5FACC7C84C3560435B97329EAE5FD330238DF6E83C053129679A63`
- candidate ZIP has `config.xml`
- candidate API download returned non-empty content

### Explicit V7 Timeframe Mismatch Block

Input:

- timeframe: `D1`
- `explicitBaseCanonicalId=BS_Filtros_v7_H1`

Result:

- `ok=false`
- `error=explicit_base_timeframe_mismatch`
- no candidate promoted or generated from this blocked mismatch

### D1 Default Selection

Input:

- asset: `AUDCAD`
- timeframe: `D1`
- direction: `long`
- prompt: `filtros D1 con ADX`
- no explicit base version

Result:

- `artifactId=BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r001`
- `filename=BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r001.sqb`
- `baseCanonicalId=BS_Filtros_v6_D1`
- `baseVariant=v6_d1`
- `sourceVersionPolicy=filters_default_v6_v6_d1_v7_explicit_only`
- `candidateRevision=r001`
- `promotionState=local_candidate`
- `downloadUrl=/api/blocksettings/ai/download/BSAI_Filtros_L2_D1_from_BS_Filtros_v6_D1_r001`
- `sha256=6976714C83C79F0330918035AD0C969770EE92AA00AE25FAA8DBD3755562C853`
- candidate ZIP has `config.xml`
- candidate API download returned non-empty content

## Guards

Verified:

- `officialBlockSettingsHashesUnchanged=true`
- `sensitiveSqxSnapshotUnchanged=true`
- `candidateZipsHaveConfigXml=true`
- `candidateApiDownloadsOk=true`
- `v7RequiresExplicitBaseCanonicalId=true`
- `v7ExplicitSelectionUsedV7Base=true`
- `d1DefaultUsedV6D1=true`
- `v7D1MismatchBlocked=true`
- `noDataDbWrite=true`
- `noUserProjectsWrite=true`
- `noSqxUserDataWrite=true`
- `noSqxImport=true`
- `noSqxTaskExecution=true`
- `noProjectGeneration=true`

Private evidence:

- `.local/blocksettings_ai/smoke/bsai4_version_policy_smoke_20260606_113314.json`

## Boundaries

BS-AI4 did not:

- generate `.cfx` projects;
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

Next recommended phase: BS-AI5 can run a local project-pair smoke using one explicit v7 candidate and one D1-default candidate as separate controlled project generation attempts, still without SQX import or host datastore mutation.

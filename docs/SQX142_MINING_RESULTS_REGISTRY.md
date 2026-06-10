# SQX142-MINING-REGISTRY1/2 Mining Results Registry

Status: `active_visual_funnel_panel`

Version: `sqx142-mining-results-registry-v1`

## Purpose

The registry stores real SQX142 mining/custom project evidence in an SQX Edge-owned SQLite database. Traceability belongs to the custom project first, then to its databanks, tests and strategy rows.

Local database:

```text
.local/sqx142_mining_registry/sqx142_mining_registry.sqlite
```

This file is local/private evidence. It is not SQX `user/data/data.db`.

## Registered Custom

First real test record:

- Project: `SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1`
- Asset/timeframe: `AUDCAD` / `H1`
- Symbol/profile: `AUDCAD_darwinex` / `SQX Edge / Darwinex`
- Layer: `Capa1`
- BlockSetting family: `BS_Momentum_v6`
- Source: fresh SQX142 custom project, not legacy lab donor.

## Current Databank Snapshot

The registry scanned the local SQX142 project `databanks` folder read-only and recorded:

- `Results`: 2000 `.sqx`
- `RETEST 0`: 459 `.sqx`
- `retest 1`: 108 `.sqx`
- `TICK`: 92 `.sqx`
- `MC`: 59 `.sqx`
- `MC2`: 59 `.sqx`
- `Sequential`: 59 `.sqx`
- `Monkey Test`: 59 `.sqx`
- `Synthetic`: 59 `.sqx`
- `SPP`: 42 `.sqx`
- `WFM`: 39 `.sqx`
- `Forward`: 23 `.sqx`
- `SQX EDGE CORR1 STABILITY`: 23 `.sqx` after the manual CORR1 stability retest.
- `SQX EDGE CORR1 TAGGED`: 23 `.sqx` after the manual CORR1 tag review.

The separate exported Forward CSV/tagger evidence remains linked as a test/export confirmation, but the funnel source of truth is the custom project and its databanks.

## Registered Capa1 C2 CORR1 Decision

The first real CORR1 decision is also stored against the custom project, not as a loose CSV comparison:

- Step `91`: `Forward` -> `SQX EDGE CORR1 STABILITY`, `23` rows.
- Step `92`: `SQX EDGE CORR1 STABILITY` -> `SQX EDGE CORR1 TAGGED`, `23` rows.
- Step `93`: `SQX EDGE CORR1 TAGGED` -> `c2_template_selection_decision`, `23` rows analyzed.

Registered decision summary:

- C2 template winners: `1`;
- template-similar candidates: `22`;
- review candidates: `0`;
- status: `pass`;
- source: `sqx142-capa1-c2-corr1-registered-decision-v1`.
- decision domain: `capa1_c2_template_selection`.

The decision reader parses SQX local `.sqx` `dailyEquity.bin` series read-only while SQX is closed and writes only to the SQX Edge-owned registry/evidence folder.

## Parked USDJPY H1 Capa2 Candidate Cohort

The registry also records the real USDJPY H1 Volatilidad Capa2 closeout as a parked candidate cohort:

- Project: `SQX_EDGE_API_FRESH_USDJPY_H1_Volatilidad_20260530_082732_Capa2`.
- Source databank: `SQX EDGE C2 CORR TAGGED`.
- Input rows: `8`.
- Accepted candidate cohort: `3` strategies.
- Similar reserves: `5`.
- Primary Champion: `WF Matrix - Strategy 0.13535`.
- Co-candidates: `WF Matrix - Strategy 0.6228` and `WF Matrix - Strategy 0.26354`.
- Status: `accepted_as_single_asset_capa2_candidate_not_portfolio_master`.
- Portfolio Master guard: `deferred_pending_multi_asset_context`.

This node parks evidence for later portfolio construction. It does not mutate SQX local, generate strategies, run Portfolio Master or claim a final global portfolio.

## Commands

```powershell
tools\sqx142_mining_registry.ps1 -Action status
tools\sqx142_mining_registry.ps1 -Action scan-project -ProjectKey "SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1" -ProjectDir "<local SQX142 project folder>" -MaxSqxParse 300
tools\sqx142_mining_registry.ps1 -Action funnel-json -ProjectKey "SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1"
```

The local API exposes the sanitized funnel at:

```text
GET /api/sqx142/mining-registry/funnel?projectKey=...
POST /api/sqx142/mining-registry/scan-project
```

Edge Factory can ingest a project snapshot through `recordMiningRegistryFunnel`, which updates the asset context and Capa1 analysis funnel state.

## REGISTRY2 Visual Panel

`SQX142-MINING-REGISTRY2 Visual Funnel Panel` renders the same registered databank funnel inside:

- Edge Factory: panel `SQX142-MINING-REGISTRY2` after the command strip.
- Mining Control: `Embudo registrado — SQX142 local` below the editable mining funnel.

Buttons:

- `Cargar embudo local`: reads the SQX Edge registry through `GET /api/sqx142/mining-registry/funnel`.
- `Actualizar desde SQX local`: scans `SQX142_ROOT/user/projects/<custom>/databanks` read-only through `POST /api/sqx142/mining-registry/scan-project`, then returns sanitized funnel JSON.
- `Aplicar a Edge Factory`: calls `recordMiningRegistryFunnel` so Edge Factory marks the Capa1 custom as recorded and shows the real `Results/Forward/SPP/WFM/CORR1` counts in its trace signals.
- `Estado C2 CORR1 local` / `Registrar C2 CORR1` / `Preflight C2 CORR1` / `Parchear Capa1 SQX` / `Rollback C2 CORR1`: call the Capa1 C2 CORR2 local custom project integration endpoint and then refresh the registry. These actions are governed by `docs/SQX142_PORTFOLIO_CORR2_LOCAL_CUSTOM_PROJECT_INTEGRATION.md`.
- `Analizar C2 CORR1`: calls the registered Capa1 C2 CORR1 decision endpoint over `SQX EDGE CORR1 TAGGED` and records the `c2_template_selection_decision` node back into the same custom-project funnel.

The visual source remains the local SQX Edge registry. REGISTRY2 scanning stays read-only; Capa1 C2 CORR2 patching is a separate guarded action that requires SQX closed and creates the `SQX EDGE CORR1 STABILITY` / `SQX EDGE CORR1 TAGGED` nodes.

## Boundaries

Allowed:

- Read SQX142 `user/projects/<custom>/databanks` while SQX is closed.
- Parse `.sqx` ZIP metadata and strategy fingerprints read-only.
- Store sanitized counts, filenames, metrics and funnel snapshots in SQX Edge-owned SQLite.

Blocked:

- Writing SQX `user/data/data.db`.
- Patching jars, internal plugins, license or activation.
- Launching SQX, `run_project`, Migration Tool or `/project/checkResources`.
- Deleting databanks or mutating SQX projects as part of registry ingestion.
- Treating tagger filtering as the decision engine.

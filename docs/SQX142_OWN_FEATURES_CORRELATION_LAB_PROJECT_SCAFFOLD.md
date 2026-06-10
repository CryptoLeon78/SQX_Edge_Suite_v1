# SQX142-OWN-FEATURES3B Correlation Lab Project Scaffold

Status: `installed_view_confirmed_retest_carrier_blocked_by_legacy_exit_dependency`

Version: `sqx142-own-features3b-correlation-lab-project-scaffold-v1`

## Purpose

This block creates one clearly named SQX142 lab custom project for the Correlation Pack manual confirmation, so the operator does not need to choose among old customs or red projects.

The lab project is a local SQX142-only scaffold. It is not a production Capa1/Capa2 base and it is not a methodology promotion.

## Installed Lab Project

- Donor project: `Mining15_USDJPY_H4_BS_Volatilidad_v6_LS_Capa1`.
- Target project: `SQX_EDGE_CORR_LAB_Mining15_USDJPY_H4_20260527`.
- Backup id: `sqx142-own-features3b-correlation-lab-project-scaffold-v1_20260527_133250`.
- Target `project.cfx` hash after scaffold: `4197bd1a3f5f57909f7bcbe56f8a3f1c8ed4cc2b46861e59401bbfa1a8d44bf7`.
- Target directory hash after scaffold: `2d9c46a4b3514cc8a1c79fb9d8809750584f16892e4793f7cf30e8039e055dda`.

Only these databanks were copied from the donor:

- `Monkey Test`: `86` strategies.
- `Syntetic`: `86` strategies.

The scaffold also creates empty output databank:

- `SQX EDGE CORR TAGGED`: `0` strategies before manual run.

## Project Patch

Inside the lab copy only:

- Project name is patched to `SQX_EDGE_CORR_LAB_Mining15_USDJPY_H4_20260527`.
- Databank views for `Monkey Test`, `Syntetic`, `Foward` and `SQX EDGE CORR TAGGED` are set to `SQX EDGE CORRELATION REVIEW`.
- `Retest-Task2.xml` is renamed in the project UI as `SQX EDGE CORR TAG`.
- `SQX EDGE CORR TAG` uses input `Monkey Test`.
- `SQX EDGE CORR TAG` uses output `SQX EDGE CORR TAGGED`.
- `SQX EDGE CORR TAG` uses Custom Analysis `SQXEdgeCorrelationTagger`.
- `FitPortfolio` is disabled for the lab tag task.
- `CrossChecks` are disabled for the lab tag task.
- The lab tag task is left inactive by default to avoid accidental run.

## Operator Flow

1. Open SQX142.
2. Open project `SQX_EDGE_CORR_LAB_Mining15_USDJPY_H4_20260527`.
3. Confirm project does not show unresolved resources.
4. Open databank `Monkey Test`.
5. Confirm view `SQX EDGE CORRELATION REVIEW` is active or select it manually.
6. If you only want a visual check, inspect the six SQXEdge columns on `Monkey Test`.
7. To populate fresh tagged output, enable/run only task `SQX EDGE CORR TAG`.
8. Inspect output databank `SQX EDGE CORR TAGGED`.
9. Confirm visible values in `SQXEdgeCorrDecision`, `SQXEdgeCorrRank`, `SQXEdgeCorrScore`, `SQXEdgeMaxCorr`, `SQXEdgeCorrStatus` and `SQXEdgeNearestWinner`.

If every row stays `-1`, `0`, empty or `missing`, the most likely cause is name mismatch between the installed `correlation_decisions.csv` and the databank strategy names.

## Manual Retest Carrier Finding

The lab view and Custom Analysis were visible in SQX142, but running `SQX EDGE CORR TAG` against the copied `Monkey Test` databank rejected the strategies with `backtest exception` before the tagger could populate `SQX EDGE CORR TAGGED`.

Sanitized local log diagnosis:

- The failure is not `SQXEdgeCorrelationTagger`.
- SQX142 cannot instantiate old strategies that reference retired snippet/class `ExitAfterDays`.
- The copied donor databanks were mined before the day-based exit snippets were archived.
- A Retest task must reconstruct/backtest the strategy before Custom Analysis can write special values, so this lab carrier is blocked for those legacy rows.
- Post-fix read-only status reports `retiredDependencyPreflight.status=blocked_legacy_retired_snippets`: `Monkey Test` has `86/86` affected strategies and `Syntetic` has `86/86` affected strategies.

Operational decision:

- Do not create a placeholder `ExitAfterDays` snippet just to make old strategies load.
- Do not keep rerunning this lab Retest against affected databanks.
- Use a fresh mining/custom project, or a donor databank that passes the retired-dependency preflight, before using Retest as a visual carrier for SQX correlation tags.
- Edge Factory remains the canonical source for correlation decisions when the SQX Retest carrier is blocked.

## Commands

Status:

```powershell
tools\sqx142_own_features_correlation_lab_project_scaffold.ps1 -Action status
```

Plan:

```powershell
tools\sqx142_own_features_correlation_lab_project_scaffold.ps1 -Action plan
```

Install:

```powershell
tools\sqx142_own_features_correlation_lab_project_scaffold.ps1 -Action install
```

Rollback:

```powershell
tools\sqx142_own_features_correlation_lab_project_scaffold.ps1 -Action rollback -BackupId sqx142-own-features3b-correlation-lab-project-scaffold-v1_20260527_133250
```

Rollback moves the lab project to SQXEdge quarantine. It does not recursively delete it.

## Boundaries

Allowed:

- Create one lab project under `SQX142_ROOT/user/projects`.
- Copy only donor databanks `Monkey Test` and `Syntetic`.
- Patch only the copied lab `project.cfx`.
- Record evidence under ignored `.local/sqx142_own_features/lab_project_scaffold/`.

Blocked:

- SQX runtime launch from script.
- `data.db` writes.
- Jars, engine files, internal plugins, license or activation changes.
- Production Capa1/Capa2 project mutation.
- Databank deletion.
- `run_project`.
- Migration Tool.
- Forced pass or profitability claims.

## Verification

- `tools\sqx142_own_features_correlation_lab_project_scaffold.ps1 -Action plan` returned donor `Monkey Test=86`, `Syntetic=86`, target missing and planned rollback by quarantine.
- `tools\sqx142_own_features_correlation_lab_project_scaffold.ps1 -Action install` created the lab project with backup id `sqx142-own-features3b-correlation-lab-project-scaffold-v1_20260527_133250`.
- Post-install status reports target exists, `Monkey Test=86`, `Syntetic=86`, `SQX EDGE CORR TAGGED=0`, view `SQX EDGE CORRELATION REVIEW`, custom analysis `SQXEdgeCorrelationTagger`, input `Monkey Test`, output `SQX EDGE CORR TAGGED`.
- Manual SQX run confirmed `SQX EDGE CORR TAG` starts, but `SQX EDGE CORR TAGGED` stays empty because legacy strategies in `Monkey Test` reference retired dependency `ExitAfterDays`; the tool now exposes `retiredDependencyPreflight` and future installs block donors with `ExitAfterDays` or `ExitAfterTradingDays`.
- `backend/sqx-edge-tool/test_sqx142_correlation_lab_project_scaffold.py` passed.
- `tests/js/contracts/sqx142_own_features3b_correlation_lab_project_scaffold_contracts.mjs` passed.

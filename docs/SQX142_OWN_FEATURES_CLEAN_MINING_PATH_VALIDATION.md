# SQX142-OWN-FEATURES4 Clean Mining Path Validation

Status: `pass`

Version: `sqx142-own-features4-clean-mining-path-validation-v1`

## Purpose

This block moves the Correlation Pack validation away from contaminated legacy databanks and into a fresh SQX142 mining path.

`SQX142-OWN-FEATURES3B` proved that the view and Custom Analysis are visible, but the copied `Monkey Test` carrier is blocked because its old strategies reference retired dependencies `ExitAfterDays` and `ExitAfterTradingDays`. FEATURES4 treats that lab project as blocked evidence, not as a source to repair by adding placeholder snippets.

## Read-Only Preflight

Run:

```powershell
tools\sqx142_own_features_clean_mining_path_validation.ps1 -Action status
tools\sqx142_own_features_clean_mining_path_validation.ps1 -Action checklist
```

Current read-only findings:

- Generated custom projects `Mining15_AUDCAD_H1_BS_Momentum_v6_Capa1` and `Mining15_AUDCAD_H1_BS_Momentum_v6_Capa2` report no stabilizer findings and no stale `zipfstmp*.tmp` files.
- `SQX EDGE CORRELATION REVIEW` assets are installed and the tag CSV schema remains valid.
- The old lab project remains blocked by retired dependencies, so it must not be used as the Retest carrier for FEATURES4.
- SQX was open during the first FEATURES4 preflight; any install or rollback action must wait until SQX is closed.
- Runtime follow-up confirmed both generated Mining15 layers are clean in SQX UI and in `taskmanager/listProjects`.
- The Project Generator `SQX Edge / Darwinex` profile now strips sibling `Resources/Instruments` entries while preserving each `Symbols/Symbol/InstrumentInfo`, matching the SQX142-compatible shape validated locally.
- Fresh API-generated AUDCAD H1 Momentum Capa1/Capa2 customs loaded without unresolved-resource warnings.
- Fresh Capa1 mining/retest produced a real `Results` databank, but a later SQX project-config save failed and the Capa1 `project.cfx` must be restored before continuing that custom project.
- The latest fresh Capa1 run did not produce a usable `Foward` databank; the final Forward export remains pending.

## Current Incident Note

After the fresh Capa1 mining/retest run, SQX reported that the Capa1 project config was corrupted and offered to use a default config. Read-only log inspection points to a SQX ZIP update failure during task activation, not to a resource-resolution failure:

- `Saving project config failed`
- `Failed to update zip content`
- `FileSystemAlreadyExistsException`
- later default config had no tasks and only one databank.

The safe recovery rule is:

1. Do not mutate while SQX is open.
2. Preserve the generated databanks and external saved strategy copies.
3. After SQX is closed, backup the project folder, validate the surviving ZIP temp file, restore `project.cfx` from the valid temp if it matches the full 12-task config, then remove/quarantine the stale temp.
4. Reopen SQX and confirm the project has 12 tasks, no unresolved resources, and the saved databanks are visible.

Recovery applied on 2026-05-29:

- SQX process check was clean before mutation.
- The fresh Capa1 project folder was backed up under ignored local evidence.
- The valid surviving ZIP temp was restored over the 322-byte default `project.cfx`.
- Because the temp ZIP had reintroduced three sibling `Resources/Instruments` nodes, those were stripped again from `Build-Task1.xml`, `AutomaticRetest-Task8.xml` and `AutomaticRetest-Task7.xml`.
- Final `project.cfx` hash: `51D2824DF333A2F99EDA82B4ABC9E30275564003F4650B05D7DA6C4D564EA38D`.
- Final read-only validation: 13 ZIP entries, 12 tasks, 17 databanks, zero `Resources/Instruments`, zero `Resources/CustomBlocks` children, and one nested `Symbols/Symbol/InstrumentInfo` per task XML.
- Operator reopened SQX and confirmed fresh Capa1 loads with no config error, all tasks present, no red unresolved resources, and `Results` with 2000 strategies visible.

## Fresh Forward Data Smoke

The operator exported the fresh Forward CSV after the restored project loaded cleanly:

- Source rows: 23.
- Source hash: `B190C4B0B04E8F527A4D0A361D0073B62D5747CB6CF8CBE5001EEA438D9A7BEA`.
- Data Smoke build output:
  - `.local/sqx142_own_features/data_smoke/fresh_forward_20260529_215735/correlation_decisions.csv`
  - rows: 23
  - tag hash: `3401856dc3dc4fb5d71a5d4c116f3049ba0cd372d3c1dc8559d9271d7d6c2732`
  - decisions: `portfolio=1`, `similar=22`, `review=0`
- Tag CSV was installed while SQX was closed:
  - target: `user/extend/SQXEdge/Correlation/correlation_decisions.csv`
  - backup id: `sqx142-own-features2-correlation-data-smoke-v1_20260529_215849`

Final visual/export confirmation:

- SQX `SQX EDGE CORRELATION REVIEW` columns populated on the fresh Forward databank.
- Operator enabled `SQXEdgeCorrelationTagger` Custom Analysis in the Forward task ranking settings.
- `Filter by results of custom analysis` was kept disabled so SQX tags/annotates all rows without removing non-portfolio rows.
- Final tagger export:
  - rows: 23
  - hash: `092AB2E3C97ED81DC8E2BD7FE9793B952D2E61D9B0A9F325A1520A8C78EC99C4`
  - `SQX Edge Corr Decision`: 1 row with `1`, 22 rows with `0`
  - `SQX Edge Corr Rank`: 1 row with `1`, 22 rows with `-1`
  - `SQX Edge Corr Status`: 23 rows with `1`
  - `SQX Edge Nearest Winner`: populated on 22 similar rows
- Final FEATURES4 record:
  - `.local/sqx142_own_features/clean_mining_path_validation/sqx142-own-features4-clean-mining-path-validation-v1_manual_record_20260529_221731.json`
  - outcome: `pass`

## Operator Validation Path

1. Open SQX142 manually.
2. Confirm the generated Capa1/Capa2 projects do not show alternating red unresolved-resource status at startup.
3. Generate or select a fresh custom from Edge Factory using the corrected `SQX Edge / Darwinex` profile.
4. Load the fresh custom in SQX142 without clicking `Load config using these settings` unless SQX forces it.
5. Run a short fresh mining/retest path so the output databank does not come from the old `ExitAfterDays` carrier.
6. Export the fresh output databank CSV.
   - For Data Smoke, export the selected databank without SQXEdge tagger columns first; the Data Smoke builds the tag CSV from that export.
   - For academic final validation, prefer the final survivor/Forward databank only if it is populated and was produced by the predeclared pipeline. If Forward is empty, use the latest non-empty survivor databank only as a pipeline smoke test, not as final academic evidence.
7. Build a new correlation tag CSV from that fresh CSV:

```powershell
tools\sqx142_own_features_correlation_data_smoke.ps1 -Action build -InputCsv <fresh-export.csv>
```

8. Close SQX142 before installing the new tag CSV:

```powershell
tools\sqx142_own_features_correlation_data_smoke.ps1 -Action install -InputCsv <fresh-export.csv>
```

9. Reopen SQX142, select `SQX EDGE CORRELATION REVIEW`, and confirm the SQXEdge columns populate for matching fresh rows.

## Recording

After the manual path, record the result locally:

```powershell
tools\sqx142_own_features_clean_mining_path_validation.ps1 -Action record -Outcome pass -GeneratedProjectsStable -FreshCustomGenerated -FreshMiningRun -FreshCsvExported -DataSmokeBuilt -TagCsvInstalled -ColumnsPopulated -NoRetiredDependencies -NoUnresolvedResources -OperatorNote "Confirmed fresh SQX142 path."
```

Evidence is written only under ignored `.local/sqx142_own_features/clean_mining_path_validation/`.

## Boundaries

Blocked:

- SQX runtime launch from scripts.
- Jar, engine, binary, internal plugin, license or activation changes.
- `data.db` writes.
- Production Capa1/Capa2 base mutation.
- Databank deletion.
- `run_project`.
- Migration Tool.
- Placeholder snippets for retired dependencies.
- Forced pass or profitability claims.

Allowed:

- Read-only project/load status.
- Manual operator validation in SQX142.
- Fresh exported CSV processing through the existing Data Smoke builder.
- Installing only `user/extend/SQXEdge/Correlation/correlation_decisions.csv` after SQX is closed, with the existing backup/hash/rollback discipline.

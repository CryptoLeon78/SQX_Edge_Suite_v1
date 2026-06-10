# SQX142-OWN-FEATURES5 Forward Tagger Repeatable Flow

Status: `built_from_features4_pass_ready_for_reuse`

Version: `sqx142-own-features5-forward-tagger-flow-v1`

## Purpose

This block turns the successful FEATURES4 manual path into a repeatable operator flow:

1. export a clean Forward/Foward databank CSV before using the SQXEdge tagger as a filter;
2. build and install `correlation_decisions.csv` through the existing Data Smoke guard;
3. enable `SQXEdgeCorrelationTagger` in SQX only as an annotation step;
4. keep `Filter by results of custom analysis` disabled so SQX does not remove rows;
5. verify/export the populated `SQX EDGE CORRELATION REVIEW` columns.

Edge Factory/Data Smoke remains the canonical correlation decision engine. SQX is the lab visualization/tagging surface.

## Tool

```powershell
tools\sqx142_own_features_forward_tagger_flow.ps1 -Action status
tools\sqx142_own_features_forward_tagger_flow.ps1 -Action checklist
tools\sqx142_own_features_forward_tagger_flow.ps1 -Action validate-export -InputCsv <tagger-confirmation-export.csv>
tools\sqx142_own_features_forward_tagger_flow.ps1 -Action record -Outcome pass -UntaggedForwardCsvExported -DataSmokeBuilt -TagCsvInstalled -TaggerEnabled -FilterByResultsDisabled -ColumnsPopulated -FinalTaggerCsvExported
```

`validate-export` is read-only. It checks the final SQX export for:

- `SQX Edge Corr Decision`
- `SQX Edge Corr Rank`
- `SQX Edge Corr Score`
- `SQX Edge Max Corr`
- `SQX Edge Corr Status`
- `SQX Edge Nearest Winner`

It writes evidence under ignored `.local/sqx142_own_features/forward_tagger_flow/`.

## Repeatable Sequence

1. In SQX, open a clean generated custom whose final survivor databank is Forward/Foward.
2. Export Forward/Foward before using `SQXEdgeCorrelationTagger` as a filter.
3. Close SQX.
4. Build and install the tag CSV:

```powershell
tools\sqx142_own_features_correlation_data_smoke.ps1 -Action build -InputCsv <forward-export.csv> -OutputDir <local-output-dir>
tools\sqx142_own_features_correlation_data_smoke.ps1 -Action install -TagCsvPath <local-output-dir>\correlation_decisions.csv -OutputDir <local-output-dir>
```

5. Reopen SQX.
6. In the Forward task, go to `Full settings` -> `Ranking`.
7. Enable Custom Analysis `SQXEdgeCorrelationTagger`.
8. Keep `Filter by results of custom analysis` disabled.
9. Select `SQX EDGE CORRELATION REVIEW`.
10. Confirm the SQXEdge columns populate.
11. Export a final tagger-confirmation CSV.
12. Run `validate-export` and then `record`.

## Accepted FEATURES4 Evidence

The first validated run was AUDCAD H1 Momentum Capa1:

- fresh Forward rows: 23
- Data Smoke decisions: `portfolio=1`, `similar=22`, `review=0`
- installed tag CSV hash: `3401856dc3dc4fb5d71a5d4c116f3049ba0cd372d3c1dc8559d9271d7d6c2732`
- final tagger export hash: `092AB2E3C97ED81DC8E2BD7FE9793B952D2E61D9B0A9F325A1520A8C78EC99C4`
- final FEATURES4 record: `.local/sqx142_own_features/clean_mining_path_validation/sqx142-own-features4-clean-mining-path-validation-v1_manual_record_20260529_221731.json`
- FEATURES5 validation evidence: `.local/sqx142_own_features/forward_tagger_flow/sqx142-own-features5-forward-tagger-flow-v1_validate_export_20260529_222646.json`
- final FEATURES5 record: `.local/sqx142_own_features/forward_tagger_flow/sqx142-own-features5-forward-tagger-flow-v1_manual_record_20260529_222703.json`

## Boundaries

Blocked:

- SQX runtime launch from scripts.
- `checkResources` as a shortcut for this flow.
- enabling `Filter by results of custom analysis` for the lab visualization flow.
- deleting or filtering databank rows inside SQX as part of tagger confirmation.
- jar, engine, internal plugin, license or activation changes.
- `data.db` writes.
- `user/projects` writes.
- databank deletion.
- `run_project`.
- Migration Tool.
- forced pass or profitability claims.

Allowed:

- manual operator SQX actions.
- Data Smoke `build`.
- Data Smoke `install` only while SQX is closed and only for `user/extend/SQXEdge/Correlation/correlation_decisions.csv`.
- read-only validation of the final tagger export.

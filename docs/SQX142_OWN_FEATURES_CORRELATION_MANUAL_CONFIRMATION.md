# SQX142-OWN-FEATURES3 Correlation Pack Manual Confirmation

Status: `superseded_by_features4_features5_clean_path`

Version: `sqx142-own-features3-correlation-manual-confirmation-v1`

## Purpose

This block prepared the original lab-only SQX142 confirmation flow. FEATURES1 installed the supported snippets/view package; FEATURES2 installed a real `correlation_decisions.csv`; FEATURES3 told the operator exactly what to open, what custom item to select, what columns must populate, and how to record the result without touching SQX internals.

FEATURES3 is no longer an open blocker. The original lab carrier was later shown by FEATURES3B to be unsuitable because the copied legacy databanks contained retired strategy dependencies. FEATURES4 and FEATURES5 then validated the same Correlation Pack on a fresh AUDCAD H1 Momentum path: the `SQX EDGE CORRELATION REVIEW` columns populated through `SQXEdgeCorrelationTagger`, filtering stayed disabled, the final tagger export was validated, and the repeatable Forward tagger flow was recorded.

## Historical Preflight

Latest local status before the clean-path supersession:

- SQX process count: `0`.
- Package files installed: `true`.
- View installed: `SQX EDGE CORRELATION REVIEW`.
- Custom Analysis display name: `SQX Edge Correlation Tagger`.
- Custom Analysis code id: `SQXEdgeCorrelationTagger`.
- Tag CSV: `user/extend/SQXEdge/Correlation/correlation_decisions.csv`.
- Tag CSV schema: `strategyRef,candidateId,decision,reason,score,maxObservedCorrelation,correlationStatus,nearestWinnerId,portfolioRank,generatedAt,version`.
- Tag CSV rows: `86`.
- Dedicated lab project: `SQX_EDGE_CORR_LAB_Mining15_USDJPY_H4_20260527`.

Run the preflight again with:

```powershell
tools\sqx142_own_features_correlation_manual_confirmation.ps1 -Action status
tools\sqx142_own_features_correlation_manual_confirmation.ps1 -Action checklist
```

## Historical Lab Operator Steps

These steps remain documented only for lab traceability. They are not the current blocker and should not be used to reopen the old legacy carrier as production evidence.

1. Open SQX142 lab manually.
2. If snippets compilation appears, compile all snippets and stop only if SQX reports a red error for `SQXEdgeCorrelationTagger` or `SQXEdgeCorr*`.
3. Open dedicated project `SQX_EDGE_CORR_LAB_Mining15_USDJPY_H4_20260527`.
4. Use databank `Monkey Test` for the first check.
5. Select databank view `SQX EDGE CORRELATION REVIEW`.
6. If you want fresh tagged output, enable/run only task `SQX EDGE CORR TAG`; it uses input `Monkey Test`, output `SQX EDGE CORR TAGGED` and Custom Analysis `SQXEdgeCorrelationTagger`.
7. Inspect `Monkey Test` or output databank `SQX EDGE CORR TAGGED`:
   - `SQXEdgeCorrDecision`
   - `SQXEdgeCorrRank`
   - `SQXEdgeCorrScore`
   - `SQXEdgeMaxCorr`
   - `SQXEdgeCorrStatus`
   - `SQXEdgeNearestWinner`

## Expected Signals

Pass:

- The view is visible.
- The tagger is selectable as `SQX Edge Correlation Tagger` or `SQXEdgeCorrelationTagger`.
- The six SQXEdge columns are visible.
- At least one matching strategy row shows non-default correlation values.
- No strategy is rejected by the tagger.

Review:

- Columns show only `-1`, `0`, empty, or `missing` values. This usually means the tag CSV does not match the current databank strategy names, not that the pack failed.

Blocked:

- Snippets fail compilation.
- The view is missing.
- The tagger is not listed.
- SQX rejects strategies because of the tagger.

## Recording

If this historical lab check is repeated for comparison, record the result locally:

```powershell
tools\sqx142_own_features_correlation_manual_confirmation.ps1 -Action record -Outcome pass -ViewVisible -SnippetsCompiled -TaggerSelectable -ColumnsPopulated -NoStrategyRejection -OperatorNote "Confirmed in SQX142 lab."
```

Use `-Outcome blocked` or `-Outcome fail` if any required signal is missing. Evidence is written only under ignored `.local/sqx142_own_features/manual_confirmation/`.

The dedicated lab project is documented in `docs/SQX142_OWN_FEATURES_CORRELATION_LAB_PROJECT_SCAFFOLD.md`. The accepted clean-path confirmation is documented in `docs/SQX142_OWN_FEATURES_CLEAN_MINING_PATH_VALIDATION.md` and made repeatable in `docs/SQX142_OWN_FEATURES_FORWARD_TAGGER_FLOW.md`.

## Boundaries

This block does not launch SQX, does not write SQX files, does not write `data.db`, does not touch `user/projects`, does not delete databanks, does not run projects, does not use Migration Tool, and does not patch jars, engine files, internal plugins, license or activation surfaces.

The tagger remains lab-only. Edge Factory remains the canonical correlation decision engine. FEATURES4/5 close the operational confirmation for the clean path; the old FEATURES3 lab carrier stays historical/superseded evidence, not pending work.

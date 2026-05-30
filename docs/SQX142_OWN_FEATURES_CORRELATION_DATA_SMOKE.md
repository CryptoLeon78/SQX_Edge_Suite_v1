# SQX142-OWN-FEATURES2 Correlation Pack Data Smoke

Status: built; CSV install is gated by SQX closed.

Version: `sqx142-own-features2-correlation-data-smoke-v1`

## Purpose

This block verifies the data path behind the visible `SQX EDGE CORRELATION REVIEW` view. The goal is to generate a real `correlation_decisions.csv` from an operator CSV/JSON export, install only that CSV into the supported SQXEdge folder, and confirm that the existing tagger can populate the visible columns.

## Tools

- Builder: `backend/sqx-edge-tool/tools/sqx142_correlation_data_smoke.py`
- Operator wrapper: `tools/sqx142_own_features_correlation_data_smoke.ps1`
- Actions: `status`, `build`, `install`, `rollback`

`build` reads source strategy rows and writes:

- `.local/sqx142_own_features/data_smoke/latest/correlation_decisions.csv`
- `.local/sqx142_own_features/data_smoke/latest/correlation_data_smoke_public.json`

`install` requires SQX closed and copies only:

- `user/extend/SQXEdge/Correlation/correlation_decisions.csv`

## Boundaries

Allowed: replace the lab tag CSV with backup/hash/rollback.

Blocked: jars, internal plugins, license/activation, `data.db`, `user/projects`, databank deletion, `run_project`, Migration Tool, and SQX runtime launch.

## Manual Smoke

1. Export or prepare source rows with strategy names matching the SQX databank strategy names.
2. Run `build` or `install` with `-InputCsv`.
3. Open SQX142 lab.
4. Compile snippets if prompted.
5. Activate/run `SQX Edge Correlation Tagger` only in a cloned/lab workflow.
6. Open `SQX EDGE CORRELATION REVIEW`.
7. Confirm visible values in `SQXEdgeCorrDecision`, `SQXEdgeCorrRank`, `SQXEdgeCorrScore`, `SQXEdgeMaxCorr`, `SQXEdgeCorrStatus`, and `SQXEdgeNearestWinner`.

The sample CSV proves the pipeline but will only populate SQX rows whose strategy names match the sample names.

The governed manual UI confirmation continues in `docs/SQX142_OWN_FEATURES_CORRELATION_MANUAL_CONFIRMATION.md` with helper `tools\sqx142_own_features_correlation_manual_confirmation.ps1`.

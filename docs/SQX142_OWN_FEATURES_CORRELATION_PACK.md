# SQX142-OWN-FEATURES1 Correlation Pack Hibrido

Status: built, lab install gated while SQX142 is open.

Version: `sqx142-own-features1-correlation-pack-v1`

## Scope

This block implements a real SQX Edge-owned correlation/diversity pack without patching SQX jars or internal plugins. Edge Factory remains the canonical decision engine and SQX142 can visualize the result through supported lab-only surfaces:

- `user/extend/Snippets/SQ/CustomAnalysis`
- `user/extend/Snippets/SQ/Columns/Databanks`
- `user/settings/views/databanks`
- `user/extend/SQXEdge/Correlation`

## Implemented

- Backend `sqx142-correlation-filter-external-v1` now emits `strategyRef`, `portfolioRank`, and optional `sqxTagCsv`.
- `strategyRef` is `strategy_ + sha256(strategyName)[0:16]`; raw strategy names are not returned in the tag CSV.
- Edge Factory requests `includeSqxTagCsv`, shows `portfolio/similar/review`, and exposes `Descargar SQX Tag CSV`.
- Package lives at `integrations/sqx142/own_features/correlation_pack/`.
- Installer lives at `tools/sqx142_own_features_correlation_pack.ps1` with `status/install/rollback`.

## SQX Lab Package

The package contains:

- `SQXEdgeCorrelationTagger.java`
- `SQXEdgeCorrDecision.java`
- `SQXEdgeCorrRank.java`
- `SQXEdgeCorrScore.java`
- `SQXEdgeMaxCorr.java`
- `SQXEdgeCorrStatus.java`
- `SQXEdgeNearestWinner.java`
- `SQX EDGE CORRELATION REVIEW.vw`
- `correlation_decisions.csv` sample

The tagger reads `user/extend/SQXEdge/Correlation/correlation_decisions.csv` by default, or the optional `SQX_EDGE_CORRELATION_TAG_CSV` environment variable. It writes `specialValues` only and always returns `true`.

## Safety Boundary

Blocked: jars, internal plugins, license or activation surfaces, `data.db`, `user/projects`, databank deletion, `run_project`, and Migration Tool.

The installer requires SQX to be closed, creates backups and hashes, and can roll back by restoring the previous files or removing files that did not exist before install.

Do not enable `CustomAnalysis=true` in Capa1/Capa2 templates. Use only in a cloned/lab SQX142 workspace for manual visual smoke.

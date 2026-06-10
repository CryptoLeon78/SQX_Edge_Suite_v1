# SQX142 Own Features Correlation Pack

Version: `sqx142-own-features1-correlation-pack-v1`

This package adds a lab-only visual bridge between the SQX Edge correlation filter and SQX142 supported snippet/view surfaces. Edge Factory remains the canonical decision engine. SQX142 only receives tags through `specialValues` and a databank view.

## What It Installs

- `user/extend/Snippets/SQ/CustomAnalysis/SQXEdgeCorrelationTagger.java`
- `user/extend/Snippets/SQ/Columns/Databanks/SQXEdgeCorrDecision.java`
- `user/extend/Snippets/SQ/Columns/Databanks/SQXEdgeCorrRank.java`
- `user/extend/Snippets/SQ/Columns/Databanks/SQXEdgeCorrScore.java`
- `user/extend/Snippets/SQ/Columns/Databanks/SQXEdgeMaxCorr.java`
- `user/extend/Snippets/SQ/Columns/Databanks/SQXEdgeCorrStatus.java`
- `user/extend/Snippets/SQ/Columns/Databanks/SQXEdgeNearestWinner.java`
- `user/settings/views/databanks/SQX EDGE CORRELATION REVIEW.vw`
- `user/extend/SQXEdge/Correlation/correlation_decisions.sample.csv`
- `user/extend/SQXEdge/Correlation/correlation_decisions.csv` only when missing

## Runtime Behavior

`SQXEdgeCorrelationTagger` reads `user/extend/SQXEdge/Correlation/correlation_decisions.csv` by default. The optional environment variable `SQX_EDGE_CORRELATION_TAG_CSV` can point to another CSV for a lab run.

The tagger computes `strategyRef` as `strategy_ + sha256(ResultsGroup.getName())[0:16]`, looks up that ref in the CSV, writes SQX Edge values into `specialValues`, and always returns `true`. It never rejects strategies, deletes databanks, or changes project templates.

## Boundary

Blocked by design: jars, internal plugins, license or activation surfaces, `data.db`, `user/projects`, databank deletion, `run_project`, and Migration Tool.

Do not enable `CustomAnalysis=true` in Capa1/Capa2 templates. Use only in a cloned/lab SQX142 workspace after the installer reports SQX is closed.

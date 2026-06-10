# SQX142-144-BACKPORT6 Monte Carlo Candidate Benchmarks

Estado: `completed_build_no_sqx_runtime`.

Este bloque adapta las ideas de Build 144 `MACHRBlockRandomization`, `SimulateParameterJitter` y `RandomlyDegradeExecution` como benchmarks externos reproducibles de SQX Edge para candidatos de Portfolio Lab/CSV. No son metodos nativos de SQX 142, no reemplazan MC/MC2 canonicos y no copian internals propietarios de SQX 144.

## Implementacion

- Core: `backend/sqx-edge-tool/core/sqx142_monte_carlo_candidate_benchmarks.py`.
- API local-only: `POST /api/sqx142/monte-carlo/benchmarks`.
- Tests: `backend/sqx-edge-tool/test_sqx142_monte_carlo_candidate_benchmarks.py`.
- Version de respuesta: `sqx142-monte-carlo-candidate-benchmarks-v1`.
- Modo: `external_readonly`.
- Fuente esperada: `portfolio_lab_phase29`.

## Entradas

El endpoint acepta `rows`, `csv` o `portfolioLab`. Cada candidato puede traer:

- `returnSeries`: retornos comparables separados por `|`, `;`, espacios o lista numerica.
- `equitySeries`: curva de equity/balance desde la que se derivan retornos.
- Trazas publicas opcionales: `asset`, `timeframe`, `BlockSetting`.

El minimo por defecto es `minComparablePoints=12`; si falta serie o es corta, el candidato queda `benchmark_review` con `not_enough_series`.

## Metodos Externos

- `MACHRBlockRandomization`: reordena bloques de retornos de tamano `blockSize=4` usando seed determinista.
- `SimulateParameterJitter`: aplica ruido multiplicativo reproducible con `parameterJitterPct=0.15`.
- `RandomlyDegradeExecution`: resta degradacion de ejecucion reproducible con `executionDegradeBps=2.0`.

Todos los metodos usan `simulations=64` y `seed=sqx142-mc-benchmark-v1` por defecto. No usan randomness global, no arrancan SQX y no leen/escriben `data.db` ni `user/projects`.

## Salidas

Cada item devuelve:

- `candidateId` y `strategyRef` opacos.
- `decision`: `benchmark_pass`, `benchmark_review` o `benchmark_fail`.
- `base.points`, `base.cumulativeReturnPct` y `base.maxDrawdownPct`.
- `benchmarks[]` con `medianReturnPct`, `p05ReturnPct`, `medianDrawdownPct`, `maxDrawdownPct`, `survivalRate` y `status`.
- `trace` saneado con `asset`, `timeframe` y `BlockSetting`.

El resumen devuelve `inputRows`, `evaluatedRows`, `benchmarkPass`, `benchmarkReview`, `benchmarkFail`, `sampleBlocked` y `redactedFields`. Hay `CSV export` opcional con `includeCsvExport=true`.

## Decisiones

- `benchmark_pass`: todos los metodos externos pasan.
- `benchmark_review`: faltan series comparables, aparece aviso, fila sample/demo/example o marcador forced/manual/synthetic/fabricated pass.
- `benchmark_fail`: al menos un metodo incumple `minSurvivalRate=0.70` o `maxMedianDrawdownPct=35.0`.

## Privacidad Y Gate

El endpoint exige operador local y devuelve `403 local_operator_required` a remoto/tester. La respuesta mantiene:

- `privacy.local_paths_returned=false`.
- `privacy.raw_strategy_names_returned=false`.
- `privacy.private_fields_returned=false`.
- `privacy.tokens_returned=false`.

Tambien redacta rutas locales, emails, tokens, secretos y claves privadas antes de resumir.

## Bloqueado

- Copiar metodos/clases/plugins internos de SQX 144.
- Llamar MC runtime de SQX o API interna de StrategyQuant.
- Escribir `data.db` o `user/projects`.
- Relanzar retests, optimizaciones o proyectos.
- Activar `CustomAnalysis=true` o `FitPortfolio=true`.
- Convertir muestras, demos o forced/manual/synthetic/fabricated pass en candidatos reales.
- Prometer profit guarantee, risk zero o sustitucion de MC/MC2 canonicos.

## Verificacion

- `test_sqx142_monte_carlo_candidate_benchmarks.py` -> `6 passed`.
- Evidencia local ignorada: `.local/sqx142_144_backport/sqx142_144_backport6_monte_carlo_candidate_benchmarks_20260526_183500.json`.

Siguiente bloque recomendado: `SQX142-144-BACKPORT7 MT5 Data Intake Probe`.

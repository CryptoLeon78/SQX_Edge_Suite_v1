# J2 Champion vs Challenger Core

Date: 2026-05-08

Status: implemented as a pure frontend core with contracts. No dashboard UI was added.

## Objective

J2 implements the first native Champion vs Challenger building block:

- CSV parsing.
- Column alias resolution.
- Strategy metric normalization.
- Formal Champion vs Challenger comparison.
- Deterministic candidate ranking.

The implementation intentionally avoids DOM access, backend endpoints and visible UI. It prepares the foundation for J3/J4 without changing dashboard behavior.

## Implemented Files

- `app/js/modules/champion-challenger-core.js`
- `tests/js/contracts/champion_challenger_core_contracts.mjs`
- `tests/js/module_contracts.mjs`

## Public Module Contract

The module registers as:

- `SQX.championChallengerCore`
- `SQX.modules['champion-challenger-core']`

Exposed functions:

- `detectDelimiter(text)`
- `parseCsv(text, options)`
- `normalizeHeader(value)`
- `resolveColumnAliases(headers, options)`
- `parseNumber(value)`
- `parseStrategyCsv(text, options)`
- `compareCandidate(champion, challenger, options)`
- `rankCandidates(champion, challengers, options)`
- `escapeHtml(value)`

## Accepted CSV Behavior

Implemented parser guarantees:

- Comma and semicolon delimiter detection.
- Quoted values.
- Delimiters inside quoted values.
- Escaped quotes.
- Empty-file rejection.
- Header validation.
- Configurable maximum size and maximum rows.
- Original row number preservation for traceability.

## Alias Contract

Minimum J1 aliases are implemented for:

- `strategy_name`
- `symbol`
- `net_profit`
- `profit_factor`
- `return_drawdown`
- `drawdown_pct`
- `trades`
- `r_expectancy`
- `stagnation`
- `entry_indicators`
- `filters_result`

Duplicate aliases are warnings, not silent overwrites.

## Numeric Normalization

The core supports common StrategyQuant/operator formats:

- Decimal dot: `1.42`
- Decimal comma: `1,42`
- US thousands: `1,234.56`
- EU thousands: `1.234,56`
- Percent suffix: `12.5%`
- Currency symbols stripped before numeric parsing.

Blank or invalid numeric values are normalized to `null` and produce warnings.

## Formal Comparison

Default hard checks:

| Check | Rule |
| --- | --- |
| Profit factor | `challenger.profit_factor >= champion.profit_factor * 1.05` |
| Return/drawdown | `challenger.return_drawdown >= champion.return_drawdown * 0.95` |
| Trades | `challenger.trades >= champion.trades * 0.70` |

Optional advisory checks:

- Drawdown percent, disabled by default.
- Forward/OOS flag, enabled only when requested.

Result objects expose:

- `formal_pass_count`
- `formal_fail_count`
- `advisory_pass_count`
- `advisory_fail_count`
- `failure_reasons`
- `warnings`
- `normalized_metrics`
- `source_trace`

## Security Boundary

Imported CSV values are treated as untrusted.

Current protections:

- Imported strategy names are escaped through `escapeHtml`.
- Raw CSV values are preserved for traceability but not rendered by this phase.
- Imported names are not used as DOM IDs.
- No remote calls.
- No automatic persistence.
- No portable packaging of imported files.

## Test Coverage

Contracts cover:

- Module registration.
- Header normalization.
- Delimiter detection.
- Alias resolution.
- Unknown and duplicate column handling.
- Numeric parser formats.
- Quoted semicolon values.
- XSS-like strategy names rendered as text.
- Missing required columns.
- Champion row-count validation.
- Formal ranking and failure reasons.

## Deferred To J3/J4

- OOS block parser.
- Stability scoring.
- Dashboard UI.
- E2E screenshot verification.
- Regime/EGT adapter.
- Export and Strategy Builder handoff.

# CFX-BASE142 - Base Template Compatibility

## Summary

CFX-BASE142 repairs the repository base `.cfx` templates so they can be opened
and edited in the authorized StrategyQuant X build 142 host before the operator
adjusts default parameters.

Affected templates:

- `backend/sqx-edge-tool/templates/Capa1_Long.cfx`
- `backend/sqx-edge-tool/templates/Capa2_Base.cfx`

## Problem Found

The base templates still contained old resource shapes:

- `<Resources><Symbols>` entries whose `InstrumentInfo broker` was `-1` while
  the symbol referenced broker `4`.
- Capa 2 automatic retests with placeholder symbols such as
  `[[Dow Jones Industrial Average]]`.
- Empty `<Brokers />` sections in tasks that still referenced broker-bound
  charts.
- Stale SQX session resources and `MarketOpenSession` values such as
  `Futures_Commodities1`, even while the task setup showed `No Session`.
- Backtest precision stored as M1 (`testPrecision="1"`) while the SQX 142
  Data Manager resolves the same Darwinex symbols as TICK.
- Resource metadata copied too literally from `data.db` (`rows`, full data
  range and stale decimal precision), which made SQX 142 show "Differences"
  for symbols that already existed locally.
- Stale absolute `StrategyType` paths from the machine where the original
  templates were created.

This matches the SQX 142 error family where the project cannot resolve
resources and StrategyQuant reaches a null broker object, including messages
around `BrokerDto.getName()`.

## Fix Applied

- Rebased both templates to the SQX 142 `AUDCAD_darwinex` H1 Forex resource
  from the configured `data.db`. This is intentionally a neutral seed so the
  base templates open cleanly in SQX 142 without triggering commodity-session
  resolution while the operator edits default parameters.
- Rebuilt each task's `<Resources><Symbols>` with one resolvable broker-bound
  symbol.
- Rebuilt missing `<Resources><Brokers><Broker id="4" ... /></Brokers>` blocks.
- Forced the session contract to `No Session` consistently by clearing
  `<Resources><Sessions>` and stale `BuildTradingOptions/MarketOpenSession`
  values.
- Forced `testPrecision="2"` so SQX 142 reads the generated/base projects as
  tick-precision projects.
- Rebuilt symbol resources in the same shape as SQX 142 native projects:
  task-level date range on `<Symbol>`, `InstrumentInfo` date/rows as `0` and
  decimals derived from `tickSize`/`tickStep`.
- Bounded `<Symbol dateFrom/dateTo>` to available SQX `DATA` rows when a task
  asks for a methodology period older than the local data. This prevents SQX
  142 from raising "Missing N days" for cases such as AUDCAD OOS 2010-2016
  when Data Manager only contains AUDCAD from 2017 onward.
- Normalized every task resource to `precision="TICK"` and `timezone="EETUS"`.
  SQX showed "Symbol differences" when even one internal retest resource kept
  stale template values such as `M1`, `D1` or `Etc/UCT`.
- Pruned unused broker entries and serialized empty `<Sessions />` nodes without
  inherited whitespace so SQX 142 does not inspect stale broker/session debris
  from the original seed project.
- Validated against a native SQX 142 AUDCAD project that `source="4"`,
  `broker="4"` and `InstrumentInfo dataType="3"` are compatible Darwinex
  resource values. The `DATA.DATATYPE=1` row in `data.db` represents the loaded
  tick data series and must not be blindly copied over `InstrumentInfo`.
- Removed stale absolute paths from task-level `StrategyType` nodes.
- Labeled the templates as:
  - `Capa1_Long_SQX142_Base`
  - `Capa2_Base_SQX142_Base`

Project Generator still repatches symbol, timeframe, direction, costs,
BlockSettings, dates and embedded Capa 2 strategy metadata for each generated
custom. The SQX 142 base resource is only a safe default that allows the
template files themselves to load; generated customs must always use the asset
and timeframe selected by the user in Plan Mining or Custom manual.

## Guardrail

`backend/sqx-edge-tool/test_cfx_template_compatibility.py` now validates that
the base templates:

- have every chart symbol represented in `<Resources><Symbols>`;
- include a broker entry for every symbol and `InstrumentInfo` broker;
- do not keep stale resource sessions or non-`No Session`
  `MarketOpenSession` values;
- use tick backtest precision (`testPrecision="2"`);
- do not contain placeholder symbols;
- do not keep absolute `StrategyType` paths;
- remain clearly labeled as SQX 142 base templates.

## SQX UI Probe

The 2026-05-17 probe
`CODEx_TEST_AUDCAD_H4_LS_BS_Volatilidad_SQX142_Capa1.cfx` loaded successfully
in the operator's SQX 142 UI after resource dates were bounded to local `DATA`
availability.

The failing pre-fix symptom was `Missing 2831 days` on `AUDCAD_darwinex`
because a resource requested `2010.01.01-2016.12.31` while local SQX 142 had
AUDCAD data only from `2017.10.02`. The task's methodological dates may still
target the old OOS period, but the resource resolver must see a symbol date
window that exists in Data Manager.

## Operator Flow

1. Open the repaired base templates in SQX 142.
2. Adjust the desired default parameters manually.
3. Export or save the updated `.cfx` files.
4. Place the updated files in `material de diagnostico/` for review.
5. Codex will compare the updated defaults and update Workflow copy/tests to
   match the new methodology.

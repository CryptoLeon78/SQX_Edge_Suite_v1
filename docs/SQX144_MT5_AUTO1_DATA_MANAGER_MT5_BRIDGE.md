# SQX144-MT5-AUTO1 - Data Manager MT5 Bridge

Marker: `sqx144-mt5-auto1-data-manager-bridge-v1`
Status: `real_mt5_response_validated_usdjpy_p90`
Host: `sqx144_full`

## Purpose

`SQX144-MT5-AUTO1` opens the automation track that follows `sqx144-mt5-instrument-parity-gate-v1`.

The previous MT5 parity gate consumed one existing `SQXInfoScript` XML export and then used an offline, SQX-closed, approval-gated DB apply. That proved the SQX `INSTRUMENTS` fields can be corrected safely, but it did not solve the operator workflow: it did not launch MT5, did not ask MT5 for the selected symbol, did not compute historical spread percentiles and did not add a Data Manager button.

AUTO1 creates our own bridge source, `SQXInfoBridge.mq5`, and the SQX Edge consumer contract around it.

## Scope

Implemented in this phase:

- `integrations/sqx144/mt5_bridge/SQXInfoBridge.mq5`
- `backend/sqx-edge-tool/core/sqx144_mt5_bridge.py`
- `tools/sqx144_mt5_auto1_data_manager_bridge.ps1`
- `backend/sqx-edge-tool/test_sqx144_mt5_auto1_data_manager_bridge.py`
- `tests/js/contracts/sqx144_mt5_auto1_data_manager_bridge_contracts.mjs`

The bridge is designed as an MT5 Expert Advisor with `OnTimer()`. It reads a request file, calculates symbol properties plus historical spread percentiles, writes JSON responses, and stops there.

## Request And Response

Request file:

- `SQXInfoBridge.request.ini`
- Required symbol field: `symbol`
- Optional fields: `requestId`, `spreadTimeframe`, `fromYear`, `toYear`, `maxBars`

Response files:

- `SQXInfoBridge.latest.json`
- `SQXInfoBridge.response.<requestId>.json`

Response contract:

- `properties`: digits, point, pip size, SQX tick size, SQX tick step, tick value, contract size, current bid/ask, point value and current spread.
- `spreadStats`: global spread statistics over available MT5 bars: `min`, `max`, `mean`, `p50`, `p75`, `p90`, `p95`, `p99`.
- `yearlySpreadStats`: the same spread statistics per year, using only years with actual copied bars.
- Safety flags: `writesSqxHost=false`, `writesDataDb=false`, `runsSqxTasks=false`, `placesOrders=false`.

## Spread Policy

The XML pilot used the value exposed by the old EA, which was a single default spread value. AUTO1 changes that.

`SQXInfoBridge.mq5` calculates multiple spread statistics from MT5 history. SQX Edge consumes all percentiles and proposes one `DEFAULTSPREAD` according to a named policy.

Default policy: `p90`.

Contract marker: `defaultSpreadPolicy=p90`.

Rationale:

- `p50` can under-price normal trading costs.
- `p75` may be useful for more permissive diagnostics.
- `p90` is the conservative default for generated SQX work because it avoids anchoring to the median.
- `p95` and `p99` remain available for stress or high-cost variants.
- `mean` remains available for comparison, not as the preferred default.

The selected spread policy is explicit in validation output as `spreadPolicy`. No hidden spread selection is allowed.

## Real USDJPY Response

AUTO1 produced and validated the first real MT5 bridge response.

Status marker: `real_mt5_response_validated_usdjpy_p90`

- Evidence markers: `mt5Symbol=USDJPY`, `spreadSamples=768790`
- Request id: `sqx_auto1_usdjpy_20260608_194938`
- Requested SQX symbol: `USDJPY_Darwinex`
- Resolved MT5 symbol: `USDJPY`
- Response file: `SQXInfoBridge.latest.json`
- Per-request file: `SQXInfoBridge.response.sqx_auto1_usdjpy_20260608_194938.json`
- Spread timeframe: `PERIOD_M1`
- Spread samples: `768790`
- Year count: `3`
- Years: `2024`, `2025`, `2026`
- Global spread percentiles: `p50=0.4`, `p75=0.6`, `p90=0.7`, `p95=1.2`, `p99=6.5`
- Proposed `DEFAULTSPREAD=0.7` with `spreadPolicy=p90`
- Proposed `POINTVALUE=624.30546`
- Proposed `TICKSIZE=0.01`
- Proposed `TICKSTEP=0.001`
- Validation result: `bridge_response_validated`
- Blockers: none
- Warnings: none

The bridge maps `USDJPY_Darwinex` to MT5 `USDJPY` while keeping the requested SQX symbol in the response. This is required because the existing MT5 chart/script context uses the broker symbol, while SQX profiles carry the broker suffix.

## Automation Path

Target workflow for the future Data Manager button:

1. Operator selects an instrument in SQX Data Manager.
2. SQX Data Manager button calls SQX Edge with the selected symbol.
3. SQX Edge writes `SQXInfoBridge.request.ini`.
4. The running MT5 bridge receives the request through `OnTimer()`.
5. MT5 calculates symbol properties plus spread percentiles over available history and writes `SQXInfoBridge.latest.json`.
6. SQX Edge validates the response and produces a diff/plan for the matching SQX instrument.
7. A separate apply gate handles SQX mutation only when allowed.

AUTO1 implements steps 3 to 6 as the bridge foundation. The actual SQX Data Manager button is not installed in this phase:

- `dataManagerButtonPlanned=true`
- `dataManagerButtonInstalled=false`

## Boundaries

No SQX DB mutation in SQX144-MT5-AUTO1 unless a separate DB mutation gate is opened and approved.

Current AUTO1 safety markers:

- `writesDataDb=false`
- `writesUserProjects=false`
- `mutatesDatabanks=false`
- `runsSqxTasks=false`
- `usesMigrationTool=false`
- `launchesMt5=false`
- `runsMt5Ea=false`
- `placesOrders=false`

AUTO1 does not:

- update `data.db`;
- update `INSTRUMENTS`;
- mutate `SOURCE`, `BROKER_ID`, history coverage, `DATA`, `ROWS`, `DATEFROM` or `DATETO`;
- write `user/projects`;
- mutate databanks;
- run SQX projects or tasks;
- use Migration Tool;
- install a Data Manager button;
- launch MT5;
- place trades.

`tools/sqx144_mt5_auto1_data_manager_bridge.ps1 write-request -Apply` may write a request file into the configured MT5 Files directory. `install-source -Apply` may copy `SQXInfoBridge.mq5` into the configured MT5 Experts directory. Those actions write only MT5-side bridge/request files and still do not write SQX.

`-Apply` is path-allowlisted: it may target the configured Darwinex BEPB MT5 directory or ignored `.local/mt5_bridge_auto1` test/evidence paths only. `install-source -Apply` will not overwrite an existing `SQXInfoBridge.mq5` unless `-Overwrite` is also supplied.

## Commands

Dry-run status:

```powershell
tools\sqx144_mt5_auto1_data_manager_bridge.ps1 status
```

Create a visible request template:

```powershell
tools\sqx144_mt5_auto1_data_manager_bridge.ps1 request-template -Symbol USDJPY_Darwinex -SpreadTimeframe M1
```

Write a request to MT5 Files only after choosing to do so:

```powershell
tools\sqx144_mt5_auto1_data_manager_bridge.ps1 write-request -Symbol USDJPY_Darwinex -SpreadTimeframe M1 -Apply
```

Install the MT5 source only when ready to place the bridge into MT5 Experts:

```powershell
tools\sqx144_mt5_auto1_data_manager_bridge.ps1 install-source -Apply
```

Validate the latest bridge response and propose SQX fields without applying them:

```powershell
tools\sqx144_mt5_auto1_data_manager_bridge.ps1 validate-response -SpreadPolicy p90
```

## Next Phase

Recommended next phase after AUTO1 verification:

`SQX144-MT5-AUTO2 - Data Manager Button Bridge`

AUTO2 should add a visible Data Manager control only after:

- `SQXInfoBridge.mq5` is installed and compiling cleanly in MT5;
- a real response exists for at least `USDJPY_Darwinex`;
- SQX Edge validates that response;
- the operator accepts the selected spread policy;
- the SQX mutation path remains a separate gate.

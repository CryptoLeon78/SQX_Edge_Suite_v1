# BS-AI14 Capa1 Monitor Decision

Marker: `bs-ai14-capa1-monitor-decision-v1`

Status: `monitor_ready_stop_or_review_candidate_no_capa2`

Latest methodology conclusion: `tick_real_pf_failed_trade_threshold_warning_no_capa2`

## Scope

BS-AI14 monitors the first BS-AI Capa1 run after BS-AI13 and decides whether
to continue monitoring, review survivors, request a controlled Capa1 stop, or
prepare a later Capa2 preflight.

This gate starts read-only. It does not start Capa2 and does not stop Capa1 by
itself.

## Current Observation

The operator reported SQX144 Full open on the BS-AI Capa1 Build task with about
360 strategies in `Results`, 3 strategies through `RETEST 0`, and low pass rate.

Read-only status and process checks on 2026-06-07 showed:

- SQX remote access on `127.0.0.1:8080` reachable.
- Capa1 visible with `tasks=14`, `databanks=15`, `strategies=385`,
  `hasUnresolvedResources=false`.
- Capa2 visible with `tasks=14`, `databanks=15`, `strategies=0`,
  `hasUnresolvedResources=false`.
- Capa1 `project.cfx` hash remains OK.
- `RETEST 0` contains 3 `.sqx` files.
- Capa2 databanks remain empty.
- The latest sanitized SQX log recorded `RETEST 0` finishing and saving 3 files,
  then a later Capa1 Build start; the latest log timestamp is stale versus the
  current clock.
- A 20 second process sample showed zero CPU delta for the main SQX process
  while memory remained high.

Decision: this is not a clean signal to start Capa2. It is a
`stop_or_review_candidate_no_capa2` situation: capture evidence and ask the
operator for explicit stop/review approval if the UI still appears running.

## Operator Stop And Retest Conclusion

On 2026-06-07 the operator stopped the Capa1 Build task and ran the Capa1
retests. A read-only post-run audit records:

- SQX remote still sees Capa1 with `tasks=14`, `databanks=15`,
  `strategies=425`, `hasUnresolvedResources=false`.
- Capa2 remains unstarted with `strategies=0`.
- Local databank files are `RETEST 0` = 37 `.sqx`, `retest 1` = 5 `.sqx`,
  and `TICK` = 0 `.sqx`.
- The sanitized project log records `RETEST 0` testing 383 strategies and
  passing 34 new strategies, leaving 37 in `RETEST 0`.
- The sanitized project log records `RETEST 1` testing 37 strategies and
  passing 5 into `retest 1`.
- The sanitized project log records `TICK REAL` testing the 5 `retest 1`
  survivors for 7 min 45 s and passing 0.
- The failed-detail cause reported for `TICK REAL` is
  `Profit factor[Main data] >= 1.30` with Count 5, 100% of the tested
  survivors.
- SQX appears to stop/log rejection at the first failed active filter. Therefore
  the log does not prove the later TICK REAL filters would have passed; it only
  proves Profit Factor was the first observed blocker under the current filter
  order.
- No `TICK` survivor exists; downstream MC/MC2/Sequential/Monkey/Synthetic/SPP/
  WFM/Forward tasks immediately had zero input.

Conclusion: this branch is first blocked by Profit Factor on real-tick Darwinex
precision data under the current TICK REAL filter order. The log cannot exclude
additional failures behind that first blocker, including `# of trades >= 200`.
The correct phase decision is
`tick_real_pf_failed_trade_threshold_warning_no_capa2`: do not start Capa2 and
do not relax TICK filters to rescue this candidate.

However, the operator clarified an important methodology issue in the current
TICK REAL design: the absolute `# of trades >= 200` filter expects the real-tick
precision run to preserve a trade count comparable to the Build / RETEST 0 /
RETEST 1 chain, even though those earlier checks use less precise simulated
tick conditions. That is a valid design warning. A real-tick validation gate can
require enough sample size, but it should allow a governed tolerance for
trade-count drift caused by precision/data execution differences. A strict
absolute threshold that is equal to or higher than the earlier simulated
precision threshold can reject a strategy for normal precision drift rather than
for loss of edge.

Methodology implication: the H1 long-only Capa1 branch with official
`BS_Volatilidad_v6_intraday_v6` produced a thin but real validation chain
through `RETEST 0` and `retest 1`, then lost all survivors at the first logged
TICK REAL blocker. That is enough to block Capa2 for this branch/candidate
combination. Separately, the TICK REAL trade-count rule needs redesign before
the next governed experiment: prefer a tolerance/ratio rule against prior
survivor trade count, or a lower absolute minimum that is explicitly justified
as sample-size protection rather than a no-margin equality expectation.

Next safe action is a diagnostic planning gate only if needed: inspect or export
the 5 `retest 1` survivor metrics without changing pass states, then decide
whether the next experiment should change branch/direction/base hypothesis. Any
filter relaxation would be a new diagnostic experiment and must not be treated
as continuation of this validation result.

## Tooling

- Core: `backend/sqx-edge-tool/core/bsai14_capa1_monitor_gate.py`
- Wrapper: `tools/sqx144_bsai14_capa1_monitor_gate.ps1 status|monitor|decision-template`
- Tests: `backend/sqx-edge-tool/test_bsai14_capa1_monitor_gate.py`

`status` reads SQX remote project state and sanitized local counters without
writing evidence.

`monitor` writes sanitized evidence under ignored `.local/blocksettings_ai/`.

`decision-template` prints the current recommendation plus the exact approval
phrase required before any stop request.

## Stop Approval

BS-AI14 does not stop Capa1 automatically.

If the operator decides to stop the stale/idle visible run, the required phrase
is:

`APRUEBO STOP BS-AI14 CAPA1 SIN CAPA2`

After approval, the existing BS-AI13 `stop-capa1` endpoint can be used as the
bounded stop action, then BS-AI14 must run `monitor` again to record the final
state.

## Boundaries

BS-AI14 blocks:

- Capa2 Start.
- New import.
- `taskmanager/openProject`.
- `loadAsIs`.
- Resource resolution or `Add missing symbols`.
- Direct `data.db` patching.
- Direct script-side `user/projects` patching.
- Databank deletion.
- Migration Tool.
- BSAI promotion.
- Official v6/v7 overwrite.
- 144.2953 promotion.
- Profitability, pass-rate or risk-zero claims.

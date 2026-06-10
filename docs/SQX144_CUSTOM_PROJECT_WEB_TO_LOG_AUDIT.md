# SQX144 Custom Project Web-To-Log Audit

Status: active audit note.
Date: 2026-06-06.
Marker: `sqx144-custom-project-web-to-log-audit-v1`.

## Scope

This note records the first SQX144 Full audit of custom projects generated from
the protected web app and then loaded manually into the licensed SQX144 Full
host.

The inspected custom pair was:

- `Project_USTEC_H1_BS_Momentum_v6_L_Capa1`
- `Project_USTEC_H1_BS_Momentum_v6_L_Capa2`

Raw SQX logs, local paths, license payloads and private workspace evidence stay
local-only and are not copied into the repository.

## Trace

Observed flow:

1. The web app called Project Generator through `/generate-custom`.
2. Remote-session mode wrote the generated `.cfx` files to the active workspace
   outputs area, not to the shared operator output folder.
3. The operator downloaded/opened the `.cfx` pair and loaded it into SQX144
   Full.
4. SQX144 converted the project files to Build 144 project shape and wrote
   project-global logs for the Capa1 Build attempts.

The generated projects had no source-machine path leakage and no stale SQX142 or
SQX143 path tokens in the inspected XML.

## Runtime Findings

The Capa1 project loaded and started Build successfully. SQX prepared
`NASDAQ_darwinex / H1` data and created the data feed; the short operator runs
were stopped manually.

Build results observed in the project-global logs:

- first run: about 15m33s, 4227 generated, 0 accepted, 4227 rejected;
- second run: about 3m37s, 1270 generated, 0 accepted, 1270 rejected.

The rejection pattern was dominated by the initial population Profit Factor
filter and no-trade / too-few-trades filters. This is a natural methodology
outcome for that short USTEC/H1 LONG Momentum probe, not a resource resolver or
license failure.

SQX responsiveness during execution is explained by CPU-heavy Build work plus
the already observed SQX144 UI/databank update pressure. The task itself did not
show crash, out-of-memory or resource-load failure.

## Corrected Event

SQX144 logged a project-resource error while applying default commission during
the custom-project load. The inspected generated Capa2 XML contained one
`Setup` without a `Commissions` node, inherited from the base task shape. Older
generator logic skipped missing `Commissions` nodes instead of creating them.

Correction:

- `core/xml_patcher.py` now creates `Commissions` when missing before applying
  the generated commission method/value.
- Regression coverage asserts direct patcher behavior and generated Capa2
  custom coverage so every `Setup` has `Commissions`.
- The already generated local Capa2 `.cfx` and the already loaded SQX144 Capa2
  `project.cfx` were repaired with an ignored local backup; the only missing
  node was in `AutomaticRetest-Task4.xml`.

Verification:

- targeted `test_cfx_template_compatibility.py` selection passed;
- a temporary USTEC/H1 Momentum Capa2 generation against the SQX144 Full data
  profile produced zero setups missing `Commissions`.
- the repaired local artifacts now report zero setups missing `Commissions`.

## Data Availability Note

The generator preserved the canonical Capa1/Capa2 date contract. During SQX144
load, SQX adjusted some USTEC/Darwinex task date fields to the available local
data range because that host's USTEC/NASDAQ Darwinex history starts later than
the canonical Build start.

This is a traceability warning rather than a crash. Future evidence for index
customs should state whether the loaded host had enough data to cover the
canonical date window or whether SQX bounded the live project on import.

## Disk Posture

The active disk posture is tight: C: was measured below the historical critical
threshold used by the SQX performance roadmap.

Cleanup candidates, pending explicit operator approval:

- remove or move the old SQX144 Full pre-update backup after a fresh off-disk
  archive or after the operator accepts that rollback can use the confirmed
  working SQX144 Full host;
- SQX142 fallback is closed as active fallback by
  `docs/SQX144_RESULTS_CONFIRMATION_CLOSEOUT.md`; deleting SQX142 still needs
  explicit operator approval;
- treat SQX143 as a small, low-value removal candidate only after checking no
  current tool still needs its runtime profile;
- clean ignored local evidence with retention rules before deleting any
  StrategyQuant host.

No deletion was performed during this audit.

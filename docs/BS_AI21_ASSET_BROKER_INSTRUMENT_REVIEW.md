# BS-AI21 Asset Broker Instrument Review

Marker: `bs-ai21-asset-broker-instrument-review-v1`

Status: `asset_broker_instrument_review_completed_new_capa1_allowed_with_controls_no_apply`

Gate label: `BS-AI21 asset/broker/instrument configuration review`

## Scope

BS-AI21 reviews the active `sqx144_full` asset, broker, instrument and data
source configuration before any new BS-AI Capa1 experiment.

Target project:

`BSAI16_AUDCAD_H1_L_TICKR65_F120_Capa1_v001`

This phase is read-only. It writes only local ignored evidence and does not
Start, Stop, import, resolve resources, write `data.db`, write `user/projects`,
mutate databanks, open Capa2 or use Migration Tool. In short: no data.db,
no user/projects and no databank mutation.

## Evidence

Review evidence:

- `bsai21_asset_broker_instrument_review_review_20260610_212614.json`

Catalog readback:

- Catalog quick check: `ok`.
- `BROKER=12`.
- `INSTRUMENTS=989`.
- `DATA=54`.
- Read mode: `sqlite_uri_mode_ro_query_only`.

## Effective AUDCAD Contract

Primary execution side:

- `AUDCAD_darwinex`.
- Broker id `4`, source id `4`.
- Effective instrument: `AUDCAD_darwinex`.
- Effective H1 backing source: `TICK`.
- Rows: `340730947`.
- Spread `1.3`.
- Point value `71753.512334`.
- Tick size `0.0001`.
- Tick step `0.00001`.
- Order size multiplier `1.0`.
- Order size step `0.01`.

Effective lowercase marker: spread `1.3`, point value `71753.512334`.

Reference Dukascopy source:

- `AUDCAD_dukascopy`.
- Source id `2`.
- Effective data row uses broker id `4`.
- Effective instrument: `AUDCAD_darwinex`.
- Effective H1 backing source: `TICK`.
- Rows: `414742952`.

Effective contract comparison:

- `parityOk=true`.
- No effective spread mismatch.
- No effective point-value mismatch.
- No tick size or tick step mismatch.

## Standalone Dukascopy Warning

The standalone `AUDCAD_dukascopy` instrument row exists but is not the effective
instrument used by the reviewed Dukascopy TICK source.

Standalone row observed:

- Spread `1.9`.
- Point value `71848.371197`.
- Tick size `0.0001`.
- Tick step `0.00001`.

This differs from `AUDCAD_darwinex`, but the real reviewed data row for
`AUDCAD_dukascopy` points to `AUDCAD_darwinex`. Therefore the standalone
Dukascopy mismatch is a warning, not a blocker, as long as the next project
continues to use the effective Darwinex instrument mapping.

Warnings recorded:

- `primary_h1_uses_tick_backing_source_no_direct_h1_data_row`.
- `reference_h1_uses_tick_backing_source_no_direct_h1_data_row`.
- `reference_dukascopy_auto3_profile_missing_using_host_convention`.
- `reference_dukascopy_history_source_only_fallback_uses_effective_darwinex_instrument`.
- `standalone_dukascopy_instrument_differs_but_history_uses_darwinex_effective_instrument`.

## Decision

Decision:

`bsai21_review_clean_new_preregistered_capa1_allowed_with_controls`

Meaning:

- BS-AI21 found no effective asset/broker/instrument blocker for the next
  preregistered Capa1 experiment.
- The failed BS-AI16 branch remains failed for Capa2.
- BS-AI21 does not rescue strategies, relax filters or reinterpret pass states.
- The next experiment must explicitly keep the effective instrument contract:
  `AUDCAD_darwinex` for the Darwinex side and Dukascopy TICK source mapped to
  the same effective instrument.
- Do not select standalone `AUDCAD_dukascopy` as an effective project
  instrument unless a later gate fixes or explicitly waives the cost mismatch.

## Tooling

- Core: `backend/sqx-edge-tool/core/bsai21_asset_broker_instrument_review.py`
- Wrapper: `tools/sqx144_bsai21_asset_broker_instrument_review.ps1 status|review|decision-template`
- Tests: `backend/sqx-edge-tool/test_bsai21_asset_broker_instrument_review.py`
- Contract: `tests/js/contracts/bsai21_asset_broker_instrument_review_contracts.mjs`

`review` writes ignored local evidence under the BS-AI asset/broker/instrument
review evidence root. Public payloads must not expose local paths, raw SQL, raw
XML, raw logs, secrets or license material.

## Boundaries

BS-AI21 blocks:

- No Capa2.
- No Start.
- No import.
- Capa2 Start.
- New Start or Stop.
- New import.
- `taskmanager/openProject`.
- `loadAsIs`.
- Resource resolution or Add missing symbols.
- Direct `data.db` patching.
- Direct script-side `user/projects` patching.
- Databank mutation or deletion.
- Migration Tool.
- Filter relaxation for the current lot.
- Forced pass states.
- BSAI promotion.
- Official v6/v7 overwrite.
- SQX144 144.2953 promotion.
- Profitability, pass-rate or risk-zero claims.

## Next Gate

Recommended next gate: `BS-AI22 preregistered Capa1 design`.

BS-AI22 should design a new Capa1 experiment with the cost/data contract
pre-registered up front, including the warning that standalone
`AUDCAD_dukascopy` is not the effective instrument for this route.

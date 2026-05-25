# Phase30 Capa2 Portfolio Master Contract

Status: documented and registered operating contract only. Evidence: `phase30_capa2_portfolio_master_contract_20260525_152846.json`. `phase30_capa2_portfolio_master_inputs_pending` is also registered with evidence `phase30_capa2_portfolio_master_inputs_pending_20260525_154242.json`. `phase30_capa2_portfolio_master_contract` is the Portfolio Master operating contract after the Phase29 governed Lab.

## Purpose

Portfolio Master is the controlled packaging step after the governed Portfolio Lab has produced a shortlist, diversity rationale and sizing intent. Phase30 defines what must be true before a Portfolio Master artifact can be generated; it does not generate or execute that artifact.

## Required Inputs

- Governed Lab output from Phase29 with shortlist status, diversity reasons, rejected/similar candidates and base-risk sizing.
- Operator Forward CSV/equity/account/broker context, including the Forward CSV source, starting equity, account constraints and broker compatibility notes.
- Operator review confirming that selected strategies are natural Forward survivors and were not manually promoted from failed rows.

## Blocked Until Ready

Actual SQX artifact generation remains blocked until governed Lab output and operator Forward CSV/equity/account/broker context are present. Until then, Phase30 may document the package contract, review checklist, sizing controls and evidence expectations only.

## Inputs Pending Gate

`phase30_capa2_portfolio_master_inputs_pending` is a governed wait state, not artifact generation. The gate confirms `processes=[]`, `cfxGuard=true`, no Capa2 `.cfx` mutation, no `FitPortfolio` drift and no SQX runtime activity.

Current input status: `pending_inputs`. Missing inputs are governed Lab output, natural Forward CSV, comparable equity/return series, account context and broker context. The gate must not fabricate winners, fabricate input files, infer lot sizes, run SQX, rerun retests, optimize or generate Portfolio Master artifacts.

## Guardrails

- No SQX execution, smoke, retest rerun, optimization or Portfolio Master artifact generation in this phase.
- No forced pass and no manual promotion from failed strategies.
- No FitPortfolio drift: Phase30 must not enable SQX `FitPortfolio`, portfolio fitting or hidden selection pressure.
- No live/broker guarantee: broker notes are compatibility context, not a promise that live execution or any specific broker account will work.
- No profitability guarantee, drawdown-reduction guarantee or risk-zero claim.

## Allowed Output

- A public-safe operating contract for Portfolio Master.
- A checklist of required operator inputs and acceptance evidence.
- A blocked-artifact statement that names what evidence is missing before generation.

## Next Gate

The next movement may be artifact generation only after the operator supplies governed Phase29 Lab output plus Forward CSV/equity/account/broker context and the docs manifest is updated in the same change.

Current next state: `phase30_capa2_portfolio_master_inputs_pending`.

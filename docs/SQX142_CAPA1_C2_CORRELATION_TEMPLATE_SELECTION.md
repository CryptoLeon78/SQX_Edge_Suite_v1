# SQX142-CAPA1-C2-CORR Template Selection

Status: `implemented_reclassified_from_portfolio`

Version: `sqx142-capa1-c2-corr1-template-selection-v1`

Registered SQX local reader: `sqx142-capa1-c2-corr1-registered-decision-v1`

Local project integrator: `sqx142-capa1-c2-corr2-local-project-integration-v1`

## Decision

The AUDCAD H1 custom that produced the first real CORR1 evidence is a Capa1 custom. Its correlation result is therefore not a portfolio decision. It is a Template C2 selection decision:

- `IS_CORR` selects or rejects Capa1 candidates for Template Maker / C2 template generation.
- `OOS3_CORR` audits stability and can veto or warn, but it does not choose replacement candidates.
- The real mining/databank evidence remains valid and registered; only the downstream semantic node is reclassified.

Canonical decision domain:

```text
capa1_c2_template_selection
```

Canonical decision node:

```text
c2_template_selection_decision
```

Legacy aliases remain supported only for compatibility:

```text
sqx142-portfolio-corr1-registered-decision-v1
sqx142-portfolio-corr2-local-custom-project-integration-v1
POST /api/sqx142/portfolio-corr1/registered-decision
POST /api/sqx142/portfolio-corr2/local-project
```

## Real Evidence Preserved

Project:

```text
SQX_EDGE_API_FRESH_AUDCAD_H1_Momentum_20260528_090029_Capa1
```

Valid Capa1 databank funnel:

- `Results=2000`
- `RETEST 0=459`
- `retest 1=108`
- `TICK=92`
- `MC=59`
- `MC2=59`
- `Sequential=59`
- `Monkey Test=59`
- `Synthetic=59`
- `SPP=42`
- `WFM=39`
- `Forward=23`
- `SQX EDGE CORR1 STABILITY=23`
- `SQX EDGE CORR1 TAGGED=23`

Registered decision:

- input: `SQX EDGE CORR1 TAGGED`
- rows: `23`
- C2 template winners from IS: `1`
- template-similar candidates: `22`
- review: `0`
- status: `pass`

## Implementation

Backend:

```text
POST /api/sqx142/capa1-c2-correlation/stability-audit
POST /api/sqx142/capa1-c2-corr1/registered-decision
POST /api/sqx142/capa1-c2-corr2/local-project
```

State:

```text
edgeFactory.c2TemplateSelection
```

Registry markers:

```text
capa1_c2_corr2_project_patch
capa1_c2_corr1_stability_retest
capa1_c2_corr1_tagger_review
capa1_c2_corr1_registered_selection_decision
capa1_c2_corr1_registered_decision
```

The shared correlation engine is still reused, but the report returns:

- `decisionDomain=capa1_c2_template_selection`
- `selectionSurface=Template Maker / C2 template generation`
- `downstreamSurface=Capa2 custom project generation`
- `decisionLabels.selected=c2_template_winner`
- `decisionLabels.similar=c2_template_similar`
- `decisionLabels.review=c2_template_review`

## Boundaries

Allowed:

- Read SQX local `.sqx` daily equity while SQX is closed.
- Store Capa1 CORR1 decisions in the SQX Edge registry.
- Patch the target Capa1 `project.cfx` only through the guarded integrator with backup/rollback and SQX closed.

Blocked:

- Treating Capa1 CORR1 as Portfolio Master evidence.
- Selecting alternates from OOS3/Forward without a later untouched holdout.
- Launching SQX from the suite, `run_project`, Migration Tool or `checkResources`.
- Writing SQX `data.db`, patching jars/internal plugins/license, deleting databanks or forcing pass.

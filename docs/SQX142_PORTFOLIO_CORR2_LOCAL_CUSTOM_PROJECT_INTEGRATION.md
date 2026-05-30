# SQX142-PORTFOLIO-CORR2 Local Custom Project Integration

Status: `implemented_local_project_patch_ready`

Version: `sqx142-portfolio-corr2-local-custom-project-integration-v1`

## Decision

CORR1 now has a governed SQX142 local project surface. The first applied version created the lane from `Results`, and the operator then corrected the live SQX task to use the final survivor databank `Forward`. The canonical active contract is now:

- `CORR1 STABILITY RETEST`: reads `Forward` and writes `SQX EDGE CORR1 STABILITY`.
- `CORR1 TAG REVIEW`: reads `SQX EDGE CORR1 STABILITY`, runs `SQXEdgeCorrelationTagger` with filtering disabled, and writes `SQX EDGE CORR1 TAGGED`.

Both tasks use `testPrecision=4` real tick and keep `DeleteFailedStrategies=false` so the audit preserves evidence rather than becoming another elimination gate.
Both tasks are created active because the governed SQX workflow expects the operator to run them and populate the CORR1 review views immediately after Forward exists.

## Implementation

Local tool:

```powershell
tools\sqx142_portfolio_corr2_local_project_integration.ps1 -Action status
tools\sqx142_portfolio_corr2_local_project_integration.ps1 -Action plan
tools\sqx142_portfolio_corr2_local_project_integration.ps1 -Action apply
tools\sqx142_portfolio_corr2_local_project_integration.ps1 -Action record
tools\sqx142_portfolio_corr2_local_project_integration.ps1 -Action rollback -BackupId <backup-id>
```

Local API:

```text
POST /api/sqx142/portfolio-corr2/local-project
```

Frontend:

- Edge Factory and Mining Control add `Estado CORR1 local`, `Registrar CORR1`, `Preflight CORR1`, `Parchear custom SQX` and `Rollback CORR1`.
- The registered funnel now recognizes `SQX EDGE CORR1 STABILITY` and `SQX EDGE CORR1 TAGGED`.
- After `apply`, the UI refreshes the SQX142 mining registry so the new nodes appear alongside the real databank counts.

Registry:

- The integrator records CORR2 steps into `.local/sqx142_mining_registry/sqx142_mining_registry.sqlite`.
- `record` captures manual SQX execution after the operator has run the two CORR1 tasks, without patching the custom again.
- The patch event is custom-project-centric, with backup id, before/after hashes and pending manual run states.

## Methodology

The active input is `Forward` because the current purpose is to re-audit the final survivor cohort inside SQX and preserve the exact 23-row finalist lineage. This is narrower than the earlier `Results` concept, so the downstream decision remains conservative:

- `IS_CORR` selects/diversifies when a broader upstream stability run exists.
- `OOS3_CORR` / `Forward` audits/vetoes stability for the finalist cohort.
- OOS3 does not select alternates. If it is used to choose replacements, another later holdout is required.

This block reuses the academic rationale documented in `docs/SQX142_PORTFOLIO_CORR1_STABILITY_AUDIT.md`: PBO, Deflated Sharpe Ratio, White Reality Check and purged/embargoed validation support avoiding repeated selection on the same holdout. They support the discipline, not a profitability claim.

## Boundaries

Allowed:

- Patch the targeted SQX142 custom project `project.cfx` while SQX is closed.
- Create empty CORR1 databank folders for the target custom.
- Write ignored backup/evidence under `.local`.
- Update SQX Edge-owned registry SQLite.

Blocked:

- no jars, engine binaries, internal plugins, license or activation changes.
- no SQX runtime launch from scripts.
- no `user/data/data.db` writes.
- no databank deletion.
- no `run_project`, Migration Tool or `/project/checkResources`.
- no forced pass, profit guarantee or risk-zero claim.

## Manual SQX Step

After `apply`, open SQX142 manually and confirm:

- custom project opens without red unresolved-resource warnings;
- original 12 tasks remain and CORR1 tasks appear active at the end;
- `Results` still contains the original strategies;
- `Forward`, `Synthetic`, `SQX EDGE CORR1 STABILITY` and `SQX EDGE CORR1 TAGGED` exist with the expected post-run counts.

After manual SQX execution, run `record` or the UI `Registrar CORR1` button to update the custom-project funnel.

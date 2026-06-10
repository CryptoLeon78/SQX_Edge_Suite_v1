import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const script = fs.readFileSync(path.join(repoRoot, 'tools/sqx144_mt5_instrument_parity_gate.ps1'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx144_mt5_instrument_parity.py'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/SQX144_MT5_INSTRUMENT_PARITY_GATE.md'), 'utf8');

[
  "sqx144-mt5-instrument-parity-gate-v1",
  "ValidateSet('status', 'audit', 'plan', 'backup', 'apply', 'verify', 'rollback')",
  "writesUserProjects = $false",
  "mutatesDatabanks = $false",
  "runsSqxTasks = $false",
  "launchesMt5 = $false",
  "runsMt5Ea = $false",
  "usesMigrationTool = $false",
  "offlineApplyOnly = $true",
  "core.sqx144_mt5_instrument_parity",
  "[switch]$Apply",
  "--approval",
].forEach((marker) => {
  assert.ok(script.includes(marker), `SQX144 MT5 wrapper marker missing: ${marker}`);
});

[
  "sqx144-mt5-instrument-parity-gate-v1",
  "sqlite_uri_mode_ro_query_only",
  "xml_external_entities_rejected",
  "duplicate_normalized_symbol",
  "empty_mt5_commissions_ignored",
  "APRUEBO SQX144 MT5 INSTRUMENT APPLY",
  "no_source_broker_history",
  "BROKER_ID",
  "DATEFROM",
  "DATETO",
  "ROWS",
].forEach((marker) => {
  assert.ok(core.includes(marker), `SQX144 MT5 core marker missing: ${marker}`);
});

[
  "sqx144-mt5-instrument-parity-gate-v1",
  "implemented_apply_gated_db_offline_usdjpy_pilot_ready",
  "USDJPY_Darwinex",
  "USDJPY_darwinex",
  "POINTVALUE",
  "TICKSIZE",
  "TICKSTEP",
  "DEFAULTSPREAD",
  "DEFAULTSLIPPAGE",
  "SWAP",
  "ORDERSIZEMULTIPLIER",
  "ORDERSIZESTEP",
  "empty MT5 commissions do not overwrite SQX commission",
  "writesUserProjects=false",
  "mutatesDatabanks=false",
  "runsSqxTasks=false",
  "Migration Tool is not used",
].forEach((marker) => {
  assert.ok(doc.includes(marker), `SQX144 MT5 doc marker missing: ${marker}`);
});

[
  'Start-Process',
  'project/start',
  'project/stop',
  'taskmanager/openProject',
  'Add missing symbols',
  'Load without resolving these issues',
  'Migration Tool allowed',
  'C:\\\\Program Files\\\\Darwinex MetaTrader 5 BEPB',
  'Remove-Item',
  'Set-Content',
  'Add-Content',
  'Copy-Item',
  'Move-Item',
].forEach((forbidden) => {
  assert.ok(!script.includes(forbidden), `SQX144 MT5 wrapper must not contain ${forbidden}`);
});

console.log('sqx144 mt5 instrument parity gate contracts ok');

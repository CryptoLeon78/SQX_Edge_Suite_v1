import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const scriptPath = path.join(repoRoot, 'tools/sqx144_electron_cache_refresh.ps1');
const runbookPath = path.join(repoRoot, 'docs/maintenance/SQX144_ELECTRON_CACHE_RUNBOOK.md');
const script = fs.readFileSync(scriptPath, 'utf8');
const runbook = fs.readFileSync(runbookPath, 'utf8');

[
  'sqx144-electron-cache-refresh-v1',
  "ValidateSet('status', 'plan', 'refresh')",
  'SQX144-CACHE1',
  'SQX_144_Full',
  'APRUEBO SQX144 ELECTRON CACHE REFRESH host=sqx144_full move_cache_only preserve_local_storage_indexeddb_preferences',
  'Move-Item',
  'Refusing to move outside Electron userData',
  'sqx_process_running',
  'sqx144_full_root_mismatch',
  'electron_user_data_outside_host_root',
  'deletesCache = $false',
  'writesDataDb = $false',
  'writesUserProjects = $false',
  'mutatesDatabanks = $false',
  'runsSqxTasks = $false',
  'launchesMt5 = $false',
  'runsMt5Ea = $false',
  'usesMigrationTool = $false',
  'directDbWriteAllowed = $false',
  'historyImportAllowed = $false',
  'preservesLocalStorage = $true',
  'preservesIndexedDb = $true',
  'preservesWebStorage = $true',
  'preservesPreferences = $true',
].forEach((marker) => {
  assert.ok(script.includes(marker), `SQX144 cache script marker missing: ${marker}`);
});

[
  'Cache',
  'Code Cache',
  'GPUCache',
  'DawnGraphiteCache',
  'DawnWebGPUCache',
  'blob_storage',
  'Network',
  'Session Storage',
  'Shared Dictionary',
].forEach((cacheName) => {
  assert.ok(script.includes(`'${cacheName}'`), `SQX144 cache script should include volatile cache ${cacheName}`);
});

[
  'Local Storage',
  'IndexedDB',
  'WebStorage',
  'Preferences',
  'Local State',
  'main-window-state.json',
  'DIPS',
  'SharedStorage',
].forEach((stateName) => {
  assert.ok(script.includes(`'${stateName}'`), `SQX144 cache script should preserve state ${stateName}`);
  assert.ok(runbook.includes(stateName), `SQX144 cache runbook should document preserved state ${stateName}`);
});

[
  'Remove-Item',
  'Stop-Process',
  'Start-Process',
  'DataSourceMt5Api/importData',
  'taskmanager/openProject',
  'project/start',
  'project/stop',
  'Add missing symbols',
  'Migration Tool allowed',
  'UPDATE INSTRUMENTS',
  'INSERT INTO',
  'DELETE FROM',
  'terminal64.exe',
].forEach((forbidden) => {
  assert.ok(!script.includes(forbidden), `SQX144 cache script must not contain ${forbidden}`);
});

[
  'sqx144-electron-cache-refresh-v1',
  'Aplicar cambios',
  'Move-Item',
  'does not use `Remove-Item`',
  'does not touch `data.db`',
].forEach((marker) => {
  assert.ok(runbook.includes(marker), `SQX144 cache runbook marker missing: ${marker}`);
});

console.log('sqx144 electron cache refresh contracts ok');

import { assert, createLoadedSandbox } from './harness.mjs';

const { SQX, sandbox } = createLoadedSandbox([
  'app/js/modules/state-backup.js',
]);

assert.equal(SQX.modules['state-backup'], SQX.stateBackup);

const keys = SQX.stateBackup.allowedKeys({
  storageKeys: () => ({
    priorityProgress: 'custom_priority',
    license: 'sqx_license_state_v1',
  }),
});
assert.equal(keys.includes('custom_priority'), true);
assert.equal(keys.includes('sqx_license_state_v1'), false);
assert.equal(keys.includes('sqx_fulfillment_operator_v1'), false);

sandbox.localStorage.setItem('custom_priority', JSON.stringify({ a: 'completed' }));
sandbox.localStorage.setItem('sqx_plan_user_v1', JSON.stringify({ minings: [{ num: 99 }], phases: {} }));
sandbox.localStorage.setItem('sqx_license_state_v1', JSON.stringify({ value: 'redacted' }));
const snapshot = SQX.stateBackup.collectState(sandbox.localStorage, {
  storageKeys: () => ({ priorityProgress: 'custom_priority' }),
});
assert.equal(snapshot.custom_priority.a, 'completed');
assert.equal(snapshot.sqx_plan_user_v1.minings[0].num, 99);
assert.equal(snapshot.sqx_license_state_v1, undefined);

const applied = SQX.stateBackup.applyState({
  custom_priority: { b: 'current' },
  sqx_license_state_v1: { value: 'must-not-restore' },
  sqx_pg_api_base_v1: 'http://127.0.0.1:5050/api',
}, sandbox.localStorage, {
  storageKeys: () => ({ priorityProgress: 'custom_priority' }),
});
assert.equal(applied.sort().join('|'), 'custom_priority|sqx_pg_api_base_v1');
assert.equal(JSON.parse(sandbox.localStorage.getItem('custom_priority')).b, 'current');
assert.equal(sandbox.localStorage.getItem('sqx_pg_api_base_v1'), 'http://127.0.0.1:5050/api');
assert.match(SQX.stateBackup.listHtml([{ name: 'state_backup_2026.json', size_kb: 1.4, mtime: 1778256000 }]), /Restaurar/);
assert.match(SQX.stateBackup.listHtml([{ name: 'state_backup_remote.json', size_kb: 1.4, mtime: 1778256000, scope: 'remote_workspace' }]), /workspace remoto/);

let lastFetch = null;
sandbox.fetch = async (url, options = {}) => {
  lastFetch = { url: String(url), options };
  if (String(url).endsWith('/state/backups')) {
    return { ok: true, json: async () => ({ ok: true, scope: 'remote_workspace', backups: [] }) };
  }
  if (String(url).includes('/state/restore/')) {
    return {
      ok: true,
      json: async () => ({
        ok: true,
        scope: 'remote_workspace',
        payload: { data: { sqx_plan_user_v1: { minings: [{ num: 7 }] } } }
      })
    };
  }
  return { ok: true, json: async () => ({ ok: true, scope: 'remote_workspace', filename: 'state_backup_contract.json' }) };
};
await SQX.stateBackup.createBackup({ storage: sandbox.localStorage });
assert.equal(lastFetch.options.credentials, 'include', 'state backup API should include remote credentials');
assert.equal(lastFetch.url.endsWith('/state/backup'), true, 'state backup should call backup endpoint');

let savedSnapshot = null;
SQX.remoteState = {
  saveSnapshot: async (keys, source) => {
    savedSnapshot = { keys, source };
    return { ok: true };
  }
};
await SQX.stateBackup.restoreBackup('state_backup_contract.json', { storage: sandbox.localStorage });
assert.deepEqual(Array.from(savedSnapshot.keys), ['sqx_plan_user_v1'], 'remote restore should resync restored keys to workspace state');
assert.equal(savedSnapshot.source, 'state-restore', 'remote restore should trace save source');

console.log('state backup contracts ok');

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

console.log('state backup contracts ok');

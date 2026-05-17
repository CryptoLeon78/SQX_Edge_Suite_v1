import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { assert, createLoadedSandbox, repoRoot } from './harness.mjs';

const calls = [];
const { SQX, sandbox, context } = createLoadedSandbox([
  'app/js/modules/storage.js',
]);

sandbox.SQX_CONFIG = {
  storageKeys: {
    planUser: 'sqx_plan_user_v1',
    pipelineState: 'sqx_pipeline_state_v1',
    strategiesUser: 'sqx_strategies_user_v1',
    strategiesDeleted: 'sqx_strategies_deleted_v1',
  },
  apiBase: () => 'https://sqx.example.invalid/api',
};
sandbox.fetch = (url, options = {}) => {
  calls.push({ url, options });
  if (url.endsWith('/remote/state/bootstrap')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({
        ok: true,
        version: 'remote-workspace-state-v1',
        state: {
          sqx_plan_user_v1: { minings: [{ num: 31, asset: 'XAUUSD' }], phases: {} },
          sqx_strategies_user_v1: [{ id: 'remote-strategy' }],
          sqx_license_state_v1: { ignored: true },
        },
        stateKeys: ['sqx_plan_user_v1', 'sqx_strategies_user_v1'],
      }),
    });
  }
  if (url.endsWith('/remote/state/save')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ ok: true, savedKeys: ['sqx_plan_user_v1'] }),
    });
  }
  throw new Error(`unexpected fetch ${url}`);
};

vm.runInContext(
  fs.readFileSync(path.join(repoRoot, 'app/js/modules/remote-state.js'), 'utf8'),
  context,
  { filename: 'remote-state.js' }
);

await SQX.remoteState.bootstrap();

assert.equal(SQX.remoteState.version, 'remote-workspace-state-v1');
assert.equal(SQX.remoteState.isEnabled(), true);
assert.equal(SQX.remoteState.allowedKeys().includes('sqx_plan_user_v1'), true);
assert.equal(SQX.remoteState.allowedKeys().includes('sqx_license_state_v1'), false);
assert.equal(JSON.parse(sandbox.localStorage.getItem('sqx_plan_user_v1')).minings[0].num, 31);
assert.equal(JSON.parse(sandbox.localStorage.getItem('sqx_strategies_user_v1'))[0].id, 'remote-strategy');
assert.equal(sandbox.localStorage.getItem('sqx_license_state_v1'), null);

SQX.storage.setJson('sqx_plan_user_v1', { minings: [{ num: 32 }], phases: {} });
assert.equal(calls.some(call => call.url === 'https://sqx.example.invalid/api/remote/state/save'), true);

console.log('remote state contracts ok');

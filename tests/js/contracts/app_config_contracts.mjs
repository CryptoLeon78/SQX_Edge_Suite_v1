import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { assert, repoRoot } from './harness.mjs';

function loadApiBase(location, storedApiBase = '') {
  const store = new Map();
  if (storedApiBase) store.set('sqx_pg_api_base_v1', storedApiBase);
  const sandbox = {
    window: null,
    globalThis: null,
    document: {
      body: { classList: { toggle() {} } },
      querySelector() { return null; },
      querySelectorAll() { return []; },
      getElementById() { return null; },
    },
    localStorage: {
      getItem: key => store.has(key) ? store.get(key) : null,
      setItem: (key, value) => store.set(key, String(value)),
    },
    location,
    SQX_MANIFEST: {
      ui: {
        api: { defaultHost: '127.0.0.1', defaultPort: 5050, basePath: '/api', remoteBasePath: '/dashboard/api' },
        storageKeys: { apiBase: 'sqx_pg_api_base_v1' },
      },
      product: {},
    },
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  const context = vm.createContext(sandbox);
  const code = fs.readFileSync(path.join(repoRoot, 'app/js/app-config.js'), 'utf8');
  vm.runInContext(code, context, { filename: 'app/js/app-config.js' });
  return sandbox.SQX_CONFIG.apiBase();
}

function loadDiagnostics(location, storedApiBase = '') {
  const store = new Map();
  if (storedApiBase) store.set('sqx_pg_api_base_v1', storedApiBase);
  const sandbox = {
    window: null,
    globalThis: null,
    document: {
      body: { classList: { toggle() {} } },
      querySelector() { return null; },
      querySelectorAll() { return []; },
      getElementById() { return null; },
    },
    localStorage: {
      getItem: key => store.has(key) ? store.get(key) : null,
      setItem: (key, value) => store.set(key, String(value)),
      removeItem: key => store.delete(key),
    },
    location,
    SQX_MANIFEST: {
      ui: {
        api: { defaultHost: '127.0.0.1', defaultPort: 5050, basePath: '/api', remoteBasePath: '/dashboard/api' },
        storageKeys: { apiBase: 'sqx_pg_api_base_v1' },
      },
      product: {},
    },
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  const context = vm.createContext(sandbox);
  const code = fs.readFileSync(path.join(repoRoot, 'app/js/app-config.js'), 'utf8');
  vm.runInContext(code, context, { filename: 'app/js/app-config.js' });
  return sandbox.SQX_CONFIG.diagnostics();
}

assert.equal(
  loadApiBase({ protocol: 'https:', hostname: 'app.sqxedgesuite.org', origin: 'https://app.sqxedgesuite.org' }),
  'https://app.sqxedgesuite.org/dashboard/api',
);

assert.equal(
  loadApiBase({ protocol: 'http:', hostname: 'localhost', origin: 'http://localhost:8080' }),
  'http://localhost:5050/api',
);

assert.equal(
  loadApiBase({ protocol: 'https:', hostname: 'app.sqxedgesuite.org', origin: 'https://app.sqxedgesuite.org' }, 'https://app.sqxedgesuite.org/dashboard/api-v2'),
  'https://app.sqxedgesuite.org/dashboard/api-v2',
  'remote app may keep an explicit dashboard-scoped API base',
);

assert.equal(
  loadApiBase({ protocol: 'https:', hostname: 'app.sqxedgesuite.org', origin: 'https://app.sqxedgesuite.org' }, 'https://app.sqxedgesuite.org/api'),
  'https://app.sqxedgesuite.org/dashboard/api',
  'remote app must migrate old same-origin /api bases to the dashboard-scoped API alias',
);

assert.equal(
  loadApiBase({ protocol: 'https:', hostname: 'app.sqxedgesuite.org', origin: 'https://app.sqxedgesuite.org' }, 'https://custom.example.invalid/api'),
  'https://app.sqxedgesuite.org/dashboard/api',
  'remote app must ignore cross-origin API bases from old tester storage',
);

assert.equal(
  loadApiBase({ protocol: 'https:', hostname: 'app.sqxedgesuite.org', origin: 'https://app.sqxedgesuite.org' }, 'http://127.0.0.1:5050/api'),
  'https://app.sqxedgesuite.org/dashboard/api',
  'remote app must ignore stale local API base from tester browser storage',
);

assert.equal(
  loadApiBase({ protocol: 'https:', hostname: 'app.sqxedgesuite.org', origin: 'https://app.sqxedgesuite.org' }, 'http://example.invalid/api'),
  'https://app.sqxedgesuite.org/dashboard/api',
  'remote app must ignore insecure stored API bases from old sessions',
);

assert.equal(
  loadApiBase({ protocol: 'http:', hostname: 'localhost', origin: 'http://localhost:8080' }, 'http://127.0.0.1:5050/api'),
  'http://127.0.0.1:5050/api',
  'local operator mode should still allow local API base',
);

const remoteDiagnostics = loadDiagnostics(
  { protocol: 'https:', hostname: 'app.sqxedgesuite.org', host: 'app.sqxedgesuite.org', origin: 'https://app.sqxedgesuite.org' },
  'https://custom.example.invalid/api',
);
assert.equal(remoteDiagnostics.configVersion, 'remote-api-same-origin-v2');
assert.equal(remoteDiagnostics.apiBase, 'https://app.sqxedgesuite.org/dashboard/api');
assert.equal(remoteDiagnostics.pageOrigin, 'https://app.sqxedgesuite.org');

console.log('app config contracts ok');

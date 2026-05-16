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
        api: { defaultHost: '127.0.0.1', defaultPort: 5050, basePath: '/api' },
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

assert.equal(
  loadApiBase({ protocol: 'https:', hostname: 'app.sqxedgesuite.org', origin: 'https://app.sqxedgesuite.org' }),
  'https://app.sqxedgesuite.org/api',
);

assert.equal(
  loadApiBase({ protocol: 'http:', hostname: 'localhost', origin: 'http://localhost:8080' }),
  'http://localhost:5050/api',
);

assert.equal(
  loadApiBase({ protocol: 'https:', hostname: 'app.sqxedgesuite.org', origin: 'https://app.sqxedgesuite.org' }, 'https://custom.example.invalid/api'),
  'https://custom.example.invalid/api',
);

console.log('app config contracts ok');

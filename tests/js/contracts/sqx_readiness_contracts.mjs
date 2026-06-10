import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { assert, Element, createLoadedSandbox, repoRoot } from './harness.mjs';

const required = [
  'sqx_root_selected',
  'sqx_version_compatible',
  'data_db_found',
  'brokers_validated',
  'curated_assets_validated',
  'snippets_ready',
  'correlation_view_ready',
  'portable_source_acknowledged',
  'sensitive_files_excluded',
];
const { SQX, sandbox, context, document } = createLoadedSandbox([
  'app/js/modules/config.js',
  'app/js/modules/storage.js',
]);
document.add(new Element('sqx-readiness-backdrop'));
document.add(new Element('sqx-readiness-progress'));
document.add(new Element('sqx-readiness-detail'));
document.add(new Element('sqx-readiness-count'));
document.add(new Element('sqx-readiness-refresh'));
document.add(new Element('sqx-readiness-dismiss'));
document.add(new Element('sqx-readiness-report-file'));
const generateButton = document.add(new Element('pg-custom-generate', [], { sqxReadinessRequires: 'project_generator.generate' }));
required.forEach(id => {
  const input = document.add(new Element(`readiness-${id}`, [], { sqxReadinessCheck: id }));
  input.tagName = 'input';
  input.type = 'checkbox';
});

const calls = [];
sandbox.SQX_CONFIG = {
  storageKeys: { sqxReadinessStatus: 'sqx_readiness_status_v1' },
  apiBase: () => 'https://sqx.example.invalid/api',
};
sandbox.fetch = (url, options = {}) => {
  calls.push({ url, options });
  if (url.endsWith('/sqx-readiness/manifest')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ ok: true, requiredChecklist: required, privacy: { dataDbCopied: false } }),
    });
  }
  if (url.endsWith('/sqx-readiness/status')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({
        ok: true,
        complete: false,
        checks: Object.fromEntries(required.map(id => [id, false])),
        missing: required,
      }),
    });
  }
  if (url.endsWith('/sqx-readiness/report')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({
        ok: true,
        complete: true,
        checks: Object.fromEntries(required.map(id => [id, true])),
        missing: [],
        source: 'checker_report',
      }),
    });
  }
  throw new Error(`unexpected fetch ${url}`);
};

vm.runInContext(
  fs.readFileSync(path.join(repoRoot, 'app/js/modules/sqx-readiness.js'), 'utf8'),
  context,
  { filename: 'sqx-readiness.js' }
);

await SQX.sqxReadiness.init();
assert.equal(SQX.sqxReadiness.version, 'sqx-edge.sqx-readiness-status-v1');
assert.equal(document.documentElement.dataset.sqxReadiness, 'blocked');
assert.equal(document.getElementById('sqx-readiness-backdrop').hidden, false);
assert.equal(generateButton.disabled, true);
assert.equal(JSON.parse(sandbox.localStorage.getItem('sqx_readiness_status_v1')).complete, false);

await SQX.sqxReadiness.importReport({ checkerVersion: 'test', checks: Object.fromEntries(required.map(id => [id, true])) });
assert.equal(document.documentElement.dataset.sqxReadiness, 'complete');
assert.equal(document.getElementById('sqx-readiness-backdrop').hidden, true);
assert.equal(generateButton.disabled, false);
assert.equal(calls.some(call => call.url.endsWith('/sqx-readiness/report')), true);

console.log('sqx readiness contracts ok');

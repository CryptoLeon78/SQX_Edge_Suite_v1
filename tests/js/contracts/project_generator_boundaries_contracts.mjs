import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const moduleDir = path.join(repoRoot, 'app/js/modules');
const readModule = name => fs.readFileSync(path.join(moduleDir, name), 'utf8');

const files = {
  cleaner: readModule('project-generator-cleaner.js'),
  config: readModule('project-generator-config.js'),
  core: readModule('project-generator-core.js'),
  dom: readModule('project-generator-dom.js'),
  renderers: readModule('project-generator-renderers.js'),
  shell: readModule('project-generator.js'),
  status: readModule('project-generator-status.js'),
};

[
  ['core', 'computeOnboardingState'],
  ['core', 'applyOnboardingState'],
  ['core', 'applyStatusBanner'],
  ['core', 'fetchJson'],
  ['config', 'configSaveBody'],
  ['config', 'aliasTableHtml'],
  ['config', 'validateSqxPathHtml'],
  ['dom', 'readConfigInputs'],
  ['dom', 'writeConfigInputs'],
  ['dom', 'appendLog'],
  ['renderers', 'miningRowsHtml'],
  ['renderers', 'outputState'],
  ['status', 'generateOneResult'],
  ['status', 'openOutputSuccessStatus'],
  ['cleaner', 'cleanerTableHtml'],
  ['cleaner', 'cleanerOptions'],
].forEach(([bucket, fn]) => {
  assert.match(files[bucket], new RegExp(`function ${fn}\\(`), `${fn} should live in ${bucket}`);
});

[
  ['core', 'cleaner'],
  ['core', 'miningRowsHtml'],
  ['config', 'cleanerTableHtml'],
  ['config', 'generateOneResult'],
  ['dom', 'cleanerTableHtml'],
  ['dom', 'generateOneResult'],
  ['renderers', 'configSaveBody'],
  ['renderers', 'cleanerOptions'],
  ['status', 'cleanerTableHtml'],
  ['status', 'aliasTableHtml'],
  ['cleaner', 'configSaveBody'],
  ['cleaner', 'generateOneResult'],
].forEach(([bucket, forbidden]) => {
  assert.doesNotMatch(files[bucket], new RegExp(forbidden), `${bucket} should not contain ${forbidden}`);
});

assert.match(files.shell, /SQX\.registerModule\('project-generator', SQX\.projectGenerator\)/);
assert.doesNotMatch(files.shell, /function computeOnboardingState\(/);
assert.doesNotMatch(files.shell, /function cleanerTableHtml\(/);
assert.doesNotMatch(files.shell, /Object\.assign\(PG/);

console.log('project generator boundaries contracts ok');

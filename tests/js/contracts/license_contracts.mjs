import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const licenseJs = fs.readFileSync(path.join(repoRoot, 'app/js/modules/license.js'), 'utf8');
const productManifest = JSON.parse(fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/product_manifest.json'), 'utf8'));
const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');

for (const exportName of [
  'currentStatus',
  'fetchJson',
  'hasFeature',
  'importLicenseText',
  'renderPanel',
  'refreshBackendStatus',
  'storageKey',
]) {
  assert.ok(licenseJs.includes(exportName), `missing license export ${exportName}`);
}

assert.ok(licenseJs.includes("SQX.registerModule('license'"));
assert.equal(productManifest.build.channel, 'internal');
assert.equal(productManifest.licensing.signatureMode, 'rsa_sha256_pkcs1_v1_5');
assert.equal(productManifest.licensing.signatureAlgorithm, 'RS256');
assert.ok(productManifest.licensing.publicKey.n.length > 100);
assert.equal(productManifest.upgrade.headline, 'SQX Edge Pro');
assert.ok(productManifest.upgrade.bullets.length >= 3);
assert.ok(JSON.stringify(productManifest.upgrade).includes('24 EUR/mes'));
assert.ok(productManifest.marketing.tagline.includes('pipeline operativo'));
assert.ok(productManifest.features['project_generator.generate']);
assert.ok(productManifest.features['strategy_cleaner.apply']);
assert.deepEqual(productManifest.accessLevels.internal.features, ['*']);
assert.ok(html.includes('id="license-panel"'));
assert.ok(html.includes('id="license-upgrade-list"'));
assert.ok(html.includes('id="license-plan-strip"'));
assert.ok(html.includes('js/modules/license.js'));
assert.ok(licenseJs.includes('/license/import'));
assert.ok(licenseJs.includes('/license/clear'));

console.log('license contracts ok');

import fs from 'node:fs';
import path from 'node:path';
import { assert, createLoadedSandbox, repoRoot } from './harness.mjs';

const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const mainJs = fs.readFileSync(path.join(repoRoot, 'app/js/main.js'), 'utf8');
const uiManifest = JSON.parse(fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/ui_manifest.json'), 'utf8'));
const productManifest = JSON.parse(fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/product_manifest.json'), 'utf8'));

const { SQX } = createLoadedSandbox(['app/js/modules/view-creator.js']);
const viewCreator = SQX.viewCreator;

assert.ok(html.includes('id="tab-views"'), 'missing SQX Views tab panel');
assert.ok(html.includes('id="vc-metric-list"'), 'missing metric catalog mount');
assert.ok(html.includes('id="vc-download-btn"'), 'missing .vw download button');
assert.ok(html.includes('id="vc-save-preset-btn"'), 'missing saved preset button');
assert.ok(html.includes('id="vc-saved-select"'), 'missing saved preset selector');
assert.ok(html.includes('id="vc-export-presets-btn"'), 'missing preset pack export button');
assert.ok(html.includes('id="vc-import-presets-btn"'), 'missing preset pack import button');
assert.ok(html.includes('js/modules/view-creator.js'), 'missing view creator script');
assert.ok(mainJs.includes('window.SQX.viewCreator.init()'), 'main.js must initialize view creator');
assert.ok(uiManifest.tabs.some(tab => tab.id === 'views' && tab.label === 'SQX Views'), 'ui manifest missing SQX Views tab');
assert.equal(uiManifest.storageKeys.viewCreatorPresets, 'sqx_view_creator_presets_v1');
assert.equal(productManifest.features['view_creator.core'].tier, 'free');
assert.equal(productManifest.features['view_creator.full'].tier, 'pro');
assert.ok(productManifest.accessLevels.free.features.includes('view_creator.core'));
assert.ok(productManifest.accessLevels.pro.features.includes('view_creator.full'));

assert.equal(viewCreator.metrics.length, 88, 'catalog should preserve the imported metric universe');
assert.ok(viewCreator.metrics.some(metric => metric.className === 'AnnualPctReturnDDRatio'));
assert.ok(viewCreator.metrics.some(metric => metric.className === 'VaR_Hobbiecode'));
assert.ok(viewCreator.metrics.some(metric => metric.className === 'NumberOfCanceled'));

const egtCore = viewCreator.metrics
  .filter(metric => metric.selectedDefault)
  .map(metric => ({
    display: metric.display,
    className: metric.className,
    annual: metric.category !== 'fixed' && metric.annualDefault,
  }));
const columns = viewCreator.columnSpecs(egtCore, 9, 21, true, 'by_year');
assert.equal(columns.length, 104, 'EGT Core should match the supplied annual view shape');
assert.equal(columns.filter(column => column.sampleType === 21).length, 10);
assert.equal(columns.filter(column => column.sampleType === 127).length, 14);

const xml = viewCreator.buildViewXml({
  viewName: 'EGT - Anual',
  selected: egtCore,
  yearCount: 9,
  sampleStart: 21,
  includeTotal: true,
  groupMode: 'by_year',
});
assert.ok(xml.startsWith('<View name="EGT - Anual" originalName="EGT - Anual">'));
assert.ok(xml.includes('class="AnnualPctReturnDDRatio"'));
assert.ok(xml.includes('sampleType="29"'));
assert.ok(xml.endsWith('</View>'));

const savedConfig = viewCreator.serializeConfig({
  viewName: 'Risk View',
  yearCount: 5,
  sampleStart: 21,
  includeTotal: false,
  groupMode: 'by_metric',
  selected: egtCore.slice(0, 3),
});
assert.equal(savedConfig.viewName, 'Risk View');
assert.equal(savedConfig.metrics.length, 3);
assert.equal(savedConfig.groupMode, 'by_metric');
assert.equal(viewCreator.storageKey, 'sqx_view_creator_presets_v1');
viewCreator.setSavedPresets([{ id: 'risk-view', name: 'Risk View', config: savedConfig }]);
assert.equal(viewCreator.getSavedPresets().length, 1);
assert.equal(viewCreator.getSavedPresets()[0].config.yearCount, 5);
assert.equal(viewCreator.packageType, 'sqx-edge.view-presets');
assert.equal(viewCreator.packageVersion, 1);

const presetPack = viewCreator.buildPresetPackage();
assert.equal(presetPack.type, 'sqx-edge.view-presets');
assert.equal(presetPack.presets.length, 1);
assert.equal(presetPack.presets[0].id, 'risk-view');

const importResult = viewCreator.importPresetPackageFromText(JSON.stringify({
  type: 'sqx-edge.view-presets',
  version: 1,
  presets: [{
    id: 'risk-view',
    name: 'Risk View Imported',
    config: {
      viewName: 'Risk View Imported',
      yearCount: 6,
      sampleStart: 22,
      includeTotal: true,
      groupMode: 'by_year',
      metrics: [
        { className: 'Symbol', annual: false },
        { className: 'NetProfit', annual: true },
        { className: 'UnknownMetric', annual: true },
      ],
    },
  }],
}));
assert.equal(importResult.imported, 1);
assert.equal(viewCreator.getSavedPresets().length, 1);
assert.equal(viewCreator.getSavedPresets()[0].name, 'Risk View Imported');
assert.equal(viewCreator.getSavedPresets()[0].config.metrics.length, 2);

console.log('view creator contracts ok');

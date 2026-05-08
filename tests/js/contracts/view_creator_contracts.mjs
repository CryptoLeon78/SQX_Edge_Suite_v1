import fs from 'node:fs';
import path from 'node:path';
import { assert, createLoadedSandbox, Element, repoRoot } from './harness.mjs';

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
assert.ok(html.includes('id="vc-template-list"'), 'missing buyer-ready template list');
assert.ok(html.includes('id="vc-export-template-pack-btn"'), 'missing buyer-ready template pack export button');
assert.ok(html.includes('id="vc-profile-list"'), 'missing buyer profile pack list');
assert.ok(html.includes('id="vc-profile-count"'), 'missing buyer profile pack count');
assert.ok(html.includes('id="vc-workflow-pack-list"'), 'missing validation workflow pack list');
assert.ok(html.includes('id="vc-workflow-pack-count"'), 'missing validation workflow pack count');
assert.ok(html.includes('id="strat-views-handoff"'), 'missing strategies to SQX Views handoff');
assert.ok(html.includes('id="workflow-views-handoff"'), 'missing workflow to SQX Views handoff');
assert.ok(html.includes('data-vc-handoff="risk"'), 'missing risk view handoff preset');
assert.ok(html.includes('data-vc-handoff="robustness"'), 'missing robustness view handoff preset');
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

const buyerTemplates = viewCreator.buyerReadyTemplates();
assert.equal(buyerTemplates.length, 4);
assert.ok(buyerTemplates.some(template => template.id === 'egt-first-review' && template.tier === 'free'));
assert.ok(buyerTemplates.some(template => template.id === 'full-audit-handoff' && template.config.groupMode === 'by_metric'));
assert.ok(buyerTemplates.every(template => template.config.metrics.length > 0));
const buyerPack = viewCreator.buildBuyerReadyTemplatePack();
assert.equal(buyerPack.type, 'sqx-edge.view-presets');
assert.equal(buyerPack.presets.length, 4);
assert.ok(buyerPack.presets.some(preset => preset.id === 'buyer-risk-capital-review'));
const profilePacks = viewCreator.buyerProfilePacks();
assert.equal(profilePacks.length, 4);
assert.ok(profilePacks.some(pack => pack.id === 'free-evaluation-starter' && pack.tier === 'free'));
assert.ok(profilePacks.some(pack => pack.id === 'pro-setup-assist' && pack.templates.length === 3));
const setupPack = viewCreator.buildBuyerProfilePack('pro-setup-assist');
assert.equal(setupPack.type, 'sqx-edge.view-presets');
assert.equal(setupPack.presets.length, 3);
assert.ok(setupPack.presets.some(preset => preset.id === 'profile-pro-setup-assist-risk-capital-review'));
assert.ok(viewCreator.buildAllBuyerProfilePacks().presets.length >= 9);
const workflowPacks = viewCreator.validationWorkflowPacks();
assert.equal(workflowPacks.length, 4);
assert.ok(workflowPacks.some(pack => pack.id === 'free-core-validation' && pack.tier === 'free'));
assert.ok(workflowPacks.some(pack => pack.id === 'asset-family-review' && pack.type === 'asset'));
const assetFamilyPack = viewCreator.buildValidationWorkflowPack('asset-family-review');
assert.equal(assetFamilyPack.type, 'sqx-edge.view-presets');
assert.equal(assetFamilyPack.presets.length, 3);
assert.ok(assetFamilyPack.presets.some(preset => preset.id === 'workflow-asset-family-review-gold-risk-review'));
assert.ok(viewCreator.buildAllValidationWorkflowPacks().presets.length >= 10);

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

const handoffSandbox = createLoadedSandbox(['app/js/modules/ui.js', 'app/js/modules/view-creator.js']);
handoffSandbox.document.addTab('inicio', true);
handoffSandbox.document.addTab('views', false);
[
  'vc-view-name',
  'vc-year-count',
  'vc-sample-start',
  'vc-group-mode',
  'vc-include-total',
  'vc-preview',
  'vc-selected-count',
  'vc-column-count',
  'vc-year-range',
  'vc-preview-title',
  'vc-mode-label',
  'vc-status',
].forEach(id => handoffSandbox.document.add(new Element(id)));
handoffSandbox.document.getElementById('vc-include-total').checked = true;
handoffSandbox.document.getElementById('vc-group-mode').value = 'by_year';
handoffSandbox.SQX.viewCreator.openHandoff({ preset: 'risk', viewName: 'SQX Risk Review', yearCount: 5 });
assert.ok(handoffSandbox.document.getElementById('tab-btn-views').classList.contains('active'));
assert.equal(handoffSandbox.document.getElementById('vc-view-name').value, 'SQX Risk Review');
assert.equal(handoffSandbox.document.getElementById('vc-year-count').value, 5);
assert.ok(Number(handoffSandbox.document.getElementById('vc-column-count').textContent) > 64);

const templateSandbox = createLoadedSandbox(['app/js/modules/view-creator.js']);
[
  'vc-view-name',
  'vc-year-count',
  'vc-sample-start',
  'vc-group-mode',
  'vc-include-total',
  'vc-preview',
  'vc-selected-count',
  'vc-column-count',
  'vc-year-range',
  'vc-preview-title',
  'vc-mode-label',
  'vc-status',
  'vc-saved-select',
  'vc-saved-count',
].forEach(id => templateSandbox.document.add(new Element(id)));
templateSandbox.document.getElementById('vc-include-total').checked = true;
templateSandbox.document.getElementById('vc-group-mode').value = 'by_year';
const loadedTemplate = templateSandbox.SQX.viewCreator.loadBuyerReadyTemplate('risk-capital-review');
assert.equal(loadedTemplate.name, 'Risk Capital Review');
assert.equal(templateSandbox.document.getElementById('vc-view-name').value, 'Risk Capital Review');
assert.ok(Number(templateSandbox.document.getElementById('vc-column-count').textContent) > 64);
const savedTemplate = templateSandbox.SQX.viewCreator.saveBuyerReadyTemplate('risk-capital-review');
assert.equal(savedTemplate.id, 'buyer-risk-capital-review');
assert.equal(templateSandbox.SQX.viewCreator.getSavedPresets().length, 1);
const loadedProfile = templateSandbox.SQX.viewCreator.loadBuyerProfilePack('risk-capital-buyer');
assert.equal(loadedProfile.name, 'Risk Capital Buyer');
assert.equal(templateSandbox.document.getElementById('vc-view-name').value, 'Risk Capital Review');
const savedProfile = templateSandbox.SQX.viewCreator.saveBuyerProfilePack('risk-capital-buyer');
assert.equal(savedProfile.length, 2);
assert.ok(templateSandbox.SQX.viewCreator.getSavedPresets().some(preset => preset.id === 'profile-risk-capital-buyer-risk-capital-review'));
const loadedWorkflow = templateSandbox.SQX.viewCreator.loadValidationWorkflowPack('asset-family-review');
assert.equal(loadedWorkflow.name, 'Asset Family Review');
assert.equal(templateSandbox.document.getElementById('vc-view-name').value, 'Forex First Review');
const savedWorkflow = templateSandbox.SQX.viewCreator.saveValidationWorkflowPack('asset-family-review');
assert.equal(savedWorkflow.length, 3);
assert.ok(templateSandbox.SQX.viewCreator.getSavedPresets().some(preset => preset.id === 'workflow-asset-family-review-gold-risk-review'));

console.log('view creator contracts ok');

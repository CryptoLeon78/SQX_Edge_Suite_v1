import fs from 'node:fs';
import path from 'node:path';
import { assert, createLoadedSandbox, Element, repoRoot } from './harness.mjs';

const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const mainJs = fs.readFileSync(path.join(repoRoot, 'app/js/main.js'), 'utf8');
const uiManifest = JSON.parse(fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/ui_manifest.json'), 'utf8'));
const productManifest = JSON.parse(fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/config/product_manifest.json'), 'utf8'));

const { SQX } = createLoadedSandbox(['app/js/modules/view-creator.js']);
const viewCreator = SQX.viewCreator;

assert.ok(html.includes('id="tab-views"'), 'missing View CORR1 tab panel');
assert.ok(html.includes('SQX EDGE CORRELATION REVIEW'), 'missing active correlation view contract');
assert.ok(html.includes('Plano CORR1'), 'missing flat CORR1 column order option');
assert.ok(html.includes('id="vc-template-list"'), 'missing buyer-ready template list');
assert.ok(html.includes('views-guide-flow'), 'missing guided View CORR1 flow');
assert.ok(html.includes('id="vc-active-guide"'), 'missing active view guide');
assert.ok(html.includes('id="vc-download-btn"'), 'missing .vw download button');
assert.ok(!html.includes('data-vc-handoff="risk"'), 'risk handoff should not render');
assert.ok(!html.includes('data-vc-handoff="robustness"'), 'robustness handoff should not render');
assert.ok(!html.includes('EGT Core'), 'EGT Core view should not render as active View CORR1 UX');
assert.ok(!html.includes('CVC Decision Cert'), 'CVC Decision Cert view should not render as active View CORR1 UX');
assert.ok(!html.includes('Full audit'), 'Full audit view should not render as active View CORR1 UX');
assert.ok(mainJs.includes('window.SQX.viewCreator.init()'), 'main.js must initialize view creator');
assert.ok(uiManifest.tabs.some(tab => tab.id === 'views' && tab.label === 'View CORR1'), 'ui manifest missing View CORR1 tab');
assert.equal(uiManifest.storageKeys.viewCreatorPresets, 'sqx_view_creator_presets_v1');
assert.equal(productManifest.features['view_creator.core'].label, 'View CORR1');
assert.equal(productManifest.features['view_creator.full'].label, 'View CORR1 completo');

assert.equal(viewCreator.metrics.length, 96, 'metric universe should remain available for custom/user presets');
assert.ok(viewCreator.metrics.some(metric => metric.className === 'SQXEdgeCorrDecision'));
assert.ok(viewCreator.metrics.some(metric => metric.className === 'ReturnDDRatio'));
assert.ok(viewCreator.metrics.some(metric => metric.className === 'VaR_Hobbiecode'));

const buyerTemplates = viewCreator.buyerReadyTemplates();
assert.equal(buyerTemplates.length, 1, 'SQX Views should expose only the CORR1 buyer-ready template');
const corrTemplate = buyerTemplates[0];
assert.equal(corrTemplate.id, 'sqx-edge-correlation-review');
assert.equal(corrTemplate.name, 'SQX EDGE CORRELATION REVIEW');
assert.equal(corrTemplate.priority, 'obligatoria');
assert.equal(corrTemplate.oosTag, 'corr1');
assert.equal(corrTemplate.config.viewName, 'SQX EDGE CORRELATION REVIEW');
assert.equal(corrTemplate.config.yearCount, 1);
assert.equal(corrTemplate.config.includeTotal, false);
assert.equal(corrTemplate.config.groupMode, 'plain');
assert.ok(corrTemplate.config.metrics.some(metric => metric.className === 'SQXEdgeCorrDecision'));
assert.ok(corrTemplate.config.metrics.some(metric => metric.className === 'ReturnDDRatio'));
assert.ok(corrTemplate.metricTags.includes('CORR1'));
assert.ok(corrTemplate.metricTags.includes('Decision'));
assert.equal(
  JSON.stringify(buyerTemplates.map(template => template.id)),
  JSON.stringify(['sqx-edge-correlation-review']),
  'retired SQX view templates must stay out of the exposed catalog'
);

const corrColumns = viewCreator.columnSpecs(corrTemplate.config.metrics, 1, 21, false, 'plain');
assert.equal(corrColumns.length, 17, 'CORR1 view should export the active 17-column contract');
assert.ok(corrColumns.every(column => column.sampleType === 127), 'CORR1 plain contract should use consolidated sample columns');
const corrXml = viewCreator.buildTemplateMakerCertView();
assert.ok(corrXml.includes('name="SQX EDGE CORRELATION REVIEW"'));
assert.equal((corrXml.match(/<Column /g) || []).length, 17, 'Template Maker helper should match CORR1 columns');
assert.ok(corrXml.includes('class="SQXEdgeCorrDecision" name="SQX Edge Corr Decision"'));
assert.ok(corrXml.includes('class="ReturnDDRatio" name="Ret/DD Ratio"'));
assert.equal(viewCreator.buildCvcDecisionCertView, undefined);
assert.equal(viewCreator.getCvcDecisionRequiredMetrics, undefined);
assert.equal(viewCreator.buyerProfilePacks, undefined);
assert.equal(viewCreator.validationWorkflowPacks, undefined);

const templateMakerRequired = viewCreator.getTemplateMakerRequiredMetrics();
assert.ok(templateMakerRequired.includes('Profit factor'));
assert.ok(templateMakerRequired.includes('Ret/DD Ratio'));
assert.ok(templateMakerRequired.includes('SQX Edge Corr Decision'));

const savedConfig = viewCreator.serializeConfig({
  viewName: 'CORR1 User View',
  yearCount: 1,
  sampleStart: 21,
  includeTotal: false,
  groupMode: 'plain',
  selected: corrTemplate.config.metrics.slice(0, 4),
});
assert.equal(savedConfig.viewName, 'CORR1 User View');
assert.equal(savedConfig.yearCount, 1);
assert.equal(savedConfig.groupMode, 'plain');
assert.equal(savedConfig.metrics.length, 4);
assert.equal(viewCreator.storageKey, 'sqx_view_creator_presets_v1');

let remotePresetPayload = null;
SQX.remoteState = {
  bootstrap: () => Promise.resolve({ ok: true }),
  saveNow: (payload, source) => {
    remotePresetPayload = { payload, source };
    return Promise.resolve({ ok: true });
  },
};
viewCreator.setSavedPresets([{ id: 'corr1-user-view', name: 'CORR1 User View', config: savedConfig }]);
await Promise.resolve();
await Promise.resolve();
assert.equal(viewCreator.getSavedPresets().length, 1);
assert.equal(remotePresetPayload.source, 'sqx-views-presets');
assert.equal(remotePresetPayload.payload.sqx_view_creator_presets_v1[0].id, 'corr1-user-view');
assert.equal(viewCreator.packageType, 'sqx-edge.view-presets');
assert.equal(viewCreator.packageVersion, 1);

const buyerPack = viewCreator.buildBuyerReadyTemplatePack();
assert.equal(buyerPack.type, 'sqx-edge.view-presets');
assert.equal(buyerPack.presets.length, 1);
assert.equal(buyerPack.presets[0].id, 'buyer-sqx-edge-correlation-review');
assert.equal(buyerPack.presets[0].config.groupMode, 'plain');

const presetPack = viewCreator.buildPresetPackage();
assert.equal(presetPack.type, 'sqx-edge.view-presets');
assert.equal(presetPack.presets.length, 1);
assert.equal(presetPack.presets[0].id, 'corr1-user-view');

const importPayload = JSON.stringify({
  type: 'sqx-edge.view-presets',
  version: 1,
  presets: [
    {
      id: 'corr1-user-view',
      name: 'CORR1 User View Imported',
      config: {
        viewName: 'CORR1 User View Imported',
        yearCount: 1,
        sampleStart: 21,
        includeTotal: false,
        groupMode: 'plain',
        metrics: [
          { className: 'Symbol', annual: false },
          { className: 'SQXEdgeCorrDecision', annual: false },
          { className: 'UnknownMetric', annual: true },
        ],
      },
    },
    {
      id: 'corr1-preview',
      name: 'CORR1 Preview',
      config: {
        viewName: 'CORR1 Preview',
        yearCount: 1,
        sampleStart: 21,
        includeTotal: false,
        groupMode: 'plain',
        metrics: [
          { className: 'Symbol', annual: false },
          { className: 'ReturnDDRatio', annual: true },
        ],
      },
    },
  ],
});
const preview = viewCreator.presetImportPreviewFromText(importPayload);
assert.equal(preview.incomingCount, 2);
assert.equal(preview.duplicateCount, 1);
assert.equal(preview.newCount, 1);
assert.match(viewCreator.presetImportPreviewSummary(preview), /2 presets · 1 nuevos · 1 reemplazos/);
assert.match(viewCreator.presetImportPreviewHtml(preview), /views-import-preview-row/);
assert.match(viewCreator.presetImportPreviewHtml(preview), /reemplaza/);
const importResult = viewCreator.importPresetPackageFromText(importPayload);
assert.equal(importResult.imported, 2);
assert.equal(viewCreator.getSavedPresets().length, 2);
assert.equal(viewCreator.getSavedPresets()[0].name, 'CORR1 User View Imported');
assert.equal(viewCreator.getSavedPresets()[0].config.metrics.length, 2);

const handoffSandbox = createLoadedSandbox(['app/js/modules/ui.js', 'app/js/modules/view-creator.js']);
handoffSandbox.document.addTab('inicio', true);
handoffSandbox.document.addTab('views', false);
handoffSandbox.SQX.edgeFactory = { getState: () => ({ experienceMode: 'advanced' }) };
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
  'vc-guide-title',
  'vc-guide-source',
  'vc-guide-purpose',
  'vc-guide-when',
  'vc-guide-next',
  'vc-guide-tags',
  'vc-guide-config',
  'vc-summary-view',
  'vc-summary-oos',
  'vc-summary-sample',
  'vc-summary-order',
  'vc-summary-total',
].forEach(id => handoffSandbox.document.add(new Element(id)));
handoffSandbox.document.getElementById('vc-include-total').checked = true;
handoffSandbox.document.getElementById('vc-group-mode').value = 'by_year';
handoffSandbox.SQX.viewCreator.openHandoff({
  preset: 'sqx-edge-correlation-review',
  viewName: 'SQX EDGE CORRELATION REVIEW',
  yearCount: 1,
  sampleStart: 21,
  includeTotal: false,
  groupMode: 'plain',
});
assert.ok(handoffSandbox.document.getElementById('tab-btn-views').classList.contains('active'));
assert.equal(handoffSandbox.document.getElementById('vc-view-name').value, 'SQX EDGE CORRELATION REVIEW');
assert.equal(handoffSandbox.document.getElementById('vc-year-count').value, 1);
assert.equal(handoffSandbox.document.getElementById('vc-group-mode').value, 'plain');
assert.equal(handoffSandbox.document.getElementById('vc-include-total').checked, false);
assert.equal(Number(handoffSandbox.document.getElementById('vc-column-count').textContent), 17);
assert.match(handoffSandbox.document.getElementById('vc-status').textContent, /Handoff cargado/);

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
  'vc-template-list',
  'vc-template-count',
  'vc-guide-title',
  'vc-guide-source',
  'vc-guide-purpose',
  'vc-guide-when',
  'vc-guide-next',
  'vc-guide-tags',
  'vc-guide-config',
  'vc-summary-view',
  'vc-summary-oos',
  'vc-summary-sample',
  'vc-summary-order',
  'vc-summary-total',
].forEach(id => templateSandbox.document.add(new Element(id)));
templateSandbox.document.getElementById('vc-include-total').checked = true;
templateSandbox.document.getElementById('vc-group-mode').value = 'by_year';
const loadedTemplate = templateSandbox.SQX.viewCreator.loadBuyerReadyTemplate('sqx-edge-correlation-review');
assert.equal(loadedTemplate.name, 'SQX EDGE CORRELATION REVIEW');
assert.equal(templateSandbox.document.getElementById('vc-view-name').value, 'SQX EDGE CORRELATION REVIEW');
assert.equal(templateSandbox.document.getElementById('vc-group-mode').value, 'plain');
assert.equal(templateSandbox.document.getElementById('vc-include-total').checked, false);
assert.equal(Number(templateSandbox.document.getElementById('vc-column-count').textContent), 17);
assert.equal(templateSandbox.document.getElementById('vc-guide-title').textContent, 'SQX EDGE CORRELATION REVIEW');
assert.match(templateSandbox.document.getElementById('vc-guide-next').textContent, /Template Maker/i);
assert.equal(templateSandbox.document.getElementById('vc-summary-view').textContent, 'SQX EDGE CORRELATION REVIEW');
assert.match(templateSandbox.document.getElementById('vc-summary-oos').textContent, /1/);
const savedTemplate = templateSandbox.SQX.viewCreator.saveBuyerReadyTemplate('sqx-edge-correlation-review');
assert.equal(savedTemplate.id, 'buyer-sqx-edge-correlation-review');
assert.equal(templateSandbox.SQX.viewCreator.getSavedPresets().length, 1);
templateSandbox.SQX.viewCreator.renderBuyerReadyTemplates();
const renderedTemplates = templateSandbox.document.getElementById('vc-template-list').innerHTML;
assert.ok(renderedTemplates.includes('Usar esta view'));
assert.ok(renderedTemplates.includes('views-template-select'));
assert.ok(renderedTemplates.includes('data-vc-template-card'));
assert.ok(renderedTemplates.includes('CORR1'));
assert.ok(renderedTemplates.includes('Decision'));
assert.ok(!renderedTemplates.includes('Guardar como preset'));
assert.ok(!renderedTemplates.includes('EGT Core'));
assert.ok(!renderedTemplates.includes('CVC Decision Cert'));
assert.ok(!renderedTemplates.includes('Full audit'));

console.log('view creator contracts ok');

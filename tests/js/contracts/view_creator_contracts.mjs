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
assert.ok(html.includes('id="vc-template-list"'), 'missing buyer-ready template list');
assert.ok(html.includes('views-guide-flow'), 'missing guided SQX Views flow');
assert.ok(html.includes('Elige la view que necesitas'), 'missing guided view choice step');
assert.ok(html.includes('Revisa la configuración'), 'missing guided configuration step');
assert.ok(html.includes('Comprueba la vista'), 'missing guided preview step');
assert.ok(html.includes('Exporta e importa en SQX'), 'missing guided export step');
assert.ok(html.includes('id="vc-active-guide"'), 'missing active view guide');
assert.ok(html.includes('id="vc-guide-title"'), 'missing active guide title');
assert.ok(html.includes('id="vc-summary-view"'), 'missing guided config summary');
assert.ok(html.includes('id="vc-advanced-config"'), 'missing collapsed advanced config');
assert.ok(html.includes('id="vc-metrics-details"'), 'missing collapsed advanced metric editor');
assert.ok(html.includes('<span>Paso 3</span>'), 'preview step should keep the same visual hierarchy as other steps');
assert.ok(html.includes('<strong>Comprueba la vista</strong>'), 'preview step title should be fixed and highlighted');
assert.ok(html.includes('class="views-preview-subtitle"'), 'preview selected view should render as subtitle');
assert.ok(!html.includes('Paso 3 · Comprueba la vista'), 'preview step should not merge step label and title');
assert.ok(html.includes('Ajustes avanzados'), 'missing advanced settings disclosure');
assert.ok(html.includes('Editar métricas avanzadas'), 'missing advanced metrics disclosure');
assert.ok(html.includes('Descargar .vw'), 'missing primary .vw CTA');
assert.ok(!html.includes('id="vc-saved-details"'), 'custom presets KPI should not render in SQX Views');
assert.ok(!html.includes('id="vc-advanced-actions"'), 'advanced actions KPI should not render in SQX Views');
assert.ok(!html.includes('Guardar como preset'), 'guided cards should not expose preset saving');
assert.ok(!html.includes('sampleType=127'), 'UI should explain total consolidated without raw sampleType 127');
assert.ok(!html.includes('id="vc-profile-list"'), 'buyer profile packs should not render as visible KPI');
assert.ok(!html.includes('id="vc-workflow-pack-list"'), 'validation workflow packs should not render as visible KPI');
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
let remotePresetPayload = null;
SQX.remoteState = {
  bootstrap: () => Promise.resolve({ ok: true }),
  saveNow: (payload, source) => {
    remotePresetPayload = { payload, source };
    return Promise.resolve({ ok: true });
  },
};
viewCreator.setSavedPresets([{ id: 'risk-view', name: 'Risk View', config: savedConfig }]);
await Promise.resolve();
await Promise.resolve();
assert.equal(viewCreator.getSavedPresets().length, 1);
assert.equal(viewCreator.getSavedPresets()[0].config.yearCount, 5);
assert.equal(remotePresetPayload.source, 'sqx-views-presets');
assert.equal(remotePresetPayload.payload.sqx_view_creator_presets_v1[0].id, 'risk-view');
assert.equal(viewCreator.packageType, 'sqx-edge.view-presets');
assert.equal(viewCreator.packageVersion, 1);

const buyerTemplates = viewCreator.buyerReadyTemplates();
assert.equal(buyerTemplates.length, 6);
assert.ok(buyerTemplates.some(template => template.id === 'egt-first-review' && template.name === 'EGT Core' && template.priority === 'obligatoria'));
assert.ok(buyerTemplates.some(template => template.id === 'robustness-pack-screen' && template.name === 'Robustez' && template.priority === 'obligatoria'));
assert.ok(buyerTemplates.some(template => template.id === 'template-maker-cert' && template.name === 'Template Maker Cert' && template.priority === 'obligatoria'));
assert.ok(buyerTemplates.some(template => template.id === 'cvc-decision-cert' && template.name === 'CVC Decision Cert' && template.priority === 'obligatoria'));
assert.ok(buyerTemplates.some(template => template.id === 'risk-capital-review' && template.name === 'Risk' && template.priority === 'recomendable'));
assert.ok(buyerTemplates.some(template => template.id === 'full-audit-handoff' && template.name === 'Full audit' && template.priority === 'recomendable'));
assert.ok(buyerTemplates.some(template => template.id === 'full-audit-handoff' && template.config.groupMode === 'by_metric'));
assert.ok(buyerTemplates.every(template => template.config.metrics.length > 0));
assert.ok(buyerTemplates.every(template => Array.isArray(template.metricTags) && template.metricTags.length >= 4));
assert.ok(buyerTemplates.every(template => template.objective && template.when && template.nextAction));
assert.ok(buyerTemplates.some(template => template.id === 'egt-first-review' && template.oosTag === '9oos' && template.oosOptions.includes(1) && template.oosOptions.includes(9)));
assert.ok(buyerTemplates.some(template => template.id === 'risk-capital-review' && template.oosTag === '7oos' && template.metricTags.includes('VaR')));
const templateMakerRequired = viewCreator.getTemplateMakerRequiredMetrics();
assert.ok(templateMakerRequired.includes('Net profit'));
assert.ok(templateMakerRequired.includes('CAGR/Max DD %'));
assert.ok(!templateMakerRequired.includes('Ret/DD Ratio'), 'Ret/DD should be derived by Template Maker, not required in exported CSV');
const cvcRequired = viewCreator.getCvcDecisionRequiredMetrics();
assert.ok(cvcRequired.includes('Avg. Bars in Trade'));
assert.ok(cvcRequired.includes('Avg. Trades Per Month'));
assert.ok(cvcRequired.includes('Entry indicators'));
const tmCert = buyerTemplates.find(template => template.id === 'template-maker-cert');
assert.ok(tmCert.config.metrics.some(metric => metric.className === 'NetProfit'));
assert.ok(tmCert.config.metrics.some(metric => metric.className === 'AnnualPctReturnDDRatio'));
assert.ok(tmCert.metricTags.includes('Ret/DD derivado'));
const templateMakerCertXml = viewCreator.buildTemplateMakerCertView();
assert.ok(templateMakerCertXml.includes('name="Template Maker Cert"'));
assert.equal((templateMakerCertXml.match(/<Column /g) || []).length, 133, 'Template Maker Cert helper should build a real SQX view, not an empty shell');
assert.ok(templateMakerCertXml.includes('class="NetProfit" name="Net profit" sampleType="127"'));
assert.ok(templateMakerCertXml.includes('class="WinningPct" name="Winning Percent" sampleType="29"'));
const cvcCert = buyerTemplates.find(template => template.id === 'cvc-decision-cert');
assert.ok(cvcCert.config.metrics.some(metric => metric.className === 'AvgBarsInTrade'));
assert.ok(cvcCert.config.metrics.some(metric => metric.className === 'AvgTradesPerMonth'));
assert.ok(cvcCert.config.metrics.some(metric => metric.className === 'EntryIndicators'));
const cvcDecisionCertXml = viewCreator.buildCvcDecisionCertView();
assert.ok(cvcDecisionCertXml.includes('name="CVC Decision Cert"'));
assert.ok((cvcDecisionCertXml.match(/<Column /g) || []).length > 0, 'CVC Decision Cert helper should build real columns');
const buyerPack = viewCreator.buildBuyerReadyTemplatePack();
assert.equal(buyerPack.type, 'sqx-edge.view-presets');
assert.equal(buyerPack.presets.length, 6);
assert.ok(buyerPack.presets.some(preset => preset.id === 'buyer-template-maker-cert'));
assert.ok(buyerPack.presets.some(preset => preset.id === 'buyer-cvc-decision-cert'));
assert.ok(buyerPack.presets.some(preset => preset.id === 'buyer-risk-capital-review'));
assert.equal(viewCreator.buyerProfilePacks, undefined);
assert.equal(viewCreator.validationWorkflowPacks, undefined);
assert.equal(viewCreator.buildBuyerProfilePack, undefined);
assert.equal(viewCreator.buildValidationWorkflowPack, undefined);
assert.equal(viewCreator.renderBuyerProfilePacks, undefined);
assert.equal(viewCreator.renderValidationWorkflowPacks, undefined);

const presetPack = viewCreator.buildPresetPackage();
assert.equal(presetPack.type, 'sqx-edge.view-presets');
assert.equal(presetPack.presets.length, 1);
assert.equal(presetPack.presets[0].id, 'risk-view');

const importPayload = JSON.stringify({
  type: 'sqx-edge.view-presets',
  version: 1,
  presets: [
    {
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
    },
    {
      id: 'audit-preview',
      name: 'Audit Preview',
      config: {
        viewName: 'Audit Preview',
        yearCount: 4,
        sampleStart: 24,
        includeTotal: false,
        groupMode: 'by_metric',
        metrics: [
          { className: 'Symbol', annual: false },
          { className: 'DrawdownPct', annual: true },
        ],
      },
    },
  ],
});
const preview = viewCreator.presetImportPreviewFromText(importPayload);
assert.equal(preview.incomingCount, 2);
assert.equal(preview.duplicateCount, 1);
assert.equal(preview.newCount, 1);
assert.equal(preview.metricClassCount, 3);
assert.match(viewCreator.presetImportPreviewSummary(preview), /2 presets · 1 nuevos · 1 reemplazos/);
assert.match(viewCreator.presetImportPreviewHtml(preview), /views-import-preview-row/);
assert.match(viewCreator.presetImportPreviewHtml(preview), /reemplaza/);
const importResult = viewCreator.importPresetPackageFromText(importPayload);
assert.equal(importResult.imported, 2);
assert.equal(viewCreator.getSavedPresets().length, 2);
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
const loadedTemplate = templateSandbox.SQX.viewCreator.loadBuyerReadyTemplate('risk-capital-review');
assert.equal(loadedTemplate.name, 'Risk');
assert.equal(templateSandbox.document.getElementById('vc-view-name').value, 'Risk');
assert.ok(Number(templateSandbox.document.getElementById('vc-column-count').textContent) > 64);
assert.equal(templateSandbox.document.getElementById('vc-guide-title').textContent, 'Risk');
assert.match(templateSandbox.document.getElementById('vc-guide-next').textContent, /riesgo|perfil objetivo/i);
assert.equal(templateSandbox.document.getElementById('vc-summary-view').textContent, 'Risk');
assert.match(templateSandbox.document.getElementById('vc-summary-oos').textContent, /7/);
const savedTemplate = templateSandbox.SQX.viewCreator.saveBuyerReadyTemplate('risk-capital-review');
assert.equal(savedTemplate.id, 'buyer-risk-capital-review');
assert.equal(templateSandbox.SQX.viewCreator.getSavedPresets().length, 1);
templateSandbox.SQX.viewCreator.renderBuyerReadyTemplates();
const renderedTemplates = templateSandbox.document.getElementById('vc-template-list').innerHTML;
assert.ok(renderedTemplates.includes('Usar esta view'));
assert.ok(renderedTemplates.includes('views-template-select'));
assert.ok(renderedTemplates.includes('data-vc-template-card'));
assert.ok(!renderedTemplates.includes('Guardar como preset'));
assert.ok(renderedTemplates.includes('9oos'));
assert.ok(renderedTemplates.includes('7oos'));
assert.ok(renderedTemplates.includes('VaR'));
assert.ok(renderedTemplates.includes('TICK REAL'));
assert.ok(!renderedTemplates.includes('>free<'));
assert.ok(!renderedTemplates.includes('>pro<'));
assert.ok(!renderedTemplates.includes('s21..'));
assert.ok(!renderedTemplates.includes('s23..'));

console.log('view creator contracts ok');

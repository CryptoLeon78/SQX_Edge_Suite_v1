import fs from 'node:fs';
import path from 'node:path';
import { assert, Element, createLoadedSandbox, repoRoot } from './harness.mjs';

const html = fs.readFileSync(path.join(repoRoot, 'app/SQX_Dashboard_v6.html'), 'utf8');
const dashboardCss = fs.readFileSync(path.join(repoRoot, 'app/css/dashboard.css'), 'utf8');

assert.ok(html.includes('id="tab-projectgen"'), 'Project Generator tab panel should render');
assert.ok(html.includes('pg-guide-flow'), 'Project Generator should expose guided step flow');
assert.ok(html.includes('API local'), 'Project Generator should explain API local step');
assert.ok(html.includes('Configura SQX'), 'Project Generator should expose SQX configuration step');
assert.ok(html.includes('Elige generación'), 'Project Generator should expose generation choice step');
assert.ok(html.includes('Genera y revisa'), 'Project Generator should expose generation review step');
assert.ok(html.includes('PASO 5'), 'Project Generator should expose result/log step');
assert.ok(html.includes('Plan Mining'), 'Project Generator should clarify Plan Mining path');
assert.ok(html.includes('Custom libre'), 'Project Generator should preserve custom generation path');
assert.equal((html.match(/<details class="pg-step-panel/g) || []).length, 5, 'Project Generator should render 5 collapsible step panels');
assert.ok(html.includes('pg-step-summary'), 'Project Generator steps should use summary headers');
assert.doesNotMatch(html, /<details class="pg-step-panel[^>]*\sopen\b/, 'Project Generator steps should start closed by default');
assert.ok(html.includes('id="pg-mode-methodological"'), 'Project Generator should expose methodological generation mode');
assert.ok(html.includes('id="pg-mode-manual"'), 'Project Generator should expose manual generation mode');
assert.ok(html.includes('id="pg-mode-methodological-panel"'), 'Project Generator should render methodological workspace');
assert.ok(html.includes('id="pg-mode-manual-panel"'), 'Project Generator should render manual workspace');
assert.ok(html.includes('id="pg-mode-placeholder"'), 'Project Generator should render an empty mode placeholder');
assert.ok(html.includes('id="pg-open-output"'), 'Project Generator should keep output folder action inside generation step');
assert.ok(html.includes('id="pg-custom-generate"'), 'Project Generator should keep custom generate action');
assert.ok(html.indexOf('id="pg-custom-generate"') > html.indexOf('id="pg-mode-manual-panel"'), 'Custom libre should live inside the manual generation workspace');
assert.ok(!html.includes('id="pg-gen-all-c1"'), 'Project Generator should remove Capa 1 bulk-all action');
assert.ok(!html.includes('id="pg-gen-all-c2"'), 'Project Generator should remove Capa 2 bulk-all action');
assert.doesNotMatch(html, /Generación masiva/, 'Project Generator should remove the visual bulk generation block');
assert.ok(html.includes('id="pg-generate-selected-c1"'), 'Project Generator should generate selected Plan Mining rows in Capa 1');
assert.ok(html.includes('id="pg-generate-selected-c2"'), 'Project Generator should generate selected Plan Mining rows in Capa 2');
assert.ok(html.includes('id="pg-capa2-bs"'), 'Project Generator should expose the real Capa 2 BlockSetting selector');
assert.ok(html.includes('id="pg-select-all-minings"'), 'Project Generator should allow selecting all Plan Mining rows');
assert.ok(html.includes('id="pg-custom-save-preset"'), 'Project Generator should keep custom preset save action');
assert.ok(html.includes('id="pg-custom-import-presets-file"'), 'Project Generator should keep preset pack import input');
assert.ok(html.includes('id="pg-aliases-suggest"'), 'Project Generator should keep alias suggestion action');
assert.ok(html.includes('id="cln-scan"'), 'Strategy Cleaner should remain available during Project Generator pass');
assert.ok(!html.includes('id="pg-custom-starter-list"'), 'retired starter profile list must not return');
assert.ok(!html.includes('id="pg-custom-family-list"'), 'retired objective family list must not return');
assert.ok(!html.includes('id="pg-buyer-handoff-card"'), 'retired buyer handoff card must not return');
assert.ok(!dashboardCss.includes('export-btn::before'), 'Export buttons must not render decorative pseudo-symbols');
assert.doesNotMatch(html, /↻|📂|📦/, 'Project Generator controls should avoid decorative symbols in button text');

const { SQX, document, sandbox } = createLoadedSandbox();
const PG = SQX.projectGenerator;

assert.equal(PG.escapeHtml('<x>'), '&lt;x&gt;');
assert.equal(PG.dom.escapeHtml('<x>'), '&lt;x&gt;');
[
  'pg-sqx-path', 'pg-sqx-db', 'pg-sqx-projects', 'pg-output-dir', 'pg-tpl-c1', 'pg-tpl-c2',
  'pg-custom-name', 'pg-custom-asset', 'pg-custom-tf', 'pg-custom-bs',
  'pg-custom-dir', 'pg-custom-capa', 'pg-custom-template', 'pg-custom-status'
].forEach(id => {
  document.add(new Element(id));
});
document.getElementById('pg-sqx-path').value = ' C:/SQX ';
document.getElementById('pg-sqx-db').value = ' C:/SQX/data.db ';
document.getElementById('pg-sqx-projects').value = ' C:/SQX/projects ';
document.getElementById('pg-output-dir').value = ' C:/out ';
document.getElementById('pg-tpl-c1').value = ' C1.cfx ';
document.getElementById('pg-tpl-c2').value = ' C2.cfx ';
const domConfig = PG.dom.readConfigInputs(document, { EURUSD: 'EURUSD_M1' });
assert.equal(domConfig.sqxPath, 'C:/SQX');
assert.equal(domConfig.assetAliases.EURUSD, 'EURUSD_M1');
PG.dom.writeConfigInputs(document, { sqx_path: 'D:/SQX', output_dir: 'D:/out' });
assert.equal(document.getElementById('pg-sqx-path').value, 'D:/SQX');
assert.equal(document.getElementById('pg-output-dir').value, 'D:/out');
PG.dom.applySqxFields(document, { sqxPath: 'E:/SQX', dataDb: 'E:/db', projectsDir: 'E:/projects' });
assert.equal(document.getElementById('pg-sqx-db').value, 'E:/db');
document.getElementById('pg-custom-name').value = ' Custom EURUSD H1 ';
document.getElementById('pg-custom-asset').value = ' eurusd ';
document.getElementById('pg-custom-tf').value = ' h1 ';
document.getElementById('pg-custom-bs').value = '';
document.getElementById('pg-custom-dir').value = 'both';
document.getElementById('pg-custom-capa').value = '2';
document.getElementById('pg-custom-template').value = ' C2.cfx ';
const customInputs = PG.dom.readCustomProjectInputs(document);
assert.equal(customInputs.asset, 'EURUSD');
assert.equal(customInputs.tf, 'H1');
assert.equal(customInputs.bs, 'BS_Custom');
assert.equal(customInputs.capa, 2);
assert.equal(customInputs.template, 'C2.cfx');
assert.equal(PG.dom.setCustomProjectStatus(document, { text: 'Generado', level: 'ok' }), true);
assert.equal(document.getElementById('pg-custom-status').textContent, 'Generado');
assert.equal(document.getElementById('pg-custom-status').classList.contains('is-ok'), true);
PG.dom.writeCustomProjectInputs(document, { name: 'Preset EURUSD', asset: 'GBPUSD', tf: 'M15', bs: 'BS_Momentum_v6', dir: 'short', capa: 2, template: 'Tpl.cfx' });
assert.equal(document.getElementById('pg-custom-asset').value, 'GBPUSD');
assert.equal(document.getElementById('pg-custom-dir').value, 'short');
[
  'pg-status-refresh', 'pg-settings-toggle', 'pg-settings-save', 'pg-settings-reload',
  'pg-onboarding-action', 'pg-onboarding-secondary', 'pg-onboarding-tertiary',
  'pg-autodetect', 'pg-aliases-suggest', 'pg-validate', 'pg-mode-methodological',
  'pg-mode-manual', 'pg-custom-generate', 'pg-custom-save-preset', 'pg-custom-load-preset',
  'pg-custom-delete-preset', 'pg-output-refresh', 'pg-open-output', 'pg-log-clear',
  'pg-custom-export-presets', 'pg-custom-import-presets', 'pg-custom-import-presets-file',
  'pg-select-all-minings', 'pg-clear-selected-minings', 'pg-generate-selected-c1', 'pg-generate-selected-c2',
  'pg-settings-body', 'pg-log'
].forEach(id => document.add(new Element(id)));
let checkHealthCalls = 0;
let generateSelectedCapa = 0;
let generationMode = '';
let selectedAllCalls = 0;
let clearSelectedCalls = 0;
let generateCustomCalls = 0;
let saveCustomPresetCalls = 0;
let loadCustomPresetCalls = 0;
let deleteCustomPresetCalls = 0;
let exportCustomPresetCalls = 0;
let openImportCustomPresetCalls = 0;
let importCustomPresetCalls = 0;
PG.bindings.bindProjectGeneratorEvents(document, {
  checkHealth: () => { checkHealthCalls++; },
  exportCustomPresets: () => { exportCustomPresetCalls++; },
  clearSelectedMinings: () => { clearSelectedCalls++; },
  generateCustom: () => { generateCustomCalls++; },
  generateSelected: capa => { generateSelectedCapa = capa; },
  importCustomPresets: () => { importCustomPresetCalls++; },
  saveCustomPreset: () => { saveCustomPresetCalls++; },
  loadCustomPreset: () => { loadCustomPresetCalls++; },
  deleteCustomPreset: () => { deleteCustomPresetCalls++; },
  openImportCustomPresets: () => { openImportCustomPresetCalls++; },
  selectAllMinings: () => { selectedAllCalls++; },
  setGenerationMode: mode => { generationMode = mode; },
  setSettingsOpen: open => { document.getElementById('pg-settings-body').style.display = open ? 'block' : 'none'; },
});
document.getElementById('pg-status-refresh').click();
document.getElementById('pg-mode-methodological').click();
document.getElementById('pg-select-all-minings').click();
document.getElementById('pg-clear-selected-minings').click();
document.getElementById('pg-generate-selected-c1').click();
document.getElementById('pg-custom-generate').click();
document.getElementById('pg-custom-save-preset').click();
document.getElementById('pg-custom-load-preset').click();
document.getElementById('pg-custom-delete-preset').click();
document.getElementById('pg-custom-export-presets').click();
document.getElementById('pg-custom-import-presets').click();
document.getElementById('pg-custom-import-presets-file').dispatch('change');
document.getElementById('pg-custom-asset').dispatch('input');
document.getElementById('pg-custom-dir').dispatch('change');
assert.equal(checkHealthCalls, 1);
assert.equal(generationMode, 'methodological');
assert.equal(generateSelectedCapa, 1);
assert.equal(selectedAllCalls, 1);
assert.equal(clearSelectedCalls, 1);
assert.equal(generateCustomCalls, 1);
assert.equal(saveCustomPresetCalls, 1);
assert.equal(loadCustomPresetCalls, 1);
assert.equal(deleteCustomPresetCalls, 1);
assert.equal(exportCustomPresetCalls, 1);
assert.equal(openImportCustomPresetCalls, 1);
assert.equal(importCustomPresetCalls, 1);
document.getElementById('pg-log').textContent = 'old';
document.getElementById('pg-log-clear').click();
assert.equal(document.getElementById('pg-log').textContent, '[esperando primera acción…]');
const pgApiState = PG.computeOnboardingState({
  apiBase: 'http://127.0.0.1:8765',
  connected: false,
  configState: {},
  healthMeta: {},
  minings: [],
  outputFiles: [],
});
assert.equal(pgApiState.completed, 0);
assert.equal(pgApiState.current.id, 'api');
assert.equal(pgApiState.tertiaryVisible, false);

const pgReadyState = PG.computeOnboardingState({
  apiBase: 'http://127.0.0.1:8765',
  connected: true,
  configState: { sqx_path: 'C:/SQX', sqx_data_db: 'C:/SQX/data.db' },
  healthMeta: {
    data_db_exists: true,
    output_dir: 'out',
    output_dir_exists: true,
    sqx_path: 'C:/SQX',
    sqx_path_set: true,
    templates_capa1_exists: true,
    templates_capa2_exists: true,
  },
  minings: [{ asset: 'EURUSD', tf: 'H1' }],
  outputFiles: [{ name: 'M01.cfx' }],
});
assert.equal(pgReadyState.completed, 4);
assert.equal(pgReadyState.current, null);
assert.equal(pgReadyState.tertiaryAction, 'refresh');

[
  'pg-onboarding-progress', 'pg-onboarding-title', 'pg-onboarding-desc',
  'pg-onboarding-bar', 'pg-onboarding-steps', 'pg-onboarding-action',
  'pg-onboarding-secondary', 'pg-onboarding-tertiary', 'pg-assistant-next',
  'pg-assistant-hint', 'pg-assistant-checks'
].forEach(id => document.add(new Element(id)));
assert.equal(PG.applyOnboardingState(pgReadyState, document), true);
assert.equal(document.getElementById('pg-onboarding-progress').textContent, '4/4');
assert.equal(document.getElementById('pg-onboarding-bar').style.width, '100%');
assert.equal(document.getElementById('pg-onboarding-tertiary').dataset.pgAssistantAction, 'refresh');
assert.match(document.getElementById('pg-onboarding-steps').innerHTML, /pg-step done/);

const prepared = PG.prepareRequestOptions({ body: { alpha: 1 }, headers: { Accept: 'application/json' } });
assert.equal(prepared.body, '{"alpha":1}');
assert.equal(prepared.headers['Content-Type'], 'application/json');
assert.equal(prepared.headers.Accept, 'application/json');

let fetchUrl = '';
let fetchOptions = null;
const jsonResult = await PG.fetchJson('http://api.local', '/health', { method: 'POST', body: { ok: true } }, async (url, options) => {
  fetchUrl = url;
  fetchOptions = options;
  return { ok: true, status: 200, text: async () => '{"ok":true,"version":"20"}' };
});
assert.equal(fetchUrl, 'http://api.local/health');
assert.equal(fetchOptions.body, '{"ok":true}');
assert.equal(jsonResult.version, '20');
await assert.rejects(
  () => PG.fetchJson('', '/bad', {}, async () => ({ ok: false, status: 500, text: async () => 'boom' })),
  /boom/
);

document.add(new Element('pg-status-banner', ['pg-status-loading']));
document.add(new Element('pg-status-title'));
document.add(new Element('pg-status-desc'));
assert.equal(PG.applyStatusBanner({ state: 'up', title: 'API OK', desc: 'Lista' }, document), true);
assert.equal(document.getElementById('pg-status-title').textContent, 'API OK');
assert.equal(document.getElementById('pg-status-desc').textContent, 'Lista');
assert.equal(document.getElementById('pg-status-banner').classList.contains('pg-status-up'), true);
assert.equal(document.getElementById('pg-status-banner').classList.contains('pg-status-loading'), false);

const pgAssets = PG.uniqueAssets([{ asset: 'GBPUSD' }, { asset: 'EURUSD' }, { asset: 'GBPUSD' }]);
assert.deepEqual(pgAssets, ['EURUSD', 'GBPUSD']);
assert.equal(PG.directionClass('short'), 'short');
assert.equal(PG.directionLabel('both'), 'L+S');
const aliasHtml = PG.aliasTableHtml([{ asset: 'EURUSD' }], { EURUSD: 'EURUSD_M1' });
assert.match(aliasHtml, /data-pg-alias="EURUSD"/);
assert.match(aliasHtml, /value="EURUSD_M1"/);
assert.match(PG.aliasTableHtml([], {}), /esperando minings/);

const aliasSuggestions = [
  { instrument: 'EURUSD_M1', score: 96, description: 'Major', broker_id: 10 },
  { instrument: 'EURUSD_M5', score: 88, description: '', broker_id: 11 },
  { instrument: 'EURUSD_H1', score: 82, description: 'Alt', broker_id: 12 },
  { instrument: 'EURUSD_H4', score: 81, description: 'Alt', broker_id: 13 },
  { instrument: 'EURUSD_D1', score: 80, description: 'Alt', broker_id: 14 },
  { instrument: 'EURUSD_W1', score: 79, description: 'Ignored', broker_id: 15 },
];
assert.equal(PG.aliasTopSuggestions(aliasSuggestions, 5).length, 5);
assert.match(PG.aliasSuggestionPrompt('EURUSD', aliasSuggestions), /1\. EURUSD_M1 \[96%\]/);
assert.doesNotMatch(PG.aliasSuggestionPrompt('EURUSD', aliasSuggestions), /EURUSD_W1/);
assert.equal(PG.aliasChoiceValue('2', aliasSuggestions), 'EURUSD_M5');
assert.equal(PG.aliasChoiceValue(' CUSTOM ', aliasSuggestions), 'CUSTOM');
assert.equal(PG.aliasChoiceValue('', aliasSuggestions), '');
assert.equal(PG.aliasSuggestionEmptyMessage('GBPUSD'), 'Sin sugerencias para GBPUSD en data.db');
assert.equal(PG.aliasProposedMessage('EURUSD', 'EURUSD_M1'), 'Alias propuesto: EURUSD → EURUSD_M1 (pulsa Guardar config)');
assert.equal(PG.aliasAutoSuggestStartMessage(3), 'Auto-sugiriendo para 3 assets…');
assert.equal(PG.aliasAutoSuggestResult(1).level, 'ok');
assert.equal(PG.aliasAutoSuggestResult(0).level, 'info');

const miningHtml = PG.miningRowsHtml([{
  num: 7,
  asset: 'EURUSD',
  tf: 'H1',
  bs: 'BS_Tendencia_v6',
  dir: 'long',
  _info: { source: 'db', instrument: 'EURUSD_M1', spread: 1.2, swap_long: -1, swap_short: 0.5 },
}]);
assert.doesNotMatch(miningHtml, /data-pg-gen=/);
assert.doesNotMatch(miningHtml, /&#128202;|&#128203;|📦/);
assert.match(miningHtml, /pgm-dir long/);
assert.match(miningHtml, /EURUSD_M1/);
const outputHtml = PG.outputListHtml([{ name: 'M07.cfx', size_kb: 12, mtime: 1770000000 }]);
assert.match(outputHtml, /M07\.cfx/);
assert.match(outputHtml, /12 KB/);
assert.match(PG.outputListHtml([]), /No hay \.cfx/);
assert.equal(PG.miningsCountLabel(4), '4 minings');
assert.equal(PG.selectedMiningCountLabel(1), '1 seleccionado');
assert.equal(PG.selectedMiningCountLabel(2), '2 seleccionados');
assert.equal(PG.bulkGenerateLabel(4), '4 minings · Capa 1 + Capa 2');
assert.equal(PG.normalizeDirection('L'), 'long');
assert.equal(PG.directionLabel('S'), 'SHORT');
assert.match(miningHtml, /BS_Tendencia_v6/);
const miningRowsHtml = PG.miningRowsHtml([{ num: 9, asset: 'XAUUSD', tf: 'H1', bs: 'BS_Tendencia_v6', dir: 'L', _user: true, source: 'manual' }], { 9: true });
assert.match(miningRowsHtml, /data-pg-mining-check="9" checked/);
assert.match(miningRowsHtml, /USER/);
assert.match(PG.miningRowsHtml([], {}), /Plan Mining vac/);
const enrichedMinings = await PG.enrichMiningsWithSymbolInfo(
  [{ asset: 'EURUSD' }, { asset: 'FAIL' }],
  async asset => {
    if (asset === 'FAIL') throw new Error('missing');
    return { instrument: 'EURUSD_M1' };
  }
);
assert.equal(enrichedMinings[0]._info.instrument, 'EURUSD_M1');
assert.equal(enrichedMinings[1]._info, null);
const outputState = PG.outputState({ output_dir: 'C:/out', files: [{ name: 'A.cfx', size_kb: 1, mtime: 1770000000 }] });
assert.equal(outputState.outputDir, 'C:/out');
assert.equal(outputState.countLabel, '1 archivos');
assert.match(outputState.html, /A\.cfx/);
assert.equal(PG.openOutputDisconnectedStatus().logText, 'Backend desconectado');
assert.equal(PG.openOutputSuccessStatus('C:/out').traceDetail, 'C:/out');
assert.equal(PG.openOutputErrorStatus('denied').logText, 'Error abrir carpeta: denied');
assert.match(PG.messageHtml('Error <x>', 'error'), /&lt;x&gt;/);

assert.equal(PG.generateOneStartMessage(3, 2), 'Generando Mining 3 · Capa 2…');
const generateOneOk = PG.generateOneResult({ ok: true, filename: 'M03.cfx' }, 3, 2);
assert.equal(generateOneOk.logText, '✓ M03.cfx');
assert.equal(generateOneOk.traceDetail, 'Mining 3 · Capa 2 · M03.cfx');
assert.equal(PG.generateOneResult({ ok: false, error: 'bad template' }, 3, 1).traceLevel, 'err');
assert.equal(PG.generateCustomStartMessage({ asset: 'EURUSD', tf: 'H1', capa: 2 }), 'Generando custom EURUSD H1 · Capa 2…');
assert.equal(PG.generateCustomMissingStatus().level, 'err');
const generateCustomOk = PG.generateCustomResult({ ok: true, filename: 'Custom_EURUSD_H1_Capa1.cfx', project_name: 'Custom_EURUSD_H1', capa: 1 }, { asset: 'EURUSD' });
assert.equal(generateCustomOk.text, 'Generado: Custom_EURUSD_H1_Capa1.cfx');
assert.equal(generateCustomOk.traceTitle, 'Custom libre generado');
assert.equal(PG.generateCustomResult({ ok: false, error: 'missing asset' }, {}).level, 'err');
assert.equal(PG.generateErrorResult('offline').logText, '✗ Error: offline');
assert.equal(PG.generateAllConfirmMessage(1, 12), '¿Generar 12 minings en Capa 1? Sobrescribe los existentes en output/.');
assert.equal(PG.generateAllConfirmMessage(2, 0), '¿Generar todos los minings en Capa 2? Sobrescribe los existentes en output/.');
assert.equal(PG.generateAllStartMessage(2), 'Generando TODOS · Capa 2…');
assert.equal(PG.generateAllResultSummary({ ok_count: 2, fail_count: 1 }).level, 'err');
assert.equal(PG.generateAllTrace(2, { ok_count: 2, fail_count: 0 }).detail, 'Capa 2 · OK 2 · FAIL 0');
const generateAllLines = PG.generateAllResultLines([
  { ok: true, mining: 3, filename: 'M03.cfx' },
  { ok: false, mining: 12, error: 'bad db' },
]);
assert.equal(generateAllLines[0].text, '  ✓ M03 → M03.cfx');
assert.equal(generateAllLines[1].text, '  ✗ M12 → bad db');

const configBody = PG.configSaveBody({
  sqxPath: 'C:/SQX',
  sqxDataDb: 'C:/SQX/data.db',
  sqxProjectsDir: 'C:/SQX/projects',
  outputDir: 'C:/out',
  templateCapa1: 'C1.cfx',
  templateCapa2: 'C2.cfx',
  assetAliases: { EURUSD: 'EURUSD_M1' },
});
assert.equal(configBody.sqx_path, 'C:/SQX');
assert.equal(configBody.sqx_data_db, 'C:/SQX/data.db');
assert.equal(configBody.asset_aliases.EURUSD, 'EURUSD_M1');
const configStatus = PG.configSaveStatus({ updated_keys: ['sqx_path', 'output_dir'] });
assert.equal(configStatus.message, '✓ Guardado: sqx_path, output_dir');
assert.equal(configStatus.logText, 'Config actualizada (2 keys)');
assert.equal(configStatus.traceDetail, 'sqx_path, output_dir');
assert.equal(PG.configSaveError('disk full').message, '✗ Error: disk full');
assert.equal(PG.customPresetIdFromName('EURUSD H1 Long'), 'eurusd-h1-long');
const normalizedCustom = PG.normalizeCustomProjectConfig({ asset: ' eurusd ', tf: ' h1 ', bs: '', dir: 'both', capa: 2 });
assert.equal(normalizedCustom.asset, 'EURUSD');
assert.equal(normalizedCustom.bs, 'BS_Custom');
assert.equal(normalizedCustom.dir, 'both');
const savedCustom = PG.upsertCustomProjectPreset(normalizedCustom, 'EURUSD H1 Core', sandbox.localStorage);
assert.equal(savedCustom.ok, true);
assert.equal(savedCustom.preset.id, 'eurusd-h1-core');
assert.equal(PG.getCustomProjectPresets(sandbox.localStorage).length, 1);
const customPack = PG.buildCustomProjectPresetPackage(null, sandbox.localStorage);
assert.equal(customPack.type, 'sqx-edge.project-generator-custom-presets');
assert.equal(customPack.version, 1);
assert.equal(customPack.presets.length, 1);
const customImport = PG.importCustomProjectPresetPackageFromText(JSON.stringify({
  type: 'sqx-edge.project-generator-custom-presets',
  version: 1,
  presets: [{
    id: 'gbpusd-m15-short',
    name: 'GBPUSD M15 Short',
    config: { asset: 'gbpusd', tf: 'm15', bs: '', dir: 'short', capa: 2, template: 'Tpl.cfx' },
  }],
}), sandbox.localStorage);
assert.equal(customImport.imported, 1);
assert.equal(PG.getCustomProjectPresets(sandbox.localStorage).length, 2);
assert.equal(PG.findCustomProjectPreset('gbpusd-m15-short', sandbox.localStorage).config.asset, 'GBPUSD');
const importPreview = PG.customProjectPresetImportPreviewFromText(JSON.stringify({
  type: 'sqx-edge.project-generator-custom-presets',
  version: 1,
  presets: [
    {
      id: 'gbpusd-m15-short',
      name: 'GBPUSD M15 Short',
      config: { asset: 'gbpusd', tf: 'm15', bs: '', dir: 'short', capa: 2, template: 'Tpl.cfx' },
    },
    {
      id: 'xauusd-h1-risk',
      name: 'XAUUSD H1 Risk',
      config: { asset: 'xauusd', tf: 'h1', bs: 'BS_Gold', dir: 'both', capa: 2, template: '' },
    },
  ],
}), sandbox.localStorage);
assert.equal(importPreview.incomingCount, 2);
assert.equal(importPreview.duplicateCount, 1);
assert.equal(importPreview.newCount, 1);
assert.equal(JSON.stringify(importPreview.assets), JSON.stringify(['GBPUSD', 'XAUUSD']));
assert.match(PG.customProjectPresetImportPreviewSummary(importPreview), /2 presets · 1 nuevos · 1 reemplazos/);
assert.match(PG.customProjectPresetImportPreviewHtml(importPreview), /pg-import-preview-row/);
assert.match(PG.customProjectPresetImportPreviewHtml(importPreview), /reemplaza/);
assert.match(PG.customProjectPresetOptionsHtml(savedCustom.presets), /EURUSD H1 Core/);
assert.equal(PG.customProjectPresetCountLabel(1), '1 guardado');
assert.equal(PG.findCustomProjectPreset('eurusd-h1-core', sandbox.localStorage).config.asset, 'EURUSD');
assert.equal(PG.getCustomStarterProfiles, undefined);
assert.equal(PG.buildCustomStarterProfilePack, undefined);
assert.equal(PG.getCustomProfileFamilies, undefined);
assert.equal(PG.buildCustomProfileFamilyPack, undefined);
assert.equal(PG.normalizeBuyerCfxHandoffInput, undefined);
assert.equal(PG.buyerCfxHandoffMarkdown, undefined);
assert.equal(PG.deleteCustomProjectPreset('eurusd-h1-core', sandbox.localStorage).deleted, true);
assert.equal(PG.deleteCustomProjectPreset('gbpusd-m15-short', sandbox.localStorage).deleted, true);
assert.equal(PG.getCustomProjectPresets(sandbox.localStorage).length, 0);
assert.equal(PG.upsertCustomProjectPreset({ asset: '', tf: '' }, '', sandbox.localStorage).ok, false);
const candidateFields = PG.sqxCandidateFields({ sqx_path: 'C:/SQX', data_db: 'db', projects_dir: 'projects' });
assert.equal(candidateFields.sqxPath, 'C:/SQX');
assert.equal(candidateFields.dataDb, 'db');
assert.equal(candidateFields.projectsDir, 'projects');
const candidateStatus = PG.sqxCandidateSelectedStatus({ sqx_path: 'C:/SQX' });
assert.equal(candidateStatus.logText, 'Path SQX seleccionado: C:/SQX (pulsa Guardar config)');
assert.equal(candidateStatus.traceDetail, 'C:/SQX');
assert.match(PG.validateSqxMissingPathHtml(), /Pon primero/);
const validationResult = { valid: true, resolved: { data_db: 'C:/SQX/data.db', projects_dir: 'C:/SQX/projects' } };
assert.equal(PG.validateSqxShouldApply(validationResult), true);
assert.equal(PG.validateSqxShouldApply({ valid: true, resolved: {} }), false);
assert.equal(PG.validateSqxResolvedFields(validationResult).projectsDir, 'C:/SQX/projects');
assert.equal(PG.validateSqxTrace('C:/SQX').title, 'Validacion SQX correcta');

assert.match(PG.sqxNotFoundHtml(), /No se encontro/);
assert.match(PG.sqxAppliedHtml(), /Aplicado/);
assert.match(PG.autodetectCandidatesHtml({
  found: 1,
  candidates: [{ version: '1.0', has_exe: true, sqx_path: 'C:/SQX', data_db: 'C:/SQX/user/data/data.db' }],
}), /pg-use-btn/);
assert.match(PG.validateSqxPathHtml({
  valid: true,
  checks: { base_exists: true, data_db_exists: true, projects_exists: true, exe_exists: true },
}), /Path valido/);

const cleanerHtml = PG.cleanerTableHtml([{
  path: 'C:/SQX/A&B.sqx',
  name: 'A&B.sqx',
  asset: 'EURUSD',
  timeframe: 'H1',
  direction: 'long',
  exit_after_bars_count: 2,
  fitness_id: 'F1',
  size_kb: 34,
}], { 'C:/SQX/A&B.sqx': true });
assert.match(cleanerHtml, /cln-row-check/);
assert.match(cleanerHtml, /checked/);
assert.match(cleanerHtml, /A&amp;B\.sqx/);
assert.match(cleanerHtml, /cv-num warn/);
assert.equal(PG.cleanerTableHtml([], {}), '');
assert.equal(PG.cleanerMissingDirStatus().text, 'Pon una carpeta primero.');
assert.equal(PG.cleanerScanningStatus().color, 'var(--text2)');
assert.equal(PG.cleanerErrorStatus('boom').text, '✗ boom');
assert.equal(PG.cleanerNoSelectionStatus().level, 'err');
assert.equal(PG.cleanerNoActionStatus().text, 'Selecciona al menos una acción');
assert.equal(PG.cleanerProcessingStatus(2).text, 'Procesando 2 archivos...');
const cleanerOptions = PG.cleanerOptions({ removeExitBars: true, renameInstitutional: false, renamePattern: 'X' });
assert.equal(cleanerOptions.remove_exit_bars, true);
assert.equal(cleanerOptions.rename_institutional, false);
assert.equal(PG.cleanerHasAction(cleanerOptions), true);
assert.equal(PG.cleanerHasAction(PG.cleanerOptions({})), false);
assert.match(PG.cleanerConfirmMessage(2, cleanerOptions), /Eliminar ExitAfterBars/);
assert.equal(PG.cleanerResultSummary({ ok_count: 3, fail_count: 0 }), 'Resultado: 3 OK · 0 FAIL');
assert.equal(PG.cleanerResultLevel({ fail_count: 0 }), 'ok');
assert.equal(PG.cleanerResultLines([{ ok: true, path: 'C:/SQX/clean.sqx', actions: ['rename'] }])[0], 'OK clean.sqx - rename');
assert.equal(PG.cleanerResultTrace(2, { ok_count: 1, fail_count: 1 }).detail, '2 archivos · OK 1 · FAIL 1');
assert.equal(PG.cleanerProcessErrorTrace('bad').traceTitle, 'Error en limpieza SQX');
const selectedMap = PG.cleanerSelectedMap(['C:/SQX/a.sqx', 'C:/SQX/b.sqx']);
assert.equal(selectedMap['C:/SQX/a.sqx'], true);
assert.equal(PG.cleanerSelectedLabel(2), '2 seleccionadas');
assert.equal(PG.cleanerScanMessage({ ok: true, count: 2 }).actionsDisplay, 'block');
assert.equal(PG.cleanerScanMessage({ ok: true, count: 0 }).actionsDisplay, 'none');
assert.equal(PG.cleanerPreviewPattern(''), '{asset}_{tf}_{dir}_{id}');
assert.equal(PG.cleanerPreviewPattern(' {asset}_{id} '), '{asset}_{id}');
const previewLines = PG.cleanerPreviewLines([
  { current: 'old.sqx', new_name: 'new.sqx' },
  { path: 'bad.sqx', error: 'missing asset' },
]);
assert.equal(PG.cleanerPreviewHeader(previewLines), 'Preview rename para 2 archivos:');
assert.equal(previewLines[0].level, 'info');
assert.equal(previewLines[1].level, 'err');

console.log('project generator contracts ok');

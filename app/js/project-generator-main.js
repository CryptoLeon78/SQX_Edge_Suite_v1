// ============================================================
// PROJECT GENERATOR — Tab que consume el backend Python (F3 API)
// ============================================================
const SQX_PG_MODULE = (window.SQX && window.SQX.projectGenerator) || {};
const PG_API = (window.SQX_CONFIG && window.SQX_CONFIG.apiBase()) || '';
const PG_STATE = {
  aliases: {},
  config: {},
  connected: false,
  healthMeta: {},
  healthTimer: null,
  lastTraceState: '',
  minings: [],
  outputDir: '',
  outputFiles: [],
  planCount: 0,
};
const PG_ALIAS_MIN_SCORE = (window.SQX_CONFIG && window.SQX_CONFIG.value('projectGenerator.aliasSuggestMinScore', 80)) || 80;
const pgApiInline = document.getElementById('pg-api-base-inline');
if (pgApiInline && PG_API) pgApiInline.textContent = PG_API;

function pgEsc(value) {
  return SQX_PG_MODULE.escapeHtml
    ? SQX_PG_MODULE.escapeHtml(value)
    : String(value == null ? '' : value).replace(/[&<>"']/g, ch => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    }[ch]));
}

function pgLog(msg, level) {
  const log = document.getElementById('pg-log');
  if (!log) return;
  const t = new Date().toLocaleTimeString();
  const cls = level === 'ok' ? 'log-ok' : level === 'err' ? 'log-err' : 'log-info';
  if (log.textContent.trim() === '[esperando primera acción…]') log.textContent = '';
  log.append(document.createTextNode('[' + t + '] '));
  const span = document.createElement('span');
  span.className = cls;
  span.textContent = msg;
  log.append(span, document.createTextNode('\n'));
  log.scrollTop = log.scrollHeight;
}

function pgTrace(title, detail, level) {
  if (typeof window.addHomeTrace === 'function') {
    window.addHomeTrace(title, detail, level || 'info');
  }
}

function pgSetSettingsOpen(open) {
  const body = document.getElementById('pg-settings-body');
  const arrow = document.getElementById('pg-settings-arrow');
  if (!body || !arrow) return;
  const shouldOpen = !!open;
  body.style.display = shouldOpen ? 'block' : 'none';
  arrow.classList.toggle('closed', !shouldOpen);
}

function pgFocusSettingsField(id) {
  pgSetSettingsOpen(true);
  const target = document.getElementById(id);
  if (!target) return;
  target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  setTimeout(() => target.focus(), 90);
}

function pgDom(id) {
  return document.getElementById(id);
}

function pgInputValue(id) {
  return (pgDom(id) || {}).value || '';
}

function pgTrimmedInputValue(id) {
  return pgInputValue(id).trim();
}

function pgSetInputValue(id, value) {
  const input = pgDom(id);
  if (input) input.value = value || '';
}

function pgSetText(id, text) {
  const el = pgDom(id);
  if (el) el.textContent = text;
}

function pgSetHtml(id, html) {
  const el = pgDom(id);
  if (el) el.innerHTML = html;
  return el;
}

function pgReadConfigInputs() {
  return {
    sqxPath: pgTrimmedInputValue('pg-sqx-path'),
    sqxDataDb: pgTrimmedInputValue('pg-sqx-db'),
    sqxProjectsDir: pgTrimmedInputValue('pg-sqx-projects'),
    outputDir: pgTrimmedInputValue('pg-output-dir'),
    templateCapa1: pgTrimmedInputValue('pg-tpl-c1'),
    templateCapa2: pgTrimmedInputValue('pg-tpl-c2'),
    assetAliases: PG_STATE.aliases,
  };
}

function pgWriteConfigInputs(config) {
  const c = config || {};
  pgSetInputValue('pg-sqx-path', c.sqx_path);
  pgSetInputValue('pg-sqx-db', c.sqx_data_db);
  pgSetInputValue('pg-sqx-projects', c.sqx_projects_dir);
  pgSetInputValue('pg-output-dir', c.output_dir);
  pgSetInputValue('pg-tpl-c1', c.template_capa1);
  pgSetInputValue('pg-tpl-c2', c.template_capa2);
}

function pgApplySqxFields(fields) {
  pgSetInputValue('pg-sqx-path', fields.sqxPath);
  pgSetInputValue('pg-sqx-db', fields.dataDb);
  pgSetInputValue('pg-sqx-projects', fields.projectsDir);
}

function pgApplySqxCandidate(candidate, outputEl) {
  const fields = SQX_PG_MODULE.sqxCandidateFields(candidate);
  const status = SQX_PG_MODULE.sqxCandidateSelectedStatus(candidate);
  pgApplySqxFields(fields);
  pgLog(status.logText, status.logLevel);
  pgTrace(status.traceTitle, status.traceDetail, status.traceLevel);
  pgRenderOnboarding();
  if (outputEl) outputEl.innerHTML = SQX_PG_MODULE.sqxAppliedHtml();
}

function pgApplyValidatedSqxPath(path, response) {
  const fields = SQX_PG_MODULE.validateSqxResolvedFields(response);
  const trace = SQX_PG_MODULE.validateSqxTrace(path);
  pgSetInputValue('pg-sqx-db', fields.dataDb);
  pgSetInputValue('pg-sqx-projects', fields.projectsDir);
  pgTrace(trace.title, trace.detail, trace.level);
  pgRenderOnboarding();
}

function pgSetSettingsMessage(status) {
  const msg = pgDom('pg-settings-msg');
  if (!msg) return;
  msg.textContent = status.message;
  if (Object.prototype.hasOwnProperty.call(status, 'color')) msg.style.color = status.color;
}

function pgUpdateMiningSummary(count) {
  pgSetText('pg-minings-count', SQX_PG_MODULE.miningsCountLabel(count));
  pgSetText('pg-bulk-count', SQX_PG_MODULE.bulkGenerateLabel(count));
}

function pgRenderMiningsList(infos) {
  pgSetHtml('pg-minings-table', SQX_PG_MODULE.miningRowsHtml(infos));
  document.querySelectorAll('button[data-pg-gen]').forEach(btn => {
    btn.addEventListener('click', () => pgGenerateOne(parseInt(btn.dataset.pgGen,10), parseInt(btn.dataset.pgCapa,10)));
  });
}

function pgRenderOutputState(output) {
  pgSetText('pg-output-count', output.countLabel);
  pgSetHtml('pg-output-list', output.html);
}

function pgGetOnboardingState() {
  return SQX_PG_MODULE.computeOnboardingState({
    apiBase: PG_API,
    connected: PG_STATE.connected,
    configState: PG_STATE.config,
    dbInput: pgInputValue('pg-sqx-db'),
    healthMeta: PG_STATE.healthMeta,
    minings: PG_STATE.minings,
    outputDir: PG_STATE.outputDir,
    outputFiles: PG_STATE.outputFiles,
    sqxPathInput: pgInputValue('pg-sqx-path'),
  });
}

function pgRenderOnboarding() {
  const state = pgGetOnboardingState();
  if (SQX_PG_MODULE.applyOnboardingState) SQX_PG_MODULE.applyOnboardingState(state, document);
}

async function pgFetch(path, options) {
  return SQX_PG_MODULE.fetchJson(PG_API, path, options);
}

function pgSetStatus(state, title, desc, meta) {
  if (meta && Object.keys(meta).length) PG_STATE.healthMeta = meta;
  else if (state === 'down') PG_STATE.healthMeta = {};
  if (typeof window.updateHomeBackendStatus === 'function') {
    window.updateHomeBackendStatus(state, title, desc, meta || {});
  }
  if (state !== 'loading' && state !== PG_STATE.lastTraceState) {
    PG_STATE.lastTraceState = state;
    pgTrace(
      state === 'up' ? 'Backend conectado' : 'Backend desconectado',
      state === 'up' ? ((meta && meta.sqx_path) || 'API local operativa') : desc,
      state === 'up' ? 'ok' : 'err'
    );
  }
  SQX_PG_MODULE.applyStatusBanner({ state, title, desc }, document);
  pgRenderOnboarding();
}

async function pgCheckHealth() {
  pgSetStatus('loading', 'Comprobando…', 'GET ' + PG_API + '/health');
  try {
    const h = await pgFetch('/health');
    PG_STATE.connected = true;
    const tplOk = h.templates_capa1_exists && h.templates_capa2_exists;
    pgSetStatus('up',
      '🟢 Backend conectado · v' + h.version,
      'SQX path: ' + (h.sqx_path || '(no set)') + ' · Templates: ' + (tplOk ? 'C1+C2 OK' : '⚠ alguno falta'),
      h);
    await pgLoadAll();
  } catch(e) {
    PG_STATE.connected = false;
    pgSetStatus('down',
      '🔴 Backend desconectado',
      'Lanza "backend/sqx-edge-tool/run-web.bat" para arrancar la API local (' + PG_API + '). Detalle: ' + e.message,
      { error: e.message });
  }
}

async function pgLoadAll() {
  await Promise.all([pgLoadConfig(), pgLoadMinings(), pgLoadOutput()]);
}

async function pgLoadConfig() {
  try {
    const c = await pgFetch('/config');
    PG_STATE.config = c || {};
    pgWriteConfigInputs(c);
    PG_STATE.aliases = c.asset_aliases || {};
    pgRenderAliases();
    pgRenderOnboarding();
  } catch(e) { pgLog('Error cargando config: ' + e.message, 'err'); }
}

function pgRenderAliases() {
  const tbl = document.getElementById('pg-aliases-table');
  if (!tbl) return;
  pgFetch('/minings').then(minings => {
    tbl.innerHTML = SQX_PG_MODULE.aliasTableHtml(minings, PG_STATE.aliases);
    tbl.querySelectorAll('input[data-pg-alias]').forEach(inp => {
      inp.addEventListener('change', function(){
        const k = this.dataset.pgAlias;
        const v = this.value.trim();
        if (v) PG_STATE.aliases[k] = v;
        else delete PG_STATE.aliases[k];
      });
    });
    tbl.querySelectorAll('button[data-pg-suggest-asset]').forEach(btn => {
      btn.addEventListener('click', () => pgSuggestForAsset(btn.dataset.pgSuggestAsset));
    });
  }).catch(() => {
    tbl.innerHTML = SQX_PG_MODULE.aliasTableHtml([], PG_STATE.aliases);
  });
}

async function pgSuggestForAsset(asset) {
  try {
    const r = await pgFetch('/suggest-instruments/' + asset);
    if (!r.suggestions || !r.suggestions.length) {
      pgLog(SQX_PG_MODULE.aliasSuggestionEmptyMessage(asset), 'err');
      pgRenderOnboarding();
      return;
    }
    const choice = prompt(SQX_PG_MODULE.aliasSuggestionPrompt(asset, r.suggestions), '1');
    if (!choice) return;
    const chosen = SQX_PG_MODULE.aliasChoiceValue(choice, r.suggestions);
    if (!chosen) return;
    PG_STATE.aliases[asset] = chosen;
    document.querySelector('input[data-pg-alias="' + asset + '"]').value = chosen;
    pgLog(SQX_PG_MODULE.aliasProposedMessage(asset, chosen), 'info');
    pgTrace('Alias propuesto', asset + ' -> ' + chosen, 'info');
  } catch(e) { pgLog('Error sugiriendo: ' + e.message, 'err'); }
}

async function pgSuggestAll() {
  const inputs = document.querySelectorAll('input[data-pg-alias]');
  pgLog(SQX_PG_MODULE.aliasAutoSuggestStartMessage(inputs.length), 'info');
  let found = 0;
  for (const inp of inputs) {
    const asset = inp.dataset.pgAlias;
    try {
      const r = await pgFetch('/suggest-instruments/' + asset);
      const top = r.suggestions && r.suggestions[0];
      // Solo sugerir si score > 80 y no hay alias actual
      if (top && top.score >= PG_ALIAS_MIN_SCORE && !inp.value.trim()) {
        inp.value = top.instrument;
        PG_STATE.aliases[asset] = top.instrument;
        found++;
      }
    } catch {}
  }
  const result = SQX_PG_MODULE.aliasAutoSuggestResult(found);
  pgLog(result.text, result.level);
}

async function pgLoadMinings() {
  try {
    const minings = await pgFetch('/minings');
    PG_STATE.minings = minings;
    PG_STATE.planCount = minings.length;
    pgUpdateMiningSummary(minings.length);
    const infos = await SQX_PG_MODULE.enrichMiningsWithSymbolInfo(minings, async asset => {
      return (await pgFetch('/symbol-info/' + asset)).info;
    });
    pgRenderMiningsList(infos);
    pgRenderOnboarding();
  } catch(e) { pgLog('Error cargando minings: ' + e.message, 'err'); }
}

async function pgLoadOutput() {
  try {
    const r = await pgFetch('/output');
    const output = SQX_PG_MODULE.outputState(r);
    PG_STATE.outputDir = output.outputDir;
    PG_STATE.outputFiles = output.files;
    pgRenderOutputState(output);
    pgRenderOnboarding();
  } catch(e) { pgLog('Error cargando output: ' + e.message, 'err'); }
}

async function pgGenerateOne(mining, capa) {
  pgLog(SQX_PG_MODULE.generateOneStartMessage(mining, capa), 'info');
  try {
    const r = await pgFetch('/generate', { method:'POST', body: { mining, capa } });
    const result = SQX_PG_MODULE.generateOneResult(r, mining, capa);
    pgLog(result.logText, result.logLevel);
    pgTrace(result.traceTitle, result.traceDetail, result.traceLevel);
    if (r.ok) await pgLoadOutput();
  } catch(e) {
    const result = SQX_PG_MODULE.generateErrorResult(e.message, 'Error generando proyecto');
    pgLog(result.logText, result.logLevel);
    pgTrace(result.traceTitle, result.traceDetail, result.traceLevel);
  }
}

async function pgGenerateAll(capa) {
  if (!confirm(SQX_PG_MODULE.generateAllConfirmMessage(capa, PG_STATE.planCount))) return;
  pgLog(SQX_PG_MODULE.generateAllStartMessage(capa), 'info');
  try {
    const r = await pgFetch('/generate-all', { method:'POST', body: { capa } });
    const summary = SQX_PG_MODULE.generateAllResultSummary(r);
    const trace = SQX_PG_MODULE.generateAllTrace(capa, r);
    pgLog(summary.text, summary.level);
    pgTrace(trace.title, trace.detail, trace.level);
    SQX_PG_MODULE.generateAllResultLines(r.results).forEach(line => {
      pgLog(line.text, line.level);
    });
    await pgLoadOutput();
  } catch(e) {
    const result = SQX_PG_MODULE.generateErrorResult(e.message, 'Error en generacion masiva');
    pgLog(result.logText, result.logLevel);
    pgTrace(result.traceTitle, result.traceDetail, result.traceLevel);
  }
}

async function pgSaveConfig() {
  const body = SQX_PG_MODULE.configSaveBody(pgReadConfigInputs());
  pgSetSettingsMessage({ message: 'Guardando…' });
  try {
    const r = await pgFetch('/config', { method:'POST', body });
    const status = SQX_PG_MODULE.configSaveStatus(r);
    pgSetSettingsMessage(status);
    pgLog(status.logText, status.logLevel);
    pgTrace(status.traceTitle, status.traceDetail, status.traceLevel);
    await pgCheckHealth();
  } catch(e) {
    const status = SQX_PG_MODULE.configSaveError(e.message);
    pgSetSettingsMessage(status);
    pgTrace(status.traceTitle, status.traceDetail, status.traceLevel);
  }
}

// ── Listeners Project Generator ──
async function pgAutodetectSqx() {
  const out = pgDom('pg-autodetect-results');
  if (!out) return;
  out.innerHTML = SQX_PG_MODULE.messageHtml('Buscando instalaciones de SQX...', 'info');
  try {
    const r = await pgFetch('/autodetect-sqx');
    out.innerHTML = SQX_PG_MODULE.autodetectCandidatesHtml(r);
    if (!r.found) return;
    document.querySelectorAll('.pg-use-btn').forEach(btn => {
      btn.addEventListener('click', function(){
        const c = r.candidates[parseInt(this.dataset.idx, 10)];
        pgApplySqxCandidate(c, out);
      });
    });
  } catch(e) {
    out.innerHTML = SQX_PG_MODULE.messageHtml('Error: ' + e.message, 'error');
  }
}

async function pgValidateSqxPath() {
  const path = pgTrimmedInputValue('pg-sqx-path');
  const out = pgDom('pg-autodetect-results');
  if (!out) return;
  if (!path) {
    out.innerHTML = SQX_PG_MODULE.validateSqxMissingPathHtml();
    return;
  }
  try {
    const r = await pgFetch('/validate-sqx-path', { method:'POST', body: { path } });
    out.innerHTML = SQX_PG_MODULE.validateSqxPathHtml(r);
    if (SQX_PG_MODULE.validateSqxShouldApply(r)) {
      pgApplyValidatedSqxPath(path, r);
    }
  } catch(e) {
    out.innerHTML = SQX_PG_MODULE.messageHtml('Error: ' + e.message, 'error');
    pgTrace('Error validando SQX', e.message, 'err');
  }
}

async function pgOpenOutputFolder() {
  if (!PG_STATE.connected) {
    const status = SQX_PG_MODULE.openOutputDisconnectedStatus();
    pgLog(status.logText, status.logLevel);
    return;
  }
  try {
    const outputDir = PG_STATE.outputDir || (await pgFetch('/output')).output_dir;
    await pgFetch('/open-folder', { method:'POST', body: { path: outputDir } });
    const status = SQX_PG_MODULE.openOutputSuccessStatus(outputDir);
    pgLog(status.logText, status.logLevel);
    pgTrace(status.traceTitle, status.traceDetail, status.traceLevel);
  } catch(e) {
    const status = SQX_PG_MODULE.openOutputErrorStatus(e.message);
    pgLog(status.logText, status.logLevel);
    pgTrace(status.traceTitle, status.traceDetail, status.traceLevel);
  }
}

async function pgRunOnboardingAction() {
  const state = pgGetOnboardingState();
  const current = state.current;
  if (!current) {
    await pgOpenOutputFolder();
    return;
  }
  if (current.id === 'api') {
    await pgCheckHealth();
    return;
  }
  if (current.id === 'sqx') {
    pgSetSettingsOpen(true);
    const path = pgTrimmedInputValue('pg-sqx-path');
    if (path) await pgValidateSqxPath();
    else await pgAutodetectSqx();
    return;
  }
  if (current.id === 'templates') {
    const targetId = !PG_STATE.healthMeta.templates_capa1_exists ? 'pg-tpl-c1'
      : (!PG_STATE.healthMeta.templates_capa2_exists ? 'pg-tpl-c2' : 'pg-output-dir');
    pgFocusSettingsField(targetId);
    return;
  }
  if (PG_STATE.minings.length) {
    await pgGenerateOne(PG_STATE.minings[0].num, 1);
    return;
  }
  await pgCheckHealth();
}

async function pgRunOnboardingSecondaryAction() {
  const state = pgGetOnboardingState();
  if (state.current && state.current.id === 'templates') {
    await pgCheckHealth();
    return;
  }
  pgFocusSettingsField('pg-sqx-path');
}

async function pgRunOnboardingTertiaryAction() {
  const action = (document.getElementById('pg-onboarding-tertiary') || {}).dataset?.pgAssistantAction || 'save';
  if (action === 'refresh') {
    await pgCheckHealth();
    return;
  }
  if (action === 'output') {
    await pgLoadOutput();
    return;
  }
  pgSetSettingsOpen(true);
  await pgSaveConfig();
}

(function pgInit(){
  const refresh = document.getElementById('pg-status-refresh');
  if (!refresh) return; // tab no está en el HTML

  // ── Strategy Cleaner ──
  const CLN_STATE = {
    files: [],
    selected: new Set(),
  };

  async function clnScan() {
    const dir = document.getElementById('cln-dir').value.trim();
    const recursive = document.getElementById('cln-recursive').checked;
    const info = document.getElementById('cln-info');
    if (!dir) {
      const status = SQX_PG_MODULE.cleanerMissingDirStatus();
      info.textContent = status.text; info.style.color=status.color; return;
    }
    const scanning = SQX_PG_MODULE.cleanerScanningStatus();
    info.textContent = scanning.text; info.style.color=scanning.color;
    try {
      const r = await pgFetch('/sqx-list', { method:'POST', body: { dir, recursive } });
      if (!r.ok) {
        const status = SQX_PG_MODULE.cleanerErrorStatus(r.error);
        info.textContent = status.text; info.style.color=status.color; return;
      }
      CLN_STATE.files = r.files;
      CLN_STATE.selected = new Set();
      const scanMessage = SQX_PG_MODULE.cleanerScanMessage(r);
      info.textContent = scanMessage.text;
      info.style.color = scanMessage.color;
      clnRenderTable();
      document.getElementById('cln-actions').style.display = scanMessage.actionsDisplay;
    } catch(e) {
      const status = SQX_PG_MODULE.cleanerErrorStatus(e.message);
      info.textContent = status.text; info.style.color=status.color;
    }
  }

  function clnRenderTable() {
    const tbl = document.getElementById('cln-table');
    tbl.innerHTML = SQX_PG_MODULE.cleanerTableHtml(CLN_STATE.files, SQX_PG_MODULE.cleanerSelectedMap([...CLN_STATE.selected]));
    if (!CLN_STATE.files.length) { clnUpdateSelectedCount(); return; }
    document.querySelectorAll('.cln-row-check').forEach(cb => cb.addEventListener('change', function(){
      const p = this.dataset.path;
      if (this.checked) CLN_STATE.selected.add(p); else CLN_STATE.selected.delete(p);
      clnUpdateSelectedCount();
    }));
    document.getElementById('cln-th-check').addEventListener('change', function(){
      if (this.checked) CLN_STATE.files.forEach(f => CLN_STATE.selected.add(f.path));
      else CLN_STATE.selected.clear();
      clnRenderTable();
      clnUpdateSelectedCount();
    });
    clnUpdateSelectedCount();
  }

  function clnUpdateSelectedCount() {
    document.getElementById('cln-selected').textContent = SQX_PG_MODULE.cleanerSelectedLabel(CLN_STATE.selected.size);
  }

  async function clnPreviewRename() {
    if (!CLN_STATE.selected.size) {
      const status = SQX_PG_MODULE.cleanerNoSelectionStatus();
      pgLog(status.text, status.level); return;
    }
    const pattern = SQX_PG_MODULE.cleanerPreviewPattern(document.getElementById('cln-pattern').value);
    try {
      const r = await pgFetch('/sqx-preview-rename', { method:'POST', body: { files: [...CLN_STATE.selected], pattern } });
      pgLog(SQX_PG_MODULE.cleanerPreviewHeader(r.previews), 'info');
      SQX_PG_MODULE.cleanerPreviewLines(r.previews).forEach(line => {
        pgLog(line.text, line.level);
      });
    } catch(e) { pgLog('Error preview: ' + e.message, 'err'); }
  }

  async function clnProcess() {
    if (!CLN_STATE.selected.size) {
      const status = SQX_PG_MODULE.cleanerNoSelectionStatus();
      pgLog(status.text, status.level); return;
    }
    const opts = SQX_PG_MODULE.cleanerOptions({
      removeExitBars: document.getElementById('cln-opt-eab').checked,
      renameInstitutional: document.getElementById('cln-opt-rename').checked,
      renamePattern: document.getElementById('cln-pattern').value.trim() || '{asset}_{tf}_{dir}_{id}',
    });
    if (!SQX_PG_MODULE.cleanerHasAction(opts)) {
      const status = SQX_PG_MODULE.cleanerNoActionStatus();
      pgLog(status.text, status.level); return;
    }
    if (!confirm(SQX_PG_MODULE.cleanerConfirmMessage(CLN_STATE.selected.size, opts))) return;
    const processing = SQX_PG_MODULE.cleanerProcessingStatus(CLN_STATE.selected.size);
    pgLog(processing.text, processing.level);
    try {
      const r = await pgFetch('/sqx-clean', { method:'POST', body: { files: [...CLN_STATE.selected], options: opts } });
      pgLog(SQX_PG_MODULE.cleanerResultSummary(r), SQX_PG_MODULE.cleanerResultLevel(r));
      const trace = SQX_PG_MODULE.cleanerResultTrace(CLN_STATE.selected.size, r);
      pgTrace(trace.title, trace.detail, trace.level);
      (r.results || []).forEach(result => {
        const line = SQX_PG_MODULE.cleanerResultLines([result])[0];
        pgLog('  ' + line, result.ok ? 'ok' : 'err');
      });
      await clnScan();
    } catch(e) {
      const status = SQX_PG_MODULE.cleanerProcessErrorTrace(e.message);
      pgLog(status.logText, status.logLevel);
      pgTrace(status.traceTitle, status.traceDetail, status.traceLevel);
    }
  }

  function bindProjectGeneratorEvents() {
    refresh.addEventListener('click', pgCheckHealth);
    document.getElementById('pg-settings-toggle').addEventListener('click', function(){
      const body = document.getElementById('pg-settings-body');
      const open = body.style.display !== 'none';
      pgSetSettingsOpen(!open);
    });
    document.getElementById('pg-settings-save').addEventListener('click', pgSaveConfig);
    document.getElementById('pg-settings-reload').addEventListener('click', pgLoadConfig);
    document.getElementById('pg-onboarding-action').addEventListener('click', pgRunOnboardingAction);
    document.getElementById('pg-onboarding-secondary').addEventListener('click', pgRunOnboardingSecondaryAction);
    document.getElementById('pg-onboarding-tertiary').addEventListener('click', pgRunOnboardingTertiaryAction);
    document.getElementById('pg-autodetect').addEventListener('click', pgAutodetectSqx);
    document.getElementById('pg-aliases-suggest').addEventListener('click', pgSuggestAll);
    document.getElementById('pg-validate').addEventListener('click', pgValidateSqxPath);
    document.getElementById('pg-gen-all-c1').addEventListener('click', () => pgGenerateAll(1));
    document.getElementById('pg-gen-all-c2').addEventListener('click', () => pgGenerateAll(2));
    document.getElementById('pg-output-refresh').addEventListener('click', pgLoadOutput);
    document.getElementById('pg-open-output').addEventListener('click', pgOpenOutputFolder);
    document.getElementById('pg-log-clear').addEventListener('click', function(){
      document.getElementById('pg-log').textContent = '[esperando primera acción…]';
    });
  }

  function bindStrategyCleanerEvents() {
    document.getElementById('cln-scan').addEventListener('click', clnScan);
    document.getElementById('cln-preview').addEventListener('click', clnPreviewRename);
    document.getElementById('cln-process').addEventListener('click', clnProcess);
    document.getElementById('cln-select-all').addEventListener('click', function(){ CLN_STATE.files.forEach(f => CLN_STATE.selected.add(f.path)); clnRenderTable(); });
    document.getElementById('cln-select-none').addEventListener('click', function(){ CLN_STATE.selected.clear(); clnRenderTable(); });
    document.getElementById('cln-opt-rename').addEventListener('change', function(){
      document.getElementById('cln-pattern-wrap').style.display = this.checked ? 'inline-block' : 'none';
    });
  }

  function bindProjectGeneratorPolling() {
    document.querySelectorAll('.tab[data-tab="projectgen"]').forEach(t => {
      t.addEventListener('click', function(){ setTimeout(pgCheckHealth, 100); });
    });
    setInterval(function(){
      if (document.getElementById('tab-projectgen').style.display !== 'none') pgCheckHealth();
    }, 30000);
    pgRenderOnboarding();
    setTimeout(pgCheckHealth, 500);
  }

  bindProjectGeneratorEvents();
  bindStrategyCleanerEvents();
  bindProjectGeneratorPolling();
})();

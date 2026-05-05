// ============================================================
// SQX Dashboard — main / INIT
// Initial render calls + app shell bindings
// ============================================================

renderSqxLegend();
renderAssetGrid();
renderCategoriesView();
renderFiltros();
renderPriority();
renderStrategies();
renderPipelineState();
renderHome();

if (window.SQX && window.SQX.workflow) {
  window.SQX.workflow.init();
}

// ============================================================
// PROJECT GENERATOR — Tab que consume el backend Python (F3 API)
// ============================================================
const SQX_PG_MODULE = (window.SQX && window.SQX.projectGenerator) || {};
const PG_API = (window.SQX_CONFIG && window.SQX_CONFIG.apiBase()) || '';
let PG_CONNECTED = false;
let PG_HEALTH_TIMER = null;
let PG_PLAN_COUNT = 0;
let PG_LAST_TRACE_STATE = '';
let PG_HEALTH_META = {};
let PG_CONFIG_STATE = {};
let PG_MININGS = [];
let PG_OUTPUT_FILES = [];
let PG_OUTPUT_DIR = '';
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

function pgGetOnboardingState() {
  return SQX_PG_MODULE.computeOnboardingState({
    apiBase: PG_API,
    connected: PG_CONNECTED,
    configState: PG_CONFIG_STATE,
    dbInput: (document.getElementById('pg-sqx-db') || {}).value,
    healthMeta: PG_HEALTH_META,
    minings: PG_MININGS,
    outputDir: PG_OUTPUT_DIR,
    outputFiles: PG_OUTPUT_FILES,
    sqxPathInput: (document.getElementById('pg-sqx-path') || {}).value,
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
  if (meta && Object.keys(meta).length) PG_HEALTH_META = meta;
  else if (state === 'down') PG_HEALTH_META = {};
  if (typeof window.updateHomeBackendStatus === 'function') {
    window.updateHomeBackendStatus(state, title, desc, meta || {});
  }
  if (state !== 'loading' && state !== PG_LAST_TRACE_STATE) {
    PG_LAST_TRACE_STATE = state;
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
    PG_CONNECTED = true;
    const tplOk = h.templates_capa1_exists && h.templates_capa2_exists;
    pgSetStatus('up',
      '🟢 Backend conectado · v' + h.version,
      'SQX path: ' + (h.sqx_path || '(no set)') + ' · Templates: ' + (tplOk ? 'C1+C2 OK' : '⚠ alguno falta'),
      h);
    await pgLoadAll();
  } catch(e) {
    PG_CONNECTED = false;
    pgSetStatus('down',
      '🔴 Backend desconectado',
      'Lanza "backend/sqx-edge-tool/run-web.bat" para arrancar la API local (' + PG_API + '). Detalle: ' + e.message,
      { error: e.message });
  }
}

async function pgLoadAll() {
  await Promise.all([pgLoadConfig(), pgLoadMinings(), pgLoadOutput()]);
}

let PG_ALIASES = {}; // estado en memoria de los aliases editados

async function pgLoadConfig() {
  try {
    const c = await pgFetch('/config');
    PG_CONFIG_STATE = c || {};
    document.getElementById('pg-sqx-path').value = c.sqx_path || '';
    document.getElementById('pg-sqx-db').value = c.sqx_data_db || '';
    document.getElementById('pg-sqx-projects').value = c.sqx_projects_dir || '';
    document.getElementById('pg-output-dir').value = c.output_dir || '';
    document.getElementById('pg-tpl-c1').value = c.template_capa1 || '';
    document.getElementById('pg-tpl-c2').value = c.template_capa2 || '';
    PG_ALIASES = c.asset_aliases || {};
    pgRenderAliases();
    pgRenderOnboarding();
  } catch(e) { pgLog('Error cargando config: ' + e.message, 'err'); }
}

function pgRenderAliases() {
  const tbl = document.getElementById('pg-aliases-table');
  if (!tbl) return;
  pgFetch('/minings').then(minings => {
    tbl.innerHTML = SQX_PG_MODULE.aliasTableHtml(minings, PG_ALIASES);
    tbl.querySelectorAll('input[data-pg-alias]').forEach(inp => {
      inp.addEventListener('change', function(){
        const k = this.dataset.pgAlias;
        const v = this.value.trim();
        if (v) PG_ALIASES[k] = v;
        else delete PG_ALIASES[k];
      });
    });
    tbl.querySelectorAll('button[data-pg-suggest-asset]').forEach(btn => {
      btn.addEventListener('click', () => pgSuggestForAsset(btn.dataset.pgSuggestAsset));
    });
  }).catch(() => {
    tbl.innerHTML = SQX_PG_MODULE.aliasTableHtml([], PG_ALIASES);
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
    PG_ALIASES[asset] = chosen;
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
        PG_ALIASES[asset] = top.instrument;
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
    PG_MININGS = minings;
    PG_PLAN_COUNT = minings.length;
    document.getElementById('pg-minings-count').textContent = minings.length + ' minings';
    const bulkCount = document.getElementById('pg-bulk-count');
    if (bulkCount) bulkCount.textContent = minings.length + ' minings · Capa 1 + Capa 2';
    // Resolver costos para cada mining en paralelo (cosmético, no bloquea generación)
    const infos = await Promise.all(minings.map(async m => {
      try { return { ...m, _info: (await pgFetch('/symbol-info/' + m.asset)).info }; }
      catch { return { ...m, _info: null }; }
    }));
    document.getElementById('pg-minings-table').innerHTML = SQX_PG_MODULE.miningRowsHtml(infos);
    document.querySelectorAll('button[data-pg-gen]').forEach(btn => {
      btn.addEventListener('click', () => pgGenerateOne(parseInt(btn.dataset.pgGen,10), parseInt(btn.dataset.pgCapa,10)));
    });
    pgRenderOnboarding();
  } catch(e) { pgLog('Error cargando minings: ' + e.message, 'err'); }
}

async function pgLoadOutput() {
  try {
    const r = await pgFetch('/output');
    PG_OUTPUT_DIR = r.output_dir || '';
    PG_OUTPUT_FILES = r.files || [];
    document.getElementById('pg-output-count').textContent = r.files.length + ' archivos';
    pgRenderOnboarding();
    const list = document.getElementById('pg-output-list');
    list.innerHTML = SQX_PG_MODULE.outputListHtml(r.files);
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
  if (!confirm(SQX_PG_MODULE.generateAllConfirmMessage(capa, PG_PLAN_COUNT))) return;
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
  const body = SQX_PG_MODULE.configSaveBody({
    sqxPath: document.getElementById('pg-sqx-path').value.trim(),
    sqxDataDb: document.getElementById('pg-sqx-db').value.trim(),
    sqxProjectsDir: document.getElementById('pg-sqx-projects').value.trim(),
    outputDir: document.getElementById('pg-output-dir').value.trim(),
    templateCapa1: document.getElementById('pg-tpl-c1').value.trim(),
    templateCapa2: document.getElementById('pg-tpl-c2').value.trim(),
    assetAliases: PG_ALIASES,
  });
  const msg = document.getElementById('pg-settings-msg');
  msg.textContent = 'Guardando…';
  try {
    const r = await pgFetch('/config', { method:'POST', body });
    const status = SQX_PG_MODULE.configSaveStatus(r);
    msg.textContent = status.message;
    msg.style.color = status.color;
    pgLog(status.logText, status.logLevel);
    pgTrace(status.traceTitle, status.traceDetail, status.traceLevel);
    await pgCheckHealth();
  } catch(e) {
    const status = SQX_PG_MODULE.configSaveError(e.message);
    msg.textContent = status.message;
    msg.style.color = status.color;
    pgTrace(status.traceTitle, status.traceDetail, status.traceLevel);
  }
}

// ── Listeners Project Generator ──
async function pgAutodetectSqx() {
  const out = document.getElementById('pg-autodetect-results');
  if (!out) return;
  out.innerHTML = SQX_PG_MODULE.messageHtml('Buscando instalaciones de SQX...', 'info');
  try {
    const r = await pgFetch('/autodetect-sqx');
    out.innerHTML = SQX_PG_MODULE.autodetectCandidatesHtml(r);
    if (!r.found) return;
    document.querySelectorAll('.pg-use-btn').forEach(btn => {
      btn.addEventListener('click', function(){
        const c = r.candidates[parseInt(this.dataset.idx, 10)];
        const fields = SQX_PG_MODULE.sqxCandidateFields(c);
        const status = SQX_PG_MODULE.sqxCandidateSelectedStatus(c);
        document.getElementById('pg-sqx-path').value = fields.sqxPath;
        document.getElementById('pg-sqx-db').value = fields.dataDb;
        document.getElementById('pg-sqx-projects').value = fields.projectsDir;
        pgLog(status.logText, status.logLevel);
        pgTrace(status.traceTitle, status.traceDetail, status.traceLevel);
        pgRenderOnboarding();
        out.innerHTML = SQX_PG_MODULE.sqxAppliedHtml();
      });
    });
  } catch(e) {
    out.innerHTML = SQX_PG_MODULE.messageHtml('Error: ' + e.message, 'error');
  }
}

async function pgValidateSqxPath() {
  const path = document.getElementById('pg-sqx-path').value.trim();
  const out = document.getElementById('pg-autodetect-results');
  if (!out) return;
  if (!path) {
    out.innerHTML = SQX_PG_MODULE.validateSqxMissingPathHtml();
    return;
  }
  try {
    const r = await pgFetch('/validate-sqx-path', { method:'POST', body: { path } });
    out.innerHTML = SQX_PG_MODULE.validateSqxPathHtml(r);
    if (SQX_PG_MODULE.validateSqxShouldApply(r)) {
      const fields = SQX_PG_MODULE.validateSqxResolvedFields(r);
      const trace = SQX_PG_MODULE.validateSqxTrace(path);
      document.getElementById('pg-sqx-db').value = fields.dataDb;
      document.getElementById('pg-sqx-projects').value = fields.projectsDir;
      pgTrace(trace.title, trace.detail, trace.level);
      pgRenderOnboarding();
    }
  } catch(e) {
    out.innerHTML = SQX_PG_MODULE.messageHtml('Error: ' + e.message, 'error');
    pgTrace('Error validando SQX', e.message, 'err');
  }
}

async function pgOpenOutputFolder() {
  if (!PG_CONNECTED) {
    pgLog('Backend desconectado', 'err');
    return;
  }
  try {
    const outputDir = PG_OUTPUT_DIR || (await pgFetch('/output')).output_dir;
    await pgFetch('/open-folder', { method:'POST', body: { path: outputDir } });
    pgLog('Carpeta output abierta', 'info');
    pgTrace('Carpeta output abierta', outputDir, 'info');
  } catch(e) {
    pgLog('Error abrir carpeta: ' + e.message, 'err');
    pgTrace('Error abriendo output', e.message, 'err');
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
    const path = document.getElementById('pg-sqx-path').value.trim();
    if (path) await pgValidateSqxPath();
    else await pgAutodetectSqx();
    return;
  }
  if (current.id === 'templates') {
    const targetId = !PG_HEALTH_META.templates_capa1_exists ? 'pg-tpl-c1'
      : (!PG_HEALTH_META.templates_capa2_exists ? 'pg-tpl-c2' : 'pg-output-dir');
    pgFocusSettingsField(targetId);
    return;
  }
  if (PG_MININGS.length) {
    await pgGenerateOne(PG_MININGS[0].num, 1);
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

  // Auto-sugerir aliases para todos los assets
  document.getElementById('pg-aliases-suggest').addEventListener('click', pgSuggestAll);

  document.getElementById('pg-validate').addEventListener('click', pgValidateSqxPath);

  document.getElementById('pg-gen-all-c1').addEventListener('click', () => pgGenerateAll(1));
  document.getElementById('pg-gen-all-c2').addEventListener('click', () => pgGenerateAll(2));
  document.getElementById('pg-output-refresh').addEventListener('click', pgLoadOutput);
  document.getElementById('pg-log-clear').addEventListener('click', function(){
    document.getElementById('pg-log').textContent = '[esperando primera acción…]';
  });

  // ── Strategy Cleaner ──
  let CLN_FILES = [];        // todos los .sqx escaneados
  let CLN_SELECTED = new Set(); // paths seleccionados

  async function clnScan() {
    const dir = document.getElementById('cln-dir').value.trim();
    const recursive = document.getElementById('cln-recursive').checked;
    const info = document.getElementById('cln-info');
    if (!dir) { info.textContent = 'Pon una carpeta primero.'; info.style.color='var(--yellow)'; return; }
    info.textContent = '🔍 Escaneando...'; info.style.color='var(--text2)';
    try {
      const r = await pgFetch('/sqx-list', { method:'POST', body: { dir, recursive } });
      if (!r.ok) { info.textContent = '✗ ' + r.error; info.style.color='var(--red)'; return; }
      CLN_FILES = r.files;
      CLN_SELECTED = new Set();
      const scanMessage = SQX_PG_MODULE.cleanerScanMessage(r);
      info.textContent = scanMessage.text;
      info.style.color = scanMessage.color;
      clnRenderTable();
      document.getElementById('cln-actions').style.display = scanMessage.actionsDisplay;
    } catch(e) { info.textContent = '✗ ' + e.message; info.style.color='var(--red)'; }
  }

  function clnRenderTable() {
    const tbl = document.getElementById('cln-table');
    tbl.innerHTML = SQX_PG_MODULE.cleanerTableHtml(CLN_FILES, SQX_PG_MODULE.cleanerSelectedMap([...CLN_SELECTED]));
    if (!CLN_FILES.length) { clnUpdateSelectedCount(); return; }
    document.querySelectorAll('.cln-row-check').forEach(cb => cb.addEventListener('change', function(){
      const p = this.dataset.path;
      if (this.checked) CLN_SELECTED.add(p); else CLN_SELECTED.delete(p);
      clnUpdateSelectedCount();
    }));
    document.getElementById('cln-th-check').addEventListener('change', function(){
      if (this.checked) CLN_FILES.forEach(f => CLN_SELECTED.add(f.path));
      else CLN_SELECTED.clear();
      clnRenderTable();
      clnUpdateSelectedCount();
    });
    clnUpdateSelectedCount();
  }

  function clnUpdateSelectedCount() {
    document.getElementById('cln-selected').textContent = SQX_PG_MODULE.cleanerSelectedLabel(CLN_SELECTED.size);
  }

  async function clnPreviewRename() {
    if (!CLN_SELECTED.size) { pgLog('No hay nada seleccionado', 'err'); return; }
    const pattern = SQX_PG_MODULE.cleanerPreviewPattern(document.getElementById('cln-pattern').value);
    try {
      const r = await pgFetch('/sqx-preview-rename', { method:'POST', body: { files: [...CLN_SELECTED], pattern } });
      pgLog(SQX_PG_MODULE.cleanerPreviewHeader(r.previews), 'info');
      SQX_PG_MODULE.cleanerPreviewLines(r.previews).forEach(line => {
        pgLog(line.text, line.level);
      });
    } catch(e) { pgLog('Error preview: ' + e.message, 'err'); }
  }

  async function clnProcess() {
    if (!CLN_SELECTED.size) { pgLog('No hay nada seleccionado', 'err'); return; }
    const opts = SQX_PG_MODULE.cleanerOptions({
      removeExitBars: document.getElementById('cln-opt-eab').checked,
      renameInstitutional: document.getElementById('cln-opt-rename').checked,
      renamePattern: document.getElementById('cln-pattern').value.trim() || '{asset}_{tf}_{dir}_{id}',
    });
    if (!SQX_PG_MODULE.cleanerHasAction(opts)) {
      pgLog('Selecciona al menos una acción', 'err'); return;
    }
    if (!confirm(SQX_PG_MODULE.cleanerConfirmMessage(CLN_SELECTED.size, opts))) return;
    pgLog('Procesando ' + CLN_SELECTED.size + ' archivos...', 'info');
    try {
      const r = await pgFetch('/sqx-clean', { method:'POST', body: { files: [...CLN_SELECTED], options: opts } });
      pgLog(SQX_PG_MODULE.cleanerResultSummary(r), SQX_PG_MODULE.cleanerResultLevel(r));
      pgTrace(
        'Limpieza SQX completada',
        CLN_SELECTED.size + ' archivos · OK ' + r.ok_count + ' · FAIL ' + r.fail_count,
        SQX_PG_MODULE.cleanerResultLevel(r)
      );
      (r.results || []).forEach(result => {
        const line = SQX_PG_MODULE.cleanerResultLines([result])[0];
        pgLog('  ' + line, result.ok ? 'ok' : 'err');
      });
      await clnScan();
    } catch(e) { pgLog('Error procesando: ' + e.message, 'err'); pgTrace('Error en limpieza SQX', e.message, 'err'); }
  }

  document.getElementById('cln-scan').addEventListener('click', clnScan);
  document.getElementById('cln-preview').addEventListener('click', clnPreviewRename);
  document.getElementById('cln-process').addEventListener('click', clnProcess);
  document.getElementById('cln-select-all').addEventListener('click', function(){ CLN_FILES.forEach(f => CLN_SELECTED.add(f.path)); clnRenderTable(); });
  document.getElementById('cln-select-none').addEventListener('click', function(){ CLN_SELECTED.clear(); clnRenderTable(); });
  document.getElementById('cln-opt-rename').addEventListener('change', function(){
    document.getElementById('cln-pattern-wrap').style.display = this.checked ? 'inline-block' : 'none';
  });

  document.getElementById('pg-open-output').addEventListener('click', async function(){
    if (!PG_CONNECTED) { pgLog('Backend desconectado', 'err'); return; }
    try {
      // El path absoluto lo resuelve el backend
      const r = await pgFetch('/output');
      await pgFetch('/open-folder', { method:'POST', body: { path: r.output_dir } });
      pgLog('📁 Abierta carpeta output', 'info');
      pgTrace('Carpeta output abierta', r.output_dir, 'info');
    } catch(e) { pgLog('Error abrir carpeta: ' + e.message, 'err'); pgTrace('Error abriendo output', e.message, 'err'); }
  });

  // Auto-check al abrir el tab
  document.querySelectorAll('.tab[data-tab="projectgen"]').forEach(t => {
    t.addEventListener('click', function(){ setTimeout(pgCheckHealth, 100); });
  });
  // Polling cada 30s mientras esté visible
  setInterval(function(){
    if (document.getElementById('tab-projectgen').style.display !== 'none') pgCheckHealth();
  }, 30000);
  // Initial check al cargar la página (silencioso)
  pgRenderOnboarding();
  setTimeout(pgCheckHealth, 500);
})();

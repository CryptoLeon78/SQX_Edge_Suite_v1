// ============================================================
// PROJECT GENERATOR — Tab que consume el backend Python (F3 API)
// ============================================================
const SQX_PG_MODULE = (window.SQX && window.SQX.projectGenerator) || {};
const SQX_PG_DOM = SQX_PG_MODULE.dom || {};
const SQX_PG_BINDINGS = SQX_PG_MODULE.bindings || {};
const PG_API_INITIAL = (window.SQX_CONFIG && window.SQX_CONFIG.apiBase()) || '';
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
  generationMode: '',
  selectedMiningNums: new Set(),
  selectedOutputNames: new Set(),
};
const PG_ALIAS_MIN_SCORE = (window.SQX_CONFIG && window.SQX_CONFIG.value('projectGenerator.aliasSuggestMinScore', 80)) || 80;
const pgApiInline = document.getElementById('pg-api-base-inline');
if (pgApiInline) pgApiInline.textContent = 'Servicio preparado';

function pgApiBase() {
  return (window.SQX_CONFIG && window.SQX_CONFIG.apiBase && window.SQX_CONFIG.apiBase()) || PG_API_INITIAL || '';
}

function pgConnectionDiagnostic(error) {
  const diag = window.SQX_CONFIG && window.SQX_CONFIG.diagnostics ? window.SQX_CONFIG.diagnostics() : {};
  const origin = (window.location && window.location.origin) || '';
  const apiBase = String(diag.apiBase || pgApiBase() || '');
  const apiLabel = origin && apiBase.indexOf(origin) === 0 ? apiBase.replace(origin, 'mismo-origen') : (apiBase || 'sin-api');
  const online = typeof navigator !== 'undefined' && typeof navigator.onLine === 'boolean' ? (navigator.onLine ? 'online' : 'offline') : 'online-desconocido';
  const errorName = error && error.name ? String(error.name) : 'Error';
  return 'Diagnóstico seguro: API ' + apiLabel
    + ' · config ' + (diag.configVersion || (window.SQX_CONFIG && window.SQX_CONFIG.version) || 'sin-version')
    + ' · pagina ' + ((diag.host || (window.location && window.location.host)) || 'sin-host')
    + ' · red ' + online
    + ' · error ' + errorName + '.';
}

function pgEsc(value) {
  return SQX_PG_DOM.escapeHtml ? SQX_PG_DOM.escapeHtml(value) : SQX_PG_MODULE.escapeHtml(value);
}

function pgLog(msg, level) {
  if (SQX_PG_DOM.appendLog) SQX_PG_DOM.appendLog(document, msg, level);
}

function pgTrace(title, detail, level) {
  if (SQX_PG_DOM.trace) SQX_PG_DOM.trace(window, title, detail, level);
}

function pgSetSettingsOpen(open) {
  if (SQX_PG_DOM.setSettingsOpen) SQX_PG_DOM.setSettingsOpen(document, open);
}

function pgSetStepOpen(id, open) {
  const el = pgDom(id);
  if (!el || String(el.tagName || '').toLowerCase() !== 'details') return false;
  el.open = !!open;
  return true;
}

function pgSetGenerationMode(mode) {
  const normalized = mode === 'manual' ? 'manual' : (mode === 'methodological' ? 'methodological' : '');
  PG_STATE.generationMode = normalized;
  document.querySelectorAll('[data-pg-mode]').forEach(btn => {
    const active = btn.dataset.pgMode === normalized;
    btn.classList.toggle('is-active', active);
    btn.setAttribute('aria-pressed', active ? 'true' : 'false');
  });

  const methodPanel = pgDom('pg-mode-methodological-panel');
  const manualPanel = pgDom('pg-mode-manual-panel');
  const placeholder = pgDom('pg-mode-placeholder');
  if (methodPanel) methodPanel.hidden = normalized !== 'methodological';
  if (manualPanel) manualPanel.hidden = normalized !== 'manual';
  if (placeholder) placeholder.hidden = !!normalized;

  const status = normalized === 'manual'
    ? 'Modo activo: Generación manual · Custom libre.'
    : (normalized === 'methodological'
      ? 'Modo activo: Generación metodológica · Minings del plan.'
      : 'Elige un modo en el Paso 3 para mostrar su panel de trabajo.');
  pgSetText('pg-generation-mode-status', status);

  if (normalized) {
    pgSetStepOpen('pg-step-generate', true);
    const target = normalized === 'manual' ? manualPanel : methodPanel;
    if (target && target.scrollIntoView) {
      window.setTimeout(() => target.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
    }
  }
}

function pgFocusSettingsField(id) {
  if (SQX_PG_DOM.focusSettingsField) SQX_PG_DOM.focusSettingsField(document, id);
}

function pgDom(id) {
  return SQX_PG_DOM.byId ? SQX_PG_DOM.byId(document, id) : document.getElementById(id);
}

function pgInputValue(id) {
  return SQX_PG_DOM.inputValue ? SQX_PG_DOM.inputValue(document, id) : ((pgDom(id) || {}).value || '');
}

function pgTrimmedInputValue(id) {
  return SQX_PG_DOM.trimmedInputValue ? SQX_PG_DOM.trimmedInputValue(document, id) : pgInputValue(id).trim();
}

function pgSetInputValue(id, value) {
  if (SQX_PG_DOM.setInputValue) SQX_PG_DOM.setInputValue(document, id, value);
}

function pgSetText(id, text) {
  if (SQX_PG_DOM.setText) SQX_PG_DOM.setText(document, id, text);
}

function pgSetHtml(id, html) {
  return SQX_PG_DOM.setHtml ? SQX_PG_DOM.setHtml(document, id, html) : null;
}

function pgReadConfigInputs() {
  return SQX_PG_DOM.readConfigInputs(document, PG_STATE.aliases);
}

function pgWriteConfigInputs(config) {
  SQX_PG_DOM.writeConfigInputs(document, config);
}

function pgApplySqxFields(fields) {
  SQX_PG_DOM.applySqxFields(document, fields);
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
  SQX_PG_DOM.setSettingsMessage(document, status);
}

function pgReadCustomInputs() {
  return SQX_PG_DOM.readCustomProjectInputs ? SQX_PG_DOM.readCustomProjectInputs(document) : {};
}

function pgSelectedCapa2Blocksetting() {
  return pgInputValue('pg-capa2-bs').trim();
}

function pgApplyCapa2Selection(payload, capa) {
  const data = payload || {};
  const selected = pgSelectedCapa2Blocksetting();
  if (Number(capa || data.capa || 1) === 2 && selected) {
    data.blocksetting_capa2 = selected;
  }
  return data;
}

function pgReadTargetProfile() {
  const id = pgInputValue('pg-target-profile') || 'sqxedge_darwinex';
  const custom = {
    brokerPostfix: pgTrimmedInputValue('pg-target-postfix'),
    symbol: pgTrimmedInputValue('pg-target-symbol'),
    brokerId: pgTrimmedInputValue('pg-target-broker-id'),
    sourceId: pgTrimmedInputValue('pg-target-source-id'),
    brokerName: pgTrimmedInputValue('pg-target-broker-name'),
    timezone: pgTrimmedInputValue('pg-target-timezone'),
  };
  const payload = { id };
  if (id === 'custom_user_broker') {
    payload.custom = custom;
  }
  return payload;
}

function pgApplyTargetProfile(payload) {
  const data = payload || {};
  data.target_profile = pgReadTargetProfile();
  return data;
}

function pgUpdateTargetProfileUi() {
  const id = pgInputValue('pg-target-profile') || 'sqxedge_darwinex';
  const custom = pgDom('pg-target-custom-fields');
  if (custom) custom.hidden = id !== 'custom_user_broker';
  const warning = id === 'custom_user_broker'
    ? 'Modo remapeo: usa símbolo exacto o sufijo, Broker ID y Source ID del Data Manager del usuario destino. Si no los conoces, genera con SQX Edge / Darwinex y el usuario verá el diálogo de recursos en SQX.'
    : 'Perfil recomendado para el servidor SQX Edge Suite. Si el usuario abrirá el .cfx en otro SQX sin Darwinex/data compatible, selecciona Broker del usuario y remapea el símbolo principal.';
  pgSetText('pg-target-profile-warning', warning);
}

function pgSetCustomStatus(text, level) {
  if (SQX_PG_DOM.setCustomProjectStatus) {
    SQX_PG_DOM.setCustomProjectStatus(document, { text, level });
  }
}

function pgSetCustomPackStatus(text) {
  pgSetText('pg-custom-pack-status', text || '');
}

function pgSetCustomImportPreview(html, hasItems) {
  const el = pgDom('pg-custom-import-preview');
  if (!el) return;
  el.innerHTML = html || '';
  el.classList.toggle('has-items', !!hasItems);
}

function pgWriteCustomInputs(config) {
  if (SQX_PG_DOM.writeCustomProjectInputs) SQX_PG_DOM.writeCustomProjectInputs(document, config);
}

function pgRenderCustomPresets(selectedId) {
  const presets = SQX_PG_MODULE.getCustomProjectPresets ? SQX_PG_MODULE.getCustomProjectPresets() : [];
  pgSetText('pg-custom-presets-count', SQX_PG_MODULE.customProjectPresetCountLabel(presets.length));
  pgSetHtml('pg-custom-presets-select', SQX_PG_MODULE.customProjectPresetOptionsHtml(presets));
  if (selectedId) pgSetInputValue('pg-custom-presets-select', selectedId);
  return presets;
}

function pgDownloadJson(filename, payload) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function pgUpdateMiningSummary(count) {
  pgSetText('pg-minings-count', SQX_PG_MODULE.miningsCountLabel(count));
}

function pgSelectedMiningMap() {
  const map = {};
  PG_STATE.selectedMiningNums.forEach(num => { map[num] = true; });
  return map;
}

function pgSelectedOutputMap() {
  const map = {};
  PG_STATE.selectedOutputNames.forEach(name => { map[name] = true; });
  return map;
}

function pgUpdateSelectedOutputCount() {
  pgSetText('pg-output-selected-count', SQX_PG_MODULE.selectedOutputCountLabel
    ? SQX_PG_MODULE.selectedOutputCountLabel(PG_STATE.selectedOutputNames.size)
    : (PG_STATE.selectedOutputNames.size + ' seleccionados'));
}

function pgSyncSelectedOutputs() {
  const valid = new Set((PG_STATE.outputFiles || []).map(file => String(file.name || '')));
  Array.from(PG_STATE.selectedOutputNames).forEach(name => {
    if (!valid.has(name)) PG_STATE.selectedOutputNames.delete(name);
  });
  pgUpdateSelectedOutputCount();
}

function pgUpdateSelectedMiningCount() {
  pgSetText('pg-selected-count', SQX_PG_MODULE.selectedMiningCountLabel(PG_STATE.selectedMiningNums.size));
}

function pgSyncSelectedMinings() {
  const valid = new Set((PG_STATE.minings || []).map(mining => parseInt(mining.num, 10)));
  Array.from(PG_STATE.selectedMiningNums).forEach(num => {
    if (!valid.has(num)) PG_STATE.selectedMiningNums.delete(num);
  });
  pgUpdateSelectedMiningCount();
}

function pgRenderMiningsList(infos) {
  pgSyncSelectedMinings();
  pgSetHtml('pg-minings-table', SQX_PG_MODULE.miningRowsHtml(infos, pgSelectedMiningMap()));
  document.querySelectorAll('input[data-pg-mining-check]').forEach(input => {
    input.addEventListener('change', () => {
      const num = parseInt(input.dataset.pgMiningCheck, 10);
      if (input.checked) PG_STATE.selectedMiningNums.add(num);
      else PG_STATE.selectedMiningNums.delete(num);
      pgUpdateSelectedMiningCount();
    });
  });
  pgUpdateSelectedMiningCount();
}

function pgRenderOutputState(output) {
  PG_STATE.outputFiles = output.files || PG_STATE.outputFiles || [];
  pgSyncSelectedOutputs();
  if (SQX_PG_MODULE.outputState && output && output.files) {
    output.html = SQX_PG_MODULE.outputListHtml(output.files, pgSelectedOutputMap());
  }
  pgSetText('pg-output-count', output.countLabel);
  pgSetHtml('pg-output-list', output.html);
  pgSetText('pg-open-output', 'Descargar todo ZIP');
  document.querySelectorAll('input[data-pg-output-check]').forEach(input => {
    input.addEventListener('change', () => {
      const name = input.dataset.pgOutputCheck || '';
      if (input.checked) PG_STATE.selectedOutputNames.add(name);
      else PG_STATE.selectedOutputNames.delete(name);
      pgUpdateSelectedOutputCount();
    });
  });
  document.querySelectorAll('button[data-pg-output-download]').forEach(btn => {
    btn.addEventListener('click', () => pgDownloadOutputFile(btn.dataset.pgOutputDownload));
  });
  document.querySelectorAll('button[data-pg-output-delete]').forEach(btn => {
    btn.addEventListener('click', () => pgDeleteOutputFiles([btn.dataset.pgOutputDelete]));
  });
  pgUpdateSelectedOutputCount();
}

function pgResetGeneratedCfxSession(detail) {
  const resetState = detail && detail.resetState
    ? detail.resetState
    : SQX_PG_MODULE.markGeneratedOutputReset(PG_STATE.outputFiles || [], { reason: 'plan-mining-reset' });
  PG_STATE.outputFiles = [];
  PG_STATE.selectedOutputNames.clear();
  pgRenderOutputState(SQX_PG_MODULE.outputState({ output_dir: PG_STATE.outputDir, files: [] }, resetState));
  const log = pgDom('pg-log');
  if (log) log.textContent = '[Plan Mining reiniciado: .cfx generados vacíos para la nueva sesión.]';
  pgRenderOnboarding();
  return resetState;
}

function pgGetOnboardingState() {
  return SQX_PG_MODULE.computeOnboardingState({
    apiBase: pgApiBase(),
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
  return SQX_PG_MODULE.fetchJson(pgApiBase(), path, options);
}

function pgIsRemoteSessionRequired(error) {
  return SQX_PG_MODULE.isRemoteSessionRequiredError
    ? SQX_PG_MODULE.isRemoteSessionRequiredError(error)
    : String((error && error.message) || '').toLowerCase().includes('remote_session_required');
}

function pgHandleRemoteSessionRequired(error) {
  const message = 'Sesión SQX Edge Suite pendiente o caducada. Pulsa Acceso DASHBOARD en Bienvenida para crear la sesión de app y el workspace antes de generar o descargar .cfx.';
  pgLog(message, 'err');
  pgSetStatus('down', 'Sesión de app requerida', 'Acceso Cloudflare OK, pero falta activar la sesión interna de SQX Edge Suite. No se fuerza navegación desde Project Generator para evitar bucles de bienvenida.', {
    error: (error && (error.code || error.message)) || 'remote_session_required'
  });
  return true;
}

function pgHandleFetchError(error, title, traceTitle) {
  if (pgIsRemoteSessionRequired(error)) {
    pgHandleRemoteSessionRequired(error);
    return true;
  }
  if (title) pgLog(title + ': ' + error.message, 'err');
  if (traceTitle) pgTrace(traceTitle, error.message, 'err');
  return false;
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
      state === 'up' ? 'Conexiones internas OK' : desc,
      state === 'up' ? 'ok' : 'err'
    );
  }
  SQX_PG_MODULE.applyStatusBanner({ state, title, desc }, document);
  pgRenderOnboarding();
}

async function pgCheckHealth() {
  pgSetStatus('loading', 'Comprobando…', 'Validando conexiones internas del servicio');
  try {
    const h = await pgFetch('/health');
    PG_STATE.connected = true;
    const tplOk = h.templates_capa1_exists && h.templates_capa2_exists;
    pgSetStatus('up',
      'Servicio conectado · v' + h.version,
      'Conexiones internas: ' + (tplOk ? 'SQX, templates y workspace OK' : 'revisión requerida en templates'),
      h);
    await pgLoadAll();
  } catch(e) {
    if (pgIsRemoteSessionRequired(e)) {
      pgHandleRemoteSessionRequired(e);
      return;
    }
    PG_STATE.connected = false;
    const diagnostic = pgConnectionDiagnostic(e);
    pgSetStatus('down',
      'Servicio desconectado',
      'El servicio no responde. Reintenta o registra incidencia desde Control Panel. Detalle: ' + e.message + '. ' + diagnostic,
      { error: e.message });
    await pgLoadMinings();
  }
}

async function pgLoadAll() {
  await Promise.all([pgLoadConfig(), pgLoadMinings(), pgLoadOutput()]);
}

function pgNormalizePlanMining(mining) {
  const data = mining || {};
  return {
    num: parseInt(data.num, 10),
    phase: parseInt(data.phase, 10) || 0,
    asset: String(data.asset || '').trim().toUpperCase(),
    tf: String(data.tf || '').trim().toUpperCase(),
    bs: String(data.bs || data.blocksetting || '').trim(),
    dir: String(data.dir || data.direction || 'long').trim(),
    name: data.name || '',
    source: data.source || '',
    blocksetting: data.blocksetting || data.blocksetting_trace || null,
    _user: !!data._user,
  };
}

function pgActivePlanMinings() {
  let sourceAvailable = false;
  let minings = [];
  try {
    if (typeof window.getPlanMinings === 'function') {
      sourceAvailable = true;
      minings = window.getPlanMinings();
    } else if (Array.isArray(window.PLAN_ALL)) {
      sourceAvailable = true;
      minings = window.PLAN_ALL;
    } else if (Array.isArray(window.PLAN_MININGS)) {
      sourceAvailable = true;
      minings = window.PLAN_MININGS;
    }
  } catch (_err) {
    minings = [];
  }
  return {
    sourceAvailable,
    minings: (minings || []).map(pgNormalizePlanMining).filter(mining => {
      return mining.num && mining.asset && mining.tf && mining.bs && mining.dir;
    }).sort((a, b) => a.num - b.num),
  };
}

async function pgLoadConfig() {
  try {
    const c = await pgFetch('/config');
    PG_STATE.config = c || {};
    pgWriteConfigInputs(c);
    pgUpdateTargetProfileUi();
    PG_STATE.aliases = c.asset_aliases || {};
    pgRenderAliases();
    pgRenderOnboarding();
  } catch(e) {
    if (pgHandleFetchError(e, 'Error cargando config')) return;
  }
}

function pgRenderAliases() {
  const tbl = document.getElementById('pg-aliases-table');
  if (!tbl) return;
  const activePlan = pgActivePlanMinings();
  if (activePlan.sourceAvailable) {
    tbl.innerHTML = SQX_PG_MODULE.aliasTableHtml(activePlan.minings, PG_STATE.aliases);
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
    return;
  }
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
    const activePlan = pgActivePlanMinings();
    const minings = activePlan.sourceAvailable ? activePlan.minings : await pgFetch('/minings');
    PG_STATE.minings = minings;
    PG_STATE.planCount = minings.length;
    pgUpdateMiningSummary(minings.length);
    pgRenderMiningsList(minings);
    const infos = await SQX_PG_MODULE.enrichMiningsWithSymbolInfo(minings, async asset => {
      return (await pgFetch('/symbol-info/' + asset)).info;
    });
    PG_STATE.minings = infos;
    pgRenderMiningsList(infos);
    pgRenderOnboarding();
  } catch(e) {
    PG_STATE.minings = [];
    PG_STATE.planCount = 0;
    pgUpdateMiningSummary(0);
    pgRenderMiningsList([]);
    pgLog('Error cargando minings: ' + e.message, 'err');
  }
}

function pgFindMining(num) {
  const miningNum = parseInt(num, 10);
  return (PG_STATE.minings || []).find(mining => parseInt(mining.num, 10) === miningNum) || null;
}

function pgProjectNameFromMining(mining) {
  const num = String(mining.num || 0).padStart(2, '0');
  const dir = SQX_PG_MODULE.directionLabel(mining.dir).replace(/[^A-Z0-9]/g, '');
  return ['Mining' + num, mining.asset, mining.tf, mining.bs, dir].filter(Boolean).join('_');
}

function pgCustomPayloadFromMining(mining, capa) {
  return pgApplyTargetProfile(pgApplyCapa2Selection({
    name: mining.name || pgProjectNameFromMining(mining),
    asset: mining.asset,
    tf: mining.tf,
    bs: mining.bs,
    dir: mining.dir,
    capa,
  }, capa));
}

async function pgGenerateMiningRequest(mining, capa) {
  if (mining && mining._user) {
    const customResult = await pgFetch('/generate-custom', { method:'POST', body: pgCustomPayloadFromMining(mining, capa) });
    return Object.assign({}, customResult, { mining: mining.num });
  }
  return await pgFetch('/generate', { method:'POST', body: pgApplyTargetProfile(pgApplyCapa2Selection({ mining: mining.num, capa }, capa)) });
}

async function pgLoadOutput() {
  try {
    const r = await pgFetch('/output');
    const output = SQX_PG_MODULE.outputState(r);
    PG_STATE.outputDir = output.outputDir;
    PG_STATE.outputFiles = output.files;
    pgRenderOutputState(output);
    pgRenderOnboarding();
  } catch(e) {
    if (pgHandleFetchError(e, 'Error cargando output')) return;
  }
}

function pgRecordEdgeFactoryGeneration(capa, mode, minings, results, extra) {
  try {
    if (!window.SQX || !window.SQX.edgeFactory || typeof window.SQX.edgeFactory.recordProjectGeneration !== 'function') return;
    window.SQX.edgeFactory.recordProjectGeneration(Object.assign({
      capa: parseInt(capa, 10) || 1,
      mode: mode || 'methodology',
      minings: Array.isArray(minings) ? minings : [],
      results: Array.isArray(results) ? results : [],
      outputFiles: PG_STATE.outputFiles || [],
      generatedAt: new Date().toISOString()
    }, extra || {}));
    if (window.SQX.edgeFactoryUI && typeof window.SQX.edgeFactoryUI.renderState === 'function') {
      window.SQX.edgeFactoryUI.renderState();
    }
  } catch(e) {
    console.warn('Edge Factory generation handoff skipped:', e && e.message ? e.message : e);
  }
}

function pgRecordEdgeFactoryDownload(kind, files, capa) {
  try {
    if (!window.SQX || !window.SQX.edgeFactory || typeof window.SQX.edgeFactory.recordDownloadRequest !== 'function') return;
    window.SQX.edgeFactory.recordDownloadRequest({
      kind: kind || 'cfx',
      capa: capa == null ? null : capa,
      files: files || []
    });
  } catch(e) {
    console.warn('Edge Factory download handoff skipped:', e && e.message ? e.message : e);
  }
}

async function pgGenerateOne(mining, capa) {
  const planMining = pgFindMining(mining) || pgNormalizePlanMining({ num: mining, asset: '', tf: '', bs: '', dir: 'long' });
  pgLog(SQX_PG_MODULE.generateOneStartMessage(planMining.num, capa), 'info');
  try {
    const r = await pgGenerateMiningRequest(planMining, capa);
    const result = SQX_PG_MODULE.generateOneResult(r, planMining.num, capa);
    pgLog(result.logText, result.logLevel);
    pgTrace(result.traceTitle, result.traceDetail, result.traceLevel);
    if (r.ok) {
      await pgLoadOutput();
      pgRecordEdgeFactoryGeneration(capa, 'methodology-one', [planMining], [Object.assign({}, r, { mining: planMining.num })]);
      pgLog('Archivo listo en .cfx generados: pulsa Descargar en la fila o Descargar todo ZIP.', 'info');
    }
  } catch(e) {
    if (pgHandleFetchError(e)) return;
    const result = SQX_PG_MODULE.generateErrorResult(e.message, 'Error generando proyecto');
    pgLog(result.logText, result.logLevel);
    pgTrace(result.traceTitle, result.traceDetail, result.traceLevel);
  }
}

async function pgGenerateCustom() {
  const body = pgApplyTargetProfile(pgApplyCapa2Selection(pgReadCustomInputs()));
  if (!body.asset || !body.tf) {
    const status = SQX_PG_MODULE.generateCustomMissingStatus();
    pgSetCustomStatus(status.text, status.level);
    pgLog(status.logText, status.logLevel);
    return;
  }
  pgSetCustomStatus(SQX_PG_MODULE.generateCustomStartMessage(body), 'info');
  pgLog(SQX_PG_MODULE.generateCustomStartMessage(body), 'info');
  try {
    const r = await pgFetch('/generate-custom', { method:'POST', body });
    const result = SQX_PG_MODULE.generateCustomResult(r, body);
    pgSetCustomStatus(result.text, result.level);
    pgLog(result.logText, result.logLevel);
    pgTrace(result.traceTitle, result.traceDetail, result.traceLevel);
    if (r.ok) {
      await pgLoadOutput();
      pgRecordEdgeFactoryGeneration(body.capa || 1, 'manual', [], [r], { custom: body });
      pgLog('Archivo listo en .cfx generados: pulsa Descargar en la fila o Descargar todo ZIP.', 'info');
    }
  } catch(e) {
    if (pgHandleFetchError(e)) return;
    const result = SQX_PG_MODULE.generateCustomResult({ ok:false, error:e.message }, body);
    pgSetCustomStatus(result.text, result.level);
    pgLog(result.logText, result.logLevel);
    pgTrace(result.traceTitle, result.traceDetail, result.traceLevel);
  }
}

function pgSaveCustomPreset() {
  const body = pgReadCustomInputs();
  const presetName = pgTrimmedInputValue('pg-custom-preset-name');
  const result = SQX_PG_MODULE.upsertCustomProjectPreset(body, presetName);
  if (!result.ok) {
    pgSetCustomStatus(result.error, 'err');
    pgLog(result.error, 'err');
    return;
  }
  pgRenderCustomPresets(result.preset.id);
  pgSetInputValue('pg-custom-preset-name', '');
  pgSetCustomStatus('Preset guardado: ' + result.preset.name, 'ok');
  pgLog('Preset custom guardado: ' + result.preset.name, 'ok');
  pgTrace('Preset custom guardado', result.preset.name, 'ok');
}

function pgSelectedCustomPreset() {
  const id = pgInputValue('pg-custom-presets-select');
  return id && SQX_PG_MODULE.findCustomProjectPreset(id);
}

function pgLoadCustomPreset() {
  const preset = pgSelectedCustomPreset();
  if (!preset) {
    pgSetCustomStatus('Selecciona un preset custom para cargar.', 'err');
    return;
  }
  pgWriteCustomInputs(preset.config);
  pgSetCustomStatus('Preset cargado: ' + preset.name, 'ok');
  pgLog('Preset custom cargado: ' + preset.name, 'info');
  pgTrace('Preset custom cargado', preset.name, 'info');
}

function pgDeleteCustomPreset() {
  const preset = pgSelectedCustomPreset();
  if (!preset) {
    pgSetCustomStatus('Selecciona un preset custom para eliminar.', 'err');
    return;
  }
  const result = SQX_PG_MODULE.deleteCustomProjectPreset(preset.id);
  pgRenderCustomPresets();
  pgSetCustomStatus(result.deleted ? 'Preset eliminado: ' + preset.name : 'No se pudo eliminar el preset.', result.deleted ? 'ok' : 'err');
  pgLog((result.deleted ? 'Preset custom eliminado: ' : 'Preset custom no encontrado: ') + preset.name, result.deleted ? 'info' : 'err');
}

function pgExportCustomPresets() {
  const presets = SQX_PG_MODULE.getCustomProjectPresets ? SQX_PG_MODULE.getCustomProjectPresets() : [];
  if (!presets.length) {
    pgSetCustomStatus('Guarda al menos un preset custom antes de exportar.', 'err');
    pgSetCustomPackStatus('No hay presets para exportar.');
    return;
  }
  const pack = SQX_PG_MODULE.buildCustomProjectPresetPackage(presets);
  const day = new Date().toISOString().slice(0, 10);
  pgDownloadJson('sqx-custom-project-presets-' + day + '.json', pack);
  pgSetCustomStatus('Pack exportado: ' + pack.presets.length + ' presets.', 'ok');
  pgSetCustomPackStatus('Pack JSON listo para otra instalacion.');
  pgLog('Pack de presets custom exportado: ' + pack.presets.length + ' presets.', 'ok');
}

function pgOpenImportCustomPresets() {
  const fileInput = pgDom('pg-custom-import-presets-file');
  if (fileInput) fileInput.click();
}

function pgImportCustomPresets(event) {
  const file = event && event.target && event.target.files && event.target.files[0];
  if (!file) {
    pgSetCustomStatus('Selecciona un pack JSON de presets custom.', 'err');
    pgSetCustomImportPreview('', false);
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    const preview = SQX_PG_MODULE.customProjectPresetImportPreviewFromText
      ? SQX_PG_MODULE.customProjectPresetImportPreviewFromText(reader.result || '')
      : { incomingCount: 0 };
    const previewHtml = SQX_PG_MODULE.customProjectPresetImportPreviewHtml
      ? SQX_PG_MODULE.customProjectPresetImportPreviewHtml(preview)
      : '';
    pgSetCustomImportPreview(previewHtml, !!preview.incomingCount);
    const result = SQX_PG_MODULE.importCustomProjectPresetPackageFromText(reader.result || '');
    pgRenderCustomPresets(result.presets[0] && result.presets[0].id);
    if (result.imported) {
      pgSetCustomStatus('Pack importado: ' + result.imported + ' presets.', 'ok');
      pgSetCustomPackStatus((SQX_PG_MODULE.customProjectPresetImportPreviewSummary && SQX_PG_MODULE.customProjectPresetImportPreviewSummary(preview)) || 'Presets importados y fusionados con los locales.');
      pgLog('Pack de presets custom importado: ' + result.imported + ' presets. ' + (SQX_PG_MODULE.customProjectPresetImportPreviewSummary ? SQX_PG_MODULE.customProjectPresetImportPreviewSummary(preview) : ''), 'ok');
    } else {
      pgSetCustomStatus('El pack no contiene presets custom validos.', 'err');
      pgSetCustomPackStatus('Importacion sin cambios.');
    }
  };
  reader.onerror = () => {
    pgSetCustomStatus('No se pudo leer el pack de presets custom.', 'err');
    pgSetCustomPackStatus('Error leyendo el archivo.');
    pgSetCustomImportPreview('', false);
  };
  reader.readAsText(file);
  if (event && event.target) event.target.value = '';
}

async function pgGenerateAll(capa) {
  const minings = (PG_STATE.minings || []).slice();
  if (!minings.length) {
    pgLog('No hay minings activos en Plan Mining para generar.', 'err');
    return;
  }
  if (!confirm(SQX_PG_MODULE.generateAllConfirmMessage(capa, minings.length))) return;
  pgLog(SQX_PG_MODULE.generateAllStartMessage(capa), 'info');
  const results = [];
  for (const mining of minings) {
    try {
      pgLog(SQX_PG_MODULE.generateOneStartMessage(mining.num, capa), 'info');
      const r = await pgGenerateMiningRequest(mining, capa);
      results.push(Object.assign({}, r, { mining: mining.num }));
    } catch(e) {
      if (pgHandleFetchError(e)) return;
      results.push({ ok:false, mining:mining.num, error:e.message });
    }
  }
  const okCount = results.filter(result => result.ok).length;
  const summaryPayload = { ok: okCount === results.length, ok_count: okCount, fail_count: results.length - okCount, results };
  const summary = SQX_PG_MODULE.generateAllResultSummary(summaryPayload);
  const trace = SQX_PG_MODULE.generateAllTrace(capa, summaryPayload);
  pgLog(summary.text, summary.level);
  pgTrace(trace.title, trace.detail, trace.level);
  SQX_PG_MODULE.generateAllResultLines(results).forEach(line => {
    pgLog(line.text, line.level);
  });
  await pgLoadOutput();
  pgRecordEdgeFactoryGeneration(capa, 'methodology-all', minings, results);
  pgLog('Generación terminada. Descarga desde .cfx generados con Descargar, Descargar seleccionados o Descargar todo ZIP.', 'info');
}

async function pgGenerateSelected(capa) {
  const selected = (PG_STATE.minings || []).filter(mining => PG_STATE.selectedMiningNums.has(parseInt(mining.num, 10)));
  if (!selected.length) {
    pgLog('Selecciona al menos un mining del plan antes de generar.', 'err');
    return;
  }
  if (!confirm(SQX_PG_MODULE.generateAllConfirmMessage(capa, selected.length))) return;
  pgLog('Generando seleccionados · Capa ' + capa + '…', 'info');
  const results = [];
  for (const mining of selected) {
    try {
      pgLog(SQX_PG_MODULE.generateOneStartMessage(mining.num, capa), 'info');
      const r = await pgGenerateMiningRequest(mining, capa);
      results.push(Object.assign({}, r, { mining: mining.num }));
    } catch(e) {
      if (pgHandleFetchError(e)) return;
      results.push({ ok:false, mining:mining.num, error:e.message });
    }
  }
  const okCount = results.filter(result => result.ok).length;
  const summary = SQX_PG_MODULE.generateAllResultSummary({ ok_count: okCount, fail_count: results.length - okCount });
  pgLog(summary.text, summary.level);
  SQX_PG_MODULE.generateAllResultLines(results).forEach(line => {
    pgLog(line.text, line.level);
  });
  await pgLoadOutput();
  pgRecordEdgeFactoryGeneration(capa, 'methodology-selected', selected, results);
  pgLog('Generación terminada. Descarga desde .cfx generados con Descargar, Descargar seleccionados o Descargar todo ZIP.', 'info');
}

function pgSelectAllMinings() {
  (PG_STATE.minings || []).forEach(mining => PG_STATE.selectedMiningNums.add(parseInt(mining.num, 10)));
  pgRenderMiningsList(PG_STATE.minings);
}

function pgClearSelectedMinings() {
  PG_STATE.selectedMiningNums.clear();
  pgRenderMiningsList(PG_STATE.minings);
}

function pgDeleteSelectedMinings() {
  const selected = Array.from(PG_STATE.selectedMiningNums).filter(Boolean).sort((a, b) => a - b);
  if (!selected.length) {
    pgLog('Selecciona al menos un mining del plan antes de borrar.', 'err');
    return;
  }
  if (typeof window.removePlanMiningsByNums !== 'function') {
    pgLog('Borrado de selección no disponible en este contexto.', 'err');
    return;
  }
  if (!confirm('Borrar ' + selected.length + ' mining(s) seleccionados del Plan Mining? Esta acción afecta al plan activo del workspace.')) return;
  const summary = window.removePlanMiningsByNums(selected) || {};
  PG_STATE.selectedMiningNums.clear();
  pgLoadMinings();
  pgRenderAliases();
  pgLog('Plan Mining actualizado: ' + (summary.removed || 0) + ' mining(s) borrados de la selección.', summary.removed ? 'ok' : 'err');
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

function pgOutputDownloadUrl(path) {
  return (pgApiBase() || '') + path;
}

function pgStartBrowserDownload(url) {
  window.location.assign(url);
}

function pgFilenameFromDisposition(headerValue, fallback) {
  const header = String(headerValue || '');
  const utf = header.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf && utf[1]) return decodeURIComponent(utf[1].replace(/"/g, ''));
  const plain = header.match(/filename="?([^";]+)"?/i);
  return plain && plain[1] ? plain[1] : fallback;
}

async function pgDownloadOutputBundle(names) {
  const selected = (names || []).map(name => String(name || '').trim()).filter(Boolean);
  if (!selected.length) {
    pgLog('No hay .cfx seleccionados para descargar.', 'err');
    return;
  }
  try {
    const response = await fetch(pgOutputDownloadUrl('/output/download-selected'), {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ files: selected })
    });
    if (!response.ok) {
      let message = 'HTTP ' + response.status;
      let code = '';
      try {
        const data = await response.json();
        code = data.error || '';
        message = data.message || data.error || message;
      } catch (_err) {}
      const error = new Error(message);
      error.status = response.status;
      error.code = code;
      throw error;
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = pgFilenameFromDisposition(response.headers.get('Content-Disposition'), selected.length === 1 ? selected[0] : 'sqx-edge-suite-cfx-selected.zip');
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    pgRecordEdgeFactoryDownload(selected.length === 1 ? 'cfx' : 'cfx-zip', selected);
    pgLog('Descarga solicitada: ' + selected.length + ' .cfx. El navegador la guardará en Descargas.', 'ok');
  } catch(e) {
    if (pgHandleFetchError(e)) return;
    pgLog('Error descargando .cfx seleccionado(s): ' + e.message, 'err');
  }
}

function pgDownloadOutputFile(name) {
  const clean = String(name || '').trim();
  if (!clean) {
    pgLog('No hay archivo .cfx seleccionado para descargar.', 'err');
    return;
  }
  pgStartBrowserDownload(pgOutputDownloadUrl('/output/download/' + encodeURIComponent(clean)));
  pgRecordEdgeFactoryDownload('cfx', [clean]);
  pgLog('Descarga solicitada: ' + clean + '. El navegador la guardará en su carpeta Descargas configurada.', 'ok');
}

function pgDownloadAllOutput() {
  if (!(PG_STATE.outputFiles || []).length) {
    pgLog('No hay .cfx generados para descargar.', 'err');
    return;
  }
  pgStartBrowserDownload(pgOutputDownloadUrl('/output/download-all'));
  pgRecordEdgeFactoryDownload('cfx-zip', PG_STATE.outputFiles || []);
  pgLog('Descarga ZIP solicitada. El navegador la guardará en su carpeta Descargas configurada.', 'ok');
}

function pgDownloadSelectedOutputFiles() {
  const selected = Array.from(PG_STATE.selectedOutputNames).filter(Boolean);
  if (!selected.length) {
    pgDownloadAllOutput();
    return;
  }
  pgDownloadOutputBundle(selected);
}

async function pgDeleteOutputFiles(names) {
  const selected = (names || []).map(name => String(name || '').trim()).filter(Boolean);
  if (!selected.length) {
    pgLog('Selecciona al menos un .cfx generado antes de borrar.', 'err');
    return;
  }
  if (!confirm('Borrar ' + selected.length + ' archivo(s) .cfx generado(s) del output activo?')) return;
  try {
    const result = await pgFetch('/output/delete', { method:'POST', body: { files: selected } });
    selected.forEach(name => PG_STATE.selectedOutputNames.delete(name));
    pgLog('Output actualizado: ' + (result.deleted || []).length + ' .cfx borrado(s).', result.ok ? 'ok' : 'err');
    await pgLoadOutput();
  } catch(e) {
    if (pgHandleFetchError(e)) return;
    pgLog('Error borrando .cfx generado(s): ' + e.message, 'err');
  }
}

function pgDeleteSelectedOutputFiles() {
  pgDeleteOutputFiles(Array.from(PG_STATE.selectedOutputNames));
}

async function pgOpenOutputFolder() {
  if (!PG_STATE.connected) {
    const status = SQX_PG_MODULE.openOutputDisconnectedStatus();
    pgLog(status.logText, status.logLevel);
    return;
  }
  pgDownloadAllOutput();
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
  pgRenderCustomPresets();
  pgSetGenerationMode('');
  pgUpdateTargetProfileUi();
  ['pg-target-profile', 'pg-target-postfix', 'pg-target-symbol', 'pg-target-broker-id', 'pg-target-source-id', 'pg-target-broker-name', 'pg-target-timezone'].forEach(id => {
    const el = pgDom(id);
    if (el) el.addEventListener(id === 'pg-target-profile' ? 'change' : 'input', pgUpdateTargetProfileUi);
  });
  pgLoadMinings();

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

  SQX_PG_BINDINGS.bindProjectGeneratorEvents(document, {
    autodetectSqx: pgAutodetectSqx,
    checkHealth: pgCheckHealth,
    deleteCustomPreset: pgDeleteCustomPreset,
    deleteSelectedMinings: pgDeleteSelectedMinings,
    deleteSelectedOutputFiles: pgDeleteSelectedOutputFiles,
    downloadSelectedOutputFiles: pgDownloadSelectedOutputFiles,
    exportCustomPresets: pgExportCustomPresets,
    clearSelectedMinings: pgClearSelectedMinings,
    generateCustom: pgGenerateCustom,
    generateSelected: pgGenerateSelected,
    importCustomPresets: pgImportCustomPresets,
    loadCustomPreset: pgLoadCustomPreset,
    loadConfig: pgLoadConfig,
    loadOutput: pgLoadOutput,
    openOutputFolder: pgOpenOutputFolder,
    openImportCustomPresets: pgOpenImportCustomPresets,
    runOnboardingAction: pgRunOnboardingAction,
    runOnboardingSecondaryAction: pgRunOnboardingSecondaryAction,
    runOnboardingTertiaryAction: pgRunOnboardingTertiaryAction,
    saveCustomPreset: pgSaveCustomPreset,
    saveConfig: pgSaveConfig,
    selectAllMinings: pgSelectAllMinings,
    setGenerationMode: pgSetGenerationMode,
    setSettingsOpen: pgSetSettingsOpen,
    suggestAll: pgSuggestAll,
    validateSqxPath: pgValidateSqxPath,
  });
  SQX_PG_BINDINGS.bindStrategyCleanerEvents(document, CLN_STATE, {
    previewRename: clnPreviewRename,
    process: clnProcess,
    renderTable: clnRenderTable,
    scan: clnScan,
  });
  SQX_PG_BINDINGS.bindProjectGeneratorPolling(window, document, {
    checkHealth: pgCheckHealth,
    renderOnboarding: pgRenderOnboarding,
  });
  SQX_PG_MODULE.getCurrentOutputFiles = () => (PG_STATE.outputFiles || []).slice();
  SQX_PG_MODULE.resetGeneratedCfxSession = pgResetGeneratedCfxSession;
  window.addEventListener('sqx:project-generator-output-reset', event => {
    pgResetGeneratedCfxSession(event && event.detail);
  });
  window.addEventListener('sqx:plan-minings-changed', () => {
    pgLoadMinings();
    pgRenderAliases();
    pgRenderOnboarding();
  });
  window.pgActivateProjectGenerationMode = pgSetGenerationMode;
})();

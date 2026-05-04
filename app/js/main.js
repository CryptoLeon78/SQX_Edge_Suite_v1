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
  const url = PG_API + path;
  const opts = Object.assign({}, options || {});
  if (opts.body && typeof opts.body !== 'string') {
    opts.body = JSON.stringify(opts.body);
    opts.headers = Object.assign({'Content-Type': 'application/json'}, opts.headers || {});
  }
  const r = await fetch(url, opts);
  const text = await r.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; }
  catch { data = { ok: false, error: text || ('HTTP ' + r.status) }; }
  if (!r.ok || data.ok === false) throw new Error(data.error || ('HTTP ' + r.status));
  return data;
}

function pgSetStatus(state, title, desc, meta) {
  const banner = document.getElementById('pg-status-banner');
  const t = document.getElementById('pg-status-title');
  const d = document.getElementById('pg-status-desc');
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
  if (!banner) return;
  banner.classList.remove('pg-status-up', 'pg-status-down', 'pg-status-loading');
  banner.classList.add('pg-status-' + state);
  if (t) t.textContent = title;
  if (d) d.textContent = desc;
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
  // Lista de assets únicos del plan (los obtenemos de la tabla minings ya cargada)
  // Si todavía no se han cargado, mostramos placeholder
  fetch(PG_API + '/minings').then(r => r.json()).then(minings => {
    const assets = [...new Set(minings.map(m => m.asset))].sort();
    tbl.innerHTML =
      '<table class="cat-table" style="font-size:12px;">' +
        '<thead><tr><th>Asset (plan)</th><th>Instrument SQX (alias)</th><th></th></tr></thead>' +
        '<tbody>' +
        assets.map(a => {
          const cur = PG_ALIASES[a] || '';
          return '<tr>' +
            '<td style="font-weight:700;">'+pgEsc(a)+'</td>' +
            '<td><input type="text" class="search-input" style="width:200px;font-size:12px;padding:4px 8px;" data-pg-alias="'+pgEsc(a)+'" value="'+pgEsc(cur)+'" placeholder="(default)"></td>' +
            '<td><button class="export-btn" style="padding:3px 10px;font-size:11px;" data-pg-suggest-asset="'+pgEsc(a)+'">🔍</button></td>' +
          '</tr>';
        }).join('') +
        '</tbody>' +
      '</table>';
    // Bind input change
    tbl.querySelectorAll('input[data-pg-alias]').forEach(inp => {
      inp.addEventListener('change', function(){
        const k = this.dataset.pgAlias;
        const v = this.value.trim();
        if (v) PG_ALIASES[k] = v;
        else delete PG_ALIASES[k];
      });
    });
    // Bind suggest button
    tbl.querySelectorAll('button[data-pg-suggest-asset]').forEach(btn => {
      btn.addEventListener('click', () => pgSuggestForAsset(btn.dataset.pgSuggestAsset));
    });
  }).catch(() => {
    tbl.innerHTML = '<div style="color:var(--text2);font-size:12px;">(esperando minings…)</div>';
  });
}

async function pgSuggestForAsset(asset) {
  try {
    const r = await pgFetch('/suggest-instruments/' + asset);
    if (!r.suggestions || !r.suggestions.length) {
      pgLog('Sin sugerencias para ' + asset + ' en data.db', 'err');
      pgRenderOnboarding();
      return;
    }
    // Mostrar prompt simple con las top 5 sugerencias
    const top = r.suggestions.slice(0, 5);
    const opts = top.map((s, i) => (i+1) + '. ' + s.instrument + ' [' + s.score + '%] — ' + (s.description || '') + ' (broker_id=' + s.broker_id + ')').join('\n');
    const choice = prompt('Sugerencias para "' + asset + '":\n\n' + opts + '\n\nElige número (1-' + top.length + ') o escribe el ticker manualmente:', '1');
    if (!choice) return;
    let chosen = '';
    const idx = parseInt(choice, 10);
    if (idx >= 1 && idx <= top.length) chosen = top[idx - 1].instrument;
    else chosen = choice.trim();
    PG_ALIASES[asset] = chosen;
    document.querySelector('input[data-pg-alias="' + asset + '"]').value = chosen;
    pgLog('Alias propuesto: ' + asset + ' → ' + chosen + ' (pulsa Guardar config)', 'info');
    pgTrace('Alias propuesto', asset + ' -> ' + chosen, 'info');
  } catch(e) { pgLog('Error sugiriendo: ' + e.message, 'err'); }
}

async function pgSuggestAll() {
  const inputs = document.querySelectorAll('input[data-pg-alias]');
  pgLog('Auto-sugiriendo para ' + inputs.length + ' assets…', 'info');
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
  pgLog('Auto-suggest: ' + found + ' aliases nuevos propuestos (pulsa Guardar config)', found > 0 ? 'ok' : 'info');
}

function pgDirClass(d) { return d === 'long' ? 'long' : d === 'short' ? 'short' : 'both'; }
function pgDirLabel(d) { return d === 'long' ? 'LONG' : d === 'short' ? 'SHORT' : 'L+S'; }

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
    const html = infos.map(m => {
      const info = m._info;
      const srcBadge = info && info.source === 'db'
        ? '<span class="pgm-src pgm-src-db" title="Costos leídos de data.db: ' + pgEsc(info.instrument) + ' spread=' + pgEsc(info.spread) + ' swap=' + pgEsc(info.swap_long) + '/' + pgEsc(info.swap_short) + '">📊 DB</span>'
        : '<span class="pgm-src pgm-src-fallback" title="Costos por defecto (data.db no disponible o asset no encontrado)">📋 Default</span>';
      const instrAlias = info && info.instrument && info.instrument !== m.asset
        ? '<span class="pgm-alias" title="Alias: ' + pgEsc(m.asset) + ' -> ' + pgEsc(info.instrument) + ' en SQX DB">→ ' + pgEsc(info.instrument) + '</span>'
        : '';
      return '<div class="pg-mining-row">' +
        '<div class="pgm-num">M' + String(m.num).padStart(2,'0') + '</div>' +
        '<div class="pgm-asset">' + pgEsc(m.asset) + instrAlias + '</div>' +
        '<div class="pgm-tf">' + pgEsc(m.tf) + '</div>' +
        '<div class="pgm-bs">' + pgEsc(m.bs) + '</div>' +
        '<div class="pgm-dir ' + pgDirClass(m.dir) + '">' + pgDirLabel(m.dir) + '</div>' +
        srcBadge +
        '<div class="pgm-actions">' +
          '<button class="pgm-btn c1" data-pg-gen="' + m.num + '" data-pg-capa="1">📦 Capa 1</button>' +
          '<button class="pgm-btn c2" data-pg-gen="' + m.num + '" data-pg-capa="2">📦 Capa 2</button>' +
        '</div>' +
      '</div>';
    });
    document.getElementById('pg-minings-table').innerHTML = html.join('');
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
    if (!r.files.length) {
      list.innerHTML = '<div class="pg-output-empty">No hay .cfx generados todavía. Pulsa un botón "📦 Capa 1/2" arriba.</div>';
      return;
    }
    list.innerHTML = r.files.map(f =>
      '<div class="pg-output-row">' +
        '<div class="pgo-name">' + pgEsc(f.name) + '</div>' +
        '<div class="pgo-size">' + pgEsc(f.size_kb) + ' KB</div>' +
        '<div class="pgo-time">' + new Date(f.mtime * 1000).toLocaleString() + '</div>' +
      '</div>').join('');
    pgRenderOnboarding();
  } catch(e) { pgLog('Error cargando output: ' + e.message, 'err'); }
}

async function pgGenerateOne(mining, capa) {
  pgLog('Generando Mining ' + mining + ' · Capa ' + capa + '…', 'info');
  try {
    const r = await pgFetch('/generate', { method:'POST', body: { mining, capa } });
    if (r.ok) {
      pgLog('✓ ' + r.filename, 'ok');
      pgTrace('Proyecto generado', 'Mining ' + mining + ' · Capa ' + capa + ' · ' + r.filename, 'ok');
      await pgLoadOutput();
    } else {
      pgLog('✗ ' + (r.error || 'fallo'), 'err');
      pgTrace('Error generando proyecto', 'Mining ' + mining + ' · ' + (r.error || 'fallo'), 'err');
    }
  } catch(e) { pgLog('✗ Error: ' + e.message, 'err'); pgTrace('Error generando proyecto', e.message, 'err'); }
}

async function pgGenerateAll(capa) {
  const countLabel = PG_PLAN_COUNT || 'todos los';
  if (!confirm('¿Generar ' + countLabel + ' minings en Capa ' + capa + '? Sobrescribe los existentes en output/.')) return;
  pgLog('Generando TODOS · Capa ' + capa + '…', 'info');
  try {
    const r = await pgFetch('/generate-all', { method:'POST', body: { capa } });
    pgLog('OK: ' + r.ok_count + ' · FAIL: ' + r.fail_count, r.fail_count === 0 ? 'ok' : 'err');
    pgTrace(
      'Generacion masiva completada',
      'Capa ' + capa + ' · OK ' + r.ok_count + ' · FAIL ' + r.fail_count,
      r.fail_count === 0 ? 'ok' : 'err'
    );
    r.results.forEach(x => {
      if (x.ok) pgLog('  ✓ M' + String(x.mining).padStart(2,'0') + ' → ' + x.filename, 'ok');
      else pgLog('  ✗ M' + String(x.mining).padStart(2,'0') + ' → ' + x.error, 'err');
    });
    await pgLoadOutput();
  } catch(e) { pgLog('✗ Error: ' + e.message, 'err'); pgTrace('Error en generacion masiva', e.message, 'err'); }
}

async function pgSaveConfig() {
  const body = {
    sqx_path: document.getElementById('pg-sqx-path').value.trim(),
    sqx_data_db: document.getElementById('pg-sqx-db').value.trim(),
    sqx_projects_dir: document.getElementById('pg-sqx-projects').value.trim(),
    output_dir: document.getElementById('pg-output-dir').value.trim(),
    template_capa1: document.getElementById('pg-tpl-c1').value.trim(),
    template_capa2: document.getElementById('pg-tpl-c2').value.trim(),
    asset_aliases: PG_ALIASES,
  };
  const msg = document.getElementById('pg-settings-msg');
  msg.textContent = 'Guardando…';
  try {
    const r = await pgFetch('/config', { method:'POST', body });
    msg.textContent = '✓ Guardado: ' + r.updated_keys.join(', ');
    msg.style.color = 'var(--green)';
    pgLog('Config actualizada (' + r.updated_keys.length + ' keys)', 'ok');
    pgTrace('Configuracion guardada', r.updated_keys.join(', '), 'ok');
    await pgCheckHealth();
  } catch(e) {
    msg.textContent = '✗ Error: ' + e.message;
    msg.style.color = 'var(--red)';
    pgTrace('Error guardando configuracion', e.message, 'err');
  }
}

// ── Listeners Project Generator ──
async function pgAutodetectSqx() {
  const out = document.getElementById('pg-autodetect-results');
  if (!out) return;
  out.innerHTML = '<div style="color:var(--text2);font-size:12px;">Buscando instalaciones de SQX...</div>';
  try {
    const r = await pgFetch('/autodetect-sqx');
    if (!r.found) {
      out.innerHTML = '<div class="alert warning"><div class="alert-icon">!</div><div class="alert-content"><strong>No se encontro ninguna instalacion de SQX.</strong>Edita los campos manualmente con la ruta donde este StrategyQuantX.exe.</div></div>';
      return;
    }
    out.innerHTML = '<div style="font-size:12px;color:var(--text2);margin-bottom:6px;">' + r.found + ' instalacion(es) detectada(s):</div>' +
      r.candidates.map((c, i) =>
        '<div class="pg-autodetect-row">' +
          '<div style="flex:1;">' +
            '<div style="font-weight:700;font-size:13px;">SQX v' + pgEsc(c.version) + (c.has_exe ? ' OK' : ' sin exe') + '</div>' +
            '<div style="font-family:Consolas,monospace;font-size:11px;color:var(--text2);">' + pgEsc(c.sqx_path) + '</div>' +
            '<div style="font-family:Consolas,monospace;font-size:10px;color:var(--text2);">-> data.db: ' + pgEsc(c.data_db) + '</div>' +
          '</div>' +
          '<button class="export-btn pg-use-btn" data-idx="' + i + '" style="border-color:var(--green);color:var(--green);">Usar esta</button>' +
        '</div>'
      ).join('');
    document.querySelectorAll('.pg-use-btn').forEach(btn => {
      btn.addEventListener('click', function(){
        const c = r.candidates[parseInt(this.dataset.idx, 10)];
        document.getElementById('pg-sqx-path').value = c.sqx_path;
        document.getElementById('pg-sqx-db').value = c.data_db;
        document.getElementById('pg-sqx-projects').value = c.projects_dir;
        pgLog('Path SQX seleccionado: ' + c.sqx_path + ' (pulsa Guardar config)', 'info');
        pgTrace('Ruta SQX detectada', c.sqx_path, 'info');
        pgRenderOnboarding();
        out.innerHTML = '<div class="alert success"><div class="alert-icon">OK</div><div class="alert-content"><strong>Aplicado.</strong> Pulsa "Guardar config" para persistir.</div></div>';
      });
    });
  } catch(e) {
    out.innerHTML = '<div style="color:var(--red);font-size:12px;">Error: ' + pgEsc(e.message) + '</div>';
  }
}

async function pgValidateSqxPath() {
  const path = document.getElementById('pg-sqx-path').value.trim();
  const out = document.getElementById('pg-autodetect-results');
  if (!out) return;
  if (!path) {
    out.innerHTML = '<div style="color:var(--yellow);font-size:12px;">Pon primero un SQX install path.</div>';
    return;
  }
  try {
    const r = await pgFetch('/validate-sqx-path', { method:'POST', body: { path } });
    const c = r.checks;
    const item = (label, ok) => '<li style="color:' + (ok ? 'var(--green)' : 'var(--red)') + ';">' + (ok ? 'OK' : 'X') + ' ' + label + '</li>';
    out.innerHTML = '<div class="alert ' + (r.valid ? 'success' : 'warning') + '"><div class="alert-icon">' + (r.valid ? 'OK' : '!') + '</div><div class="alert-content"><strong>' + (r.valid ? 'Path valido' : 'Path con problemas') + '</strong>' +
      '<ul style="margin-top:6px;padding-left:20px;font-size:12px;">' +
        item('Directorio base existe', c.base_exists) +
        item('user/data/data.db existe', c.data_db_exists) +
        item('user/projects existe', c.projects_exists) +
        item('StrategyQuantX.exe existe', c.exe_exists) +
      '</ul></div></div>';
    if (r.valid && r.resolved.data_db) {
      document.getElementById('pg-sqx-db').value = r.resolved.data_db;
      document.getElementById('pg-sqx-projects').value = r.resolved.projects_dir || '';
      pgTrace('Validacion SQX correcta', path, 'ok');
      pgRenderOnboarding();
    }
  } catch(e) {
    out.innerHTML = '<div style="color:var(--red);font-size:12px;">Error: ' + pgEsc(e.message) + '</div>';
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

  // Auto-detect SQX install
  document.getElementById('pg-autodetect').addEventListener('click', async function(){
    const out = document.getElementById('pg-autodetect-results');
    out.innerHTML = '<div style="color:var(--text2);font-size:12px;">🔍 Buscando instalaciones de SQX...</div>';
    try {
      const r = await pgFetch('/autodetect-sqx');
      if (!r.found) {
        out.innerHTML = '<div class="alert warning"><div class="alert-icon">⚠</div><div class="alert-content"><strong>No se encontró ninguna instalación de SQX.</strong>Edita los campos manualmente con la ruta donde esté StrategyQuantX.exe.</div></div>';
        return;
      }
      out.innerHTML = '<div style="font-size:12px;color:var(--text2);margin-bottom:6px;">'+r.found+' instalación(es) detectada(s):</div>' +
        r.candidates.map((c, i) =>
          '<div class="pg-autodetect-row">' +
            '<div style="flex:1;">' +
              '<div style="font-weight:700;font-size:13px;">SQX v'+pgEsc(c.version)+(c.has_exe?' ✓':' ⚠ sin .exe')+'</div>' +
              '<div style="font-family:Consolas,monospace;font-size:11px;color:var(--text2);">'+pgEsc(c.sqx_path)+'</div>' +
              '<div style="font-family:Consolas,monospace;font-size:10px;color:var(--text2);">→ data.db: '+pgEsc(c.data_db)+'</div>' +
            '</div>' +
            '<button class="export-btn pg-use-btn" data-idx="'+i+'" style="border-color:var(--green);color:var(--green);">Usar esta</button>' +
          '</div>'
        ).join('');
      // Bind use buttons
      document.querySelectorAll('.pg-use-btn').forEach(btn => {
        btn.addEventListener('click', function(){
          const c = r.candidates[parseInt(this.dataset.idx, 10)];
          document.getElementById('pg-sqx-path').value = c.sqx_path;
          document.getElementById('pg-sqx-db').value = c.data_db;
          document.getElementById('pg-sqx-projects').value = c.projects_dir;
          pgLog('Path SQX seleccionado: ' + c.sqx_path + ' (pulsa Guardar config)', 'info');
          pgTrace('Ruta SQX detectada', c.sqx_path, 'info');
          out.innerHTML = '<div class="alert success"><div class="alert-icon">✓</div><div class="alert-content"><strong>Aplicado.</strong> Pulsa "💾 Guardar config" para persistir.</div></div>';
        });
      });
    } catch(e) {
      out.innerHTML = '<div style="color:var(--red);font-size:12px;">Error: '+pgEsc(e.message)+'</div>';
    }
  });

  // Auto-sugerir aliases para todos los assets
  document.getElementById('pg-aliases-suggest').addEventListener('click', pgSuggestAll);

  // Validar paths actuales
  document.getElementById('pg-validate').addEventListener('click', async function(){
    const path = document.getElementById('pg-sqx-path').value.trim();
    const out = document.getElementById('pg-autodetect-results');
    if (!path) { out.innerHTML = '<div style="color:var(--yellow);font-size:12px;">Pon primero un SQX install path.</div>'; return; }
    try {
      const r = await pgFetch('/validate-sqx-path', { method:'POST', body: { path } });
      const c = r.checks;
      const item = (label, ok) => '<li style="color:'+(ok?'var(--green)':'var(--red)')+';">'+(ok?'✓':'✗')+' '+label+'</li>';
      out.innerHTML = '<div class="alert '+(r.valid?'success':'warning')+'"><div class="alert-icon">'+(r.valid?'✓':'⚠')+'</div><div class="alert-content"><strong>'+(r.valid?'Path válido':'Path con problemas')+'</strong>' +
        '<ul style="margin-top:6px;padding-left:20px;font-size:12px;">' +
          item('Directorio base existe', c.base_exists) +
          item('user/data/data.db existe', c.data_db_exists) +
          item('user/projects/ existe', c.projects_exists) +
          item('StrategyQuantX.exe existe', c.exe_exists) +
        '</ul></div></div>';
      if (r.valid && r.resolved.data_db) {
        document.getElementById('pg-sqx-db').value = r.resolved.data_db;
        document.getElementById('pg-sqx-projects').value = r.resolved.projects_dir || '';
        pgTrace('Validacion SQX correcta', path, 'ok');
      }
    } catch(e) {
      out.innerHTML = '<div style="color:var(--red);font-size:12px;">Error: '+pgEsc(e.message)+'</div>';
      pgTrace('Error validando SQX', e.message, 'err');
    }
  });

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
      info.textContent = '✓ ' + r.count + ' archivos .sqx encontrados';
      info.style.color = 'var(--green)';
      clnRenderTable();
      document.getElementById('cln-actions').style.display = r.count > 0 ? 'block' : 'none';
    } catch(e) { info.textContent = '✗ ' + e.message; info.style.color='var(--red)'; }
  }

  function clnRenderTable() {
    const tbl = document.getElementById('cln-table');
    if (!CLN_FILES.length) { tbl.innerHTML = ''; return; }
    tbl.innerHTML =
      '<div class="matrix-wrap" style="max-height:380px;">' +
        '<table class="cat-table" style="font-size:11px;">' +
          '<thead><tr>' +
            '<th style="width:30px;"><input type="checkbox" id="cln-th-check"></th>' +
            '<th>Archivo</th><th>Asset</th><th>TF</th><th>Dir</th>' +
            '<th>EAB</th><th>ID</th><th>KB</th>' +
          '</tr></thead><tbody>' +
          CLN_FILES.map(f => {
            const checked = CLN_SELECTED.has(f.path) ? 'checked' : '';
            const eabCls = f.exit_after_bars_count > 0 ? 'cv-num warn' : 'cv-num pos';
            return '<tr>' +
              '<td><input type="checkbox" class="cln-row-check" data-path="'+pgEsc(f.path)+'" '+checked+'></td>' +
              '<td style="font-family:Consolas,monospace;">'+pgEsc(f.name)+'</td>' +
              '<td><strong>'+pgEsc(f.asset)+'</strong></td>' +
              '<td>'+pgEsc(f.timeframe)+'</td>' +
              '<td>'+pgEsc(f.direction)+'</td>' +
              '<td class="'+eabCls+'">'+pgEsc(f.exit_after_bars_count)+'</td>' +
              '<td>'+pgEsc(f.fitness_id)+'</td>' +
              '<td style="color:var(--text2);">'+pgEsc(f.size_kb)+'</td>' +
            '</tr>';
          }).join('') +
        '</tbody></table></div>';
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
    document.getElementById('cln-selected').textContent = CLN_SELECTED.size + ' seleccionadas';
  }

  async function clnPreviewRename() {
    if (!CLN_SELECTED.size) { pgLog('No hay nada seleccionado', 'err'); return; }
    const pattern = document.getElementById('cln-pattern').value.trim() || '{asset}_{tf}_{dir}_{id}';
    try {
      const r = await pgFetch('/sqx-preview-rename', { method:'POST', body: { files: [...CLN_SELECTED], pattern } });
      pgLog('Preview rename para ' + r.previews.length + ' archivos:', 'info');
      r.previews.forEach(p => {
        if (p.error) pgLog('  ✗ ' + p.path + ': ' + p.error, 'err');
        else pgLog('  ' + p.current + ' → ' + p.new_name, 'info');
      });
    } catch(e) { pgLog('Error preview: ' + e.message, 'err'); }
  }

  async function clnProcess() {
    if (!CLN_SELECTED.size) { pgLog('No hay nada seleccionado', 'err'); return; }
    const opts = {
      remove_exit_bars: document.getElementById('cln-opt-eab').checked,
      rename_institutional: document.getElementById('cln-opt-rename').checked,
      rename_pattern: document.getElementById('cln-pattern').value.trim() || '{asset}_{tf}_{dir}_{id}',
    };
    if (!opts.remove_exit_bars && !opts.rename_institutional) {
      pgLog('Selecciona al menos una acción', 'err'); return;
    }
    const msg = `¿Procesar ${CLN_SELECTED.size} archivos?\n\n` +
      (opts.remove_exit_bars ? '• Eliminar ExitAfterBars (set 0)\n' : '') +
      (opts.rename_institutional ? `• Renombrar a: ${opts.rename_pattern}\n` : '') +
      '\nSe crea backup automático antes de modificar cada .sqx.';
    if (!confirm(msg)) return;
    pgLog('🧹 Procesando ' + CLN_SELECTED.size + ' archivos...', 'info');
    try {
      const r = await pgFetch('/sqx-clean', { method:'POST', body: { files: [...CLN_SELECTED], options: opts } });
      pgLog('Resultado: ' + r.ok_count + ' OK · ' + r.fail_count + ' FAIL', r.fail_count === 0 ? 'ok' : 'err');
      pgTrace(
        'Limpieza SQX completada',
        CLN_SELECTED.size + ' archivos · OK ' + r.ok_count + ' · FAIL ' + r.fail_count,
        r.fail_count === 0 ? 'ok' : 'err'
      );
      r.results.forEach(x => {
        const fname = x.path.split(/[\\/]/).pop();
        if (x.ok) pgLog('  ✓ ' + fname + ' — ' + x.actions.join(', '), 'ok');
        else pgLog('  ✗ ' + fname + ' — ' + x.actions.join(', '), 'err');
      });
      // Re-scan al terminar
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

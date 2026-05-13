// ============================================================
// DATA
// ============================================================

// ============================================================
// STATE
// ============================================================

const STATE = {
  selectedAsset:   null,
  filterType:      'all',
  filterDir:       'all',
  filterCatRating: 'all',
  filterCatSub:    'all',
  filterCatTf:     'all',
  assetSort:       'name',
};
// Proxy shortcuts for backward compat with render functions
let selectedAsset   = null;
let filterType      = 'all';
let filterSqx       = 'all';
let filterDir       = 'all';
let filterCatRating = 'all';
let filterCatSub    = 'all';
let filterCatTf     = 'all';
let assetSort       = 'name';

const sortState   = { cat:{} };
const collapseMap = {};
const DEFAULT_CATEGORY_COLLAPSED = true;
const SQX_MODULES = window.SQX || {};
const SQX_CONFIG_API = SQX_MODULES.config || {};
const SQX_RUNTIME_CONFIG = SQX_CONFIG_API.raw || window.SQX_CONFIG || { ui:{}, storageKeys:{}, value:function(_path, fallback){ return fallback; } };
const SQX_UI_CONFIG = SQX_CONFIG_API.ui ? SQX_CONFIG_API.ui() : SQX_RUNTIME_CONFIG.ui || {};
const SQX_STORAGE_KEYS = SQX_CONFIG_API.storageKeys ? SQX_CONFIG_API.storageKeys() : SQX_RUNTIME_CONFIG.storageKeys || {};
const SQX_UI_MODULE = SQX_MODULES.ui || {};
const SQX_FORMATTERS = SQX_MODULES.formatters || {};
const SQX_DOMAIN = SQX_MODULES.domain || {};
const SQX_DATASETS = SQX_MODULES.datasets || {};
const SQX_RENDERERS = SQX_MODULES.renderers || {};
const SQX_CHARTS = SQX_MODULES.charts || {};
const SQX_STRATEGIES = SQX_MODULES.strategies || {};
const SQX_HOME = SQX_MODULES.home || {};
const SQX_STORAGE = SQX_MODULES.storage || {
  getJson:function(key, fallback){ try { return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback)); } catch(e){ return fallback; } },
  setJson:function(key, value){ localStorage.setItem(key, JSON.stringify(value)); return true; }
};

function sqxConfigValue(path, fallback) {
  if (SQX_CONFIG_API.value) return SQX_CONFIG_API.value(path, fallback);
  return SQX_RUNTIME_CONFIG.value ? SQX_RUNTIME_CONFIG.value(path, fallback) : fallback;
}

if (SQX_MODULES.registerModule) {
  SQX_MODULES.registerModule('dashboard-legacy', {
    state: STATE,
    config: {
      ui: SQX_UI_CONFIG,
      storageKeys: SQX_STORAGE_KEYS,
      value: sqxConfigValue
    }
  });
}

function sqxStatusMeta(status) {
  if (SQX_CONFIG_API.statusMeta) return SQX_CONFIG_API.statusMeta(status);
  const statuses = SQX_UI_CONFIG.statuses || [];
  return statuses.find(s => s.id === status) || { id: status, label: status };
}

function sqxStatusSequence() {
  if (SQX_CONFIG_API.statusSequence) return SQX_CONFIG_API.statusSequence();
  const statuses = SQX_UI_CONFIG.statuses || [];
  return statuses.length ? statuses.map(s => s.id) : ['pending', 'current', 'completed'];
}

// ============================================================
// SCORE
// ============================================================
function calcScore(asset, dirFilter) {
  if (SQX_DOMAIN.calcScore) return SQX_DOMAIN.calcScore(asset, dirFilter, RATING_ORDER);
  return { raw: 0, count: 0, norm: 0 };
}

// ============================================================
// HELPERS
// ============================================================
function rLabel(r) {
  if (SQX_FORMATTERS.ratingLabel) return SQX_FORMATTERS.ratingLabel(r);
  if (r==='++') return { text:'Estrella', cls:'rating-pp' };
  if (r==='+')  return { text:'Bueno',    cls:'rating-p'  };
  if (r==='~')  return { text:'Precauc.', cls:'rating-t'  };
  return { text:'No recom.', cls:'rating-m' };
}
function hmCls(r) {
  if (SQX_FORMATTERS.heatmapClass) return SQX_FORMATTERS.heatmapClass(r);
  if (r==='++') return 'hm-pp'; if (r==='+') return 'hm-p';
  if (r==='~')  return 'hm-t';  if (r==='-') return 'hm-m';
  return '';
}
function dirCls(d) {
  return SQX_FORMATTERS.assetDirectionClass ? SQX_FORMATTERS.assetDirectionClass(d) : d==='L' ? 'dir-long' : d==='S' ? 'dir-short' : 'dir-both';
}

// SQX Config: A = Both + Entry Symmetry, B = Both sin symmetry, C = Only Long, D = Only Short
function getSqxConfig(asset) {
  return SQX_DOMAIN.getSqxConfig ? SQX_DOMAIN.getSqxConfig(asset) : { code:'B', label:'Both sin Symmetry', desc:'Both (Long & Short) con Symmetry OFF. SQX optimiza L y S por separado.' };
}
function sqxBadge(asset, mini=false) {
  const c = getSqxConfig(asset);
  return SQX_RENDERERS.sqxBadge ? SQX_RENDERERS.sqxBadge(c, mini) : '';
}

// Replica visual del panel "Trading directions settings" de SQX según el código de config (A/B/C/D)
function sqxPreviewHTML(code) {
  return SQX_RENDERERS.sqxPreviewHTML ? SQX_RENDERERS.sqxPreviewHTML(code) : '';
}


let HISTORICAL = SQX_DATASETS.historical ? SQX_DATASETS.historical() : {};

// Data-driven scores (Dukascopy H1 2010-2026)
let SCORES = SQX_DATASETS.scores ? SQX_DATASETS.scores() : {};

function getScore(assetId, catKey) {
  if (SQX_DOMAIN.scoreFromScores) return SQX_DOMAIN.scoreFromScores(SCORES, assetId, catKey);
  return null;
}

// Sobreescribe los ratings editoriales en ASSETS con los data-driven (Dukascopy H1).
// Tras esto toda la UI (grid, cat-cards, tablas y vistas de prioridad) usa automaticamente
// los ratings objetivos calculados desde datos reales.
function applyObjectiveRatings() {
  if (SQX_DOMAIN.applyObjectiveRatings) SQX_DOMAIN.applyObjectiveRatings(ASSETS, SCORES, getScore);
}
applyObjectiveRatings();

function ratingPairBadge(score) {
  return SQX_RENDERERS.ratingPairBadge ? SQX_RENDERERS.ratingPairBadge(score) : '';
}

function compositeBar(score) {
  return SQX_RENDERERS.compositeBar ? SQX_RENDERERS.compositeBar(score) : '';
}

function historyChartSVG(assetId) {
  const data = HISTORICAL[assetId];
  return SQX_CHARTS.renderHistoryChart
    ? SQX_CHARTS.renderHistoryChart(assetId, data, MACRO_EVENTS, sqxConfigValue('chart', {}))
    : '';
}

function historySection(assetId) {
  const chartHtml = HISTORICAL[assetId] ? historyChartSVG(assetId) : '';
  return SQX_RENDERERS.historySection
    ? SQX_RENDERERS.historySection(assetId, HISTORICAL, chartHtml, MACRO_EVENTS)
    : '';
}

function renderSqxLegend() {
  const codes = ['A','B','C','D'];
  document.getElementById('sqx-legend-grid').innerHTML = SQX_RENDERERS.sqxLegend
    ? SQX_RENDERERS.sqxLegend(codes, SQX_CONFIG_DESC, sqxPreviewHTML)
    : '';
}
function tfMatch(tf, filter) {
  return SQX_DOMAIN.tfMatch ? SQX_DOMAIN.tfMatch(tf, filter) : filter==='all' || tf.includes(filter);
}
function thH(label, col, ctx, key) {
  return SQX_RENDERERS.sortableHeader
    ? SQX_RENDERERS.sortableHeader(label, col, ctx, key, sortState.cat[key] || {})
    : '';
}
window.doSort = function doSort(ctx, key, col) {
  if (ctx==='cat') {
    if (!sortState.cat[key]) sortState.cat[key]={col:null,dir:null};
    const s=sortState.cat[key];
    if (s.col===col) { s.dir = s.dir==='asc'?'desc':(s.dir==='desc'?null:'asc'); if(!s.dir) s.col=null; }
    else { s.col=col; s.dir='asc'; }
    renderCategoriesView();
  }
}
function sortRows(rows, col, dir) {
  return SQX_DOMAIN.sortRows ? SQX_DOMAIN.sortRows(rows, col, dir, RATING_ORDER) : rows;
}
function sparkHTML(asset) {
  return SQX_RENDERERS.sparkHTML ? SQX_RENDERERS.sparkHTML(asset, CAT_KEYS, CAT_META) : '';
}

// ============================================================
// RENDER: ASSET GRID
// ============================================================
// Filtro SQX:
//   A / B → match contra la config primaria recomendada (getSqxConfig)
//   C     → activos con ≥1 categoría dir:'L' (ideas Long puras — índices/oro)
//   D     → activos con ≥1 categoría dir:'S' (ideas Short puras — índices/oro)
function assetMatchesSqxFilter(a, code) {
  return SQX_DOMAIN.assetMatchesSqxFilter ? SQX_DOMAIN.assetMatchesSqxFilter(a, code) : true;
}

function renderAssetGrid() {
  const search = document.getElementById('search-asset').value.toUpperCase();
  let list = ASSETS.filter(a => {
    if (filterType!=='all' && a.type!==filterType) return false;
    if (!assetMatchesSqxFilter(a, filterSqx)) return false;
    if (search && !a.id.includes(search)) return false;
    return true;
  }).map(a => ({ ...a, sc: calcScore(a,'all') }));

  if (assetSort==='score-desc') list.sort((a,b)=>b.sc.raw-a.sc.raw);
  else if (assetSort==='score-asc') list.sort((a,b)=>a.sc.raw-b.sc.raw);
  else if (assetSort==='cats-desc') list.sort((a,b)=>b.sc.count-a.sc.count);
  else list.sort((a,b)=>a.id.localeCompare(b.id));

  document.getElementById('asset-grid').innerHTML = list.map(a =>
    `<div class="asset-card type-${a.type}${selectedAsset===a.id?' selected':''}" onclick="selectAsset('${a.id}')">
      <div class="name">${a.id}</div>
      <span class="type-badge">${a.sub}</span>
      ${sparkHTML(a)}
      <div class="score-badge">Score: <span>${a.sc.norm}%</span></div>
      <div style="margin-top:6px">${sqxBadge(a, true)}</div>
    </div>`
  ).join('');
}

window.selectAsset = function selectAsset(id) {
  selectedAsset = id; renderAssetGrid(); renderDetail();
}

// ============================================================
// RENDER: DETAIL
// ============================================================
function renderDetail() {
  const panel = document.getElementById('detail-panel');
  if (!selectedAsset) { panel.classList.remove('visible'); return; }
  const a = ASSETS.find(x=>x.id===selectedAsset);
  if (!a) return;
  panel.classList.add('visible');

  const baseCats = {};
  for (const [key,val] of Object.entries(a.cats)) {
    const base = key.replace(/_S$/,'');
    if (!baseCats[base]) baseCats[base]=[];
    baseCats[base].push({...val, isShort:key.endsWith('_S')});
  }
  const sc = calcScore(a,'all');
  const typeBg    = a.type==='forex'?'rgba(59,130,246,.15)':a.type==='index'?'rgba(168,85,247,.15)':'rgba(234,179,8,.15)';
  const typeColor = a.type==='forex'?'var(--accent)':a.type==='index'?'var(--purple)':'var(--yellow)';

  const sqxConf = getSqxConfig(a);
  const sqxMeta = SQX_CONFIG_DESC[sqxConf.code] || { label:sqxConf.label, desc:sqxConf.desc };
  let html = `<div class="detail-header">
    <div class="asset-name">${a.id}</div>
    <span class="asset-type" style="background:${typeBg};color:${typeColor}">${a.sub}</span>
    ${sqxBadge(a)}
    <div class="asset-desc">${Object.keys(baseCats).length} categorias | ${a.type==='forex'?'L/S simetrico':'Long != Short'}</div>
    <div class="detail-score">${sc.norm}%<small>score global</small></div>
  </div>
  <div class="sqx-detail-box">
    ${sqxPreviewHTML(sqxConf.code)}
    <div class="sqx-detail-text">
      <strong>Config SQX ${sqxConf.code} · ${sqxConf.label}</strong>
      ${sqxMeta.desc}
    </div>
  </div>
  ${historySection(a.id)}
  <div class="cat-cards">`;

  for (const [catKey,entries] of Object.entries(baseCats)) {
    const meta = CAT_META[catKey]; if (!meta) continue;
    for (const entry of entries) {
      const r = rLabel(entry.rating);
      const dLabel = entry.dir==='L'?'LONG':entry.dir==='S'?'SHORT':'LONG / SHORT';
      const sc = getScore(a.id, catKey);
      const tip = sc && sc.metrics
        ? Object.entries(sc.metrics).map(([k,v]) => k+'='+v).join(' · ')
        : '';
      html += `<div class="cat-card">
        <div class="cat-card-header">
          <div class="cat-icon" style="background:${meta.color}22;color:${meta.color}">${meta.icon}</div>
          <div class="cat-name">${meta.name}</div>
          <span class="rating ${r.cls}" title="${tip}">${r.text}</span>
        </div>
        <div class="info-row"><span class="info-label">Direccion</span><span class="info-value ${dirCls(entry.dir)}">${dLabel}</span></div>
        <div class="info-row"><span class="info-label">Timeframes</span><span class="info-value">${entry.tf}</span></div>
        <div class="info-row"><span class="info-label">Por que</span><span class="info-value" style="font-weight:400;font-size:12px">${entry.why}</span></div>
        ${compositeBar(sc)}
        <div class="quick-actions">
          <button class="action-btn btn-plan" onclick="event.stopPropagation();quickAddToPlan('${a.id}','${entry.isShort ? catKey + '_S' : catKey}','${entry.tf}','${entry.dir}')">+ Plan</button>
          <button class="action-btn btn-pg" onclick="event.stopPropagation();quickToProjectGen('${a.id}','${entry.isShort ? catKey + '_S' : catKey}','${entry.tf}','${entry.dir}')">Gen Project</button>
        </div>
      </div>`;
    }
  }
  html += '</div>';
  panel.innerHTML = html;
  panel.scrollIntoView({behavior:'smooth',block:'nearest'});
}

// ============================================================
// RENDER: CATEGORIES
// ============================================================
function renderCategoriesView() {
  let html='';
  for (const [catKey,meta] of Object.entries(CAT_META)) {
    let rows=[];
    for (const a of ASSETS) {
      for (const [key,val] of Object.entries(a.cats)) {
        const base=key.replace(/_S$/,'');
        if (base!==catKey) continue;
        if (filterDir==='L'&&val.dir==='S') continue;
        if (filterDir==='S'&&val.dir==='L') continue;
        if (filterCatRating!=='all'&&val.rating!==filterCatRating) continue;
        if (filterCatSub!=='all'&&a.sub!==filterCatSub) continue;
        if (filterCatTf!=='all'&&!tfMatch(val.tf,filterCatTf)) continue;
        rows.push({asset:a,...val,isShort:key.endsWith('_S')});
      }
    }
    const s=sortState.cat[catKey]||{col:null,dir:null};
    rows=sortRows(rows,s.col,s.dir);
    const collapsed=collapseMap[catKey]??DEFAULT_CATEGORY_COLLAPSED;
    const maxH=collapsed?'0':'2000px';

    html+=`<div class="category-section">
      <div class="category-header-row" onclick="toggleCat('${catKey}')">
        <div class="cat-icon" style="background:${meta.color}22;color:${meta.color}">${meta.icon}</div>
        <h2>${meta.name}</h2>
        <span class="cat-desc">${meta.desc}</span>
        <span style="color:var(--text2);font-size:13px;margin-right:8px">${rows.length} activos</span>
        <span class="collapse-arrow${collapsed?' closed':''}">▼</span>
      </div>
      <div class="cat-body" style="max-height:${maxH}">`;

    if (rows.length) {
      html+=`<table class="cat-table" style="margin-top:8px"><thead><tr>
        ${thH('Activo','asset','cat',catKey)}
        ${thH('Tipo','sub','cat',catKey)}
        ${thH('Dir','dir','cat',catKey)}
        ${thH('Timeframes','tf','cat',catKey)}
        ${thH('Rating','rating','cat',catKey)}
        <th>Por que</th>
        <th>Acciones</th>
      </tr></thead><tbody>`;
      for (const row of rows) {
        const r=rLabel(row.rating);
        const dl=row.dir==='L'?'LONG':row.dir==='S'?'SHORT':'L/S';
        html+=`<tr>
          <td><span class="asset-link" onclick="event.stopPropagation();navToAsset('${row.asset.id}')">${row.asset.id}</span></td>
          <td>${row.asset.sub}</td>
          <td class="${dirCls(row.dir)}" style="font-weight:700">${dl}</td>
          <td>${row.tf}</td>
          <td><span class="rating ${r.cls}">${r.text}</span></td>
          <td style="font-size:12px;color:var(--text2);max-width:280px">${row.why}</td>
          <td>
            <div class="quick-actions" style="margin-top:0">
              <button class="action-btn btn-plan" onclick="event.stopPropagation();quickAddToPlan('${row.asset.id}','${row.isShort ? catKey + '_S' : catKey}','${row.tf}','${row.dir}')" title="Añadir a Mining Control">+ Plan</button>
              <button class="action-btn btn-pg" onclick="event.stopPropagation();quickToProjectGen('${row.asset.id}','${row.isShort ? catKey + '_S' : catKey}','${row.tf}','${row.dir}')" title="Ir al Project Generator">Gen</button>
            </div>
          </td>
        </tr>`;
      }
      html+='</tbody></table>';
    } else {
      html+='<div class="no-data">No hay activos para este filtro</div>';
    }
    html+='</div></div>';
  }
  document.getElementById('categories-view').innerHTML=html;
}

window.toggleCat = function toggleCat(key) {
  collapseMap[key]=!(collapseMap[key]??DEFAULT_CATEGORY_COLLAPSED);
  renderCategoriesView();
}

// ============================================================
// RENDER: FILTROS
// ============================================================
function renderFiltros() {
  document.getElementById('filtros-view').innerHTML=FILTROS.map(f=>`<div class="filtro-card">
    <h3>${f.name}</h3><div class="filtro-desc">${f.desc}</div>
    <div class="thresholds">
      <div class="threshold threshold-long"><div class="th-label">Long</div>${f.long}</div>
      <div class="threshold threshold-short"><div class="th-label">Short</div>${f.short}</div>
    </div>
  </div>`).join('');
}

// ============================================================
// SQX PRIORITY — lista ranked por composite data-driven
// ============================================================

function priorityTier(pct) {
  const tiers = SQX_UI_CONFIG.priorityTiers || [];
  const found = tiers.find(t => pct >= t.min);
  if (found) return found;
  return { label: 'SKIP', cls: 'tier-skip', color: 'var(--text2)' };
}

let filterPriorityMin  = 0;
let filterPriorityCat  = 'all';
let filterPriorityType = 'all';

function renderPriority() {
  const rows = [];
  for (const a of ASSETS) {
    if (filterPriorityType !== 'all' && a.type !== filterPriorityType) continue;
    const baseSeen = new Set();
    for (const [catKey, entry] of Object.entries(a.cats)) {
      const base = catKey.endsWith('_S') ? catKey.slice(0, -2) : catKey;
      if (baseSeen.has(base)) continue;
      baseSeen.add(base);
      const sc = getScore(a.id, catKey);
      if (!sc || sc.composite === null || sc.composite === undefined) continue;
      const pct = Math.round(sc.composite * 100);
      const meta = CAT_META[base] || {};
      // Split timeframes y crear una fila independiente por cada TF
      // → permite trackear "en curso" por (activo, categoría, TF) específico
      const tfs = (entry.tf || '').split(',').map(t => t.trim()).filter(Boolean);
      const tfList = tfs.length ? tfs : [''];
      for (const tf of tfList) {
        rows.push({
          asset: a.id, type: a.type, sub: a.sub, dir: entry.dir, tf: tf,
          cat: base, catName: meta.name || base, catColor: meta.color || '#888', catIcon: meta.icon || '?',
          rating: entry.rating, composite: pct,
        });
      }
    }
  }
  let filtered = rows.filter(r => r.composite >= filterPriorityMin);
  if (filterPriorityCat !== 'all') filtered = filtered.filter(r => r.cat === filterPriorityCat);
  filtered.sort((a, b) => b.composite - a.composite);

  // Resumen tier counts
  const tierLabels = (SQX_UI_CONFIG.priorityTiers || []).map(t => t.label);
  const tierCounts = Object.fromEntries((tierLabels.length ? tierLabels : ['MAXIMA','ALTA','SECUNDARIA','BAJA','SKIP']).map(label => [label, 0]));
  for (const r of filtered) tierCounts[priorityTier(r.composite).label]++;
  const summaryHtml = Object.entries(tierCounts).map(([label,count]) => {
    const tierCfg = (SQX_UI_CONFIG.priorityTiers || []).find(t => t.label === label);
    const tier = tierCfg || priorityTier(label==='MAXIMA'?90:label==='ALTA'?75:label==='SECUNDARIA'?60:label==='BAJA'?45:0);
    return '<div class="priority-summary-card"><div class="ps-count" style="color:'+tier.color+'">'+count+'</div><div class="ps-label">'+label+'</div></div>';
  }).join('');
  document.getElementById('priority-summary').innerHTML = summaryHtml;

  let html = '<thead><tr>'
    + '<th style="width:40px">#</th>'
    + '<th style="width:90px">Tier</th>'
    + '<th>Activo</th>'
    + '<th>Categoría</th>'
    + '<th>Blocksetting</th>'
    + '<th style="width:170px">Composite</th>'
    + '<th>Rating</th>'
    + '<th>Dir</th>'
    + '<th>Timeframes</th>'
    + '<th>Approach SQX sugerido</th>'
    + '<th style="width:130px">Estado</th>'
    + '</tr></thead><tbody>';

  let pCount=0, cCount=0, dCount=0;
  filtered.forEach((r, i) => {
    const tier = priorityTier(r.composite);
    const hint = APPROACH_HINTS[r.cat] || '';
    const rl = rLabel(r.rating);
    const dLabel = r.dir==='L'?'LONG':r.dir==='S'?'SHORT':'L/S';
    const dCls = dirCls(r.dir);
    const rowId = r.asset+'|'+r.cat+'|'+r.tf+'|'+r.dir;
    const status = (PRIORITY_PROGRESS[rowId] && PRIORITY_PROGRESS[rowId].status) || 'pending';
    if (status==='completed') dCount++; else if (status==='current') cCount++; else pCount++;
    // Match con minings del plan (B.3 sync)
    const planRef = (typeof PLAN_MININGS !== 'undefined') ? PLAN_MININGS.find(m =>
      m.asset === r.asset && BS_TO_PRIORITY_CAT[m.bs] === r.cat && m.tf === r.tf && m.dir === r.dir
    ) : null;
    const planBadge = planRef ? '<span class="ps-pin-badge" title="Mining '+planRef.num+' del plan operativo (Mining Control)">📌 M'+planRef.num+'</span>' : '';
    html += '<tr>'
      + '<td style="font-weight:700;color:var(--text2)">'+(i+1)+planBadge+'</td>'
      + '<td><span class="tier-badge '+tier.cls+'">'+tier.label+'</span></td>'
      + '<td><span class="asset-link" onclick="navToAsset(\''+r.asset+'\')">'+r.asset+'</span> <span style="color:var(--text2);font-size:11px">'+r.sub+'</span></td>'
      + '<td><span style="color:'+r.catColor+';font-weight:700;display:inline-block;width:18px">'+r.catIcon+'</span> '+r.catName+'</td>'
      + '<td><code style="font-size:11px;color:var(--text2)">'+(CAT_TO_BS[r.cat]||'-')+'</code></td>'
      + '<td><span class="priority-bar-wrap"><span class="priority-bar" style="width:'+r.composite+'%;background:'+tier.color+'"></span></span><span style="font-weight:700">'+r.composite+'%</span></td>'
      + '<td><span class="rating '+rl.cls+'">'+rl.text+'</span></td>'
      + '<td class="'+dCls+'" style="font-weight:700;font-size:12px">'+dLabel+'</td>'
      + '<td style="font-size:12px">'+r.tf+'</td>'
      + '<td style="font-size:12px;color:var(--text2)">'+hint+'</td>'
      + '<td>' + statusBadgeHtml(rowId, status) + '</td>'
      + '</tr>';
  });
  html += '</tbody>';
  if (!filtered.length) html += '<tbody><tr><td colspan="11" class="no-data">Sin resultados con esos filtros</td></tr></tbody>';
  document.getElementById('priority-table').innerHTML = html;

  // Update progress bar and stats
  const total = filtered.length;
  const pct = total ? Math.round(dCount/total*100) : 0;
  document.getElementById('priority-progress-text').textContent = 'Progreso: ' + dCount + ' de ' + total + ' completados';
  document.getElementById('priority-progress-pct').textContent = pct + '%';
  document.getElementById('priority-progress-fill').style.width = pct + '%';
}

// ============================================================
// CSV EXPORT
// ============================================================
function doExport(data,filename) {
  const csv=data.map(r=>r.map(c=>`"${String(c).replace(/"/g,'""')}"`).join(',')).join('\n');
  const blob=new Blob(['\uFEFF'+csv],{type:'text/csv;charset=utf-8;'});
  const url=URL.createObjectURL(blob);
  Object.assign(document.createElement('a'),{href:url,download:filename}).click();
  URL.revokeObjectURL(url);
}
function exportCatCSV() {
  const rows=[['Activo','Tipo','Categoria','Direccion','Timeframes','Rating','Por que']];
  for (const [catKey,meta] of Object.entries(CAT_META)) {
    for (const a of ASSETS) {
      for (const [key,val] of Object.entries(a.cats)) {
        const base=key.replace(/_S$/,'');
        if (base!==catKey) continue;
        if (filterDir==='L'&&val.dir==='S') continue;
        if (filterDir==='S'&&val.dir==='L') continue;
        if (filterCatRating!=='all'&&val.rating!==filterCatRating) continue;
        if (filterCatSub!=='all'&&a.sub!==filterCatSub) continue;
        if (filterCatTf!=='all'&&!tfMatch(val.tf,filterCatTf)) continue;
        rows.push([a.id,a.sub,meta.name,val.dir,val.tf,val.rating,val.why]);
      }
    }
  }
  doExport(rows,'SQX_categorias.csv');
}

// ============================================================
// STRATEGIES — repositorio de .sqx supervivientes
// Para añadir una estrategia: usa el modal "+ Añadir estrategia" en el tab,
// pulsa "Generar JSON", copia el snippet y pégalo dentro del array.
// ============================================================

let stratFilterMining   = 'all';
let stratFilterTemplate = 'all';
let stratFilterTier     = 'all';
let stratFilterStatus   = 'all';

function tierClass(tier) {
  if (SQX_FORMATTERS.tierClass) return SQX_FORMATTERS.tierClass(tier);
  if (tier === '1')   return 'tier-1';
  if (tier === '1.5') return 'tier-15';
  if (tier === '2')   return 'tier-2';
  return 'tier-tentativa';
}
function tierLabel(tier) {
  if (SQX_FORMATTERS.tierLabel) return SQX_FORMATTERS.tierLabel(tier);
  if (tier === '1')   return 'TIER 1';
  if (tier === '1.5') return 'TIER 1.5';
  if (tier === '2')   return 'TIER 2';
  return 'TENTATIVA';
}
function dirClass(d) {
  if (SQX_FORMATTERS.strategyDirectionClass) return SQX_FORMATTERS.strategyDirectionClass(d);
  if (d === 'L')   return 'dir-L';
  if (d === 'S')   return 'dir-S';
  return 'dir-LS';
}
function metricClass(label, val) {
  if (SQX_FORMATTERS.metricClass) return SQX_FORMATTERS.metricClass(label, val);
  if (val == null) return '';
  if (label === 'PF')      return val >= 1.5 ? 'pos' : val >= 1.2 ? 'warn' : 'neg';
  if (label === 'Ret/DD')  return val >= 5   ? 'pos' : val >= 3   ? 'warn' : 'neg';
  if (label === 'R Exp')   return val >= 0.30? 'pos' : val >= 0.15? 'warn' : 'neg';
  if (label === 'DD %')    return val <  2   ? 'pos' : val <  5   ? 'warn' : 'neg';
  if (label === 'Sharpe')  return val >= 1.3 ? 'pos' : val >= 1.0 ? 'warn' : 'neg';
  if (label === 'SQN')     return val >= 1.6 ? 'pos' : val >= 1.0 ? 'warn' : 'neg';
  if (label === 'Stagn d') return val <  180 ? 'pos' : val <  365 ? 'warn' : 'neg';
  return '';
}
function fmtNum(v, dec=2) {
  if (SQX_FORMATTERS.formatNumber) return SQX_FORMATTERS.formatNumber(v, dec);
  if (v == null || v === '') return '—';
  if (typeof v !== 'number') v = parseFloat(v);
  if (isNaN(v)) return '—';
  return v.toLocaleString('en-US', { minimumFractionDigits:dec, maximumFractionDigits:dec });
}
function fmtInt(v) {
  if (SQX_FORMATTERS.formatInteger) return SQX_FORMATTERS.formatInteger(v);
  if (v == null || v === '') return '—';
  return parseInt(v,10).toLocaleString('en-US');
}

function getFilteredStrategies() {
  return SQX_STRATEGIES.filterStrategies
    ? SQX_STRATEGIES.filterStrategies(getAllStrategies(), {
      mining: stratFilterMining,
      template: stratFilterTemplate,
      tier: stratFilterTier,
      status: stratFilterStatus
    })
    : getAllStrategies().filter(s => {
      if (stratFilterMining   !== 'all' && String(s.mining)   !== stratFilterMining)   return false;
      if (stratFilterTemplate !== 'all' && s.template !== stratFilterTemplate) return false;
      if (stratFilterTier     !== 'all' && s.tier     !== stratFilterTier)     return false;
      if (stratFilterStatus   !== 'all' && s.status   !== stratFilterStatus)   return false;
      return true;
    });
}

function renderStratSummary() {
  const all = getAllStrategies();
  const summary = SQX_STRATEGIES.summarize
    ? SQX_STRATEGIES.summarize(all)
    : {
      total: all.length,
      tier1: all.filter(s => s.tier === '1').length,
      tier15: all.filter(s => s.tier === '1.5').length,
      tier2: all.filter(s => s.tier === '2').length,
      tentative: all.filter(s => s.tier === 'tentativa').length,
      deployed: all.filter(s => s.status === 'DEPLOYED').length,
      totalProfit: all.reduce((acc,s) => acc + ((s.metrics && s.metrics.net_profit) || 0), 0)
    };

  document.getElementById('strat-summary').innerHTML =
    SQX_STRATEGIES.summaryHtml
      ? SQX_STRATEGIES.summaryHtml(summary, fmtInt)
      : '<div class="strat-summary-card"><div class="ss-count">' + summary.total + '</div><div class="ss-label">Total</div></div>' +
        '<div class="strat-summary-card t1"><div class="ss-count">' + summary.tier1 + '</div><div class="ss-label">TIER 1</div></div>' +
        '<div class="strat-summary-card t15"><div class="ss-count">' + summary.tier15 + '</div><div class="ss-label">TIER 1.5</div></div>' +
        '<div class="strat-summary-card t2"><div class="ss-count">' + summary.tier2 + '</div><div class="ss-label">TIER 2</div></div>' +
        '<div class="strat-summary-card tt"><div class="ss-count">' + summary.tentative + '</div><div class="ss-label">Tentativas</div></div>' +
        '<div class="strat-summary-card"><div class="ss-count">' + summary.deployed + '</div><div class="ss-label">Deployed</div></div>' +
        '<div class="strat-summary-card"><div class="ss-count" style="font-size:18px;">$' + fmtInt(Math.round(summary.totalProfit)) + '</div><div class="ss-label">Σ Net Profit (BT)</div></div>';
}

function populateStratFilters() {
  const all = getAllStrategies();

  const mSel = document.getElementById('strat-filter-mining');
  mSel.innerHTML = SQX_STRATEGIES.filterOptionsHtml
    ? SQX_STRATEGIES.filterOptionsHtml(all, 'mining', m => 'Mining ' + m)
    : '<option value="all">Todos</option>' + [...new Set(all.map(s => s.mining))].sort((a,b)=>a-b).map(m =>
      '<option value="'+m+'">Mining ' + m + '</option>'
    ).join('');

  const tSel = document.getElementById('strat-filter-template');
  tSel.innerHTML = SQX_STRATEGIES.filterOptionsHtml
    ? SQX_STRATEGIES.filterOptionsHtml(all, 'template')
    : '<option value="all">Todos</option>' + [...new Set(all.map(s => s.template))].sort().map(t =>
      '<option value="'+t+'">' + t + '</option>'
    ).join('');
}

function stratEsc(value) {
  if (SQX_FORMATTERS.escapeHtml) return SQX_FORMATTERS.escapeHtml(value);
  return String(value == null ? '' : value).replace(/[&<>"']/g, ch => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[ch]));
}

function strategyKey(s) {
  return SQX_STRATEGIES.strategyKey
    ? SQX_STRATEGIES.strategyKey(s)
    : [s.id, s.mining, s.template, s.asset, s.tf]
      .map(v => String(v == null ? '' : v))
      .join('|');
}

function renderStrategyCard(s) {
  if (SQX_STRATEGIES.strategyCard) {
    return SQX_STRATEGIES.strategyCard(s, {
      dirClass: dirClass,
      escapeHtml: stratEsc,
      formatInteger: fmtInt,
      formatNumber: fmtNum,
      metricClass: metricClass,
      strategyKey: strategyKey,
      tierClass: tierClass,
      tierLabel: tierLabel
    });
  }
  const m = s.metrics || {};
  const dirCls = dirClass(s.direction);
  const dirTxt = s.direction === 'L' ? 'LONG' : s.direction === 'S' ? 'SHORT' : 'L+S';
  const key = strategyKey(s);
  const sourceLabel = s._imported ? 'importada' : 'base';

  const metricsRow = [
    ['Net Profit', m.net_profit != null ? '$'+fmtNum(m.net_profit, 0) : '—', m.net_profit > 0 ? 'pos' : ''],
    ['PF',         fmtNum(m.pf),         metricClass('PF', m.pf)],
    ['Ret/DD',     fmtNum(m.ret_dd),     metricClass('Ret/DD', m.ret_dd)],
    ['DD %',       m.dd_pct != null ? fmtNum(m.dd_pct) + '%' : '—', metricClass('DD %', m.dd_pct)],
    ['Sharpe',     fmtNum(m.sharpe),     metricClass('Sharpe', m.sharpe)],
    ['R Exp',      fmtNum(m.r_exp),      metricClass('R Exp', m.r_exp)],
    ['# Trades',   fmtInt(m.trades),     ''],
    ['Win %',      m.win_pct != null ? fmtNum(m.win_pct) + '%' : '—', ''],
    [m.sqn != null ? 'SQN' : (m.stagnation_days != null ? 'Stagn d' : 'WFM $'),
      m.sqn != null ? fmtNum(m.sqn) : (m.stagnation_days != null ? fmtInt(m.stagnation_days) : (m.wfm_profit != null ? '$'+fmtInt(m.wfm_profit) : '—')),
      m.sqn != null ? metricClass('SQN', m.sqn) : (m.stagnation_days != null ? metricClass('Stagn d', m.stagnation_days) : '')],
  ];

  const metricsHtml = metricsRow.map(([lbl,val,cls]) =>
    '<div class="sc-metric"><div class="m-label">' + lbl + '</div><div class="m-val ' + cls + '">' + val + '</div></div>'
  ).join('');

  const testsOk = (s.tests_passed||[]).map(t => '<span class="sc-test-ok">'+t+'</span>').join('');
  const testsKo = (s.tests_failed||[]).map(t => '<span class="sc-test-ko">'+t+'</span>').join('');

  const importedCls = s._imported ? ' user-imported' : '';
  return '<div class="strat-card ' + tierClass(s.tier) + importedCls + '">' +
    '<div class="sc-head">' +
      '<span class="sc-id">' + s.id + '</span>' +
      '<span class="sc-name">' + s.name + '</span>' +
      '<span class="strat-tier-badge ' + tierClass(s.tier) + '">' + tierLabel(s.tier) + '</span>' +
      '<span class="strat-status-badge ' + s.status + '">' + s.status.replace('_',' ') + '</span>' +
    '</div>' +
    '<div class="sc-meta">' +
      '<span class="sc-meta-pill">M' + s.mining + '</span>' +
      '<span class="sc-meta-pill">' + s.asset + '</span>' +
      '<span class="sc-meta-pill">' + s.tf + '</span>' +
      '<span class="sc-meta-pill">' + s.blocksetting + '</span>' +
      '<span class="sc-meta-pill template">' + s.template + '</span>' +
      '<span class="sc-meta-pill ' + dirCls + '">' + dirTxt + '</span>' +
    '</div>' +
    '<div class="sc-indicators"><strong>Señal</strong>' + s.indicators + '</div>' +
    '<div class="sc-indicators"><strong>Exits</strong>' + s.exits + '</div>' +
    '<div class="sc-metrics">' + metricsHtml + '</div>' +
    (testsOk || testsKo ? '<div class="sc-tests">' + testsOk + testsKo + '</div>' : '') +
    (s.notes ? '<div class="sc-notes">' + s.notes + '</div>' : '') +
    '<div class="sc-footer"><span class="sc-date">' + (s.added || '—') + '</span>' +
      '<button class="strat-remove-btn" data-strategy-key="' + stratEsc(key) + '" title="Eliminar estrategia ' + sourceLabel + '">Eliminar</button>' +
    '</div>' +
  '</div>';
}

function renderStrategies() {
  populateStratFilters();
  renderStratSummary();
  // banner de importadas
  const userInfo = document.getElementById('strat-user-info');
  if (userInfo) {
    const cnt = STRATEGIES_USER.length;
    const hiddenCnt = STRATEGIES_DELETED.length;
    userInfo.style.display = (cnt > 0 || hiddenCnt > 0) ? 'block' : 'none';
    const cntEl = document.getElementById('strat-user-count');
    if (cntEl) cntEl.textContent = cnt;
    const hiddenWrap = document.getElementById('strat-hidden-wrap');
    const hiddenCntEl = document.getElementById('strat-hidden-count');
    if (hiddenWrap) hiddenWrap.style.display = hiddenCnt > 0 ? 'inline' : 'none';
    if (hiddenCntEl) hiddenCntEl.textContent = hiddenCnt;
  }
  const list = getFilteredStrategies();
  const grid = document.getElementById('strat-grid');
  if (!list.length) {
    grid.innerHTML = '<div class="no-data" style="grid-column:1/-1;">Sin estrategias que coincidan con los filtros.</div>';
    return;
  }
  const displayList = SQX_STRATEGIES.sortForDisplay ? SQX_STRATEGIES.sortForDisplay(list) : list;
  if (!SQX_STRATEGIES.sortForDisplay) {
    const tierRank = { '1':0, '1.5':1, '2':2, 'tentativa':3 };
    displayList.sort((a,b) => {
      const ta = tierRank[a.tier] ?? 99, tb = tierRank[b.tier] ?? 99;
      if (ta !== tb) return ta - tb;
      return (b.metrics.net_profit||0) - (a.metrics.net_profit||0);
    });
  }
  grid.innerHTML = displayList.map(renderStrategyCard).join('');
  grid.querySelectorAll('.strat-remove-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      removeStrategyClick(this.dataset.strategyKey);
    });
  });
}

function removeStrategyClick(key) {
  const imported = STRATEGIES_USER.find(s => strategyKey(s) === key);
  const base = STRATEGIES.find(s => strategyKey(s) === key);
  const target = imported || base;
  if (!target) return;

  const label = [target.id, 'M' + target.mining, target.template].filter(Boolean).join(' · ');
  const prompt = imported
    ? '¿Eliminar la estrategia importada ' + label + '?'
    : '¿Eliminar la estrategia base ' + label + ' de la vista? Podrás restaurarla después.';

  if (!confirm(prompt)) return;

  if (imported) {
    STRATEGIES_USER = STRATEGIES_USER.filter(s => strategyKey(s) !== key);
    saveStrategiesUser();
  } else if (!STRATEGIES_DELETED.includes(key)) {
    STRATEGIES_DELETED.push(key);
    saveStrategiesDeleted();
  }

  renderStrategies();
  renderPipelineState();
  renderHome();
}

function exportStrategiesCSV() {
  if (SQX_STRATEGIES.exportCsvRows) {
    doExport(SQX_STRATEGIES.exportCsvRows(getAllStrategies()), 'SQX_estrategias.csv');
    return;
  }
  const headers = ['ID','Name','Mining','Asset','TF','Blocksetting','Template','Direction','Tier','Status','NetProfit','PF','Sharpe','RetDD','DDpct','Trades','WinPct','RExp','SQN','StagnationDays','TestsPassed','TestsFailed','Indicators','Exits','Notes','Added','Source'];
  doExport([headers.map(h=>'"'+h+'"').join(';')], 'SQX_estrategias.csv');
}

// ── MODAL: añadir estrategia ──
function openStratModal() { document.getElementById('strat-modal-backdrop').style.display = 'flex'; }
function closeStratModal() { document.getElementById('strat-modal-backdrop').style.display = 'none'; document.getElementById('sf-output-wrap').style.display = 'none'; }
function clearStratForm() {
  ['sf-id','sf-name','sf-template','sf-indicators','sf-exits','sf-tests-ok','sf-tests-ko','sf-notes',
   'sf-np','sf-wfm','sf-pf','sf-sharpe','sf-retdd','sf-ddpct','sf-dd','sf-trades','sf-win','sf-rexp',
   'sf-rexpscore','sf-sqn','sf-cagr','sf-stagd','sf-stagpct','sf-zprob','sf-exposure'].forEach(id => {
    const el = document.getElementById(id); if (el) el.value = '';
  });
  document.getElementById('sf-mining').value = '1';
  document.getElementById('sf-asset').value = 'XAUUSD';
  document.getElementById('sf-tf').value = 'H1';
  document.getElementById('sf-bs').value = 'BS_Tendencia';
  document.getElementById('sf-dir').value = 'L';
  document.getElementById('sf-tier').value = 'tentativa';
  document.getElementById('sf-status').value = 'CANDIDATA';
  document.getElementById('sf-output-wrap').style.display = 'none';
}
function numOrNull(id) {
  const v = document.getElementById(id).value.trim();
  if (v === '') return null;
  const n = parseFloat(v); return isNaN(n) ? null : n;
}
function intOrNull(id) {
  const v = document.getElementById(id).value.trim();
  if (v === '') return null;
  const n = parseInt(v,10); return isNaN(n) ? null : n;
}
function strOrEmpty(id) { return (document.getElementById(id).value || '').trim(); }
function listFromCSV(id) {
  const v = strOrEmpty(id); if (!v) return [];
  return v.split(',').map(x => x.trim()).filter(Boolean);
}
function readStratFormValues() {
  return {
    id: strOrEmpty('sf-id'),
    name: strOrEmpty('sf-name'),
    mining: document.getElementById('sf-mining').value,
    asset: strOrEmpty('sf-asset'),
    tf: document.getElementById('sf-tf').value,
    blocksetting: document.getElementById('sf-bs').value,
    template: strOrEmpty('sf-template'),
    direction: document.getElementById('sf-dir').value,
    indicators: strOrEmpty('sf-indicators'),
    exits: strOrEmpty('sf-exits'),
    netProfit: strOrEmpty('sf-np'),
    wfmProfit: strOrEmpty('sf-wfm'),
    pf: strOrEmpty('sf-pf'),
    sharpe: strOrEmpty('sf-sharpe'),
    retDd: strOrEmpty('sf-retdd'),
    ddPct: strOrEmpty('sf-ddpct'),
    dd: strOrEmpty('sf-dd'),
    trades: strOrEmpty('sf-trades'),
    winPct: strOrEmpty('sf-win'),
    rExp: strOrEmpty('sf-rexp'),
    rExpScore: strOrEmpty('sf-rexpscore'),
    sqn: strOrEmpty('sf-sqn'),
    cagr: strOrEmpty('sf-cagr'),
    stagnationDays: strOrEmpty('sf-stagd'),
    stagnationPct: strOrEmpty('sf-stagpct'),
    zProbability: strOrEmpty('sf-zprob'),
    exposure: strOrEmpty('sf-exposure'),
    tier: document.getElementById('sf-tier').value,
    status: document.getElementById('sf-status').value,
    testsPassed: strOrEmpty('sf-tests-ok'),
    testsFailed: strOrEmpty('sf-tests-ko'),
    notes: strOrEmpty('sf-notes')
  };
}
function generateStratJSON() {
  const obj = SQX_STRATEGIES.manualStrategyFromValues
    ? SQX_STRATEGIES.manualStrategyFromValues(readStratFormValues(), new Date().toISOString().slice(0,10))
    : {
    id:           strOrEmpty('sf-id') || '0.000000',
    name:         strOrEmpty('sf-name') || 'Sin nombre',
    mining:       parseInt(document.getElementById('sf-mining').value,10) || 1,
    asset:        strOrEmpty('sf-asset') || 'XAUUSD',
    tf:           document.getElementById('sf-tf').value,
    blocksetting: document.getElementById('sf-bs').value,
    template:     strOrEmpty('sf-template') || 'UNKNOWN',
    direction:    document.getElementById('sf-dir').value,
    indicators:   strOrEmpty('sf-indicators'),
    exits:        strOrEmpty('sf-exits'),
    metrics: {}
  };
  const M = obj.metrics;
  if (!SQX_STRATEGIES.manualStrategyFromValues) {
    const np = numOrNull('sf-np');         if (np   !== null) M.net_profit = np;
    const wf = numOrNull('sf-wfm');        if (wf   !== null) M.wfm_profit = wf;
    const pf = numOrNull('sf-pf');         if (pf   !== null) M.pf = pf;
    const sh = numOrNull('sf-sharpe');     if (sh   !== null) M.sharpe = sh;
    const rd = numOrNull('sf-retdd');      if (rd   !== null) M.ret_dd = rd;
    const dp = numOrNull('sf-ddpct');      if (dp   !== null) M.dd_pct = dp;
    const dd = numOrNull('sf-dd');         if (dd   !== null) M.dd = dd;
    const tr = intOrNull('sf-trades');     if (tr   !== null) M.trades = tr;
    const wn = numOrNull('sf-win');        if (wn   !== null) M.win_pct = wn;
    const re = numOrNull('sf-rexp');       if (re   !== null) M.r_exp = re;
    const rs = numOrNull('sf-rexpscore');  if (rs   !== null) M.r_exp_score = rs;
    const sq = numOrNull('sf-sqn');        if (sq   !== null) M.sqn = sq;
    const cg = numOrNull('sf-cagr');       if (cg   !== null) M.cagr = cg;
    const sd = intOrNull('sf-stagd');      if (sd   !== null) M.stagnation_days = sd;
    const sp = numOrNull('sf-stagpct');    if (sp   !== null) M.stagnation_pct = sp;
    const zp = numOrNull('sf-zprob');      if (zp   !== null) M.z_probability = zp;
    const ex = numOrNull('sf-exposure');   if (ex   !== null) M.exposure = ex;
    obj.tier         = document.getElementById('sf-tier').value;
    obj.status       = document.getElementById('sf-status').value;
    obj.tests_passed = listFromCSV('sf-tests-ok');
    obj.tests_failed = listFromCSV('sf-tests-ko');
    obj.notes        = strOrEmpty('sf-notes');
    obj.added        = new Date().toISOString().slice(0,10);
  }

  const json = JSON.stringify(obj, null, 2);
  document.getElementById('sf-output').textContent = json;
  document.getElementById('sf-output-wrap').style.display = 'block';
}

// ============================================================
// EVENTS
// ============================================================
var HOME_BACKEND_STATE = { state: 'loading', title: 'Comprobando', desc: 'API local pendiente de comprobar.', meta: {} };
var HOME_TRACE_KEY = (window.SQX_CONFIG && window.SQX_CONFIG.storageKeys && window.SQX_CONFIG.storageKeys.homeTrace) || 'sqx_home_trace_v1';
var HOME_TRACE = [];
HOME_TRACE = SQX_STORAGE.getJson(HOME_TRACE_KEY, []);

function saveHomeTrace() {
  SQX_STORAGE.setJson(HOME_TRACE_KEY, HOME_TRACE);
}

function homeEsc(value) {
  if (SQX_HOME.escapeHtml) return SQX_HOME.escapeHtml(value);
  if (SQX_FORMATTERS.escapeHtml) return SQX_FORMATTERS.escapeHtml(value);
  return String(value == null ? '' : value).replace(/[<>&"']/g, function(ch) {
    return ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&#39;' })[ch];
  });
}

function renderHomeTrace() {
  var list = document.getElementById('home-history-list');
  var empty = document.getElementById('home-history-empty');
  if (!list || !empty) return;
  if (!HOME_TRACE.length) {
    list.innerHTML = '';
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';
  list.innerHTML = SQX_HOME.traceHtml ? SQX_HOME.traceHtml(HOME_TRACE, homeEsc) : HOME_TRACE.map(function(item) {
    return (
      '<div class="home-history-item ' + homeEsc(item.level || 'info') + '">' +
        '<span class="home-history-dot"></span>' +
        '<div>' +
          '<div class="home-history-title">' + homeEsc(item.title || 'Evento') + '</div>' +
          '<div class="home-history-meta">' + homeEsc(item.timeLabel || '') + ' · ' + homeEsc(item.detail || '') + '</div>' +
        '</div>' +
      '</div>'
    );
  }).join('');
}

window.addHomeTrace = function(title, detail, level) {
  var item = SQX_HOME.createTraceItem ? SQX_HOME.createTraceItem(title, detail, level) : {
    title: title || 'Evento',
    detail: detail || '',
    level: level || 'info',
    timeLabel: new Date().toLocaleString(),
    ts: Date.now()
  };
  HOME_TRACE = SQX_HOME.addTrace ? SQX_HOME.addTrace(HOME_TRACE, item, 12) : [item].concat(HOME_TRACE).slice(0, 12);
  saveHomeTrace();
  renderHomeTrace();
};

function renderHome() {
  function setText(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }
  function setStateClass(id, state) {
    var el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('is-ok', 'is-warn');
    el.classList.add(state === 'ok' ? 'is-ok' : 'is-warn');
  }
  function setCheck(id, ok) {
    var el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('is-ok', 'is-warn');
    el.classList.add(ok ? 'is-ok' : 'is-warn');
  }
  function setAudit(id, ok, detail) {
    var row = document.getElementById(id);
    var detailEl = document.getElementById(id + '-detail');
    if (row) {
      row.classList.remove('is-ok', 'is-warn');
      row.classList.add(ok ? 'is-ok' : 'is-warn');
    }
    if (detailEl) detailEl.textContent = detail;
  }
  var activePlanMinings = typeof getPlanMinings === 'function' ? getPlanMinings() : (PLAN_MININGS || []);
  var activePlanPhases = typeof getPlanPhases === 'function' ? getPlanPhases() : (PHASE_META || {});
  var visibleStrategies = typeof getAllStrategies === 'function' ? getAllStrategies() : (STRATEGIES || []);
  var model = SQX_HOME.computeHomeModel
    ? SQX_HOME.computeHomeModel({
      assets: ASSETS,
      backendState: HOME_BACKEND_STATE,
      catKeys: CAT_KEYS,
      manifestVersion: (SQX_MANIFEST && SQX_MANIFEST.version) || 1,
      phaseMeta: activePlanPhases,
      pipelineState: PIPELINE_STATE,
      planMinings: activePlanMinings,
      priorityProgress: PRIORITY_PROGRESS,
      strategies: visibleStrategies,
      strategiesUser: []
    })
    : null;
  if (!model) {
    var assetCounts = (ASSETS || []).reduce(function(acc, asset) {
      acc[asset.type] = (acc[asset.type] || 0) + 1;
      return acc;
    }, {});
    var strategyUserCount = Array.isArray(STRATEGIES_USER) ? STRATEGIES_USER.length : 0;
    var marked = Object.keys(PRIORITY_PROGRESS || {}).length;
    var nextAction = (PIPELINE_STATE && PIPELINE_STATE.nextAction) || 'Plan operativo';
    var phaseCount = Object.keys(activePlanPhases || {}).length;
    var manifestOk = !!((ASSETS || []).length && activePlanMinings.length && visibleStrategies.length);
    var planOk = activePlanMinings.length > 0;
    var strategiesOk = visibleStrategies.length > 0;
    var backendOk = HOME_BACKEND_STATE.state === 'up';
    var backendMeta = HOME_BACKEND_STATE.meta || {};
    var templatesOk = backendOk && !!(backendMeta.templates_capa1_exists && backendMeta.templates_capa2_exists);
    var sqxPathOk = backendOk && !!backendMeta.sqx_path_set;
    var outputOk = backendOk && !!(backendMeta.output_dir && backendMeta.output_dir_exists);
    var auditItems = [manifestOk, planOk, backendOk, templatesOk, sqxPathOk, outputOk];
    var readiness = Math.round(([manifestOk, planOk, strategiesOk, backendOk].filter(Boolean).length / 4) * 100);
    nextAction = SQX_HOME.trimAction ? SQX_HOME.trimAction(nextAction) : (nextAction.length > 82 ? nextAction.slice(0, 79).trim() + '...' : nextAction);
    model = {
      assetCount: (ASSETS || []).length,
      assetsSub: (assetCounts.forex || 0) + ' Forex · ' + (assetCounts.index || 0) + ' Indices · ' + (assetCounts.oro || 0) + ' Oro',
      planCount: activePlanMinings.length,
      planSub: phaseCount + ' fases · minings configurados',
      strategyCount: visibleStrategies.length,
      strategiesSub: visibleStrategies.length + ' visibles · ' + strategyUserCount + ' importadas',
      priorityCount: marked,
      nextAction: nextAction,
      backendTitle: HOME_BACKEND_STATE.title,
      dataStatus: manifestOk ? 'Manifest v' + ((SQX_MANIFEST && SQX_MANIFEST.version) || 1) : 'Manifest incompleto',
      readiness: readiness,
      heroStatus: backendOk ? (sqxPathOk ? 'API conectada. Plan, manifiestos y generador listos para operar.' : 'API conectada. Falta completar la ruta SQX para generar con seguridad.') : 'Manifest activo. Arranca la API local para habilitar generacion, validacion de rutas y limpieza SQX.',
      auditScore: auditItems.filter(Boolean).length + '/' + auditItems.length,
      checks: { manifest: manifestOk, plan: planOk, strategies: strategiesOk, backend: backendOk },
      states: { backend: backendOk ? 'ok' : 'warn', data: manifestOk ? 'ok' : 'warn' },
      audit: {
        manifest: { ok: manifestOk, detail: (ASSETS || []).length + ' activos · ' + (CAT_KEYS || []).length + ' categorias' },
        plan: { ok: planOk, detail: phaseCount + ' fases · ' + activePlanMinings.length + ' minings' },
        backend: { ok: backendOk, detail: backendOk ? 'API v' + (backendMeta.version || '?') : 'API no conectada' },
        templates: { ok: templatesOk, detail: backendOk ? (templatesOk ? 'Capa 1 + Capa 2 OK' : 'revisar templates') : 'requiere API' },
        sqx: { ok: sqxPathOk, detail: backendOk ? (sqxPathOk ? 'ruta configurada' : 'ruta pendiente') : 'requiere API' },
        output: { ok: outputOk, detail: backendOk ? (outputOk ? 'carpeta accesible' : 'output pendiente') : 'requiere API' }
      }
    };
  }

  if (SQX_HOME.applyHomeModel) {
    SQX_HOME.applyHomeModel(model, document);
  } else {
    setText('home-assets-count', model.assetCount);
    setText('home-assets-sub', model.assetsSub);
    setText('home-minings-count', model.planCount);
    setText('home-plan-sub', model.planSub);
    setText('home-strategies-count', model.strategyCount);
    setText('home-strategies-sub', model.strategiesSub);
    setText('home-priority-count', model.priorityCount);
    setText('home-next-action', model.nextAction);
    setText('home-backend-status', model.backendTitle);
    setText('home-data-status', model.dataStatus);
    setText('home-readiness-score', model.readiness + '%');
    setText('home-hero-status', model.heroStatus);
    setText('home-audit-score', model.auditScore);
    var bar = document.getElementById('home-readiness-bar');
    if (bar) bar.style.width = model.readiness + '%';
    setCheck('home-check-manifest', model.checks.manifest);
    setCheck('home-check-plan', model.checks.plan);
    setCheck('home-check-strategies', model.checks.strategies);
    setCheck('home-check-backend', model.checks.backend);
    setStateClass('home-backend-status', model.states.backend);
    setStateClass('home-data-status', model.states.data);
    setAudit('home-audit-manifest', model.audit.manifest.ok, model.audit.manifest.detail);
    setAudit('home-audit-plan', model.audit.plan.ok, model.audit.plan.detail);
    setAudit('home-audit-backend', model.audit.backend.ok, model.audit.backend.detail);
    setAudit('home-audit-templates', model.audit.templates.ok, model.audit.templates.detail);
    setAudit('home-audit-sqx', model.audit.sqx.ok, model.audit.sqx.detail);
    setAudit('home-audit-output', model.audit.output.ok, model.audit.output.detail);
  }
  renderHomeTrace();
}

window.updateHomeBackendStatus = function(state, title, desc, meta) {
  HOME_BACKEND_STATE = {
    state: state || 'loading',
    title: title || 'API local',
    desc: desc || '',
    meta: meta || {}
  };
  renderHome();
};

function activateTabById(id) {
  if (SQX_UI_MODULE.activateTabById) return SQX_UI_MODULE.activateTabById(id, document);
  var tab = document.querySelector('.tab[data-tab="' + id + '"]');
  var panel = document.getElementById('tab-' + id);
  if (!tab || !panel) return;
  document.querySelectorAll('.tab').forEach(function(x) { x.classList.remove('active'); });
  tab.classList.add('active');
  document.querySelectorAll('.tab-content').forEach(function(c) { c.style.display = 'none'; });
  panel.style.display = 'block';
}

if (SQX_UI_MODULE.bindTabs) SQX_UI_MODULE.bindTabs('.tab', activateTabById, document);
else document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{
  activateTabById(t.dataset.tab);
}));

if (SQX_UI_MODULE.bindHomeTabButtons) SQX_UI_MODULE.bindHomeTabButtons('[data-home-tab]', activateTabById, document);
else document.querySelectorAll('[data-home-tab]').forEach(function(btn) {
  btn.addEventListener('click', function() {
    activateTabById(btn.dataset.homeTab);
  });
});

var homeHistoryClear = document.getElementById('home-history-clear');
if (homeHistoryClear) {
  homeHistoryClear.addEventListener('click', function() {
    HOME_TRACE = [];
    saveHomeTrace();
    renderHomeTrace();
  });
}

function bindBtns(sel, dataKey, varSetter, cb) {
  if (SQX_UI_MODULE.bindButtonGroup) return SQX_UI_MODULE.bindButtonGroup(sel, dataKey, varSetter, cb, document);
  document.querySelectorAll(sel).forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll(sel).forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    varSetter(b.dataset[dataKey]);
    cb();
  }));
}
function bindChange(id, cb) {
  if (SQX_UI_MODULE.bindChange) return SQX_UI_MODULE.bindChange(id, cb);
  const el = document.getElementById(id);
  if (el) el.addEventListener('change', cb);
}
function bindClick(id, cb) {
  if (SQX_UI_MODULE.bindClick) return SQX_UI_MODULE.bindClick(id, cb);
  const el = document.getElementById(id);
  if (el) el.addEventListener('click', cb);
}
bindBtns('[data-filter-type]', 'filterType', function(v){ filterType = v; }, renderAssetGrid);
bindBtns('[data-filter-sqx]',  'filterSqx',  function(v){ filterSqx  = v; }, renderAssetGrid);
bindBtns('[data-filter-dir]',  'filterDir',  function(v){ filterDir  = v; }, renderCategoriesView);
bindBtns('[data-priority-min]','priorityMin',function(v){ filterPriorityMin = parseInt(v,10) || 0; }, renderPriority);
bindBtns('[data-priority-type]','priorityType',function(v){ filterPriorityType = v; }, renderPriority);

if (SQX_UI_MODULE.bindInput) SQX_UI_MODULE.bindInput('search-asset', renderAssetGrid);
else document.getElementById('search-asset').addEventListener('input',renderAssetGrid);
bindChange('asset-sort', function(e){ assetSort=e.target.value; renderAssetGrid(); });
bindChange('cat-filter-rating', function(e){ filterCatRating=e.target.value; renderCategoriesView(); });
bindChange('cat-filter-sub', function(e){ filterCatSub=e.target.value; renderCategoriesView(); });
bindChange('cat-filter-tf', function(e){ filterCatTf=e.target.value; renderCategoriesView(); });
bindClick('export-cat-btn', exportCatCSV);
bindChange('priority-cat-filter', function(e){ filterPriorityCat=e.target.value; renderPriority(); });

// Global helper for inline onclick navigation to asset tab
window.navToAsset = function(id) {
  activateTabById('activos');
  selectAsset(id);
};

// Quick actions from asset/category cards into Mining Control and Project Generator.
window.quickAddToPlan = function(asset, cat, tf, dir) {
  const catBase = String(cat || '').replace(/_S$/, '');
  const ok = addPlanMiningFromCandidate(asset, catBase, tf, dir, 'asset-card');
  if (!ok) return;
  activateTabById('pipeline');
  renderPipelineState();
  setTimeout(() => {
    document.getElementById('ps-plan-card')?.scrollIntoView({ behavior:'smooth', block:'start' });
  }, 50);
};

window.quickToProjectGen = function(asset, cat, tf, dir) {
  const catBase = String(cat || '').replace(/_S$/, '');
  const bs = PRIORITY_CAT_TO_BS[cat] || PRIORITY_CAT_TO_BS[catBase] || CAT_TO_BS[cat] || CAT_TO_BS[catBase] || 'BS_Custom';
  const tfList = String(tf || '').split(',').map(t => t.trim()).filter(Boolean);
  const firstTf = tfList[0] || 'H1';
  const cleanCat = catBase.replace(/[^a-z0-9]+/gi, '');
  const config = {
    name: 'Project_' + asset + '_' + firstTf + '_' + cleanCat,
    asset: asset,
    tf: firstTf,
    bs: bs,
    dir: dir === 'L' ? 'long' : (dir === 'S' ? 'short' : 'both'),
    capa: 1,
    template: cleanCat.toUpperCase()
  };

  if (window.SQX && window.SQX.projectGenerator && window.SQX.projectGenerator.dom) {
    window.SQX.projectGenerator.dom.writeCustomProjectInputs(document, config);
  }

  activateTabById('projectgen');
  setTimeout(() => {
    const target = document.querySelector('.pg-custom-card');
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
};

// ── SQX PRIORITY: tracking persistente en localStorage ──
const PRIORITY_STATE_KEY = SQX_STORAGE_KEYS.priorityProgress || 'sqx_priority_progress_v1';
let PRIORITY_PROGRESS = {};
PRIORITY_PROGRESS = SQX_STORAGE.getJson(PRIORITY_STATE_KEY, {});
function savePriorityProgress() { SQX_STORAGE.setJson(PRIORITY_STATE_KEY, PRIORITY_PROGRESS); }

function statusBadgeHtml(id, status) {
  const label = sqxStatusMeta(status).label;
  return '<span class="status ' + status + ' clickable-status" onclick="cycleMiningStatus(\''+id+'\')">' + label + '</span>';
}

window.cycleMiningStatus = function(id) {
  const cur = (PRIORITY_PROGRESS[id] && PRIORITY_PROGRESS[id].status) || 'pending';
  const seq = sqxStatusSequence();
  const next = seq[(seq.indexOf(cur)+1) % seq.length];
  PRIORITY_PROGRESS[id] = { status: next, updated: new Date().toISOString() };
  savePriorityProgress();
  renderPriority();
  // Sync con Mining Control (re-renderiza si la fila importada cambió de estado allí)
  if (typeof renderPipelineState === 'function') renderPipelineState();
};

document.getElementById('priority-reset-btn').addEventListener('click', function() {
  if (confirm('Resetear todo el progreso del SQX Priority?')) {
    PRIORITY_PROGRESS = {};
    savePriorityProgress();
    renderPriority();
    if (typeof renderPipelineState === 'function') renderPipelineState();
  }
});
document.getElementById('priority-export-btn').addEventListener('click', function() {
  const blob = new Blob([JSON.stringify(PRIORITY_PROGRESS, null, 2)], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'sqx_priority_progress_' + new Date().toISOString().slice(0,10) + '.json';
  a.click(); URL.revokeObjectURL(url);
});
const _impFile = document.getElementById('priority-import-file');
document.getElementById('priority-import-btn').addEventListener('click', function() { _impFile.click(); });
_impFile.addEventListener('change', function(e){
  const f = e.target.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = function(ev) {
    try {
      const data = JSON.parse(ev.target.result);
      if (typeof data === 'object' && data !== null) {
        PRIORITY_PROGRESS = data;
        savePriorityProgress();
        renderPriority();
        if (typeof renderPipelineState === 'function') renderPipelineState();
        alert('Importado: ' + Object.keys(data).length + ' entradas');
      }
    } catch(err){ alert('JSON invalido: '+err.message); }
  };
  r.readAsText(f);
});
// ── ESTRATEGIAS: filtros + modal ──
bindBtns('[data-strat-tier]', 'stratTier', function(v){ stratFilterTier = v; }, renderStrategies);
document.getElementById('strat-filter-mining').addEventListener('change',  function(e){ stratFilterMining   = e.target.value; renderStrategies(); });
document.getElementById('strat-filter-template').addEventListener('change',function(e){ stratFilterTemplate = e.target.value; renderStrategies(); });
document.getElementById('strat-filter-status').addEventListener('change',  function(e){ stratFilterStatus   = e.target.value; renderStrategies(); });
document.getElementById('strat-export-btn').addEventListener('click', exportStrategiesCSV);

document.getElementById('strat-add-btn').addEventListener('click', openStratModal);
document.getElementById('strat-modal-close').addEventListener('click', closeStratModal);
document.getElementById('strat-modal-backdrop').addEventListener('click', function(e){
  if (e.target === this) closeStratModal();
});
document.getElementById('sf-generate').addEventListener('click', generateStratJSON);
document.getElementById('sf-clear').addEventListener('click', clearStratForm);
document.getElementById('sf-copy').addEventListener('click', function(){
  const txt = document.getElementById('sf-output').textContent;
  navigator.clipboard.writeText(txt).then(function(){
    const btn = document.getElementById('sf-copy');
    const old = btn.textContent;
    btn.textContent = 'Copiado';
    setTimeout(function(){ btn.textContent = old; }, 1500);
  }, function(){ alert('No se pudo copiar al portapapeles. Selecciona el texto manualmente.'); });
});
document.addEventListener('keydown', function(e){
  if (e.key === 'Escape') {
    if (document.getElementById('strat-modal-backdrop').style.display !== 'none') closeStratModal();
    if (document.getElementById('strat-import-backdrop').style.display !== 'none') closeImportModal();
    const psm = document.getElementById('ps-add-mining-backdrop');
    const psp = document.getElementById('ps-add-phase-backdrop');
    if (psm && psm.style.display !== 'none') closeAddMiningModal();
    if (psp && psp.style.display !== 'none') closeAddPhaseModal();
  }
});

// ============================================================
// MINING CONTROL - plan configurado + embudo + KPIs
// ============================================================

// ── Plan USER (añadidos por UI, persistente en localStorage) ──
const PLAN_USER_KEY = SQX_STORAGE_KEYS.planUser || 'sqx_plan_user_v1';
let PLAN_USER = { minings:[], phases:{}, baseDisabled:false, hiddenBaseMinings:[] };
try {
  const stored = SQX_STORAGE.getJson(PLAN_USER_KEY, {});
  PLAN_USER = {
    minings: Array.isArray(stored.minings) ? stored.minings : [],
    phases: stored.phases || {},
    baseDisabled: !!stored.baseDisabled,
    hiddenBaseMinings: Array.isArray(stored.hiddenBaseMinings) ? stored.hiddenBaseMinings : [],
  };
} catch(e){ /* keep defaults */ }
function normalizePlanUserState() {
  PLAN_USER.minings = (Array.isArray(PLAN_USER.minings) ? PLAN_USER.minings : []).map(function(m) {
    return Object.assign({}, m, {
      num: parseInt(m.num, 10),
      phase: parseInt(m.phase, 10),
      source: m.source || 'manual',
    });
  }).filter(function(m) {
    return m.num && m.phase && m.asset && m.tf && m.bs && m.dir;
  });
  PLAN_USER.phases = PLAN_USER.phases || {};
  PLAN_USER.baseDisabled = !!PLAN_USER.baseDisabled;
  PLAN_USER.hiddenBaseMinings = (Array.isArray(PLAN_USER.hiddenBaseMinings) ? PLAN_USER.hiddenBaseMinings : [])
    .map(function(n) { return parseInt(n, 10); })
    .filter(function(n, idx, arr) { return n && arr.indexOf(n) === idx; });
}
normalizePlanUserState();
function savePlanUser() { SQX_STORAGE.setJson(PLAN_USER_KEY, PLAN_USER); }
function planEsc(value) { return stratEsc(value); }

function getPlanMinings() {
  normalizePlanUserState();
  const hidden = new Set(PLAN_USER.hiddenBaseMinings || []);
  const all = [
    ...(PLAN_USER.baseDisabled ? [] : PLAN_MININGS.filter(function(m) { return !hidden.has(m.num); })),
    ...PLAN_USER.minings.map(m => ({...m, _user:true}))
  ];
  return all.sort((a,b) => a.num - b.num);
}
function getPlanPhases() {
  normalizePlanUserState();
  return Object.assign({}, PLAN_USER.baseDisabled ? {} : PHASE_META, PLAN_USER.phases);
}
function getPlanPhaseNums() {
  const phases = getPlanPhases();
  return Object.keys(phases).map(n => parseInt(n,10)).filter(n => !isNaN(n)).sort((a,b)=>a-b);
}
function nextMiningNum() {
  const all = getPlanMinings();
  return all.length ? Math.max(...all.map(m => m.num)) + 1 : 1;
}
function nextPhaseNum() {
  const nums = getPlanPhaseNums();
  return nums.length ? Math.max(...nums) + 1 : 1;
}
function addMiningUser(m) {
  const currentMinings = getPlanMinings();
  const mining = {
    num: parseInt(m.num, 10) || nextMiningNum(),
    phase: parseInt(m.phase, 10) || 1,
    asset: String(m.asset || '').trim().toUpperCase(),
    tf: String(m.tf || '').trim().toUpperCase(),
    bs: String(m.bs || '').trim(),
    dir: String(m.dir || '').trim(),
    source: m.source || 'manual',
  };
  if (!mining.asset || !mining.tf || !mining.bs || !mining.dir || !mining.phase) return false;
  if (currentMinings.some(x => x.num === mining.num)) return false;
  if (currentMinings.some(x => x.asset === mining.asset && x.tf === mining.tf && x.bs === mining.bs && x.dir === mining.dir)) return false;
  if (!getPlanPhases()[mining.phase]) {
    PLAN_USER.phases[mining.phase] = { name: 'Fase ' + mining.phase, desc: 'Fase creada desde Plan mining' };
  }
  PLAN_USER.minings.push(mining);
  savePlanUser();
  return true;
}
function resolvePlanPhaseForMining(asset) {
  const all = getPlanMinings();
  const sameAssetMining = all.find(function(m) { return m.asset === asset; });
  if (sameAssetMining) return sameAssetMining.phase;
  const nums = getPlanPhaseNums();
  if (nums.length) return nums[0];
  PLAN_USER.phases[1] = { name: 'Manual', desc: 'Minings añadidos por el usuario' };
  return 1;
}
function addPlanMiningFromCandidate(asset, cat, tf, dir, source) {
  const catBase = String(cat || '').replace(/_S$/, '');
  const bs = PRIORITY_CAT_TO_BS[cat] || PRIORITY_CAT_TO_BS[catBase] || CAT_TO_BS[cat] || CAT_TO_BS[catBase];
  if (!bs) { alert('Categoría desconocida: '+catBase); return false; }
  const tfList = String(tf || '').split(',').map(function(t) { return t.trim().toUpperCase(); }).filter(Boolean);
  const firstTf = tfList[0] || 'H1';
  const cleanAsset = String(asset || '').trim().toUpperCase();
  const cleanDir = String(dir || 'L').trim();
  const exists = getPlanMinings().some(function(m) {
    return m.asset === cleanAsset && m.tf === firstTf && m.bs === bs && m.dir === cleanDir;
  });
  if (exists) {
    alert('Ese mining ya existe en el Plan mining.');
    return false;
  }
  const phase = resolvePlanPhaseForMining(cleanAsset);
  const ok = addMiningUser({
    num: nextMiningNum(),
    phase: phase,
    asset: cleanAsset,
    tf: firstTf,
    bs: bs,
    dir: cleanDir,
    source: source || 'manual',
  });
  if (!ok) alert('No se ha podido añadir el mining al Plan mining.');
  return ok;
}
function addPhaseUser(num, name, desc) {
  if (!num || !name) return false;
  if (getPlanPhases()[num]) return false; // ya existe
  PLAN_USER.phases[num] = { name: name, desc: desc || '' };
  savePlanUser();
  return true;
}
function setPhaseMetaUser(num, name, desc) {
  if (!num || !name) return false;
  PLAN_USER.phases[num] = { name: name, desc: desc || '' };
  savePlanUser();
  return true;
}
function revertPhaseMetaUser(num) {
  if (!PLAN_USER.phases[num]) return false;
  delete PLAN_USER.phases[num];
  savePlanUser();
  return true;
}
function removeUserMining(num) {
  PLAN_USER.minings = PLAN_USER.minings.filter(m => m.num !== num);
  savePlanUser();
}
function removeUserPhase(num) {
  // No eliminar fase si tiene minings asignados
  const used = getPlanMinings().some(m => m.phase === num);
  if (used) { alert('La fase '+num+' tiene minings asignados. Elimínalos primero.'); return false; }
  delete PLAN_USER.phases[num];
  savePlanUser();
  return true;
}
function clearPlanUser() {
  PLAN_USER = { minings:[], phases:{}, baseDisabled:false, hiddenBaseMinings:[] };
  savePlanUser();
}
function resetPlanMiningUserState() {
  PLAN_USER = {
    minings:[],
    phases:{},
    baseDisabled:true,
    hiddenBaseMinings: PLAN_MININGS.map(function(m) { return m.num; }),
    resetAt: new Date().toISOString()
  };
  savePlanUser();
  PIPELINE_STATE.overrides = {};
  PIPELINE_STATE.funnels = {};
  PIPELINE_STATE.nextAction = '';
  savePipelineState();
}
function resetPlanPhaseMinings(phase) {
  const p = parseInt(phase, 10);
  if (!p) return false;
  const baseNums = PLAN_MININGS.filter(function(m) { return m.phase === p; }).map(function(m) { return m.num; });
  const userNums = PLAN_USER.minings.filter(function(m) { return m.phase === p; }).map(function(m) { return m.num; });
  const removedNums = baseNums.concat(userNums);
  const hidden = new Set(PLAN_USER.hiddenBaseMinings || []);
  baseNums.forEach(function(num) { hidden.add(num); });
  PLAN_USER.hiddenBaseMinings = Array.from(hidden);
  PLAN_USER.minings = PLAN_USER.minings.filter(function(m) { return m.phase !== p; });
  Object.keys(PIPELINE_STATE.overrides || {}).forEach(function(num) {
    if (removedNums.indexOf(parseInt(num, 10)) !== -1) delete PIPELINE_STATE.overrides[num];
  });
  savePlanUser();
  savePipelineState();
  return true;
}
// Alias visible para el helper de status (lee PLAN_ALL si existe)
window.PLAN_ALL = null;
function refreshPlanAll() { window.PLAN_ALL = getPlanMinings(); }
refreshPlanAll();
window.setPhaseMetaUser = setPhaseMetaUser;
window.addMiningUser = addMiningUser;
window.addPlanMiningFromCandidate = addPlanMiningFromCandidate;
window.resetPlanMiningUserState = resetPlanMiningUserState;
window.clearPlanUser = clearPlanUser;

// Mapping inverso BS → categoría de prioridad operativa

// Convierte un mining → key de prioridad operativa (formato 'asset|cat|tf|dir')
function miningToPriorityKey(mining) {
  const cat = BS_TO_PRIORITY_CAT[mining.bs];
  if (!cat) return null;
  return mining.asset + '|' + cat + '|' + mining.tf + '|' + mining.dir;
}

// localStorage state — pipeline tracking
// Estructura: { overrides: { num: 'current'|... }, funnels: {...}, nextAction:'' }
// `overrides` solo guarda los manuales; el estado por defecto se deriva de prioridad operativa
const PIPELINE_STATE_KEY = SQX_STORAGE_KEYS.pipelineState || 'sqx_pipeline_state_v1';
let PIPELINE_STATE = { overrides:{}, funnels:{}, nextAction:'' };
try {
  const stored = SQX_STORAGE.getJson(PIPELINE_STATE_KEY, {});
  // Migración del formato antiguo (miningStatus → overrides) + limpieza del preset fantasma
  let overrides = stored.overrides || stored.miningStatus || {};
  // Si solo hay UN override y es el preset Mining 1 = 'current' (preset antiguo), limpiarlo
  // — así el auto-sync con la prioridad operativa funciona desde el primer momento
  if (!stored.overrides && stored.miningStatus &&
      Object.keys(stored.miningStatus).length === 1 &&
      stored.miningStatus[1] === 'current') {
    overrides = {};
  }
  PIPELINE_STATE = { overrides:overrides, funnels:stored.funnels || {}, nextAction:stored.nextAction || '' };
  // Persistir migración limpia para que no se vuelva a aplicar
  SQX_STORAGE.setJson(PIPELINE_STATE_KEY, PIPELINE_STATE);
} catch(e){ /* keep defaults */ }
// pre-load funnel Mining 1 LINEAR si no hay
if (!PIPELINE_STATE.funnels['1|LINEAR']) PIPELINE_STATE.funnels['1|LINEAR'] = {...FUNNEL_PRELOAD['1|LINEAR']};
if (!PIPELINE_STATE.nextAction) PIPELINE_STATE.nextAction = sqxConfigValue('pipeline.defaultNextAction', 'Filter-by-correlation entre las estrategias PASSED del WFM.');

function savePipelineState() { SQX_STORAGE.setJson(PIPELINE_STATE_KEY, PIPELINE_STATE); }

// Devuelve { status, source } donde source ∈ {'manual','priority','strategies','default'}
function getMiningStatusInfo(num) {
  // 1) Override manual en Mining Control
  if (PIPELINE_STATE.overrides[num]) {
    return { status: PIPELINE_STATE.overrides[num], source: 'manual' };
  }
  // 2) Estado de la prioridad operativa (source of truth por defecto)
  const m = (typeof PLAN_ALL !== 'undefined' ? PLAN_ALL : PLAN_MININGS).find(x => x.num === num);
  if (m) {
    const key = miningToPriorityKey(m);
    if (key && typeof PRIORITY_PROGRESS !== 'undefined' && PRIORITY_PROGRESS[key] && PRIORITY_PROGRESS[key].status) {
      return { status: PRIORITY_PROGRESS[key].status, source: 'priority' };
    }
  }
  // 3) Si hay estrategias del mining → al menos current
  const has = getAllStrategies().some(s => s.mining === num);
  if (has) return { status: 'current', source: 'strategies' };
  // 4) Default
  return { status: 'pending', source: 'default' };
}
function getMiningStatus(num) { return getMiningStatusInfo(num).status; }

function setMiningOverride(num, st) {
  PIPELINE_STATE.overrides[num] = st;
  savePipelineState();
}
function clearMiningOverride(num) {
  delete PIPELINE_STATE.overrides[num];
  savePipelineState();
}
function clearAllOverrides() {
  PIPELINE_STATE.overrides = {};
  savePipelineState();
}
function cycleMiningStatusPS(num) {
  const cur = getMiningStatus(num);
  const seq = sqxStatusSequence();
  const next = seq[(seq.indexOf(cur)+1) % seq.length];
  setMiningOverride(num, next);
  renderPipelineState();
}
window.cycleMiningStatusPS = cycleMiningStatusPS;
window.clearMiningOverride = function(num) { clearMiningOverride(num); renderPipelineState(); };

function getStrategiesByMining(num) {
  return getAllStrategies().filter(s => s.mining === num);
}
function getTemplatesByMining(num) {
  return [...new Set(getStrategiesByMining(num).map(s => s.template))].filter(t=>t && t!=='UNKNOWN');
}

function renderPsHealth() {
  const panel = document.getElementById('ps-health-panel');
  if (!panel) return;
  const allMinings = getPlanMinings();
  const allStrats = getAllStrategies();
  const total = allMinings.length;
  if (!total) {
    panel.innerHTML = '';
    return;
  }

  const completed = allMinings.filter(m => getMiningStatus(m.num) === 'completed').length;
  const inProgress = allMinings.filter(m => getMiningStatus(m.num) === 'current').length;
  const tier1 = allStrats.filter(s => s.tier === '1').length;
  const efficiency = completed > 0 ? (tier1 / completed).toFixed(1) : '0.0';
  let bottleneck = 'Ninguno';
  let bnClass = 'is-ok';
  if (inProgress > 8) {
    bottleneck = 'Exceso de Mining';
    bnClass = 'is-warn';
  } else if (completed > 0 && tier1 === 0) {
    bottleneck = 'Falta de Alpha';
    bnClass = 'is-error';
  }

  panel.innerHTML =
    '<div class="ps-h-item '+bnClass+'">' +
      '<span class="ps-h-label">Status Operativo</span>' +
      '<strong class="ps-h-val">'+bottleneck+'</strong>' +
    '</div>' +
    '<div class="ps-h-item">' +
      '<span class="ps-h-label">Alpha Efficiency</span>' +
      '<strong class="ps-h-val">'+efficiency+' <small>T1/M</small></strong>' +
    '</div>' +
    '<div class="ps-h-item">' +
      '<span class="ps-h-label">Mining Load</span>' +
      '<strong class="ps-h-val">'+Math.round(inProgress / total * 100)+'%</strong>' +
    '</div>';
}

function renderPsKpis() {
  const allMinings = getPlanMinings();
  const total = allMinings.length;
  const completed = allMinings.filter(m => getMiningStatus(m.num) === 'completed').length;
  const current   = allMinings.filter(m => getMiningStatus(m.num) === 'current').length;
  const pending   = total - completed - current;
  const pctDone   = total ? Math.round((completed/total)*100) : 0;

  const all = getAllStrategies();
  const survivors = all.filter(s => s.tier==='1' || s.tier==='1.5' || s.tier==='2').length;
  const tier1     = all.filter(s => s.tier==='1').length;
  const deployed  = all.filter(s => s.status==='DEPLOYED').length;
  const tentativas= all.filter(s => s.tier==='tentativa').length;
  const portfolioGoal = 10; // mid del rango 8-12

  document.getElementById('ps-kpis').innerHTML =
    '<div class="ps-kpi k-progress">' +
      '<div class="ps-k-label">Mining Control</div>' +
      '<div class="ps-k-value">'+completed+' / '+total+'</div>' +
      '<div class="ps-k-sub">'+current+' en curso · '+pending+' pendientes</div>' +
      '<div class="ps-k-bar-bg"><div class="ps-k-bar-fill" style="width:'+pctDone+'%"></div></div>' +
    '</div>' +
    '<div class="ps-kpi k-survivors">' +
      '<div class="ps-k-label">Supervivientes</div>' +
      '<div class="ps-k-value">'+survivors+'</div>' +
      '<div class="ps-k-sub">'+tier1+' TIER 1 · ' + (survivors-tier1) + ' TIER 1.5+2</div>' +
    '</div>' +
    '<div class="ps-kpi k-deployed">' +
      '<div class="ps-k-label">Deployed MT5</div>' +
      '<div class="ps-k-value">'+deployed+' / '+portfolioGoal+'</div>' +
      '<div class="ps-k-sub">objetivo portfolio 8-12</div>' +
      '<div class="ps-k-bar-bg"><div class="ps-k-bar-fill" style="width:'+Math.min(100, Math.round(deployed/portfolioGoal*100))+'%"></div></div>' +
    '</div>' +
    '<div class="ps-kpi k-pending">' +
      '<div class="ps-k-label">Tentativas</div>' +
      '<div class="ps-k-value">'+tentativas+'</div>' +
      '<div class="ps-k-sub">candidatas pendientes de tests</div>' +
    '</div>' +
    '<div class="ps-kpi k-time">' +
      '<div class="ps-k-label">Tiempo estimado</div>' +
      '<div class="ps-k-value">~'+(pending+current)*15+'h</div>' +
      '<div class="ps-k-sub">15h promedio por mining restante</div>' +
    '</div>';
}

function renderPsNextAction() {
  document.getElementById('ps-na-text').textContent = PIPELINE_STATE.nextAction || '(sin definir)';
}

function hasFunnelDataForKey(key) {
  const data = getFunnelData(key);
  return Object.values(data).some(function(v) { return typeof v === 'number' && v > 0; });
}

function getTemplateForMining(num, preferredTemplate) {
  const templates = getTemplatesByMining(num);
  if (preferredTemplate && (templates.includes(preferredTemplate) || hasFunnelDataForKey(num + '|' + preferredTemplate))) {
    return preferredTemplate;
  }
  if (templates.length) return templates[0];
  const funnelKey = Object.keys(PIPELINE_STATE.funnels || {}).find(function(key) {
    return key.indexOf(num + '|') === 0 && hasFunnelDataForKey(key);
  });
  return funnelKey ? funnelKey.split('|')[1] : '';
}

function getOperationalFocusModel() {
  const minings = getPlanMinings();
  if (!minings.length) return { empty:true };

  const selectedNum = parseInt((document.getElementById('ps-funnel-mining') || {}).value, 10);
  const selectedTemplate = (document.getElementById('ps-funnel-template') || {}).value || '';
  const selectedMining = minings.find(function(m) { return m.num === selectedNum; });
  const selectedKey = selectedMining && selectedTemplate ? selectedMining.num + '|' + selectedTemplate : '';
  const selectedHasData = !!selectedMining && (
    hasFunnelDataForKey(selectedKey) ||
    getStrategiesByMining(selectedMining.num).some(function(s) { return s.template === selectedTemplate; })
  );

  let mining = selectedHasData ? selectedMining : null;
  if (!mining) mining = minings.find(function(m) { return getStrategiesByMining(m.num).length > 0; }) || null;
  if (!mining) mining = minings.find(function(m) { return getMiningStatus(m.num) === 'current'; }) || null;
  if (!mining) mining = minings[0];

  const template = getTemplateForMining(mining.num, mining.num === selectedNum ? selectedTemplate : '');
  const templateLabel = template || 'Pendiente';
  const key = template ? mining.num + '|' + template : '';
  const funnel = key ? getFunnelData(key) : {};
  const initial = typeof funnel.mining === 'number' ? funnel.mining : 0;
  const terminalStage = FUNNEL_STAGES_DEFAULT[FUNNEL_STAGES_DEFAULT.length - 1];
  const terminal = terminalStage && typeof funnel[terminalStage.id] === 'number'
    ? funnel[terminalStage.id]
    : FUNNEL_STAGES_DEFAULT.reduce(function(last, stage) {
      return typeof funnel[stage.id] === 'number' ? funnel[stage.id] : last;
    }, 0);
  const survival = initial > 0 ? (terminal / initial * 100) : null;
  const allStrategies = getStrategiesByMining(mining.num);
  const strategies = template ? allStrategies.filter(function(s) { return s.template === template; }) : allStrategies;
  const tier1 = strategies.filter(function(s) { return s.tier === '1'; }).length;
  const tier15 = strategies.filter(function(s) { return s.tier === '1.5'; }).length;
  const tier2 = strategies.filter(function(s) { return s.tier === '2'; }).length;
  const tentative = strategies.filter(function(s) { return s.tier === 'tentativa'; }).length;
  const failed = strategies.reduce(function(acc, s) {
    (s.tests_failed || []).forEach(function(test) {
      if (acc.indexOf(test) === -1) acc.push(test);
    });
    return acc;
  }, []);
  const info = getMiningStatusInfo(mining.num);

  return {
    empty:false,
    mining:mining,
    template:templateLabel,
    status:info.status,
    statusLabel:sqxStatusMeta(info.status).label,
    statusSource:info.source,
    initial:initial,
    terminal:terminal,
    survival:survival,
    strategyCount:strategies.length,
    tier1:tier1,
    tier15:tier15,
    tier2:tier2,
    tentative:tentative,
    failed:failed,
    nextAction:PIPELINE_STATE.nextAction || '(sin definir)'
  };
}

function renderPsOperationalFocus() {
  const card = document.getElementById('ps-current-pipeline-status');
  if (!card) return;
  const model = getOperationalFocusModel();
  card.classList.add('ps-focus-card');
  if (model.empty) {
    card.innerHTML =
      '<div class="card-header">' +
        '<h2>Foco operativo</h2>' +
        '<span class="badge warning">Plan vacio</span>' +
      '</div>' +
      '<div class="ps-focus-empty">' +
        '<strong>No hay mining activo que dirigir.</strong>' +
        '<span>Empieza con <b>+ Mining</b> o añade assets desde <b>Por Activo</b>. Cuando exista un plan, esta tarjeta resumira el foco real, embudo, estrategias y siguiente accion.</span>' +
      '</div>';
    return;
  }

  const mining = model.mining;
  const statusClass = model.status || 'pending';
  const statusSource = model.statusSource === 'manual' ? 'manual' : (model.statusSource === 'priority' ? 'prioridad' : (model.statusSource === 'strategies' ? 'auto' : 'default'));
  const survivalLabel = model.survival == null ? 'sin embudo' : model.survival.toFixed(1) + '%';
  const funnelLabel = model.initial > 0 ? fmtInt(model.initial) + ' -> ' + fmtInt(model.terminal) : 'sin datos';
  const failedLabel = model.failed.length ? model.failed.slice(0, 2).map(planEsc).join(' · ') + (model.failed.length > 2 ? ' +' + (model.failed.length - 2) : '') : 'sin fallos registrados';

  card.innerHTML =
    '<div class="card-header">' +
      '<h2>Foco operativo</h2>' +
      '<span class="badge layer1">Mining ' + mining.num + '</span>' +
      '<span class="badge info">' + planEsc(model.template) + '</span>' +
      '<span class="status ' + statusClass + '">' + planEsc(model.statusLabel) + '</span>' +
    '</div>' +
    '<div class="ps-focus-grid">' +
      '<div class="ps-focus-main">' +
        '<div class="ps-focus-title">' +
          '<strong>' + planEsc(mining.asset) + ' ' + planEsc(mining.tf) + '</strong>' +
          '<span>' + planEsc(mining.bs) + ' · ' + planEsc(mining.dir) + ' · Fase ' + mining.phase + '</span>' +
        '</div>' +
        '<div class="ps-focus-meta">' +
          '<span class="ps-focus-pill">Estado: <strong>' + planEsc(model.statusLabel) + '</strong></span>' +
          '<span class="ps-focus-pill">Fuente: <strong>' + planEsc(statusSource) + '</strong></span>' +
          '<span class="ps-focus-pill">Template: <strong>' + planEsc(model.template) + '</strong></span>' +
        '</div>' +
        '<div class="ps-focus-next"><strong>Siguiente accion:</strong> ' + planEsc(model.nextAction) + '</div>' +
        '<div class="ps-focus-actions">' +
          '<button class="export-btn" onclick="document.getElementById(\'ps-plan-card\').scrollIntoView({behavior:\'smooth\',block:\'start\'})">Ver plan</button>' +
          '<button class="export-btn" onclick="document.getElementById(\'ps-funnel-card\').scrollIntoView({behavior:\'smooth\',block:\'start\'})">Ver embudo</button>' +
          '<button class="export-btn" onclick="activateTabById(\'estrategias\')">Ver estrategias</button>' +
        '</div>' +
      '</div>' +
      '<div class="ps-focus-metrics">' +
        '<div class="ps-focus-metric"><span>Embudo</span><strong>' + planEsc(survivalLabel) + '</strong><small>' + planEsc(funnelLabel) + '</small></div>' +
        '<div class="ps-focus-metric"><span>Estrategias</span><strong>' + model.strategyCount + '</strong><small>' + model.tier1 + ' T1 · ' + (model.tier15 + model.tier2) + ' T1.5/T2 · ' + model.tentative + ' tentativas</small></div>' +
        '<div class="ps-focus-metric"><span>Ganadoras</span><strong>' + (model.tier1 + model.tier15 + model.tier2) + '</strong><small>Supervivientes visibles para este foco</small></div>' +
        '<div class="ps-focus-metric"><span>Riesgo pendiente</span><strong>' + (model.failed.length || 0) + '</strong><small>' + failedLabel + '</small></div>' +
      '</div>' +
    '</div>';
}

function renderPsPlan() {
  refreshPlanAll();
  const allMinings = getPlanMinings();
  const allPhases = getPlanPhases();
  const phases = getPlanPhaseNums().filter(function(p) {
    return !!PLAN_USER.phases[p] || allMinings.some(function(m) { return m.phase === p; });
  });
  if (!allMinings.length && !phases.length) {
    document.getElementById('ps-plan-table').innerHTML =
      '<div class="ps-empty-plan">' +
        '<strong>Plan mining vacío</strong>' +
        '<span>Empieza desde cero con <b>+ Mining</b> o añade assets desde las tarjetas de <b>Por Activo</b>. Todo lo que agregues entrará aquí como centro de control.</span>' +
      '</div>';
    return;
  }
  const html = phases.map(p => {
    const meta = allPhases[p] || { name:'(sin nombre)', desc:'' };
    const isUserPhase = !!PLAN_USER.phases[p];
    const minings = allMinings.filter(m => m.phase === p);
    const done = minings.filter(m => getMiningStatus(m.num)==='completed').length;
    const pct = minings.length ? Math.round(done/minings.length*100) : 0;
    const rows = minings.length ? minings.map(m => {
      const info = getMiningStatusInfo(m.num);
      const st = info.status;
      const stLbl = sqxStatusMeta(st).label;
      // Badge de fuente del estado
      let srcBadge = '';
      if (info.source === 'manual') {
        srcBadge = '<span class="ps-src-badge ps-src-manual" title="Override manual. Click para volver a prioridad operativa" onclick="event.stopPropagation();clearMiningOverride('+m.num+')">Manual ↻</span>';
      } else if (info.source === 'priority') {
        srcBadge = '<span class="ps-src-badge ps-src-priority" title="Sincronizado desde prioridad operativa">Prioridad</span>';
      } else if (info.source === 'strategies') {
        srcBadge = '<span class="ps-src-badge ps-src-strategies" title="Auto-detectado: hay estrategias importadas de este mining">Auto</span>';
      }
      // Composite % del Priority si existe
      const pkey = miningToPriorityKey(m);
      let compHtml = '';
      if (pkey && typeof getScore === 'function') {
        const a = ASSETS.find(x => x.id === m.asset);
        if (a) {
          // intentar leer composite del catKey base o catKey_S según dirección
          const catBase = BS_TO_PRIORITY_CAT[m.bs];
          const sc = getScore(m.asset, m.dir==='S' ? (catBase+'_S') : catBase);
          if (sc && sc.composite != null) {
            const pct = Math.round(sc.composite * 100);
            compHtml = '<div class="ps-m-comp" title="Composite percentile data-driven">'+pct+'%</div>';
          }
        }
      }
      const survivors = getStrategiesByMining(m.num).filter(s => s.tier==='1'||s.tier==='1.5'||s.tier==='2').length;
      const tentativas = getStrategiesByMining(m.num).filter(s => s.tier==='tentativa').length;
      const tpls = getTemplatesByMining(m.num);
      const dirCls = m.dir==='L'?'dir-l':(m.dir==='S'?'dir-s':'dir-ls');
      const survBadge = survivors > 0 ?
        '<span class="ps-m-survivors" title="' + survivors + ' supervivientes (TIER 1/1.5/2)">' + survivors + '</span>' :
        '<span class="ps-m-survivors zero">0</span>';
      const tentBadge = tentativas > 0 ? ' <span class="ps-m-survivors zero" style="background:rgba(249,115,22,.12);color:var(--orange);">' + tentativas + ' ?</span>' : '';
      const tplsHtml = tpls.length ? '<div style="font-size:10px;color:var(--text2);margin-top:3px;">Templates: '+tpls.map(planEsc).join(', ')+'</div>' : '';
      const userBadge = m._user ? '<span class="ps-user-badge" title="Añadido por UI (vive en localStorage)">USER</span>' : '';
      const removeBtn = m._user ? '<button class="ps-remove-btn" title="Eliminar este mining USER" onclick="removeUserMiningClick('+m.num+')">✕</button>' : '';
      return '<tr>' +
        '<td class="ps-m-num">'+m.num+userBadge+'</td>' +
        '<td><div class="ps-m-asset">'+planEsc(m.asset)+'</div>'+tplsHtml+'</td>' +
        '<td class="ps-m-tf">'+planEsc(m.tf)+'</td>' +
        '<td><span class="ps-m-bs">'+planEsc(m.bs)+'</span></td>' +
        '<td><span class="'+dirCls+'" style="font-weight:700;font-size:12px;">'+planEsc(m.dir)+'</span></td>' +
        '<td>'+compHtml+'</td>' +
        '<td>'+survBadge+tentBadge+'</td>' +
        '<td><span class="status '+st+' clickable-status" onclick="cycleMiningStatusPS('+m.num+')">'+stLbl+'</span> '+srcBadge+removeBtn+'</td>' +
      '</tr>';
    }).join('') : '<tr class="ps-empty-phase-row"><td colspan="8">Fase sin minings todavia. Usa <strong>+ Mining</strong> y asignala a esta fase para empezar a poblarla.</td></tr>';
    const phaseCls = p > 5 ? 'p1' : 'p'+p; // las USER reusan estilo p1
    const isBasePhase = !!PHASE_META[p];
    const isCustomPhase = isUserPhase && !isBasePhase;
    const phaseUserBadge = isCustomPhase
      ? '<span class="ps-user-badge" title="Fase creada en localStorage">USER</span>'
      : (isUserPhase ? '<span class="ps-user-badge" title="Texto editado en localStorage">EDIT</span>' : '');
    const phaseEdit = '<button class="ps-phase-edit-btn" title="Editar nombre y descripcion de esta fase" onclick="editPlanPhaseClick('+p+')">Editar fase</button>';
    const phaseClear = '<button class="ps-phase-reset-btn" title="Quitar todos los minings de esta fase" onclick="resetPlanPhaseClick('+p+')">Reset fase</button>';
    const phaseReset = isCustomPhase
      ? '<button class="ps-remove-btn" title="Eliminar fase local" onclick="removeUserPhaseClick('+p+')">✕</button>'
      : (isUserPhase ? '<button class="ps-remove-btn" title="Revertir texto base de la fase" onclick="revertPlanPhaseClick('+p+')">↻</button>' : '');
    return '<div class="ps-phase">' +
      '<div class="ps-phase-head '+phaseCls+'">' +
        '<div class="ps-phase-num">'+p+'</div>' +
        '<div class="ps-phase-copy">' +
          '<h3>FASE '+p+' — '+planEsc(meta.name)+phaseUserBadge+'</h3>' +
          '<span>'+planEsc(meta.desc)+'</span>' +
        '</div>' +
        '<span class="ps-phase-count">'+done+'/'+minings.length+'</span>' +
        '<div class="ps-phase-bar"><div style="width:'+pct+'%"></div></div>' +
        '<div class="ps-phase-tools">'+phaseEdit+phaseClear+phaseReset+'</div>' +
      '</div>' +
      '<table class="ps-mining-table">' +
        '<thead><tr><th>#</th><th>Asset</th><th>TF</th><th>Blocksetting</th><th>Dir</th><th>Composite</th><th>Estrategias</th><th>Estado</th></tr></thead>' +
        '<tbody>'+rows+'</tbody>' +
      '</table>' +
    '</div>';
  }).join('');
  document.getElementById('ps-plan-table').innerHTML = html;
}

function getCurrentFunnelKey() {
  const m = document.getElementById('ps-funnel-mining').value;
  const t = document.getElementById('ps-funnel-template').value;
  return m + '|' + t;
}

function getFunnelData(key) {
  return PIPELINE_STATE.funnels[key] || {};
}

function setFunnelValue(key, stage, val) {
  if (!PIPELINE_STATE.funnels[key]) PIPELINE_STATE.funnels[key] = {};
  if (val === '' || val == null) delete PIPELINE_STATE.funnels[key][stage];
  else PIPELINE_STATE.funnels[key][stage] = parseInt(val,10) || 0;
  savePipelineState();
}

function populateFunnelSelectors() {
  const selM = document.getElementById('ps-funnel-mining');
  const selT = document.getElementById('ps-funnel-template');
  // mining selector
  const planNums = getPlanMinings().map(function(m) { return m.num; });
  const miningsWithStrats = getAllStrategies().map(function(s) { return s.mining; });
  const miningsAll = [...new Set(planNums.concat(miningsWithStrats))].filter(Boolean).sort((a,b)=>a-b);
  if (!miningsAll.length) miningsAll.push(1);
  const curM = parseInt(selM.value,10) || miningsAll[0];
  selM.innerHTML = miningsAll.map(m => '<option value="'+m+'">Mining '+m+'</option>').join('');
  selM.value = miningsAll.includes(curM) ? curM : miningsAll[0];
  // template selector
  const tpls = getTemplatesByMining(parseInt(selM.value,10));
  const funnelTemplates = Object.keys(PIPELINE_STATE.funnels || {}).filter(function(key) {
    return key.indexOf(selM.value + '|') === 0;
  }).map(function(key) { return key.split('|')[1]; });
  const tplsAll = [...new Set(tpls.concat(funnelTemplates))].filter(Boolean);
  if (!tplsAll.length) tplsAll.push('LINEAR');
  const curT = selT.value || tplsAll[0];
  selT.innerHTML = tplsAll.map(t => '<option value="'+t+'">'+t+'</option>').join('');
  selT.value = tplsAll.includes(curT) ? curT : tplsAll[0];
}

function renderPsFunnel() {
  const key = getCurrentFunnelKey();
  const data = getFunnelData(key);
  const stages = FUNNEL_STAGES_DEFAULT;
  const initial = data[stages[0].id] || 0;

  let html = '<div class="ps-funnel-graph">';
  for (let i = 0; i < stages.length; i++) {
    const stage = stages[i];
    const v = data[stage.id];
    const safeValue = typeof v === 'number' ? v : 0;
    const valStr = v == null ? '0' : v;
    const prevValue = i === 0 ? initial : (data[stages[i - 1].id] || 0);
    const wTop = initial > 0 ? Math.max(15, (prevValue / initial) * 100) : 100;
    const wBot = initial > 0 ? Math.max(15, (safeValue / initial) * 100) : 100;
    const survNum = initial > 0 ? safeValue / initial * 100 : 0;
    const surv = survNum.toFixed(1) + '%';
    const cls = stage.terminal ? 'ps-funnel-step-graph terminal' : 'ps-funnel-step-graph';
    const tL = (100 - wTop) / 2;
    const tR = 100 - tL;
    const bL = (100 - wBot) / 2;
    const bR = 100 - bL;
    const clipPath = 'polygon('+tL+'% 0%, '+tR+'% 0%, '+bR+'% 100%, '+bL+'% 100%)';
    const hue = Math.round(200 + (survNum * 0.5));
    const bg = 'linear-gradient(135deg, hsla('+hue+', 80%, 50%, 0.8), hsla('+(hue + 40)+', 80%, 40%, 0.8))';

    html += '<div class="'+cls+'">' +
      '<div class="pf-shape" style="clip-path:'+clipPath+';background:'+bg+'"></div>' +
      '<div class="pf-label-layer">' +
        '<div class="pf-name">'+stage.name+'</div>' +
        '<div class="pf-metrics-wrap">' +
          '<span class="pf-count-big" data-stage="'+stage.id+'" onclick="editFunnelCell(this, \''+key+'\', \''+stage.id+'\')">'+valStr+'</span>' +
          '<span class="pf-survival-tag">'+surv+'</span>' +
        '</div>' +
      '</div>' +
    '</div>';
  }
  html += '</div>';
  document.getElementById('ps-funnel').innerHTML = html;
}

window.editFunnelCell = function(el, key, stage) {
  if (el.classList.contains('editing')) return;
  const cur = el.textContent.trim();
  el.classList.add('editing');
  el.innerHTML = '<input type="number" min="0" value="'+(cur==='—'?'':cur)+'">';
  const inp = el.querySelector('input');
  inp.focus(); inp.select();
  function commit() {
    const v = inp.value.trim();
    setFunnelValue(key, stage, v);
    el.classList.remove('editing');
    renderPsOperationalFocus();
    renderPsFunnel();
  }
  inp.addEventListener('blur', commit);
  inp.addEventListener('keydown', function(e){
    if (e.key === 'Enter') { e.preventDefault(); commit(); }
    if (e.key === 'Escape') { el.classList.remove('editing'); renderPsFunnel(); }
  });
};

// ── Precarga desde Por Activo: items añadidos con + Plan y ya unidos al plan ──
function getOrphanPriorityItems() {
  if (typeof PRIORITY_PROGRESS === 'undefined') return [];
  const planKeys = new Set(getPlanMinings().map(m => miningToPriorityKey(m)).filter(Boolean));
  const out = [];
  for (const [key, val] of Object.entries(PRIORITY_PROGRESS)) {
    const status = val && val.status;
    if (status !== 'current' && status !== 'completed') continue;
    if (planKeys.has(key)) continue;
    const parts = key.split('|');
    if (parts.length !== 4) continue;
    const [asset, cat, tfRaw, dir] = parts;
    if (!PRIORITY_CAT_TO_BS[cat]) continue;
    // Detectar key legacy con múltiples TFs ("H1, H4, D1") → split en múltiples orphans
    const tfs = tfRaw.includes(',') ? tfRaw.split(',').map(t => t.trim()).filter(Boolean) : [tfRaw];
    const isLegacy = tfs.length > 1;
    for (const tf of tfs) {
      // Si este TF específico ya tiene un mining en el plan → no es huérfano
      const newKey = asset+'|'+cat+'|'+tf+'|'+dir;
      if (planKeys.has(newKey)) continue;
      // Composite del scoring
      let comp = null;
      const a = (typeof ASSETS !== 'undefined') ? ASSETS.find(x => x.id === asset) : null;
      if (a && typeof getScore === 'function') {
        const sc = getScore(asset, dir==='S' ? (cat+'_S') : cat);
        if (sc && sc.composite != null) comp = Math.round(sc.composite * 100);
      }
      out.push({ origKey: key, key: newKey, asset, cat, tf, dir, status, bs: PRIORITY_CAT_TO_BS[cat], composite: comp, isLegacy });
    }
  }
  out.sort((a,b) => {
    if (a.status !== b.status) return a.status === 'completed' ? -1 : 1;
    return (b.composite||0) - (a.composite||0);
  });
  return out;
}

function renderOrphans() {
  const card = document.getElementById('ps-orphans-card');
  const list = document.getElementById('ps-orphans-list');
  if (!card || !list) return;
  const preloaded = PLAN_USER.minings.filter(function(m) { return m.source === 'asset-card'; });
  if (!preloaded.length) { card.style.display = 'none'; list.innerHTML = ''; return; }
  card.style.display = 'block';
  list.innerHTML = preloaded.map(function(m) {
    const dirCls = m.dir==='L'?'dir-l':(m.dir==='S'?'dir-s':'dir-ls');
    const dirTxt = m.dir==='L'?'LONG':(m.dir==='S'?'SHORT':'L+S');
    const phaseMeta = getPlanPhases()[m.phase] || { name: '' };
    return '<div class="ps-orphan-row">' +
      '<span class="po-asset">'+planEsc(m.asset)+'</span>' +
      '<span class="po-cat">FASE '+m.phase+(phaseMeta.name ? ' · '+planEsc(phaseMeta.name) : '')+'</span>' +
      '<span class="po-tf">'+planEsc(m.tf)+'</span>' +
      '<span class="'+dirCls+' po-dir">'+dirTxt+'</span>' +
      '<span class="po-bs">'+planEsc(m.bs)+'</span>' +
      '<span class="po-status current">Mining #'+m.num+'</span>' +
      '<button class="po-add-btn" onclick="document.getElementById(\'ps-plan-card\').scrollIntoView({behavior:\'smooth\',block:\'start\'})">Ver en plan</button>' +
      '<button class="po-remove-btn" title="Quitar esta precarga del Plan mining" onclick="removeUserMiningClick('+m.num+')">Quitar</button>' +
    '</div>';
  }).join('');
}

window.removeOrphanFromPriority = function(origKey, isLegacy) {
  if (typeof PRIORITY_PROGRESS === 'undefined') return;
  if (!PRIORITY_PROGRESS[origKey]) { renderPipelineState(); return; }
  const msg = isLegacy
    ? '¿Eliminar la key legacy "'+origKey+'" de la prioridad operativa? (Contiene varios TFs juntos; se borran todos.)'
    : '¿Eliminar este item de la prioridad operativa?';
  if (!confirm(msg)) return;
  delete PRIORITY_PROGRESS[origKey];
  if (typeof savePriorityProgress === 'function') savePriorityProgress();
  if (typeof renderPriority === 'function') renderPriority();
  renderPipelineState();
};

window.promoteOrphanToPlan = function(key) {
  const parts = key.split('|');
  if (parts.length !== 4) return;
  const [asset, cat, tf, dir] = parts;
  const bs = PRIORITY_CAT_TO_BS[cat];
  if (!bs) { alert('Categoría desconocida: '+cat); return; }
  // Abrir modal pre-rellenado
  openAddMiningModal();
  document.getElementById('psm-num').value = nextMiningNum();
  document.getElementById('psm-asset').value = asset;
  document.getElementById('psm-tf').value = tf;
  document.getElementById('psm-bs').value = bs;
  document.getElementById('psm-dir').value = dir;
  // Sugerir fase: si el asset coincide con el de alguna fase DEFAULT lo elegimos, si no la última
  const phaseSel = document.getElementById('psm-phase');
  const allMin = getPlanMinings();
  const sameAssetMining = allMin.find(m => m.asset === asset);
  if (sameAssetMining) phaseSel.value = String(sameAssetMining.phase);
};

function renderPipelineState() {
  renderPsKpis();
  renderPsHealth();
  renderPsPlan();
  populateFunnelSelectors();
  renderPsNextAction();
  renderPsOperationalFocus();
  renderPsFunnel();
  renderOrphans();
  // override info bar
  const ovCount = Object.keys(PIPELINE_STATE.overrides || {}).length;
  const info = document.getElementById('ps-overrides-info');
  const restore = document.getElementById('ps-restore-auto');
  if (info && restore) {
    if (ovCount > 0) {
      info.style.display = 'inline-block';
      info.textContent = '✏ ' + ovCount + ' override' + (ovCount===1?'':'s') + ' manual' + (ovCount===1?'':'es');
      restore.style.display = 'inline-block';
    } else {
      info.style.display = 'none';
      restore.style.display = 'none';
    }
  }
  // counts del plan
  const allMinings = getPlanMinings();
  const allPhasesCount = getPlanPhaseNums().filter(p => allMinings.some(m => m.phase === p)).length;
  const cntEl = document.getElementById('ps-plan-counts');
  if (cntEl) cntEl.textContent = allPhasesCount + ' fases · ' + allMinings.length + ' minings';
  // banner USER
  const userInfo = document.getElementById('ps-plan-user-info');
  if (userInfo) {
    const editedPhases = Object.keys(PLAN_USER.phases || {}).length;
    const addedMinings = PLAN_USER.minings.length;
    const hiddenBase = (PLAN_USER.hiddenBaseMinings || []).length;
    const baseDisabled = !!PLAN_USER.baseDisabled;
    const userCount = addedMinings + editedPhases + hiddenBase + (baseDisabled ? 1 : 0);
    userInfo.style.display = userCount > 0 ? 'block' : 'none';
    const cnt = document.getElementById('ps-plan-user-count');
    if (cnt) cnt.textContent = addedMinings;
    const summary = document.getElementById('ps-plan-user-summary');
    if (summary) {
      const parts = [];
      if (addedMinings) parts.push(addedMinings + ' mining' + (addedMinings===1?'':'s') + ' añadidos');
      if (editedPhases) parts.push(editedPhases + ' fase' + (editedPhases===1?'':'s') + '/texto' + (editedPhases===1?'':'s'));
      if (hiddenBase) parts.push(hiddenBase + ' base oculto' + (hiddenBase===1?'':'s'));
      if (baseDisabled) parts.push('plan base desactivado');
      summary.textContent = parts.length ? parts.join(' · ') : '';
    }
    const preview = document.getElementById('ps-plan-user-preview');
    if (preview) {
      const sample = PLAN_USER.minings.slice(0, 8).map(function(m) {
        return '<span>'+planEsc(m.asset)+' '+planEsc(m.tf)+' · F'+m.phase+' · '+planEsc(m.bs)+'</span>';
      }).join('');
      const more = PLAN_USER.minings.length > 8 ? '<span>+'+(PLAN_USER.minings.length - 8)+' mas</span>' : '';
      const baseFlag = baseDisabled ? '<span>Base apagada</span>' : '';
      preview.innerHTML = sample + more + baseFlag;
    }
  }
  renderHome();
}

// listeners
document.getElementById('ps-funnel-mining').addEventListener('change', function(){
  populateFunnelSelectors();
  renderPsOperationalFocus();
  renderPsFunnel();
});
document.getElementById('ps-funnel-template').addEventListener('change', function() {
  renderPsOperationalFocus();
  renderPsFunnel();
});

document.getElementById('ps-na-edit').addEventListener('click', function(){
  const v = prompt('Próxima acción inmediata:', PIPELINE_STATE.nextAction || '');
  if (v != null) { PIPELINE_STATE.nextAction = v.trim(); savePipelineState(); renderPsNextAction(); renderPsOperationalFocus(); }
});

document.getElementById('ps-plan-reset').addEventListener('click', function(){
  if (confirm('¿Resetear estados del plan mining? Borra overrides manuales y vuelve a la prioridad operativa. No afecta fases, assets, estrategias ni embudos.')) {
    PIPELINE_STATE.overrides = {};
    savePipelineState();
    renderPipelineState();
  }
});

document.getElementById('ps-plan-reset-plan').addEventListener('click', function(){
  const editedPhases = Object.keys(PLAN_USER.phases || {}).length;
  const addedMinings = PLAN_USER.minings.length;
  const hiddenBase = (PLAN_USER.hiddenBaseMinings || []).length;
  const hasBase = !PLAN_USER.baseDisabled && PLAN_MININGS.length > 0;
  if (!editedPhases && !addedMinings && !hiddenBase && !hasBase && !Object.keys(PIPELINE_STATE.overrides || {}).length) return;
  if (confirm('¿Resetear TODO el Plan mining? Se borran minings añadidos, se oculta el plan base y se limpian estados/embudos para empezar desde cero.')) {
    resetPlanMiningUserState();
    renderPipelineState();
  }
});

document.getElementById('ps-restore-auto').addEventListener('click', function(){
  const n = Object.keys(PIPELINE_STATE.overrides || {}).length;
  if (!n) return;
  if (confirm('¿Limpiar los '+n+' override(s) manual(es) y volver a la prioridad operativa?')) {
    clearAllOverrides();
    renderPipelineState();
  }
});

// ── B.2: gestión del plan (modales + listeners) ──
function openAddMiningModal() {
  // pre-fill num auto + populate fase select
  document.getElementById('psm-num').value = nextMiningNum();
  const sel = document.getElementById('psm-phase');
  const phases = getPlanPhaseNums();
  const meta = getPlanPhases();
  const modalPhases = phases.length ? phases : [1];
  sel.innerHTML = modalPhases.map(p => '<option value="'+p+'">FASE '+p+' — '+(meta[p]?.name || 'Manual')+'</option>').join('');
  document.getElementById('ps-add-mining-backdrop').style.display = 'flex';
}
function closeAddMiningModal() { document.getElementById('ps-add-mining-backdrop').style.display = 'none'; }

function openAddPhaseModal() {
  document.getElementById('psp-num').value = nextPhaseNum();
  document.getElementById('psp-name').value = '';
  document.getElementById('psp-desc').value = '';
  document.getElementById('ps-add-phase-backdrop').style.display = 'flex';
}
function closeAddPhaseModal() { document.getElementById('ps-add-phase-backdrop').style.display = 'none'; }

function saveAddMining() {
  const m = {
    num:    parseInt(document.getElementById('psm-num').value, 10),
    phase:  parseInt(document.getElementById('psm-phase').value, 10),
    asset:  (document.getElementById('psm-asset').value || '').trim().toUpperCase(),
    tf:     document.getElementById('psm-tf').value,
    bs:     document.getElementById('psm-bs').value,
    dir:    document.getElementById('psm-dir').value,
  };
  if (!m.num || !m.phase || !m.asset) { alert('Faltan campos obligatorios.'); return; }
  if (!addMiningUser(m)) { alert('Mining #'+m.num+' ya existe en el plan.'); return; }
  closeAddMiningModal();
  renderPipelineState();
}

function saveAddPhase() {
  const num  = parseInt(document.getElementById('psp-num').value, 10);
  const name = (document.getElementById('psp-name').value || '').trim();
  const desc = (document.getElementById('psp-desc').value || '').trim();
  if (!num || !name) { alert('Número y nombre son obligatorios.'); return; }
  if (!addPhaseUser(num, name, desc)) { alert('Fase '+num+' ya existe.'); return; }
  closeAddPhaseModal();
  renderPipelineState();
}

window.removeUserMiningClick = function(num) {
  if (confirm('¿Eliminar mining #'+num+' del plan USER?')) { removeUserMining(num); renderPipelineState(); }
};
window.removeUserPhaseClick = function(num) {
  if (confirm('¿Eliminar fase '+num+' del plan USER?')) { if (removeUserPhase(num)) renderPipelineState(); }
};
window.editPlanPhaseClick = function(num) {
  const phases = getPlanPhases();
  const meta = phases[num] || { name:'', desc:'' };
  const name = prompt('Nombre corto de la fase '+num+':', meta.name || '');
  if (name == null) return;
  const cleanName = name.trim();
  if (!cleanName) { alert('El nombre de fase no puede quedar vacío.'); return; }
  const desc = prompt('Descripción operativa de la fase '+num+':', meta.desc || '');
  if (desc == null) return;
  setPhaseMetaUser(num, cleanName, desc.trim());
  renderPipelineState();
};
window.revertPlanPhaseClick = function(num) {
  if (confirm('¿Revertir el texto editado de la fase '+num+' y volver al valor base?')) {
    if (revertPhaseMetaUser(num)) renderPipelineState();
  }
};
window.resetPlanPhaseClick = function(num) {
  const p = parseInt(num, 10);
  const phaseMinings = getPlanMinings().filter(function(m) { return m.phase === p; });
  if (!phaseMinings.length) return;
  if (confirm('¿Resetear todos los minings de la fase '+p+'? Se quitan del Plan mining los base y los añadidos de esa fase.')) {
    if (resetPlanPhaseMinings(p)) renderPipelineState();
  }
};

document.getElementById('ps-add-mining-btn').addEventListener('click', openAddMiningModal);
document.getElementById('ps-add-phase-btn').addEventListener('click', openAddPhaseModal);
document.getElementById('ps-add-mining-close').addEventListener('click', closeAddMiningModal);
document.getElementById('ps-add-phase-close').addEventListener('click', closeAddPhaseModal);
document.getElementById('ps-add-mining-backdrop').addEventListener('click', function(e){ if (e.target === this) closeAddMiningModal(); });
document.getElementById('ps-add-phase-backdrop').addEventListener('click', function(e){ if (e.target === this) closeAddPhaseModal(); });
document.getElementById('psm-cancel').addEventListener('click', closeAddMiningModal);
document.getElementById('psp-cancel').addEventListener('click', closeAddPhaseModal);
document.getElementById('psm-save').addEventListener('click', saveAddMining);
document.getElementById('psp-save').addEventListener('click', saveAddPhase);

document.getElementById('ps-clear-plan-user-btn').addEventListener('click', function(){
  const n = PLAN_USER.minings.length + Object.keys(PLAN_USER.phases).length + (PLAN_USER.hiddenBaseMinings || []).length + (PLAN_USER.baseDisabled ? 1 : 0);
  if (!n) return;
  if (confirm('¿Limpiar la precarga local del plan? Se borran minings añadidos y textos editados; se restaura el plan base.')) {
    clearPlanUser(); renderPipelineState();
  }
});

document.getElementById('ps-project-zero-state').addEventListener('click', function(){
  if (confirm('¿Poner a cero el proyecto operativo local? Se borran plan, prioridad, embudos, estrategias visibles, checklist y presets de trabajo. No se toca licencia ni API.')) {
    resetProjectWorkingData();
    alert('Proyecto limpio activado. Ya puedes validar el flujo desde datos nuevos.');
  }
});

document.getElementById('ps-consolidate-plan').addEventListener('click', function(){
  const all = getPlanMinings().map(m => { const c = {...m}; delete c._user; return c; });
  const phases = getPlanPhases();
  const minJson = JSON.stringify(all, null, 2);
  const phJson  = JSON.stringify(phases, null, 2);
  const wrapper = JSON.stringify({ version: 1, minings: all, phases: phases }, null, 2);
  const w = window.open('', '_blank', 'width=900,height=700');
  if (w) {
    w.document.write('<html><head><title>SQX Plan — Consolidado</title><style>body{background:#0f1117;color:#e4e4e7;font-family:Segoe UI,sans-serif;padding:20px;}h1{font-size:16px;margin-bottom:10px;}p{color:#9ca3af;font-size:12px;margin-bottom:14px;}pre{background:#0a0c12;border:1px solid #2e3348;border-radius:8px;padding:14px;font-family:Consolas,monospace;font-size:12px;color:#9eb1d3;line-height:1.5;overflow:auto;max-height:80vh;white-space:pre-wrap;}button{margin-bottom:10px;padding:8px 16px;background:#22c55e;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:700;}</style></head><body>');
    w.document.write('<h1>Consolidado: '+all.length+' minings · '+Object.keys(phases).length+' fases</h1>');
    w.document.write('<p>JSON compatible con <code>backend/sqx-edge-tool/config/plan.json</code>.</p>');
    w.document.write('<button onclick="navigator.clipboard.writeText(document.getElementById(\'cn\').textContent).then(()=>this.textContent=\'Copiado\')">Copiar al portapapeles</button>');
    w.document.write('<pre id="cn">'+wrapper.replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]))+'</pre>');
    w.document.write('</body></html>');
    w.document.close();
  } else {
    navigator.clipboard.writeText(wrapper);
    alert('Popup bloqueado. He copiado el snippet al portapapeles ('+all.length+' minings · '+Object.keys(phases).length+' fases).');
  }
});

// ============================================================
// CSV IMPORT — Databank Export de SQX
// ============================================================
const STRAT_USER_KEY = SQX_STORAGE_KEYS.strategiesUser || 'sqx_strategies_user_v1';
const STRAT_DELETED_KEY = SQX_STORAGE_KEYS.strategiesDeleted || 'sqx_strategies_deleted_v1';
let STRATEGIES_USER = [];
let STRATEGIES_DELETED = [];
STRATEGIES_USER = SQX_STORAGE.getJson(STRAT_USER_KEY, []);
STRATEGIES_DELETED = SQX_STORAGE.getJson(STRAT_DELETED_KEY, []);
if (!Array.isArray(STRATEGIES_USER)) STRATEGIES_USER = [];
if (!Array.isArray(STRATEGIES_DELETED)) STRATEGIES_DELETED = [];
function saveStrategiesUser() { SQX_STORAGE.setJson(STRAT_USER_KEY, STRATEGIES_USER); }
function saveStrategiesDeleted() { SQX_STORAGE.setJson(STRAT_DELETED_KEY, STRATEGIES_DELETED); }

function resetProjectWorkingData() {
  resetPlanMiningUserState();

  PRIORITY_PROGRESS = {};
  savePriorityProgress();

  PIPELINE_STATE = { overrides:{}, funnels:{}, nextAction:'' };
  savePipelineState();

  STRATEGIES_USER = [];
  STRATEGIES_DELETED = STRATEGIES.map(strategyKey);
  saveStrategiesUser();
  saveStrategiesDeleted();

  HOME_TRACE = [];
  saveHomeTrace();

  [
    SQX_STORAGE_KEYS.workflowChecklist || 'sqx_workflow_checklist_v1',
    SQX_STORAGE_KEYS.viewCreatorPresets || 'sqx_view_creator_presets_v1',
    'sqx_pg_custom_presets_v1'
  ].forEach(function(key) {
    try { localStorage.removeItem(key); } catch (err) {}
  });

  renderPriority();
  renderStrategies();
  renderPipelineState();
  renderHomeTrace();
  renderHome();
}
window.resetProjectWorkingData = resetProjectWorkingData;

const SQX_COLUMN_MAP = sqxConfigValue('csvImport.columnMap', {});

function autoDetectTemplate(indicators) {
  const rules = sqxConfigValue('csvImport.templateKeywords', []);
  if (SQX_STRATEGIES.autoDetectTemplate) return SQX_STRATEGIES.autoDetectTemplate(indicators, rules);
  if (!indicators) return null;
  const ind = indicators.toUpperCase();
  for (const rule of rules) {
    if ((rule.keywords || []).some(keyword => ind.includes(keyword))) return rule.template;
  }
  return null;
}

// Parser CSV simple — separador configurable, soporte comillas con escape ""
function parseCSV(text, sep) {
  if (SQX_STRATEGIES.parseCSV) return SQX_STRATEGIES.parseCSV(text, sep);
  const rows = [];
  let cur = '', inQuotes = false, row = [];
  for (let i = 0; i < text.length; i++) {
    const c = text[i], n = text[i+1];
    if (inQuotes) {
      if (c === '"' && n === '"') { cur += '"'; i++; }
      else if (c === '"') { inQuotes = false; }
      else { cur += c; }
    } else {
      if (c === '"') { inQuotes = true; }
      else if (c === sep) { row.push(cur); cur = ''; }
      else if (c === '\n') { row.push(cur); rows.push(row); row = []; cur = ''; }
      else if (c === '\r') { /* skip */ }
      else { cur += c; }
    }
  }
  if (cur !== '' || row.length) { row.push(cur); rows.push(row); }
  return rows.filter(r => r.length > 1 || (r.length === 1 && r[0].trim() !== ''));
}

function detectSeparator(text) {
  if (SQX_STRATEGIES.detectSeparator) return SQX_STRATEGIES.detectSeparator(text);
  const sample = text.split('\n')[0] || '';
  const semis = (sample.match(/;/g) || []).length;
  const commas = (sample.match(/,/g) || []).length;
  return semis > commas ? ';' : ',';
}

const csvImport = {
  step: 1, rows: [], headers: [], mapping: {}, selected: new Set(), filter: '', sortCol: null, sortDir: 'desc'
};

function openImportModal() {
  csvImport.step = 1; csvImport.rows = []; csvImport.headers = []; csvImport.mapping = {};
  csvImport.selected = new Set(); csvImport.filter = ''; csvImport.sortCol = null; csvImport.sortDir = 'desc';
  document.getElementById('csv-file-info').style.display = 'none';
  document.getElementById('csv-mapping-summary').innerHTML = '';
  document.getElementById('strat-import-backdrop').style.display = 'flex';
  showStep(1);
}
function closeImportModal() { document.getElementById('strat-import-backdrop').style.display = 'none'; }

function showStep(n) {
  csvImport.step = n;
  for (let i = 1; i <= 4; i++) {
    const pane = document.getElementById('csv-pane-'+i);
    pane.style.display = (i === n) ? 'block' : 'none';
    pane.classList.toggle('active', i === n);
    const stepEl = document.querySelector('.csv-step[data-step="'+i+'"]');
    stepEl.classList.toggle('active', i === n);
    stepEl.classList.toggle('done', i < n);
  }
  document.getElementById('csv-back-btn').disabled = (n === 1);
  const next = document.getElementById('csv-next-btn');
  const finish = document.getElementById('csv-finish-btn');
  if (n === 4) { next.style.display = 'none'; finish.style.display = 'inline-block'; }
  else { next.style.display = 'inline-block'; finish.style.display = 'none'; }
  // habilita next según condiciones
  if (n === 1) next.disabled = csvImport.rows.length === 0;
  else if (n === 3) next.disabled = csvImport.selected.size === 0;
  else next.disabled = false;

  if (n === 3) renderCsvPreview();
  if (n === 4) renderCsvConfirm();
}

function readCsvFile(file) {
  const r = new FileReader();
  r.onload = function(ev) {
    const text = ev.target.result;
    const sep = detectSeparator(text);
    const rows = parseCSV(text, sep);
    if (rows.length < 2) { alert('CSV vacío o no válido.'); return; }
    csvImport.headers = rows[0];
    csvImport.rows = rows.slice(1).map(r => {
      const obj = {};
      csvImport.headers.forEach((h, i) => { obj[h] = (r[i] !== undefined ? r[i] : ''); });
      return obj;
    });
    // mapping automático
    csvImport.mapping = {};
    csvImport.headers.forEach(h => { if (SQX_COLUMN_MAP[h]) csvImport.mapping[h] = SQX_COLUMN_MAP[h]; });
    const recognized = Object.keys(csvImport.mapping).length;
    const total = csvImport.headers.length;
    document.getElementById('csv-file-name').textContent = file.name;
    document.getElementById('csv-file-meta').textContent = (file.size/1024).toFixed(1)+' KB · separador "'+sep+'" · '+csvImport.rows.length+' filas · '+total+' columnas';
    const ok = recognized === total ? 'var(--green)' : (recognized >= total*0.7 ? 'var(--accent)' : 'var(--yellow)');
    document.getElementById('csv-mapping-summary').innerHTML =
      '<span style="color:'+ok+'; font-weight:700;">'+recognized+'/'+total+'</span> columnas reconocidas automáticamente del esquema SQX. ' +
      (recognized < total ? '<span style="color:var(--text2);">Las no reconocidas se ignoran al importar.</span>' : '');
    document.getElementById('csv-file-info').style.display = 'block';
    // auto-seleccionar todas
    csvImport.selected = new Set(csvImport.rows.map((_,i)=>i));
    showStep(1); // refresh next button
  };
  r.readAsText(file, 'UTF-8');
}

function getCsvFilteredRows() {
  if (SQX_STRATEGIES.filterCsvRows) {
    return SQX_STRATEGIES.filterCsvRows(csvImport.rows, {
      filter: csvImport.filter,
      sortCol: csvImport.sortCol,
      sortDir: csvImport.sortDir
    });
  }
  const q = csvImport.filter.toLowerCase().trim();
  let rows = csvImport.rows.map((r,i) => ({_idx:i, ...r}));
  if (q) {
    rows = rows.filter(r =>
      (r['Strategy Name']||'').toLowerCase().includes(q) ||
      (r['Entry indicators']||'').toLowerCase().includes(q)
    );
  }
  if (csvImport.sortCol) {
    const col = csvImport.sortCol;
    const dir = csvImport.sortDir === 'asc' ? 1 : -1;
    rows.sort((a,b) => {
      const va = parseFloat(a[col]); const vb = parseFloat(b[col]);
      const na = isNaN(va), nb = isNaN(vb);
      if (na && nb) return (a[col]||'').localeCompare(b[col]||'') * dir;
      if (na) return 1; if (nb) return -1;
      return (va - vb) * dir;
    });
  }
  return rows;
}

function renderCsvPreview() {
  const rows = getCsvFilteredRows();
  document.getElementById('csv-row-count').textContent = csvImport.rows.length;
  document.getElementById('csv-selected-count').textContent = csvImport.selected.size;
  const t = document.getElementById('csv-preview-table');
  if (SQX_STRATEGIES.csvPreviewTable) {
    t.innerHTML = SQX_STRATEGIES.csvPreviewTable(rows, {
      selected: csvImport.selected,
      sortCol: csvImport.sortCol,
      sortDir: csvImport.sortDir
    }, {
      autoDetectTemplate: autoDetectTemplate
    });
  } else {
    const cols = ['Strategy Name','Net profit','Profit factor','Sharpe Ratio','Ret/DD Ratio','Max DD %','# of trades','Winning Percent','SQN Score','R Expectancy','Stagnation','Entry indicators'];
    const head = '<thead><tr><th style="width:30px;"><input type="checkbox" id="csv-th-check"></th>' +
      cols.map(c => {
        const arrow = csvImport.sortCol === c ? (csvImport.sortDir==='asc'?' ▲':' ▼') : '';
        return '<th class="sortable" data-col="'+c+'">'+c+arrow+'</th>';
      }).join('') + '<th>TPL</th></tr></thead>';
    const body = '<tbody>' + rows.map(r => {
      const idx = r._idx;
      const checked = csvImport.selected.has(idx) ? 'checked' : '';
      const tpl = autoDetectTemplate(r['Entry indicators']) || '—';
      const cells = cols.map(c => {
        const v = r[c] || '';
        if (c === 'Strategy Name') return '<td class="cv-id">'+v+'</td>';
        if (c === 'Entry indicators') return '<td style="font-size:11px; color:var(--text2); max-width:280px; white-space:normal;">'+v+'</td>';
        return '<td class="cv-num">'+v+'</td>';
      }).join('');
      return '<tr><td><input type="checkbox" class="cv-row-check" data-idx="'+idx+'" '+checked+'></td>' + cells + '<td><span class="cv-tpl">'+tpl+'</span></td></tr>';
    }).join('') + '</tbody>';
    t.innerHTML = head + body;
  }
  // events
  document.getElementById('csv-th-check').checked = (csvImport.selected.size === csvImport.rows.length);
  document.getElementById('csv-th-check').addEventListener('change', function(){
    if (this.checked) csvImport.selected = new Set(csvImport.rows.map((_,i)=>i));
    else csvImport.selected = new Set();
    renderCsvPreview(); showStep(3);
  });
  t.querySelectorAll('.cv-row-check').forEach(cb => cb.addEventListener('change', function(){
    const i = parseInt(this.dataset.idx,10);
    if (this.checked) csvImport.selected.add(i); else csvImport.selected.delete(i);
    document.getElementById('csv-selected-count').textContent = csvImport.selected.size;
    document.getElementById('csv-next-btn').disabled = csvImport.selected.size === 0;
  }));
  t.querySelectorAll('th.sortable').forEach(th => th.addEventListener('click', function(){
    const c = this.dataset.col;
    if (csvImport.sortCol === c) csvImport.sortDir = csvImport.sortDir === 'asc' ? 'desc' : 'asc';
    else { csvImport.sortCol = c; csvImport.sortDir = 'desc'; }
    renderCsvPreview();
  }));
}

function renderCsvConfirm() {
  const meta = readImportMeta();
  document.getElementById('csv-confirm-summary').innerHTML = SQX_STRATEGIES.csvConfirmHtml
    ? SQX_STRATEGIES.csvConfirmHtml(meta, csvImport.selected, csvImport.rows)
    : '<div><strong>'+csvImport.selected.size+'</strong> estrategia(s) se importarán.</div>';
}

function readImportMeta() {
  return {
    mining:       parseInt(document.getElementById('csv-meta-mining').value, 10) || 1,
    bs:           document.getElementById('csv-meta-bs').value,
    template:     (document.getElementById('csv-meta-template').value || '').trim(),
    autoTemplate: document.getElementById('csv-meta-autotemplate').value === 'yes',
    dir:          document.getElementById('csv-meta-dir').value,
    tier:         document.getElementById('csv-meta-tier').value,
    status:       document.getElementById('csv-meta-status').value,
    phase:        document.getElementById('csv-meta-phase').value,
    notes:        (document.getElementById('csv-meta-notes').value || '').trim(),
  };
}

function rowToStrategy(row, meta) {
  if (SQX_STRATEGIES.rowToStrategy) {
    return SQX_STRATEGIES.rowToStrategy(row, meta, {
      columnMap: SQX_COLUMN_MAP,
      templateRules: sqxConfigValue('csvImport.templateKeywords', [])
    });
  }
  const sn = (row['Strategy Name'] || '').trim();
  const id = sn.replace(/^Strategy\s+/i, '') || sn;
  const indicators = row['Entry indicators'] || '';
  let template = meta.template || 'UNKNOWN';
  if (meta.autoTemplate) {
    const auto = autoDetectTemplate(indicators);
    if (auto) template = auto;
  }
  const numFields = ['m.net_profit','m.fitness','m.net_profit_pct','m.dd','m.dd_pct','m.open_dd_pct','m.max_intraday_dd','m.ret_dd','m.annual_pct_return','m.sharpe','m.pf','m.win_pct','m.trades_per_month','m.exit_quality','m.equity_angle','m.exposure','m.recovery_factor','m.z_score','m.sqn','m.r_exp','m.std_dev','m.payout_ratio','m.avg_bars_in_trade'];
  const intFields = ['m.trades','m.wins','m.losses','m.max_consec_wins','m.max_consec_losses','m.longest_trade_days','m.complexity','m.stagnation_days'];
  const metrics = {};
  Object.entries(SQX_COLUMN_MAP).forEach(([col, target]) => {
    if (!target.startsWith('m.')) return;
    const key = target.slice(2);
    const raw = row[col];
    if (raw == null || raw === '') return;
    if (intFields.includes(target))      { const n = parseInt(raw,10);   if (!isNaN(n)) metrics[key] = n; }
    else if (numFields.includes(target)) { const n = parseFloat(raw);    if (!isNaN(n)) metrics[key] = n; }
    else metrics[key] = raw;
  });
  let asset = (row['Symbol'] || '').replace(/_darwinex$/i,'').replace(/_[a-z]+$/i,'').toUpperCase() || 'XAUUSD';
  let tf = (row['TimeFrame'] || '').toUpperCase() || 'H1';
  const noteParts = [];
  if (meta.phase) noteParts.push('Fase: '+meta.phase);
  if (meta.notes) noteParts.push(meta.notes);
  return {
    id: id,
    name: indicators ? indicators.split(',').slice(0,3).join(' + ') : 'Sin nombre',
    mining: meta.mining,
    asset: asset,
    tf: tf,
    blocksetting: meta.bs,
    template: template,
    direction: meta.dir,
    indicators: indicators,
    exits: '— (no en CSV)',
    metrics: metrics,
    tier: meta.tier,
    status: meta.status,
    tests_passed: [],
    tests_failed: [],
    notes: noteParts.join(' · '),
    added: new Date().toISOString().slice(0,10),
    _imported: true,
    _import_id: 'imp_' + Date.now() + '_' + id
  };
}

function commitImport() {
  const meta = readImportMeta();
  const newOnes = Array.from(csvImport.selected).map(i => rowToStrategy(csvImport.rows[i], meta));
  const dedupe = SQX_STRATEGIES.dedupeImportedStrategies
    ? SQX_STRATEGIES.dedupeImportedStrategies(STRATEGIES, STRATEGIES_USER, newOnes)
    : { fresh: newOnes, duplicates: 0 };
  const fresh = dedupe.fresh;
  const dups = dedupe.duplicates;
  STRATEGIES_USER = [...STRATEGIES_USER, ...fresh];
  saveStrategiesUser();
  closeImportModal();
  renderStrategies();
  renderPipelineState();
  alert('Importadas: '+fresh.length + (dups ? ' (omitidas '+dups+' duplicadas)' : ''));
}

// override de getAllStrategies y refactor de filtros
function getAllStrategies() {
  if (SQX_STRATEGIES.getAllStrategies) {
    return SQX_STRATEGIES.getAllStrategies(STRATEGIES, STRATEGIES_USER, STRATEGIES_DELETED);
  }
  const deleted = new Set(STRATEGIES_DELETED);
  return [
    ...STRATEGIES.filter(s => !deleted.has(strategyKey(s))),
    ...STRATEGIES_USER
  ];
}

// ── consolidate (todo el array a JSON compatible con config/strategies.json) ──
function consolidateStrategiesJSON() {
  const all = getAllStrategies();
  const wrapper = SQX_STRATEGIES.consolidateJson
    ? SQX_STRATEGIES.consolidateJson(all)
    : JSON.stringify({ version: 1, strategies: all }, null, 2);
  const w = window.open('', '_blank', 'width=900,height=700');
  if (w) {
    const html = SQX_STRATEGIES.consolidatedPopupHtml
      ? SQX_STRATEGIES.consolidatedPopupHtml(wrapper, all.length)
      : '<pre>'+wrapper.replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]))+'</pre>';
    w.document.write(html);
    w.document.close();
  } else {
    navigator.clipboard.writeText(wrapper);
    alert('Popup bloqueado. He copiado el JSON al portapapeles ('+all.length+' estrategias).');
  }
}

// ── listeners CSV import ──
document.getElementById('strat-import-btn').addEventListener('click', openImportModal);
document.getElementById('strat-import-close').addEventListener('click', closeImportModal);
document.getElementById('strat-import-backdrop').addEventListener('click', function(e){ if (e.target === this) closeImportModal(); });
document.getElementById('csv-cancel-btn').addEventListener('click', closeImportModal);
document.getElementById('csv-back-btn').addEventListener('click', function(){ if (csvImport.step > 1) showStep(csvImport.step - 1); });
document.getElementById('csv-next-btn').addEventListener('click', function(){ if (csvImport.step < 4) showStep(csvImport.step + 1); });
document.getElementById('csv-finish-btn').addEventListener('click', commitImport);

const dz = document.getElementById('csv-dropzone');
dz.addEventListener('click', function(){ document.getElementById('strat-import-file').click(); });
dz.addEventListener('dragover', function(e){ e.preventDefault(); dz.classList.add('drag-over'); });
dz.addEventListener('dragleave', function(){ dz.classList.remove('drag-over'); });
dz.addEventListener('drop', function(e){
  e.preventDefault(); dz.classList.remove('drag-over');
  const f = e.dataTransfer.files[0]; if (f) readCsvFile(f);
});
document.getElementById('strat-import-file').addEventListener('change', function(e){
  const f = e.target.files[0]; if (f) readCsvFile(f);
});

document.getElementById('csv-filter-input').addEventListener('input', function(e){
  csvImport.filter = e.target.value; renderCsvPreview();
});
document.getElementById('csv-select-all').addEventListener('click', function(){
  getCsvFilteredRows().forEach(r => csvImport.selected.add(r._idx));
  renderCsvPreview(); document.getElementById('csv-next-btn').disabled = false;
});
document.getElementById('csv-select-none').addEventListener('click', function(){
  getCsvFilteredRows().forEach(r => csvImport.selected.delete(r._idx));
  renderCsvPreview(); document.getElementById('csv-next-btn').disabled = csvImport.selected.size === 0;
});
document.getElementById('csv-select-top10').addEventListener('click', function(){
  const sorted = [...csvImport.rows].map((r,i)=>({_idx:i, np: parseFloat(r['Net profit'])||0}))
    .sort((a,b)=>b.np-a.np).slice(0,10);
  csvImport.selected = new Set(sorted.map(s=>s._idx));
  renderCsvPreview(); document.getElementById('csv-next-btn').disabled = false;
});

document.getElementById('strat-consolidate-btn').addEventListener('click', consolidateStrategiesJSON);
document.getElementById('strat-clear-user-btn').addEventListener('click', function(){
  if (!STRATEGIES_USER.length) return;
  if (confirm('¿Borrar las '+STRATEGIES_USER.length+' estrategias importadas? Las estrategias base se mantienen.')) {
    STRATEGIES_USER = []; saveStrategiesUser(); renderStrategies(); renderPipelineState(); renderHome();
  }
});
document.getElementById('strat-restore-hidden-btn').addEventListener('click', function(){
  if (!STRATEGIES_DELETED.length) return;
  if (confirm('¿Restaurar las '+STRATEGIES_DELETED.length+' estrategias base eliminadas de la vista?')) {
    STRATEGIES_DELETED = []; saveStrategiesDeleted(); renderStrategies(); renderPipelineState(); renderHome();
  }
});

// INIT


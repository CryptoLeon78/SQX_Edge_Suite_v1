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
const SQX_RUNTIME_CONFIG = window.SQX_CONFIG || { ui:{}, storageKeys:{}, value:function(_path, fallback){ return fallback; } };
const SQX_UI_CONFIG = SQX_RUNTIME_CONFIG.ui || {};
const SQX_STORAGE_KEYS = SQX_RUNTIME_CONFIG.storageKeys || {};

function sqxConfigValue(path, fallback) {
  return SQX_RUNTIME_CONFIG.value ? SQX_RUNTIME_CONFIG.value(path, fallback) : fallback;
}

function sqxStatusMeta(status) {
  const statuses = SQX_UI_CONFIG.statuses || [];
  return statuses.find(s => s.id === status) || { id: status, label: status };
}

function sqxStatusSequence() {
  const statuses = SQX_UI_CONFIG.statuses || [];
  return statuses.length ? statuses.map(s => s.id) : ['pending', 'current', 'completed'];
}

// ============================================================
// SCORE
// ============================================================
function calcScore(asset, dirFilter) {
  let total = 0, count = 0;
  for (const [, val] of Object.entries(asset.cats)) {
    if (dirFilter === 'L' && val.dir === 'S') continue;
    if (dirFilter === 'S' && val.dir === 'L') continue;
    total += RATING_ORDER[val.rating] ?? 0;
    count++;
  }
  return { raw: total, count, norm: count ? Math.round((total / (count * 3)) * 100) : 0 };
}

// ============================================================
// HELPERS
// ============================================================
function rLabel(r) {
  if (r==='++') return { text:'Estrella', cls:'rating-pp' };
  if (r==='+')  return { text:'Bueno',    cls:'rating-p'  };
  if (r==='~')  return { text:'Precauc.', cls:'rating-t'  };
  return { text:'No recom.', cls:'rating-m' };
}
function hmCls(r) {
  if (r==='++') return 'hm-pp'; if (r==='+') return 'hm-p';
  if (r==='~')  return 'hm-t';  if (r==='-') return 'hm-m';
  return '';
}
function dirCls(d) {
  return d==='L' ? 'dir-long' : d==='S' ? 'dir-short' : 'dir-both';
}

// SQX Config: A = Both + Entry Symmetry, B = Both sin symmetry, C = Only Long, D = Only Short
function getSqxConfig(asset) {
  const keys = Object.keys(asset.cats);
  let hasL=false, hasS=false, hasLS=false, hasPair=false;
  for (const k of keys) {
    const v = asset.cats[k];
    if (v.dir === 'L/S') hasLS = true;
    else if (v.dir === 'L') hasL = true;
    else if (v.dir === 'S') hasS = true;
    if (k.endsWith('_S')) hasPair = true;
  }
  // A: forex sim (todas L/S, sin pares _S)
  if (hasLS && !hasPair && !hasL && !hasS) {
    return { code:'A', label:'Both + Entry Sym', desc:'Both (Long & Short) con Entry Symmetry ON. Reglas espejadas L/S — ideal para forex simétrico.' };
  }
  // B: tiene pares _S (reglas distintas L vs S)
  if (hasPair) {
    return { code:'B', label:'Both sin Symmetry', desc:'Both (Long & Short) con Symmetry OFF. SQX optimiza L y S por separado — necesario cuando las reglas Long ≠ Short (índices, oro).' };
  }
  // C: solo Long
  if (hasL && !hasS) {
    return { code:'C', label:'Only Long', desc:'Only Long. Solo se buscan estrategias en lado Long.' };
  }
  // D: solo Short
  if (hasS && !hasL) {
    return { code:'D', label:'Only Short', desc:'Only Short. Solo se buscan estrategias en lado Short.' };
  }
  // mixto raro (L y S sin pares _S → tratar como B)
  return { code:'B', label:'Both sin Symmetry', desc:'Both (Long & Short) con Symmetry OFF. SQX optimiza L y S por separado.' };
}
function sqxBadge(asset, mini=false) {
  const c = getSqxConfig(asset);
  const cls = mini ? `sqx-mini sqx-${c.code}` : `sqx-badge sqx-${c.code}`;
  const title = `Config SQX ${c.code}: ${c.desc}`;
  if (mini) return `<span class="${cls}" title="${title}">SQX ${c.code}</span>`;
  return `<span class="${cls}" title="${title}"><span class="sqx-letter">${c.code}</span><span>SQX · ${c.label}</span></span>`;
}

// Replica visual del panel "Trading directions settings" de SQX según el código de config (A/B/C/D)
function sqxPreviewHTML(code) {
  const isLong  = code === 'C';
  const isShort = code === 'D';
  const isBoth  = code === 'A' || code === 'B';
  const entrySymOn = code === 'A';
  const symDisabled = isLong || isShort;
  return ''
    + '<div class="sqx-preview">'
    +   '<div class="sqx-preview-header">Trading directions settings</div>'
    +   '<div class="sqx-preview-body">'
    +     '<div class="sqx-preview-title">Strategy directions</div>'
    +     '<div class="sqx-preview-row">'
    +       '<div class="sqx-radios">'
    +         '<div class="sqx-radio'+(isBoth?' active':'')+'"><span class="sqx-radio-dot"></span>Both (Long and Short)</div>'
    +         '<div class="sqx-radio'+(isLong?' active':'')+'"><span class="sqx-radio-dot"></span>Only Long</div>'
    +         '<div class="sqx-radio'+(isShort?' active':'')+'"><span class="sqx-radio-dot"></span>Only Short</div>'
    +       '</div>'
    +       '<div class="sqx-toggles">'
    +         '<div class="sqx-toggle'+(entrySymOn?' on':'')+(symDisabled?' disabled':'')+'"><span class="sqx-toggle-track"><span class="sqx-toggle-knob"></span></span>Entry Symmetry</div>'
    +         '<div class="sqx-toggle'+(symDisabled?' disabled':'')+'"><span class="sqx-toggle-track"><span class="sqx-toggle-knob"></span></span>Exit Symmetry</div>'
    +       '</div>'
    +     '</div>'
    +   '</div>'
    + '</div>';
}


let HISTORICAL = {};
try {
  if (window.SQX_HISTORICAL_DATA) {
    HISTORICAL = window.SQX_HISTORICAL_DATA;
  } else {
    const _hd = document.getElementById('historical-data');
    const _txt = _hd && _hd.textContent.trim();
    if (_txt && !_txt.startsWith('__')) HISTORICAL = JSON.parse(_txt);
  }
} catch(e) { console.warn('No se pudo parsear historical-data:', e); }

// Data-driven scores (Dukascopy H1 2010-2026)
let SCORES = {};
try {
  if (window.SQX_SCORES_DATA) {
    SCORES = window.SQX_SCORES_DATA;
  } else {
    const _sd = document.getElementById('scores-data');
    const _stxt = _sd && _sd.textContent.trim();
    if (_stxt && !_stxt.startsWith('__')) SCORES = JSON.parse(_stxt);
  }
} catch(e) { console.warn('No se pudo parsear scores-data:', e); }

function getScore(assetId, catKey) {
  const base = catKey.endsWith('_S') ? catKey.slice(0, -2) : catKey;
  const a = SCORES[assetId];
  if (!a || !a[base]) return null;
  const e = a[base];
  return {
    base: base,
    objective: e.objective,
    composite: e.composite_score,
    metrics: (a.metrics && a.metrics[base]) || {},
  };
}

// Sobreescribe los ratings editoriales en ASSETS con los data-driven (Dukascopy H1).
// Tras esto toda la UI (grid, cat-cards, tablas y vistas de prioridad) usa automaticamente
// los ratings objetivos calculados desde datos reales.
function applyObjectiveRatings() {
  if (!SCORES || !Object.keys(SCORES).length) return;
  for (const a of ASSETS) {
    for (const [catKey, entry] of Object.entries(a.cats)) {
      const sc = getScore(a.id, catKey);
      if (sc && sc.objective) {
        entry.rating = sc.objective;
        entry._composite = sc.composite;
        entry._metrics = sc.metrics;
      }
    }
  }
}
applyObjectiveRatings();

function ratingPairBadge(score) {
  if (!score || !score.objective) return '';
  const absDiff = Math.abs(score.diff || 0);
  let cls = '';
  let icon = '';
  if (absDiff >= 2)      { cls = 'discrepancy-major'; icon = ' !!'; }
  else if (absDiff >= 1) { cls = 'discrepancy';       icon = ' !'; }
  const pct = Math.max(0, Math.min(100, Math.round((score.composite || 0) * 100)));
  const metricStr = Object.entries(score.metrics).map(([k,v]) => k+'='+v).join('  ');
  const tip = 'Editorial L='+(score.editorialL||'-')+'  S='+(score.editorialS||'-')+'\nData-driven: '+score.objective+'\nComposite percentile: '+pct+'%\n'+metricStr;
  return '<span class="rating-pair '+cls+'" title="'+tip+'">'
    + '<span class="rp-label">DATA</span>'
    + '<span>'+score.objective+icon+'</span>'
    + '</span>';
}

function compositeBar(score) {
  if (!score || score.composite === null || score.composite === undefined) return '';
  const pct = Math.max(0, Math.min(100, Math.round(score.composite * 100)));
  const color = pct >= 75 ? 'var(--green)' : pct >= 50 ? 'var(--accent)' : pct >= 25 ? 'var(--yellow)' : 'var(--red)';
  return '<div class="composite-bar"><div class="composite-bar-fill" style="width:'+pct+'%;background:'+color+'"></div></div>'
    + '<div class="composite-text">Composite '+pct+'% percentil (Dukascopy H1 2010-2026)</div>';
}

function historyChartSVG(assetId) {
  const data = HISTORICAL[assetId];
  if (!data) return '<div class="history-no-data">Sin histórico disponible para '+assetId+' (no estaba en Darwinex).</div>';

  const chartCfg = sqxConfigValue('chart', {});
  const W=chartCfg.width || 720, H=chartCfg.height || 220;
  const padL=chartCfg.padL || 44, padR=chartCfg.padR || 14, padT=chartCfg.padT || 18, padB=chartCfg.padB || 32;
  const innerW = W-padL-padR, innerH = H-padT-padB;
  const v = data.v, n = v.length;
  const [sy, sm] = data.start.split('-').map(Number);

  const xAt = i => padL + (n>1 ? (i/(n-1))*innerW : innerW/2);
  const minV = Math.min.apply(null, v), maxV = Math.max.apply(null, v);
  const useLog = (maxV/Math.max(minV,0.001)) > 3;
  const tx = useLog ? Math.log : (x=>x);
  const minT = tx(minV), maxT = tx(maxV), rangeT = (maxT-minT) || 1;
  const yAt = val => padT + (1 - (tx(val)-minT)/rangeT) * innerH;

  // 24-month SMA (régimen) — más estable que SMA12
  const SMA_PERIOD = chartCfg.smaPeriod || 24;
  const sma = v.map((_, i) => {
    if (i < SMA_PERIOD-1) return null;
    let s=0; for (let k=i-(SMA_PERIOD-1); k<=i; k++) s += v[k]; return s/SMA_PERIOD;
  });

  // Régimen raw: precio vs SMA24
  const regimeRaw = v.map((_, i) => sma[i] === null ? null : (v[i] > sma[i] ? 1 : -1));

  // Bandas bull/bear con HYSTERESIS — sólo flip si el cambio se sostiene 6+ meses
  // Esto elimina los flips ruidosos cortos y muestra regímenes coherentes
  const MIN_BAND_MONTHS = chartCfg.minBandMonths || 6;
  const bands = [];
  let curStart = -1, curBull = null;
  for (let i=0; i<n; i++) {
    if (regimeRaw[i] === null) continue;
    const isBull = regimeRaw[i] === 1;
    if (curBull === null) { curBull = isBull; curStart = i; continue; }
    if (isBull !== curBull) {
      // Verificar si el cambio se sostiene los próximos MIN_BAND_MONTHS meses
      let sustained = true;
      for (let k=i; k<Math.min(i+MIN_BAND_MONTHS, n); k++) {
        if (regimeRaw[k] !== null && (regimeRaw[k] === 1) !== isBull) { sustained = false; break; }
      }
      if (sustained) {
        bands.push({ start: curStart, end: i-1, bull: curBull });
        curStart = i; curBull = isBull;
      }
    }
  }
  if (curStart !== -1) bands.push({ start: curStart, end: n-1, bull: curBull });

  // Paths
  let path = '', smaPath = '', smaStarted = false;
  for (let i=0; i<n; i++) {
    path += (i===0?'M':'L') + xAt(i).toFixed(1) + ',' + yAt(v[i]).toFixed(1) + ' ';
    if (sma[i] !== null) {
      smaPath += (smaStarted?'L':'M') + xAt(i).toFixed(1) + ',' + yAt(sma[i]).toFixed(1) + ' ';
      smaStarted = true;
    }
  }

  // Year ticks
  const totalMonths = n + (sm-1);
  const ey = sy + Math.floor((totalMonths-1) / 12);
  const span = ey - sy;
  const tickEvery = span >= 16 ? 3 : span >= 10 ? 2 : 1;
  const yearTicks = [];
  for (let yy = Math.ceil(sy/tickEvery)*tickEvery; yy <= ey; yy += tickEvery) {
    const idx = (yy - sy) * 12 - (sm - 1);
    if (idx >= 0 && idx < n) yearTicks.push({ year: yy, idx });
  }

  let svg = '<svg class="history-chart" viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="xMidYMid meet">';
  svg += '<rect x="0" y="0" width="'+W+'" height="'+H+'" fill="#11141d" rx="6"/>';

  // Bandas régimen
  for (const b of bands) {
    const x1 = xAt(b.start), x2 = xAt(b.end);
    const fill = b.bull ? 'rgba(34,197,94,0.18)' : 'rgba(239,68,68,0.18)';
    svg += '<rect x="'+x1.toFixed(1)+'" y="'+padT+'" width="'+(x2-x1).toFixed(1)+'" height="'+innerH+'" fill="'+fill+'"/>';
  }

  // Gridlines horizontales
  const gridVals = [];
  if (useLog) {
    const decades = [50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000];
    for (const d of decades) if (d >= minV*0.9 && d <= maxV*1.1) gridVals.push(d);
  } else {
    const span2 = maxV - minV;
    const step = span2 < 30 ? 5 : span2 < 80 ? 10 : 20;
    for (let g = Math.floor(minV/step)*step; g <= maxV; g += step) {
      if (g >= minV*0.95) gridVals.push(g);
    }
  }
  for (const g of gridVals) {
    const yp = yAt(g);
    svg += '<line x1="'+padL+'" y1="'+yp.toFixed(1)+'" x2="'+(W-padR)+'" y2="'+yp.toFixed(1)+'" stroke="#2e3348" stroke-width="0.5" stroke-dasharray="2,3"/>';
    svg += '<text x="'+(padL-6)+'" y="'+(yp+3).toFixed(1)+'" text-anchor="end" font-size="10" fill="#9ca3af">'+g.toFixed(0)+'</text>';
  }
  // Línea base 100
  if (100 >= minV && 100 <= maxV) {
    const y100 = yAt(100);
    svg += '<line x1="'+padL+'" y1="'+y100.toFixed(1)+'" x2="'+(W-padR)+'" y2="'+y100.toFixed(1)+'" stroke="#3b82f6" stroke-width="0.7" stroke-dasharray="3,2" opacity="0.4"/>';
  }

  // Year ticks
  for (const t of yearTicks) {
    const xp = xAt(t.idx);
    svg += '<line x1="'+xp.toFixed(1)+'" y1="'+padT+'" x2="'+xp.toFixed(1)+'" y2="'+(H-padB+2)+'" stroke="#2e3348" stroke-width="0.5"/>';
    svg += '<text x="'+xp.toFixed(1)+'" y="'+(H-padB+15)+'" text-anchor="middle" font-size="10" fill="#9ca3af">'+t.year+'</text>';
  }

  // Eventos macro
  for (const ev of MACRO_EVENTS) {
    const parts = ev.date.split('-').map(Number);
    const idx = (parts[0]-sy)*12 + (parts[1]-sm);
    if (idx < 0 || idx >= n) continue;
    const xp = xAt(idx);
    svg += '<line x1="'+xp.toFixed(1)+'" y1="'+padT+'" x2="'+xp.toFixed(1)+'" y2="'+(H-padB)+'" stroke="'+ev.color+'" stroke-width="1.2" stroke-dasharray="3,2" opacity="0.7"><title>'+ev.label+' ('+ev.date+')</title></line>';
    svg += '<circle cx="'+xp.toFixed(1)+'" cy="'+(padT-2)+'" r="3.2" fill="'+ev.color+'"><title>'+ev.label+' ('+ev.date+')</title></circle>';
  }

  // SMA12
  svg += '<path d="'+smaPath+'" fill="none" stroke="#9ca3af" stroke-width="1" stroke-dasharray="3,2" opacity="0.55"/>';
  // Curva principal
  svg += '<path d="'+path+'" fill="none" stroke="#3b82f6" stroke-width="1.7"/>';

  // Stat top-right
  const last = v[n-1], first = v[0];
  const totalChange = ((last/first - 1) * 100);
  const tcStr = (totalChange>=0?'+':'') + totalChange.toFixed(1) + '%';
  const tcColor = totalChange >= 0 ? '#22c55e' : '#ef4444';
  svg += '<text x="'+(W-padR)+'" y="'+(padT-4)+'" text-anchor="end" font-size="11" fill="'+tcColor+'" font-weight="700">'+tcStr+' ('+data.start+' → hoy)</text>';

  svg += '</svg>';
  return svg;
}

function historySection(assetId) {
  if (!HISTORICAL[assetId]) {
    if (Object.keys(HISTORICAL).length === 0) return ''; // datos no inyectados aún, no mostrar
    return '<div class="history-section"><div class="history-title">📈 Histórico real</div>'
      + '<div class="history-no-data">Sin datos para '+assetId+' (no disponible en Darwinex).</div></div>';
  }
  return '<div class="history-section">'
    + '<div class="history-title">📈 Histórico real mensual base 100 — Darwinex MT5 · línea gris = SMA24 (régimen, mín 6 meses)</div>'
    + historyChartSVG(assetId)
    + '<div class="history-events-legend">'
    + MACRO_EVENTS.map(e => '<span><i style="background:'+e.color+'"></i>'+e.label+' ('+e.date+')</span>').join('')
    + '<span style="margin-left:auto"><i style="background:rgba(34,197,94,.5)"></i>Sobre SMA24 = bull (sostenido ≥6m)</span>'
    + '<span><i style="background:rgba(239,68,68,.5)"></i>Bajo SMA24 = bear (sostenido ≥6m)</span>'
    + '</div></div>';
}

function renderSqxLegend() {
  const codes = ['A','B','C','D'];
  document.getElementById('sqx-legend-grid').innerHTML = codes.map(code => {
    const meta = SQX_CONFIG_DESC[code];
    return ''
      + '<div class="sqx-config-card">'
      +   '<div class="sqx-config-card-head">'
      +     '<span class="sqx-badge sqx-'+code+'"><span class="sqx-letter">'+code+'</span><span>'+meta.label+'</span></span>'
      +   '</div>'
      +   sqxPreviewHTML(code)
      +   '<div class="sqx-config-desc">'+meta.desc+'</div>'
      + '</div>';
  }).join('');
}
function tfMatch(tf, filter) {
  return filter==='all' || tf.includes(filter);
}
function thH(label, col, ctx, key) {
  const s = sortState.cat[key] || {};
  const cls = s.col===col ? (s.dir==='asc'?'sort-asc':'sort-desc') : '';
  return `<th class="sortable ${cls}" onclick="doSort('${ctx}','${key}','${col}')">${label}<span class="sort-icon"></span></th>`;
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
  if (!col||!dir) return rows;
  return [...rows].sort((a,b)=>{
    let va,vb;
    if (col==='asset')  { va=a.asset?.id||''; vb=b.asset?.id||''; }
    else if (col==='sub')    { va=a.asset?.sub||''; vb=b.asset?.sub||''; }
    else if (col==='dir')    { va=a.dir||''; vb=b.dir||''; }
    else if (col==='tf')     { va=a.tf||''; vb=b.tf||''; }
    else if (col==='rating') { va=RATING_ORDER[a.rating]??-1; vb=RATING_ORDER[b.rating]??-1; }
    else { va=''; vb=''; }
    if (typeof va==='number') return dir==='asc'?va-vb:vb-va;
    return dir==='asc'?va.localeCompare(vb):vb.localeCompare(va);
  });
}
function sparkHTML(asset) {
  return '<div class="sparkline">' + CAT_KEYS.map(ck => {
    const e = asset.cats[ck];
    if (!e) return `<div class="sparkline-seg" style="background:#1e2233"></div>`;
    const alpha = e.rating==='++' ? 1 : e.rating==='+' ? 0.7 : e.rating==='~' ? 0.4 : 0.2;
    return `<div class="sparkline-seg" style="background:${CAT_META[ck].color};opacity:${alpha}" title="${CAT_META[ck].name}: ${e.rating}"></div>`;
  }).join('') + '</div>';
}

// ============================================================
// RENDER: ASSET GRID
// ============================================================
// Filtro SQX:
//   A / B → match contra la config primaria recomendada (getSqxConfig)
//   C     → activos con ≥1 categoría dir:'L' (ideas Long puras — índices/oro)
//   D     → activos con ≥1 categoría dir:'S' (ideas Short puras — índices/oro)
function assetMatchesSqxFilter(a, code) {
  if (code === 'all') return true;
  if (code === 'A' || code === 'B') return getSqxConfig(a).code === code;
  if (code === 'C') return Object.values(a.cats).some(v => v.dir === 'L');
  if (code === 'D') return Object.values(a.cats).some(v => v.dir === 'S');
  return true;
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
    const planBadge = planRef ? '<span class="ps-pin-badge" title="Mining '+planRef.num+' del plan operativo (Pipeline State)">📌 M'+planRef.num+'</span>' : '';
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
  if (tier === '1')   return 'tier-1';
  if (tier === '1.5') return 'tier-15';
  if (tier === '2')   return 'tier-2';
  return 'tier-tentativa';
}
function tierLabel(tier) {
  if (tier === '1')   return 'TIER 1';
  if (tier === '1.5') return 'TIER 1.5';
  if (tier === '2')   return 'TIER 2';
  return 'TENTATIVA';
}
function dirClass(d) {
  if (d === 'L')   return 'dir-L';
  if (d === 'S')   return 'dir-S';
  return 'dir-LS';
}
function metricClass(label, val) {
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
  if (v == null || v === '') return '—';
  if (typeof v !== 'number') v = parseFloat(v);
  if (isNaN(v)) return '—';
  return v.toLocaleString('en-US', { minimumFractionDigits:dec, maximumFractionDigits:dec });
}
function fmtInt(v) {
  if (v == null || v === '') return '—';
  return parseInt(v,10).toLocaleString('en-US');
}

function getFilteredStrategies() {
  return getAllStrategies().filter(s => {
    if (stratFilterMining   !== 'all' && String(s.mining)   !== stratFilterMining)   return false;
    if (stratFilterTemplate !== 'all' && s.template !== stratFilterTemplate) return false;
    if (stratFilterTier     !== 'all' && s.tier     !== stratFilterTier)     return false;
    if (stratFilterStatus   !== 'all' && s.status   !== stratFilterStatus)   return false;
    return true;
  });
}

function renderStratSummary() {
  const all = getAllStrategies();
  const t1  = all.filter(s => s.tier === '1').length;
  const t15 = all.filter(s => s.tier === '1.5').length;
  const t2  = all.filter(s => s.tier === '2').length;
  const tt  = all.filter(s => s.tier === 'tentativa').length;
  const deployed = all.filter(s => s.status === 'DEPLOYED').length;
  const totalProfit = all.reduce((acc,s) => acc + ((s.metrics && s.metrics.net_profit) || 0), 0);

  document.getElementById('strat-summary').innerHTML =
    '<div class="strat-summary-card"><div class="ss-count">' + all.length + '</div><div class="ss-label">Total</div></div>' +
    '<div class="strat-summary-card t1"><div class="ss-count">' + t1 + '</div><div class="ss-label">TIER 1</div></div>' +
    '<div class="strat-summary-card t15"><div class="ss-count">' + t15 + '</div><div class="ss-label">TIER 1.5</div></div>' +
    '<div class="strat-summary-card t2"><div class="ss-count">' + t2 + '</div><div class="ss-label">TIER 2</div></div>' +
    '<div class="strat-summary-card tt"><div class="ss-count">' + tt + '</div><div class="ss-label">Tentativas</div></div>' +
    '<div class="strat-summary-card"><div class="ss-count">' + deployed + '</div><div class="ss-label">Deployed</div></div>' +
    '<div class="strat-summary-card"><div class="ss-count" style="font-size:18px;">$' + fmtInt(Math.round(totalProfit)) + '</div><div class="ss-label">Σ Net Profit (BT)</div></div>';
}

function populateStratFilters() {
  const all = getAllStrategies();
  const minings   = [...new Set(all.map(s => s.mining))].sort((a,b)=>a-b);
  const templates = [...new Set(all.map(s => s.template))].sort();

  const mSel = document.getElementById('strat-filter-mining');
  mSel.innerHTML = '<option value="all">Todos</option>' + minings.map(m =>
    '<option value="'+m+'">Mining ' + m + '</option>'
  ).join('');

  const tSel = document.getElementById('strat-filter-template');
  tSel.innerHTML = '<option value="all">Todos</option>' + templates.map(t =>
    '<option value="'+t+'">' + t + '</option>'
  ).join('');
}

function renderStrategyCard(s) {
  const m = s.metrics || {};
  const dirCls = dirClass(s.direction);
  const dirTxt = s.direction === 'L' ? 'LONG' : s.direction === 'S' ? 'SHORT' : 'L+S';

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

  const testsOk = (s.tests_passed||[]).map(t => '<span class="sc-test-ok">✓ '+t+'</span>').join('');
  const testsKo = (s.tests_failed||[]).map(t => '<span class="sc-test-ko">✗ '+t+'</span>').join('');

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
    '<div class="sc-footer"><span class="sc-date">📅 ' + (s.added || '—') + '</span></div>' +
  '</div>';
}

function renderStrategies() {
  populateStratFilters();
  renderStratSummary();
  // banner de importadas
  const userInfo = document.getElementById('strat-user-info');
  if (userInfo) {
    const cnt = STRATEGIES_USER.length;
    userInfo.style.display = cnt > 0 ? 'block' : 'none';
    const cntEl = document.getElementById('strat-user-count');
    if (cntEl) cntEl.textContent = cnt;
  }
  const list = getFilteredStrategies();
  const grid = document.getElementById('strat-grid');
  if (!list.length) {
    grid.innerHTML = '<div class="no-data" style="grid-column:1/-1;">Sin estrategias que coincidan con los filtros.</div>';
    return;
  }
  // sort: tier 1 → 1.5 → 2 → tentativa, dentro mismo tier por net_profit desc
  const tierRank = { '1':0, '1.5':1, '2':2, 'tentativa':3 };
  list.sort((a,b) => {
    const ta = tierRank[a.tier] ?? 99, tb = tierRank[b.tier] ?? 99;
    if (ta !== tb) return ta - tb;
    return (b.metrics.net_profit||0) - (a.metrics.net_profit||0);
  });
  grid.innerHTML = list.map(renderStrategyCard).join('');
}

function exportStrategiesCSV() {
  const headers = ['ID','Name','Mining','Asset','TF','Blocksetting','Template','Direction','Tier','Status','NetProfit','PF','Sharpe','RetDD','DDpct','Trades','WinPct','RExp','SQN','StagnationDays','TestsPassed','TestsFailed','Indicators','Exits','Notes','Added','Source'];
  const rows = getAllStrategies().map(s => {
    const m = s.metrics || {};
    return [
      s.id, s.name, s.mining, s.asset, s.tf, s.blocksetting, s.template, s.direction, s.tier, s.status,
      m.net_profit ?? '', m.pf ?? '', m.sharpe ?? '', m.ret_dd ?? '', m.dd_pct ?? '',
      m.trades ?? '', m.win_pct ?? '', m.r_exp ?? '', m.sqn ?? '', m.stagnation_days ?? '',
      (s.tests_passed||[]).join('|'), (s.tests_failed||[]).join('|'),
      (s.indicators||'').replace(/[\r\n]+/g,' '), (s.exits||'').replace(/[\r\n]+/g,' '),
      (s.notes||'').replace(/[\r\n]+/g,' '), s.added || '',
      s._imported ? 'IMPORTED' : 'DEFAULT'
    ].map(v => '"' + String(v).replace(/"/g,'""') + '"').join(';');
  });
  doExport([headers.map(h=>'"'+h+'"').join(';'), ...rows], 'SQX_estrategias.csv');
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
function generateStratJSON() {
  const obj = {
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
  // métricas - solo incluir las rellenadas
  const M = obj.metrics;
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

  const json = JSON.stringify(obj, null, 2);
  document.getElementById('sf-output').textContent = json;
  document.getElementById('sf-output-wrap').style.display = 'block';
}

// ============================================================
// EVENTS
// ============================================================
function renderHome() {
  function setText(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }
  var assetCounts = (ASSETS || []).reduce(function(acc, asset) {
    acc[asset.type] = (acc[asset.type] || 0) + 1;
    return acc;
  }, {});
  var strategyUserCount = Array.isArray(STRATEGIES_USER) ? STRATEGIES_USER.length : 0;
  var marked = Object.keys(PRIORITY_PROGRESS || {}).length;
  var nextAction = (PIPELINE_STATE && PIPELINE_STATE.nextAction) || 'Plan operativo';
  if (nextAction.length > 96) nextAction = nextAction.slice(0, 93).trim() + '...';

  setText('home-assets-count', (ASSETS || []).length);
  setText(
    'home-assets-sub',
    (assetCounts.forex || 0) + ' Forex · ' + (assetCounts.index || 0) + ' Indices · ' + (assetCounts.oro || 0) + ' Oro'
  );
  setText('home-minings-count', (PLAN_MININGS || []).length);
  setText('home-strategies-count', (STRATEGIES || []).length + strategyUserCount);
  setText('home-priority-count', marked);
  setText('home-next-action', nextAction);
}

function activateTabById(id) {
  var tab = document.querySelector('.tab[data-tab="' + id + '"]');
  var panel = document.getElementById('tab-' + id);
  if (!tab || !panel) return;
  document.querySelectorAll('.tab').forEach(function(x) { x.classList.remove('active'); });
  tab.classList.add('active');
  document.querySelectorAll('.tab-content').forEach(function(c) { c.style.display = 'none'; });
  panel.style.display = 'block';
}

document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{
  activateTabById(t.dataset.tab);
}));

document.querySelectorAll('[data-home-tab]').forEach(function(btn) {
  btn.addEventListener('click', function() {
    activateTabById(btn.dataset.homeTab);
  });
});

function bindBtns(sel, dataKey, varSetter, cb) {
  document.querySelectorAll(sel).forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll(sel).forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    varSetter(b.dataset[dataKey]);
    cb();
  }));
}
function bindChange(id, cb) {
  const el = document.getElementById(id);
  if (el) el.addEventListener('change', cb);
}
function bindClick(id, cb) {
  const el = document.getElementById(id);
  if (el) el.addEventListener('click', cb);
}
bindBtns('[data-filter-type]', 'filterType', function(v){ filterType = v; }, renderAssetGrid);
bindBtns('[data-filter-sqx]',  'filterSqx',  function(v){ filterSqx  = v; }, renderAssetGrid);
bindBtns('[data-filter-dir]',  'filterDir',  function(v){ filterDir  = v; }, renderCategoriesView);
bindBtns('[data-priority-min]','priorityMin',function(v){ filterPriorityMin = parseInt(v,10) || 0; }, renderPriority);
bindBtns('[data-priority-type]','priorityType',function(v){ filterPriorityType = v; }, renderPriority);

document.getElementById('search-asset').addEventListener('input',renderAssetGrid);
document.getElementById('asset-sort').addEventListener('change',function(e){ assetSort=e.target.value; renderAssetGrid(); });
document.getElementById('cat-filter-rating').addEventListener('change',function(e){ filterCatRating=e.target.value; renderCategoriesView(); });
document.getElementById('cat-filter-sub').addEventListener('change',function(e){ filterCatSub=e.target.value; renderCategoriesView(); });
document.getElementById('cat-filter-tf').addEventListener('change',function(e){ filterCatTf=e.target.value; renderCategoriesView(); });
document.getElementById('export-cat-btn').addEventListener('click',exportCatCSV);
document.getElementById('priority-cat-filter').addEventListener('change',function(e){ filterPriorityCat=e.target.value; renderPriority(); });

// Global helper for inline onclick navigation to asset tab
window.navToAsset = function(id) {
  var tab = document.querySelector('.tab[data-tab="activos"]');
  if (tab) tab.click();
  selectAsset(id);
};

// ── SQX PRIORITY: tracking persistente en localStorage ──
const PRIORITY_STATE_KEY = SQX_STORAGE_KEYS.priorityProgress || 'sqx_priority_progress_v1';
let PRIORITY_PROGRESS = {};
try { PRIORITY_PROGRESS = JSON.parse(localStorage.getItem(PRIORITY_STATE_KEY) || '{}'); } catch(e){ PRIORITY_PROGRESS = {}; }
function savePriorityProgress() { localStorage.setItem(PRIORITY_STATE_KEY, JSON.stringify(PRIORITY_PROGRESS)); }

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
  // Sync con Pipeline State (re-renderiza si la fila importada cambió de estado allí)
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
    btn.textContent = '✓ Copiado';
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
// PIPELINE STATE — plan configurado + embudo + KPIs
// ============================================================

// ── Plan USER (añadidos por UI, persistente en localStorage) ──
const PLAN_USER_KEY = SQX_STORAGE_KEYS.planUser || 'sqx_plan_user_v1';
let PLAN_USER = { minings:[], phases:{} };
try {
  const stored = JSON.parse(localStorage.getItem(PLAN_USER_KEY) || '{}');
  PLAN_USER = { minings: stored.minings || [], phases: stored.phases || {} };
} catch(e){ /* keep defaults */ }
function savePlanUser() { localStorage.setItem(PLAN_USER_KEY, JSON.stringify(PLAN_USER)); }

function getPlanMinings() {
  // Combina DEFAULT + USER, ordena por num
  const all = [
    ...PLAN_MININGS,
    ...PLAN_USER.minings.map(m => ({...m, _user:true}))
  ];
  return all.sort((a,b) => a.num - b.num);
}
function getPlanPhases() {
  // Combina PHASE_META + USER phases
  return Object.assign({}, PHASE_META, PLAN_USER.phases);
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
  // Validación mínima
  if (!m.asset || !m.tf || !m.bs || !m.dir || !m.phase) return false;
  // Dedupe por (num)
  if (getPlanMinings().some(x => x.num === m.num)) return false;
  PLAN_USER.minings.push({ num:m.num, phase:m.phase, asset:m.asset, tf:m.tf, bs:m.bs, dir:m.dir });
  savePlanUser();
  return true;
}
function addPhaseUser(num, name, desc) {
  if (!num || !name) return false;
  if (getPlanPhases()[num]) return false; // ya existe
  PLAN_USER.phases[num] = { name: name, desc: desc || '' };
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
  PLAN_USER = { minings:[], phases:{} };
  savePlanUser();
}
// Alias visible para el helper de status (lee PLAN_ALL si existe)
window.PLAN_ALL = null;
function refreshPlanAll() { window.PLAN_ALL = getPlanMinings(); }
refreshPlanAll();

// Mapping inverso BS → categoría Priority (para sync con SQX Priority)

// Convierte un mining → key del SQX Priority (formato 'asset|cat|tf|dir')
function miningToPriorityKey(mining) {
  const cat = BS_TO_PRIORITY_CAT[mining.bs];
  if (!cat) return null;
  return mining.asset + '|' + cat + '|' + mining.tf + '|' + mining.dir;
}

// localStorage state — pipeline tracking
// Estructura: { overrides: { num: 'current'|... }, funnels: {...}, nextAction:'' }
// `overrides` solo guarda los manuales; el estado por defecto se deriva de SQX Priority
const PIPELINE_STATE_KEY = SQX_STORAGE_KEYS.pipelineState || 'sqx_pipeline_state_v1';
let PIPELINE_STATE = { overrides:{}, funnels:{}, nextAction:'' };
try {
  const stored = JSON.parse(localStorage.getItem(PIPELINE_STATE_KEY) || '{}');
  // Migración del formato antiguo (miningStatus → overrides) + limpieza del preset fantasma
  let overrides = stored.overrides || stored.miningStatus || {};
  // Si solo hay UN override y es el preset Mining 1 = 'current' (preset antiguo), limpiarlo
  // — así el auto-sync con SQX Priority funciona desde el primer momento
  if (!stored.overrides && stored.miningStatus &&
      Object.keys(stored.miningStatus).length === 1 &&
      stored.miningStatus[1] === 'current') {
    overrides = {};
  }
  PIPELINE_STATE = { overrides:overrides, funnels:stored.funnels || {}, nextAction:stored.nextAction || '' };
  // Persistir migración limpia para que no se vuelva a aplicar
  localStorage.setItem(PIPELINE_STATE_KEY, JSON.stringify(PIPELINE_STATE));
} catch(e){ /* keep defaults */ }
// pre-load funnel Mining 1 LINEAR si no hay
if (!PIPELINE_STATE.funnels['1|LINEAR']) PIPELINE_STATE.funnels['1|LINEAR'] = {...FUNNEL_PRELOAD['1|LINEAR']};
if (!PIPELINE_STATE.nextAction) PIPELINE_STATE.nextAction = sqxConfigValue('pipeline.defaultNextAction', 'Filter-by-correlation entre las estrategias PASSED del WFM.');

function savePipelineState() { localStorage.setItem(PIPELINE_STATE_KEY, JSON.stringify(PIPELINE_STATE)); }

// Devuelve { status, source } donde source ∈ {'manual','priority','strategies','default'}
function getMiningStatusInfo(num) {
  // 1) Override manual en Pipeline State
  if (PIPELINE_STATE.overrides[num]) {
    return { status: PIPELINE_STATE.overrides[num], source: 'manual' };
  }
  // 2) Estado del SQX Priority (source of truth por defecto)
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

function renderPsKpis() {
  const allMinings = getPlanMinings();
  const total = allMinings.length;
  const completed = allMinings.filter(m => getMiningStatus(m.num) === 'completed').length;
  const current   = allMinings.filter(m => getMiningStatus(m.num) === 'current').length;
  const pending   = total - completed - current;
  const pctDone   = Math.round((completed/total)*100);

  const all = getAllStrategies();
  const survivors = all.filter(s => s.tier==='1' || s.tier==='1.5' || s.tier==='2').length;
  const tier1     = all.filter(s => s.tier==='1').length;
  const deployed  = all.filter(s => s.status==='DEPLOYED').length;
  const tentativas= all.filter(s => s.tier==='tentativa').length;
  const portfolioGoal = 10; // mid del rango 8-12

  document.getElementById('ps-kpis').innerHTML =
    '<div class="ps-kpi k-progress">' +
      '<div class="ps-k-label">Plan minings</div>' +
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

function renderPsPlan() {
  refreshPlanAll();
  const allMinings = getPlanMinings();
  const allPhases = getPlanPhases();
  const phases = getPlanPhaseNums().filter(p => allMinings.some(m => m.phase === p));
  const html = phases.map(p => {
    const meta = allPhases[p] || { name:'(sin nombre)', desc:'' };
    const isUserPhase = !!PLAN_USER.phases[p];
    const minings = allMinings.filter(m => m.phase === p);
    const done = minings.filter(m => getMiningStatus(m.num)==='completed').length;
    const pct = minings.length ? Math.round(done/minings.length*100) : 0;
    const rows = minings.map(m => {
      const info = getMiningStatusInfo(m.num);
      const st = info.status;
      const stLbl = sqxStatusMeta(st).label;
      // Badge de fuente del estado
      let srcBadge = '';
      if (info.source === 'manual') {
        srcBadge = '<span class="ps-src-badge ps-src-manual" title="Override manual — click ↻ para volver a auto-sync con Priority" onclick="event.stopPropagation();clearMiningOverride('+m.num+')">✏ Manual ↻</span>';
      } else if (info.source === 'priority') {
        srcBadge = '<span class="ps-src-badge ps-src-priority" title="Sincronizado desde SQX Priority">🔗 Priority</span>';
      } else if (info.source === 'strategies') {
        srcBadge = '<span class="ps-src-badge ps-src-strategies" title="Auto-detectado: hay estrategias importadas de este mining">📦 Auto</span>';
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
        '<span class="ps-m-survivors" title="' + survivors + ' supervivientes (TIER 1/1.5/2)">' + survivors + ' ✓</span>' :
        '<span class="ps-m-survivors zero">0 ✓</span>';
      const tentBadge = tentativas > 0 ? ' <span class="ps-m-survivors zero" style="background:rgba(249,115,22,.12);color:var(--orange);">' + tentativas + ' ?</span>' : '';
      const tplsHtml = tpls.length ? '<div style="font-size:10px;color:var(--text2);margin-top:3px;">Templates: '+tpls.join(', ')+'</div>' : '';
      const userBadge = m._user ? '<span class="ps-user-badge" title="Añadido por UI (vive en localStorage)">USER</span>' : '';
      const removeBtn = m._user ? '<button class="ps-remove-btn" title="Eliminar este mining USER" onclick="removeUserMiningClick('+m.num+')">✕</button>' : '';
      return '<tr>' +
        '<td class="ps-m-num">'+m.num+userBadge+'</td>' +
        '<td><div class="ps-m-asset">'+m.asset+'</div>'+tplsHtml+'</td>' +
        '<td class="ps-m-tf">'+m.tf+'</td>' +
        '<td><span class="ps-m-bs">'+m.bs+'</span></td>' +
        '<td><span class="'+dirCls+'" style="font-weight:700;font-size:12px;">'+m.dir+'</span></td>' +
        '<td>'+compHtml+'</td>' +
        '<td>'+survBadge+tentBadge+'</td>' +
        '<td><span class="status '+st+' clickable-status" onclick="cycleMiningStatusPS('+m.num+')">'+stLbl+'</span> '+srcBadge+removeBtn+'</td>' +
      '</tr>';
    }).join('');
    const phaseCls = p > 5 ? 'p1' : 'p'+p; // las USER reusan estilo p1
    const phaseUserBadge = isUserPhase ? '<span class="ps-user-badge" title="Fase USER (localStorage)">USER</span>' : '';
    const phaseRemove = isUserPhase ? '<button class="ps-remove-btn" title="Eliminar fase USER" onclick="removeUserPhaseClick('+p+')">✕</button>' : '';
    return '<div class="ps-phase">' +
      '<div class="ps-phase-head '+phaseCls+'">' +
        '<div class="ps-phase-num">'+p+'</div>' +
        '<h3>FASE '+p+' — '+meta.name+phaseUserBadge+'</h3>' +
        '<span style="color:var(--text2);font-size:12px;">'+meta.desc+'</span>' +
        '<span class="ps-phase-count">'+done+'/'+minings.length+'</span>' +
        '<div class="ps-phase-bar"><div style="width:'+pct+'%"></div></div>' +
        phaseRemove +
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
  const miningsWithStrats = [...new Set(getAllStrategies().map(s => s.mining))].sort((a,b)=>a-b);
  const miningsAll = miningsWithStrats.length ? miningsWithStrats : [1];
  const curM = parseInt(selM.value,10) || miningsAll[0];
  selM.innerHTML = miningsAll.map(m => '<option value="'+m+'">Mining '+m+'</option>').join('');
  selM.value = miningsAll.includes(curM) ? curM : miningsAll[0];
  // template selector
  const tpls = getTemplatesByMining(parseInt(selM.value,10));
  const tplsAll = tpls.length ? tpls : ['LINEAR'];
  const curT = selT.value || tplsAll[0];
  selT.innerHTML = tplsAll.map(t => '<option value="'+t+'">'+t+'</option>').join('');
  selT.value = tplsAll.includes(curT) ? curT : tplsAll[0];
}

function renderPsFunnel() {
  const key = getCurrentFunnelKey();
  const data = getFunnelData(key);
  const initial = data[FUNNEL_STAGES_DEFAULT[0].id] || 0;
  const html = FUNNEL_STAGES_DEFAULT.map(stage => {
    const v = data[stage.id];
    const valStr = v == null ? '—' : v;
    const pct = (initial > 0 && typeof v === 'number') ? Math.max(2, Math.round(v/initial*100)) : 0;
    const surv = (initial > 0 && typeof v === 'number') ? (v/initial*100).toFixed(2) + '%' : '';
    const cls = stage.terminal ? 'ps-funnel-step terminal ps-funnel-final' : 'ps-funnel-step';
    return '<div class="'+cls+'">' +
      '<div class="pf-name">'+stage.name+'</div>' +
      '<div class="pf-bar-wrap"><div class="pf-bar" style="width:'+pct+'%"></div></div>' +
      '<div class="pf-count" data-stage="'+stage.id+'" onclick="editFunnelCell(this, \''+key+'\', \''+stage.id+'\')">'+valStr+'</div>' +
      '<div class="pf-survival">'+surv+'</div>' +
    '</div>';
  }).join('');
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
    renderPsFunnel();
  }
  inp.addEventListener('blur', commit);
  inp.addEventListener('keydown', function(e){
    if (e.key === 'Enter') { e.preventDefault(); commit(); }
    if (e.key === 'Escape') { el.classList.remove('editing'); renderPsFunnel(); }
  });
};

// ── Orphans: items current/completed en SQX Priority sin match en el plan ──
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
  const orphans = getOrphanPriorityItems();
  const card = document.getElementById('ps-orphans-card');
  const list = document.getElementById('ps-orphans-list');
  if (!card || !list) return;
  if (!orphans.length) { card.style.display = 'none'; return; }
  card.style.display = 'block';
  const meta = (typeof CAT_META !== 'undefined') ? CAT_META : {};
  list.innerHTML = orphans.map(o => {
    const catName = (meta[o.cat] && meta[o.cat].name) || o.cat;
    const dirCls = o.dir==='L'?'dir-l':(o.dir==='S'?'dir-s':'dir-ls');
    const dirTxt = o.dir==='L'?'LONG':(o.dir==='S'?'SHORT':'L+S');
    const compHtml = o.composite != null ? '<span class="po-comp">'+o.composite+'%</span>' : '';
    const stLbl = sqxStatusMeta(o.status).label;
    const legacyBadge = o.isLegacy ? '<span class="po-legacy" title="Key del Priority en formato antiguo (TFs juntos). Se ha hecho split visual; al «Quitar» se elimina la key entera.">⚠ Legacy</span>' : '';
    const safeOrig = o.origKey.replace(/\\/g,'\\\\').replace(/'/g,"\\'");
    const safeNew  = o.key.replace(/\\/g,'\\\\').replace(/'/g,"\\'");
    return '<div class="ps-orphan-row">' +
      '<span class="po-asset">'+o.asset+'</span>' +
      '<span class="po-cat">'+catName+'</span>' +
      '<span class="po-tf">'+o.tf+'</span>' +
      '<span class="'+dirCls+' po-dir">'+dirTxt+'</span>' +
      '<span class="po-bs">'+o.bs+'</span>' +
      compHtml +
      '<span class="po-status '+o.status+'">'+stLbl+'</span>' +
      legacyBadge +
      '<button class="po-add-btn" onclick="promoteOrphanToPlan(\''+safeNew+'\')">+ Añadir al plan</button>' +
      '<button class="po-remove-btn" title="Eliminar este item del SQX Priority (no afecta el plan)" onclick="removeOrphanFromPriority(\''+safeOrig+'\','+(o.isLegacy?'true':'false')+')">✕ Quitar</button>' +
    '</div>';
  }).join('');
}

window.removeOrphanFromPriority = function(origKey, isLegacy) {
  if (typeof PRIORITY_PROGRESS === 'undefined') return;
  if (!PRIORITY_PROGRESS[origKey]) { renderPipelineState(); return; }
  const msg = isLegacy
    ? '¿Eliminar la key legacy "'+origKey+'" del SQX Priority? (Contiene varios TFs juntos — se borran todos.)'
    : '¿Eliminar este item del SQX Priority?';
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
  renderPsNextAction();
  renderOrphans();
  renderPsPlan();
  populateFunnelSelectors();
  renderPsFunnel();
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
    const userCount = PLAN_USER.minings.length + Object.keys(PLAN_USER.phases).length;
    userInfo.style.display = userCount > 0 ? 'block' : 'none';
    const cnt = document.getElementById('ps-plan-user-count');
    if (cnt) cnt.textContent = userCount;
  }
}

// listeners
document.getElementById('ps-funnel-mining').addEventListener('change', function(){
  populateFunnelSelectors();
  renderPsFunnel();
});
document.getElementById('ps-funnel-template').addEventListener('change', renderPsFunnel);

document.getElementById('ps-na-edit').addEventListener('click', function(){
  const v = prompt('Próxima acción inmediata:', PIPELINE_STATE.nextAction || '');
  if (v != null) { PIPELINE_STATE.nextAction = v.trim(); savePipelineState(); renderPsNextAction(); }
});

document.getElementById('ps-plan-reset').addEventListener('click', function(){
  if (confirm('¿Resetear COMPLETAMENTE el tracking? Borra overrides manuales y deja solo el auto-sync con SQX Priority. (No afecta estrategias ni embudos.)')) {
    PIPELINE_STATE.overrides = {};
    savePipelineState();
    renderPipelineState();
  }
});

document.getElementById('ps-restore-auto').addEventListener('click', function(){
  const n = Object.keys(PIPELINE_STATE.overrides || {}).length;
  if (!n) return;
  if (confirm('¿Limpiar los '+n+' override(s) manual(es) y volver al auto-sync con SQX Priority?')) {
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
  sel.innerHTML = phases.map(p => '<option value="'+p+'">FASE '+p+' — '+(meta[p]?.name || '')+'</option>').join('');
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
  const n = PLAN_USER.minings.length + Object.keys(PLAN_USER.phases).length;
  if (!n) return;
  if (confirm('¿Borrar los '+n+' añadidos USER del plan? Los DEFAULT se mantienen.')) {
    clearPlanUser(); renderPipelineState();
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
    w.document.write('<h1>💾 Consolidado: '+all.length+' minings · '+Object.keys(phases).length+' fases</h1>');
    w.document.write('<p>JSON compatible con <code>backend/sqx-edge-tool/config/plan.json</code>.</p>');
    w.document.write('<button onclick="navigator.clipboard.writeText(document.getElementById(\'cn\').textContent).then(()=>this.textContent=\'✓ Copiado\')">📋 Copiar al portapapeles</button>');
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
let STRATEGIES_USER = [];
try { STRATEGIES_USER = JSON.parse(localStorage.getItem(STRAT_USER_KEY) || '[]'); } catch(e){ STRATEGIES_USER = []; }
function saveStrategiesUser() { localStorage.setItem(STRAT_USER_KEY, JSON.stringify(STRATEGIES_USER)); }

const SQX_COLUMN_MAP = sqxConfigValue('csvImport.columnMap', {});

function autoDetectTemplate(indicators) {
  if (!indicators) return null;
  const ind = indicators.toUpperCase();
  const rules = sqxConfigValue('csvImport.templateKeywords', []);
  for (const rule of rules) {
    if ((rule.keywords || []).some(keyword => ind.includes(keyword))) return rule.template;
  }
  return null;
}

// Parser CSV simple — separador configurable, soporte comillas con escape ""
function parseCSV(text, sep) {
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
  const cols = ['Strategy Name','Net profit','Profit factor','Sharpe Ratio','Ret/DD Ratio','Max DD %','# of trades','Winning Percent','SQN Score','R Expectancy','Stagnation','Entry indicators'];
  const head = '<thead><tr><th style="width:30px;"><input type="checkbox" id="csv-th-check"></th>' +
    cols.map(c => {
      const isNum = c !== 'Strategy Name' && c !== 'Entry indicators';
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
      const num = parseFloat(v);
      let cls = '';
      if (!isNaN(num)) {
        if (c === 'Profit factor')   cls = num >= 1.5 ? 'pos' : num >= 1.2 ? 'warn' : 'neg';
        if (c === 'Sharpe Ratio')    cls = num >= 1.3 ? 'pos' : num >= 1.0 ? 'warn' : 'neg';
        if (c === 'Ret/DD Ratio')    cls = num >= 5   ? 'pos' : num >= 3   ? 'warn' : 'neg';
        if (c === 'Max DD %')        cls = num <  2   ? 'pos' : num <  5   ? 'warn' : 'neg';
        if (c === 'R Expectancy')    cls = num >= 0.30? 'pos' : num >= 0.15? 'warn' : 'neg';
        if (c === 'SQN Score')       cls = num >= 1.6 ? 'pos' : num >= 1.0 ? 'warn' : 'neg';
        if (c === 'Stagnation')      cls = num <  180 ? 'pos' : num <  365 ? 'warn' : 'neg';
        if (c === 'Net profit')      cls = num > 0    ? 'pos' : 'neg';
      }
      return '<td class="cv-num '+cls+'">'+v+'</td>';
    }).join('');
    return '<tr><td><input type="checkbox" class="cv-row-check" data-idx="'+idx+'" '+checked+'></td>' + cells + '<td><span class="cv-tpl">'+tpl+'</span></td></tr>';
  }).join('') + '</tbody>';
  const t = document.getElementById('csv-preview-table');
  t.innerHTML = head + body;
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
  const sel = csvImport.selected.size;
  const sample = Array.from(csvImport.selected).slice(0,5).map(i => 'Strategy ' + (csvImport.rows[i]['Strategy Name']||'').replace(/^Strategy /,'')).join(', ');
  document.getElementById('csv-confirm-summary').innerHTML =
    '<div><strong>'+sel+'</strong> estrategia(s) se importarán.</div>' +
    '<div style="margin-top:6px;">Mining <strong>'+meta.mining+'</strong> · '+meta.bs+' · Template default <strong>'+(meta.template||'(auto-detect)')+'</strong> · Dirección <strong>'+meta.dir+'</strong> · TIER <strong>'+meta.tier+'</strong> · Status <strong>'+meta.status+'</strong></div>' +
    (sample ? '<div style="margin-top:6px; font-size:12px; color:var(--text2);">Primeras: '+sample+(sel>5?'…':'')+'</div>' : '');
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
  // dedupe contra existentes (mismo id + mining + template)
  const existingKeys = new Set([...STRATEGIES, ...STRATEGIES_USER].map(s => s.id+'|'+s.mining+'|'+s.template));
  const fresh = newOnes.filter(s => !existingKeys.has(s.id+'|'+s.mining+'|'+s.template));
  const dups = newOnes.length - fresh.length;
  STRATEGIES_USER = [...STRATEGIES_USER, ...fresh];
  saveStrategiesUser();
  closeImportModal();
  renderStrategies();
  renderPipelineState();
  alert('✓ Importadas: '+fresh.length + (dups ? ' (omitidas '+dups+' duplicadas)' : ''));
}

// override de getAllStrategies y refactor de filtros
function getAllStrategies() {
  return [...STRATEGIES, ...STRATEGIES_USER];
}

// ── consolidate (todo el array a JSON compatible con config/strategies.json) ──
function consolidateStrategiesJSON() {
  const all = getAllStrategies().map(s => {
    const c = JSON.parse(JSON.stringify(s));
    delete c._imported; delete c._import_id;
    return c;
  });
  const wrapper = JSON.stringify({ version: 1, strategies: all }, null, 2);
  // muestra en un modal simple usando el sf-output-wrap si está cerrado, si no en alert
  const w = window.open('', '_blank', 'width=900,height=700');
  if (w) {
    w.document.write('<html><head><title>SQX Strategies — Consolidado</title><style>body{background:#0f1117;color:#e4e4e7;font-family:Segoe UI,sans-serif;padding:20px;}h1{font-size:16px;margin-bottom:10px;}p{color:#9ca3af;font-size:12px;margin-bottom:14px;}pre{background:#0a0c12;border:1px solid #2e3348;border-radius:8px;padding:14px;font-family:Consolas,monospace;font-size:12px;color:#9eb1d3;line-height:1.5;overflow:auto;max-height:80vh;white-space:pre-wrap;}button{margin-bottom:10px;padding:8px 16px;background:#22c55e;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:700;}</style></head><body>');
    w.document.write('<h1>💾 Consolidado: '+all.length+' estrategias</h1>');
    w.document.write('<p>JSON compatible con <code>backend/sqx-edge-tool/config/strategies.json</code>.</p>');
    w.document.write('<button onclick="navigator.clipboard.writeText(document.getElementById(\'cn\').textContent).then(()=>this.textContent=\'✓ Copiado\')">📋 Copiar al portapapeles</button>');
    w.document.write('<pre id="cn">'+wrapper.replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]))+'</pre>');
    w.document.write('</body></html>');
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
  if (confirm('¿Borrar las '+STRATEGIES_USER.length+' estrategias importadas? Las del HTML se mantienen.')) {
    STRATEGIES_USER = []; saveStrategiesUser(); renderStrategies(); renderPipelineState();
  }
});

// INIT


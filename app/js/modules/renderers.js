(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  function sqxBadge(config, mini) {
    var cls = mini ? 'sqx-mini sqx-' + config.code : 'sqx-badge sqx-' + config.code;
    var title = 'Config SQX ' + config.code + ': ' + config.desc;
    if (mini) return '<span class="' + cls + '" title="' + title + '">SQX ' + config.code + '</span>';
    return '<span class="' + cls + '" title="' + title + '"><span class="sqx-letter">' + config.code + '</span><span>SQX · ' + config.label + '</span></span>';
  }

  function sqxPreviewHTML(code) {
    var isLong = code === 'C';
    var isShort = code === 'D';
    var isBoth = code === 'A' || code === 'B';
    var entrySymOn = code === 'A';
    var symDisabled = isLong || isShort;
    return ''
      + '<div class="sqx-preview">'
      +   '<div class="sqx-preview-header">Trading directions settings</div>'
      +   '<div class="sqx-preview-body">'
      +     '<div class="sqx-preview-title">Strategy directions</div>'
      +     '<div class="sqx-preview-row">'
      +       '<div class="sqx-radios">'
      +         '<div class="sqx-radio' + (isBoth ? ' active' : '') + '"><span class="sqx-radio-dot"></span>Both (Long and Short)</div>'
      +         '<div class="sqx-radio' + (isLong ? ' active' : '') + '"><span class="sqx-radio-dot"></span>Only Long</div>'
      +         '<div class="sqx-radio' + (isShort ? ' active' : '') + '"><span class="sqx-radio-dot"></span>Only Short</div>'
      +       '</div>'
      +       '<div class="sqx-toggles">'
      +         '<div class="sqx-toggle' + (entrySymOn ? ' on' : '') + (symDisabled ? ' disabled' : '') + '"><span class="sqx-toggle-track"><span class="sqx-toggle-knob"></span></span>Entry Symmetry</div>'
      +         '<div class="sqx-toggle' + (symDisabled ? ' disabled' : '') + '"><span class="sqx-toggle-track"><span class="sqx-toggle-knob"></span></span>Exit Symmetry</div>'
      +       '</div>'
      +     '</div>'
      +   '</div>'
      + '</div>';
  }

  function ratingPairBadge(score) {
    if (!score || !score.objective) return '';
    var absDiff = Math.abs(score.diff || 0);
    var cls = '';
    var icon = '';
    if (absDiff >= 2) { cls = 'discrepancy-major'; icon = ' !!'; }
    else if (absDiff >= 1) { cls = 'discrepancy'; icon = ' !'; }
    var pct = Math.max(0, Math.min(100, Math.round((score.composite || 0) * 100)));
    var metricStr = Object.entries(score.metrics).map(function(entry) { return entry[0] + '=' + entry[1]; }).join('  ');
    var tip = 'Editorial L=' + (score.editorialL || '-') + '  S=' + (score.editorialS || '-') + '\nData-driven: ' + score.objective + '\nComposite percentile: ' + pct + '%\n' + metricStr;
    return '<span class="rating-pair ' + cls + '" title="' + tip + '">'
      + '<span class="rp-label">DATA</span>'
      + '<span>' + score.objective + icon + '</span>'
      + '</span>';
  }

  function compositeBar(score) {
    if (!score || score.composite === null || score.composite === undefined) return '';
    var pct = Math.max(0, Math.min(100, Math.round(score.composite * 100)));
    var color = pct >= 75 ? 'var(--green)' : pct >= 50 ? 'var(--accent)' : pct >= 25 ? 'var(--yellow)' : 'var(--red)';
    return '<div class="composite-bar"><div class="composite-bar-fill" style="width:' + pct + '%;background:' + color + '"></div></div>'
      + '<div class="composite-text">Composite ' + pct + '% percentil (Dukascopy H1 2010-2026)</div>';
  }

  function historySection(assetId, historical, chartHtml, macroEvents) {
    var history = historical || {};
    if (!history[assetId]) {
      if (Object.keys(history).length === 0) return '';
      return '<div class="history-section"><div class="history-title">Histórico real</div>'
        + '<div class="history-no-data">Sin datos para ' + assetId + ' (no disponible en Darwinex).</div></div>';
    }

    return '<div class="history-section">'
      + '<div class="history-title">Histórico real mensual base 100 — Darwinex MT5 · línea gris = SMA24 (régimen, mín 6 meses)</div>'
      + chartHtml
      + '<div class="history-events-legend">'
      + (macroEvents || []).map(function(event) {
        return '<span><i style="background:' + event.color + '"></i>' + event.label + ' (' + event.date + ')</span>';
      }).join('')
      + '<span style="margin-left:auto"><i style="background:rgba(34,197,94,.5)"></i>Sobre SMA24 = bull (sostenido ≥6m)</span>'
      + '<span><i style="background:rgba(239,68,68,.5)"></i>Bajo SMA24 = bear (sostenido ≥6m)</span>'
      + '</div></div>';
  }

  function sqxLegend(codes, configDesc, previewFn) {
    return (codes || []).map(function(code) {
      var meta = configDesc[code];
      return ''
        + '<div class="sqx-config-card">'
        +   '<div class="sqx-config-card-head">'
        +     '<span class="sqx-badge sqx-' + code + '"><span class="sqx-letter">' + code + '</span><span>' + meta.label + '</span></span>'
        +   '</div>'
        +   previewFn(code)
        +   '<div class="sqx-config-desc">' + meta.desc + '</div>'
        + '</div>';
    }).join('');
  }

  function sortableHeader(label, col, ctx, key, state) {
    var s = state || {};
    var cls = s.col === col ? (s.dir === 'asc' ? 'sort-asc' : 'sort-desc') : '';
    return '<th class="sortable ' + cls + '" onclick="doSort(\'' + ctx + '\',\'' + key + '\',\'' + col + '\')">' + label + '<span class="sort-icon"></span></th>';
  }

  function sparkHTML(asset, catKeys, catMeta) {
    return '<div class="sparkline">' + (catKeys || []).map(function(catKey) {
      var entry = asset.cats[catKey];
      if (!entry) return '<div class="sparkline-seg" style="background:#1e2233"></div>';
      var alpha = entry.rating === '++' ? 1 : entry.rating === '+' ? 0.7 : entry.rating === '~' ? 0.4 : 0.2;
      return '<div class="sparkline-seg" style="background:' + catMeta[catKey].color + ';opacity:' + alpha + '" title="' + catMeta[catKey].name + ': ' + entry.rating + '"></div>';
    }).join('') + '</div>';
  }

  SQX.renderers = SQX.renderers || {
    compositeBar: compositeBar,
    historySection: historySection,
    ratingPairBadge: ratingPairBadge,
    sortableHeader: sortableHeader,
    sparkHTML: sparkHTML,
    sqxBadge: sqxBadge,
    sqxLegend: sqxLegend,
    sqxPreviewHTML: sqxPreviewHTML
  };

  if (SQX.registerModule) {
    SQX.registerModule('renderers', SQX.renderers);
  }
})(window);

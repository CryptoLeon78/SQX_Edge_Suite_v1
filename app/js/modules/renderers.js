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

  SQX.renderers = SQX.renderers || {
    compositeBar: compositeBar,
    ratingPairBadge: ratingPairBadge,
    sqxBadge: sqxBadge,
    sqxPreviewHTML: sqxPreviewHTML
  };

  if (SQX.registerModule) {
    SQX.registerModule('renderers', SQX.renderers);
  }
})(window);

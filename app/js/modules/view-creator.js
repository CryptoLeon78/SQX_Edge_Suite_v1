(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var ui = SQX.ui || {};
  var config = SQX.config || {};
  var raw = config.raw || global.SQX_CONFIG || {};
  var storageKeys = raw.storageKeys || {};
  var presetsStorageKey = storageKeys.viewCreatorPresets || 'sqx_view_creator_presets_v1';

  var CATEGORY_LABELS = {
    fixed: 'Identificacion / contexto',
    core: 'Core EGT / Regimen',
    advanced: 'Avanzadas cuantitativas',
    trades: 'Trades / Win-Loss',
    drawdown: 'Drawdown',
    returns: 'Return / Profit',
    risk: 'Risk',
    activity: 'Activity / Exposure',
    extra: 'Symmetry / Edge',
    counts: 'Contadores'
  };

  var METRICS = [
    ['Symbol', 'Symbol', false, true, 'fixed'],
    ['TimeFrame', 'TimeFrame', false, true, 'fixed'],
    ['Mini equity chart', 'MiniEquityChart', false, true, 'fixed'],
    ['Fitness', 'Fitness', false, true, 'fixed'],
    ['Entry indicators', 'EntryIndicators', false, false, 'fixed'],
    ['Exit indicators', 'ExitIndicators', false, false, 'fixed'],
    ['Complexity', 'Complexity', false, false, 'fixed'],
    ['Note', 'Note', false, false, 'fixed'],
    ['Parameters', 'Parameters', false, false, 'fixed'],
    ['Magic number', 'MagicNumber', false, false, 'fixed'],
    ['Template', 'TemplateColumn', false, false, 'fixed'],
    ['CAGR/Max DD %', 'AnnualPctReturnDDRatio', true, true, 'core'],
    ['Net profit', 'NetProfit', true, true, 'core'],
    ['# of trades', 'NumberOfTrades', true, true, 'core'],
    ['Profit factor', 'ProfitFactor', true, true, 'core'],
    ['Max DD %', 'DrawdownPct', true, true, 'core'],
    ['Sharpe Ratio', 'SharpeRatio', true, true, 'core'],
    ['Sortino Ratio', 'SortinoRatio', true, true, 'advanced'],
    ['Calmar Ratio', 'CalmarRatio', true, true, 'advanced'],
    ['Sterling Ratio', 'SterlingRatio', true, false, 'advanced'],
    ['SQN', 'SQN', true, false, 'advanced'],
    ['SQN Score', 'SQNScore', true, false, 'advanced'],
    ['R Expectancy', 'RExpectancy', true, false, 'advanced'],
    ['R Expectancy Score', 'RExpectancyScore', true, false, 'advanced'],
    ['Ulcer Index %', 'UlcerIndex', true, false, 'advanced'],
    ['Ulcer Performance Index', 'UlcerPerformanceIndex', true, false, 'advanced'],
    ['Strategy Quality Score', 'StrategyQualityScore', true, false, 'advanced'],
    ['Recovery Factor', 'RecoveryFactor', true, false, 'advanced'],
    ['Stability', 'Stability', true, false, 'advanced'],
    ['Stability SQ3', 'StabilitySQ3', true, false, 'advanced'],
    ['Profitable Months', 'ProfitableMonths', true, false, 'advanced'],
    ['% Profitable Months', 'ProfitableMonthsPct', true, true, 'advanced'],
    ['Worst Year Profit', 'WorstYearProfit', true, true, 'advanced'],
    ['Stagnation', 'Stagnation', true, false, 'advanced'],
    ['% Stagnation', 'StagnationPct', true, false, 'advanced'],
    ['Avg. Trade', 'AvgTrade', true, false, 'trades'],
    ['Avg. Win', 'AvgWin', true, false, 'trades'],
    ['Avg. Loss', 'AvgLoss', true, false, 'trades'],
    ['Win/Loss ratio', 'WinLossRatio', true, false, 'trades'],
    ['Winning Percent', 'WinningPct', true, false, 'trades'],
    ['Payout ratio', 'PayoutRatio', true, false, 'trades'],
    ['Expectancy', 'Expectancy', true, false, 'trades'],
    ['Kelly formula', 'KellyFormula', true, false, 'trades'],
    ['Avg. Bars in Trade', 'AvgBarsInTrade', true, false, 'trades'],
    ['Avg. Bars Win', 'AvgBarsWin', true, false, 'trades'],
    ['Avg. Bars Loss', 'AvgBarsLoss', true, false, 'trades'],
    ['Max Consec. Wins', 'MaxConsecWins', true, false, 'trades'],
    ['Max Consec. Losses', 'MaxConsecLosses', true, false, 'trades'],
    ['RR Ratio Median', 'RRRatioMedian', true, false, 'trades'],
    ['Drawdown ($)', 'Drawdown', true, false, 'drawdown'],
    ['Max Drawdown Duration', 'MaxNewHighDuration', true, false, 'drawdown'],
    ['Avg. Drawdown', 'AvgDrawdown', true, false, 'drawdown'],
    ['Avg. % Drawdown', 'AvgPctDrawdown', true, false, 'drawdown'],
    ['Max Intraday Drawdown', 'MaxIntradayDrawdown', true, false, 'drawdown'],
    ['Open Drawdown', 'OpenDrawdown', true, false, 'drawdown'],
    ['Open Drawdown %', 'OpenDrawdownPct', true, false, 'drawdown'],
    ['CAGR', 'CAGR', true, false, 'returns'],
    ['Annual % Return', 'AnnualPctReturn', true, false, 'returns'],
    ['Net profit in %', 'NetProfitInPct', true, false, 'returns'],
    ['Gross profit', 'GrossProfit', true, false, 'returns'],
    ['Gross loss', 'GrossLoss', true, false, 'returns'],
    ['Avg. Profit Per Day', 'AvgProfitPerDay', true, false, 'returns'],
    ['Avg. Profit Per Month', 'AvgProfitPerMonth', true, false, 'returns'],
    ['Avg. % Profit Per Year', 'AvgPctProfitPerYear', true, false, 'returns'],
    ['VaR (95%)', 'VaR_Hobbiecode', true, false, 'risk'],
    ['CVaR (95%)', 'CVaR_Hobbiecode', true, false, 'risk'],
    ['StandardDev', 'StandardDev', true, false, 'risk'],
    ['Z-Score', 'ZScore', true, false, 'risk'],
    ['Z-Probability', 'ZProbability', true, false, 'risk'],
    ['Negative Streaks P80', 'NegativeStreaksPct80', true, false, 'risk'],
    ['Negative Streaks P95', 'NegativeStreaksPct95', true, false, 'risk'],
    ['Exposure', 'Exposure', true, false, 'activity'],
    ['Exposure Position', 'ExposurePosition', true, false, 'activity'],
    ['Exposure Bars %', 'ExposureBarsPercent', true, false, 'activity'],
    ['Avg. Trades Per Day', 'AvgTradesPerDay', true, false, 'activity'],
    ['Avg. Trades Per Month', 'AvgTradesPerMonth', true, false, 'activity'],
    ['Avg. Trades Per Year', 'AvgTradesPerYear', true, false, 'activity'],
    ['Longest trade (days)', 'LongestTrade', true, false, 'activity'],
    ['Symmetry', 'Symmetry', true, false, 'extra'],
    ['Trades Symmetry', 'TradesSymmetry', true, false, 'extra'],
    ['Edge Ratio', 'EdgeRatioInPips', true, false, 'extra'],
    ['Equity Slope', 'EquitySlope', true, false, 'extra'],
    ['EquityAngle', 'EquityAngle', true, false, 'extra'],
    ['AHPR', 'AHPR', true, false, 'extra'],
    ['RINAIndex', 'RINAIndex', true, false, 'extra'],
    ['RSquared', 'RSquared', true, false, 'extra'],
    ['# of profits', 'NumberOfProfits', true, false, 'counts'],
    ['# of canceled', 'NumberOfCanceled', true, false, 'counts']
  ].map(function(row) {
    return {
      display: row[0],
      className: row[1],
      annualDefault: row[2],
      selectedDefault: row[3],
      category: row[4]
    };
  });

  var PRESETS = {
    'egt-core': function(metric) { return metric.selectedDefault; },
    robustness: function(metric) {
      return metric.category === 'fixed' && metric.selectedDefault ||
        ['AnnualPctReturnDDRatio', 'NetProfit', 'NumberOfTrades', 'ProfitFactor', 'DrawdownPct', 'SharpeRatio', 'SortinoRatio', 'CalmarRatio', 'RecoveryFactor', 'Stability', 'ProfitableMonthsPct', 'WorstYearProfit', 'StagnationPct'].indexOf(metric.className) >= 0;
    },
    risk: function(metric) {
      return metric.category === 'fixed' && metric.selectedDefault ||
        ['DrawdownPct', 'Drawdown', 'AvgDrawdown', 'AvgPctDrawdown', 'MaxNewHighDuration', 'UlcerIndex', 'UlcerPerformanceIndex', 'VaR_Hobbiecode', 'CVaR_Hobbiecode', 'StandardDev', 'ZScore', 'ZProbability'].indexOf(metric.className) >= 0;
    },
    'full-audit': function(metric) { return metric.category !== 'fixed' || metric.selectedDefault; },
    clear: function(metric) { return metric.category === 'fixed' && metric.selectedDefault; }
  };
  var metricState = {};
  METRICS.forEach(function(metric) {
    metricState[metric.className] = {
      selected: !!metric.selectedDefault,
      annual: !!(metric.annualDefault && metric.category !== 'fixed')
    };
  });

  function byId(id) {
    return global.document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[<>&"']/g, function(ch) {
      return ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&#39;' })[ch];
    });
  }

  function escapeXml(value) {
    return String(value == null ? '' : value).replace(/[<>&"']/g, function(ch) {
      return ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' })[ch];
    });
  }

  function sanitizeInt(value, fallback, min, max) {
    var parsed = parseInt(value, 10);
    if (isNaN(parsed)) return fallback;
    return Math.max(min, Math.min(max, parsed));
  }

  function hasFullAccess() {
    return !SQX.license || !SQX.license.hasFeature || SQX.license.hasFeature('view_creator.full');
  }

  function metricByClass(className) {
    return METRICS.find(function(metric) { return metric.className === className; });
  }

  function safeJsonParse(rawValue, fallback) {
    try {
      return JSON.parse(rawValue);
    } catch (_err) {
      return fallback;
    }
  }

  function getSavedPresets() {
    var payload = safeJsonParse(global.localStorage.getItem(presetsStorageKey), []);
    return Array.isArray(payload) ? payload.filter(function(item) {
      return item && typeof item === 'object' && item.id && item.name && item.config;
    }) : [];
  }

  function setSavedPresets(presets) {
    global.localStorage.setItem(presetsStorageKey, JSON.stringify((presets || []).slice(0, 30)));
    return getSavedPresets();
  }

  function countColumns(selected, yearCount, includeTotal) {
    var annual = selected.filter(function(metric) { return metric.annual; }).length;
    var fixed = selected.length - annual;
    return fixed + annual * (yearCount + (includeTotal ? 1 : 0));
  }

  function columnSpecs(selected, yearCount, sampleStart, includeTotal, groupMode) {
    var columns = [];
    var annualList = selected.filter(function(metric) { return metric.annual; });
    function add(metric, sampleType) {
      columns.push({
        display: metric.display,
        className: metric.className,
        sampleType: sampleType
      });
    }

    if (groupMode === 'by_metric') {
      selected.forEach(function(metric) {
        if (!metric.annual) {
          add(metric, 127);
          return;
        }
        for (var i = 0; i < yearCount; i += 1) add(metric, sampleStart + i);
        if (includeTotal) add(metric, 127);
      });
      return columns;
    }

    var emittedAnnual = false;
    selected.forEach(function(metric) {
      if (!metric.annual) {
        add(metric, 127);
        return;
      }
      if (emittedAnnual) return;
      for (var year = 0; year < yearCount; year += 1) {
        annualList.forEach(function(annualMetric) { add(annualMetric, sampleStart + year); });
      }
      if (includeTotal) {
        annualList.forEach(function(annualMetric) { add(annualMetric, 127); });
      }
      emittedAnnual = true;
    });
    return columns;
  }

  function columnXml(column) {
    return '    <Column class="' + escapeXml(column.className) +
      '" name="' + escapeXml(column.display) +
      '" sampleType="' + escapeXml(column.sampleType) +
      '" direction="0" plType="10" resultType="main" confidenceLevel="50" market="1" subresult="30" showMainResult="true"/>';
  }

  function buildViewXml(options) {
    var opts = options || {};
    var viewName = String(opts.viewName || 'EGT - Anual').trim() || 'EGT - Anual';
    var selected = opts.selected || [];
    var yearCount = sanitizeInt(opts.yearCount, 9, 1, 30);
    var sampleStart = sanitizeInt(opts.sampleStart, 21, 0, 126);
    var includeTotal = opts.includeTotal !== false;
    var groupMode = opts.groupMode === 'by_metric' ? 'by_metric' : 'by_year';
    var columns = columnSpecs(selected, yearCount, sampleStart, includeTotal, groupMode);
    return [
      '<View name="' + escapeXml(viewName) + '" originalName="' + escapeXml(viewName) + '">',
      '  <Columns>'
    ].concat(columns.map(columnXml), [
      '  </Columns>',
      '</View>'
    ]).join('\n');
  }

  function selectedMetrics() {
    return METRICS.filter(function(metric) {
      var state = metricState[metric.className] || {};
      return !!state.selected;
    }).map(function(metric) {
      var state = metricState[metric.className] || {};
      return {
        display: metric.display,
        className: metric.className,
        category: metric.category,
        annual: metric.category !== 'fixed' && !!state.annual
      };
    });
  }

  function serializeConfig(options) {
    var opts = options || optionsFromDom();
    return {
      viewName: String(opts.viewName || 'EGT - Anual').trim() || 'EGT - Anual',
      yearCount: sanitizeInt(opts.yearCount, 9, 1, 30),
      sampleStart: sanitizeInt(opts.sampleStart, 21, 0, 126),
      includeTotal: opts.includeTotal !== false,
      groupMode: opts.groupMode === 'by_metric' ? 'by_metric' : 'by_year',
      metrics: (opts.selected || []).map(function(metric) {
        return {
          className: metric.className,
          annual: !!metric.annual
        };
      })
    };
  }

  function applyConfig(savedConfig) {
    var cfg = savedConfig || {};
    if (byId('vc-view-name')) byId('vc-view-name').value = cfg.viewName || 'EGT - Anual';
    if (byId('vc-year-count')) byId('vc-year-count').value = sanitizeInt(cfg.yearCount, 9, 1, 30);
    if (byId('vc-sample-start')) byId('vc-sample-start').value = sanitizeInt(cfg.sampleStart, 21, 0, 126);
    if (byId('vc-include-total')) byId('vc-include-total').checked = cfg.includeTotal !== false;
    if (byId('vc-group-mode')) byId('vc-group-mode').value = cfg.groupMode === 'by_metric' ? 'by_metric' : 'by_year';
    if (byId('vc-search')) byId('vc-search').value = '';
    METRICS.forEach(function(metric) {
      setMetric(metric.className, false, metric.annualDefault);
    });
    (cfg.metrics || []).forEach(function(item) {
      var metric = metricByClass(item.className);
      if (metric) setMetric(metric.className, true, item.annual);
    });
    Array.from(global.document.querySelectorAll('[data-vc-preset]')).forEach(function(button) {
      button.classList.remove('active');
    });
    renderMetrics();
    updatePreview();
  }

  function optionsFromDom() {
    return {
      viewName: byId('vc-view-name') ? byId('vc-view-name').value : 'EGT - Anual',
      yearCount: byId('vc-year-count') ? byId('vc-year-count').value : 9,
      sampleStart: byId('vc-sample-start') ? byId('vc-sample-start').value : 21,
      includeTotal: byId('vc-include-total') ? byId('vc-include-total').checked : true,
      groupMode: byId('vc-group-mode') ? byId('vc-group-mode').value : 'by_year',
      selected: selectedMetrics()
    };
  }

  function previewLines(options) {
    var opts = options || {};
    var yearCount = sanitizeInt(opts.yearCount, 9, 1, 30);
    var sampleStart = sanitizeInt(opts.sampleStart, 21, 0, 126);
    var selected = opts.selected || [];
    var columns = columnSpecs(selected, yearCount, sampleStart, opts.includeTotal !== false, opts.groupMode);
    var lines = [
      "Vista: '" + (opts.viewName || 'EGT - Anual') + "'",
      'Samples: ' + sampleStart + '..' + (sampleStart + yearCount - 1) + (opts.includeTotal !== false ? ' + 127 total' : ''),
      'Metricas: ' + selected.length + ' | Columnas: ' + columns.length,
      '------------------------------------------------------------'
    ];
    columns.slice(0, 80).forEach(function(column, index) {
      lines.push(String(index + 1).padStart(3, ' ') + '. ' + column.display + '  s' + column.sampleType + '  [' + column.className + ']');
    });
    if (columns.length > 80) lines.push('... ' + (columns.length - 80) + ' columnas mas');
    return lines;
  }

  function setStatus(text, state) {
    var el = byId('vc-status');
    if (!el) return;
    el.textContent = text || '';
    el.classList.remove('is-ok', 'is-warn', 'is-error');
    if (state) el.classList.add('is-' + state);
  }

  function presetIdFromName(name) {
    return String(name || '')
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 48) || 'preset';
  }

  function renderSavedPresets() {
    var presets = getSavedPresets();
    var select = byId('vc-saved-select');
    var count = byId('vc-saved-count');
    if (count) count.textContent = presets.length + (presets.length === 1 ? ' guardado' : ' guardados');
    if (!select) return presets;
    if (!presets.length) {
      select.innerHTML = '<option value="">Sin presets guardados</option>';
      return presets;
    }
    select.innerHTML = presets.map(function(preset) {
      return '<option value="' + escapeHtml(preset.id) + '">' + escapeHtml(preset.name) + '</option>';
    }).join('');
    return presets;
  }

  function updatePreview() {
    var opts = optionsFromDom();
    var selected = opts.selected || [];
    var yearCount = sanitizeInt(opts.yearCount, 9, 1, 30);
    var sampleStart = sanitizeInt(opts.sampleStart, 21, 0, 126);
    var includeTotal = opts.includeTotal !== false;
    var columnCount = countColumns(selected, yearCount, includeTotal);
    var preview = byId('vc-preview');
    if (preview) preview.textContent = previewLines(opts).join('\n');
    if (byId('vc-selected-count')) byId('vc-selected-count').textContent = String(selected.length);
    if (byId('vc-column-count')) byId('vc-column-count').textContent = String(columnCount);
    if (byId('vc-year-range')) byId('vc-year-range').textContent = sampleStart + '..' + (sampleStart + yearCount - 1);
    if (byId('vc-preview-title')) byId('vc-preview-title').textContent = opts.viewName || 'EGT - Anual';
    if (byId('vc-mode-label')) byId('vc-mode-label').textContent = opts.groupMode === 'by_metric' ? 'Agrupado por metrica' : 'Agrupado por ano';
    setStatus(columnCount + ' columnas preparadas para descargar.', 'ok');
    return opts;
  }

  function groupedMetrics(filterText) {
    var filter = String(filterText || '').toLowerCase().trim();
    return METRICS.filter(function(metric) {
      if (!filter) return true;
      return (metric.display + ' ' + metric.className + ' ' + metric.category).toLowerCase().indexOf(filter) >= 0;
    }).reduce(function(acc, metric) {
      if (!acc[metric.category]) acc[metric.category] = [];
      acc[metric.category].push(metric);
      return acc;
    }, {});
  }

  function metricRow(metric) {
    var state = metricState[metric.className] || {};
    var selected = state.selected ? ' checked' : '';
    var annual = state.annual && metric.category !== 'fixed' ? ' checked' : '';
    var annualControl = metric.category === 'fixed'
      ? '<span class="views-annual-pill total">127</span>'
      : '<label class="views-annual-pill"><input id="vc-annual-' + escapeHtml(metric.className) + '" type="checkbox" data-vc-annual="' + escapeHtml(metric.className) + '"' + annual + '> anual</label>';
    return '<div class="views-metric-row" title="' + escapeHtml(metric.display + ' / ' + metric.className) + '">' +
      '<label class="views-metric-main">' +
        '<input id="vc-metric-' + escapeHtml(metric.className) + '" type="checkbox" data-vc-metric="' + escapeHtml(metric.className) + '"' + selected + '>' +
        '<span><span class="views-metric-name">' + escapeHtml(metric.display) + '</span><span class="views-metric-class">' + escapeHtml(metric.className) + '</span></span>' +
      '</label>' +
      annualControl +
    '</div>';
  }

  function renderMetrics() {
    var list = byId('vc-metric-list');
    if (!list) return;
    var search = byId('vc-search');
    var grouped = groupedMetrics(search ? search.value : '');
    var order = ['fixed', 'core', 'advanced', 'trades', 'drawdown', 'returns', 'risk', 'activity', 'extra', 'counts'];
    list.innerHTML = order.filter(function(category) {
      return grouped[category] && grouped[category].length;
    }).map(function(category) {
      var rows = grouped[category].map(metricRow).join('');
      return '<div class="views-category">' +
        '<div class="views-category-head"><strong>' + escapeHtml(CATEGORY_LABELS[category] || category) + '</strong><small>' + grouped[category].length + ' metricas</small></div>' +
        '<div class="views-metric-grid">' + rows + '</div>' +
      '</div>';
    }).join('');
    bindMetricChanges();
  }

  function setMetric(className, selected, annual) {
    var metric = metricByClass(className);
    metricState[className] = {
      selected: !!selected,
      annual: !!(metric && metric.category !== 'fixed' && annual !== false)
    };
    var selectedEl = byId('vc-metric-' + className);
    var annualEl = byId('vc-annual-' + className);
    if (selectedEl) selectedEl.checked = !!selected;
    if (annualEl && metric && metric.category !== 'fixed') annualEl.checked = annual !== false;
  }

  function applyPreset(name) {
    var hasFull = hasFullAccess();
    var preset = PRESETS[name] || PRESETS['egt-core'];
    if (!hasFull && name !== 'egt-core' && name !== 'clear') {
      setStatus('El catalogo completo requiere SQX Edge Pro.', 'warn');
      name = 'egt-core';
      preset = PRESETS[name];
    }
    METRICS.forEach(function(metric) {
      setMetric(metric.className, preset(metric), metric.annualDefault);
    });
    Array.from(global.document.querySelectorAll('[data-vc-preset]')).forEach(function(button) {
      button.classList.toggle('active', button.dataset.vcPreset === name);
    });
    renderMetrics();
    updatePreview();
  }

  function saveCurrentPreset() {
    var input = byId('vc-preset-name');
    var viewName = byId('vc-view-name') ? byId('vc-view-name').value.trim() : '';
    var name = input && input.value.trim() ? input.value.trim() : (viewName || 'Vista SQX');
    var id = presetIdFromName(name);
    var presets = getSavedPresets().filter(function(preset) { return preset.id !== id; });
    presets.unshift({
      id: id,
      name: name,
      savedAt: new Date().toISOString(),
      config: serializeConfig(optionsFromDom())
    });
    setSavedPresets(presets);
    renderSavedPresets();
    if (byId('vc-saved-select')) byId('vc-saved-select').value = id;
    setStatus('Preset guardado: ' + name, 'ok');
    if (input) input.value = '';
  }

  function selectedSavedPreset() {
    var select = byId('vc-saved-select');
    var id = select ? select.value : '';
    return getSavedPresets().find(function(preset) { return preset.id === id; }) || null;
  }

  function loadSavedPreset() {
    var preset = selectedSavedPreset();
    if (!preset) {
      setStatus('No hay preset guardado seleccionado.', 'warn');
      return;
    }
    applyConfig(preset.config);
    setStatus('Preset cargado: ' + preset.name, 'ok');
  }

  function deleteSavedPreset() {
    var preset = selectedSavedPreset();
    if (!preset) {
      setStatus('No hay preset guardado seleccionado.', 'warn');
      return;
    }
    setSavedPresets(getSavedPresets().filter(function(item) { return item.id !== preset.id; }));
    renderSavedPresets();
    setStatus('Preset eliminado: ' + preset.name, 'ok');
  }

  function downloadView() {
    var opts = updatePreview();
    if (!opts.selected.length) {
      setStatus('Selecciona al menos una metrica.', 'error');
      return;
    }
    var xml = buildViewXml(opts);
    var filename = (String(opts.viewName || 'SQX View').trim() || 'SQX View').replace(/[\\/:*?"<>|]+/g, '_') + '.vw';
    var blob = new Blob([xml], { type: 'application/xml' });
    var url = URL.createObjectURL(blob);
    var link = global.document.createElement('a');
    link.href = url;
    link.download = filename;
    global.document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    setStatus('Vista descargada: ' + filename, 'ok');
    if (global.addHomeTrace) global.addHomeTrace('SQX View Creator', filename + ' generado', 'ok');
  }

  function copyXml() {
    var xml = buildViewXml(updatePreview());
    if (!global.navigator.clipboard) {
      setStatus('Clipboard no disponible en este navegador.', 'warn');
      return;
    }
    global.navigator.clipboard.writeText(xml).then(function() {
      setStatus('XML copiado al portapapeles.', 'ok');
    }).catch(function() {
      setStatus('No se pudo copiar el XML.', 'error');
    });
  }

  function bindMetricChanges() {
    Array.from(global.document.querySelectorAll('[data-vc-metric], [data-vc-annual]')).forEach(function(input) {
      input.addEventListener('change', function() {
        var className = input.dataset.vcMetric || input.dataset.vcAnnual;
        var state = metricState[className] || { selected: false, annual: false };
        if (input.dataset.vcMetric) state.selected = input.checked;
        if (input.dataset.vcAnnual) state.annual = input.checked;
        metricState[className] = state;
        updatePreview();
      });
    });
  }

  function bindControls() {
    ['vc-view-name', 'vc-year-count', 'vc-sample-start', 'vc-group-mode', 'vc-include-total'].forEach(function(id) {
      var el = byId(id);
      if (!el) return;
      el.addEventListener(el.tagName === 'SELECT' || el.type === 'checkbox' ? 'change' : 'input', updatePreview);
    });
    if (byId('vc-search')) byId('vc-search').addEventListener('input', function() {
      renderMetrics();
      updatePreview();
    });
    Array.from(global.document.querySelectorAll('[data-vc-preset]')).forEach(function(button) {
      button.addEventListener('click', function() { applyPreset(button.dataset.vcPreset); });
    });
    if (byId('vc-download-btn')) byId('vc-download-btn').addEventListener('click', downloadView);
    if (byId('vc-copy-btn')) byId('vc-copy-btn').addEventListener('click', copyXml);
    if (byId('vc-save-preset-btn')) byId('vc-save-preset-btn').addEventListener('click', saveCurrentPreset);
    if (byId('vc-load-preset-btn')) byId('vc-load-preset-btn').addEventListener('click', loadSavedPreset);
    if (byId('vc-delete-preset-btn')) byId('vc-delete-preset-btn').addEventListener('click', deleteSavedPreset);
  }

  function init() {
    if (!byId('vc-metric-list')) return;
    renderMetrics();
    bindControls();
    renderSavedPresets();
    var note = byId('vc-license-note');
    if (note) note.textContent = hasFullAccess() ? 'Catalogo completo habilitado.' : 'Free: preset EGT Core. Pro desbloquea presets avanzados.';
    updatePreview();
  }

  SQX.viewCreator = SQX.viewCreator || {
    applyPreset: applyPreset,
    applyConfig: applyConfig,
    buildViewXml: buildViewXml,
    categoryLabels: CATEGORY_LABELS,
    columnSpecs: columnSpecs,
    countColumns: countColumns,
    downloadView: downloadView,
    getSavedPresets: getSavedPresets,
    groupedMetrics: groupedMetrics,
    init: init,
    metrics: METRICS,
    previewLines: previewLines,
    sanitizeInt: sanitizeInt,
    saveCurrentPreset: saveCurrentPreset,
    selectedMetrics: selectedMetrics,
    serializeConfig: serializeConfig,
    setSavedPresets: setSavedPresets,
    storageKey: presetsStorageKey
  };

  if (SQX.registerModule) {
    SQX.registerModule('view-creator', SQX.viewCreator);
  }
})(window);

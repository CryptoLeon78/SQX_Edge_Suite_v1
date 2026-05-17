(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var ui = SQX.ui || {};
  var config = SQX.config || {};
  var raw = config.raw || global.SQX_CONFIG || {};
  var storageKeys = raw.storageKeys || {};
  var presetsStorageKey = storageKeys.viewCreatorPresets || 'sqx_view_creator_presets_v1';
  var PRESET_PACKAGE_TYPE = 'sqx-edge.view-presets';
  var PRESET_PACKAGE_VERSION = 1;
  var TEMPLATE_MAKER_REQUIRED_METRICS = [
    'Net profit',
    '# of trades',
    'Profit factor',
    'Max DD %',
    'Sharpe Ratio',
    'Stability',
    'CAGR/Max DD %',
    'Winning Percent',
    'SQN',
    'Recovery Factor',
    'Calmar Ratio',
    'Sortino Ratio',
    '% Profitable Months'
  ];
  var TEMPLATE_MAKER_CERT_CLASSES = [
    'Symbol',
    'TimeFrame',
    'Fitness',
    'NetProfit',
    'NumberOfTrades',
    'ProfitFactor',
    'DrawdownPct',
    'SharpeRatio',
    'Stability',
    'AnnualPctReturnDDRatio',
    'WinningPct',
    'SQN',
    'RecoveryFactor',
    'CalmarRatio',
    'SortinoRatio',
    'ProfitableMonthsPct'
  ];
  var CVC_DECISION_REQUIRED_METRICS = [
    'Net profit',
    '# of trades',
    'Profit factor',
    'CAGR/Max DD %',
    'Max DD %',
    'Worst Year Profit',
    'Entry indicators',
    'Avg. Bars in Trade',
    'Avg. Trades Per Month'
  ];
  var CVC_DECISION_CERT_CLASSES = [
    'Symbol',
    'TimeFrame',
    'Fitness',
    'EntryIndicators',
    'NetProfit',
    'NumberOfTrades',
    'ProfitFactor',
    'AnnualPctReturnDDRatio',
    'DrawdownPct',
    'WorstYearProfit',
    'AvgBarsInTrade',
    'AvgTradesPerMonth',
    'RecoveryFactor',
    'Stability'
  ];

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
    'template-maker-cert': function(metric) {
      return TEMPLATE_MAKER_CERT_CLASSES.indexOf(metric.className) >= 0;
    },
    'cvc-decision-cert': function(metric) {
      return CVC_DECISION_CERT_CLASSES.indexOf(metric.className) >= 0;
    },
    'full-audit': function(metric) { return metric.category !== 'fixed' || metric.selectedDefault; },
    clear: function(metric) { return metric.category === 'fixed' && metric.selectedDefault; }
  };

  var BUYER_READY_TEMPLATE_DEFINITIONS = [
    {
      id: 'egt-first-review',
      name: 'EGT Core',
      tier: 'free',
      priority: 'obligatoria',
      preset: 'egt-core',
      description: 'View obligatoria para la primera lectura anual del edge, regimen y base de comparacion.',
      objective: 'Primera lectura obligatoria del edge: rentabilidad, volumen de trades y ratio Ret/DD por bloque OOS.',
      when: 'Antes de Mining 1 y en cada revision inicial del databank.',
      nextAction: 'Descarga la .vw, importala en SQX y decide si el edge merece pasar a Robustez.',
      metricTags: ['PF', 'Trades', 'Ret/DD', 'Net Profit'],
      oosTag: '9oos',
      oosOptions: [1, 2, 3, 7, 9],
      config: { viewName: 'EGT Core', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_year' }
    },
    {
      id: 'robustness-pack-screen',
      name: 'Robustez',
      tier: 'pro',
      priority: 'obligatoria',
      preset: 'robustness',
      description: 'View obligatoria para revisar estabilidad, años malos, stagnation y ratios antes de portfolio.',
      objective: 'Control obligatorio de estabilidad: TICK REAL, MC, SPP, WFM, años malos y ratios de supervivencia.',
      when: 'Despues de EGT Core, antes de aceptar una estrategia para portfolio o entrega.',
      nextAction: 'Revisa estabilidad y años malos; si aguanta, pasa a Risk o Full audit segun el caso.',
      metricTags: ['TICK REAL', 'MC', 'SPP', 'WFM'],
      oosTag: '9oos',
      oosOptions: [1, 2, 3, 7, 9],
      config: { viewName: 'Robustez', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_metric' }
    },
    {
      id: 'template-maker-cert',
      name: 'Template Maker Cert',
      tier: 'free',
      priority: 'obligatoria',
      preset: 'template-maker-cert',
      description: 'View obligatoria para exportar el Databank CSV que certifica KPIs en Template Maker.',
      objective: 'Contrato oficial de métricas: Template Maker usa este CSV para certificar Capa 1 y habilitar C2. Ret/DD se deriva desde CAGR/Max DD % si SQX no lo exporta como columna propia.',
      when: 'Antes de certificar estrategias en Template Maker. Primero importa esta .vw en SQX y exporta el Databank CSV.',
      nextAction: 'Exporta el Databank CSV con esta view antes de certificar estrategias en Template Maker.',
      metricTags: ['CSV Cert', 'KPIs C1', 'Ret/DD derivado', 'PASSED', 'C2'],
      oosTag: '9oos',
      oosOptions: [1, 2, 3, 7, 9],
      config: { viewName: 'Template Maker Cert', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_metric' }
    },
    {
      id: 'cvc-decision-cert',
      name: 'CVC Decision Cert',
      tier: 'free',
      priority: 'obligatoria',
      preset: 'cvc-decision-cert',
      description: 'View obligatoria para exportar Champion, Challengers y OOS con las columnas que decide Champion vs Challenger.',
      objective: 'Contrato oficial CVC: direccion, arquetipo, OOS, volatilidad y score final sin depender de columnas ocultas.',
      when: 'Antes de comparar finalistas en Champion vs Challenger.',
      nextAction: 'Exporta Champion, Challengers y OOS con esta view antes de tomar la decision final.',
      metricTags: ['CVC', 'OOS', 'Arquetipo', 'Volatilidad', 'Short'],
      oosTag: '9oos',
      oosOptions: [1, 2, 3, 7, 9],
      config: { viewName: 'CVC Decision Cert', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_metric' }
    },
    {
      id: 'risk-capital-review',
      name: 'Risk',
      tier: 'pro',
      priority: 'recomendable',
      preset: 'risk',
      description: 'View recomendable para drawdown, dispersion, rachas negativas y stress previo a entrega.',
      objective: 'Revision de riesgo operativo: drawdown, VaR/CVaR, Z-Score, dispersion y rachas negativas.',
      when: 'Antes de entregar una estrategia o cuando el riesgo decide si se descarta.',
      nextAction: 'Confirma que el riesgo encaja con el perfil objetivo antes de exportar resultados.',
      metricTags: ['VaR', 'CVaR', 'Z-Score', 'Drawdown'],
      oosTag: '7oos',
      oosOptions: [1, 2, 3, 7, 9],
      config: { viewName: 'Risk', yearCount: 7, sampleStart: 23, includeTotal: true, groupMode: 'by_year' }
    },
    {
      id: 'full-audit-handoff',
      name: 'Full audit',
      tier: 'pro',
      priority: 'recomendable',
      preset: 'full-audit',
      description: 'View recomendable para auditoria completa y CSV posterior cuando una tanda merece investigacion.',
      objective: 'Vista amplia para auditoria final, documentacion de decisiones y CSV completo.',
      when: 'Cuando una tanda ya supero filtros iniciales y merece revision profunda.',
      nextAction: 'Exporta CSV desde SQX con esta view para documentar la decision final.',
      metricTags: ['PF', 'R Exp', 'CAGR/DD', 'Stagnation'],
      oosTag: '9oos',
      oosOptions: [1, 2, 3, 7, 9],
      config: { viewName: 'Full audit', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_metric' }
    }
  ];

  var metricState = {};
  var activeTemplateId = 'egt-first-review';
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

  function syncSavedPresetsToRemote(presets) {
    var remoteState = SQX.remoteState;
    if (!remoteState) return;
    var payload = {};
    payload[presetsStorageKey] = presets || [];
    function save() {
      if (remoteState.saveNow) {
        return remoteState.saveNow(payload, 'sqx-views-presets');
      }
      if (remoteState.queueSave) {
        return remoteState.queueSave(presetsStorageKey, presets || []);
      }
      return Promise.resolve({ ok: false, skipped: true });
    }
    try {
      if (remoteState.bootstrap) {
        remoteState.bootstrap().then(save).catch(function() {});
        return;
      }
      save();
    } catch (_err) {}
  }

  function setSavedPresets(presets) {
    var clean = (presets || []).map(normalizePreset).filter(Boolean).slice(0, 30);
    global.localStorage.setItem(presetsStorageKey, JSON.stringify(clean));
    syncSavedPresetsToRemote(clean);
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

  function hydrateMetricSelection(items) {
    return (items || []).map(function(item) {
      var metric = item && metricByClass(item.className || item);
      if (!metric) return null;
      return {
        display: metric.display,
        className: metric.className,
        category: metric.category,
        annual: metric.category !== 'fixed' && item.annual !== false
      };
    }).filter(Boolean);
  }

  function buildViewXml(options) {
    var opts = options || {};
    var viewName = String(opts.viewName || 'EGT - Anual').trim() || 'EGT - Anual';
    var selected = hydrateMetricSelection(opts.selected || opts.metrics || []);
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

  function normalizeConfig(config) {
    var cfg = config || {};
    var metrics = Array.isArray(cfg.metrics) ? cfg.metrics.map(function(item) {
      var metric = item && metricByClass(item.className);
      if (!metric) return null;
      return {
        className: metric.className,
        annual: metric.category !== 'fixed' && item.annual !== false
      };
    }).filter(Boolean) : [];
    return {
      viewName: String(cfg.viewName || 'EGT - Anual').trim() || 'EGT - Anual',
      yearCount: sanitizeInt(cfg.yearCount, 9, 1, 30),
      sampleStart: sanitizeInt(cfg.sampleStart, 21, 0, 126),
      includeTotal: cfg.includeTotal !== false,
      groupMode: cfg.groupMode === 'by_metric' ? 'by_metric' : 'by_year',
      metrics: metrics
    };
  }

  function normalizePreset(item) {
    if (!item || typeof item !== 'object') return null;
    var config = normalizeConfig(item.config);
    if (!config.metrics.length) return null;
    var name = String(item.name || config.viewName || 'Vista SQX').trim() || 'Vista SQX';
    return {
      id: presetIdFromName(item.id || name),
      name: name,
      savedAt: String(item.savedAt || new Date().toISOString()),
      config: config
    };
  }

  function buildPresetPackage(presets) {
    return {
      type: PRESET_PACKAGE_TYPE,
      version: PRESET_PACKAGE_VERSION,
      app: 'SQX Edge',
      exportedAt: new Date().toISOString(),
      presets: (presets || getSavedPresets()).map(normalizePreset).filter(Boolean)
    };
  }

  function configFromPresetName(presetName, config) {
    var selector = PRESETS[presetName] || PRESETS['egt-core'];
    var cfg = config || {};
    return normalizeConfig({
      viewName: cfg.viewName,
      yearCount: cfg.yearCount,
      sampleStart: cfg.sampleStart,
      includeTotal: cfg.includeTotal,
      groupMode: cfg.groupMode,
      metrics: METRICS.filter(function(metric) { return selector(metric); }).map(function(metric) {
        return {
          className: metric.className,
          annual: metric.category !== 'fixed' && metric.annualDefault
        };
      })
    });
  }

  function buyerTemplateFromDefinition(definition) {
    return {
      id: definition.id,
      name: definition.name,
      tier: definition.tier || 'pro',
      priority: definition.priority || 'recomendable',
      preset: definition.preset || 'egt-core',
      description: definition.description || '',
      objective: definition.objective || definition.description || '',
      when: definition.when || '',
      nextAction: definition.nextAction || '',
      metricTags: Array.isArray(definition.metricTags) ? definition.metricTags.slice() : [],
      oosTag: definition.oosTag || '',
      oosOptions: Array.isArray(definition.oosOptions) ? definition.oosOptions.slice() : [],
      config: configFromPresetName(definition.preset, definition.config)
    };
  }

  function getBuyerReadyTemplates() {
    return BUYER_READY_TEMPLATE_DEFINITIONS.map(buyerTemplateFromDefinition);
  }

  function findBuyerReadyTemplate(id) {
    return getBuyerReadyTemplates().find(function(template) { return template.id === id; }) || null;
  }

  function findBuyerReadyTemplateByPreset(presetName) {
    return getBuyerReadyTemplates().find(function(template) { return template.preset === presetName; }) || null;
  }

  function setText(id, value) {
    var el = byId(id);
    if (el) el.textContent = value == null ? '' : String(value);
  }

  function setHtml(id, value) {
    var el = byId(id);
    if (el) el.innerHTML = value || '';
  }

  function guideConfigText(template) {
    var cfg = normalizeConfig(template && template.config);
    var sampleEnd = cfg.sampleStart + cfg.yearCount - 1;
    return cfg.yearCount + ' OOS · bloques SQX ' + cfg.sampleStart + '..' + sampleEnd
      + (cfg.includeTotal ? ' + Total consolidado' : '')
      + ' · ' + (cfg.groupMode === 'by_metric' ? 'orden por métrica' : 'orden por año');
  }

  function updateGuideCards() {
    Array.from(global.document.querySelectorAll('[data-vc-template-card]')).forEach(function(card) {
      var active = card.dataset.vcTemplateCard === activeTemplateId;
      card.classList.toggle('is-active', active);
      card.setAttribute('aria-current', active ? 'true' : 'false');
    });
    Array.from(global.document.querySelectorAll('[data-vc-preset]')).forEach(function(button) {
      var template = findBuyerReadyTemplate(activeTemplateId);
      button.classList.toggle('active', !!template && button.dataset.vcPreset === template.preset);
    });
  }

  function setActiveViewGuide(templateId, source) {
    var template = findBuyerReadyTemplate(templateId);
    if (!template) {
      activeTemplateId = '';
      setText('vc-guide-title', 'View personalizada');
      setText('vc-guide-source', source || 'Seleccion manual');
      setText('vc-guide-purpose', 'Has cambiado metricas o ajustes fuera de una plantilla guiada.');
      setText('vc-guide-when', 'Usala solo si sabes que columnas necesita el retest.');
      setText('vc-guide-next', 'Comprueba la preview y descarga la .vw cuando el contador sea coherente.');
      setHtml('vc-guide-tags', '<span class="views-template-metric-tag">custom</span>');
      setText('vc-guide-config', 'Configuracion manual activa');
      updateGuideCards();
      return null;
    }
    activeTemplateId = template.id;
    setText('vc-guide-title', template.name);
    setText('vc-guide-source', source || 'View cargada');
    setText('vc-guide-purpose', template.objective || template.description);
    setText('vc-guide-when', template.when || 'Sigue el orden del pipeline antes de exportar.');
    setText('vc-guide-next', template.nextAction || 'Descarga la .vw e importala en SQX.');
    setHtml('vc-guide-tags', (template.metricTags || []).map(function(tag) {
      return '<span class="views-template-metric-tag">' + escapeHtml(tag) + '</span>';
    }).join('') + '<span class="views-template-metric-tag">' + escapeHtml(template.oosTag || (template.config.yearCount + 'oos')) + '</span>');
    setText('vc-guide-config', guideConfigText(template));
    updateGuideCards();
    return template;
  }

  function templateToPreset(template) {
    if (!template) return null;
    return normalizePreset({
      id: 'buyer-' + template.id,
      name: template.name,
      savedAt: new Date().toISOString(),
      config: template.config
    });
  }

  function accessibleBuyerReadyTemplates() {
    var full = hasFullAccess();
    return getBuyerReadyTemplates().filter(function(template) {
      return full || template.tier !== 'pro';
    });
  }

  function buildBuyerReadyTemplatePack() {
    return buildPresetPackage(accessibleBuyerReadyTemplates().map(templateToPreset));
  }

  function buildTemplateMakerCertView() {
    var template = findBuyerReadyTemplate('template-maker-cert');
    return buildViewXml(template ? template.config : configFromPresetName('template-maker-cert', {
      viewName: 'Template Maker Cert',
      yearCount: 9,
      sampleStart: 21,
      includeTotal: true,
      groupMode: 'by_metric'
    }));
  }

  function getTemplateMakerRequiredMetrics() {
    return TEMPLATE_MAKER_REQUIRED_METRICS.slice();
  }

  function buildCvcDecisionCertView() {
    var template = findBuyerReadyTemplate('cvc-decision-cert');
    return buildViewXml(template ? template.config : configFromPresetName('cvc-decision-cert', {
      viewName: 'CVC Decision Cert',
      yearCount: 9,
      sampleStart: 21,
      includeTotal: true,
      groupMode: 'by_metric'
    }));
  }

  function getCvcDecisionRequiredMetrics() {
    return CVC_DECISION_REQUIRED_METRICS.slice();
  }

  function parsePresetPackage(payload) {
    var data = typeof payload === 'string' ? safeJsonParse(payload, null) : payload;
    if (!data) return [];
    if (Array.isArray(data)) return data.map(normalizePreset).filter(Boolean);
    if (Array.isArray(data.presets)) return data.presets.map(normalizePreset).filter(Boolean);
    if (data.config) return [normalizePreset(data)].filter(Boolean);
    return [];
  }

  function presetColumnCount(preset) {
    var cfg = normalizeConfig(preset && preset.config);
    return countColumns(cfg.metrics || [], cfg.yearCount, cfg.includeTotal);
  }

  function presetImportPreview(payload) {
    var incoming = parsePresetPackage(payload);
    var current = getSavedPresets();
    var currentIds = current.reduce(function(acc, preset) {
      acc[preset.id] = true;
      return acc;
    }, {});
    var duplicateIds = [];
    var metricClasses = {};
    incoming.forEach(function(preset) {
      if (currentIds[preset.id]) duplicateIds.push(preset.id);
      (preset.config.metrics || []).forEach(function(metric) {
        metricClasses[metric.className] = true;
      });
    });
    var mergedCount = incoming.length + current.filter(function(preset) {
      return incoming.every(function(item) { return item.id !== preset.id; });
    }).length;
    return {
      incoming: incoming,
      incomingCount: incoming.length,
      duplicateCount: duplicateIds.length,
      duplicateIds: duplicateIds,
      finalCount: Math.min(30, mergedCount),
      metricClassCount: Object.keys(metricClasses).length,
      newCount: Math.max(0, incoming.length - duplicateIds.length)
    };
  }

  function presetImportPreviewFromText(text) {
    return presetImportPreview(String(text || ''));
  }

  function presetImportPreviewSummary(preview) {
    var data = preview || {};
    if (!data.incomingCount) return 'Preview: el pack no contiene presets SQX Views validos.';
    return 'Preview: ' + data.incomingCount + (data.incomingCount === 1 ? ' preset' : ' presets')
      + ' · ' + data.newCount + ' nuevos'
      + ' · ' + data.duplicateCount + ' reemplazos'
      + ' · ' + data.metricClassCount + ' métricas'
      + ' · total final ' + data.finalCount;
  }

  function presetImportPreviewHtml(preview) {
    var data = preview || {};
    if (!data.incomingCount) return '<div class="views-template-desc">El pack no contiene presets SQX Views validos.</div>';
    var rows = data.incoming.slice(0, 8).map(function(preset) {
      var cfg = normalizeConfig(preset.config);
      var duplicate = data.duplicateIds.indexOf(preset.id) >= 0;
      return ''
        + '<div class="views-import-preview-row">'
        +   '<strong title="' + escapeHtml(preset.name) + '">' + escapeHtml(preset.name) + '</strong>'
        +   '<span>' + escapeHtml(cfg.metrics.length) + ' met</span>'
        +   '<span>' + escapeHtml(presetColumnCount(preset)) + ' col</span>'
        +   '<span>' + escapeHtml(cfg.yearCount) + 'y</span>'
        +   '<span>' + escapeHtml(cfg.groupMode === 'by_metric' ? 'métrica' : 'año') + '</span>'
        +   (duplicate ? '<span class="is-duplicate">reemplaza</span>' : '<span>nuevo</span>')
        + '</div>';
    }).join('');
    if (data.incoming.length > 8) {
      rows += '<div class="views-import-preview-row"><strong>+' + escapeHtml(data.incoming.length - 8) + ' presets mas</strong><span>pack</span></div>';
    }
    return ''
      + '<div class="views-import-preview-head">'
      +   '<strong>' + escapeHtml(presetImportPreviewSummary(data)) + '</strong>'
      +   '<span>' + escapeHtml(data.metricClassCount) + ' clases SQX</span>'
      + '</div>'
      + '<div class="views-import-preview-list">' + rows + '</div>';
  }

  function importPresetPackage(payload) {
    var incoming = parsePresetPackage(payload);
    if (!incoming.length) {
      return { imported: 0, presets: getSavedPresets() };
    }
    var incomingIds = incoming.reduce(function(acc, preset) {
      acc[preset.id] = true;
      return acc;
    }, {});
    var merged = incoming.concat(getSavedPresets().filter(function(preset) {
      return !incomingIds[preset.id];
    }));
    return { imported: incoming.length, presets: setSavedPresets(merged) };
  }

  function importPresetPackageFromText(text) {
    return importPresetPackage(String(text || ''));
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
      'Bloques OOS: ' + sampleStart + '..' + (sampleStart + yearCount - 1) + (opts.includeTotal !== false ? ' + Total consolidado' : ''),
      'Metricas: ' + selected.length + ' | Columnas: ' + columns.length,
      '------------------------------------------------------------'
    ];
    columns.slice(0, 80).forEach(function(column, index) {
      var sampleLabel = column.sampleType === 127 ? 'Total consolidado' : 'OOS ' + column.sampleType;
      lines.push(String(index + 1).padStart(3, ' ') + '. ' + column.display + '  ' + sampleLabel + '  [' + column.className + ']');
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

  function setImportPreview(html, hasItems) {
    var el = byId('vc-import-preview');
    if (!el) return;
    el.innerHTML = html || '';
    el.classList.toggle('has-items', !!hasItems);
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

  function updateConfigSummary(opts) {
    var options = opts || optionsFromDom();
    var yearCount = sanitizeInt(options.yearCount, 9, 1, 30);
    var sampleStart = sanitizeInt(options.sampleStart, 21, 0, 126);
    var sampleEnd = sampleStart + yearCount - 1;
    setText('vc-summary-view', options.viewName || 'EGT - Anual');
    setText('vc-summary-oos', yearCount + (yearCount === 1 ? ' bloque' : ' bloques'));
    setText('vc-summary-sample', sampleStart + '..' + sampleEnd);
    setText('vc-summary-order', options.groupMode === 'by_metric' ? 'Por métrica' : 'Por año');
    setText('vc-summary-total', options.includeTotal !== false ? 'Incluido' : 'Sin total');
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
    if (byId('vc-mode-label')) byId('vc-mode-label').textContent = opts.groupMode === 'by_metric' ? 'Agrupado por métrica' : 'Agrupado por año';
    updateConfigSummary(opts);
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
      ? '<span class="views-annual-pill total">Total</span>'
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
        '<div class="views-category-head"><strong>' + escapeHtml(CATEGORY_LABELS[category] || category) + '</strong><small>' + grouped[category].length + ' métricas</small></div>' +
        '<div class="views-metric-grid">' + rows + '</div>' +
      '</div>';
    }).join('');
    bindMetricChanges();
  }

  function renderBuyerReadyTemplates() {
    var list = byId('vc-template-list');
    var count = byId('vc-template-count');
    var templates = getBuyerReadyTemplates();
    var full = hasFullAccess();
    if (count) count.textContent = templates.length + (templates.length === 1 ? ' view' : ' views');
    if (!list) return templates;
    list.innerHTML = templates.map(function(template) {
      var disabled = template.tier === 'pro' && !full;
      var actionAttrs = disabled ? ' disabled aria-disabled="true"' : '';
      var oosOptions = (template.oosOptions || []).map(function(value) { return value + 'oos'; }).join(', ');
      var oosTitle = oosOptions ? ' title="Opciones OOS: ' + escapeHtml(oosOptions) + '"' : '';
      var metricTags = (template.metricTags || []).map(function(tag) {
        return '<span class="views-template-metric-tag">' + escapeHtml(tag) + '</span>';
      }).join('');
      var isActive = template.id === activeTemplateId;
      return '<article class="views-template-card is-guide-card' + (isActive ? ' is-active' : '') + '" data-vc-template-card="' + escapeHtml(template.id) + '" aria-current="' + (isActive ? 'true' : 'false') + '">' +
        '<div class="views-template-top">' +
          '<div><div class="views-template-name">' + escapeHtml(template.name) + '</div>' +
          '<p class="views-template-desc">' + escapeHtml(template.objective || template.description) + '</p></div>' +
          '<div class="views-template-badges">' +
            '<span class="views-template-priority ' + escapeHtml(template.priority || 'recomendable') + '">' + escapeHtml(template.priority || 'recomendable') + '</span>' +
          '</div>' +
        '</div>' +
        '<div class="views-template-when"><strong>Uso:</strong> ' + escapeHtml(template.when || template.description) + '</div>' +
        '<div class="views-template-meta">' +
          '<span>' + template.config.metrics.length + ' métricas</span>' +
          '<span' + oosTitle + '>' + escapeHtml(template.oosTag || (template.config.yearCount + 'oos')) + '</span>' +
          metricTags +
        '</div>' +
        '<div class="views-template-actions">' +
          '<button class="export-btn views-template-select" data-vc-template-load="' + escapeHtml(template.id) + '" type="button"' + actionAttrs + '>Usar esta view</button>' +
        '</div>' +
      '</article>';
    }).join('');
    return templates;
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
    if (!hasFull && name !== 'egt-core' && name !== 'template-maker-cert' && name !== 'clear') {
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
    setActiveViewGuide(name === 'clear' ? '' : (findBuyerReadyTemplateByPreset(name) || {}).id, name === 'clear' ? 'Seleccion limpia' : 'Preset aplicado');
  }

  function setFieldValue(id, value) {
    var el = byId(id);
    if (!el || value == null || value === '') return;
    el.value = value;
  }

  function openHandoff(options) {
    var opts = options || {};
    var preset = opts.preset || opts.handoff || 'egt-core';
    if (SQX.ui && SQX.ui.activateTabById) SQX.ui.activateTabById('views', global.document);
    setFieldValue('vc-view-name', opts.viewName || opts.name);
    setFieldValue('vc-year-count', opts.yearCount || opts.years);
    setFieldValue('vc-sample-start', opts.sampleStart);
    if (opts.groupMode) setFieldValue('vc-group-mode', opts.groupMode);
    applyPreset(preset);
    setActiveViewGuide((findBuyerReadyTemplateByPreset(preset) || {}).id, 'Handoff cargado');
    var shell = global.document.querySelector('.views-shell');
    if (shell && shell.scrollIntoView) shell.scrollIntoView({ behavior: 'smooth', block: 'start' });
    var preview = updatePreview();
    setStatus('Handoff cargado: ' + (opts.viewName || opts.name || preset) + '.', 'ok');
    if (global.addHomeTrace) global.addHomeTrace('SQX Views', 'Handoff ' + preset + ' preparado', 'ok');
    return preview;
  }

  function bindHandoffLinks() {
    Array.from(global.document.querySelectorAll('[data-vc-handoff]')).forEach(function(button) {
      button.addEventListener('click', function() {
        openHandoff({
          preset: button.dataset.vcHandoff,
          viewName: button.dataset.vcName,
          yearCount: button.dataset.vcYears,
          sampleStart: button.dataset.vcSampleStart,
          groupMode: button.dataset.vcGroupMode
        });
      });
    });
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
    setActiveViewGuide('', 'Preset propio cargado');
    setText('vc-guide-title', preset.name);
    setText('vc-guide-purpose', 'Preset propio cargado con la configuracion que guardaste.');
    setText('vc-guide-when', 'Usalo como variante controlada si mantiene el mismo objetivo metodologico.');
    setText('vc-guide-next', 'Comprueba columnas y descarga la .vw cuando la preview encaje.');
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

  function loadBuyerReadyTemplate(id) {
    var template = findBuyerReadyTemplate(id);
    if (!template) {
      setStatus('View no encontrada.', 'warn');
      return null;
    }
    if (template.tier === 'pro' && !hasFullAccess()) {
      setStatus('Esta view requiere SQX Edge Pro.', 'warn');
      return null;
    }
    applyConfig(template.config);
    setActiveViewGuide(template.id, 'View cargada');
    setStatus('View cargada: ' + template.name + '. ' + (template.nextAction || ''), 'ok');
    if (global.addHomeTrace) global.addHomeTrace('SQX Views', 'View ' + template.name + ' cargada', 'ok');
    return template;
  }

  function saveBuyerReadyTemplate(id) {
    var template = findBuyerReadyTemplate(id);
    var preset = templateToPreset(template);
    if (!preset) {
      setStatus('View no encontrada.', 'warn');
      return null;
    }
    if (template.tier === 'pro' && !hasFullAccess()) {
      setStatus('Esta view requiere SQX Edge Pro.', 'warn');
      return null;
    }
    var presets = getSavedPresets().filter(function(item) { return item.id !== preset.id; });
    presets.unshift(preset);
    setSavedPresets(presets);
    renderSavedPresets();
    if (byId('vc-saved-select')) byId('vc-saved-select').value = preset.id;
    setActiveViewGuide(template.id, 'View guardada como preset');
    setStatus('View guardada como preset: ' + preset.name + '.', 'ok');
    return preset;
  }

  function downloadJson(filename, payload) {
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var link = global.document.createElement('a');
    link.href = url;
    link.download = filename;
    global.document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function exportPresetPackage() {
    var presets = getSavedPresets();
    if (!presets.length) {
      setStatus('Guarda al menos un preset antes de exportar.', 'warn');
      return;
    }
    var pack = buildPresetPackage(presets);
    var day = new Date().toISOString().slice(0, 10);
    downloadJson('sqx-view-presets-' + day + '.json', pack);
    setStatus('Pack exportado: ' + pack.presets.length + ' presets.', 'ok');
  }

  function exportBuyerReadyTemplatePack() {
    var pack = buildBuyerReadyTemplatePack();
    if (!pack.presets.length) {
      setStatus('No hay views disponibles para exportar.', 'warn');
      return;
    }
    downloadJson('sqx-view-buyer-ready-pack-v' + PRESET_PACKAGE_VERSION + '.json', pack);
    setStatus('Views exportadas: ' + pack.presets.length + ' presets.', 'ok');
  }

  function importPresetFile(file) {
    if (!file) {
      setStatus('Selecciona un pack JSON de presets.', 'warn');
      setImportPreview('', false);
      return;
    }
    var reader = new FileReader();
    reader.onload = function() {
      var preview = presetImportPreviewFromText(reader.result || '');
      setImportPreview(presetImportPreviewHtml(preview), !!preview.incomingCount);
      var result = importPresetPackageFromText(reader.result || '');
      renderSavedPresets();
      setStatus(result.imported ? presetImportPreviewSummary(preview) : 'El pack no contiene presets validos.', result.imported ? 'ok' : 'warn');
    };
    reader.onerror = function() {
      setStatus('No se pudo leer el pack de presets.', 'error');
      setImportPreview('', false);
    };
    reader.readAsText(file);
  }

  function downloadView() {
    var opts = updatePreview();
    if (!opts.selected.length) {
      setStatus('Selecciona al menos una métrica.', 'error');
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
    if (byId('vc-export-presets-btn')) byId('vc-export-presets-btn').addEventListener('click', exportPresetPackage);
    if (byId('vc-export-template-pack-btn')) byId('vc-export-template-pack-btn').addEventListener('click', exportBuyerReadyTemplatePack);
    if (byId('vc-template-list')) {
      byId('vc-template-list').addEventListener('click', function(event) {
        var loadId = event.target && event.target.dataset ? event.target.dataset.vcTemplateLoad : '';
        var saveId = event.target && event.target.dataset ? event.target.dataset.vcTemplateSave : '';
        if (loadId) loadBuyerReadyTemplate(loadId);
        if (saveId) saveBuyerReadyTemplate(saveId);
      });
    }
    if (byId('vc-import-presets-btn') && byId('vc-import-presets-file')) {
      byId('vc-import-presets-btn').addEventListener('click', function() { byId('vc-import-presets-file').click(); });
      byId('vc-import-presets-file').addEventListener('change', function(event) {
        importPresetFile(event.target.files && event.target.files[0]);
        event.target.value = '';
      });
    }
    bindHandoffLinks();
  }

  function init() {
    if (!byId('vc-metric-list')) return;
    if (global.addEventListener && !SQX.viewCreatorRemotePresetListenerBound) {
      global.addEventListener('sqx:remote-state-loaded', function(event) {
        var keys = event && event.detail && event.detail.keys;
        if (Array.isArray(keys) && keys.indexOf(presetsStorageKey) >= 0) renderSavedPresets();
      });
      SQX.viewCreatorRemotePresetListenerBound = true;
    }
    renderMetrics();
    bindControls();
    renderBuyerReadyTemplates();
    renderSavedPresets();
    var note = byId('vc-license-note');
    if (note) note.textContent = hasFullAccess() ? 'Catálogo completo habilitado.' : 'Preset EGT Core activo. Las views avanzadas requieren licencia.';
    updatePreview();
    setActiveViewGuide(activeTemplateId, 'View recomendada para empezar');
  }

  SQX.viewCreator = SQX.viewCreator || {
    applyPreset: applyPreset,
    applyConfig: applyConfig,
    buildViewXml: buildViewXml,
    categoryLabels: CATEGORY_LABELS,
    columnSpecs: columnSpecs,
    countColumns: countColumns,
    downloadView: downloadView,
    bindHandoffLinks: bindHandoffLinks,
    buildBuyerReadyTemplatePack: buildBuyerReadyTemplatePack,
    buildCvcDecisionCertView: buildCvcDecisionCertView,
    buildTemplateMakerCertView: buildTemplateMakerCertView,
    buildPresetPackage: buildPresetPackage,
    buyerReadyTemplates: getBuyerReadyTemplates,
    importPresetPackage: importPresetPackage,
    importPresetPackageFromText: importPresetPackageFromText,
    getSavedPresets: getSavedPresets,
    getCvcDecisionRequiredMetrics: getCvcDecisionRequiredMetrics,
    getTemplateMakerRequiredMetrics: getTemplateMakerRequiredMetrics,
    groupedMetrics: groupedMetrics,
    init: init,
    loadBuyerReadyTemplate: loadBuyerReadyTemplate,
    metrics: METRICS,
    packageType: PRESET_PACKAGE_TYPE,
    packageVersion: PRESET_PACKAGE_VERSION,
    openHandoff: openHandoff,
    presetImportPreview: presetImportPreview,
    presetImportPreviewFromText: presetImportPreviewFromText,
    presetImportPreviewHtml: presetImportPreviewHtml,
    presetImportPreviewSummary: presetImportPreviewSummary,
    previewLines: previewLines,
    renderBuyerReadyTemplates: renderBuyerReadyTemplates,
    sanitizeInt: sanitizeInt,
    saveBuyerReadyTemplate: saveBuyerReadyTemplate,
    saveCurrentPreset: saveCurrentPreset,
    selectedMetrics: selectedMetrics,
    serializeConfig: serializeConfig,
    setActiveViewGuide: setActiveViewGuide,
    setSavedPresets: setSavedPresets,
    storageKey: presetsStorageKey
  };

  if (SQX.registerModule) {
    SQX.registerModule('view-creator', SQX.viewCreator);
  }
})(window);

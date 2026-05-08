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

  var BUYER_READY_TEMPLATE_DEFINITIONS = [
    {
      id: 'egt-first-review',
      name: 'EGT First Review',
      tier: 'free',
      preset: 'egt-core',
      description: 'Vista inicial para revisar candidatos con el set EGT Core anual.',
      config: { viewName: 'EGT First Review', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_year' }
    },
    {
      id: 'robustness-pack-screen',
      name: 'Robustness Pack Screen',
      tier: 'pro',
      preset: 'robustness',
      description: 'Revision de estabilidad, anos malos, stagnation y ratios para filtrar antes de portfolio.',
      config: { viewName: 'Robustness Pack Screen', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_metric' }
    },
    {
      id: 'risk-capital-review',
      name: 'Risk Capital Review',
      tier: 'pro',
      preset: 'risk',
      description: 'Vista de riesgo para drawdown, dispersion, rachas negativas y stress previo a entrega.',
      config: { viewName: 'Risk Capital Review', yearCount: 7, sampleStart: 23, includeTotal: true, groupMode: 'by_year' }
    },
    {
      id: 'full-audit-handoff',
      name: 'Full Audit Handoff',
      tier: 'pro',
      preset: 'full-audit',
      description: 'Salida amplia para auditoria completa y CSV posterior cuando una tanda ya merece investigacion.',
      config: { viewName: 'Full Audit Handoff', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_metric' }
    }
  ];

  var BUYER_PROFILE_PACK_DEFINITIONS = [
    {
      id: 'free-evaluation-starter',
      name: 'Free Evaluation Starter',
      tier: 'free',
      description: 'Pack minimo para que un usuario pruebe la carga de vistas sin activar Pro.',
      templateIds: ['egt-first-review']
    },
    {
      id: 'pro-setup-assist',
      name: 'Pro Setup Assist',
      tier: 'pro',
      description: 'Primer pack recomendado para entregar a un comprador Pro tras configuracion inicial.',
      templateIds: ['egt-first-review', 'robustness-pack-screen', 'risk-capital-review']
    },
    {
      id: 'risk-capital-buyer',
      name: 'Risk Capital Buyer',
      tier: 'pro',
      description: 'Pack orientado a compradores que priorizan drawdown, dispersion y riesgo operativo.',
      templateIds: ['risk-capital-review', 'robustness-pack-screen']
    },
    {
      id: 'audit-delivery-buyer',
      name: 'Audit Delivery Buyer',
      tier: 'pro',
      description: 'Pack amplio para handoff de auditoria cuando una tanda ya paso filtros iniciales.',
      templateIds: ['full-audit-handoff', 'risk-capital-review', 'robustness-pack-screen']
    }
  ];
  var VALIDATION_WORKFLOW_PACK_DEFINITIONS = [
    {
      id: 'free-core-validation',
      name: 'Free Core Validation',
      tier: 'free',
      type: 'validation',
      description: 'Flujo minimo para validar que SQX Views carga y exporta una vista anual base.',
      views: [
        { id: 'free-egt-intake', name: 'Free EGT Intake', preset: 'egt-core', config: { viewName: 'Free EGT Intake', yearCount: 5, sampleStart: 25, includeTotal: true, groupMode: 'by_year' } }
      ]
    },
    {
      id: 'asset-family-review',
      name: 'Asset Family Review',
      tier: 'pro',
      type: 'asset',
      description: 'Tres vistas preparadas para revisar Forex, indices y oro con enfoque distinto por familia.',
      views: [
        { id: 'forex-first-review', name: 'Forex First Review', preset: 'egt-core', config: { viewName: 'Forex First Review', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_year' } },
        { id: 'index-robustness-review', name: 'Index Robustness Review', preset: 'robustness', config: { viewName: 'Index Robustness Review', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_metric' } },
        { id: 'gold-risk-review', name: 'Gold Risk Review', preset: 'risk', config: { viewName: 'Gold Risk Review', yearCount: 7, sampleStart: 23, includeTotal: true, groupMode: 'by_year' } }
      ]
    },
    {
      id: 'validation-screen-flow',
      name: 'Validation Screen Flow',
      tier: 'pro',
      type: 'validation',
      description: 'Secuencia intake -> robustez -> capital risk para revisar candidatos antes de portfolio.',
      views: [
        { id: 'intake-egt-core', name: 'Intake EGT Core', preset: 'egt-core', config: { viewName: 'Intake EGT Core', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_year' } },
        { id: 'stability-stress-screen', name: 'Stability Stress Screen', preset: 'robustness', config: { viewName: 'Stability Stress Screen', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_metric' } },
        { id: 'capital-risk-cut', name: 'Capital Risk Cut', preset: 'risk', config: { viewName: 'Capital Risk Cut', yearCount: 7, sampleStart: 23, includeTotal: true, groupMode: 'by_year' } }
      ]
    },
    {
      id: 'audit-export-flow',
      name: 'Audit Export Flow',
      tier: 'pro',
      type: 'handoff',
      description: 'Pack de entrega para auditoria: vista amplia, apendice de riesgo y apendice de robustez.',
      views: [
        { id: 'full-audit-export', name: 'Full Audit Export', preset: 'full-audit', config: { viewName: 'Full Audit Export', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_metric' } },
        { id: 'risk-appendix', name: 'Risk Appendix', preset: 'risk', config: { viewName: 'Risk Appendix', yearCount: 7, sampleStart: 23, includeTotal: true, groupMode: 'by_year' } },
        { id: 'robustness-appendix', name: 'Robustness Appendix', preset: 'robustness', config: { viewName: 'Robustness Appendix', yearCount: 9, sampleStart: 21, includeTotal: true, groupMode: 'by_metric' } }
      ]
    }
  ];

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
    var clean = (presets || []).map(normalizePreset).filter(Boolean).slice(0, 30);
    global.localStorage.setItem(presetsStorageKey, JSON.stringify(clean));
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
      preset: definition.preset || 'egt-core',
      description: definition.description || '',
      config: configFromPresetName(definition.preset, definition.config)
    };
  }

  function getBuyerReadyTemplates() {
    return BUYER_READY_TEMPLATE_DEFINITIONS.map(buyerTemplateFromDefinition);
  }

  function findBuyerReadyTemplate(id) {
    return getBuyerReadyTemplates().find(function(template) { return template.id === id; }) || null;
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

  function buyerProfilePackFromDefinition(definition) {
    var templates = (definition.templateIds || []).map(findBuyerReadyTemplate).filter(Boolean);
    return {
      id: definition.id,
      name: definition.name,
      tier: definition.tier || 'pro',
      description: definition.description || '',
      templateIds: templates.map(function(template) { return template.id; }),
      templates: templates
    };
  }

  function getBuyerProfilePacks() {
    return BUYER_PROFILE_PACK_DEFINITIONS.map(buyerProfilePackFromDefinition);
  }

  function findBuyerProfilePack(id) {
    return getBuyerProfilePacks().find(function(pack) { return pack.id === id; }) || null;
  }

  function canUseBuyerProfilePack(pack) {
    return !!(pack && (pack.tier !== 'pro' || hasFullAccess()));
  }

  function profileTemplateToPreset(pack, template) {
    if (!pack || !template) return null;
    return normalizePreset({
      id: 'profile-' + pack.id + '-' + template.id,
      name: pack.name + ' - ' + template.name,
      savedAt: new Date().toISOString(),
      config: template.config
    });
  }

  function buyerProfilePackPresets(id) {
    var pack = typeof id === 'string' ? findBuyerProfilePack(id) : id;
    if (!pack) return [];
    return pack.templates.map(function(template) {
      return profileTemplateToPreset(pack, template);
    }).filter(Boolean);
  }

  function buildBuyerProfilePack(id) {
    return buildPresetPackage(buyerProfilePackPresets(id));
  }

  function buildAllBuyerProfilePacks() {
    var packs = getBuyerProfilePacks().filter(canUseBuyerProfilePack);
    var presets = [];
    packs.forEach(function(pack) {
      presets = presets.concat(buyerProfilePackPresets(pack));
    });
    return buildPresetPackage(presets);
  }

  function validationWorkflowViewFromDefinition(definition) {
    var view = definition || {};
    return {
      id: view.id,
      name: view.name,
      preset: view.preset || 'egt-core',
      config: configFromPresetName(view.preset || 'egt-core', view.config || {})
    };
  }

  function validationWorkflowPackFromDefinition(definition) {
    var views = (definition.views || []).map(validationWorkflowViewFromDefinition).filter(function(view) {
      return view.id && view.name && view.config.metrics.length;
    });
    return {
      id: definition.id,
      name: definition.name,
      tier: definition.tier || 'pro',
      type: definition.type || 'validation',
      description: definition.description || '',
      views: views
    };
  }

  function getValidationWorkflowPacks() {
    return VALIDATION_WORKFLOW_PACK_DEFINITIONS.map(validationWorkflowPackFromDefinition);
  }

  function findValidationWorkflowPack(id) {
    return getValidationWorkflowPacks().find(function(pack) { return pack.id === id; }) || null;
  }

  function canUseValidationWorkflowPack(pack) {
    return !!(pack && (pack.tier !== 'pro' || hasFullAccess()));
  }

  function validationWorkflowViewToPreset(pack, view) {
    if (!pack || !view) return null;
    return normalizePreset({
      id: 'workflow-' + pack.id + '-' + view.id,
      name: pack.name + ' - ' + view.name,
      savedAt: new Date().toISOString(),
      config: view.config
    });
  }

  function validationWorkflowPackPresets(id) {
    var pack = typeof id === 'string' ? findValidationWorkflowPack(id) : id;
    if (!pack) return [];
    return pack.views.map(function(view) {
      return validationWorkflowViewToPreset(pack, view);
    }).filter(Boolean);
  }

  function buildValidationWorkflowPack(id) {
    return buildPresetPackage(validationWorkflowPackPresets(id));
  }

  function buildAllValidationWorkflowPacks() {
    var packs = getValidationWorkflowPacks().filter(canUseValidationWorkflowPack);
    var presets = [];
    packs.forEach(function(pack) {
      presets = presets.concat(validationWorkflowPackPresets(pack));
    });
    return buildPresetPackage(presets);
  }

  function parsePresetPackage(payload) {
    var data = typeof payload === 'string' ? safeJsonParse(payload, null) : payload;
    if (!data) return [];
    if (Array.isArray(data)) return data.map(normalizePreset).filter(Boolean);
    if (Array.isArray(data.presets)) return data.presets.map(normalizePreset).filter(Boolean);
    if (data.config) return [normalizePreset(data)].filter(Boolean);
    return [];
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

  function renderBuyerReadyTemplates() {
    var list = byId('vc-template-list');
    var count = byId('vc-template-count');
    var templates = getBuyerReadyTemplates();
    var full = hasFullAccess();
    if (count) count.textContent = templates.length + (templates.length === 1 ? ' ejemplo' : ' ejemplos');
    if (!list) return templates;
    list.innerHTML = templates.map(function(template) {
      var disabled = template.tier === 'pro' && !full;
      var actionAttrs = disabled ? ' disabled aria-disabled="true"' : '';
      return '<article class="views-template-card ' + (template.tier === 'pro' ? 'is-pro' : 'is-free') + '">' +
        '<div class="views-template-top">' +
          '<div><div class="views-template-name">' + escapeHtml(template.name) + '</div>' +
          '<p class="views-template-desc">' + escapeHtml(template.description) + '</p></div>' +
          '<span class="views-template-tier ' + escapeHtml(template.tier) + '">' + escapeHtml(template.tier) + '</span>' +
        '</div>' +
        '<div class="views-template-meta">' +
          '<span>' + template.config.metrics.length + ' metricas</span>' +
          '<span>' + template.config.yearCount + ' anos</span>' +
          '<span>s' + template.config.sampleStart + '..' + (template.config.sampleStart + template.config.yearCount - 1) + '</span>' +
        '</div>' +
        '<div class="views-template-actions">' +
          '<button class="filter-btn" data-vc-template-load="' + escapeHtml(template.id) + '" type="button"' + actionAttrs + '>Cargar</button>' +
          '<button class="filter-btn" data-vc-template-save="' + escapeHtml(template.id) + '" type="button"' + actionAttrs + '>Guardar</button>' +
        '</div>' +
      '</article>';
    }).join('');
    return templates;
  }

  function renderBuyerProfilePacks() {
    var list = byId('vc-profile-list');
    var count = byId('vc-profile-count');
    var packs = getBuyerProfilePacks();
    var full = hasFullAccess();
    if (count) count.textContent = packs.length + (packs.length === 1 ? ' pack' : ' packs');
    if (!list) return packs;
    list.innerHTML = packs.map(function(pack) {
      var disabled = pack.tier === 'pro' && !full;
      var actionAttrs = disabled ? ' disabled aria-disabled="true"' : '';
      var flow = pack.templates.map(function(template) {
        return '<span>' + escapeHtml(template.name) + '</span>';
      }).join('');
      return '<article class="views-profile-card ' + (pack.tier === 'pro' ? 'is-pro' : 'is-free') + '">' +
        '<div class="views-profile-top">' +
          '<div><div class="views-profile-name">' + escapeHtml(pack.name) + '</div>' +
          '<p class="views-profile-desc">' + escapeHtml(pack.description) + '</p></div>' +
          '<span class="views-template-tier ' + escapeHtml(pack.tier) + '">' + escapeHtml(pack.tier) + '</span>' +
        '</div>' +
        '<div class="views-profile-meta">' +
          '<span>' + pack.templates.length + ' vistas</span>' +
          '<span>' + pack.templates.reduce(function(total, template) { return total + template.config.metrics.length; }, 0) + ' metricas base</span>' +
        '</div>' +
        '<div class="views-profile-flow">' + flow + '</div>' +
        '<div class="views-profile-actions">' +
          '<button class="filter-btn" data-vc-profile-load="' + escapeHtml(pack.id) + '" type="button"' + actionAttrs + '>Cargar</button>' +
          '<button class="filter-btn" data-vc-profile-save="' + escapeHtml(pack.id) + '" type="button"' + actionAttrs + '>Guardar pack</button>' +
          '<button class="filter-btn" data-vc-profile-export="' + escapeHtml(pack.id) + '" type="button"' + actionAttrs + '>Exportar</button>' +
        '</div>' +
      '</article>';
    }).join('');
    return packs;
  }

  function renderValidationWorkflowPacks() {
    var list = byId('vc-workflow-pack-list');
    var count = byId('vc-workflow-pack-count');
    var packs = getValidationWorkflowPacks();
    var full = hasFullAccess();
    if (count) count.textContent = packs.length + (packs.length === 1 ? ' flujo' : ' flujos');
    if (!list) return packs;
    list.innerHTML = packs.map(function(pack) {
      var disabled = pack.tier === 'pro' && !full;
      var actionAttrs = disabled ? ' disabled aria-disabled="true"' : '';
      var flow = pack.views.map(function(view) {
        return '<span>' + escapeHtml(view.name) + '</span>';
      }).join('');
      return '<article class="views-workflow-card ' + (pack.tier === 'pro' ? 'is-pro' : 'is-free') + '">' +
        '<div class="views-profile-top">' +
          '<div><div class="views-profile-name">' + escapeHtml(pack.name) + '</div>' +
          '<p class="views-profile-desc">' + escapeHtml(pack.description) + '</p></div>' +
          '<span class="views-template-tier ' + escapeHtml(pack.tier) + '">' + escapeHtml(pack.type) + '</span>' +
        '</div>' +
        '<div class="views-profile-meta">' +
          '<span>' + pack.views.length + ' vistas</span>' +
          '<span>' + pack.views.reduce(function(total, view) { return total + view.config.metrics.length; }, 0) + ' metricas base</span>' +
        '</div>' +
        '<div class="views-profile-flow">' + flow + '</div>' +
        '<div class="views-profile-actions">' +
          '<button class="filter-btn" data-vc-workflow-load="' + escapeHtml(pack.id) + '" type="button"' + actionAttrs + '>Cargar</button>' +
          '<button class="filter-btn" data-vc-workflow-save="' + escapeHtml(pack.id) + '" type="button"' + actionAttrs + '>Guardar pack</button>' +
          '<button class="filter-btn" data-vc-workflow-export="' + escapeHtml(pack.id) + '" type="button"' + actionAttrs + '>Exportar</button>' +
        '</div>' +
      '</article>';
    }).join('');
    return packs;
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
    var shell = global.document.querySelector('.views-shell');
    if (shell && shell.scrollIntoView) shell.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setStatus('Handoff cargado: ' + (opts.viewName || opts.name || preset) + '.', 'ok');
    if (global.addHomeTrace) global.addHomeTrace('SQX Views', 'Handoff ' + preset + ' preparado', 'ok');
    return updatePreview();
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
      setStatus('Ejemplo no encontrado.', 'warn');
      return null;
    }
    if (template.tier === 'pro' && !hasFullAccess()) {
      setStatus('Este ejemplo requiere SQX Edge Pro.', 'warn');
      return null;
    }
    applyConfig(template.config);
    setStatus('Ejemplo cargado: ' + template.name + '.', 'ok');
    if (global.addHomeTrace) global.addHomeTrace('SQX Views', 'Ejemplo ' + template.name + ' cargado', 'ok');
    return template;
  }

  function saveBuyerReadyTemplate(id) {
    var template = findBuyerReadyTemplate(id);
    var preset = templateToPreset(template);
    if (!preset) {
      setStatus('Ejemplo no encontrado.', 'warn');
      return null;
    }
    if (template.tier === 'pro' && !hasFullAccess()) {
      setStatus('Este ejemplo requiere SQX Edge Pro.', 'warn');
      return null;
    }
    var presets = getSavedPresets().filter(function(item) { return item.id !== preset.id; });
    presets.unshift(preset);
    setSavedPresets(presets);
    renderSavedPresets();
    if (byId('vc-saved-select')) byId('vc-saved-select').value = preset.id;
    setStatus('Ejemplo guardado como preset: ' + preset.name + '.', 'ok');
    return preset;
  }

  function loadBuyerProfilePack(id) {
    var pack = findBuyerProfilePack(id);
    if (!pack) {
      setStatus('Pack de perfil no encontrado.', 'warn');
      return null;
    }
    if (!canUseBuyerProfilePack(pack)) {
      setStatus('Este pack por perfil requiere SQX Edge Pro.', 'warn');
      return null;
    }
    var first = pack.templates[0];
    if (!first) {
      setStatus('El pack no contiene vistas validas.', 'warn');
      return null;
    }
    applyConfig(first.config);
    setStatus('Pack cargado: ' + pack.name + ' (' + first.name + ').', 'ok');
    if (global.addHomeTrace) global.addHomeTrace('SQX Views', 'Pack ' + pack.name + ' cargado', 'ok');
    return pack;
  }

  function saveBuyerProfilePack(id) {
    var pack = findBuyerProfilePack(id);
    if (!pack) {
      setStatus('Pack de perfil no encontrado.', 'warn');
      return null;
    }
    if (!canUseBuyerProfilePack(pack)) {
      setStatus('Este pack por perfil requiere SQX Edge Pro.', 'warn');
      return null;
    }
    var incoming = buyerProfilePackPresets(pack);
    if (!incoming.length) {
      setStatus('El pack no contiene presets validos.', 'warn');
      return null;
    }
    var incomingIds = incoming.reduce(function(acc, preset) {
      acc[preset.id] = true;
      return acc;
    }, {});
    setSavedPresets(incoming.concat(getSavedPresets().filter(function(preset) { return !incomingIds[preset.id]; })));
    renderSavedPresets();
    if (byId('vc-saved-select')) byId('vc-saved-select').value = incoming[0].id;
    setStatus('Pack guardado: ' + pack.name + ' (' + incoming.length + ' presets).', 'ok');
    return incoming;
  }

  function loadValidationWorkflowPack(id) {
    var pack = findValidationWorkflowPack(id);
    if (!pack) {
      setStatus('Flujo de validacion no encontrado.', 'warn');
      return null;
    }
    if (!canUseValidationWorkflowPack(pack)) {
      setStatus('Este flujo requiere SQX Edge Pro.', 'warn');
      return null;
    }
    var first = pack.views[0];
    if (!first) {
      setStatus('El flujo no contiene vistas validas.', 'warn');
      return null;
    }
    applyConfig(first.config);
    setStatus('Flujo cargado: ' + pack.name + ' (' + first.name + ').', 'ok');
    if (global.addHomeTrace) global.addHomeTrace('SQX Views', 'Flujo ' + pack.name + ' cargado', 'ok');
    return pack;
  }

  function saveValidationWorkflowPack(id) {
    var pack = findValidationWorkflowPack(id);
    if (!pack) {
      setStatus('Flujo de validacion no encontrado.', 'warn');
      return null;
    }
    if (!canUseValidationWorkflowPack(pack)) {
      setStatus('Este flujo requiere SQX Edge Pro.', 'warn');
      return null;
    }
    var incoming = validationWorkflowPackPresets(pack);
    if (!incoming.length) {
      setStatus('El flujo no contiene presets validos.', 'warn');
      return null;
    }
    var incomingIds = incoming.reduce(function(acc, preset) {
      acc[preset.id] = true;
      return acc;
    }, {});
    setSavedPresets(incoming.concat(getSavedPresets().filter(function(preset) { return !incomingIds[preset.id]; })));
    renderSavedPresets();
    if (byId('vc-saved-select')) byId('vc-saved-select').value = incoming[0].id;
    setStatus('Flujo guardado: ' + pack.name + ' (' + incoming.length + ' presets).', 'ok');
    return incoming;
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
      setStatus('No hay ejemplos disponibles para exportar.', 'warn');
      return;
    }
    downloadJson('sqx-view-buyer-ready-pack-v' + PRESET_PACKAGE_VERSION + '.json', pack);
    setStatus('Ejemplos exportados: ' + pack.presets.length + ' presets.', 'ok');
  }

  function exportBuyerProfilePack(id) {
    var packDef = findBuyerProfilePack(id);
    if (!packDef) {
      setStatus('Pack de perfil no encontrado.', 'warn');
      return null;
    }
    if (!canUseBuyerProfilePack(packDef)) {
      setStatus('Este pack por perfil requiere SQX Edge Pro.', 'warn');
      return null;
    }
    var pack = buildBuyerProfilePack(packDef);
    if (!pack.presets.length) {
      setStatus('El pack no contiene presets validos.', 'warn');
      return null;
    }
    downloadJson('sqx-view-profile-' + packDef.id + '-pack-v' + PRESET_PACKAGE_VERSION + '.json', pack);
    setStatus('Pack exportado: ' + packDef.name + ' (' + pack.presets.length + ' presets).', 'ok');
    return pack;
  }

  function exportValidationWorkflowPack(id) {
    var packDef = findValidationWorkflowPack(id);
    if (!packDef) {
      setStatus('Flujo de validacion no encontrado.', 'warn');
      return null;
    }
    if (!canUseValidationWorkflowPack(packDef)) {
      setStatus('Este flujo requiere SQX Edge Pro.', 'warn');
      return null;
    }
    var pack = buildValidationWorkflowPack(packDef);
    if (!pack.presets.length) {
      setStatus('El flujo no contiene presets validos.', 'warn');
      return null;
    }
    downloadJson('sqx-view-workflow-' + packDef.id + '-pack-v' + PRESET_PACKAGE_VERSION + '.json', pack);
    setStatus('Flujo exportado: ' + packDef.name + ' (' + pack.presets.length + ' presets).', 'ok');
    return pack;
  }

  function importPresetFile(file) {
    if (!file) {
      setStatus('Selecciona un pack JSON de presets.', 'warn');
      return;
    }
    var reader = new FileReader();
    reader.onload = function() {
      var result = importPresetPackageFromText(reader.result || '');
      renderSavedPresets();
      setStatus(result.imported ? 'Pack importado: ' + result.imported + ' presets.' : 'El pack no contiene presets validos.', result.imported ? 'ok' : 'warn');
    };
    reader.onerror = function() {
      setStatus('No se pudo leer el pack de presets.', 'error');
    };
    reader.readAsText(file);
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
    if (byId('vc-profile-list')) {
      byId('vc-profile-list').addEventListener('click', function(event) {
        var loadId = event.target && event.target.dataset ? event.target.dataset.vcProfileLoad : '';
        var saveId = event.target && event.target.dataset ? event.target.dataset.vcProfileSave : '';
        var exportId = event.target && event.target.dataset ? event.target.dataset.vcProfileExport : '';
        if (loadId) loadBuyerProfilePack(loadId);
        if (saveId) saveBuyerProfilePack(saveId);
        if (exportId) exportBuyerProfilePack(exportId);
      });
    }
    if (byId('vc-workflow-pack-list')) {
      byId('vc-workflow-pack-list').addEventListener('click', function(event) {
        var loadId = event.target && event.target.dataset ? event.target.dataset.vcWorkflowLoad : '';
        var saveId = event.target && event.target.dataset ? event.target.dataset.vcWorkflowSave : '';
        var exportId = event.target && event.target.dataset ? event.target.dataset.vcWorkflowExport : '';
        if (loadId) loadValidationWorkflowPack(loadId);
        if (saveId) saveValidationWorkflowPack(saveId);
        if (exportId) exportValidationWorkflowPack(exportId);
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
    renderMetrics();
    bindControls();
    renderBuyerReadyTemplates();
    renderBuyerProfilePacks();
    renderValidationWorkflowPacks();
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
    bindHandoffLinks: bindHandoffLinks,
    buildAllBuyerProfilePacks: buildAllBuyerProfilePacks,
    buildAllValidationWorkflowPacks: buildAllValidationWorkflowPacks,
    buildBuyerReadyTemplatePack: buildBuyerReadyTemplatePack,
    buildBuyerProfilePack: buildBuyerProfilePack,
    buildPresetPackage: buildPresetPackage,
    buildValidationWorkflowPack: buildValidationWorkflowPack,
    buyerProfilePacks: getBuyerProfilePacks,
    buyerReadyTemplates: getBuyerReadyTemplates,
    exportBuyerProfilePack: exportBuyerProfilePack,
    exportValidationWorkflowPack: exportValidationWorkflowPack,
    importPresetPackage: importPresetPackage,
    importPresetPackageFromText: importPresetPackageFromText,
    getSavedPresets: getSavedPresets,
    groupedMetrics: groupedMetrics,
    init: init,
    loadBuyerReadyTemplate: loadBuyerReadyTemplate,
    loadBuyerProfilePack: loadBuyerProfilePack,
    loadValidationWorkflowPack: loadValidationWorkflowPack,
    metrics: METRICS,
    packageType: PRESET_PACKAGE_TYPE,
    packageVersion: PRESET_PACKAGE_VERSION,
    openHandoff: openHandoff,
    previewLines: previewLines,
    renderBuyerReadyTemplates: renderBuyerReadyTemplates,
    renderBuyerProfilePacks: renderBuyerProfilePacks,
    renderValidationWorkflowPacks: renderValidationWorkflowPacks,
    sanitizeInt: sanitizeInt,
    saveBuyerReadyTemplate: saveBuyerReadyTemplate,
    saveBuyerProfilePack: saveBuyerProfilePack,
    saveValidationWorkflowPack: saveValidationWorkflowPack,
    saveCurrentPreset: saveCurrentPreset,
    selectedMetrics: selectedMetrics,
    serializeConfig: serializeConfig,
    setSavedPresets: setSavedPresets,
    storageKey: presetsStorageKey,
    validationWorkflowPacks: getValidationWorkflowPacks
  };

  if (SQX.registerModule) {
    SQX.registerModule('view-creator', SQX.viewCreator);
  }
})(window);

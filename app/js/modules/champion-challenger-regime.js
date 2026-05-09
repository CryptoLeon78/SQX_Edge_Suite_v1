(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  var DEFAULT_THRESHOLDS = {
    minCoverageMonths: 60,
    minRegimeComposite: 0.50,
    flatReturnAbs12m: 0.03,
    riskReturn12m: -0.12,
    maxDrawdown36m: -0.35,
    highVolatility12m: 0.09
  };
  var EGT_V2_THRESHOLDS = {
    direction: 'long_only',
    minBlocksPerRegime: 2,
    long_only: {
      BULL: { pass: 1.5, strong: 2.5 },
      BEAR: { pass: 0.0, strong: 1.0 },
      RANGE: { pass: 0.0, strong: 1.0 }
    },
    long_short: {
      BULL: { pass: 1.0, strong: 2.0 },
      BEAR: { pass: 1.0, strong: 2.0 },
      RANGE: { pass: 0.5, strong: 1.5 }
    }
  };

  function cloneThresholds(overrides) {
    var result = {};
    Object.keys(DEFAULT_THRESHOLDS).forEach(function(key) {
      result[key] = DEFAULT_THRESHOLDS[key];
    });
    Object.keys(overrides || {}).forEach(function(key) {
      if (overrides[key] != null && isFinite(Number(overrides[key]))) {
        result[key] = Number(overrides[key]);
      }
    });
    return result;
  }

  function historicalData() {
    if (SQX.datasets && SQX.datasets.historical) return SQX.datasets.historical() || {};
    return global.SQX_HISTORICAL_DATA || {};
  }

  function scoresData() {
    if (SQX.datasets && SQX.datasets.scores) return SQX.datasets.scores() || {};
    return global.SQX_SCORES_DATA || {};
  }

  function normalizeSymbol(value) {
    return String(value == null ? '' : value).toUpperCase().replace(/[^A-Z0-9]/g, '');
  }

  function symbolIndex() {
    var index = {};
    Object.keys(historicalData()).forEach(function(symbol) {
      index[normalizeSymbol(symbol)] = symbol;
    });
    Object.keys(scoresData()).forEach(function(symbol) {
      index[normalizeSymbol(symbol)] = index[normalizeSymbol(symbol)] || symbol;
    });
    return index;
  }

  function resolveSymbol(value) {
    var normalized = normalizeSymbol(value);
    var index = symbolIndex();
    return {
      input: value,
      normalized: normalized,
      symbol: index[normalized] || normalized || ''
    };
  }

  function safeValues(series) {
    return ((series && series.v) || []).map(function(value) {
      return Number(value);
    }).filter(function(value) {
      return isFinite(value) && value > 0;
    });
  }

  function pctReturn(values, months) {
    if (!values || values.length <= months) return null;
    var last = values[values.length - 1];
    var base = values[values.length - 1 - months];
    if (!base) return null;
    return (last / base) - 1;
  }

  function maxDrawdown(values, months) {
    var source = values || [];
    var windowValues = months && source.length > months ? source.slice(source.length - months) : source.slice();
    if (!windowValues.length) return null;
    var peak = windowValues[0];
    var worst = 0;
    windowValues.forEach(function(value) {
      if (value > peak) peak = value;
      if (peak > 0) {
        var dd = (value / peak) - 1;
        if (dd < worst) worst = dd;
      }
    });
    return worst;
  }

  function monthlyVolatility(values, months) {
    var source = values || [];
    var windowValues = months && source.length > months + 1 ? source.slice(source.length - months - 1) : source.slice();
    var returns = [];
    for (var i = 1; i < windowValues.length; i += 1) {
      if (windowValues[i - 1]) returns.push((windowValues[i] / windowValues[i - 1]) - 1);
    }
    if (!returns.length) return null;
    var avg = returns.reduce(function(acc, value) { return acc + value; }, 0) / returns.length;
    var variance = returns.reduce(function(acc, value) {
      return acc + Math.pow(value - avg, 2);
    }, 0) / returns.length;
    return Math.sqrt(variance);
  }

  function scoreForSymbol(symbol) {
    var scores = scoresData()[symbol] || {};
    var regime = scores.regimen || {};
    var metrics = scores.metrics && scores.metrics.regimen || {};
    return {
      objective: regime.objective || null,
      composite: regime.composite_score != null ? Number(regime.composite_score) : null,
      scope: regime.scope || null,
      metrics: metrics
    };
  }

  function cloneRegimeThresholds(overrides) {
    var source = overrides || {};
    var result = {
      direction: source.direction || EGT_V2_THRESHOLDS.direction,
      minBlocksPerRegime: source.minBlocksPerRegime || source.min_blocks_per_regime || EGT_V2_THRESHOLDS.minBlocksPerRegime,
      long_only: {
        BULL: Object.assign({}, EGT_V2_THRESHOLDS.long_only.BULL, source.long_only && source.long_only.BULL),
        BEAR: Object.assign({}, EGT_V2_THRESHOLDS.long_only.BEAR, source.long_only && source.long_only.BEAR),
        RANGE: Object.assign({}, EGT_V2_THRESHOLDS.long_only.RANGE, source.long_only && source.long_only.RANGE)
      },
      long_short: {
        BULL: Object.assign({}, EGT_V2_THRESHOLDS.long_short.BULL, source.long_short && source.long_short.BULL),
        BEAR: Object.assign({}, EGT_V2_THRESHOLDS.long_short.BEAR, source.long_short && source.long_short.BEAR),
        RANGE: Object.assign({}, EGT_V2_THRESHOLDS.long_short.RANGE, source.long_short && source.long_short.RANGE)
      }
    };
    if (result.direction !== 'long_only' && result.direction !== 'long_short') result.direction = 'long_only';
    result.minBlocksPerRegime = Math.max(1, Number(result.minBlocksPerRegime) || EGT_V2_THRESHOLDS.minBlocksPerRegime);
    return result;
  }

  function normalizeRegimeGroup(value) {
    var text = String(value == null ? '' : value).toUpperCase();
    if (text.indexOf('BULL') !== -1) return 'BULL';
    if (text.indexOf('BEAR') !== -1) return 'BEAR';
    if (text.indexOf('RANGE') !== -1 || text.indexOf('FLAT') !== -1 || text.indexOf('SIDE') !== -1) return 'RANGE';
    return null;
  }

  function finiteNumber(value) {
    return typeof value === 'number' && isFinite(value);
  }

  function average(values) {
    if (!values.length) return null;
    return values.reduce(function(acc, value) { return acc + value; }, 0) / values.length;
  }

  function variance(values, mean) {
    if (!values.length || mean == null) return null;
    return values.reduce(function(acc, value) { return acc + Math.pow(value - mean, 2); }, 0) / values.length;
  }

  function metricValueForBlock(oosRecord, block, metricName) {
    var metrics = oosRecord && oosRecord.metrics_by_block && oosRecord.metrics_by_block[block] || {};
    var normalized = String(metricName == null ? '' : metricName).trim().toLowerCase();
    var keys = Object.keys(metrics);
    for (var i = 0; i < keys.length; i += 1) {
      if (keys[i].trim().toLowerCase() === normalized) return metrics[keys[i]];
    }
    return null;
  }

  function primaryOosValues(oosRecord) {
    var metric = oosRecord && oosRecord.primary_metric;
    var blocks = Object.keys(oosRecord && oosRecord.metrics_by_block || {})
      .map(function(block) { return parseInt(block, 10); })
      .filter(function(block) { return isFinite(block); })
      .sort(function(a, b) { return a - b; });
    return blocks.map(function(block) {
      return { block: block, value: metricValueForBlock(oosRecord, block, metric) };
    }).filter(function(item) {
      return finiteNumber(item.value);
    });
  }

  function tradesForBlock(oosRecord, block) {
    var names = ['# trades', '# of trades', '# of Trades', 'Trades', 'Number of trades'];
    for (var i = 0; i < names.length; i += 1) {
      var value = metricValueForBlock(oosRecord, block, names[i]);
      if (finiteNumber(value)) return value;
    }
    return null;
  }

  function emptyEgtV2(verdict, warnings, thresholds) {
    return {
      verdict: verdict || 'UNKNOWN',
      label: 'UNKNOWN',
      direction: thresholds.direction,
      dominant_regime: null,
      dominant_avg: null,
      stats_by_regime: {
        BULL: { count: 0, avg: null, min: null },
        BEAR: { count: 0, avg: null, min: null },
        RANGE: { count: 0, avg: null, min: null }
      },
      pass_by_regime: {},
      strong_by_regime: {},
      sufficient_by_regime: {},
      failed_regimes: [],
      insufficient_regimes: [],
      evaluated_regimes: [],
      worst_regime_avg: null,
      variance_across_regimes: null,
      thresholds: thresholds[thresholds.direction] || thresholds.long_only,
      warnings: warnings || []
    };
  }

  function assessEgtV2(oosRecord, regimeBlocks, options) {
    var opts = options || {};
    var thresholds = cloneRegimeThresholds(opts.thresholds);
    var directionThresholds = thresholds[thresholds.direction] || thresholds.long_only;
    var warnings = [];
    if (!oosRecord || !oosRecord.metrics_by_block) {
      return emptyEgtV2('UNKNOWN', [{ code: 'egt_v2_oos_missing' }], thresholds);
    }
    if (!Array.isArray(regimeBlocks) || !regimeBlocks.length) {
      return emptyEgtV2('UNKNOWN', [{ code: 'egt_v2_regime_blocks_missing' }], thresholds);
    }

    var oosValues = primaryOosValues(oosRecord);
    if (!oosValues.length) return emptyEgtV2('UNKNOWN', [{ code: 'egt_v2_oos_primary_metric_missing' }], thresholds);
    var byBlock = {};
    oosValues.forEach(function(item) { byBlock[item.block] = item.value; });

    var groups = { BULL: [], BEAR: [], RANGE: [] };
    var skippedDueToTrades = [];
    regimeBlocks.forEach(function(blockInfo, index) {
      var block = blockInfo.block || blockInfo.idx || blockInfo.oos_block || index + 1;
      var group = normalizeRegimeGroup(blockInfo.group || blockInfo.regime || blockInfo.label);
      if (!group) return;
      var value = byBlock[block];
      if (!finiteNumber(value)) return;
      if (opts.minTradesPerBlock != null) {
        var trades = tradesForBlock(oosRecord, block);
        if (!finiteNumber(trades) || trades < Number(opts.minTradesPerBlock)) {
          skippedDueToTrades.push(block);
          return;
        }
      }
      groups[group].push(value);
    });

    if (skippedDueToTrades.length) {
      warnings.push({ code: 'egt_v2_blocks_skipped_min_trades', blocks: skippedDueToTrades.slice() });
    }

    var stats = {};
    ['BULL', 'BEAR', 'RANGE'].forEach(function(regime) {
      var values = groups[regime];
      stats[regime] = {
        count: values.length,
        avg: average(values),
        min: values.length ? Math.min.apply(Math, values) : null
      };
    });

    var regimesWithData = ['BULL', 'BEAR', 'RANGE'].filter(function(regime) {
      return stats[regime].count > 0 && stats[regime].avg != null;
    });
    if (!regimesWithData.length) return emptyEgtV2('UNKNOWN', [{ code: 'egt_v2_no_regime_overlap' }].concat(warnings), thresholds);

    var sufficient = {};
    var passed = {};
    var strong = {};
    ['BULL', 'BEAR', 'RANGE'].forEach(function(regime) {
      sufficient[regime] = stats[regime].count >= thresholds.minBlocksPerRegime;
      if (!sufficient[regime] || stats[regime].avg == null) {
        passed[regime] = null;
        strong[regime] = null;
        return;
      }
      passed[regime] = stats[regime].avg >= directionThresholds[regime].pass;
      strong[regime] = stats[regime].avg >= directionThresholds[regime].strong;
    });

    var evaluated = ['BULL', 'BEAR', 'RANGE'].filter(function(regime) { return sufficient[regime]; });
    var insufficient = regimesWithData.filter(function(regime) { return !sufficient[regime]; });
    var failed = evaluated.filter(function(regime) { return passed[regime] === false; });
    var strongRegimes = evaluated.filter(function(regime) { return strong[regime] === true; });
    var dominant = regimesWithData.reduce(function(best, regime) {
      if (!best) return regime;
      if (stats[regime].count > stats[best].count) return regime;
      if (stats[regime].count === stats[best].count && stats[regime].avg > stats[best].avg) return regime;
      return best;
    }, null);

    var verdict = 'INSUFFICIENT';
    if (!evaluated.length) verdict = 'INSUFFICIENT';
    else if (failed.length) verdict = 'RISK';
    else if (strong[dominant]) verdict = 'STRONG';
    else if (strongRegimes.length) verdict = 'COMPLIANT';
    else verdict = 'DEFENSIVE';

    var evalAvgs = evaluated.map(function(regime) { return stats[regime].avg; }).filter(finiteNumber);
    var mean = average(evalAvgs);
    var legacyLabel = (verdict === 'STRONG' || verdict === 'COMPLIANT') ? 'COMPLIANT'
      : verdict === 'RISK' ? 'RISK'
      : verdict === 'UNKNOWN' ? 'UNKNOWN'
      : 'FLAT';

    return {
      verdict: verdict,
      label: legacyLabel,
      direction: thresholds.direction,
      dominant_regime: dominant,
      dominant_avg: dominant ? stats[dominant].avg : null,
      stats_by_regime: stats,
      pass_by_regime: passed,
      strong_by_regime: strong,
      sufficient_by_regime: sufficient,
      failed_regimes: failed,
      insufficient_regimes: insufficient,
      evaluated_regimes: evaluated,
      worst_regime_avg: evalAvgs.length ? Math.min.apply(Math, evalAvgs) : null,
      variance_across_regimes: variance(evalAvgs, mean),
      thresholds: directionThresholds,
      warnings: warnings
    };
  }

  function classify(evidence, thresholds) {
    if (evidence.coverage_months < thresholds.minCoverageMonths) return 'UNKNOWN';
    if (evidence.regime_score == null) return 'UNKNOWN';
    if (
      evidence.regime_score < thresholds.minRegimeComposite ||
      evidence.return_12m <= thresholds.riskReturn12m ||
      evidence.max_drawdown_36m <= thresholds.maxDrawdown36m ||
      evidence.volatility_12m >= thresholds.highVolatility12m
    ) {
      return 'RISK';
    }
    if (Math.abs(evidence.return_12m || 0) <= thresholds.flatReturnAbs12m) return 'FLAT';
    return 'COMPLIANT';
  }

  function reasonsFor(evidence, thresholds) {
    var reasons = [];
    if (evidence.coverage_months < thresholds.minCoverageMonths) reasons.push('coverage_below_threshold');
    if (evidence.regime_score == null) reasons.push('regime_score_missing');
    else if (evidence.regime_score < thresholds.minRegimeComposite) reasons.push('regime_score_below_threshold');
    if (evidence.return_12m != null && evidence.return_12m <= thresholds.riskReturn12m) reasons.push('recent_return_risk');
    if (evidence.max_drawdown_36m != null && evidence.max_drawdown_36m <= thresholds.maxDrawdown36m) reasons.push('drawdown_risk');
    if (evidence.volatility_12m != null && evidence.volatility_12m >= thresholds.highVolatility12m) reasons.push('volatility_risk');
    if (evidence.label === 'FLAT') reasons.push('flat_recent_trend');
    return reasons;
  }

  function assessSymbol(symbolInput, options) {
    var thresholds = cloneThresholds(options && options.thresholds);
    var resolved = resolveSymbol(symbolInput);
    var series = historicalData()[resolved.symbol];
    var values = safeValues(series);
    var score = scoreForSymbol(resolved.symbol);
    var evidence = {
      symbol: resolved.symbol,
      input_symbol: symbolInput,
      coverage_months: values.length,
      start: series && series.start || null,
      return_12m: pctReturn(values, 12),
      return_36m: pctReturn(values, 36),
      max_drawdown_36m: maxDrawdown(values, 36),
      volatility_12m: monthlyVolatility(values, 12),
      regime_objective: score.objective,
      regime_score: score.composite,
      regime_scope: score.scope,
      regime_metrics: score.metrics,
      thresholds: thresholds
    };
    evidence.label = classify(evidence, thresholds);
    evidence.reasons = reasonsFor(evidence, thresholds);
    evidence.ok = evidence.label === 'COMPLIANT';
    return evidence;
  }

  function assessCandidate(candidate, options) {
    var metrics = candidate && candidate.normalized_metrics || {};
    return assessSymbol(candidate && candidate.symbol || metrics.symbol || '', options);
  }

  function formatPercent(value) {
    if (value == null || !isFinite(Number(value))) return '-';
    return Math.round(Number(value) * 100) + '%';
  }

  function formatSignedPercent(value) {
    if (value == null || !isFinite(Number(value))) return '-';
    var rounded = Math.round(Number(value) * 100);
    return (rounded > 0 ? '+' : '') + rounded + '%';
  }

  function evidenceSummary(evidence) {
    if (!evidence || !evidence.symbol) return 'UNKNOWN - sin simbolo';
    if (evidence.label === 'UNKNOWN') return 'UNKNOWN - cobertura insuficiente';
    return evidence.label + ' | Reg ' + (evidence.regime_objective || '-') + ' | 12m ' + formatSignedPercent(evidence.return_12m);
  }

  SQX.championChallengerRegime = SQX.championChallengerRegime || {
    defaultThresholds: DEFAULT_THRESHOLDS,
    egtV2Thresholds: EGT_V2_THRESHOLDS,
    assessEgtV2: assessEgtV2,
    assessCandidate: assessCandidate,
    assessSymbol: assessSymbol,
    evidenceSummary: evidenceSummary,
    formatPercent: formatPercent,
    formatSignedPercent: formatSignedPercent,
    normalizeRegimeGroup: normalizeRegimeGroup,
    maxDrawdown: maxDrawdown,
    monthlyVolatility: monthlyVolatility,
    normalizeSymbol: normalizeSymbol,
    pctReturn: pctReturn,
    resolveSymbol: resolveSymbol
  };

  if (SQX.registerModule) {
    SQX.registerModule('champion-challenger-regime', SQX.championChallengerRegime);
  }
})(window);

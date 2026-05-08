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
    assessCandidate: assessCandidate,
    assessSymbol: assessSymbol,
    evidenceSummary: evidenceSummary,
    formatPercent: formatPercent,
    formatSignedPercent: formatSignedPercent,
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

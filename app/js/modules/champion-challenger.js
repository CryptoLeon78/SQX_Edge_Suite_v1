(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  var IDS = {
    champion: 'cvc-champion-input',
    challenger: 'cvc-challenger-input',
    oos: 'cvc-oos-input',
    run: 'cvc-run-btn',
    sample: 'cvc-sample-btn',
    clear: 'cvc-clear-btn',
    status: 'cvc-status',
    summary: 'cvc-summary',
    ranking: 'cvc-ranking',
    empty: 'cvc-empty',
    oosSummary: 'cvc-oos-summary',
    candidateCount: 'cvc-candidate-count',
    readyCount: 'cvc-ready-count',
    oosReadyCount: 'cvc-oos-ready-count',
    regimeReadyCount: 'cvc-regime-ready-count'
  };

  function getCore() {
    return SQX.championChallengerCore || null;
  }

  function getUi() {
    return SQX.ui || {};
  }

  function byId(id, doc) {
    var target = doc || global.document;
    return target && target.getElementById ? target.getElementById(id) : null;
  }

  function textValue(id, doc) {
    var node = byId(id, doc);
    return node ? node.value || '' : '';
  }

  function setValue(id, value, doc) {
    var node = byId(id, doc);
    if (node) node.value = value == null ? '' : String(value);
  }

  function setText(id, value, doc) {
    var node = byId(id, doc);
    if (node) node.textContent = value == null ? '' : String(value);
  }

  function setHtml(id, html, doc) {
    var node = byId(id, doc);
    if (node) node.innerHTML = html == null ? '' : String(html);
  }

  function setDisplay(id, display, doc) {
    var node = byId(id, doc);
    if (node) node.style.display = display;
  }

  function setStatus(message, tone, doc) {
    var node = byId(IDS.status, doc);
    if (!node) return;
    node.textContent = message || '';
    node.classList.remove('is-ok', 'is-warn', 'is-error');
    if (tone) node.classList.add('is-' + tone);
  }

  function fmt(value, digits) {
    if (value == null || value === '' || !isFinite(Number(value))) return '-';
    var places = digits == null ? 2 : digits;
    return Number(value).toFixed(places);
  }

  function pct(value) {
    if (value == null || !isFinite(Number(value))) return '-';
    return Math.round(Number(value) * 100) + '%';
  }

  function keyFor(value) {
    return String(value == null ? '' : value).trim().toLowerCase();
  }

  function errorText(error) {
    if (typeof error === 'string') return error;
    if (!error || !error.code) return 'unknown_error';
    var suffix = error.field ? ':' + error.field : '';
    if (error.rowNumber) suffix += ' fila ' + error.rowNumber;
    return error.code + suffix;
  }

  function sampleData() {
    return {
      champion: [
        'Strategy Name;Symbol;Profit factor;Return/Drawdown;# trades;Drawdown %;Filters Result',
        'Champion Base;EURUSD;1.50;4.00;200;5.0;PASSED'
      ].join('\n'),
      challenger: [
        'Strategy Name;Symbol;Profit factor;Return/Drawdown;# trades;Drawdown %;Filters Result;Entry indicators',
        'Challenger A;EURUSD;1.62;3.95;180;5.2;PASSED;EMA RSI',
        'Challenger B;EURUSD;1.55;4.25;130;4.8;PASSED;MACD',
        'Challenger C;EURUSD;1.70;3.60;260;7.1;FAILED;Bollinger'
      ].join('\n'),
      oos: [
        'Strategy Name;Symbol;CAGR/Max DD (OOS1);Profit Factor (OOS1);Worst Year Profit (OOS1);CAGR/Max DD (OOS2);Profit Factor (OOS2);Worst Year Profit (OOS2);CAGR/Max DD (OOS3);Profit Factor (OOS3);Worst Year Profit (OOS3)',
        'Challenger A;EURUSD;2.4;1.7;120;1.8;1.5;80;1.1;1.4;40',
        'Challenger B;EURUSD;1.2;1.3;60;-0.4;1.1;-30;0.8;1.2;20',
        'Challenger C;EURUSD;2.0;1.6;90;1.5;1.5;70'
      ].join('\n')
    };
  }

  function parseInputs(doc) {
    var core = getCore();
    if (!core) {
      return { ok: false, errors: ['champion_challenger_core_missing'], warnings: [], rankings: [] };
    }

    var champion = core.parseStrategyCsv(textValue(IDS.champion, doc), { role: 'champion' });
    var challengers = core.parseStrategyCsv(textValue(IDS.challenger, doc), { role: 'challenger' });
    var oosText = textValue(IDS.oos, doc);
    var oos = oosText.trim() ? core.parseOosCsv(oosText) : null;
    var errors = [];
    var warnings = [];

    if (!champion.ok) errors = errors.concat(champion.errors.map(errorText));
    if (!challengers.ok) errors = errors.concat(challengers.errors.map(errorText));
    if (oos && !oos.ok) errors = errors.concat(oos.errors.map(errorText));

    warnings = warnings
      .concat((champion.warnings || []).map(errorText))
      .concat((challengers.warnings || []).map(errorText))
      .concat(oos ? (oos.warnings || []).map(errorText) : []);

    if (errors.length) {
      return { ok: false, champion: champion, challengers: challengers, oos: oos, errors: errors, warnings: warnings, rankings: [] };
    }

    return {
      ok: true,
      champion: champion,
      challengers: challengers,
      oos: oos,
      errors: [],
      warnings: warnings,
      rankings: buildRankings(champion.records[0], challengers.records, oos)
    };
  }

  function isStableOos(record) {
    return !!record &&
      record.stable_enough &&
      record.positive_block_ratio != null &&
      record.positive_block_ratio >= 0.67 &&
      !record.has_negative_worst_year &&
      record.max_negative_streak <= 1;
  }

  function buildRankings(champion, challengers, oos) {
    var core = getCore();
    var regime = SQX.championChallengerRegime || null;
    var oosByName = {};
    if (oos && oos.records) {
      oos.records.forEach(function(record) {
        oosByName[keyFor(record.strategy_name)] = record;
      });
    }

    return core.rankCandidates(champion, challengers, {
      enableDrawdownCheck: true,
      enableForwardCheck: true
    }).map(function(item) {
      var oosRecord = oosByName[keyFor(item.strategy_name)] || null;
      item.oos = oosRecord;
      item.oos_stable = isStableOos(oosRecord);
      item.regime_evidence = regime && regime.assessCandidate ? regime.assessCandidate(item) : null;
      return item;
    }).sort(function(a, b) {
      if (a.formal_fail_count !== b.formal_fail_count) return a.formal_fail_count - b.formal_fail_count;
      if (a.oos_stable !== b.oos_stable) return a.oos_stable ? -1 : 1;
      var ratioA = a.oos && a.oos.positive_block_ratio != null ? a.oos.positive_block_ratio : -1;
      var ratioB = b.oos && b.oos.positive_block_ratio != null ? b.oos.positive_block_ratio : -1;
      if (ratioA !== ratioB) return ratioB - ratioA;
      return (b.normalized_metrics.profit_factor || 0) - (a.normalized_metrics.profit_factor || 0);
    });
  }

  function renderMetric(label, value) {
    var core = getCore();
    return '<div class="cvc-metric"><span>' + core.escapeHtml(label) + '</span><strong>' + core.escapeHtml(value) + '</strong></div>';
  }

  function renderChecks(checks) {
    var core = getCore();
    return (checks || []).map(function(check) {
      var cls = check.passed ? 'is-pass' : 'is-fail';
      return '<span class="cvc-check ' + cls + '">' + core.escapeHtml(check.label) + '</span>';
    }).join('');
  }

  function renderRow(item, index) {
    var core = getCore();
    var regime = SQX.championChallengerRegime || null;
    var metrics = item.normalized_metrics || {};
    var oos = item.oos;
    var oosText = oos
      ? 'OOS ' + pct(oos.positive_block_ratio) + ' positivo, ' + (oos.stable_enough ? oos.block_count + ' bloques' : 'bloques insuficientes')
      : 'Sin OOS asociado';
    var regimeText = regime && regime.evidenceSummary
      ? regime.evidenceSummary(item.regime_evidence)
      : 'UNKNOWN - sin evidencia';
    var statusClass = item.formal_fail_count === 0 ? 'is-pass' : 'is-review';
    if (item.oos_stable) statusClass += ' is-stable';
    if (item.regime_evidence && item.regime_evidence.label) statusClass += ' is-regime-' + item.regime_evidence.label.toLowerCase();

    return [
      '<article class="cvc-result-row ' + statusClass + '">',
      '<div class="cvc-rank">#' + (index + 1) + '</div>',
      '<div class="cvc-result-main">',
      '<div class="cvc-result-title">',
      '<strong>' + item.safe_strategy_name + '</strong>',
      '<span>' + core.escapeHtml(item.symbol || metrics.symbol || '') + '</span>',
      '</div>',
      '<div class="cvc-result-checks">' + renderChecks(item.checks) + '</div>',
      '</div>',
      '<div class="cvc-result-metrics">',
      renderMetric('PF', fmt(metrics.profit_factor, 2)),
      renderMetric('Ret/DD', fmt(metrics.return_drawdown, 2)),
      renderMetric('Trades', fmt(metrics.trades, 0)),
      renderMetric('OOS', core.escapeHtml(oosText)),
      renderMetric('EGT', core.escapeHtml(regimeText)),
      '</div>',
      '</article>'
    ].join('');
  }

  function renderSummary(model, doc) {
    var total = model.rankings.length;
    var ready = model.rankings.filter(function(item) { return item.formal_fail_count === 0; }).length;
    var stable = model.rankings.filter(function(item) { return item.oos_stable; }).length;
    var regimeReady = model.rankings.filter(function(item) {
      return item.regime_evidence && item.regime_evidence.label === 'COMPLIANT';
    }).length;
    var warnings = model.warnings.length;

    setText(IDS.candidateCount, total, doc);
    setText(IDS.readyCount, ready, doc);
    setText(IDS.oosReadyCount, stable, doc);
    setText(IDS.regimeReadyCount, regimeReady, doc);
    setHtml(IDS.summary, [
      renderMetric('Candidatas evaluadas', total),
      renderMetric('Sin fallos formales', ready),
      renderMetric('OOS estable', stable),
      renderMetric('EGT compliant', regimeReady),
      renderMetric('Avisos de datos', warnings)
    ].join(''), doc);
    setText(IDS.oosSummary, stable + ' OOS estable | ' + regimeReady + ' EGT compliant.', doc);
  }

  function renderEmpty(doc) {
    setText(IDS.candidateCount, 0, doc);
    setText(IDS.readyCount, 0, doc);
    setText(IDS.oosReadyCount, 0, doc);
    setText(IDS.regimeReadyCount, 0, doc);
    setHtml(IDS.summary, '', doc);
    setHtml(IDS.ranking, '', doc);
    setText(IDS.oosSummary, 'OOS pendiente.', doc);
    setDisplay(IDS.empty, '', doc);
  }

  function renderResults(model, doc) {
    if (!model.ok) {
      renderEmpty(doc);
      setStatus('Revisa los datos: ' + model.errors.slice(0, 4).join(', '), 'error', doc);
      return model;
    }

    renderSummary(model, doc);
    setDisplay(IDS.empty, model.rankings.length ? 'none' : '', doc);
    setHtml(IDS.ranking, model.rankings.map(renderRow).join(''), doc);

    var tone = model.warnings.length ? 'warn' : 'ok';
    var message = model.rankings.length
      ? 'Comparacion lista. Ranking generado con reglas formales y OOS.'
      : 'Comparacion lista, sin candidatas.';
    if (model.warnings.length) message += ' Avisos: ' + model.warnings.slice(0, 3).join(', ');
    setStatus(message, tone, doc);
    return model;
  }

  function evaluate(options) {
    var doc = options && options.document ? options.document : global.document;
    return renderResults(parseInputs(doc), doc);
  }

  function loadSample(options) {
    var doc = options && options.document ? options.document : global.document;
    var sample = sampleData();
    setValue(IDS.champion, sample.champion, doc);
    setValue(IDS.challenger, sample.challenger, doc);
    setValue(IDS.oos, sample.oos, doc);
    return evaluate({ document: doc });
  }

  function clear(options) {
    var doc = options && options.document ? options.document : global.document;
    setValue(IDS.champion, '', doc);
    setValue(IDS.challenger, '', doc);
    setValue(IDS.oos, '', doc);
    renderEmpty(doc);
    setStatus('Esperando datos para comparar.', '', doc);
  }

  function init(options) {
    var doc = options && options.document ? options.document : global.document;
    var ui = getUi();
    if (!byId(IDS.run, doc)) return false;

    if (ui.bindClick) {
      ui.bindClick(byId(IDS.run, doc), function() { evaluate({ document: doc }); });
      ui.bindClick(byId(IDS.sample, doc), function() { loadSample({ document: doc }); });
      ui.bindClick(byId(IDS.clear, doc), function() { clear({ document: doc }); });
    } else {
      byId(IDS.run, doc).addEventListener('click', function() { evaluate({ document: doc }); });
      byId(IDS.sample, doc).addEventListener('click', function() { loadSample({ document: doc }); });
      byId(IDS.clear, doc).addEventListener('click', function() { clear({ document: doc }); });
    }
    renderEmpty(doc);
    return true;
  }

  SQX.championChallenger = SQX.championChallenger || {
    ids: IDS,
    buildRankings: buildRankings,
    clear: clear,
    evaluate: evaluate,
    init: init,
    parseInputs: parseInputs,
    sampleData: sampleData
  };

  if (SQX.registerModule) {
    SQX.registerModule('champion-challenger', SQX.championChallenger);
  }
})(window);

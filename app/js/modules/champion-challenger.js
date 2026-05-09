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
    exportReview: 'cvc-export-btn',
    handoff: 'cvc-handoff-btn',
    status: 'cvc-status',
    summary: 'cvc-summary',
    ranking: 'cvc-ranking',
    empty: 'cvc-empty',
    oosSummary: 'cvc-oos-summary',
    handoffPreview: 'cvc-handoff-preview',
    candidateCount: 'cvc-candidate-count',
    readyCount: 'cvc-ready-count',
    oosReadyCount: 'cvc-oos-ready-count',
    regimeReadyCount: 'cvc-regime-ready-count',
    healthFilter: 'cvc-filter-health-ok',
    egtV2Filter: 'cvc-filter-egt-v2-ok'
  };

  var lastModel = null;

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
        'Strategy Name;Symbol;CAGR/Max DD (OOS1);Net Profit (OOS1);Trades (OOS1);Worst Year Profit (OOS1);CAGR/Max DD (OOS2);Net Profit (OOS2);Trades (OOS2);Worst Year Profit (OOS2);CAGR/Max DD (OOS3);Net Profit (OOS3);Trades (OOS3);Worst Year Profit (OOS3);CAGR/Max DD (OOS4);Net Profit (OOS4);Trades (OOS4);Worst Year Profit (OOS4);CAGR/Max DD (OOS5);Net Profit (OOS5);Trades (OOS5);Worst Year Profit (OOS5);CAGR/Max DD (OOS6);Net Profit (OOS6);Trades (OOS6);Worst Year Profit (OOS6)',
        'Challenger A;EURUSD;3.0;100;80;120;2.8;90;82;110;3.1;95;84;115;2.9;100;86;105;3.2;110;88;120;3.0;115;90;125',
        'Challenger B;EURUSD;1.4;80;60;60;-0.4;-30;42;-30;1.0;20;52;20;0.8;15;48;15;1.1;30;55;30;0.7;10;44;10',
        'Challenger C;EURUSD;1.8;90;90;90;1.7;80;88;85;0.3;-60;40;-15;0.4;20;42;20;0.2;10;38;10;0.3;5;36;5'
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
      item.temporal_health = core.computeTemporalHealth && oosRecord ? core.computeTemporalHealth(oosRecord) : null;
      item.egt_v2 = buildEgtV2Evidence(item, oosRecord, regime);
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

  function buildEgtV2Evidence(item, oosRecord, regime) {
    if (!regime || !regime.assessEgtV2 || !oosRecord) return null;
    var blocks = null;
    if (regime.buildRegimeBlocksForSymbol) {
      blocks = regime.buildRegimeBlocksForSymbol(item.symbol || (item.normalized_metrics || {}).symbol, oosRecord.block_count);
    }
    return regime.assessEgtV2(oosRecord, blocks && blocks.blocks ? blocks.blocks : [], {
      thresholds: { direction: 'long_only' }
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

  function chipClass(prefix, value) {
    return prefix + '-' + String(value || 'unknown').toLowerCase().replace(/[^a-z0-9]+/g, '-');
  }

  function renderEvidenceChips(item) {
    var core = getCore();
    var health = item.temporal_health;
    var egt = item.egt_v2;
    var healthLabel = health ? health.status : 'unknown';
    var egtLabel = egt ? egt.verdict : 'UNKNOWN';
    var healthTitle = health
      ? 'Peak OOS' + (health.peak_block || '-') + ' | DD cierre ' + pct(health.dd_at_close) + ' | Recovery ' + pct(health.recovery_index)
      : 'Temporal Health pendiente';
    var egtTitle = egt
      ? 'Dominante ' + (egt.dominant_regime || '-') + ' | Fallan ' + ((egt.failed_regimes || []).join(', ') || '-') + ' | Insuf ' + ((egt.insufficient_regimes || []).join(', ') || '-')
      : 'EGT v2 pendiente';
    return [
      '<div class="cvc-evidence-chips">',
      '<span class="cvc-evidence-chip ' + chipClass('health', healthLabel) + '" title="' + core.escapeHtml(healthTitle) + '">Health ' + core.escapeHtml(healthLabel) + '</span>',
      '<span class="cvc-evidence-chip ' + chipClass('egt-v2', egtLabel) + '" title="' + core.escapeHtml(egtTitle) + '">EGT v2 ' + core.escapeHtml(egtLabel) + '</span>',
      '</div>'
    ].join('');
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
      renderEvidenceChips(item),
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

  function healthOk(item) {
    return !!(item.temporal_health && item.temporal_health.pass_all);
  }

  function egtV2Ok(item) {
    var verdict = item.egt_v2 && item.egt_v2.verdict;
    return verdict === 'STRONG' || verdict === 'COMPLIANT' || verdict === 'DEFENSIVE';
  }

  function filterModelRankings(model, doc) {
    var healthOnly = byId(IDS.healthFilter, doc) && byId(IDS.healthFilter, doc).checked;
    var egtOnly = byId(IDS.egtV2Filter, doc) && byId(IDS.egtV2Filter, doc).checked;
    return (model.rankings || []).filter(function(item) {
      if (healthOnly && !healthOk(item)) return false;
      if (egtOnly && !egtV2Ok(item)) return false;
      return true;
    });
  }

  function roundMetric(value, digits) {
    if (value == null || !isFinite(Number(value))) return null;
    var factor = Math.pow(10, digits == null ? 4 : digits);
    return Math.round(Number(value) * factor) / factor;
  }

  function compactChecks(checks) {
    return (checks || []).map(function(check) {
      return {
        code: check.code || '',
        label: check.label || '',
        passed: !!check.passed,
        severity: check.severity || ''
      };
    });
  }

  function compactOos(oos) {
    if (!oos) return null;
    return {
      block_count: oos.block_count || 0,
      positive_block_ratio: roundMetric(oos.positive_block_ratio, 4),
      max_negative_streak: oos.max_negative_streak || 0,
      has_negative_worst_year: !!oos.has_negative_worst_year,
      stable_enough: !!oos.stable_enough,
      primary_metric: oos.primary_metric || 'cagr_max_dd',
      average_primary_metric: roundMetric(oos.average_primary_metric, 4),
      min_primary_metric: roundMetric(oos.min_primary_metric, 4),
      max_primary_metric: roundMetric(oos.max_primary_metric, 4),
      decay_ratio: roundMetric(oos.decay_ratio, 4)
    };
  }

  function compactRegime(evidence) {
    if (!evidence) return null;
    return {
      symbol: evidence.symbol || '',
      label: evidence.label || 'UNKNOWN',
      reason: evidence.reason || '',
      monthly_return: roundMetric(evidence.monthly_return, 4),
      monthly_volatility: roundMetric(evidence.monthly_volatility, 4),
      max_drawdown: roundMetric(evidence.max_drawdown, 4),
      composite_score: roundMetric(evidence.composite_score, 4),
      sma200_persistence_bars: evidence.sma200_persistence_bars == null ? null : Number(evidence.sma200_persistence_bars)
    };
  }

  function compactCandidate(item, index) {
    var metrics = item.normalized_metrics || {};
    return {
      rank: index + 1,
      strategy_name: item.strategy_name || '',
      symbol: item.symbol || metrics.symbol || '',
      formal_fail_count: item.formal_fail_count || 0,
      passed_formal_checks: (item.checks || []).filter(function(check) { return check.passed; }).length,
      failed_formal_checks: (item.checks || []).filter(function(check) { return !check.passed; }).length,
      checks: compactChecks(item.checks),
      failure_reasons: (item.failures || []).slice(),
      metrics: {
        profit_factor: roundMetric(metrics.profit_factor, 4),
        return_drawdown: roundMetric(metrics.return_drawdown, 4),
        trades: roundMetric(metrics.trades, 0),
        drawdown_pct: roundMetric(metrics.drawdown_pct, 4)
      },
      oos: compactOos(item.oos),
      oos_stable: !!item.oos_stable,
      regime: compactRegime(item.regime_evidence)
    };
  }

  function buildReviewExport(model, options) {
    var source = model && model.rankings ? model : lastModel;
    var generatedAt = options && options.generatedAt ? options.generatedAt : new Date().toISOString();
    var rankings = source && source.rankings ? source.rankings : [];
    var ready = rankings.filter(function(item) { return item.formal_fail_count === 0; }).length;
    var stable = rankings.filter(function(item) { return item.oos_stable; }).length;
    var regimeReady = rankings.filter(function(item) {
      return item.regime_evidence && item.regime_evidence.label === 'COMPLIANT';
    }).length;

    return {
      type: 'sqx-edge.champion-challenger-review',
      version: 1,
      generated_at: generatedAt,
      source: 'SQX Edge Champion vs Challenger',
      redaction: {
        raw_csv: 'excluded',
        local_storage: 'not_used',
        remote_calls: 'none'
      },
      summary: {
        ok: !!(source && source.ok),
        candidate_count: rankings.length,
        formal_ready_count: ready,
        oos_stable_count: stable,
        regime_compliant_count: regimeReady,
        warning_count: source && source.warnings ? source.warnings.length : 0
      },
      warnings: source && source.warnings ? source.warnings.slice(0, 12) : [],
      candidates: rankings.map(compactCandidate),
      next_action: rankings.length
        ? 'review_top_candidate_before_strategy_builder_handoff'
        : 'load_or_evaluate_candidates_before_export'
    };
  }

  function buildStrategyBuilderHandoff(reviewOrModel, options) {
    var review = reviewOrModel && reviewOrModel.type === 'sqx-edge.champion-challenger-review'
      ? reviewOrModel
      : buildReviewExport(reviewOrModel, options);
    var generatedAt = options && options.generatedAt ? options.generatedAt : new Date().toISOString();
    var candidates = (review.candidates || []).map(function(candidate) {
      return {
        rank: candidate.rank,
        strategy_name: candidate.strategy_name,
        symbol: candidate.symbol,
        decision: candidate.formal_fail_count === 0 && candidate.oos_stable ? 'builder_candidate' : 'review_required',
        metrics: candidate.metrics,
        oos: candidate.oos,
        regime: candidate.regime
      };
    });

    return {
      type: 'sqx-edge.strategy-builder-handoff',
      version: 1,
      generated_at: generatedAt,
      source_review: {
        type: review.type,
        generated_at: review.generated_at,
        candidate_count: review.summary.candidate_count,
        formal_ready_count: review.summary.formal_ready_count,
        oos_stable_count: review.summary.oos_stable_count,
        regime_compliant_count: review.summary.regime_compliant_count
      },
      recommended_candidate: candidates[0] || null,
      candidates: candidates,
      builder_status: 'planned_contract',
      guardrails: [
        'No raw CSV payloads are included.',
        'No localStorage state is written.',
        'No remote calls are required.',
        'Operator must review StrategyQuant settings before live use.'
      ]
    };
  }

  function safeFilename(prefix) {
    var stamp = new Date().toISOString().replace(/[:.]/g, '-');
    return prefix + '_' + stamp + '.json';
  }

  function downloadJson(payload, filename, doc) {
    if (!global.Blob || !global.URL || !global.URL.createObjectURL || !doc || !doc.createElement) return false;
    var blob = new global.Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    var url = global.URL.createObjectURL(blob);
    var link = doc.createElement('a');
    link.href = url;
    link.download = filename;
    if (link.style) link.style.display = 'none';
    if (doc.body && doc.body.appendChild) doc.body.appendChild(link);
    if (link.click) link.click();
    if (link.parentNode && link.parentNode.removeChild) link.parentNode.removeChild(link);
    global.setTimeout(function() { global.URL.revokeObjectURL(url); }, 0);
    return true;
  }

  function renderHandoffPreview(handoff, doc) {
    var core = getCore();
    var top = handoff.recommended_candidate;
    var html = top
      ? [
        '<div class="cvc-handoff-card">',
        '<span>Strategy Builder handoff</span>',
        '<strong>#' + core.escapeHtml(top.rank) + ' ' + core.escapeHtml(top.strategy_name) + '</strong>',
        '<small>' + core.escapeHtml(top.symbol || 'sin simbolo') + ' | ' + core.escapeHtml(top.decision) + '</small>',
        '</div>'
      ].join('')
      : '<div class="cvc-handoff-card"><span>Strategy Builder handoff</span><strong>Sin candidatas</strong><small>Evalua datos antes de preparar el paquete.</small></div>';
    setHtml(IDS.handoffPreview, html, doc);
    setDisplay(IDS.handoffPreview, '', doc);
  }

  function exportReview(options) {
    var doc = options && options.document ? options.document : global.document;
    var model = evaluate({ document: doc });
    if (!model.ok || !model.rankings.length) {
      setStatus('No hay ranking exportable. Revisa o carga datos primero.', 'warn', doc);
      return null;
    }
    var payload = buildReviewExport(model);
    var downloaded = downloadJson(payload, safeFilename('sqx_cvc_review'), doc);
    setStatus(downloaded ? 'Resumen CVC exportado en JSON seguro.' : 'Resumen CVC preparado en memoria.', 'ok', doc);
    return payload;
  }

  function prepareHandoff(options) {
    var doc = options && options.document ? options.document : global.document;
    var model = evaluate({ document: doc });
    if (!model.ok || !model.rankings.length) {
      setStatus('No hay candidatas para handoff. Revisa o carga datos primero.', 'warn', doc);
      return null;
    }
    var payload = buildStrategyBuilderHandoff(buildReviewExport(model));
    var downloaded = downloadJson(payload, safeFilename('sqx_strategy_builder_handoff'), doc);
    renderHandoffPreview(payload, doc);
    setStatus(downloaded ? 'Handoff Strategy Builder exportado.' : 'Handoff Strategy Builder preparado en memoria.', 'ok', doc);
    return payload;
  }

  function renderSummary(model, doc) {
    var total = model.rankings.length;
    var ready = model.rankings.filter(function(item) { return item.formal_fail_count === 0; }).length;
    var stable = model.rankings.filter(function(item) { return item.oos_stable; }).length;
    var regimeReady = model.rankings.filter(function(item) {
      return item.regime_evidence && item.regime_evidence.label === 'COMPLIANT';
    }).length;
    var healthReady = model.rankings.filter(healthOk).length;
    var egtV2Ready = model.rankings.filter(egtV2Ok).length;
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
      renderMetric('Health OK', healthReady),
      renderMetric('EGT v2 OK', egtV2Ready),
      renderMetric('Avisos de datos', warnings)
    ].join(''), doc);
    setText(IDS.oosSummary, stable + ' OOS estable | ' + healthReady + ' Health OK | ' + egtV2Ready + ' EGT v2 OK.', doc);
  }

  function renderEmpty(doc) {
    setText(IDS.candidateCount, 0, doc);
    setText(IDS.readyCount, 0, doc);
    setText(IDS.oosReadyCount, 0, doc);
    setText(IDS.regimeReadyCount, 0, doc);
    setHtml(IDS.summary, '', doc);
    setHtml(IDS.ranking, '', doc);
    setText(IDS.oosSummary, 'OOS pendiente.', doc);
    setHtml(IDS.handoffPreview, '', doc);
    setDisplay(IDS.handoffPreview, 'none', doc);
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
    var visibleRankings = filterModelRankings(model, doc);
    setHtml(IDS.ranking, visibleRankings.map(renderRow).join(''), doc);
    if (model.rankings.length && !visibleRankings.length) {
      setHtml(IDS.ranking, '<div class="cvc-empty">Sin candidatas visibles con los filtros actuales.</div>', doc);
    }

    var tone = model.warnings.length ? 'warn' : 'ok';
    var message = model.rankings.length
      ? 'Comparacion lista. Ranking generado con reglas formales y OOS.'
      : 'Comparacion lista, sin candidatas.';
    if (model.warnings.length) message += ' Avisos: ' + model.warnings.slice(0, 3).join(', ');
    if (visibleRankings.length !== model.rankings.length) message += ' Filtro activo: ' + visibleRankings.length + '/' + model.rankings.length + ' visibles.';
    setStatus(message, tone, doc);
    lastModel = model;
    return model;
  }

  function evaluate(options) {
    var doc = options && options.document ? options.document : global.document;
    var model = renderResults(parseInputs(doc), doc);
    lastModel = model;
    return model;
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
      ui.bindClick(byId(IDS.exportReview, doc), function() { exportReview({ document: doc }); });
      ui.bindClick(byId(IDS.handoff, doc), function() { prepareHandoff({ document: doc }); });
    } else {
      byId(IDS.run, doc).addEventListener('click', function() { evaluate({ document: doc }); });
      byId(IDS.sample, doc).addEventListener('click', function() { loadSample({ document: doc }); });
      byId(IDS.clear, doc).addEventListener('click', function() { clear({ document: doc }); });
      byId(IDS.exportReview, doc).addEventListener('click', function() { exportReview({ document: doc }); });
      byId(IDS.handoff, doc).addEventListener('click', function() { prepareHandoff({ document: doc }); });
    }
    [IDS.healthFilter, IDS.egtV2Filter].forEach(function(id) {
      var node = byId(id, doc);
      if (node && node.addEventListener) {
        node.addEventListener('change', function() {
          if (lastModel) renderResults(lastModel, doc);
        });
      }
    });
    renderEmpty(doc);
    return true;
  }

  SQX.championChallenger = SQX.championChallenger || {
    ids: IDS,
    buildReviewExport: buildReviewExport,
    buildRankings: buildRankings,
    buildStrategyBuilderHandoff: buildStrategyBuilderHandoff,
    clear: clear,
    evaluate: evaluate,
    exportReview: exportReview,
    init: init,
    parseInputs: parseInputs,
    prepareHandoff: prepareHandoff,
    sampleData: sampleData
  };

  if (SQX.registerModule) {
    SQX.registerModule('champion-challenger', SQX.championChallenger);
  }
})(window);

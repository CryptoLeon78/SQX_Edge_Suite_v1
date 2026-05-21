(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var VERSION = 'edge-factory-state-v1';
  var FALLBACK_KEY = 'sqx_edge_factory_state_v1';

  var STEPS = [
    { id: 'session', label: 'Punto de partida' },
    { id: 'asset', label: 'Elegir edge' },
    { id: 'capa1-generate', label: 'Generar Capa 1' },
    { id: 'capa1-analyze', label: 'Certificar Capa 1' },
    { id: 'c2-template', label: 'Crear Template C2' },
    { id: 'capa2-generate', label: 'Generar Capa 2' },
    { id: 'capa2-analyze', label: 'Revisar Capa 2' },
    { id: 'portfolio', label: 'Portfolio' }
  ];

  function storageKey() {
    var keys = SQX.config && SQX.config.storageKeys
      ? SQX.config.storageKeys()
      : ((global.SQX_CONFIG && global.SQX_CONFIG.storageKeys) || {});
    return keys.edgeFactoryState || FALLBACK_KEY;
  }

  function defaultState() {
    return {
      version: VERSION,
      handoffVersion: 'edge-factory-handoffs-v1',
      activeStep: 'session',
      mode: 'methodology',
      experienceMode: 'basic',
      selectedCard: null,
      selectedMining: null,
      projectPrefill: null,
      capa1Outputs: [],
      capa1Analysis: null,
      c2Template: null,
      capa2Outputs: [],
      portfolioLab: null,
      downloads: [],
      lastEvent: null,
      completedSteps: []
    };
  }

  function readState() {
    var fallback = defaultState();
    try {
      var raw = global.localStorage && global.localStorage.getItem(storageKey());
      if (!raw) return fallback;
      var parsed = JSON.parse(raw);
      if (!parsed || parsed.version !== VERSION) return fallback;
      return Object.assign(fallback, parsed);
    } catch (_err) {
      return fallback;
    }
  }

  function writeState(state, source) {
    var clean = Object.assign(defaultState(), state || {}, { version: VERSION });
    try {
      if (global.localStorage) global.localStorage.setItem(storageKey(), JSON.stringify(clean));
    } catch (_err) {}
    if (SQX.remoteState && SQX.remoteState.queueSave) {
      SQX.remoteState.queueSave(storageKey(), clean);
    }
    try {
      global.dispatchEvent(new CustomEvent('sqx:edge-factory-state', {
        detail: { source: source || 'edge-factory', state: clean }
      }));
    } catch (_err) {}
    return clean;
  }

  function savePatch(patch, source) {
    return writeState(Object.assign(readState(), patch || {}), source);
  }

  function setActiveStep(stepId) {
    if (!STEPS.some(function(step) { return step.id === stepId; })) return readState();
    return savePatch({ activeStep: stepId }, 'edge-factory-active-step');
  }

  function setExperienceMode(mode) {
    var normalized = String(mode || '').toLowerCase() === 'advanced' ? 'advanced' : 'basic';
    return savePatch({ experienceMode: normalized }, 'edge-factory-experience-mode');
  }

  function completeStep(stepId, done) {
    var state = readState();
    var completed = Array.isArray(state.completedSteps) ? state.completedSteps.slice() : [];
    var index = completed.indexOf(stepId);
    if (done && index === -1) completed.push(stepId);
    if (!done && index !== -1) completed.splice(index, 1);
    var next = STEPS.find(function(step) { return completed.indexOf(step.id) === -1; });
    return savePatch({
      completedSteps: completed,
      activeStep: next ? next.id : 'portfolio'
    }, 'edge-factory-complete-step');
  }

  function safeString(value, fallback) {
    var out = value == null ? '' : String(value).trim();
    return out || (fallback || '');
  }

  function upper(value, fallback) {
    return safeString(value, fallback).toUpperCase();
  }

  function uniqueSteps(list) {
    var allowed = STEPS.map(function(step) { return step.id; });
    return (Array.isArray(list) ? list : []).filter(function(id, index, arr) {
      return allowed.indexOf(id) !== -1 && arr.indexOf(id) === index;
    });
  }

  function withCompleted(state, ids) {
    var completed = uniqueSteps(state.completedSteps || []);
    (Array.isArray(ids) ? ids : [ids]).forEach(function(id) {
      if (STEPS.some(function(step) { return step.id === id; }) && completed.indexOf(id) === -1) {
        completed.push(id);
      }
    });
    return completed;
  }

  function pushRecent(items, item, limit) {
    var next = (Array.isArray(items) ? items.slice() : []);
    next.unshift(item);
    return next.slice(0, limit || 12);
  }

  function normalizeBlockTrace(input) {
    var trace = input && (input.blocksettingTrace || input.blockSettingTrace);
    if (!trace && input && input.trace && input.trace.blocksettingTrace) trace = input.trace.blocksettingTrace;
    if (!trace) return null;
    return {
      canonicalId: safeString(trace.canonicalId || trace.blockSetting || trace.id),
      filename: safeString(trace.filename),
      sha256Short: safeString(trace.sha256Short || trace.hash || trace.sha),
      family: safeString(trace.family),
      layer: safeString(trace.layer),
      variant: safeString(trace.variant)
    };
  }

  function normalizeCard(input) {
    input = input || {};
    var blockTrace = normalizeBlockTrace(input);
    var blockSetting = safeString(
      input.blockSetting || input.blocksetting || input.bs || (blockTrace && blockTrace.canonicalId),
      'BS_Custom'
    );
    return {
      asset: upper(input.asset || input.symbol, 'ASSET'),
      timeframe: upper(input.timeframe || input.tf || input.selectedTimeframe, 'TF'),
      direction: upper(input.direction || input.dir, 'L+S'),
      family: safeString(input.family || input.category || input.cat || (blockTrace && blockTrace.family), 'custom'),
      blockSetting: blockSetting,
      blocksettingTrace: blockTrace,
      source: safeString(input.source || 'asset-card'),
      selectedAt: input.selectedAt || new Date().toISOString()
    };
  }

  function normalizeMining(input) {
    input = input || {};
    var blockTrace = normalizeBlockTrace(input);
    return {
      num: input.num == null ? null : parseInt(input.num, 10),
      phase: input.phase == null ? null : parseInt(input.phase, 10),
      asset: upper(input.asset || input.symbol, 'ASSET'),
      timeframe: upper(input.timeframe || input.tf || input.selectedTimeframe, 'TF'),
      direction: upper(input.direction || input.dir, 'L+S'),
      blockSetting: safeString(input.blockSetting || input.blocksetting || input.bs || (blockTrace && blockTrace.canonicalId), 'BS_Custom'),
      blocksettingTrace: blockTrace,
      source: safeString(input.source || 'manual'),
      recordedAt: input.recordedAt || new Date().toISOString()
    };
  }

  function normalizeFiles(files) {
    return (Array.isArray(files) ? files : []).map(function(file) {
      if (typeof file === 'string') return { name: file };
      return {
        name: safeString(file && (file.name || file.filename || file.file)),
        size: file && file.size,
        modified: safeString(file && (file.modified || file.mtime || file.updated_at || file.updatedAt))
      };
    }).filter(function(file) { return file.name; });
  }

  function summarizeResults(results) {
    var list = Array.isArray(results) ? results : [];
    var ok = list.filter(function(item) { return !!(item && item.ok); }).length;
    return {
      total: list.length,
      ok: ok,
      failed: Math.max(0, list.length - ok)
    };
  }

  function saveEvent(patch, completedIds, activeStep, source) {
    var state = readState();
    var next = Object.assign({}, state, patch || {});
    if (completedIds) next.completedSteps = withCompleted(state, completedIds);
    if (activeStep) next.activeStep = activeStep;
    next.lastEvent = {
      type: source || 'edge-factory-handoff',
      at: new Date().toISOString()
    };
    return writeState(next, source || 'edge-factory-handoff');
  }

  function recordCardSelection(input) {
    var card = normalizeCard(input || {});
    return saveEvent({ selectedCard: card }, ['asset'], 'capa1-generate', 'edge-factory-card-selection');
  }

  function recordPlanMining(input) {
    var mining = normalizeMining(input || {});
    var card = normalizeCard(Object.assign({}, input || {}, {
      asset: mining.asset,
      tf: mining.timeframe,
      dir: mining.direction,
      bs: mining.blockSetting,
      source: mining.source
    }));
    return saveEvent({
      selectedCard: card,
      selectedMining: mining
    }, ['asset'], 'capa1-generate', 'edge-factory-plan-mining');
  }

  function recordProjectPrefill(input) {
    var card = normalizeCard(input || {});
    return saveEvent({
      selectedCard: card,
      projectPrefill: {
        name: safeString(input && input.name),
        capa: numeric(input && input.capa, 1),
        asset: card.asset,
        timeframe: card.timeframe,
        direction: card.direction,
        blockSetting: card.blockSetting,
        preparedAt: new Date().toISOString()
      }
    }, ['asset'], 'capa1-generate', 'edge-factory-project-prefill');
  }

  function recordProjectGeneration(payload) {
    payload = payload || {};
    var capa = numeric(payload.capa, 1);
    var event = {
      capa: capa,
      mode: safeString(payload.mode || 'methodology'),
      generatedAt: payload.generatedAt || new Date().toISOString(),
      minings: (Array.isArray(payload.minings) ? payload.minings : []).map(normalizeMining),
      custom: payload.custom ? normalizeCard(payload.custom) : null,
      results: summarizeResults(payload.results || []),
      files: normalizeFiles(payload.outputFiles || payload.files || [])
    };
    if (capa === 2) {
      return saveEvent({
        capa2Outputs: pushRecent(readState().capa2Outputs, event, 8)
      }, ['capa2-generate'], 'capa2-analyze', 'edge-factory-capa2-generation');
    }
    return saveEvent({
      capa1Outputs: pushRecent(readState().capa1Outputs, event, 8)
    }, ['capa1-generate'], 'capa1-analyze', 'edge-factory-capa1-generation');
  }

  function recordTemplateMakerAnalysis(payload) {
    payload = payload || {};
    var report = payload.report || {};
    var diversity = payload.diversity || report.diversity || {};
    var analysis = {
      analyzedAt: payload.analyzedAt || new Date().toISOString(),
      source: safeString(payload.source || 'template-maker'),
      contract: safeString(report.contractVersion || report.schemaVersion || payload.contractVersion || 'Template Maker Cert'),
      total: numeric(report.total || payload.total, 0),
      passed: numeric(report.passed || payload.passed, 0),
      review: numeric(report.review || payload.review, 0),
      failed: numeric(report.failed || payload.failed, 0),
      certified: numeric(report.certified || payload.certified, 0),
      clusters: numeric(diversity.clusters || payload.clusters, 0),
      winners: numeric(diversity.winners || payload.winners || payload.readyForC2, 0),
      readyForC2: numeric(payload.readyForC2 || diversity.winners, 0)
    };
    var complete = analysis.passed > 0 || analysis.winners > 0 || analysis.readyForC2 > 0;
    return saveEvent({ capa1Analysis: analysis }, complete ? ['capa1-analyze'] : [], complete ? 'c2-template' : 'capa1-analyze', 'edge-factory-capa1-analysis');
  }

  function recordC2Template(trace) {
    trace = trace || {};
    var template = {
      name: safeString(trace.name || trace.templateName || 'Template_C2'),
      asset: upper(trace.asset, 'ASSET'),
      timeframe: upper(trace.timeframe, 'TF'),
      direction: upper(trace.direction, 'BOTH'),
      blockSetting: safeString(trace.blockSetting || trace.blocksetting, 'BS_Custom'),
      indicatorBase: safeString(trace.indicatorBase || trace.indicator || 'SIN_INDICADOR'),
      clusterId: safeString(trace.clusterId || trace.cluster || 'CL00'),
      sourceStrategyName: safeString(trace.sourceStrategyName || trace.strategyName || trace.source),
      generatedAt: trace.generatedAt || new Date().toISOString()
    };
    return saveEvent({ c2Template: template }, ['c2-template'], 'capa2-generate', 'edge-factory-c2-template');
  }

  function recordPortfolioLab(report) {
    var clean = Object.assign({
      version: 'portfolio-lab-mvp-v1',
      total: 0,
      winners: 0,
      rows: []
    }, report || {}, { analyzedAt: new Date().toISOString() });
    return saveEvent({ portfolioLab: clean }, clean.total ? ['capa2-analyze', 'portfolio'] : [], 'portfolio', 'edge-factory-portfolio-lab');
  }

  function recordDownloadRequest(payload) {
    payload = payload || {};
    var download = {
      kind: safeString(payload.kind || 'artifact'),
      capa: payload.capa == null ? null : numeric(payload.capa, null),
      files: normalizeFiles(payload.files || payload.outputFiles),
      requestedAt: new Date().toISOString()
    };
    return saveEvent({
      downloads: pushRecent(readState().downloads, download, 10)
    }, [], null, 'edge-factory-download-request');
  }

  function latest(list) {
    return Array.isArray(list) && list.length ? list[0] : null;
  }

  function miningLabel(mining) {
    if (!mining) return '';
    return [
      mining.num ? 'M' + String(mining.num).padStart(2, '0') : '',
      mining.asset,
      mining.timeframe,
      mining.direction,
      mining.blockSetting
    ].filter(Boolean).join(' · ');
  }

  function contextSummary(state) {
    state = Object.assign(defaultState(), state || readState());
    var c1 = latest(state.capa1Outputs);
    var c2 = latest(state.capa2Outputs);
    var filesC1 = c1 && c1.files ? c1.files.length : 0;
    var filesC2 = c2 && c2.files ? c2.files.length : 0;
    return {
      session: state.completedSteps.indexOf('session') !== -1
        ? 'OK: acceso, workspace, servicio y descargas preparados.'
        : 'Pendiente: valida acceso, workspace, servicio y descargas.',
      asset: state.selectedCard
        ? 'Hipótesis activa: ' + [state.selectedCard.asset, state.selectedCard.timeframe, state.selectedCard.direction, state.selectedCard.blockSetting].filter(Boolean).join(' · ')
        : 'Pendiente: elige una tarjeta con asset, TF, dirección y BlockSetting.',
      'capa1-generate': c1
        ? 'C1 lista: ' + (c1.results ? c1.results.ok + '/' + c1.results.total + ' OK' : 'generada') + (filesC1 ? ' · ' + filesC1 + ' archivo(s) descargables' : '')
        : (state.selectedMining ? 'Preparado para C1 descargable: ' + miningLabel(state.selectedMining) : 'Pendiente: añade o selecciona un mining trazable.'),
      'capa1-analyze': state.capa1Analysis
        ? 'C1 certificada: ' + state.capa1Analysis.total + ' estrategias · ' + state.capa1Analysis.passed + ' PASSED · ' + state.capa1Analysis.winners + ' ganadores C2.'
        : 'Pendiente: carga Databank CSV + .sqx en Template Maker.',
      'c2-template': state.c2Template
        ? 'Template C2 listo: ' + state.c2Template.name + ' · ' + state.c2Template.indicatorBase + ' · ' + state.c2Template.clusterId
        : 'Pendiente: crea Template C2 desde un ganador diverso.',
      'capa2-generate': c2
        ? 'C2 lista: ' + (c2.results ? c2.results.ok + '/' + c2.results.total + ' OK' : 'generada') + (filesC2 ? ' · ' + filesC2 + ' archivo(s) descargables' : '')
        : (state.c2Template ? 'Preparado para C2 descargable: ' + state.c2Template.name + '.' : 'Pendiente: falta Template C2 trazable.'),
      'capa2-analyze': c2
        ? 'Listo para Portfolio Lab: importa resultados Capa 2.'
        : 'Pendiente: genera Capa 2 antes del análisis.',
      portfolio: state.portfolioLab && state.portfolioLab.total
        ? 'Portfolio Lab: ' + state.portfolioLab.total + ' candidatos · ' + state.portfolioLab.winners + ' ganadores diversos.'
        : 'Pendiente: calcula shortlist en Portfolio Lab.'
    };
  }

  function numeric(value, fallback) {
    if (value == null || value === '') return fallback == null ? 0 : fallback;
    var normalized = String(value).replace('%', '').replace(',', '.').trim();
    var number = Number(normalized);
    return Number.isFinite(number) ? number : (fallback == null ? 0 : fallback);
  }

  function normalizeKey(value) {
    return String(value == null ? '' : value)
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '');
  }

  function splitDelimitedLine(line, delimiter) {
    var out = [];
    var current = '';
    var quoted = false;
    var chars = String(line || '').split('');
    for (var index = 0; index < chars.length; index += 1) {
      var ch = chars[index];
      if (ch === '"') {
        if (quoted && chars[index + 1] === '"') {
          current += '"';
          index += 1;
        } else {
          quoted = !quoted;
        }
        continue;
      }
      if (ch === delimiter && !quoted) {
        out.push(current.trim());
        current = '';
        continue;
      }
      current += ch;
    }
    out.push(current.trim());
    return out.map(function(value) { return value.replace(/^"|"$/g, '').replace(/""/g, '"'); });
  }

  function detectDelimiter(headerLine) {
    var header = String(headerLine || '');
    var semicolons = (header.match(/;/g) || []).length;
    var commas = (header.match(/,/g) || []).length;
    return semicolons > commas ? ';' : ',';
  }

  function valueByAliases(row, aliases) {
    var normalized = row && row.__normalized ? row.__normalized : {};
    for (var i = 0; i < aliases.length; i += 1) {
      var value = normalized[normalizeKey(aliases[i])];
      if (value != null && value !== '') return value;
    }
    return '';
  }

  function inferTokenFromStrategy(row, pattern, fallback) {
    var source = String((row && (row.strategy || row['Strategy Name'] || row.name)) || '');
    var match = source.match(pattern);
    return match && match[1] ? match[1] : fallback;
  }

  function parsePortfolioRows(text) {
    var lines = String(text || '').split(/\r?\n/).map(function(line) { return line.trim(); }).filter(Boolean);
    if (!lines.length) return [];
    var delimiter = detectDelimiter(lines[0]);
    var header = splitDelimitedLine(lines[0], delimiter).map(function(item) { return item.trim(); });
    return lines.slice(1).map(function(line, index) {
      var values = splitDelimitedLine(line, delimiter);
      var row = { id: 'portfolio-' + (index + 1), importIndex: index, sourceDelimiter: delimiter };
      var normalized = {};
      header.forEach(function(name, columnIndex) {
        var value = values[columnIndex] == null ? '' : values[columnIndex];
        row[name] = value;
        normalized[normalizeKey(name)] = value;
      });
      row.__normalized = normalized;
      row.strategy = valueByAliases(row, ['strategy', 'name', 'Strategy Name', 'Strategy']) || row.id;
      row.asset = upper(valueByAliases(row, ['asset', 'symbol', 'Symbol', 'Market']) || inferTokenFromStrategy(row, /^([A-Z0-9]+)[_\-\s]/i, 'GENERIC'), 'GENERIC');
      row.timeframe = upper(valueByAliases(row, ['timeframe', 'tf', 'TimeFrame', 'Time frame']) || inferTokenFromStrategy(row, /[_\-\s](M1|M5|M15|M30|H1|H4|D1|W1)[_\-\s]/i, 'H1'), 'H1');
      row.blockSetting = valueByAliases(row, ['blockSetting', 'BlockSetting', 'bs', 'Block Setting', 'Building Block', 'Building Blocks']) || inferTokenFromStrategy(row, /(BS_[A-Za-z0-9_]+)/, 'BS_Custom');
      row.indicator = valueByAliases(row, ['indicator', 'indicatorBase', 'Indicator', 'Indicador', 'Base Indicator']) || inferTokenFromStrategy(row, /_(ATR|KER|LINEAR|MACD|SUPER|ICHIMOKU|RSI|ADX|HURST|CHOPPINESS)_?/i, 'SIN_INDICADOR');
      row.clusterId = valueByAliases(row, ['cluster', 'clusterId', 'NumCluster', 'Cluster']) || inferTokenFromStrategy(row, /(CL\d+)/i, '');
      row.profitFactor = numeric(valueByAliases(row, ['profitFactor', 'Profit factor', 'Profit Factor', 'PF']), 0);
      row.retDd = numeric(valueByAliases(row, ['retDd', 'Ret/DD Ratio', 'Return / Drawdown ratio', 'CAGR/Max DD %']), 0);
      row.maxDd = numeric(valueByAliases(row, ['maxDd', 'Max DD %', 'Drawdown %', 'Max Drawdown %']), 100);
      row.trades = numeric(valueByAliases(row, ['trades', '# of trades', 'Number of trades', 'Trades']), 0);
      row.stability = numeric(valueByAliases(row, ['stability', 'Stability']), 0);
      row.winningPercent = numeric(valueByAliases(row, ['winningPercent', 'Winning Percent', 'Win %']), 0);
      row.sqn = numeric(valueByAliases(row, ['SQN', 'sqn']), 0);
      row.netProfit = numeric(valueByAliases(row, ['Net profit', 'Net Profit', 'netProfit']), 0);
      row.hasCoreMetrics = row.profitFactor > 0 && row.trades > 0 && row.maxDd < 100;
      delete row.__normalized;
      return row;
    });
  }

  function scoreCandidate(row) {
    var pf = Math.min(2.4, Math.max(0, numeric(row.profitFactor, 0)));
    var retDd = Math.min(10, Math.max(0, numeric(row.retDd, 0)));
    var drawdown = Math.max(0, 100 - Math.min(100, numeric(row.maxDd, 100)));
    var trades = Math.min(500, Math.max(0, numeric(row.trades, 0)));
    var stability = Math.min(1, Math.max(0, numeric(row.stability, 0)));
    var win = Math.min(100, Math.max(0, numeric(row.winningPercent, 0)));
    var sqn = Math.min(5, Math.max(0, numeric(row.sqn, 0)));
    return Math.round((
      (pf * 22) +
      (retDd * 7) +
      (drawdown * 0.26) +
      (trades * 0.045) +
      (stability * 16) +
      (win * 0.12) +
      (sqn * 3)
    ) * 100) / 100;
  }

  function similarity(a, b) {
    if (!a || !b) return 0;
    var score = 0;
    if (normalizeKey(a.asset) === normalizeKey(b.asset)) score += 0.22;
    if (normalizeKey(a.timeframe) === normalizeKey(b.timeframe)) score += 0.18;
    if (normalizeKey(a.blockSetting) === normalizeKey(b.blockSetting)) score += 0.22;
    if (normalizeKey(a.indicator) === normalizeKey(b.indicator)) score += 0.18;
    var pfGap = Math.abs(numeric(a.profitFactor, 1) - numeric(b.profitFactor, 1));
    var retGap = Math.abs(numeric(a.retDd, 0) - numeric(b.retDd, 0));
    var ddGap = Math.abs(numeric(a.maxDd, 100) - numeric(b.maxDd, 100));
    if (pfGap < 0.15) score += 0.08;
    if (retGap < 0.8) score += 0.06;
    if (ddGap < 4) score += 0.06;
    return Math.min(1, score);
  }

  function buildPortfolioShortlist(inputRows, options) {
    var settings = Object.assign({
      similarityThreshold: 0.78,
      maxWinners: 8,
      maxPerAsset: 2,
      minProfitFactor: 1.2,
      minTrades: 80,
      maxDrawdown: 45
    }, options || {});
    var rows = (Array.isArray(inputRows) ? inputRows : parsePortfolioRows(inputRows)).map(function(row) {
      return Object.assign({}, row, { score: scoreCandidate(row) });
    }).sort(function(a, b) {
      return b.score - a.score || a.importIndex - b.importIndex;
    });
    var winners = [];
    var perAsset = {};
    rows.forEach(function(row) {
      var closest = winners.reduce(function(best, winner) {
        var sim = similarity(row, winner);
        return sim > best.value ? { value: sim, winner: winner } : best;
      }, { value: 0, winner: null });
      row.similarity = Math.round(closest.value * 100) / 100;
      row.closestStrategy = closest.winner ? closest.winner.strategy : '';
      row.clusterRef = closest.winner ? closest.winner.clusterRef : (row.clusterId || 'CL' + String(winners.length + 1).padStart(2, '0'));
      var assetKey = normalizeKey(row.asset);
      var assetCount = perAsset[assetKey] || 0;
      var reasons = [];
      if (!row.hasCoreMetrics) reasons.push('faltan métricas núcleo');
      if (row.profitFactor < settings.minProfitFactor) reasons.push('PF bajo');
      if (row.trades < settings.minTrades) reasons.push('pocos trades');
      if (row.maxDd > settings.maxDrawdown) reasons.push('DD alto');
      if (assetCount >= settings.maxPerAsset) reasons.push('límite por asset');
      if (winners.length >= settings.maxWinners) reasons.push('límite de portfolio');
      if (!reasons.length && closest.value >= settings.similarityThreshold) reasons.push('similar a ' + closest.winner.strategy);
      if (!reasons.length) {
        row.diversityStatus = 'portfolio';
        row.decision = 'Portfolio';
        row.reason = 'ganador diverso';
        winners.push(row);
        perAsset[assetKey] = assetCount + 1;
      } else if (reasons[0].indexOf('similar a') === 0 || reasons[0] === 'límite por asset' || reasons[0] === 'límite de portfolio') {
        row.diversityStatus = 'similar';
        row.decision = 'Similar';
        row.reason = reasons.join(' · ');
      } else {
        row.diversityStatus = 'review';
        row.decision = 'Revisar';
        row.reason = reasons.join(' · ');
      }
    });
    var statusCounts = rows.reduce(function(acc, row) {
      acc[row.diversityStatus] = (acc[row.diversityStatus] || 0) + 1;
      return acc;
    }, {});
    var uniqueAssets = {};
    rows.forEach(function(row) { uniqueAssets[normalizeKey(row.asset)] = true; });
    return {
      version: 'portfolio-lab-mvp-v2',
      total: rows.length,
      winners: winners.length,
      similar: statusCounts.similar || 0,
      review: statusCounts.review || 0,
      uniqueAssets: Object.keys(uniqueAssets).filter(Boolean).length,
      settings: settings,
      rows: rows
    };
  }

  SQX.edgeFactory = {
    version: VERSION,
    storageKey: storageKey,
    defaultState: defaultState,
    getState: readState,
    savePatch: savePatch,
    setActiveStep: setActiveStep,
    setExperienceMode: setExperienceMode,
    completeStep: completeStep,
    steps: function() { return STEPS.slice(); },
    recordCardSelection: recordCardSelection,
    recordPlanMining: recordPlanMining,
    recordProjectPrefill: recordProjectPrefill,
    recordProjectGeneration: recordProjectGeneration,
    recordTemplateMakerAnalysis: recordTemplateMakerAnalysis,
    recordC2Template: recordC2Template,
    recordPortfolioLab: recordPortfolioLab,
    recordDownloadRequest: recordDownloadRequest,
    contextSummary: contextSummary,
    parsePortfolioRows: parsePortfolioRows,
    scoreCandidate: scoreCandidate,
    computeSimilarity: similarity,
    buildPortfolioShortlist: buildPortfolioShortlist
  };

  if (SQX.registerModule) SQX.registerModule('edge-factory', SQX.edgeFactory);
})(window);

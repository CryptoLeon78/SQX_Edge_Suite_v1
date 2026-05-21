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
        ? 'C1 lista: ' + (c1.results ? c1.results.ok + '/' + c1.results.total + ' OK' : 'generada') + (filesC1 ? ' · ' + filesC1 + ' descarga(s)' : '')
        : (state.selectedMining ? 'Preparado para C1: ' + miningLabel(state.selectedMining) : 'Pendiente: añade o selecciona un mining trazable.'),
      'capa1-analyze': state.capa1Analysis
        ? 'C1 certificada: ' + state.capa1Analysis.total + ' estrategias · ' + state.capa1Analysis.passed + ' PASSED · ' + state.capa1Analysis.winners + ' ganadores C2.'
        : 'Pendiente: carga Databank CSV + .sqx en Template Maker.',
      'c2-template': state.c2Template
        ? 'Template C2 listo: ' + state.c2Template.name + ' · ' + state.c2Template.indicatorBase + ' · ' + state.c2Template.clusterId
        : 'Pendiente: crea Template C2 desde un ganador diverso.',
      'capa2-generate': c2
        ? 'C2 lista: ' + (c2.results ? c2.results.ok + '/' + c2.results.total + ' OK' : 'generada') + (filesC2 ? ' · ' + filesC2 + ' descarga(s)' : '')
        : (state.c2Template ? 'Preparado para C2: ' + state.c2Template.name + '.' : 'Pendiente: falta Template C2 trazable.'),
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

  function parsePortfolioRows(text) {
    var lines = String(text || '').split(/\r?\n/).map(function(line) { return line.trim(); }).filter(Boolean);
    if (!lines.length) return [];
    var header = lines[0].split(/[;,]/).map(function(item) { return item.trim(); });
    return lines.slice(1).map(function(line, index) {
      var values = line.split(/[;,]/).map(function(item) { return item.trim(); });
      var row = { id: 'portfolio-' + (index + 1), importIndex: index };
      header.forEach(function(name, columnIndex) {
        row[name] = values[columnIndex] == null ? '' : values[columnIndex];
      });
      row.strategy = row.strategy || row.name || row['Strategy Name'] || row.id;
      row.asset = row.asset || row.symbol || row.Symbol || 'GENERIC';
      row.timeframe = row.timeframe || row.tf || row.TimeFrame || 'H1';
      row.blockSetting = row.blockSetting || row.bs || row.BlockSetting || 'BS_Custom';
      row.indicator = row.indicator || row.indicatorBase || row.Indicator || 'SIN_INDICADOR';
      row.profitFactor = numeric(row.profitFactor || row['Profit factor'], 1);
      row.retDd = numeric(row.retDd || row['Ret/DD Ratio'] || row['CAGR/Max DD %'], 0);
      row.maxDd = numeric(row.maxDd || row['Max DD %'], 100);
      row.trades = numeric(row.trades || row['# of trades'], 0);
      row.stability = numeric(row.stability || row.Stability, 0);
      return row;
    });
  }

  function scoreCandidate(row) {
    return Math.round((
      (numeric(row.profitFactor, 1) * 24) +
      (numeric(row.retDd, 0) * 8) +
      (Math.max(0, 100 - numeric(row.maxDd, 100)) * 0.32) +
      (Math.min(400, numeric(row.trades, 0)) * 0.06) +
      (numeric(row.stability, 0) * 18)
    ) * 100) / 100;
  }

  function similarity(a, b) {
    if (!a || !b) return 0;
    var score = 0;
    if (String(a.asset).toLowerCase() === String(b.asset).toLowerCase()) score += 0.25;
    if (String(a.timeframe).toLowerCase() === String(b.timeframe).toLowerCase()) score += 0.2;
    if (String(a.blockSetting).toLowerCase() === String(b.blockSetting).toLowerCase()) score += 0.25;
    if (String(a.indicator).toLowerCase() === String(b.indicator).toLowerCase()) score += 0.2;
    var pfGap = Math.abs(numeric(a.profitFactor, 1) - numeric(b.profitFactor, 1));
    if (pfGap < 0.15) score += 0.1;
    return Math.min(1, score);
  }

  function buildPortfolioShortlist(inputRows) {
    var rows = (Array.isArray(inputRows) ? inputRows : parsePortfolioRows(inputRows)).map(function(row) {
      return Object.assign({}, row, { score: scoreCandidate(row) });
    }).sort(function(a, b) {
      return b.score - a.score || a.importIndex - b.importIndex;
    });
    var winners = [];
    rows.forEach(function(row) {
      var closest = winners.reduce(function(best, winner) {
        var sim = similarity(row, winner);
        return sim > best.value ? { value: sim, winner: winner } : best;
      }, { value: 0, winner: null });
      row.similarity = Math.round(closest.value * 100) / 100;
      row.diversityStatus = closest.value >= 0.78 ? 'similar' : 'winner';
      row.clusterRef = closest.winner ? closest.winner.strategy : 'CL' + String(winners.length + 1).padStart(2, '0');
      if (row.diversityStatus === 'winner') winners.push(row);
    });
    return {
      version: 'portfolio-lab-mvp-v1',
      total: rows.length,
      winners: winners.length,
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

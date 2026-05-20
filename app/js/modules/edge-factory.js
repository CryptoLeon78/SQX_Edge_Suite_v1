(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var VERSION = 'edge-factory-state-v1';
  var FALLBACK_KEY = 'sqx_edge_factory_state_v1';

  var STEPS = [
    { id: 'session', label: 'Preparar sesión' },
    { id: 'asset', label: 'Elegir tarjeta' },
    { id: 'capa1-generate', label: 'Minar Capa 1' },
    { id: 'capa1-analyze', label: 'Analizar Capa 1' },
    { id: 'c2-template', label: 'Generar Template C2' },
    { id: 'capa2-generate', label: 'Minar Capa 2' },
    { id: 'capa2-analyze', label: 'Analizar Capa 2' },
    { id: 'portfolio', label: 'Portfolio descorrelacionado' }
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
      activeStep: 'session',
      mode: 'methodology',
      selectedCard: null,
      capa1Outputs: [],
      capa1Analysis: null,
      c2Template: null,
      capa2Outputs: [],
      portfolioLab: null,
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
    parsePortfolioRows: parsePortfolioRows,
    scoreCandidate: scoreCandidate,
    computeSimilarity: similarity,
    buildPortfolioShortlist: buildPortfolioShortlist
  };

  if (SQX.registerModule) SQX.registerModule('edge-factory', SQX.edgeFactory);
})(window);

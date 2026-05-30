(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var VERSION = 'edge-factory-state-v1';
  var FALLBACK_KEY = 'sqx_edge_factory_state_v1';
  var PORTFOLIO_LAB_VERSION = 'portfolio-lab-governed-v1';
  var PORTFOLIO_MASTER_VERSION = 'portfolio-master-contract-v1';
  var PORTFOLIO_MASTER_INPUTS_VERSION = 'portfolio-master-inputs-pending-v1';
  var PORTFOLIO_CORRELATION_STABILITY_VERSION = 'sqx142-portfolio-corr1-stability-audit-v1';
  var CAPA1_C2_CORRELATION_SELECTION_VERSION = 'sqx142-capa1-c2-corr1-template-selection-v1';
  var BACKPORT_OPERATOR_PANEL_VERSION = 'ui-integration1-backport-operator-panel-v1';
  var PORTFOLIO_TARGET_MIN = 8;
  var PORTFOLIO_TARGET_MAX = 12;
  var PORTFOLIO_MASTER_MIN_OBSERVATIONS = 3;

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
      c2TemplateSelection: null,
      c2Template: null,
      capa2Outputs: [],
      portfolioLab: null,
      portfolioCorrelationStability: null,
      portfolioMasterContract: null,
      backportOperatorPanel: null,
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
    var clean = sanitizePortfolioReport(Object.assign({}, report || {}, {
      analyzedAt: new Date().toISOString()
    }));
    var master = buildPortfolioMasterContract({ labReport: clean });
    var completed = clean.total ? ['capa2-analyze'] : [];
    return saveEvent({ portfolioLab: clean, portfolioMasterContract: master }, completed, 'portfolio', 'edge-factory-portfolio-lab');
  }

  function recordPortfolioMasterContract(payload) {
    var clean = buildPortfolioMasterContract(Object.assign({}, payload || {}, {
      encodedAt: new Date().toISOString()
    }));
    return saveEvent({
      portfolioMasterContract: clean
    }, clean.status === 'ready_for_master_review' ? ['portfolio'] : [], 'portfolio', 'edge-factory-portfolio-master-contract');
  }

  function recordPortfolioCorrelationStability(report) {
    report = report || {};
    var clean = sanitizePlainObject(report, 12000);
    clean.version = sanitizeText(clean.version || PORTFOLIO_CORRELATION_STABILITY_VERSION, PORTFOLIO_CORRELATION_STABILITY_VERSION, 80);
    clean.decisionDomain = clean.decisionDomain || 'capa2_portfolio_selection';
    clean.recordedAt = new Date().toISOString();
    return saveEvent({
      portfolioCorrelationStability: clean
    }, [], 'portfolio', 'edge-factory-portfolio-corr1-stability');
  }

  function recordC2TemplateSelection(report) {
    report = report || {};
    var clean = sanitizePlainObject(report, 12000);
    clean.version = sanitizeText(clean.version || CAPA1_C2_CORRELATION_SELECTION_VERSION, CAPA1_C2_CORRELATION_SELECTION_VERSION, 80);
    clean.decisionDomain = 'capa1_c2_template_selection';
    clean.recordedAt = new Date().toISOString();
    return saveEvent({
      c2TemplateSelection: clean
    }, ['capa1-analyze'], 'c2-template', 'edge-factory-capa1-c2-corr1-selection');
  }

  function recordMiningRegistryFunnel(input) {
    input = input || {};
    var patch = input.edgeFactoryStatePatch || {};
    var databanks = Array.isArray(input.databanks) ? input.databanks : (patch.capa1Analysis && Array.isArray(patch.capa1Analysis.databanks) ? patch.capa1Analysis.databanks : []);
    var byName = {};
    databanks.forEach(function(item) {
      byName[String(item.databank || '').toLowerCase()] = item;
    });
    var results = byName.results || null;
    var forward = byName.foward || byName.forward || null;
    var spp = byName.spp || null;
    var wfm = byName.wfm || null;
    var selectedCard = patch.selectedCard || {
      asset: input.asset,
      timeframe: input.timeframe,
      direction: input.direction,
      family: input.blocksettingFamily,
      blockSetting: input.blocksettingFamily,
      source: 'sqx142-mining-results-registry-v1'
    };
    var analysis = Object.assign({
      version: 'sqx142-mining-results-registry-v1',
      projectKey: input.projectKey,
      status: 'recorded',
      databanks: databanks,
      tests: Array.isArray(input.tests) ? input.tests : [],
      total: results ? numeric(results.row_count, 0) : 0,
      passed: forward ? numeric(forward.row_count, 0) : 0,
      winners: Math.max(numeric(spp && spp.row_count, 0), numeric(wfm && wfm.row_count, 0)),
      forwardCount: forward ? numeric(forward.row_count, 0) : 0,
      sppCount: spp ? numeric(spp.row_count, 0) : 0,
      wfmCount: wfm ? numeric(wfm.row_count, 0) : 0
    }, patch.capa1Analysis || {});
    var c2Selection = patch.c2TemplateSelection && patch.c2TemplateSelection.decisionDomain
      ? patch.c2TemplateSelection
      : null;
    return saveEvent({
      selectedCard: normalizeCard(selectedCard),
      capa1Analysis: analysis,
      c2TemplateSelection: c2Selection,
      miningRegistryFunnel: input
    }, ['asset', 'capa1-generate', 'capa1-analyze'], 'c2-template', 'edge-factory-mining-registry-funnel');
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
    var master = state.portfolioMasterContract || null;
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
        ? 'Portfolio Lab ' + (state.portfolioLab.version || PORTFOLIO_LAB_VERSION) + ': ' + state.portfolioLab.total + ' candidatos · ' + state.portfolioLab.winners + ' ganadores · Corr ' + (state.portfolioCorrelationStability ? (state.portfolioCorrelationStability.summary && state.portfolioCorrelationStability.summary.status || 'audit') : 'pendiente') + ' · Master ' + (master ? master.status : 'bloqueado') + '.'
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

  function clampNumber(value, min, max, fallback) {
    var number = numeric(value, fallback);
    if (!Number.isFinite(number)) number = fallback;
    return Math.min(max, Math.max(min, number));
  }

  function roundMetric(value, digits) {
    var power = Math.pow(10, digits == null ? 2 : digits);
    return Math.round(numeric(value, 0) * power) / power;
  }

  function sanitizeText(value, fallback, maxLength) {
    var out = safeString(value, fallback || '');
    if (!out) return '';
    if (/^[A-Za-z]:[\\/]/.test(out)) {
      out = out.split(/[\\/]/).filter(Boolean).pop() || '[ruta-local-redactada]';
    }
    out = out
      .replace(/[A-Za-z]:[\\/][^\s,;|]+/g, '[ruta-local-redactada]')
      .replace(/\\\\[^\s,;|]+/g, '[ruta-local-redactada]')
      .replace(/https?:\/\/\S+/gi, '[url-redacted]')
      .replace(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, '[email-redacted]')
      .replace(/\s+/g, ' ')
      .trim();
    if (maxLength && out.length > maxLength) out = out.slice(0, Math.max(0, maxLength - 3)).trim() + '...';
    return out;
  }

  function sanitizePrivateText(value, fallback, maxLength) {
    var out = sanitizeText(value, fallback || '');
    if (!out) return '';
    out = out
      .replace(/\b(account(?:number|id)?|login|password|pass|token|secret|api[_ -]?key|license|phone|balance|equity|server|ip)\s*[:=]\s*[^,;|\n]+/gi, function(match, key) {
        return key + '=[redacted]';
      })
      .replace(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g, '[ip-redacted]')
      .replace(/\b[A-Za-z0-9_-]{24,}\b/g, '[token-redacted]')
      .replace(/\s+/g, ' ')
      .trim();
    if (maxLength && out.length > maxLength) out = out.slice(0, Math.max(0, maxLength - 3)).trim() + '...';
    return out;
  }

  function sanitizePlainObject(value, maxLength) {
    var budget = { remaining: maxLength || 12000 };
    function walk(item) {
      if (budget.remaining <= 0) return '[truncated]';
      if (item == null || typeof item === 'number' || typeof item === 'boolean') return item;
      if (typeof item === 'string') {
        budget.remaining -= item.length;
        return sanitizePrivateText(item, '', 500);
      }
      if (Array.isArray(item)) return item.slice(0, 80).map(walk);
      if (typeof item === 'object') {
        var out = {};
        Object.keys(item).slice(0, 80).forEach(function(key) {
          out[sanitizeText(key, '', 80)] = walk(item[key]);
        });
        return out;
      }
      return '';
    }
    return walk(value || {});
  }

  function countPrivacyMarkers(value) {
    var text = String(value == null ? '' : value);
    var matches = []
      .concat(text.match(/\b(account(?:number|id)?|login|password|pass|token|secret|api[_ -]?key|license|phone|balance|equity|server|ip)\s*[:=]\s*[^,;|\n]+/gi) || [])
      .concat(text.match(/[A-Za-z]:[\\/][^\s,;|]+/g) || [])
      .concat(text.match(/\\\\[^\s,;|]+/g) || [])
      .concat(text.match(/https?:\/\/\S+/gi) || [])
      .concat(text.match(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi) || [])
      .concat(text.match(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g) || []);
    return matches.length;
  }

  function isForwardSource(value) {
    var key = normalizeKey(value);
    if (!key) return false;
    if (key.indexOf('walkforward') !== -1 || key.indexOf('walkfoward') !== -1 || key === 'wfm') return false;
    return key.indexOf('forward') !== -1 || key.indexOf('foward') !== -1;
  }

  function isPassedStatus(value) {
    var key = normalizeKey(value);
    if (!key) return false;
    if (['pass', 'passed', 'ok', 'true', '1', 'accepted', 'survivor', 'survived', 'aprobado', 'aprobada'].indexOf(key) !== -1) return true;
    return key.indexOf('passed') !== -1 || key.indexOf('survivor') !== -1 || key.indexOf('survived') !== -1;
  }

  function markerIsExplicitTrue(value) {
    var key = normalizeKey(value);
    return ['1', 'true', 'yes', 'si', 'sí', 'forced', 'force', 'synthetic', 'manual', 'override'].indexOf(key) !== -1;
  }

  function hasForcedSyntheticPass(row) {
    row = row || {};
    var forcedFlag = valueByAliases(row, ['forced', 'Forced', 'forcePass', 'Force Pass', 'forcedPass', 'Forced Pass', 'manualPass', 'Manual Pass']);
    var syntheticFlag = valueByAliases(row, ['syntheticPass', 'Synthetic Pass', 'synthetic_pass', 'Synthetic_Pass']);
    if (markerIsExplicitTrue(forcedFlag) || markerIsExplicitTrue(syntheticFlag)) return true;
    var passSource = normalizeKey(row.passSource || valueByAliases(row, ['passSource', 'Pass Source', 'resultSource', 'Result Source', 'validationMode', 'Validation Mode', 'passType', 'Pass Type']));
    if (['forced', 'force', 'synthetic', 'manual', 'override', 'fabricated', 'simulated'].indexOf(passSource) !== -1) return true;
    var joined = normalizeKey([
      row.forwardStatus,
      row.forwardSource,
      row.passSource,
      valueByAliases(row, ['status', 'Status', 'result', 'Result']),
      valueByAliases(row, ['notes', 'Notes', 'comment', 'Comment'])
    ].filter(Boolean).join(' '));
    return joined.indexOf('forcedpass') !== -1 ||
      joined.indexOf('forcepass') !== -1 ||
      joined.indexOf('syntheticpass') !== -1 ||
      joined.indexOf('manualpass') !== -1 ||
      joined.indexOf('overridepass') !== -1 ||
      joined.indexOf('fabricatedpass') !== -1 ||
      joined.indexOf('simulatedpass') !== -1 ||
      joined.indexOf('forcedresultspassed') !== -1;
  }

  function portfolioForwardContract(row) {
    row = row || {};
    var phase = row.sourcePhase || valueByAliases(row, [
      'sourcePhase', 'Source Phase', 'phase', 'Phase'
    ]);
    var databank = row.sourceDatabank || row.forwardSource || valueByAliases(row, [
      'sourceDatabank', 'Source Databank', 'databank', 'Databank',
      'resultDatabank', 'Result Databank', 'output', 'Output'
    ]);
    var source = row.forwardSource || valueByAliases(row, [
      'forwardSource', 'Forward Source', 'Foward Source', 'source', 'Source', 'databank', 'Databank',
      'resultDatabank', 'Result Databank', 'output', 'Output', 'stage', 'Stage',
      'phase', 'Phase', 'test', 'Test'
    ]) || databank;
    var status = row.forwardStatus || valueByAliases(row, [
      'forwardStatus', 'Forward Status', 'status', 'Status', 'result', 'Result',
      'filters_result', 'Filters Result', 'passed', 'Passed', 'pass', 'Pass'
    ]);
    var passSource = row.passSource || valueByAliases(row, [
      'passSource', 'Pass Source', 'resultSource', 'Result Source', 'validationMode',
      'Validation Mode', 'passType', 'Pass Type'
    ]);
    var sourceOk = isForwardSource(source || databank);
    var phaseOk = !phase || normalizeKey(phase) === 'phase28capa2forward';
    var statusOk = isPassedStatus(status);
    var forcedSynthetic = hasForcedSyntheticPass(Object.assign({}, row, {
      forwardSource: source,
      forwardStatus: status,
      passSource: passSource
    }));
    var issues = [];
    if (!phaseOk) issues.push('sourcePhase != phase28_capa2_forward');
    if (!sourceOk) issues.push('sourceDatabank != Forward/Foward');
    if (!statusOk) issues.push('status != PASSED natural');
    if (forcedSynthetic) issues.push('forced/synthetic pass rejected');
    return {
      ok: phaseOk && sourceOk && statusOk && !forcedSynthetic,
      phase: sanitizeText(phase || 'phase28_capa2_forward', ''),
      databank: sanitizeText(databank || source || 'Foward', ''),
      source: sanitizeText(source, ''),
      status: sanitizeText(status, ''),
      passSource: sanitizeText(passSource, ''),
      issues: issues
    };
  }

  function parsePortfolioSeries(value) {
    var text = String(value == null ? '' : value).trim();
    if (!text) return [];
    return text.split(/[|\s]+/).map(function(item) {
      return numeric(item, NaN);
    }).filter(function(item) {
      return Number.isFinite(item);
    });
  }

  function portfolioReturnSeries(row) {
    row = row || {};
    if (Array.isArray(row.returnSeries) && row.returnSeries.length >= 3) return row.returnSeries;
    var equity = Array.isArray(row.equitySeries) ? row.equitySeries : [];
    if (equity.length < 4) return [];
    var returns = [];
    for (var index = 1; index < equity.length; index += 1) {
      var prev = equity[index - 1];
      var current = equity[index];
      returns.push(prev ? (current - prev) / Math.abs(prev) : current - prev);
    }
    return returns;
  }

  function pearsonCorrelation(a, b) {
    if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length || a.length < 3) return null;
    var meanA = a.reduce(function(sum, item) { return sum + item; }, 0) / a.length;
    var meanB = b.reduce(function(sum, item) { return sum + item; }, 0) / b.length;
    var num = 0;
    var denA = 0;
    var denB = 0;
    for (var index = 0; index < a.length; index += 1) {
      var da = a[index] - meanA;
      var db = b[index] - meanB;
      num += da * db;
      denA += da * da;
      denB += db * db;
    }
    if (!denA || !denB) return null;
    return num / Math.sqrt(denA * denB);
  }

  function bestCorrelation(row, winners) {
    return winners.reduce(function(best, winner) {
      var correlation = pearsonCorrelation(portfolioReturnSeries(row), portfolioReturnSeries(winner));
      if (correlation == null) return best;
      return correlation > best.value
        ? { value: correlation, winner: winner, available: true }
        : Object.assign({}, best, { available: true });
    }, { value: -Infinity, winner: null, available: false });
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
      row.sourcePhase = valueByAliases(row, ['sourcePhase', 'Source Phase', 'Phase']);
      row.sourceDatabank = valueByAliases(row, ['sourceDatabank', 'Source Databank', 'Databank', 'Result Databank', 'Output Databank', 'Output']);
      row.forwardSource = valueByAliases(row, ['forwardSource', 'Forward Source', 'Foward Source', 'source', 'Source', 'databank', 'Databank', 'Result Databank', 'Output', 'output', 'Stage', 'Test']) || row.sourceDatabank;
      row.forwardStatus = valueByAliases(row, ['forwardStatus', 'Forward Status', 'status', 'Status', 'result', 'Result', 'Filters Result', 'passed', 'Passed']);
      row.passSource = valueByAliases(row, ['passSource', 'Pass Source', 'resultSource', 'Result Source', 'validationMode', 'Validation Mode', 'passType', 'Pass Type']);
      row.sampleOnly = markerIsExplicitTrue(valueByAliases(row, ['exampleOnly', 'Example Only', 'sampleOnly', 'Sample Only', 'demoOnly', 'Demo Only']));
      row.equitySeries = parsePortfolioSeries(valueByAliases(row, ['equitySeries', 'Equity Series', 'EquityCurve', 'Equity Curve', 'Balance Curve']));
      row.returnSeries = parsePortfolioSeries(valueByAliases(row, ['returnSeries', 'Return Series', 'Returns', 'returns', 'Monthly Returns']));
      row.forwardContract = portfolioForwardContract(row);
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

  function portfolioSettings(options) {
    var raw = Object.assign({
      similarityThreshold: 0.78,
      maxWinners: 10,
      maxPerAsset: 2,
      maxPerTimeframe: 4,
      maxPerBlockSetting: 3,
      maxPerIndicator: 3,
      maxPerCluster: 1,
      correlationThreshold: 0.50,
      minProfitFactor: 1.2,
      minTrades: 80,
      maxDrawdown: 45
    }, options || {});
    return {
      similarityThreshold: clampNumber(raw.similarityThreshold, 0.5, 0.95, 0.78),
      maxWinners: clampNumber(raw.maxWinners || raw.targetWinners, PORTFOLIO_TARGET_MIN, PORTFOLIO_TARGET_MAX, 12),
      targetMinWinners: PORTFOLIO_TARGET_MIN,
      targetMaxWinners: PORTFOLIO_TARGET_MAX,
      maxPerAsset: clampNumber(raw.maxPerAsset, 1, 4, 2),
      maxPerTimeframe: clampNumber(raw.maxPerTimeframe, 1, 6, 4),
      maxPerBlockSetting: clampNumber(raw.maxPerBlockSetting, 1, 4, 3),
      maxPerIndicator: clampNumber(raw.maxPerIndicator, 1, 4, 3),
      maxPerCluster: clampNumber(raw.maxPerCluster, 1, 3, 1),
      correlationThreshold: clampNumber(raw.correlationThreshold, 0.1, 0.95, 0.5),
      minProfitFactor: clampNumber(raw.minProfitFactor, 1, 3, 1.2),
      minTrades: clampNumber(raw.minTrades, 1, 1000, 80),
      maxDrawdown: clampNumber(raw.maxDrawdown, 1, 80, 45)
    };
  }

  function normalizePortfolioCandidate(row, index) {
    row = row || {};
    var contract = portfolioForwardContract(row);
    var candidate = {
      id: sanitizeText(row.id || ('portfolio-' + (index + 1)), 'portfolio-' + (index + 1), 90),
      importIndex: numeric(row.importIndex, index),
      strategy: sanitizeText(row.strategy || row.name || row['Strategy Name'] || row.id, 'portfolio-' + (index + 1), 140),
      asset: upper(sanitizeText(row.asset || row.symbol || row.Symbol, 'GENERIC', 40), 'GENERIC'),
      timeframe: upper(sanitizeText(row.timeframe || row.tf || row.TimeFrame, 'H1', 20), 'H1'),
      blockSetting: sanitizeText(row.blockSetting || row.BlockSetting || row.bs || 'BS_Custom', 'BS_Custom', 120),
      indicator: sanitizeText(row.indicator || row.indicatorBase || row.Indicator || 'SIN_INDICADOR', 'SIN_INDICADOR', 80),
      clusterId: sanitizeText(row.clusterId || row.cluster || row.Cluster || '', '', 40),
      sourcePhase: sanitizeText(row.sourcePhase || row.phase || row.Phase || 'phase28_capa2_forward', 'phase28_capa2_forward', 80),
      sourceDatabank: sanitizeText(row.sourceDatabank || row.forwardSource || row.Databank || '', '', 80),
      profitFactor: roundMetric(row.profitFactor, 2),
      retDd: roundMetric(row.retDd, 2),
      maxDd: roundMetric(row.maxDd, 2),
      trades: Math.round(numeric(row.trades, 0)),
      stability: roundMetric(row.stability, 2),
      winningPercent: roundMetric(row.winningPercent, 2),
      sqn: roundMetric(row.sqn, 2),
      netProfit: roundMetric(row.netProfit, 2),
      equitySeries: Array.isArray(row.equitySeries) ? row.equitySeries.slice(0, 240) : [],
      returnSeries: Array.isArray(row.returnSeries) ? row.returnSeries.slice(0, 240) : [],
      sampleOnly: !!row.sampleOnly || markerIsExplicitTrue(valueByAliases(row, ['exampleOnly', 'Example Only', 'sampleOnly', 'Sample Only', 'demoOnly', 'Demo Only'])),
      forwardSource: contract.source,
      forwardStatus: contract.status,
      passSource: contract.passSource,
      forwardContract: {
        ok: contract.ok,
        issues: contract.issues.slice()
      },
      eligibleForPortfolio: contract.ok
    };
    candidate.hasCoreMetrics = candidate.profitFactor > 0 && candidate.trades > 0 && candidate.maxDd < 100;
    return candidate;
  }

  function addCapReason(reasons, label, current, max) {
    if (current >= max) reasons.push(label + ' cap ' + current + '/' + max);
  }

  function buildRiskPlan(winners, settings, rejectedCount) {
    var count = winners.length;
    var status = count >= PORTFOLIO_TARGET_MIN && count <= PORTFOLIO_TARGET_MAX ? 'target-ready' : 'under-target';
    var statusLabel = status === 'target-ready'
      ? 'riesgo listo para despliegue gradual'
      : 'riesgo pendiente: faltan ganadores Forward/Foward';
    return {
      version: 'portfolio-risk-plan-v1',
      objective: '8-12 ganadores naturales de Forward/Foward antes de MT5 real',
      status: status,
      statusLabel: statusLabel,
      targetRange: PORTFOLIO_TARGET_MIN + '-' + PORTFOLIO_TARGET_MAX,
      selected: count,
      rejectedByContract: rejectedCount,
      allocationPerStrategyPct: 0.2,
      baseRiskPct: 0.2,
      minInitialRiskPct: 0.05,
      maxInitialRiskPct: 0.3,
      maxScaleRiskPct: 0.3,
      aggregateRisk: 'not_computable',
      fullDeploymentAllowed: false,
      caps: {
        perAsset: settings.maxPerAsset,
        perTimeframe: settings.maxPerTimeframe,
        perBlockSetting: settings.maxPerBlockSetting,
        perIndicator: settings.maxPerIndicator,
        perCluster: settings.maxPerCluster
      }
    };
  }

  function buildCorrelationStatus(settings, similarCount, comparablePairs) {
    var hasComparableSeries = numeric(comparablePairs, 0) > 0;
    return {
      state: hasComparableSeries ? 'correlation-available' : 'similarity-only',
      label: hasComparableSeries ? 'Correlacion real disponible con series comparables' : 'Similitud operativa, no correlacion de retornos',
      detail: hasComparableSeries
        ? 'Se han encontrado pares con equity/returns comparables; se aplica umbral 0.50.'
        : 'Portfolio Lab agrupa por asset, timeframe, BlockSetting, indicador y metricas. Si no hay equity/returns comparables, no se etiqueta como correlacion.',
      similarityThreshold: settings.similarityThreshold,
      correlationThreshold: settings.correlationThreshold,
      comparablePairs: numeric(comparablePairs, 0),
      similarCandidates: similarCount
    };
  }

  function buildDeploymentSteps(riskPlan, rejectedCount) {
    var ready = riskPlan && riskPlan.status === 'target-ready';
    return [
      {
        id: 'forward-contract',
        label: 'Confirmar supervivientes Forward/Foward naturales',
        status: rejectedCount ? 'blocked' : 'ready',
        detail: rejectedCount ? rejectedCount + ' fila(s) fuera de contrato' : 'source/status gobernado OK'
      },
      {
        id: 'portfolio-master-correlation',
        label: 'Medir correlacion real en Portfolio Master',
        status: 'pending',
        detail: 'La similitud del Lab no sustituye correlacion de retornos'
      },
      {
        id: 'mt5-reduced-risk',
        label: 'Desplegar MT5 con riesgo reducido',
        status: ready ? 'ready' : 'waiting',
        detail: 'Inicio sugerido 0.2% base, cap 0.30% por estrategia hasta observar convivencia'
      },
      {
        id: 'scale-portfolio',
        label: 'Escalar solo si el lote mantiene 8-12 finalistas',
        status: ready ? 'ready' : 'waiting',
        detail: ready ? 'shortlist dentro del rango objetivo' : 'completar diversidad antes de escalar'
      }
    ];
  }

  function sanitizePortfolioSettings(settings) {
    settings = portfolioSettings(settings || {});
    return {
      similarityThreshold: settings.similarityThreshold,
      maxWinners: settings.maxWinners,
      targetMinWinners: settings.targetMinWinners,
      targetMaxWinners: settings.targetMaxWinners,
      maxPerAsset: settings.maxPerAsset,
      maxPerTimeframe: settings.maxPerTimeframe,
      maxPerBlockSetting: settings.maxPerBlockSetting,
      maxPerIndicator: settings.maxPerIndicator,
      maxPerCluster: settings.maxPerCluster,
      correlationThreshold: settings.correlationThreshold,
      minProfitFactor: settings.minProfitFactor,
      minTrades: settings.minTrades,
      maxDrawdown: settings.maxDrawdown
    };
  }

  function sanitizePortfolioRow(row, index) {
    var original = row || {};
    row = Object.assign(normalizePortfolioCandidate(original, index || 0), {
      clusterRef: original.clusterRef,
      score: original.score,
      similarity: original.similarity,
      similarityLabel: original.similarityLabel,
      correlation: original.correlation,
      correlationStatus: original.correlationStatus,
      closestStrategy: original.closestStrategy,
      diversityStatus: original.diversityStatus,
      decision: original.decision,
      reason: original.reason,
      riskPct: original.riskPct
    });
    return {
      id: row.id,
      importIndex: row.importIndex,
      strategy: row.strategy,
      asset: row.asset,
      timeframe: row.timeframe,
      blockSetting: row.blockSetting,
      indicator: row.indicator,
      clusterId: row.clusterId,
      clusterRef: sanitizeText(row.clusterRef || row.clusterId || '', '', 40),
      profitFactor: row.profitFactor,
      retDd: row.retDd,
      maxDd: row.maxDd,
      trades: row.trades,
      stability: row.stability,
      winningPercent: row.winningPercent,
      sqn: row.sqn,
      netProfit: row.netProfit,
      score: roundMetric(row.score, 2),
      similarity: roundMetric(row.similarity, 2),
      similarityLabel: sanitizeText(row.similarityLabel || 'similitud operativa', 'similitud operativa', 120),
      correlation: row.correlation == null ? null : roundMetric(row.correlation, 2),
      correlationStatus: sanitizeText(row.correlationStatus || 'not_available', 'not_available', 40),
      closestStrategy: sanitizeText(row.closestStrategy || '', '', 140),
      diversityStatus: ['portfolio', 'similar', 'review'].indexOf(row.diversityStatus) !== -1 ? row.diversityStatus : 'review',
      decision: sanitizeText(row.decision || 'Revisar', 'Revisar', 40),
      reason: sanitizeText(row.reason || '', '', 220),
      riskPct: row.riskPct == null ? null : roundMetric(row.riskPct, 2),
      eligibleForPortfolio: !!row.eligibleForPortfolio,
      sourcePhase: sanitizeText(row.sourcePhase || 'phase28_capa2_forward', 'phase28_capa2_forward', 80),
      sourceDatabank: sanitizeText(row.sourceDatabank || row.forwardSource || '', '', 80),
      forwardSource: row.forwardSource,
      forwardStatus: row.forwardStatus,
      passSource: row.passSource,
      forwardContract: {
        ok: !!(row.forwardContract && row.forwardContract.ok),
        issues: row.forwardContract && Array.isArray(row.forwardContract.issues)
          ? row.forwardContract.issues.map(function(issue) { return sanitizeText(issue, '', 80); }).filter(Boolean)
          : []
      }
    };
  }

  function sanitizePortfolioReport(report) {
    report = report || {};
    var settings = sanitizePortfolioSettings(report.settings || {});
    var rows = (Array.isArray(report.rows) ? report.rows : []).map(sanitizePortfolioRow);
    var counts = rows.reduce(function(acc, row) {
      acc[row.diversityStatus] = (acc[row.diversityStatus] || 0) + 1;
      if (!row.eligibleForPortfolio) acc.rejected += 1;
      return acc;
    }, { portfolio: 0, similar: 0, review: 0, rejected: 0 });
    var uniqueAssets = {};
    rows.forEach(function(row) { uniqueAssets[normalizeKey(row.asset)] = true; });
    var riskPlan = report.riskPlan || buildRiskPlan(rows.filter(function(row) { return row.diversityStatus === 'portfolio'; }), settings, counts.rejected);
    var correlationStatus = report.correlationStatus || buildCorrelationStatus(settings, counts.similar || 0);
    return {
      version: PORTFOLIO_LAB_VERSION,
      analyzedAt: report.analyzedAt || new Date().toISOString(),
      sourcePhase: sanitizeText(report.sourcePhase || 'phase28_capa2_forward', 'phase28_capa2_forward', 80),
      sourceDatabank: sanitizeText(report.sourceDatabank || 'Foward', 'Foward', 80),
      selectionMode: sanitizeText(report.selectionMode || 'governed-post-forward', 'governed-post-forward', 80),
      total: rows.length,
      winners: counts.portfolio || 0,
      similar: counts.similar || 0,
      review: counts.review || 0,
      rejected: counts.rejected || 0,
      uniqueAssets: Object.keys(uniqueAssets).filter(Boolean).length,
      settings: settings,
      riskPlan: {
        version: sanitizeText(riskPlan.version || 'portfolio-risk-plan-v1'),
        objective: sanitizeText(riskPlan.objective || '8-12 ganadores naturales de Forward/Foward antes de MT5 real', '', 180),
        status: sanitizeText(riskPlan.status || 'under-target', '', 40),
        statusLabel: sanitizeText(riskPlan.statusLabel || 'riesgo pendiente', '', 120),
        targetRange: sanitizeText(riskPlan.targetRange || (PORTFOLIO_TARGET_MIN + '-' + PORTFOLIO_TARGET_MAX), '', 20),
        selected: numeric(riskPlan.selected, counts.portfolio || 0),
        rejectedByContract: numeric(riskPlan.rejectedByContract, counts.rejected || 0),
        allocationPerStrategyPct: roundMetric(riskPlan.allocationPerStrategyPct, 2),
        baseRiskPct: roundMetric(riskPlan.baseRiskPct, 2),
        minInitialRiskPct: roundMetric(riskPlan.minInitialRiskPct, 2),
        maxInitialRiskPct: roundMetric(riskPlan.maxInitialRiskPct, 2),
        maxScaleRiskPct: roundMetric(riskPlan.maxScaleRiskPct, 2),
        aggregateRisk: sanitizeText(riskPlan.aggregateRisk || 'not_computable', '', 60),
        fullDeploymentAllowed: !!riskPlan.fullDeploymentAllowed,
        caps: {
          perAsset: numeric(riskPlan.caps && riskPlan.caps.perAsset, settings.maxPerAsset),
          perTimeframe: numeric(riskPlan.caps && riskPlan.caps.perTimeframe, settings.maxPerTimeframe),
          perBlockSetting: numeric(riskPlan.caps && riskPlan.caps.perBlockSetting, settings.maxPerBlockSetting),
          perIndicator: numeric(riskPlan.caps && riskPlan.caps.perIndicator, settings.maxPerIndicator),
          perCluster: numeric(riskPlan.caps && riskPlan.caps.perCluster, settings.maxPerCluster)
        }
      },
      correlationStatus: {
        state: sanitizeText(correlationStatus.state || 'similarity-only', '', 40),
        label: sanitizeText(correlationStatus.label || 'Similitud operativa, no correlacion de retornos', '', 140),
        detail: sanitizeText(correlationStatus.detail || '', '', 240),
        similarityThreshold: roundMetric(correlationStatus.similarityThreshold || settings.similarityThreshold, 2),
        correlationThreshold: roundMetric(correlationStatus.correlationThreshold || settings.correlationThreshold, 2),
        comparablePairs: numeric(correlationStatus.comparablePairs, 0),
        similarCandidates: numeric(correlationStatus.similarCandidates, counts.similar || 0)
      },
      deploymentSteps: (Array.isArray(report.deploymentSteps) ? report.deploymentSteps : buildDeploymentSteps(riskPlan, counts.rejected)).map(function(step) {
        return {
          id: sanitizeText(step.id || '', '', 60),
          label: sanitizeText(step.label || '', '', 160),
          status: sanitizeText(step.status || 'pending', '', 40),
          detail: sanitizeText(step.detail || '', '', 200)
        };
      }),
      rows: rows
    };
  }

  function portfolioIdentity(row) {
    return normalizeKey((row && (row.strategy || row.id)) || '');
  }

  function selectedPortfolioRows(report) {
    return (report && Array.isArray(report.rows) ? report.rows : []).filter(function(row) {
      return row && row.diversityStatus === 'portfolio';
    });
  }

  function parseMasterRows(input) {
    if (Array.isArray(input)) return input.map(function(row, index) { return normalizePortfolioCandidate(row, index); });
    return parsePortfolioRows(input || '').map(function(row, index) { return normalizePortfolioCandidate(row, index); });
  }

  function sanitizeAccountBrokerContext(context) {
    var allowed = {
      accounttype: 'accountType',
      accountmodel: 'accountModel',
      mode: 'accountModel',
      environment: 'environment',
      broker: 'brokerProfile',
      brokerprofile: 'brokerProfile',
      executionmodel: 'executionModel',
      executionvenue: 'executionModel',
      basecurrency: 'baseCurrency',
      currency: 'baseCurrency',
      riskbudgetmode: 'riskBudgetMode',
      riskmodel: 'riskBudgetMode',
      leveragemode: 'leverageMode',
      notes: 'notes'
    };
    var output = {
      provided: false,
      status: 'blocked',
      publicSummary: '',
      accountType: '',
      accountModel: '',
      environment: '',
      brokerProfile: '',
      executionModel: '',
      baseCurrency: '',
      riskBudgetMode: '',
      leverageMode: '',
      privateFieldsRemoved: 0
    };
    if (context && typeof context === 'object' && !Array.isArray(context)) {
      Object.keys(context).forEach(function(key) {
        var mapped = allowed[normalizeKey(key)];
        var value = context[key];
        if (mapped) {
          output[mapped] = sanitizePrivateText(value, '', mapped === 'notes' ? 180 : 80);
        } else if (safeString(value)) {
          output.privateFieldsRemoved += 1;
        }
      });
    } else {
      output.publicSummary = sanitizePrivateText(context, '', 260);
      output.privateFieldsRemoved += countPrivacyMarkers(context);
    }
    output.provided = !!(output.publicSummary || output.accountType || output.accountModel || output.environment || output.brokerProfile || output.executionModel || output.baseCurrency || output.riskBudgetMode || output.leverageMode);
    output.status = output.provided ? 'ready' : 'blocked';
    return output;
  }

  function sanitizePortfolioMasterContext(context, kind) {
    var clean = sanitizeAccountBrokerContext(context);
    var accountProvided = !!(clean.publicSummary || clean.accountType || clean.accountModel || clean.environment || clean.baseCurrency || clean.riskBudgetMode);
    var brokerProvided = !!(clean.publicSummary || clean.brokerProfile || clean.executionModel || clean.leverageMode);
    clean.kind = kind;
    clean.provided = kind === 'broker' ? brokerProvided : accountProvided;
    clean.status = clean.provided ? 'ready' : 'blocked';
    return clean;
  }

  function buildForwardCsvReadback(input, selected) {
    var rows = parseMasterRows(input);
    var byKey = {};
    var validRows = 0;
    var sampleRows = 0;
    rows.forEach(function(row) {
      var key = portfolioIdentity(row);
      if (row.sampleOnly) sampleRows += 1;
      if (row.eligibleForPortfolio && !row.sampleOnly) validRows += 1;
      if (key && row.eligibleForPortfolio && !row.sampleOnly && !byKey[key]) byKey[key] = row;
    });
    var missing = (selected || []).filter(function(row) {
      return !byKey[portfolioIdentity(row)];
    }).map(function(row) {
      return sanitizeText(row.strategy || row.id, '', 120);
    });
    var selectedCount = (selected || []).length;
    var status = rows.length && selectedCount && !missing.length ? 'ready' : 'blocked';
    return {
      status: status,
      rowCount: rows.length,
      validRows: validRows,
      sampleRows: sampleRows,
      rejectedRows: Math.max(0, rows.length - validRows - sampleRows),
      matchedPortfolioWinners: Math.max(0, selectedCount - missing.length),
      missingPortfolioWinners: missing.slice(0, 12),
      detail: status === 'ready'
        ? 'Forward/Foward CSV reconciliado con la shortlist portfolio.'
        : (sampleRows ? 'CSV de ejemplo detectado; falta evidencia Forward/Foward real del operador.' : (rows.length ? 'Faltan ganadores de la shortlist en el CSV Forward/Foward.' : 'Falta CSV Forward/Foward de readback.'))
    };
  }

  function masterSeriesFromRow(row) {
    var returns = portfolioReturnSeries(row);
    return returns.length >= PORTFOLIO_MASTER_MIN_OBSERVATIONS ? returns : [];
  }

  function pairCorrelationStats(items) {
    var values = [];
    for (var i = 0; i < items.length; i += 1) {
      for (var j = i + 1; j < items.length; j += 1) {
        var corr = pearsonCorrelation(items[i].series, items[j].series);
        if (corr != null) values.push(corr);
      }
    }
    if (!values.length) {
      return { pairs: 0, averagePairCorrelation: null, maxPairCorrelation: null, maxAbsPairCorrelation: null };
    }
    var total = values.reduce(function(sum, item) { return sum + item; }, 0);
    var max = values.reduce(function(best, item) { return Math.max(best, item); }, -Infinity);
    var maxAbs = values.reduce(function(best, item) { return Math.max(best, Math.abs(item)); }, 0);
    return {
      pairs: values.length,
      averagePairCorrelation: roundMetric(total / values.length, 3),
      maxPairCorrelation: roundMetric(max, 3),
      maxAbsPairCorrelation: roundMetric(maxAbs, 3)
    };
  }

  function buildComparableSeriesReadback(input, selected) {
    var rows = parseMasterRows(input);
    var seriesByKey = {};
    rows.forEach(function(row) {
      var key = portfolioIdentity(row);
      var series = masterSeriesFromRow(row);
      if (key && series.length && !seriesByKey[key]) {
        seriesByKey[key] = {
          strategy: sanitizeText(row.strategy || row.id, '', 120),
          series: series,
          observations: series.length
        };
      }
    });
    var missing = [];
    var matched = [];
    (selected || []).forEach(function(row) {
      var item = seriesByKey[portfolioIdentity(row)];
      if (item) matched.push(item);
      else missing.push(sanitizeText(row.strategy || row.id, '', 120));
    });
    var selectedCount = (selected || []).length;
    var lengths = matched.map(function(item) { return item.observations; });
    var sharedObservations = lengths.length ? Math.min.apply(Math, lengths) : 0;
    var sameWindow = lengths.length > 1 && lengths.every(function(length) { return length === lengths[0]; });
    var stats = sameWindow ? pairCorrelationStats(matched) : pairCorrelationStats([]);
    var ready = !!(rows.length && selectedCount > 1 && matched.length === selectedCount && sameWindow && stats.pairs);
    return {
      status: ready ? 'ready' : 'blocked',
      aggregateRiskStatus: ready ? 'true_aggregate_risk_ready' : (rows.length ? 'not_comparable' : 'unavailable'),
      rowCount: rows.length,
      matchedPortfolioWinners: matched.length,
      missingPortfolioWinners: missing.slice(0, 12),
      sharedObservations: sharedObservations,
      sameComparableWindow: sameWindow,
      comparablePairs: stats.pairs,
      averagePairCorrelation: stats.averagePairCorrelation,
      maxPairCorrelation: stats.maxPairCorrelation,
      maxAbsPairCorrelation: stats.maxAbsPairCorrelation,
      detail: ready
        ? 'Series equity/returns comparables para calcular riesgo agregado real en Portfolio Master.'
        : (rows.length ? 'Series presentes pero no cubren todos los ganadores con la misma ventana comparable.' : 'Faltan equity/returns comparables para riesgo agregado real.')
    };
  }

  function requirement(id, label, status, detail) {
    return {
      id: id,
      label: label,
      required: true,
      status: status,
      detail: detail
    };
  }

  function sanitizePortfolioMasterContract(payload) {
    return buildPortfolioMasterContract(payload);
  }

  function buildPortfolioMasterContract(payload) {
    payload = payload || {};
    var hasLabInput = !!(payload.labReport && Array.isArray(payload.labReport.rows));
    var lab = hasLabInput ? sanitizePortfolioReport(payload.labReport) : null;
    var selected = selectedPortfolioRows(lab);
    var labReady = !!(lab && lab.version === PORTFOLIO_LAB_VERSION && lab.total && selected.length >= PORTFOLIO_TARGET_MIN && selected.length <= PORTFOLIO_TARGET_MAX);
    var forwardCsv = buildForwardCsvReadback(payload.forwardCsv || payload.forwardRows || '', selected);
    var comparableSeries = buildComparableSeriesReadback(payload.comparableSeriesCsv || payload.comparableSeries || payload.returnSeriesCsv || payload.equityReturns || '', selected);
    var accountContext = sanitizePortfolioMasterContext(payload.accountContext || payload.accountBrokerContext || '', 'account');
    var brokerContext = sanitizePortfolioMasterContext(payload.brokerContext || payload.accountBrokerContext || '', 'broker');
    var requiredInputs = [
      requirement(
        'lab-report',
        'Lab report gobernado',
        labReady ? 'ready' : 'blocked',
        lab ? (lab.winners + ' ganador(es) portfolio en ' + lab.version) : 'Falta ejecutar Portfolio Lab gobernado.'
      ),
      requirement('forward-csv', 'Forward CSV readback', forwardCsv.status, forwardCsv.detail),
      requirement('comparable-equity-returns', 'Equity/returns comparables', comparableSeries.status, comparableSeries.detail),
      requirement(
        'account-context',
        'Contexto cuenta publico',
        accountContext.status,
        accountContext.provided ? 'Contexto publico de cuenta suficiente para readback.' : 'Falta contexto de cuenta sin campos privados.'
      ),
      requirement(
        'broker-context',
        'Contexto broker/simbolos publico',
        brokerContext.status,
        brokerContext.provided ? 'Contexto publico broker/simbolos suficiente para readback.' : 'Falta contexto broker/simbolos sin campos privados.'
      )
    ];
    var blockedReasons = requiredInputs.filter(function(item) {
      return item.status !== 'ready';
    }).map(function(item) {
      return item.label + ': ' + item.detail;
    });
    var ready = !blockedReasons.length;
    return {
      version: PORTFOLIO_MASTER_VERSION,
      encodedAt: payload.encodedAt || new Date().toISOString(),
      sourceLayer: 'portfolio-master-after-governed-lab',
      sourcePhase: lab ? lab.sourcePhase : 'phase28_capa2_forward',
      sourceDatabank: lab ? lab.sourceDatabank : 'Foward',
      status: ready ? 'ready_for_master_review' : 'blocked_pending_operator_inputs',
      statusLabel: ready ? 'listo para readback en Portfolio Master' : 'bloqueado por prerrequisitos',
      inputIntake: {
        version: PORTFOLIO_MASTER_INPUTS_VERSION,
        phase: 'phase30_capa2_portfolio_master_inputs_pending',
        status: ready ? 'ready_for_operator_review' : 'pending_inputs',
        readyForOperatorReview: ready,
        providedInputs: requiredInputs.filter(function(item) { return item.status === 'ready'; }).map(function(item) { return item.id; }),
        missingInputs: requiredInputs.filter(function(item) { return item.status !== 'ready'; }).map(function(item) { return item.id; }),
        cfxGuardRequired: true,
        processesRequired: []
      },
      artifactGenerationStatus: 'blocked',
      artifactGenerationAllowed: false,
      sqxExecutionAllowed: false,
      fitPortfolioAllowed: false,
      forcedPassAllowed: false,
      deploymentClaim: 'none',
      liveDeploymentAllowed: false,
      requiredInputs: requiredInputs,
      blockedReasons: blockedReasons,
      labReadback: lab ? {
        version: lab.version,
        sourcePhase: lab.sourcePhase,
        sourceDatabank: lab.sourceDatabank,
        selectionMode: lab.selectionMode,
        total: lab.total,
        winners: lab.winners,
        riskPlanStatus: lab.riskPlan && lab.riskPlan.status,
        aggregateRiskFromLab: lab.riskPlan && lab.riskPlan.aggregateRisk
      } : null,
      inputReadback: {
        forwardCsv: forwardCsv,
        comparableSeries: comparableSeries,
        accountContext: accountContext,
        brokerContext: brokerContext,
        accountBrokerContext: {
          status: accountContext.status === 'ready' && brokerContext.status === 'ready' ? 'ready' : 'blocked',
          privateFieldsRemoved: accountContext.privateFieldsRemoved + brokerContext.privateFieldsRemoved
        }
      },
      outputReadback: {
        contract: 'sanitized-readback-only',
        portfolioMasterVersion: PORTFOLIO_MASTER_VERSION,
        shortlistSize: selected.length,
        aggregateRisk: {
          status: comparableSeries.aggregateRiskStatus,
          trueAggregateRiskAvailable: ready && comparableSeries.aggregateRiskStatus === 'true_aggregate_risk_ready',
          basis: ready ? 'comparable_return_series' : 'unavailable_until_required_inputs_present',
          comparablePairs: comparableSeries.comparablePairs,
          sharedObservations: comparableSeries.sharedObservations,
          averagePairCorrelation: comparableSeries.averagePairCorrelation,
          maxPairCorrelation: comparableSeries.maxPairCorrelation,
          maxAbsPairCorrelation: comparableSeries.maxAbsPairCorrelation,
          note: 'Readback publico; no autoriza despliegue real ni sustituye recalculo en Portfolio Master.'
        },
        selectedStrategies: selected.map(function(row) {
          return {
            id: sanitizeText(row.id, '', 90),
            strategy: sanitizeText(row.strategy, '', 140),
            asset: sanitizeText(row.asset, '', 40),
            timeframe: sanitizeText(row.timeframe, '', 20),
            forwardSource: sanitizeText(row.forwardSource, '', 80),
            riskPct: row.riskPct == null ? null : roundMetric(row.riskPct, 2)
          };
        })
      },
      privacy: {
        publicSafe: true,
        rawLocalPathsAllowed: false,
        privateFieldsAllowed: false,
        privateFieldsRemoved: accountContext.privateFieldsRemoved + brokerContext.privateFieldsRemoved
      },
      readbackSteps: [
        { id: 'master-prerequisites', label: 'Confirmar prerrequisitos Portfolio Master', status: ready ? 'ready' : 'blocked' },
        { id: 'aggregate-risk-readback', label: 'Recalcular riesgo agregado con series comparables', status: ready ? 'ready' : 'blocked' },
        { id: 'operator-review', label: 'Revision humana externa antes de cualquier accion real', status: 'required' }
      ]
    };
  }

  var BACKPORT_OPERATOR_OPERATIONS = [
    {
      id: 'mcp-status',
      label: 'MCP-like status',
      method: 'GET',
      endpoint: '/sqx142/mcp-like/status',
      expectedVersion: 'sqx142-mcp-like-readonly-v1'
    },
    {
      id: 'results-readiness',
      label: 'Results Plugin readiness',
      method: 'GET',
      endpoint: '/sqx142/mcp-like/results-plugin-readiness',
      expectedVersion: 'sqx142-mcp-like-readonly-v1'
    },
    {
      id: 'correlation-filter',
      label: 'Correlation Filter external',
      method: 'POST',
      endpoint: '/sqx142/correlation-filter/external',
      expectedVersion: 'sqx142-correlation-filter-external-v1'
    },
    {
      id: 'portfolio-correlation-stability',
      label: 'Capa2 Portfolio CORR1 stability audit',
      method: 'POST',
      endpoint: '/sqx142/portfolio-correlation/stability-audit',
      expectedVersion: PORTFOLIO_CORRELATION_STABILITY_VERSION
    },
    {
      id: 'capa1-c2-correlation-selection',
      label: 'Capa1 C2 template correlation selection',
      method: 'POST',
      endpoint: '/sqx142/capa1-c2-correlation/stability-audit',
      expectedVersion: CAPA1_C2_CORRELATION_SELECTION_VERSION
    },
    {
      id: 'monte-carlo-benchmarks',
      label: 'Monte Carlo benchmarks',
      method: 'POST',
      endpoint: '/sqx142/monte-carlo/benchmarks',
      expectedVersion: 'sqx142-monte-carlo-candidate-benchmarks-v1'
    },
    {
      id: 'mt5-data-probe',
      label: 'MT5 data intake probe',
      method: 'POST',
      endpoint: '/sqx142/mt5-data-intake/probe',
      expectedVersion: 'sqx142-mt5-data-intake-probe-v1'
    },
    {
      id: 'migration-checklist',
      label: 'Copy-only migration checklist',
      method: 'POST',
      endpoint: '/sqx142/migration/copy-only-checklist',
      expectedVersion: 'sqx142-copy-only-migration-checklist-v1'
    }
  ];

  function backportOperatorOperations() {
    return BACKPORT_OPERATOR_OPERATIONS.map(function(item) { return Object.assign({}, item); });
  }

  function backportOperatorOperation(operationId) {
    var id = safeString(operationId, 'mcp-status');
    return BACKPORT_OPERATOR_OPERATIONS.find(function(item) { return item.id === id; }) || BACKPORT_OPERATOR_OPERATIONS[0];
  }

  function safeJsonObject(text) {
    try {
      var parsed = JSON.parse(String(text || ''));
      return parsed && typeof parsed === 'object' ? parsed : null;
    } catch (_err) {
      return null;
    }
  }

  function parseBackportCsvRows(text) {
    var lines = String(text || '').split(/\r?\n/).map(function(line) { return line.trim(); }).filter(Boolean);
    if (!lines.length) return [];
    var delimiter = detectDelimiter(lines[0]);
    var headers = splitDelimitedLine(lines[0], delimiter);
    return lines.slice(1).map(function(line) {
      var values = splitDelimitedLine(line, delimiter);
      return headers.reduce(function(row, header, index) {
        row[header] = values[index] == null ? '' : values[index];
        return row;
      }, {});
    });
  }

  function backportValueByAliases(row, aliases, fallback) {
    row = row || {};
    for (var i = 0; i < aliases.length; i += 1) {
      if (row[aliases[i]] != null && row[aliases[i]] !== '') return row[aliases[i]];
    }
    var normalized = {};
    Object.keys(row).forEach(function(key) {
      normalized[normalizeKey(key)] = row[key];
    });
    for (var j = 0; j < aliases.length; j += 1) {
      var value = normalized[normalizeKey(aliases[j])];
      if (value != null && value !== '') return value;
    }
    return fallback || '';
  }

  function migrationItemsFromText(text) {
    var parsed = safeJsonObject(text);
    if (parsed && Array.isArray(parsed.items)) return parsed.items;
    if (Array.isArray(parsed)) return parsed;
    var rows = parseBackportCsvRows(text);
    if (rows.length) {
      return rows.map(function(row, index) {
        return {
          kind: backportValueByAliases(row, ['kind', 'type'], 'operator_item'),
          label: backportValueByAliases(row, ['label', 'name'], 'operator item ' + (index + 1)),
          relativePath: backportValueByAliases(row, ['relativePath', 'path', 'target'], ''),
          operation: backportValueByAliases(row, ['operation', 'action'], 'copy_review')
        };
      });
    }
    return String(text || '').split(/\r?\n/).map(function(line, index) {
      return {
        kind: 'operator_line',
        label: line.trim() || 'operator item ' + (index + 1),
        relativePath: line.trim(),
        operation: 'copy_review'
      };
    }).filter(function(item) { return item.relativePath || item.label; });
  }

  function backportOperatorSample(operationId) {
    var operation = backportOperatorOperation(operationId).id;
    if (operation === 'portfolio-correlation-stability' || operation === 'capa1-c2-correlation-selection') {
      return [
        'strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,blockSetting,isReturnSeries,oos3ReturnSeries',
        'AUDCAD_H1_A,AUDCAD,H1,1.55,5.4,18,160,BS_Momentum_v6,0.01|0.02|-0.01|0.03|0.02|0.01|0.00|0.02|0.01|0.01|0.02|0.00,0.006|0.004|-0.003|0.009|0.002|-0.001|0.008|0.004|-0.002|0.007|0.003|0.005',
        'AUDCAD_H1_B,AUDCAD,H1,1.48,4.9,20,150,BS_Momentum_v6,-0.01|0.01|0.00|0.02|-0.01|0.01|0.02|-0.01|0.00|0.01|0.02|-0.01,-0.002|0.006|0.003|-0.001|0.008|0.002|0.004|-0.003|0.006|0.003|-0.001|0.005'
      ].join('\n');
    }
    if (operation === 'correlation-filter' || operation === 'monte-carlo-benchmarks') {
      return [
        'strategy,asset,timeframe,Source Phase,Source Databank,Forward Status,Pass Source,returnSeries,equitySeries',
        'AUDCAD_H4_A,AUDCAD,H4,phase28_capa2_forward,Foward,PASSED,natural,0.01|0.02|-0.01|0.03,10000|10100|10302|10199|10504',
        'AUDCAD_H1_B,AUDCAD,H1,phase28_capa2_forward,Foward,PASSED,natural,0.008|0.012|-0.006|0.018,10000|10080|10201|10140|10322',
        'XAUUSD_H1_C,XAUUSD,H1,phase28_capa2_forward,Forward,PASSED,natural,0.012|-0.004|0.018|0.006,10000|10120|10080|10261|10322'
      ].join('\n');
    }
    if (operation === 'mt5-data-probe') {
      return [
        'time,open,high,low,close,volume',
        '2026-01-02 00:00:00,1.1000,1.1020,1.0990,1.1010,120',
        '2026-01-02 01:00:00,1.1010,1.1030,1.1000,1.1022,118',
        '2026-01-02 02:00:00,1.1022,1.1040,1.1015,1.1031,121',
        '2026-01-02 03:00:00,1.1031,1.1045,1.1020,1.1028,119'
      ].join('\n');
    }
    if (operation === 'migration-checklist') {
      return [
        'kind,label,relativePath,operation',
        'results_plugin_owned,SQX Edge Readiness Panel,user/extend/ResultsPlugins/SQX Edge Readiness Panel,copy_folder',
        'project_copy,Operator-selected project copy,user/projects/operator-selected-copy,copy_folder_after_backup',
        'license_material,License material,license/activation,never_copy'
      ].join('\n');
    }
    return '';
  }

  function buildBackportOperatorPayload(operationId, input, options) {
    var operation = backportOperatorOperation(operationId);
    options = options || {};
    if (operation.method === 'GET') return null;
    var parsed = safeJsonObject(input);
    if (operation.id === 'correlation-filter') {
      if (parsed) return Object.assign({ includeCsvExport: true, includeSqxTagCsv: true }, parsed);
      return {
        csv: String(input || ''),
        settings: {
          maxCorrelation: numeric(options.maxCorrelation, 0.50),
          warnCorrelation: numeric(options.warnCorrelation, 0.35),
          minComparablePoints: numeric(options.minComparablePoints, 12),
          similarityThreshold: numeric(options.similarityThreshold, 0.78)
        },
        includeCsvExport: true,
        includeSqxTagCsv: true
      };
    }
    if (operation.id === 'portfolio-correlation-stability' || operation.id === 'capa1-c2-correlation-selection') {
      return parsed || {
        csv: String(input || ''),
        settings: {
          maxIsCorrelation: numeric(options.maxIsCorrelation || options.maxCorrelation, 0.50),
          maxOos3Correlation: numeric(options.maxOos3Correlation, 0.60),
          warnOos3Correlation: numeric(options.warnOos3Correlation, 0.45),
          maxCorrelationDrift: numeric(options.maxCorrelationDrift, 0.25),
          minComparablePoints: numeric(options.minComparablePoints, 12)
        },
        includeCsvExport: true
      };
    }
    if (operation.id === 'monte-carlo-benchmarks') {
      return parsed || {
        csv: String(input || ''),
        settings: {
          simulations: numeric(options.simulations, 64),
          blockSize: numeric(options.blockSize, 4),
          parameterJitterPct: numeric(options.parameterJitterPct, 0.15),
          executionDegradeBps: numeric(options.executionDegradeBps, 2.0)
        },
        includeCsvExport: true
      };
    }
    if (operation.id === 'mt5-data-probe') {
      return parsed || {
        csv: String(input || ''),
        asset: sanitizeText(options.asset, 'UNKNOWN', 40),
        timeframe: upper(options.timeframe, 'UNKNOWN'),
        settings: {
          minBars: numeric(options.minBars, 20),
          minOverlapDays: numeric(options.minOverlapDays, 1)
        },
        includeCsvExport: true
      };
    }
    if (operation.id === 'migration-checklist') {
      return parsed || {
        items: migrationItemsFromText(input),
        includeCsvExport: true
      };
    }
    return parsed || { rows: parseBackportCsvRows(input), includeCsvExport: true };
  }

  function summarizeBackportOperatorResult(operationId, report) {
    var operation = backportOperatorOperation(operationId);
    report = report || {};
    var summary = report.summary && typeof report.summary === 'object' ? report.summary : {};
    var privacy = report.privacy && typeof report.privacy === 'object' ? report.privacy : {};
    var guards = report.guards && typeof report.guards === 'object' ? report.guards : {};
    var rawStatus = report.decision || report.status || report.error || (report.ok === false ? 'blocked' : 'ok');
    return {
      panelVersion: BACKPORT_OPERATOR_PANEL_VERSION,
      operationId: operation.id,
      label: operation.label,
      endpoint: operation.endpoint,
      method: operation.method,
      expectedVersion: operation.expectedVersion,
      responseVersion: safeString(report.version),
      ok: report.ok !== false && !report.error,
      status: safeString(rawStatus, 'ok'),
      total: numeric(summary.total || summary.inputRows || summary.inputItems || report.total, 0),
      primaryCount: numeric(summary.portfolio || summary.selectedByIs || summary.benchmarkPass || summary.validBars || summary.allowCopy || report.winners, 0),
      reviewCount: numeric(summary.review || summary.benchmarkReview || summary.reviewCopy || summary.catalogMatches || report.review, 0),
      blockCount: numeric(summary.blocked || summary.benchmarkFail || summary.invalidRows || summary.blockCopy || report.rejected, 0),
      csvExportAvailable: !!report.csvExport,
      sqxTagCsvAvailable: !!report.sqxTagCsv,
      localOnly: privacy.local_paths_returned === false || privacy.localPathsReturned === false || true,
      remoteTesterBlocked: guards.remote_tester_access === false || report.error === 'local_operator_required',
      sqxRuntimeStarted: guards.sqx_runtime_started === true || guards.sqxRuntimeStarted === true,
      dataDbWriteAllowed: guards.data_db_write_allowed === true || guards.dataDbWriteAllowed === true,
      raw: report
    };
  }

  function recordBackportOperatorResult(operationId, report) {
    var clean = summarizeBackportOperatorResult(operationId, report || {});
    clean.recordedAt = new Date().toISOString();
    var state = readState();
    var history = pushRecent((state.backportOperatorPanel && state.backportOperatorPanel.history) || [], clean, 8);
    return saveEvent({
      backportOperatorPanel: {
        version: BACKPORT_OPERATOR_PANEL_VERSION,
        lastOperation: clean,
        history: history
      }
    }, [], null, 'ui-integration1-backport-operator-panel');
  }

  function buildPortfolioShortlist(inputRows, options) {
    var settings = portfolioSettings(options || {});
    var rows = (Array.isArray(inputRows) ? inputRows : parsePortfolioRows(inputRows)).map(function(row, index) {
      var candidate = normalizePortfolioCandidate(row, index);
      candidate.score = scoreCandidate(candidate);
      return candidate;
    }).sort(function(a, b) {
      return b.score - a.score || a.importIndex - b.importIndex;
    });
    var winners = [];
    var perAsset = {};
    var perTimeframe = {};
    var perBlockSetting = {};
    var perIndicator = {};
    var perCluster = {};
    rows.forEach(function(row) {
      var closest = winners.reduce(function(best, winner) {
        var sim = similarity(row, winner);
        return sim > best.value ? { value: sim, winner: winner } : best;
      }, { value: 0, winner: null });
      var corr = bestCorrelation(row, winners);
      row.similarity = Math.round(closest.value * 100) / 100;
      row.correlation = corr.available && corr.value !== -Infinity ? roundMetric(corr.value, 2) : null;
      row.correlationStatus = corr.available ? 'available' : 'not_available';
      row.similarityLabel = corr.available ? 'correlacion real disponible' : 'similitud operativa, no correlacion real';
      row.closestStrategy = closest.winner ? closest.winner.strategy : '';
      row.clusterRef = row.clusterId || 'CL' + String(winners.length + 1).padStart(2, '0');
      var assetKey = normalizeKey(row.asset);
      var assetCount = perAsset[assetKey] || 0;
      var timeframeKey = normalizeKey(row.timeframe);
      var timeframeCount = perTimeframe[timeframeKey] || 0;
      var blockKey = normalizeKey(row.blockSetting);
      var blockCount = perBlockSetting[blockKey] || 0;
      var indicatorKey = normalizeKey(row.indicator);
      var indicatorCount = perIndicator[indicatorKey] || 0;
      var clusterKey = normalizeKey(row.clusterRef || row.clusterId);
      var clusterCount = perCluster[clusterKey] || 0;
      var reasons = [];
      if (!row.eligibleForPortfolio) reasons.push('rechazado: ' + row.forwardContract.issues.join(' · '));
      if (!row.hasCoreMetrics) reasons.push('faltan métricas núcleo');
      if (row.profitFactor < settings.minProfitFactor) reasons.push('PF bajo');
      if (row.trades < settings.minTrades) reasons.push('pocos trades');
      if (row.maxDd > settings.maxDrawdown) reasons.push('DD alto');
      addCapReason(reasons, 'asset', assetCount, settings.maxPerAsset);
      addCapReason(reasons, 'timeframe', timeframeCount, settings.maxPerTimeframe);
      addCapReason(reasons, 'BlockSetting', blockCount, settings.maxPerBlockSetting);
      addCapReason(reasons, 'indicador', indicatorCount, settings.maxPerIndicator);
      if (clusterCount >= settings.maxPerCluster && winners.length >= settings.targetMinWinners) reasons.push('cluster cap ' + clusterCount + '/' + settings.maxPerCluster);
      if (winners.length >= settings.maxWinners) reasons.push('límite objetivo 8-12');
      if (!reasons.length && corr.available && corr.value >= settings.correlationThreshold) reasons.push('correlacion real >= ' + settings.correlationThreshold + ' con ' + corr.winner.strategy);
      if (!reasons.length && !corr.available && closest.value >= settings.similarityThreshold) reasons.push('similitud operativa >= ' + settings.similarityThreshold + ' con ' + closest.winner.strategy + ' (no correlacion real)');
      if (!reasons.length) {
        row.diversityStatus = 'portfolio';
        row.decision = 'Portfolio';
        row.reason = 'ganador Forward/Foward natural y diverso';
        row.riskPct = Math.min(0.3, Math.max(0.05, roundMetric(0.2 * Math.min(1.25, Math.max(0.4, row.profitFactor / 1.45)) * Math.min(1.25, Math.max(0.4, row.retDd / 4)) * Math.min(1.15, Math.max(0.45, 25 / Math.max(8, row.maxDd))), 2)));
        winners.push(row);
        perAsset[assetKey] = assetCount + 1;
        perTimeframe[timeframeKey] = timeframeCount + 1;
        perBlockSetting[blockKey] = blockCount + 1;
        perIndicator[indicatorKey] = indicatorCount + 1;
        if (clusterKey) perCluster[clusterKey] = clusterCount + 1;
      } else if (row.eligibleForPortfolio && reasons.some(function(reason) { return reason.indexOf('similitud operativa') === 0 || reason.indexOf('correlacion real') === 0 || reason.indexOf(' cap ') !== -1 || reason === 'límite objetivo 8-12'; })) {
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
    var rejectedCount = rows.filter(function(row) { return !row.eligibleForPortfolio; }).length;
    var comparablePairs = rows.filter(function(row) { return row.correlationStatus === 'available'; }).length;
    var riskPlan = buildRiskPlan(winners, settings, rejectedCount);
    if (comparablePairs > 0) {
      riskPlan.aggregateRisk = 'requires_portfolio_master_contract';
      riskPlan.fullDeploymentAllowed = false;
    }
    var correlationStatus = buildCorrelationStatus(settings, statusCounts.similar || 0, comparablePairs);
    return sanitizePortfolioReport({
      version: PORTFOLIO_LAB_VERSION,
      sourcePhase: 'phase28_capa2_forward',
      sourceDatabank: 'Foward',
      selectionMode: 'governed-post-forward',
      total: rows.length,
      winners: winners.length,
      similar: statusCounts.similar || 0,
      review: statusCounts.review || 0,
      rejected: rejectedCount,
      uniqueAssets: Object.keys(uniqueAssets).filter(Boolean).length,
      settings: settings,
      riskPlan: riskPlan,
      correlationStatus: correlationStatus,
      deploymentSteps: buildDeploymentSteps(riskPlan, rejectedCount),
      rows: rows
    });
  }

  SQX.edgeFactory = {
    version: VERSION,
    portfolioLabVersion: PORTFOLIO_LAB_VERSION,
    portfolioMasterVersion: PORTFOLIO_MASTER_VERSION,
    portfolioMasterInputsVersion: PORTFOLIO_MASTER_INPUTS_VERSION,
    portfolioCorrelationStabilityVersion: PORTFOLIO_CORRELATION_STABILITY_VERSION,
    capa1C2CorrelationSelectionVersion: CAPA1_C2_CORRELATION_SELECTION_VERSION,
    backportOperatorPanelVersion: BACKPORT_OPERATOR_PANEL_VERSION,
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
    recordPortfolioCorrelationStability: recordPortfolioCorrelationStability,
    recordC2TemplateSelection: recordC2TemplateSelection,
    recordPortfolioMasterContract: recordPortfolioMasterContract,
    recordMiningRegistryFunnel: recordMiningRegistryFunnel,
    recordDownloadRequest: recordDownloadRequest,
    contextSummary: contextSummary,
    parsePortfolioRows: parsePortfolioRows,
    scoreCandidate: scoreCandidate,
    computeSimilarity: similarity,
    sanitizePortfolioReport: sanitizePortfolioReport,
    sanitizePortfolioMasterContract: sanitizePortfolioMasterContract,
    buildPortfolioMasterContract: buildPortfolioMasterContract,
    buildPortfolioShortlist: buildPortfolioShortlist,
    backportOperatorOperations: backportOperatorOperations,
    backportOperatorOperation: backportOperatorOperation,
    backportOperatorSample: backportOperatorSample,
    buildBackportOperatorPayload: buildBackportOperatorPayload,
    summarizeBackportOperatorResult: summarizeBackportOperatorResult,
    recordBackportOperatorResult: recordBackportOperatorResult
  };

  if (SQX.registerModule) SQX.registerModule('edge-factory', SQX.edgeFactory);
})(window);

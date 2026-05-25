(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  function byId(id) {
    return global.document.getElementById(id);
  }

  function all(selector, root) {
    return Array.from((root || global.document).querySelectorAll(selector));
  }

  function setText(id, value) {
    var node = byId(id);
    if (node) node.textContent = value == null ? '' : String(value);
  }

  function openTool(toolId) {
    if (!toolId) return false;
    if (SQX.ui && SQX.ui.activateTabById) return SQX.ui.activateTabById(toolId, global.document);
    var panel = byId('tab-' + toolId);
    if (!panel) return false;
    all('.tab-content').forEach(function(content) { content.style.display = 'none'; });
    panel.style.display = 'block';
    return true;
  }

  function renderState() {
    if (!SQX.edgeFactory) return null;
    var state = SQX.edgeFactory.getState();
    var steps = SQX.edgeFactory.steps();
    var completed = Array.isArray(state.completedSteps) ? state.completedSteps : [];
    var next = steps.find(function(step) { return completed.indexOf(step.id) === -1; }) || steps[steps.length - 1];
    var activeStep = state.activeStep || (next && next.id);
    var contexts = SQX.edgeFactory.contextSummary ? SQX.edgeFactory.contextSummary(state) : {};
    renderExperienceMode(state);
    all('[data-edge-stage]').forEach(function(card) {
      var id = card.dataset.edgeStage;
      card.classList.toggle('is-complete', completed.indexOf(id) !== -1);
      card.classList.toggle('is-current', id === activeStep);
      var box = card.querySelector('input[data-edge-complete]');
      if (box) box.checked = completed.indexOf(id) !== -1;
      var context = card.querySelector('[data-edge-context]');
      if (context) {
        context.textContent = contexts[id] || 'Sin contexto registrado todavía.';
        context.classList.toggle('is-empty', !contexts[id]);
      }
    });
    setText('edge-factory-progress-label', completed.length + ' de ' + steps.length + ' etapas');
    setText('edge-factory-next', completed.length === steps.length ? 'Listo para portfolio o nueva iteración' : 'Siguiente: ' + (next ? next.label : 'Punto de partida'));
    var meter = byId('edge-factory-meter-bar');
    if (meter) meter.style.width = Math.round((completed.length / steps.length) * 100) + '%';
    renderSignals(state);
    return state;
  }

  function latest(list) {
    return Array.isArray(list) && list.length ? list[0] : null;
  }

  function renderExperienceMode(state) {
    var mode = state && state.experienceMode === 'advanced' ? 'advanced' : 'basic';
    var shell = byId('edge-factory-shell');
    if (shell) {
      shell.classList.toggle('edge-mode-basic', mode === 'basic');
      shell.classList.toggle('edge-mode-advanced', mode === 'advanced');
    }
    all('[data-edge-mode]').forEach(function(button) {
      var active = button.dataset.edgeMode === mode;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    setText('edge-factory-mode-label', mode === 'advanced' ? 'Modo avanzado' : 'Modo básico');
    setText(
      'edge-factory-mode-copy',
      mode === 'advanced'
        ? 'Herramientas internas, checks manuales y custom libre visibles.'
        : 'Ruta guiada: una accion principal por etapa y controles tecnicos ocultos.'
    );
    var drawer = byId('edge-tool-drawer');
    var toggle = byId('edge-tools-toggle');
    if (mode === 'basic' && drawer && !drawer.hidden) {
      drawer.hidden = true;
      if (toggle) {
        toggle.setAttribute('aria-expanded', 'false');
        toggle.classList.remove('active');
      }
    }
  }

  function setSignal(id, title, detail, ready) {
    var node = global.document.querySelector('[data-edge-signal="' + id + '"]');
    if (!node) return;
    var strong = node.querySelector('strong');
    var small = node.querySelector('small');
    if (strong) strong.textContent = title || 'Pendiente';
    if (small) small.textContent = detail || '';
    node.classList.toggle('is-ready', !!ready);
    node.classList.toggle('is-waiting', !ready);
  }

  function renderSignals(state) {
    state = state || {};
    var card = state.selectedCard || {};
    var c1 = latest(state.capa1Outputs);
    var c2Template = state.c2Template || null;
    var portfolio = state.portfolioLab || null;
    var master = state.portfolioMasterContract || null;
    setSignal(
      'asset',
      state.selectedCard ? [card.asset, card.timeframe, card.direction].filter(Boolean).join(' · ') : 'Sin tarjeta',
      state.selectedCard ? (card.blockSetting || 'BlockSetting trazable') : 'Asset · TF · direccion · BlockSetting',
      !!state.selectedCard
    );
    setSignal(
      'capa1',
      c1 ? ((c1.results ? ((c1.results.ok || 0) + '/' + (c1.results.total || 0) + ' OK') : 'Generada')) : 'Pendiente',
      c1 && c1.files && c1.files.length ? c1.files.length + ' archivo(s) listos para descarga' : '.cfx y descarga del navegador',
      !!c1
    );
    setSignal(
      'template',
      c2Template ? (c2Template.name || 'Template C2 listo') : 'Pendiente',
      c2Template ? [c2Template.indicatorBase, c2Template.clusterId].filter(Boolean).join(' · ') : 'Indicador · cluster · exit policy',
      !!c2Template
    );
    setSignal(
      'portfolio',
      portfolio && portfolio.total ? (portfolio.winners || 0) + ' ganadores diversos' : 'Pendiente',
      portfolio && portfolio.total
        ? (portfolio.version || 'portfolio-lab-governed-v1') + ' · Master ' + (master ? master.status : 'blocked')
        : 'Shortlist diversa Capa 2',
      !!(portfolio && portfolio.total)
    );
  }

  function bindTools() {
    all('[data-edge-tool]').forEach(function(button) {
      if (button.__edgeToolBound) return;
      button.__edgeToolBound = true;
      button.addEventListener('click', function() {
        openTool(button.dataset.edgeTool);
      });
    });
  }

  function bindDrawer() {
    var toggle = byId('edge-tools-toggle');
    var drawer = byId('edge-tool-drawer');
    if (!toggle || !drawer || toggle.__edgeDrawerBound) return;
    toggle.__edgeDrawerBound = true;
    toggle.addEventListener('click', function() {
      var open = drawer.hidden;
      drawer.hidden = !open;
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.classList.toggle('active', open);
    });
  }

  function bindExperienceMode() {
    all('[data-edge-mode]').forEach(function(button) {
      if (button.__edgeModeBound) return;
      button.__edgeModeBound = true;
      button.addEventListener('click', function() {
        if (SQX.edgeFactory && SQX.edgeFactory.setExperienceMode) {
          SQX.edgeFactory.setExperienceMode(button.dataset.edgeMode);
        }
        renderState();
      });
    });
  }

  function bindStepControls() {
    all('[data-edge-step-open]').forEach(function(button) {
      if (button.__edgeStepBound) return;
      button.__edgeStepBound = true;
      button.addEventListener('click', function() {
        if (SQX.edgeFactory) SQX.edgeFactory.setActiveStep(button.dataset.edgeStepOpen);
        renderState();
        var target = global.document.querySelector('[data-edge-stage="' + button.dataset.edgeStepOpen + '"]');
        if (target && target.scrollIntoView) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
    });
    all('input[data-edge-complete]').forEach(function(box) {
      if (box.__edgeCompleteBound) return;
      box.__edgeCompleteBound = true;
      box.addEventListener('change', function() {
        if (SQX.edgeFactory) SQX.edgeFactory.completeStep(box.dataset.edgeComplete, box.checked);
        renderState();
      });
    });
  }

  function portfolioSample() {
    return [
      'Strategy Name;Symbol;TimeFrame;Profit factor;Ret/DD Ratio;Max DD %;# of trades;Stability;Winning Percent;SQN;BlockSetting;Indicator;Cluster;Forward Source;Forward Status;Pass Source',
      'AUDCAD_H4_LINEAR_CL01;AUDCAD;H4;1,68;6,2;18;245;0,72;51;2,1;BS_Volatilidad_v6;LinearRegression;CL01;Foward;PASSED;natural',
      'AUDCAD_H1_MACD_CL02;AUDCAD;H1;1,58;5,6;20;260;0,69;50;2,0;BS_Tendencia_v6;MACD;CL02;FOWARD;PASSED;natural',
      'AUDCAD_H4_LINEAR_CL03;AUDCAD;H4;1,61;5,8;19;238;0,68;49;1,9;BS_Volatilidad_v6;LinearRegression;CL03;Forward;PASSED;natural',
      'XAUUSD_H1_KER_CL04;XAUUSD;H1;1,51;4,8;22;318;0,64;48;1,8;BS_Tendencia_v6;KER;CL04;Foward;PASSED;natural',
      'US500_M15_ATR_CL05;US500;M15;1,42;4,1;24;420;0,61;46;1,6;BS_Volumen_v6_intraday_v6;ATR;CL05;Foward;PASSED;natural',
      'EURUSD_M30_RSI_CL06;EURUSD;M30;1,47;4,4;21;310;0,66;52;1,7;BS_MeanReversion_v6;RSI;CL06;Forward;PASSED;natural',
      'GBPJPY_H4_SUPER_CL07;GBPJPY;H4;1,55;5,1;26;205;0,62;49;1,8;BS_Tendencia_v6;SUPER;CL07;Foward;PASSED;natural',
      'USDJPY_H1_ADX_CL08;USDJPY;H1;1,49;4,6;23;286;0,65;51;1,7;BS_Volatilidad_v6;ADX;CL08;Foward;PASSED;natural',
      'NAS100_M15_CHOP_CL09;NAS100;M15;1,44;4,3;25;398;0,63;48;1,6;BS_Volumen_v6_intraday_v6;CHOPPINESS;CL09;Forward;PASSED;natural',
      'GER40_H1_HURST_CL10;GER40;H1;1,46;4,5;24;274;0,67;50;1,7;BS_Tendencia_v6;HURST;CL10;Foward;PASSED;natural',
      'GBPUSD_M30_MACD_CL11;GBPUSD;M30;1,43;4,2;22;302;0,64;49;1,6;BS_Tendencia_v6;MACD;CL11;Foward;PASSED;natural',
      'XAGUSD_H4_LINEAR_CL12;XAGUSD;H4;1,7;6,4;18;250;0,7;52;2,1;BS_Volatilidad_v6;LinearRegression;CL12;Synthetic;FORCED PASS;forced'
    ].join('\n');
  }

  function statusLabel(status) {
    return status === 'portfolio' ? 'Portfolio' : (status === 'similar' ? 'Similar' : 'Revisar');
  }

  function readPortfolioSettings() {
    function numberFrom(id, fallback) {
      var node = byId(id);
      var value = node ? Number(String(node.value || '').replace(',', '.')) : NaN;
      return Number.isFinite(value) ? value : fallback;
    }
    return {
      similarityThreshold: numberFrom('edge-portfolio-threshold', 0.78),
      maxWinners: numberFrom('edge-portfolio-max-winners', 12),
      maxPerAsset: numberFrom('edge-portfolio-max-asset', 2),
      maxPerTimeframe: numberFrom('edge-portfolio-max-timeframe', 4),
      maxPerBlockSetting: numberFrom('edge-portfolio-max-blocksetting', 3),
      maxPerIndicator: numberFrom('edge-portfolio-max-indicator', 3),
      maxPerCluster: numberFrom('edge-portfolio-max-cluster', 1)
    };
  }

  function renderPortfolioReport(report) {
    var output = byId('edge-portfolio-results');
    if (!output || !report) return;
    if (!report.rows || !report.rows.length) {
      output.innerHTML = '<div class="edge-portfolio-empty"><strong>No hay candidatos Capa 2 para analizar.</strong><span>Carga CSV, pega datos o usa la muestra.</span></div>';
      return;
    }
    var risk = report.riskPlan || {};
    var correlation = report.correlationStatus || {};
    var steps = Array.isArray(report.deploymentSteps) ? report.deploymentSteps : [];
    output.innerHTML =
      '<div class="edge-portfolio-summary">' +
        '<div class="edge-portfolio-stat"><span>Version</span><strong>governed-v1</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Total</span><strong>' + escapeHtml(report.total) + '</strong></div>' +
        '<div class="edge-portfolio-stat portfolio"><span>Portfolio</span><strong>' + escapeHtml(report.winners) + '</strong></div>' +
        '<div class="edge-portfolio-stat similar"><span>Similares</span><strong>' + escapeHtml(report.similar || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat review"><span>Revisar</span><strong>' + escapeHtml(report.review || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat review"><span>Rechazados</span><strong>' + escapeHtml(report.rejected || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Assets</span><strong>' + escapeHtml(report.uniqueAssets || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Rango</span><strong>' + escapeHtml(risk.targetRange || '8-12') + '</strong></div>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Plan de riesgo: ' + escapeHtml(risk.statusLabel || 'riesgo pendiente') + '</strong>' +
        '<span>' + escapeHtml(risk.objective || '8-12 ganadores naturales de Forward/Foward antes de MT5 real') + ' · riesgo base ' + escapeHtml(risk.baseRiskPct || 0.2) + '% · cap inicial ' + escapeHtml(risk.maxInitialRiskPct || 0.3) + '% · agregado ' + escapeHtml(risk.aggregateRisk || 'not_computable') + '.</span>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Correlacion: ' + escapeHtml(correlation.label || 'Similitud operativa, no correlacion de retornos') + '</strong>' +
        '<span>' + escapeHtml(correlation.detail || '') + ' · umbral similitud ' + escapeHtml(correlation.similarityThreshold || (report.settings && report.settings.similarityThreshold)) + '.</span>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Despliegue gradual</strong>' +
        '<span>' + steps.map(function(step) { return escapeHtml(step.label) + ' [' + escapeHtml(step.status) + ']'; }).join(' · ') + '</span>' +
      '</div>' +
      '<table><thead><tr><th>Estado</th><th>Estrategia</th><th>Forward/Foward</th><th>Asset</th><th>TF</th><th>BlockSetting</th><th>Indicador</th><th>PF</th><th>Ret/DD</th><th>DD</th><th>Trades</th><th>Score</th><th>Riesgo</th><th>Relación</th><th>Cluster</th><th>Motivo</th></tr></thead><tbody>' +
      report.rows.map(function(row) {
        return '<tr data-status="' + escapeHtml(row.diversityStatus) + '">' +
          '<td><span class="edge-portfolio-badge ' + escapeHtml(row.diversityStatus) + '">' + escapeHtml(statusLabel(row.diversityStatus)) + '</span></td>' +
          '<td>' + escapeHtml(row.strategy) + '</td>' +
          '<td>' + escapeHtml(row.forwardSource || '') + ' · ' + escapeHtml(row.forwardStatus || '') + '</td>' +
          '<td>' + escapeHtml(row.asset) + '</td>' +
          '<td>' + escapeHtml(row.timeframe) + '</td>' +
          '<td>' + escapeHtml(row.blockSetting) + '</td>' +
          '<td>' + escapeHtml(row.indicator) + '</td>' +
          '<td>' + escapeHtml(row.profitFactor) + '</td>' +
          '<td>' + escapeHtml(row.retDd) + '</td>' +
          '<td>' + escapeHtml(row.maxDd) + '%</td>' +
          '<td>' + escapeHtml(row.trades) + '</td>' +
          '<td>' + escapeHtml(row.score) + '</td>' +
          '<td>' + escapeHtml(row.riskPct == null ? '' : row.riskPct + '%') + '</td>' +
          '<td>' + escapeHtml(row.correlationStatus === 'available' ? ('corr ' + row.correlation) : ('sim ' + row.similarity)) + '</td>' +
          '<td>' + escapeHtml(row.clusterRef) + '</td>' +
          '<td class="edge-portfolio-reason">' + escapeHtml(row.reason || '') + (row.closestStrategy ? ' · ' + escapeHtml(row.closestStrategy) : '') + '</td>' +
        '</tr>';
      }).join('') +
      '</tbody></table>';
  }

  function portfolioMasterSeriesSample(report) {
    var winners = report && Array.isArray(report.rows)
      ? report.rows.filter(function(row) { return row.diversityStatus === 'portfolio'; })
      : [];
    var header = 'strategy,Returns';
    var rows = winners.map(function(row, index) {
      var offset = (index + 1) / 1000;
      var series = [
        0.010 + offset,
        -0.004 + offset,
        0.012 - offset,
        0.006 + offset,
        -0.003 + offset,
        0.009 - offset
      ].map(function(value) { return Math.round(value * 10000) / 10000; }).join('|');
      return '"' + String(row.strategy || row.id || '').replace(/"/g, '""') + '","' + series + '"';
    });
    return [header].concat(rows).join('\n');
  }

  function portfolioMasterAccountSample() {
    return 'accountModel=demo-forward-review; brokerProfile=ECN/low-spread; executionModel=hedging-netting reviewed; baseCurrency=USD; riskBudgetMode=0.2 pct base, 0.30 pct cap; leverageMode=broker-context-known';
  }

  function statusClass(status) {
    return status === 'ready' || status === 'ready_for_master_review' ? 'portfolio' : 'review';
  }

  function masterDisplayStatus(status) {
    if (status === 'ready_for_master_review') return 'ready';
    if (status === 'blocked_pending_operator_inputs') return 'blocked';
    return status || 'blocked';
  }

  function renderPortfolioMasterContract(contract) {
    var output = byId('edge-master-results');
    if (!output) return;
    if (!contract) {
      output.innerHTML = '<div class="edge-portfolio-empty"><strong>Sin contrato Portfolio Master.</strong><span>Primero calcula Portfolio Lab; despues aporta Forward CSV, equity/returns comparables y contexto publico cuenta/broker.</span></div>';
      return;
    }
    var risk = contract.outputReadback && contract.outputReadback.aggregateRisk ? contract.outputReadback.aggregateRisk : {};
    var inputs = Array.isArray(contract.requiredInputs) ? contract.requiredInputs : [];
    var blocked = Array.isArray(contract.blockedReasons) ? contract.blockedReasons : [];
    output.innerHTML =
      '<div class="edge-portfolio-summary">' +
        '<div class="edge-portfolio-stat ' + escapeHtml(statusClass(contract.status)) + '"><span>Estado</span><strong>' + escapeHtml(masterDisplayStatus(contract.status)) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Shortlist</span><strong>' + escapeHtml((contract.outputReadback && contract.outputReadback.shortlistSize) || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Forward</span><strong>' + escapeHtml((contract.inputReadback && contract.inputReadback.forwardCsv && contract.inputReadback.forwardCsv.matchedPortfolioWinners) || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Series</span><strong>' + escapeHtml((contract.inputReadback && contract.inputReadback.comparableSeries && contract.inputReadback.comparableSeries.matchedPortfolioWinners) || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Pares</span><strong>' + escapeHtml(risk.comparablePairs || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat review"><span>Live</span><strong>' + escapeHtml(contract.liveDeploymentAllowed ? 'SI' : 'NO') + '</strong></div>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Readback: ' + escapeHtml(contract.statusLabel || contract.status) + '</strong>' +
        '<span>Contrato publico sanitizado · ' + escapeHtml(risk.status || 'unavailable') + ' · no autoriza despliegue real.</span>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Prerrequisitos</strong>' +
        '<span>' + inputs.map(function(item) { return escapeHtml(item.label) + ' [' + escapeHtml(item.status) + ']'; }).join(' · ') + '</span>' +
      '</div>' +
      (blocked.length
        ? '<div class="edge-portfolio-empty"><strong>Bloqueos</strong><span>' + blocked.map(escapeHtml).join(' · ') + '</span></div>'
        : '<div class="edge-portfolio-empty"><strong>Bloqueos</strong><span>Sin bloqueos de contrato. Portfolio Master aun debe recalcular y confirmar antes de operar.</span></div>');
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch];
    });
  }

  function currentPortfolioLab() {
    if (!SQX.edgeFactory) return null;
    var state = SQX.edgeFactory.getState();
    return state.portfolioLab || null;
  }

  function runPortfolioLab() {
    if (!SQX.edgeFactory) return null;
    var input = byId('edge-portfolio-input');
    var report = SQX.edgeFactory.buildPortfolioShortlist(input ? input.value : '', readPortfolioSettings());
    if (SQX.edgeFactory.recordPortfolioLab) {
      SQX.edgeFactory.recordPortfolioLab(report);
    } else {
      SQX.edgeFactory.savePatch({ portfolioLab: report, activeStep: 'portfolio' }, 'portfolio-lab-run');
    }
    renderPortfolioReport(report);
    renderPortfolioMasterContract(SQX.edgeFactory.getState().portfolioMasterContract);
    renderState();
    return report;
  }

  function readPortfolioMasterInputs() {
    return {
      forwardCsv: (byId('edge-master-forward-input') || {}).value || '',
      comparableSeriesCsv: (byId('edge-master-series-input') || {}).value || '',
      accountBrokerContext: (byId('edge-master-account-input') || {}).value || ''
    };
  }

  function runPortfolioMasterContract() {
    if (!SQX.edgeFactory) return null;
    var payload = Object.assign({
      labReport: currentPortfolioLab()
    }, readPortfolioMasterInputs());
    var state = SQX.edgeFactory.recordPortfolioMasterContract
      ? SQX.edgeFactory.recordPortfolioMasterContract(payload)
      : SQX.edgeFactory.savePatch({ portfolioMasterContract: SQX.edgeFactory.buildPortfolioMasterContract(payload) }, 'portfolio-master-contract-run');
    var contract = state.portfolioMasterContract;
    renderPortfolioMasterContract(contract);
    renderState();
    return contract;
  }

  function samplePortfolioMasterContract() {
    if (!SQX.edgeFactory) return;
    var lab = currentPortfolioLab();
    var portfolioInput = byId('edge-portfolio-input');
    if (!lab || !lab.total) {
      if (portfolioInput && !portfolioInput.value) portfolioInput.value = portfolioSample();
      lab = runPortfolioLab();
    }
    var forward = byId('edge-master-forward-input');
    var series = byId('edge-master-series-input');
    var account = byId('edge-master-account-input');
    if (forward) forward.value = (portfolioInput && portfolioInput.value) || portfolioSample();
    if (series) series.value = portfolioMasterSeriesSample(lab);
    if (account) account.value = portfolioMasterAccountSample();
    runPortfolioMasterContract();
  }

  function downloadPortfolioMasterContract() {
    if (!SQX.edgeFactory) return;
    var state = SQX.edgeFactory.getState();
    var contract = state.portfolioMasterContract || runPortfolioMasterContract();
    if (!contract) return;
    var filename = 'sqx-edge-portfolio-master-contract.json';
    try {
      var blob = new Blob([JSON.stringify(contract, null, 2)], { type: 'application/json' });
      var link = global.document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
      if (SQX.edgeFactory.recordDownloadRequest) {
        SQX.edgeFactory.recordDownloadRequest({ kind: 'portfolio-master-contract', files: [filename] });
      }
    } catch (_err) {
      var output = byId('edge-master-results');
      if (output) output.textContent = JSON.stringify(contract, null, 2);
    }
  }

  function downloadPortfolioReport() {
    if (!SQX.edgeFactory) return;
    var state = SQX.edgeFactory.getState();
    var report = state.portfolioLab || runPortfolioLab();
    if (!report) return;
    if (SQX.edgeFactory.sanitizePortfolioReport) report = SQX.edgeFactory.sanitizePortfolioReport(report);
    var filename = 'sqx-edge-portfolio-lab-summary.json';
    try {
      var blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      var link = global.document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
      if (SQX.edgeFactory.recordDownloadRequest) {
        SQX.edgeFactory.recordDownloadRequest({ kind: 'portfolio-summary', files: [filename] });
      }
    } catch (_err) {
      var output = byId('edge-portfolio-results');
      if (output) output.textContent = JSON.stringify(report, null, 2);
    }
  }

  function downloadPortfolioCsv() {
    if (!SQX.edgeFactory) return;
    var state = SQX.edgeFactory.getState();
    var report = state.portfolioLab || runPortfolioLab();
    if (!report || !report.rows) return;
    if (SQX.edgeFactory.sanitizePortfolioReport) report = SQX.edgeFactory.sanitizePortfolioReport(report);
    var rows = ['decision,strategy,asset,timeframe,forwardSource,forwardStatus,blockSetting,indicator,cluster,score,similarityLabel,reason'];
    report.rows.filter(function(row) { return row.diversityStatus === 'portfolio'; }).forEach(function(row) {
      rows.push([
        row.decision,
        row.strategy,
        row.asset,
        row.timeframe,
        row.forwardSource,
        row.forwardStatus,
        row.blockSetting,
        row.indicator,
        row.clusterRef,
        row.score,
        row.similarityLabel,
        row.reason
      ].map(function(value) {
        return '"' + String(value == null ? '' : value).replace(/"/g, '""') + '"';
      }).join(','));
    });
    var filename = 'sqx-edge-portfolio-shortlist.csv';
    try {
      var blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8' });
      var link = global.document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
      if (SQX.edgeFactory.recordDownloadRequest) {
        SQX.edgeFactory.recordDownloadRequest({ kind: 'portfolio-shortlist-csv', files: [filename] });
      }
    } catch (_err) {
      var output = byId('edge-portfolio-results');
      if (output) output.textContent = rows.join('\n');
    }
  }

  function resetPortfolioLab() {
    var input = byId('edge-portfolio-input');
    var output = byId('edge-portfolio-results');
    var file = byId('edge-portfolio-file');
    var masterForward = byId('edge-master-forward-input');
    var masterSeries = byId('edge-master-series-input');
    var masterAccount = byId('edge-master-account-input');
    if (input) input.value = '';
    if (file) file.value = '';
    if (masterForward) masterForward.value = '';
    if (masterSeries) masterSeries.value = '';
    if (masterAccount) masterAccount.value = '';
    if (output) output.innerHTML = '<div class="edge-portfolio-empty"><strong>Sin lote Capa 2 cargado.</strong><span>Carga CSV, pega datos o usa la muestra para calcular ranking y diversidad.</span></div>';
    renderPortfolioMasterContract(null);
    if (SQX.edgeFactory) SQX.edgeFactory.savePatch({ portfolioLab: null, portfolioMasterContract: null }, 'portfolio-lab-reset');
    renderState();
  }

  function bindPortfolioMaster() {
    var run = byId('edge-master-run');
    var sample = byId('edge-master-sample');
    var exportBtn = byId('edge-master-export');
    var reset = byId('edge-master-reset');
    if (run && !run.__edgeMasterBound) {
      run.__edgeMasterBound = true;
      run.addEventListener('click', runPortfolioMasterContract);
    }
    if (sample && !sample.__edgeMasterBound) {
      sample.__edgeMasterBound = true;
      sample.addEventListener('click', samplePortfolioMasterContract);
    }
    if (exportBtn && !exportBtn.__edgeMasterBound) {
      exportBtn.__edgeMasterBound = true;
      exportBtn.addEventListener('click', downloadPortfolioMasterContract);
    }
    if (reset && !reset.__edgeMasterBound) {
      reset.__edgeMasterBound = true;
      reset.addEventListener('click', function() {
        ['edge-master-forward-input', 'edge-master-series-input', 'edge-master-account-input'].forEach(function(id) {
          var node = byId(id);
          if (node) node.value = '';
        });
        renderPortfolioMasterContract(null);
        if (SQX.edgeFactory) SQX.edgeFactory.savePatch({ portfolioMasterContract: null }, 'portfolio-master-reset');
        renderState();
      });
    }
  }

  function bindPortfolioLab() {
    var sample = byId('edge-portfolio-sample');
    var run = byId('edge-portfolio-run');
    var exportBtn = byId('edge-portfolio-export');
    var exportCsv = byId('edge-portfolio-export-csv');
    var reset = byId('edge-portfolio-reset');
    var file = byId('edge-portfolio-file');
    var input = byId('edge-portfolio-input');
    if (sample && !sample.__edgePortfolioBound) {
      sample.__edgePortfolioBound = true;
      sample.addEventListener('click', function() {
        if (input) input.value = portfolioSample();
        runPortfolioLab();
      });
    }
    if (run && !run.__edgePortfolioBound) {
      run.__edgePortfolioBound = true;
      run.addEventListener('click', runPortfolioLab);
    }
    if (exportBtn && !exportBtn.__edgePortfolioBound) {
      exportBtn.__edgePortfolioBound = true;
      exportBtn.addEventListener('click', downloadPortfolioReport);
    }
    if (exportCsv && !exportCsv.__edgePortfolioBound) {
      exportCsv.__edgePortfolioBound = true;
      exportCsv.addEventListener('click', downloadPortfolioCsv);
    }
    if (reset && !reset.__edgePortfolioBound) {
      reset.__edgePortfolioBound = true;
      reset.addEventListener('click', resetPortfolioLab);
    }
    if (file && !file.__edgePortfolioBound) {
      file.__edgePortfolioBound = true;
      file.addEventListener('change', function() {
        var selected = file.files && file.files[0];
        if (!selected || !input) return;
        var reader = new FileReader();
        reader.onload = function() {
          input.value = String(reader.result || '');
          runPortfolioLab();
        };
        reader.readAsText(selected);
      });
    }
  }

  function init() {
    if (!byId('edge-factory-shell')) return false;
    bindTools();
    bindDrawer();
    bindExperienceMode();
    bindStepControls();
    bindPortfolioLab();
    bindPortfolioMaster();
    if (SQX.edgeFactory) renderPortfolioMasterContract(SQX.edgeFactory.getState().portfolioMasterContract);
    renderState();
    return true;
  }

  SQX.edgeFactoryUI = {
    init: init,
    renderState: renderState,
    openTool: openTool,
    runPortfolioLab: runPortfolioLab,
    runPortfolioMasterContract: runPortfolioMasterContract,
    renderPortfolioReport: renderPortfolioReport,
    renderPortfolioMasterContract: renderPortfolioMasterContract
  };

  if (SQX.registerModule) SQX.registerModule('edge-factory-ui', SQX.edgeFactoryUI);
})(window);

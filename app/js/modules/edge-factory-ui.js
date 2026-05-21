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
    setText('edge-factory-next', completed.length === steps.length ? 'Listo para portfolio o nueva iteración' : 'Siguiente: ' + (next ? next.label : 'Preparar sesión'));
    var meter = byId('edge-factory-meter-bar');
    if (meter) meter.style.width = Math.round((completed.length / steps.length) * 100) + '%';
    return state;
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
      'strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,blockSetting,indicator',
      'AUDCAD_H4_LINEAR_CL01,AUDCAD,H4,1.68,6.2,18,245,BS_Volatilidad_v6,LinearRegression',
      'AUDCAD_H4_LINEAR_CL02,AUDCAD,H4,1.63,5.9,19,231,BS_Volatilidad_v6,LinearRegression',
      'XAUUSD_H1_KER_CL01,XAUUSD,H1,1.51,4.8,22,318,BS_Tendencia_v6,KER',
      'US500_M15_ATR_CL01,US500,M15,1.42,4.1,24,420,BS_Volumen_v6_intraday_v6,ATR'
    ].join('\n');
  }

  function renderPortfolioReport(report) {
    var output = byId('edge-portfolio-results');
    if (!output || !report) return;
    if (!report.rows || !report.rows.length) {
      output.textContent = 'No hay candidatos Capa 2 para analizar.';
      return;
    }
    output.innerHTML =
      '<div class="edge-portfolio-summary">' + report.total + ' candidatos · ' + report.winners + ' ganadores diversos</div>' +
      '<table><thead><tr><th>Estrategia</th><th>Asset</th><th>TF</th><th>Score</th><th>Diversidad</th><th>Cluster</th><th>Similitud</th></tr></thead><tbody>' +
      report.rows.map(function(row) {
        return '<tr>' +
          '<td>' + escapeHtml(row.strategy) + '</td>' +
          '<td>' + escapeHtml(row.asset) + '</td>' +
          '<td>' + escapeHtml(row.timeframe) + '</td>' +
          '<td>' + escapeHtml(row.score) + '</td>' +
          '<td>' + escapeHtml(row.diversityStatus) + '</td>' +
          '<td>' + escapeHtml(row.clusterRef) + '</td>' +
          '<td>' + escapeHtml(row.similarity) + '</td>' +
        '</tr>';
      }).join('') +
      '</tbody></table>';
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch];
    });
  }

  function runPortfolioLab() {
    if (!SQX.edgeFactory) return null;
    var input = byId('edge-portfolio-input');
    var report = SQX.edgeFactory.buildPortfolioShortlist(input ? input.value : '');
    if (SQX.edgeFactory.recordPortfolioLab) {
      SQX.edgeFactory.recordPortfolioLab(report);
    } else {
      SQX.edgeFactory.savePatch({ portfolioLab: report, activeStep: 'portfolio' }, 'portfolio-lab-run');
    }
    renderPortfolioReport(report);
    renderState();
    return report;
  }

  function downloadPortfolioReport() {
    if (!SQX.edgeFactory) return;
    var state = SQX.edgeFactory.getState();
    var report = state.portfolioLab || runPortfolioLab();
    if (!report) return;
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

  function bindPortfolioLab() {
    var sample = byId('edge-portfolio-sample');
    var run = byId('edge-portfolio-run');
    var exportBtn = byId('edge-portfolio-export');
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
  }

  function init() {
    if (!byId('edge-factory-shell')) return false;
    bindTools();
    bindDrawer();
    bindStepControls();
    bindPortfolioLab();
    renderState();
    return true;
  }

  SQX.edgeFactoryUI = {
    init: init,
    renderState: renderState,
    openTool: openTool,
    runPortfolioLab: runPortfolioLab,
    renderPortfolioReport: renderPortfolioReport
  };

  if (SQX.registerModule) SQX.registerModule('edge-factory-ui', SQX.edgeFactoryUI);
})(window);

(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  function all(selector, doc) {
    return Array.from((doc || global.document).querySelectorAll(selector));
  }

  function bindSubtabs(options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    var tabs = all(opts.tabSelector || '.subtab', doc);
    tabs.forEach(function(tab) {
      tab.addEventListener('click', function() {
        var sub = tab.dataset.subtab;
        all(opts.tabSelector || '.subtab', doc).forEach(function(node) { node.classList.remove('active'); });
        tab.classList.add('active');
        all(opts.contentSelector || '.subtab-content', doc).forEach(function(node) { node.classList.remove('active'); });
        var target = doc.getElementById(sub);
        if (target) target.classList.add('active');
      });
    });
    return tabs.length;
  }

  function resolveChecklistKey(config, fallback) {
    var cfg = config || SQX.config || {};
    if (cfg.storageKey) return cfg.storageKey('workflowChecklist', fallback || 'sqx_workflow_checklist_v1');
    var runtime = global.SQX_CONFIG || {};
    return (runtime.storageKeys && runtime.storageKeys.workflowChecklist) || fallback || 'sqx_workflow_checklist_v1';
  }

  function resolveStorage(storage) {
    return storage || SQX.storage || {
      getJson: function(key, fallback) {
        try { return JSON.parse(global.localStorage.getItem(key) || JSON.stringify(fallback)); }
        catch (_err) { return fallback; }
      },
      setJson: function(key, value) {
        global.localStorage.setItem(key, JSON.stringify(value));
        return true;
      }
    };
  }

  function bindChecklist(options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    var storage = resolveStorage(opts.storage);
    var key = opts.key || resolveChecklistKey(opts.config, opts.fallbackKey);
    var confirmFn = opts.confirm || global.confirm;
    var state = storage.getJson(key, {}) || {};

    function save() {
      storage.setJson(key, state);
    }

    var boxes = all('input[type="checkbox"][data-check]', doc);
    boxes.forEach(function(box) {
      var id = box.dataset.check;
      if (state[id]) box.checked = true;
      box.addEventListener('change', function() {
        if (box.checked) state[id] = true;
        else delete state[id];
        save();
      });
    });

    var clears = all('button[data-checklist-clear]', doc);
    clears.forEach(function(button) {
      button.addEventListener('click', function() {
        var prefix = button.dataset.checklistClear + '-';
        var matches = Object.keys(state).filter(function(checkId) { return checkId.indexOf(prefix) === 0; });
        if (!matches.length) return;
        if (confirmFn && !confirmFn('\u00bfResetear ' + matches.length + ' checks de ' + button.dataset.checklistClear + '?')) return;
        matches.forEach(function(checkId) { delete state[checkId]; });
        save();
        all('input[type="checkbox"][data-check^="' + prefix + '"]', doc).forEach(function(box) { box.checked = false; });
      });
    });

    return {
      key: key,
      state: state,
      checkboxCount: boxes.length,
      clearCount: clears.length,
      save: save
    };
  }

  function computePlanSummary(options) {
    var opts = options || {};
    var minings = opts.minings || global.PLAN_ALL || global.PLAN_MININGS || [];
    var phases = opts.phases || global.PHASE_META || {};
    var phaseIds = Object.keys(phases).filter(function(phase) {
      return minings.some(function(mining) { return String(mining.phase) === String(phase); });
    });
    var assets = {};
    var tfs = {};
    minings.forEach(function(mining) {
      if (mining && mining.asset) assets[mining.asset] = true;
      if (mining && mining.tf) tfs[mining.tf] = true;
    });
    return {
      phaseCount: phaseIds.length,
      miningCount: minings.length,
      assetCount: Object.keys(assets).length,
      timeframeCount: Object.keys(tfs).length,
      userMiningCount: minings.filter(function(mining) { return mining && mining._user; }).length
    };
  }

  function renderPlanSummary(options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    var summary = computePlanSummary(opts);
    var title = doc.getElementById('wf-plan-v2-title');
    var metrics = doc.getElementById('wf-plan-v2-metrics');
    var detail = doc.getElementById('wf-plan-v2-detail');
    if (title) title.textContent = 'Plan v2 sincronizado con Pipeline State';
    if (metrics) {
      metrics.innerHTML =
        '<span>' + summary.phaseCount + ' fases</span>' +
        '<span>' + summary.miningCount + ' minings</span>' +
        '<span>' + summary.assetCount + ' activos</span>' +
        '<span>' + summary.timeframeCount + ' TF</span>';
    }
    if (detail) {
      detail.textContent = summary.userMiningCount
        ? summary.userMiningCount + ' minings locales extendidos desde Pipeline. Workflow queda alineado con el plan operativo real.'
        : 'Workflow alineado con el plan base operativo. Las extensiones locales apareceran aqui al anadir minings desde Pipeline.';
    }
    return summary;
  }

  function init(options) {
    var opts = options || {};
    return {
      planSummary: renderPlanSummary(opts),
      subtabCount: bindSubtabs(opts),
      checklist: bindChecklist(opts)
    };
  }

  SQX.workflow = SQX.workflow || {
    bindChecklist: bindChecklist,
    bindSubtabs: bindSubtabs,
    computePlanSummary: computePlanSummary,
    init: init,
    renderPlanSummary: renderPlanSummary,
    resolveChecklistKey: resolveChecklistKey
  };

  if (SQX.registerModule) {
    SQX.registerModule('workflow', SQX.workflow);
  }
})(window);

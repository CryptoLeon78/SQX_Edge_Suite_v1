(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  function all(selector, doc) {
    return Array.from((doc || global.document).querySelectorAll(selector));
  }

  function activateWorkflowPanel(panelId, trigger, options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    if (!panelId) return false;

    all(opts.tabSelector || '.subtab', doc).forEach(function(node) { node.classList.remove('active'); });
    all(opts.stepTriggerSelector || '[data-wf-detail-target]', doc).forEach(function(node) {
      node.classList.remove('is-active');
      if (node.setAttribute) node.setAttribute('aria-expanded', 'false');
      var detail = doc.getElementById(node.dataset.wfDetailTarget);
      if (detail) detail.hidden = true;
    });

    if (trigger && trigger.dataset && trigger.dataset.subtab) {
      trigger.classList.add('active');
    } else {
      all(opts.tabSelector || '.subtab', doc).forEach(function(node) {
        if (node.dataset && node.dataset.subtab === panelId) node.classList.add('active');
      });
    }

    all(opts.contentSelector || '.subtab-content', doc).forEach(function(node) { node.classList.remove('active'); });
    var target = doc.getElementById(panelId);
    if (target) target.classList.add('active');

    return Boolean(target);
  }

  function toggleWorkflowStepDetail(trigger, options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    if (!trigger || !trigger.dataset || !trigger.dataset.wfDetailTarget) return false;
    var target = doc.getElementById(trigger.dataset.wfDetailTarget);
    if (!target) return false;
    var isOpen = !target.hidden;
    all(opts.stepTriggerSelector || '[data-wf-detail-target]', doc).forEach(function(node) {
      var detail = doc.getElementById(node.dataset.wfDetailTarget);
      if (detail) detail.hidden = true;
      node.classList.remove('is-active');
      if (node.setAttribute) node.setAttribute('aria-expanded', 'false');
    });
    if (!isOpen) {
      target.hidden = false;
      trigger.classList.add('is-active');
      if (trigger.setAttribute) trigger.setAttribute('aria-expanded', 'true');
    }
    return true;
  }

  function bindSubtabs(options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    var tabs = all(opts.tabSelector || '.subtab', doc);
    tabs.forEach(function(tab) {
      tab.addEventListener('click', function() {
        activateWorkflowPanel(tab.dataset.subtab, tab, opts);
      });
    });
    return tabs.length;
  }

  function bindStepDetails(options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    var triggers = all(opts.stepTriggerSelector || '[data-wf-detail-target]', doc);
    triggers.forEach(function(trigger) {
      function activate() {
        toggleWorkflowStepDetail(trigger, opts);
      }
      trigger.addEventListener('click', activate);
      trigger.addEventListener('keydown', function(event) {
        if (!event || (event.key !== 'Enter' && event.key !== ' ')) return;
        if (event.preventDefault) event.preventDefault();
        activate();
      });
    });
    return triggers.length;
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
    if (title) title.textContent = 'Plan v2 sincronizado con Mining Control';
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

  function renderCommandCenter(options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    var steps = all('#wf-command-steps .workflow-command-step', doc);
    var progressLabel = doc.getElementById('wf-command-progress-label');
    var nextLabel = doc.getElementById('wf-command-next');
    var meter = doc.getElementById('wf-command-meter-bar');
    if (!steps.length) {
      return { stepCount: 0, doneCount: 0, nextTitle: '' };
    }

    var doneCount = 0;
    var nextTitle = '';
    steps.forEach(function(step) {
      var box = step.querySelector('input[type="checkbox"][data-check]');
      var done = !!(box && box.checked);
      step.classList.toggle('is-done', done);
      step.classList.remove('is-current');
      if (done) doneCount += 1;
      else if (!nextTitle) {
        step.classList.add('is-current');
        var label = step.querySelector('label');
        nextTitle = label ? label.textContent.trim() : '';
      }
    });

    if (!nextTitle) nextTitle = 'Workflow completo';
    if (progressLabel) progressLabel.textContent = doneCount + ' de ' + steps.length + ' pasos';
    if (nextLabel) nextLabel.textContent = doneCount === steps.length ? 'Listo para cierre o nueva iteracion' : 'Siguiente: ' + nextTitle;
    if (meter) meter.style.width = Math.round((doneCount / steps.length) * 100) + '%';

    return {
      stepCount: steps.length,
      doneCount: doneCount,
      nextTitle: nextTitle
    };
  }

  function bindCommandCenter(options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    var boxes = all('#wf-command-steps input[type="checkbox"][data-check]', doc);
    boxes.forEach(function(box) {
      box.addEventListener('change', function() {
        renderCommandCenter(opts);
      });
    });
    return renderCommandCenter(opts);
  }

  function init(options) {
    var opts = options || {};
    var checklist = bindChecklist(opts);
    return {
      planSummary: renderPlanSummary(opts),
      subtabCount: bindSubtabs(opts),
      stepDetailCount: bindStepDetails(opts),
      checklist: checklist,
      commandCenter: bindCommandCenter(opts)
    };
  }

  SQX.workflow = SQX.workflow || {
    activateWorkflowPanel: activateWorkflowPanel,
    bindChecklist: bindChecklist,
    bindCommandCenter: bindCommandCenter,
    bindStepDetails: bindStepDetails,
    bindSubtabs: bindSubtabs,
    computePlanSummary: computePlanSummary,
    init: init,
    renderCommandCenter: renderCommandCenter,
    renderPlanSummary: renderPlanSummary,
    resolveChecklistKey: resolveChecklistKey,
    toggleWorkflowStepDetail: toggleWorkflowStepDetail
  };

  if (SQX.registerModule) {
    SQX.registerModule('workflow', SQX.workflow);
  }
})(window);

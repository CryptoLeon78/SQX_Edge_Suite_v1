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

  function init(options) {
    var opts = options || {};
    return {
      subtabCount: bindSubtabs(opts),
      checklist: bindChecklist(opts)
    };
  }

  SQX.workflow = SQX.workflow || {
    bindChecklist: bindChecklist,
    bindSubtabs: bindSubtabs,
    init: init,
    resolveChecklistKey: resolveChecklistKey
  };

  if (SQX.registerModule) {
    SQX.registerModule('workflow', SQX.workflow);
  }
})(window);

(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var PG = SQX.projectGenerator = SQX.projectGenerator || {};

  function byId(doc, id) {
    return (doc || global.document).getElementById(id);
  }

  function bind(doc, id, eventName, handler) {
    var el = byId(doc, id);
    if (!el || !handler) return false;
    el.addEventListener(eventName || 'click', handler);
    return true;
  }

  function bindProjectGeneratorEvents(doc, handlers) {
    var h = handlers || {};
    var refresh = byId(doc, 'pg-status-refresh');
    if (!refresh) return false;

    refresh.addEventListener('click', h.checkHealth);
    bind(doc, 'pg-settings-toggle', 'click', function() {
      var body = byId(doc, 'pg-settings-body');
      var open = body && body.style.display !== 'none';
      if (h.setSettingsOpen) h.setSettingsOpen(!open);
    });
    bind(doc, 'pg-settings-save', 'click', h.saveConfig);
    bind(doc, 'pg-settings-reload', 'click', h.loadConfig);
    bind(doc, 'pg-onboarding-action', 'click', h.runOnboardingAction);
    bind(doc, 'pg-onboarding-secondary', 'click', h.runOnboardingSecondaryAction);
    bind(doc, 'pg-onboarding-tertiary', 'click', h.runOnboardingTertiaryAction);
    bind(doc, 'pg-autodetect', 'click', h.autodetectSqx);
    bind(doc, 'pg-aliases-suggest', 'click', h.suggestAll);
    bind(doc, 'pg-validate', 'click', h.validateSqxPath);
    bind(doc, 'pg-custom-generate', 'click', h.generateCustom);
    bind(doc, 'pg-custom-save-preset', 'click', h.saveCustomPreset);
    bind(doc, 'pg-custom-load-preset', 'click', h.loadCustomPreset);
    bind(doc, 'pg-custom-delete-preset', 'click', h.deleteCustomPreset);
    bind(doc, 'pg-custom-starter-list', 'click', h.handleCustomStarterProfileClick);
    bind(doc, 'pg-custom-export-starter-profiles', 'click', h.exportCustomStarterProfiles);
    bind(doc, 'pg-custom-export-presets', 'click', h.exportCustomPresets);
    bind(doc, 'pg-custom-import-presets', 'click', h.openImportCustomPresets);
    bind(doc, 'pg-custom-import-presets-file', 'change', h.importCustomPresets);
    bind(doc, 'pg-gen-all-c1', 'click', function() { h.generateAll(1); });
    bind(doc, 'pg-gen-all-c2', 'click', function() { h.generateAll(2); });
    bind(doc, 'pg-output-refresh', 'click', h.loadOutput);
    bind(doc, 'pg-open-output', 'click', h.openOutputFolder);
    bind(doc, 'pg-log-clear', 'click', function() {
      var log = byId(doc, 'pg-log');
      if (log) log.textContent = '[esperando primera acción…]';
    });
    return true;
  }

  function bindStrategyCleanerEvents(doc, state, handlers) {
    var s = state || {};
    var h = handlers || {};
    bind(doc, 'cln-scan', 'click', h.scan);
    bind(doc, 'cln-preview', 'click', h.previewRename);
    bind(doc, 'cln-process', 'click', h.process);
    bind(doc, 'cln-select-all', 'click', function() {
      (s.files || []).forEach(function(file) { s.selected.add(file.path); });
      if (h.renderTable) h.renderTable();
    });
    bind(doc, 'cln-select-none', 'click', function() {
      if (s.selected) s.selected.clear();
      if (h.renderTable) h.renderTable();
    });
    bind(doc, 'cln-opt-rename', 'change', function() {
      var wrap = byId(doc, 'cln-pattern-wrap');
      if (wrap) wrap.style.display = this.checked ? 'inline-block' : 'none';
    });
    return true;
  }

  function bindProjectGeneratorPolling(targetGlobal, doc, handlers) {
    var host = targetGlobal || global;
    var h = handlers || {};
    if (doc && doc.querySelectorAll) {
      doc.querySelectorAll('.tab[data-tab="projectgen"]').forEach(function(tab) {
        tab.addEventListener('click', function() {
          host.setTimeout(h.checkHealth, 100);
        });
      });
    }
    host.setInterval(function() {
      var panel = byId(doc, 'tab-projectgen');
      if (panel && panel.style.display !== 'none' && h.checkHealth) h.checkHealth();
    }, 30000);
    if (h.renderOnboarding) h.renderOnboarding();
    host.setTimeout(h.checkHealth, 500);
    return true;
  }

  Object.assign(PG, {
    bindings: {
      bindProjectGeneratorEvents: bindProjectGeneratorEvents,
      bindProjectGeneratorPolling: bindProjectGeneratorPolling,
      bindStrategyCleanerEvents: bindStrategyCleanerEvents
    }
  });
})(window);

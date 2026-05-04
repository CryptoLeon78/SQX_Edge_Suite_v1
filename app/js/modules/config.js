(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var runtimeConfig = global.SQX_CONFIG || {};
  var fallbackConfig = {
    ui: {},
    storageKeys: {},
    value: function(_path, fallback) { return fallback; }
  };

  function value(path, fallback) {
    if (runtimeConfig.value) return runtimeConfig.value(path, fallback);
    return fallbackConfig.value(path, fallback);
  }

  function ui() {
    return runtimeConfig.ui || fallbackConfig.ui;
  }

  function storageKeys() {
    return runtimeConfig.storageKeys || fallbackConfig.storageKeys;
  }

  function storageKey(name, fallback) {
    var keys = storageKeys();
    return keys[name] || fallback || name;
  }

  function statusMeta(status) {
    var statuses = ui().statuses || [];
    for (var i = 0; i < statuses.length; i += 1) {
      if (statuses[i].id === status) return statuses[i];
    }
    return { id: status, label: status };
  }

  function statusSequence() {
    var statuses = ui().statuses || [];
    if (!statuses.length) return ['pending', 'current', 'completed'];
    return statuses.map(function(status) { return status.id; });
  }

  SQX.config = SQX.config || {
    raw: runtimeConfig,
    value: value,
    ui: ui,
    storageKeys: storageKeys,
    storageKey: storageKey,
    statusMeta: statusMeta,
    statusSequence: statusSequence
  };

  if (SQX.registerModule) {
    SQX.registerModule('config', SQX.config);
  }
})(window);

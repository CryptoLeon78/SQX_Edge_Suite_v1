(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  function storageKey(name, fallback) {
    if (SQX.config && SQX.config.storageKey) return SQX.config.storageKey(name, fallback);
    var config = global.SQX_CONFIG || {};
    var keys = config.storageKeys || {};
    return keys[name] || fallback || name;
  }

  function getJson(key, fallback) {
    try {
      var raw = global.localStorage.getItem(key);
      if (raw == null) return fallback;
      return SQX.utils && SQX.utils.safeJsonParse ? SQX.utils.safeJsonParse(raw, fallback) : JSON.parse(raw);
    } catch (_err) {
      return fallback;
    }
  }

  function setJson(key, value) {
    try {
      global.localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (_err) {
      return false;
    }
  }

  function remove(key) {
    try {
      global.localStorage.removeItem(key);
      return true;
    } catch (_err) {
      return false;
    }
  }

  SQX.storage = SQX.storage || {
    key: storageKey,
    getJson: getJson,
    setJson: setJson,
    remove: remove
  };

  if (SQX.registerModule) {
    SQX.registerModule('storage', SQX.storage);
  }
})(window);

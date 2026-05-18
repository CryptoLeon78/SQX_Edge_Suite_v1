(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var VERSION = 'remote-workspace-state-v1';
  var FALLBACK_KEYS = {
    planUser: 'sqx_plan_user_v1',
    pipelineState: 'sqx_pipeline_state_v1',
    strategiesUser: 'sqx_strategies_user_v1',
    strategiesDeleted: 'sqx_strategies_deleted_v1',
    viewCreatorPresets: 'sqx_view_creator_presets_v1'
  };
  var _enabled = false;
  var _ready = false;
  var _saving = false;
  var _lastState = {};
  var _lastError = '';
  var _bootstrapPromise = null;
  var _pending = {};
  var _timer = null;

  function apiBase() {
    var raw = (SQX.config && SQX.config.raw) || global.SQX_CONFIG || {};
    var base = raw.apiBase ? raw.apiBase() : '/api';
    return String(base || '/api').replace(/\/$/, '');
  }

  function isLocalFileMode() {
    return !!(global.location && global.location.protocol === 'file:');
  }

  function storageKeys() {
    var keys = SQX.config && SQX.config.storageKeys ? SQX.config.storageKeys() : ((global.SQX_CONFIG && global.SQX_CONFIG.storageKeys) || {});
    return {
      planUser: keys.planUser || FALLBACK_KEYS.planUser,
      pipelineState: keys.pipelineState || FALLBACK_KEYS.pipelineState,
      strategiesUser: keys.strategiesUser || FALLBACK_KEYS.strategiesUser,
      strategiesDeleted: keys.strategiesDeleted || FALLBACK_KEYS.strategiesDeleted,
      viewCreatorPresets: keys.viewCreatorPresets || FALLBACK_KEYS.viewCreatorPresets
    };
  }

  function allowedKeys() {
    var keys = storageKeys();
    return Object.keys(keys).map(function(name) { return keys[name]; });
  }

  function isAllowedKey(key) {
    return allowedKeys().indexOf(key) !== -1;
  }

  function safeJson(raw, fallback) {
    if (raw == null) return fallback;
    try { return JSON.parse(raw); }
    catch (_err) { return fallback; }
  }

  function writeLocal(key, value) {
    if (!global.localStorage) return false;
    try {
      global.localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (_err) {
      return false;
    }
  }

  function readLocal(key) {
    if (!global.localStorage) return undefined;
    try { return safeJson(global.localStorage.getItem(key), undefined); }
    catch (_err) { return undefined; }
  }

  function dispatch(name, detail) {
    try {
      global.dispatchEvent(new CustomEvent(name, { detail: detail || {} }));
    } catch (_err) {}
  }

  function fetchJson(path, options) {
    return global.fetch(apiBase() + path, Object.assign({ credentials: 'include' }, options || {}))
      .then(function(response) {
        return response.json().catch(function() { return {}; }).then(function(json) {
          if (!response.ok || json.ok === false) {
            var error = new Error(json.error || ('HTTP ' + response.status));
            error.response = json;
            throw error;
          }
          return json;
        });
      });
  }

  function applyRemoteState(state) {
    var clean = {};
    Object.keys(state || {}).forEach(function(key) {
      if (!isAllowedKey(key)) return;
      clean[key] = state[key];
      writeLocal(key, state[key]);
    });
    _lastState = clean;
    if (Object.keys(clean).length) dispatch('sqx:remote-state-loaded', {
      version: VERSION,
      state: clean,
      keys: Object.keys(clean)
    });
    return clean;
  }

  function bootstrap() {
    if (_bootstrapPromise) return _bootstrapPromise;
    if (!global.fetch || isLocalFileMode()) {
      _ready = true;
      _enabled = false;
      return Promise.resolve({ ok: false, localOnly: true, skipped: isLocalFileMode() ? 'file_mode' : 'fetch_unavailable' });
    }
    _bootstrapPromise = fetchJson('/remote/state/bootstrap')
      .then(function(result) {
        _ready = true;
        _enabled = true;
        applyRemoteState(result.state || {});
        dispatch('sqx:remote-state-ready', {
          version: VERSION,
          enabled: true,
          workspace: result.workspace || {},
          keys: result.stateKeys || []
        });
        return result;
      })
      .catch(function(err) {
        _ready = true;
        _enabled = false;
        _lastError = err.message || 'remote_state_unavailable';
        dispatch('sqx:remote-state-ready', {
          version: VERSION,
          enabled: false,
          error: _lastError
        });
        return { ok: false, error: _lastError };
      });
    return _bootstrapPromise;
  }

  function saveNow(payload, source) {
    if (!_enabled || !payload || !Object.keys(payload).length || !global.fetch) return Promise.resolve({ ok: false, skipped: true });
    _saving = true;
    return fetchJson('/remote/state/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source: source || 'dashboard', state: payload })
    }).then(function(result) {
      _saving = false;
      dispatch('sqx:remote-state-saved', {
        version: VERSION,
        keys: result.savedKeys || []
      });
      return result;
    }).catch(function(err) {
      _saving = false;
      _lastError = err.message || 'remote_state_save_failed';
      dispatch('sqx:remote-state-error', { version: VERSION, error: _lastError });
      return { ok: false, error: _lastError };
    });
  }

  function flushPending() {
    var payload = _pending;
    _pending = {};
    _timer = null;
    return saveNow(payload, 'dashboard-autosave');
  }

  function queueSave(key, value) {
    if (!_enabled || !isAllowedKey(key)) return Promise.resolve({ ok: false, skipped: true });
    _pending[key] = value;
    if (_timer) global.clearTimeout(_timer);
    _timer = global.setTimeout(flushPending, 350);
    return Promise.resolve({ ok: true, queued: true });
  }

  function patchStorage() {
    if (!SQX.storage || SQX.storage.__remoteStatePatched) return;
    var originalSetJson = SQX.storage.setJson;
    SQX.storage.setJson = function(key, value) {
      var result = originalSetJson.call(SQX.storage, key, value);
      if (_enabled && isAllowedKey(key)) queueSave(key, value);
      return result;
    };
    SQX.storage.__remoteStatePatched = true;
  }

  function saveSnapshot(keys, source) {
    var payload = {};
    (keys || allowedKeys()).forEach(function(key) {
      if (!isAllowedKey(key)) return;
      var value = readLocal(key);
      if (value !== undefined) payload[key] = value;
    });
    return saveNow(payload, source || 'dashboard-snapshot');
  }

  var api = {
    version: VERSION,
    bootstrap: bootstrap,
    patchStorage: patchStorage,
    saveNow: saveNow,
    saveSnapshot: saveSnapshot,
    queueSave: queueSave,
    allowedKeys: allowedKeys,
    storageKeys: storageKeys,
    isEnabled: function() { return _enabled; },
    isReady: function() { return _ready; },
    isSaving: function() { return _saving; },
    lastState: function() { return Object.assign({}, _lastState); },
    lastError: function() { return _lastError; }
  };

  SQX.remoteState = SQX.remoteState || api;
  if (SQX.registerModule) SQX.registerModule('remote-state', SQX.remoteState);
  patchStorage();
  bootstrap();
})(window);

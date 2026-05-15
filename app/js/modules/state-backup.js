(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var DEFAULT_KEYS = {
    priorityProgress: 'sqx_priority_progress_v1',
    planUser: 'sqx_plan_user_v1',
    pipelineState: 'sqx_pipeline_state_v1',
    strategiesUser: 'sqx_strategies_user_v1',
    strategiesDeleted: 'sqx_strategies_deleted_v1',
    workflowChecklist: 'sqx_workflow_checklist_v1',
    viewCreatorPresets: 'sqx_view_creator_presets_v1',
    projectGeneratorCustomPresets: 'sqx_pg_custom_presets_v1',
    homeTrace: 'sqx_home_trace_v1',
    apiBase: 'sqx_pg_api_base_v1'
  };

  function apiBase() {
    var config = SQX.config || {};
    var raw = config.raw || global.SQX_CONFIG || {};
    var base = raw.apiBase ? raw.apiBase() : 'http://127.0.0.1:5050/api';
    return String(base || '').replace(/\/$/, '');
  }

  function allowedKeys(config) {
    var cfg = config || SQX.config || {};
    var manifestKeys = cfg.storageKeys ? cfg.storageKeys() : ((global.SQX_CONFIG && global.SQX_CONFIG.storageKeys) || {});
    return Object.keys(DEFAULT_KEYS).map(function(name) {
      return manifestKeys[name] || DEFAULT_KEYS[name];
    }).filter(function(key, index, keys) {
      return key && keys.indexOf(key) === index;
    });
  }

  function safeJson(raw) {
    if (raw == null) return null;
    try { return JSON.parse(raw); }
    catch (_err) { return raw; }
  }

  function collectState(storage, config) {
    var store = storage || global.localStorage;
    var data = {};
    allowedKeys(config).forEach(function(key) {
      try {
        var raw = store.getItem(key);
        if (raw != null) data[key] = safeJson(raw);
      } catch (_err) {}
    });
    return data;
  }

  function applyState(data, storage, config) {
    var store = storage || global.localStorage;
    var allowed = allowedKeys(config);
    var applied = [];
    Object.keys(data || {}).forEach(function(key) {
      if (allowed.indexOf(key) === -1) return;
      try {
        var value = data[key];
        if (typeof value === 'string') store.setItem(key, value);
        else store.setItem(key, JSON.stringify(value));
        applied.push(key);
      } catch (_err) {}
    });
    return applied;
  }

  function setBadge(doc, state, text) {
    var el = (doc || global.document).getElementById('state-backup-indicator');
    if (!el) return;
    el.className = 'state-backup-badge is-' + state;
    el.textContent = text;
  }

  function setStatus(doc, text) {
    var el = (doc || global.document).getElementById('state-restore-status');
    if (el) el.textContent = text;
  }

  function fmtDate(seconds) {
    if (!seconds) return 'fecha no disponible';
    try { return new Date(seconds * 1000).toLocaleString(); }
    catch (_err) { return String(seconds); }
  }

  function listHtml(backups) {
    if (!backups || !backups.length) {
      return '<div class="state-restore-empty">No hay snapshots todavia. Crea uno con "Backup estado".</div>';
    }
    return backups.map(function(item) {
      var name = String(item.name || '');
      var trace = 'Origen: snapshot local · Destino: claves permitidas · Backup previo automatico';
      return '<div class="state-restore-row">' +
        '<div>' +
          '<div class="state-restore-name">' + escapeHtml(name) + '</div>' +
          '<div class="state-restore-meta">' + escapeHtml(fmtDate(item.mtime)) + ' · ' + escapeHtml(item.size_kb || 0) + ' KB</div>' +
          '<div class="state-restore-meta">' + escapeHtml(trace) + '</div>' +
        '</div>' +
        '<button class="export-btn" type="button" data-state-restore="' + escapeHtml(name) + '">Restaurar</button>' +
      '</div>';
    }).join('');
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch];
    });
  }

  function fetchJson(url, options) {
    return global.fetch(url, options).then(function(response) {
      return response.json().then(function(json) {
        if (!response.ok || !json.ok) throw new Error(json.error || ('HTTP ' + response.status));
        return json;
      });
    });
  }

  function createBackup(options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    var payload = collectState(opts.storage, opts.config);
    setBadge(doc, 'busy', 'Guardando...');
    return fetchJson(apiBase() + '/state/backup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(function(result) {
      setBadge(doc, 'ok', 'Backup OK');
      setStatus(doc, 'Snapshot creado: ' + result.filename);
      return result;
    }).catch(function(err) {
      setBadge(doc, 'error', 'Backup offline');
      setStatus(doc, 'No se pudo crear backup: ' + err.message);
      throw err;
    });
  }

  function renderList(backups, doc) {
    var list = (doc || global.document).getElementById('state-restore-list');
    if (list) list.innerHTML = listHtml(backups);
  }

  function refreshList(options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    setStatus(doc, 'Consultando snapshots...');
    return fetchJson(apiBase() + '/state/backups')
      .then(function(result) {
        renderList(result.backups || [], doc);
        setBadge(doc, (result.backups || []).length ? 'ok' : 'warn', (result.backups || []).length + ' backups');
        setStatus(doc, (result.backups || []).length + ' snapshots disponibles.');
        return result.backups || [];
      })
      .catch(function(err) {
        renderList([], doc);
        setBadge(doc, 'error', 'Backup offline');
        setStatus(doc, 'No se pudo listar backups: ' + err.message);
        return [];
      });
  }

  function restoreBackup(filename, options) {
    var opts = options || {};
    var doc = opts.document || global.document;
    if (!filename) return Promise.resolve([]);
    var decision = SQX.modalRegistry && SQX.modalRegistry.confirm
      ? SQX.modalRegistry.confirm({
        document: doc,
        title: 'Restaurar snapshot local',
        message: 'Restaurar este snapshot reemplazara el estado local actual. Antes se creara un backup previo para poder volver atras.',
        confirmLabel: 'Restaurar con backup previo',
        trace: [
          'Snapshot: ' + filename,
          'Lee: /state/restore',
          'Escribe: localStorage permitido',
          'Excluye: licencias, fulfillment y datos sensibles'
        ]
      })
      : Promise.resolve(!global.confirm || global.confirm('Restaurar este snapshot reemplazara el estado local actual. Se creara un backup previo.'));
    return decision.then(function(ok) {
      if (!ok) return [];
      setStatus(doc, 'Creando backup previo...');
      return createBackup(opts).catch(function() { return null; });
    }).then(function(result) {
      if (Array.isArray(result)) return result;
      setStatus(doc, 'Restaurando ' + filename + '...');
      return fetchJson(apiBase() + '/state/restore/' + encodeURIComponent(filename));
    }).then(function(result) {
      if (Array.isArray(result)) return result;
      var data = result.payload && result.payload.data ? result.payload.data : {};
      var applied = applyState(data, opts.storage, opts.config);
      setBadge(doc, 'ok', 'Restaurado');
      setStatus(doc, 'Restauradas ' + applied.length + ' claves. Recargando...');
      if (global.location && global.location.reload) global.setTimeout(function() { global.location.reload(); }, 450);
      return applied;
    }).catch(function(err) {
      setBadge(doc, 'error', 'Restore error');
      setStatus(doc, 'No se pudo restaurar: ' + err.message);
      throw err;
    });
  }

  function openRestore(doc) {
    var backdrop = (doc || global.document).getElementById('state-restore-backdrop');
    if (backdrop) backdrop.style.display = 'flex';
    return refreshList({ document: doc || global.document });
  }

  function closeRestore(doc) {
    var backdrop = (doc || global.document).getElementById('state-restore-backdrop');
    if (backdrop) backdrop.style.display = 'none';
  }

  function bind(doc) {
    var root = doc || global.document;
    var backupBtn = root.getElementById('state-backup-now');
    var restoreBtn = root.getElementById('state-backup-restore');
    var closeBtn = root.getElementById('state-restore-close');
    var refreshBtn = root.getElementById('state-restore-refresh');
    var list = root.getElementById('state-restore-list');

    if (backupBtn) backupBtn.addEventListener('click', function() { createBackup({ document: root }); });
    if (restoreBtn) restoreBtn.addEventListener('click', function() { openRestore(root); });
    if (closeBtn) closeBtn.addEventListener('click', function() { closeRestore(root); });
    if (refreshBtn) refreshBtn.addEventListener('click', function() { refreshList({ document: root }); });
    if (list) {
      list.addEventListener('click', function(event) {
        var target = event.target && event.target.closest ? event.target.closest('[data-state-restore]') : null;
        if (target) restoreBackup(target.getAttribute('data-state-restore'), { document: root });
      });
    }
    root.addEventListener('keydown', function(event) {
      if (event.key === 'Escape') closeRestore(root);
    });
  }

  function init(options) {
    var opts = options || {};
    bind(opts.document || global.document);
    refreshList({ document: opts.document || global.document });
    return { keys: allowedKeys(opts.config) };
  }

  SQX.stateBackup = SQX.stateBackup || {
    allowedKeys: allowedKeys,
    applyState: applyState,
    collectState: collectState,
    createBackup: createBackup,
    init: init,
    listHtml: listHtml,
    refreshList: refreshList,
    restoreBackup: restoreBackup
  };

  if (SQX.registerModule) {
    SQX.registerModule('state-backup', SQX.stateBackup);
  }
})(window);

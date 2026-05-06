(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var config = SQX.config || {};
  var storage = SQX.storage || {};
  var raw = config.raw || global.SQX_CONFIG || {};
  var product = raw.product || (raw.manifest && raw.manifest.product) || {};
  var upgrade = product.upgrade || {};
  var checkout = upgrade.checkout || {};
  var automation = checkout.automation || {};
  var storageKey = 'sqx_fulfillment_operator_v1';
  var cache = {
    requests: [],
    processed: [],
    summary: null,
    receiver: null,
  };

  function byId(id) {
    return global.document.getElementById(id);
  }

  function apiBase() {
    if (raw.apiBase) return raw.apiBase().replace(/\/$/, '');
    return 'http://127.0.0.1:5050/api';
  }

  function endpoint(path) {
    return apiBase() + path;
  }

  function escapeHtml(value) {
    if (SQX.utils && SQX.utils.escapeHtml) return SQX.utils.escapeHtml(value);
    return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
    });
  }

  function getJson(key, fallback) {
    if (storage.getJson) return storage.getJson(key, fallback);
    try {
      return JSON.parse(global.localStorage.getItem(key) || JSON.stringify(fallback));
    } catch (_err) {
      return fallback;
    }
  }

  function setJson(key, value) {
    if (storage.setJson) return storage.setJson(key, value);
    global.localStorage.setItem(key, JSON.stringify(value));
    return true;
  }

  function loadSettings() {
    return getJson(storageKey, {
      privateKey: '',
      zipPath: '',
      supportEmail: '',
    });
  }

  function saveSettings(settings) {
    setJson(storageKey, settings || {});
    return settings;
  }

  function readSettingsForm() {
    return {
      privateKey: (byId('fulfillment-private-key') || {}).value || '',
      zipPath: (byId('fulfillment-zip-path') || {}).value || '',
      supportEmail: (byId('fulfillment-support-email') || {}).value || '',
    };
  }

  function writeSettingsForm(settings) {
    var payload = settings || loadSettings();
    var privateKey = byId('fulfillment-private-key');
    var zipPath = byId('fulfillment-zip-path');
    var supportEmail = byId('fulfillment-support-email');
    if (privateKey) privateKey.value = payload.privateKey || '';
    if (zipPath) zipPath.value = payload.zipPath || '';
    if (supportEmail) supportEmail.value = payload.supportEmail || '';
  }

  function persistSettingsFromForm() {
    return saveSettings(readSettingsForm());
  }

  function setStatus(text, state) {
    var el = byId('fulfillment-queue-status');
    if (!el) return;
    el.textContent = text || '';
    el.classList.remove('is-ok', 'is-warn', 'is-error');
    if (state) el.classList.add('is-' + state);
  }

  function countValue(id, value) {
    var el = byId(id);
    if (el) el.textContent = String(value == null ? '--' : value);
  }

  function statusLabel(status) {
    var map = {
      queued: 'Pendiente',
      processing: 'Procesando',
      needs_review: 'Revision',
      failed: 'Fallido',
      completed: 'Entregado',
      ignored: 'Ignorado',
    };
    return map[status] || status || 'Pendiente';
  }

  function statusClass(status) {
    if (status === 'completed') return 'is-ok';
    if (status === 'failed') return 'is-error';
    if (status === 'needs_review' || status === 'processing') return 'is-warn';
    return 'is-neutral';
  }

  function timeLabel(value) {
    if (!value) return 'sin fecha';
    var date = new Date(value);
    return isNaN(date.getTime()) ? String(value) : date.toLocaleString();
  }

  function metricsFromSummary(summary) {
    var payload = summary || {};
    countValue('fulfillment-queue-count', (payload.queued || 0) + (payload.processing || 0));
    countValue('fulfillment-needs-review-count', payload.needs_review || 0);
    countValue('fulfillment-failed-count', payload.failed || 0);
    countValue('fulfillment-processed-count', payload.processed_receipts || 0);
  }

  function requestActions(request) {
    var actions = [];
    var name = escapeHtml(request.name || '');
    if (request.operator_status === 'failed') {
      actions.push('<button type="button" class="fulfillment-btn" data-fulfillment-action="process" data-request-file="' + name + '">Reintentar</button>');
    } else if (request.operator_status !== 'completed' && request.operator_status !== 'ignored') {
      actions.push('<button type="button" class="fulfillment-btn" data-fulfillment-action="process" data-request-file="' + name + '">Procesar</button>');
    }
    if (request.operator_status !== 'ignored') {
      actions.push('<button type="button" class="fulfillment-btn ghost" data-fulfillment-action="ignore" data-request-file="' + name + '">Ignorar</button>');
    }
    if (request.operator_status === 'ignored' || request.operator_status === 'needs_review') {
      actions.push('<button type="button" class="fulfillment-btn ghost" data-fulfillment-action="queue" data-request-file="' + name + '">Recolar</button>');
    }
    return actions.join('');
  }

  function requestRowHtml(request) {
    var errorHtml = request.last_error
      ? '<div class="fulfillment-request-error">' + escapeHtml(request.last_error) + '</div>'
      : '';
    var noteHtml = request.operator_note
      ? '<div class="fulfillment-request-note">' + escapeHtml(request.operator_note) + '</div>'
      : '';
    return (
      '<div class="fulfillment-request-card">' +
        '<div class="fulfillment-request-top">' +
          '<span class="fulfillment-pill ' + statusClass(request.operator_status) + '">' + escapeHtml(statusLabel(request.operator_status)) + '</span>' +
          '<span class="fulfillment-request-plan">' + escapeHtml(request.plan || 'plan') + '</span>' +
        '</div>' +
        '<strong class="fulfillment-request-email">' + escapeHtml(request.customer_email || 'sin email') + '</strong>' +
        '<div class="fulfillment-request-meta">' +
          '<span>' + escapeHtml(request.source_event || 'evento') + '</span>' +
          '<span>' + escapeHtml(request.order_id || 'sin pedido') + '</span>' +
        '</div>' +
        '<div class="fulfillment-request-meta">' +
          '<span>Intentos: ' + escapeHtml(request.attempt_count || 0) + '</span>' +
          '<span>' + escapeHtml(timeLabel(request.last_attempt_at || request.stored_at)) + '</span>' +
        '</div>' +
        noteHtml +
        errorHtml +
        '<div class="fulfillment-request-actions">' + requestActions(request) + '</div>' +
      '</div>'
    );
  }

  function renderQueue() {
    var list = byId('fulfillment-request-list');
    var empty = byId('fulfillment-empty');
    metricsFromSummary(cache.summary);
    if (!list) return cache;

    if (!cache.requests.length) {
      list.innerHTML = '';
      if (empty) empty.style.display = '';
      return cache;
    }

    if (empty) empty.style.display = 'none';
    list.innerHTML = cache.requests.slice(0, 8).map(requestRowHtml).join('');
    return cache;
  }

  async function fetchQueue() {
    var response = await fetch(endpoint(automation.queueListEndpoint || '/fulfillment/requests'));
    var payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.message || payload.error || 'No se pudo leer la cola.');
    }
    cache.requests = payload.requests || [];
    cache.processed = payload.processed || [];
    cache.summary = payload.summary || {};
    cache.receiver = payload.receiver || {};
    var receiverReady = cache.receiver.secret_configured ? 'receiver listo' : 'receiver sin secreto';
    setStatus('Cola actualizada: ' + (cache.summary.total_requests || 0) + ' requests, ' + receiverReady + '.', cache.receiver.secret_configured ? 'ok' : 'warn');
    renderQueue();
    return payload;
  }

  async function updateRequestStatus(requestFile, operatorStatus, note) {
    var response = await fetch(endpoint(automation.requestStatusEndpoint || '/fulfillment/request-status'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request_file: requestFile,
        operator_status: operatorStatus,
        note: note || '',
      })
    });
    var payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.message || payload.error || 'No se pudo actualizar el estado.');
    }
    return payload;
  }

  async function processRequest(requestFile) {
    var settings = persistSettingsFromForm();
    if (!settings.privateKey || !settings.zipPath) {
      setStatus('Completa la ruta de private key y la ruta del ZIP portable antes de procesar.', 'warn');
      throw new Error('missing_operator_paths');
    }
    setStatus('Procesando request ' + requestFile + '...', 'warn');
    var response = await fetch(endpoint(automation.processEndpoint || '/fulfillment/process'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request_file: requestFile,
        private_key: settings.privateKey,
        zip_path: settings.zipPath,
        support_email: settings.supportEmail || '',
      })
    });
    var payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || payload.message || 'Fulfillment fallido');
    }
    setStatus('Entrega completada para ' + requestFile + '.', 'ok');
    if (global.addHomeTrace) {
      global.addHomeTrace('Fulfillment completado', requestFile, 'ok');
    }
    return payload;
  }

  function handleAction(action, requestFile) {
    if (!requestFile) return Promise.resolve();
    if (action === 'process') {
      return processRequest(requestFile).then(fetchQueue);
    }
    if (action === 'ignore') {
      return updateRequestStatus(requestFile, 'ignored', 'Marcado desde panel operador').then(function() {
        setStatus('Request marcada como ignorada.', 'warn');
        if (global.addHomeTrace) {
          global.addHomeTrace('Fulfillment ignorado', requestFile, 'warn');
        }
        return fetchQueue();
      });
    }
    if (action === 'queue') {
      return updateRequestStatus(requestFile, 'queued', 'Recolada desde panel operador').then(function() {
        setStatus('Request recolada para nuevo intento.', 'ok');
        if (global.addHomeTrace) {
          global.addHomeTrace('Fulfillment recolado', requestFile, 'ok');
        }
        return fetchQueue();
      });
    }
    return Promise.resolve();
  }

  function bindActions() {
    var refreshBtn = byId('fulfillment-refresh-btn');
    var list = byId('fulfillment-request-list');
    ['fulfillment-private-key', 'fulfillment-zip-path', 'fulfillment-support-email'].forEach(function(id) {
      var node = byId(id);
      if (!node) return;
      node.addEventListener('input', persistSettingsFromForm);
    });
    if (refreshBtn) {
      refreshBtn.addEventListener('click', function() {
        fetchQueue().catch(function(err) {
          setStatus('No se pudo leer la cola: ' + err.message, 'error');
        });
      });
    }
    if (list) {
      list.addEventListener('click', function(event) {
        var button = event.target.closest('[data-fulfillment-action]');
        if (!button) return;
        var action = button.getAttribute('data-fulfillment-action');
        var requestFile = button.getAttribute('data-request-file');
        handleAction(action, requestFile).catch(function(err) {
          setStatus('Operacion no completada: ' + err.message, 'error');
          if (global.addHomeTrace) {
            global.addHomeTrace('Fulfillment con incidencia', requestFile + ' · ' + err.message, 'err');
          }
        });
      });
    }
  }

  function init() {
    if (!automation.operatorPanelEnabled) return;
    writeSettingsForm(loadSettings());
    bindActions();
    fetchQueue().catch(function(err) {
      setStatus('No se pudo conectar con la cola privada: ' + err.message, 'error');
    });
  }

  SQX.fulfillment = SQX.fulfillment || {
    apiBase: apiBase,
    endpoint: endpoint,
    fetchQueue: fetchQueue,
    handleAction: handleAction,
    init: init,
    loadSettings: loadSettings,
    processRequest: processRequest,
    readSettingsForm: readSettingsForm,
    renderQueue: renderQueue,
    saveSettings: saveSettings,
    setStatus: setStatus,
    storageKey: storageKey,
    updateRequestStatus: updateRequestStatus,
    writeSettingsForm: writeSettingsForm
  };

  if (SQX.registerModule) {
    SQX.registerModule('fulfillment', SQX.fulfillment);
  }
})(window);

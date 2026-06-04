(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var VERSION = 'sqx-edge.sqx-readiness-status-v1';
  var FALLBACK_KEY = 'sqx_readiness_status_v1';
  var REQUIRED_LABELS = {
    sqx_root_selected: 'Ruta SQX seleccionada',
    sqx_version_compatible: 'Version SQX 142 compatible',
    data_db_found: 'data.db detectada',
    brokers_validated: 'Brokers Darwinex y Dukascopy validados',
    curated_assets_validated: 'Activos y timeframes curados validados',
    snippets_ready: 'Snippets SQX Edge instalados',
    correlation_view_ready: 'View CORR1 instalada',
    views_ready: 'View CORR1 instalada',
    portable_source_acknowledged: 'Portable autorizado o pendiente reconocido',
    sensitive_files_excluded: 'Archivos sensibles excluidos'
  };
  var SENSITIVE_SELECTORS = [
    '#pg-generate-selected-c1',
    '#pg-generate-selected-c2',
    '#pg-custom-generate',
    '#edge-registry-apply',
    '#edge-corr2-apply',
    '#ps-registry-apply',
    '#ps-corr2-apply',
    '[data-edge-tool="projectgen"]',
    '[data-edge-tool="templatemaker"]',
    '[data-sqx-readiness-requires]'
  ];
  var manifest = null;
  var status = null;
  var initialized = false;

  function byId(id) {
    return global.document && global.document.getElementById ? global.document.getElementById(id) : null;
  }

  function apiBase() {
    var raw = (SQX.config && SQX.config.raw) || global.SQX_CONFIG || {};
    var base = raw.apiBase ? raw.apiBase() : '/api';
    return String(base || '/api').replace(/\/$/, '');
  }

  function storageKey() {
    if (SQX.config && SQX.config.storageKey) {
      return SQX.config.storageKey('sqxReadinessStatus', FALLBACK_KEY);
    }
    var keys = (SQX.config && SQX.config.storageKeys && SQX.config.storageKeys()) || (global.SQX_CONFIG && global.SQX_CONFIG.storageKeys) || {};
    return keys.sqxReadinessStatus || FALLBACK_KEY;
  }

  function getJson(key, fallback) {
    if (SQX.storage && SQX.storage.getJson) return SQX.storage.getJson(key, fallback);
    try {
      return JSON.parse(global.localStorage.getItem(key) || JSON.stringify(fallback));
    } catch (_err) {
      return fallback;
    }
  }

  function setJson(key, value) {
    if (SQX.storage && SQX.storage.setJson) return SQX.storage.setJson(key, value);
    try {
      global.localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (_err) {
      return false;
    }
  }

  function requiredChecks() {
    var list = manifest && manifest.requiredChecklist ? manifest.requiredChecklist : Object.keys(REQUIRED_LABELS);
    return list.filter(function(id) { return !!id; });
  }

  function fallbackStatus() {
    var checks = {};
    requiredChecks().forEach(function(id) { checks[id] = false; });
    return {
      ok: true,
      version: VERSION,
      complete: false,
      source: 'browser_default',
      checks: checks,
      missing: Object.keys(checks),
      privacy: { local_paths_returned: false, data_db_copied: false }
    };
  }

  function normalizeStatus(value) {
    var next = value && typeof value === 'object' ? value : fallbackStatus();
    var checks = {};
    requiredChecks().forEach(function(id) {
      var raw = next.checks || {};
      checks[id] = id === 'correlation_view_ready'
        ? !!(raw.correlation_view_ready || raw.views_ready || raw.viewsReady)
        : !!raw[id];
    });
    next.checks = checks;
    next.missing = Object.keys(checks).filter(function(id) { return !checks[id]; }).sort();
    next.complete = next.missing.length === 0 && !(next.blockers && next.blockers.length);
    next.version = next.version || VERSION;
    next.privacy = { local_paths_returned: false, data_db_copied: false };
    return next;
  }

  function fetchJson(path, options) {
    if (!global.fetch) return Promise.reject(new Error('fetch_unavailable'));
    return global.fetch(apiBase() + path, options || {}).then(function(response) {
      return response.json().then(function(payload) {
        if (!response.ok && !payload.ok) payload.httpStatus = response.status;
        return payload;
      });
    });
  }

  function checkboxes() {
    if (!global.document || !global.document.querySelectorAll) return [];
    return Array.prototype.slice.call(global.document.querySelectorAll('[data-sqx-readiness-check]'));
  }

  function updateDataset(complete) {
    if (global.document && global.document.documentElement) {
      global.document.documentElement.dataset.sqxReadiness = complete ? 'complete' : 'blocked';
    }
  }

  function applySensitiveDisabled(complete) {
    if (!global.document || !global.document.querySelectorAll) return;
    SENSITIVE_SELECTORS.forEach(function(selector) {
      Array.prototype.slice.call(global.document.querySelectorAll(selector)).forEach(function(el) {
        if (!el) return;
        el.disabled = !complete;
        el.setAttribute('aria-disabled', complete ? 'false' : 'true');
        el.classList.toggle('sqx-readiness-disabled', !complete);
      });
    });
  }

  function render() {
    status = normalizeStatus(status || getJson(storageKey(), fallbackStatus()));
    setJson(storageKey(), status);
    updateDataset(!!status.complete);
    applySensitiveDisabled(!!status.complete);

    var backdrop = byId('sqx-readiness-backdrop');
    var progress = byId('sqx-readiness-progress');
    var detail = byId('sqx-readiness-detail');
    var count = byId('sqx-readiness-count');
    var completeCount = 0;
    var checks = status.checks || {};

    checkboxes().forEach(function(input) {
      var id = input.dataset.sqxReadinessCheck;
      var ok = !!checks[id];
      input.checked = ok;
      if (ok) completeCount += 1;
      var row = input.closest ? input.closest('.sqx-readiness-row') : null;
      if (row) row.classList.toggle('is-complete', ok);
    });

    var total = requiredChecks().length || 1;
    if (progress) progress.style.width = Math.round((completeCount / total) * 100) + '%';
    if (count) count.textContent = completeCount + '/' + total;
    if (detail) {
      detail.textContent = status.complete
        ? 'Preparacion SQX Edge completada. Funciones SQX desbloqueadas.'
        : 'Faltan: ' + (status.missing || []).map(function(id) { return REQUIRED_LABELS[id] || id; }).join(', ');
    }
    if (backdrop) backdrop.hidden = !!status.complete || backdrop.dataset.dismissed === '1';
  }

  function collectChecksFromUi() {
    var checks = {};
    checkboxes().forEach(function(input) {
      checks[input.dataset.sqxReadinessCheck] = !!input.checked;
    });
    return checks;
  }

  function postManual() {
    status = normalizeStatus({ checks: collectChecksFromUi(), source: 'manual_checklist' });
    render();
    return fetchJson('/sqx-readiness/status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ checks: status.checks })
    }).then(function(payload) {
      status = normalizeStatus(payload);
      render();
      return status;
    }).catch(function() {
      return status;
    });
  }

  function importReport(report) {
    if (!report || typeof report !== 'object') return Promise.reject(new Error('invalid_report'));
    return fetchJson('/sqx-readiness/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ report: report })
    }).then(function(payload) {
      status = normalizeStatus(payload);
      render();
      return status;
    });
  }

  function readImportedFile(file) {
    if (!file) return Promise.reject(new Error('missing_file'));
    if (file.text) {
      return file.text().then(function(text) { return JSON.parse(text); });
    }
    return new Promise(function(resolve, reject) {
      var reader = new global.FileReader();
      reader.onload = function() {
        try { resolve(JSON.parse(reader.result)); }
        catch (err) { reject(err); }
      };
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }

  function bind() {
    checkboxes().forEach(function(input) {
      input.addEventListener('change', postManual);
    });
    var importer = byId('sqx-readiness-report-file');
    if (importer) {
      importer.addEventListener('change', function(event) {
        var file = event.target.files && event.target.files[0];
        readImportedFile(file).then(importReport).catch(function(err) {
          var detail = byId('sqx-readiness-detail');
          if (detail) detail.textContent = 'No se pudo importar el reporte: ' + err.message;
        });
      });
    }
    var dismiss = byId('sqx-readiness-dismiss');
    if (dismiss) {
      dismiss.addEventListener('click', function() {
        var backdrop = byId('sqx-readiness-backdrop');
        if (backdrop) {
          backdrop.dataset.dismissed = '1';
          backdrop.hidden = true;
        }
      });
    }
    var refresh = byId('sqx-readiness-refresh');
    if (refresh) refresh.addEventListener('click', refreshStatus);
  }

  function refreshStatus() {
    var local = getJson(storageKey(), fallbackStatus());
    status = normalizeStatus(local);
    render();
    return Promise.all([
      fetchJson('/sqx-readiness/manifest').catch(function() { return manifest; }),
      fetchJson('/sqx-readiness/status').catch(function() { return status; })
    ]).then(function(results) {
      manifest = results[0] || manifest;
      status = normalizeStatus(results[1] || status);
      render();
      return status;
    });
  }

  function init() {
    if (initialized) return refreshStatus();
    initialized = true;
    bind();
    return refreshStatus();
  }

  SQX.sqxReadiness = {
    version: VERSION,
    init: init,
    refresh: refreshStatus,
    importReport: importReport,
    postManual: postManual,
    currentStatus: function() { return status; },
    storageKey: storageKey
  };

  if (SQX.registerModule) {
    SQX.registerModule('sqx-readiness', SQX.sqxReadiness);
  }
})(window);

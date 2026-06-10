(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var config = SQX.config || {};
  var raw = config.raw || global.SQX_CONFIG || {};

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
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function statusClass(payload) {
    if (!payload || payload.state === 'api_error') return 'error';
    return payload.available && payload.status === 'GO' ? 'ok' : 'warn';
  }

  function setStatus(text, state) {
    var el = byId('mtf-evidence-status');
    if (!el) return;
    el.textContent = text || '';
    el.classList.remove('is-ok', 'is-warn', 'is-error');
    if (state) el.classList.add('is-' + state);
  }

  function setBadge(text, state) {
    var badge = byId('mtf-evidence-badge');
    if (!badge) return;
    badge.textContent = text || 'Pendiente';
    badge.classList.remove('is-ok', 'is-warn', 'is-error');
    if (state) badge.classList.add('is-' + state);
  }

  function setMetric(id, value) {
    var el = byId(id);
    if (!el) return;
    el.textContent = value == null || value === '' ? '--' : String(value);
  }

  function updatePriorityStrip(payload) {
    var source = byId('priority-source-current');
    var note = byId('priority-source-note');
    var selector = byId('priority-tf-selector');
    if (!source || !note) return;

    if (payload && payload.available && payload.status === 'GO') {
      source.textContent = 'MTF validado';
      note.textContent = 'Evidencia A56 GO disponible en Inicio, solo lectura.';
      if (selector) selector.classList.add('is-locked');
      return;
    }

    source.textContent = 'H1 baseline';
    note.textContent = 'Multi-TF preparado; pendiente de evidencia A56 GO.';
    if (selector) selector.classList.add('is-locked');
  }

  function outputHtml(item) {
    return '<div class="mtf-evidence-row">' +
      '<span>' + escapeHtml(item.timeframe || item.name || 'MTF') + '</span>' +
      '<strong>' + escapeHtml(item.file || item.message || '') + '</strong>' +
      '</div>';
  }

  function fallbackRows(payload) {
    var failures = payload && Array.isArray(payload.failures) ? payload.failures : [];
    if (!failures.length) return '';
    return failures.slice(0, 3).map(function(message) {
      return outputHtml({ timeframe: 'Pendiente', file: message });
    }).join('');
  }

  function renderEvidence(payload) {
    var summary = (payload && payload.summary) || {};
    var state = statusClass(payload);
    var list = byId('mtf-evidence-list');
    var empty = byId('mtf-evidence-empty');
    var rows = '';

    setMetric('mtf-evidence-tf-count', summary.timeframeCount);
    setMetric('mtf-evidence-asset-count', summary.assetCount);
    setMetric('mtf-evidence-covered-count', summary.currentPlanMtfCovered);
    setBadge(payload && payload.status ? payload.status : 'API', state);
    setStatus(payload && payload.message ? payload.message : 'No se pudo leer la evidencia MTF.', state);
    updatePriorityStrip(payload);

    if (payload && payload.available && Array.isArray(payload.outputs)) {
      rows = payload.outputs.map(outputHtml).join('');
    } else {
      rows = fallbackRows(payload);
    }

    if (list) list.innerHTML = rows;
    if (empty) empty.style.display = rows ? 'none' : 'block';
    return payload;
  }

  async function fetchEvidence() {
    var response = await fetch(endpoint('/mtf/evidence'));
    var payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.message || payload.error || 'No se pudo leer la evidencia MTF.');
    }
    return payload;
  }

  async function refreshEvidence() {
    setStatus('Comprobando evidencia A56...', 'warn');
    try {
      var payload = await fetchEvidence();
      renderEvidence(payload);
      if (global.addHomeTrace) {
        global.addHomeTrace('Evidencia MTF', payload.available ? 'A56 GO disponible' : 'A56 pendiente', payload.available ? 'ok' : 'warn');
      }
      return payload;
    } catch (err) {
      var payload = {
        ok: false,
        available: false,
        status: 'API',
        state: 'api_error',
        message: 'API SQX Edge no disponible para evidencia MTF.',
        summary: {},
        failures: [err.message]
      };
      renderEvidence(payload);
      if (global.addHomeTrace) {
        global.addHomeTrace('Evidencia MTF no disponible', err.message, 'err');
      }
      return payload;
    }
  }

  function bindPanel() {
    var btn = byId('mtf-evidence-refresh-btn');
    if (!btn) return;
    btn.addEventListener('click', function() {
      refreshEvidence().catch(function() {});
    });
  }

  function init() {
    bindPanel();
    refreshEvidence().catch(function() {});
  }

  SQX.mtfEvidence = SQX.mtfEvidence || {
    apiBase: apiBase,
    bindPanel: bindPanel,
    endpoint: endpoint,
    escapeHtml: escapeHtml,
    fetchEvidence: fetchEvidence,
    init: init,
    refreshEvidence: refreshEvidence,
    renderEvidence: renderEvidence,
    setStatus: setStatus,
    statusClass: statusClass,
    updatePriorityStrip: updatePriorityStrip
  };

  if (SQX.registerModule) {
    SQX.registerModule('mtf-evidence', SQX.mtfEvidence);
  }
})(window);

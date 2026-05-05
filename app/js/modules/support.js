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

  function setStatus(text, state) {
    var el = byId('support-diagnostic-status');
    if (!el) return;
    el.textContent = text || '';
    el.classList.remove('is-ok', 'is-warn', 'is-error');
    if (state) el.classList.add('is-' + state);
  }

  function diagnosticsFilename(payload) {
    return payload.filename || 'SQX_support_diagnostic.json';
  }

  function downloadJson(payload, filename) {
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var link = global.document.createElement('a');
    link.href = url;
    link.download = filename;
    global.document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  async function fetchDiagnostics() {
    var response = await fetch(apiBase() + '/support/diagnostics');
    var payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.message || payload.error || 'No se pudo generar el diagnostico.');
    }
    return payload;
  }

  async function generateDiagnostics() {
    setStatus('Generando diagnostico seguro...', 'warn');
    try {
      var payload = await fetchDiagnostics();
      downloadJson(payload, diagnosticsFilename(payload));
      setStatus('Diagnostico descargado. No incluye rutas ni licencia.', 'ok');
      if (global.addHomeTrace) {
        global.addHomeTrace('Diagnostico de soporte', 'JSON local seguro generado', 'ok');
      }
      return payload;
    } catch (err) {
      setStatus('No se pudo conectar con la API local.', 'error');
      if (global.addHomeTrace) {
        global.addHomeTrace('Diagnostico no disponible', err.message, 'err');
      }
      throw err;
    }
  }

  function bindPanel() {
    var btn = byId('support-diagnostic-btn');
    if (!btn) return;
    btn.addEventListener('click', function() {
      generateDiagnostics().catch(function() {});
    });
  }

  function init() {
    bindPanel();
    setStatus('Listo para generar un informe seguro.', 'ok');
  }

  SQX.support = SQX.support || {
    apiBase: apiBase,
    bindPanel: bindPanel,
    diagnosticsFilename: diagnosticsFilename,
    downloadJson: downloadJson,
    fetchDiagnostics: fetchDiagnostics,
    generateDiagnostics: generateDiagnostics,
    init: init,
    setStatus: setStatus
  };

  if (SQX.registerModule) {
    SQX.registerModule('support', SQX.support);
  }
})(window);

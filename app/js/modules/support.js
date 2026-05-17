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

  function setIncidentStatus(text, state) {
    var el = byId('support-incident-status');
    if (!el) return;
    el.textContent = text || '';
    el.classList.remove('is-ok', 'is-warn', 'is-error');
    if (state) el.classList.add('is-' + state);
  }

  function valueOf(id) {
    var el = byId(id);
    return el ? String(el.value || '').trim() : '';
  }

  function checked(id) {
    var el = byId(id);
    return !!(el && el.checked);
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

  function collectIncidentPayload() {
    return {
      category: valueOf('support-incident-category') || 'other',
      severity: valueOf('support-incident-severity') || 'medium',
      summary: valueOf('support-incident-summary'),
      steps: valueOf('support-incident-steps'),
      expected: valueOf('support-incident-expected'),
      actual: valueOf('support-incident-actual'),
      includeDiagnostic: checked('support-incident-include-diagnostic')
    };
  }

  function clearIncidentForm() {
    ['support-incident-summary', 'support-incident-steps', 'support-incident-expected', 'support-incident-actual'].forEach(function(id) {
      var el = byId(id);
      if (el) el.value = '';
    });
  }

  async function submitIncident() {
    var payload = collectIncidentPayload();
    if (!payload.summary) {
      setIncidentStatus('Añade un resumen corto para registrar la incidencia.', 'error');
      return { ok: false, error: 'summary_required' };
    }
    var btn = byId('support-incident-submit');
    if (btn) btn.disabled = true;
    setIncidentStatus('Registrando incidencia segura...', 'warn');
    try {
      var response = await fetch(apiBase() + '/support/incidents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      var result = await response.json();
      if (!response.ok || !result.ok) {
        throw new Error(result.message || result.error || 'No se pudo registrar la incidencia.');
      }
      clearIncidentForm();
      setIncidentStatus('Incidencia registrada: ' + result.caseId + '.', 'ok');
      if (global.addHomeTrace) {
        global.addHomeTrace('Incidencia soporte', result.caseId, 'ok');
      }
      return result;
    } catch (err) {
      setIncidentStatus('No se pudo registrar la incidencia. Revisa la API local.', 'error');
      if (global.addHomeTrace) {
        global.addHomeTrace('Incidencia no registrada', err.message, 'err');
      }
      return { ok: false, error: err.message };
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  function bindPanel() {
    var btn = byId('support-diagnostic-btn');
    var incidentBtn = byId('support-incident-submit');
    if (btn && !btn.dataset.boundSupportDiagnostic) {
      btn.dataset.boundSupportDiagnostic = '1';
      btn.addEventListener('click', function() {
        generateDiagnostics().catch(function() {});
      });
    }
    if (incidentBtn && !incidentBtn.dataset.boundSupportIncident) {
      incidentBtn.dataset.boundSupportIncident = '1';
      incidentBtn.addEventListener('click', function() {
        submitIncident().catch(function() {});
      });
    }
  }

  function init() {
    bindPanel();
    setStatus('Listo para generar un informe seguro.', 'ok');
    setIncidentStatus('Sin incidencias registradas en esta sesion.', 'ok');
  }

  SQX.support = SQX.support || {
    apiBase: apiBase,
    bindPanel: bindPanel,
    clearIncidentForm: clearIncidentForm,
    collectIncidentPayload: collectIncidentPayload,
    diagnosticsFilename: diagnosticsFilename,
    downloadJson: downloadJson,
    fetchDiagnostics: fetchDiagnostics,
    generateDiagnostics: generateDiagnostics,
    init: init,
    setIncidentStatus: setIncidentStatus,
    setStatus: setStatus,
    submitIncident: submitIncident
  };

  if (SQX.registerModule) {
    SQX.registerModule('support', SQX.support);
  }
})(window);

(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var config = SQX.config || {};
  var raw = config.raw || global.SQX_CONFIG || {};
  var cache = {
    summary: null,
    customers: [],
    privacy: null,
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

  function setStatus(text, state) {
    var el = byId('customer-cockpit-status');
    if (!el) return;
    el.textContent = text || '';
    el.classList.remove('is-ok', 'is-warn', 'is-error');
    if (state) el.classList.add('is-' + state);
  }

  function countValue(id, value) {
    var el = byId(id);
    if (el) el.textContent = String(value == null ? '--' : value);
  }

  function riskClass(risk) {
    if (risk === 'ok') return 'is-ok';
    if (risk === 'support' || risk === 'activation') return 'is-warn';
    if (risk === 'refund') return 'is-error';
    return 'is-neutral';
  }

  function riskLabel(risk) {
    var labels = {
      ok: 'OK',
      support: 'Soporte',
      activation: 'Activacion',
      refund: 'Refund',
    };
    return labels[risk] || 'Revision';
  }

  function customerHtml(customer) {
    var opps = [];
    if (customer.opportunities && customer.opportunities.template_pack) opps.push('Templates');
    if (customer.opportunities && customer.opportunities.setup_assist) opps.push('Setup Assist');
    return (
      '<div class="customer-cockpit-card">' +
        '<div class="customer-cockpit-card-top">' +
          '<span class="customer-cockpit-pill ' + riskClass(customer.risk) + '">' + escapeHtml(riskLabel(customer.risk)) + '</span>' +
          '<span class="customer-cockpit-plan">' + escapeHtml(customer.plan || 'plan') + '</span>' +
        '</div>' +
        '<strong>' + escapeHtml(customer.customer_ref || 'customer') + '</strong>' +
        '<div class="customer-cockpit-meta">' +
          '<span>' + escapeHtml(customer.renewal_label || 'Sin decision') + '</span>' +
          '<span>' + escapeHtml(customer.days_to_renewal) + ' dias</span>' +
        '</div>' +
        '<div class="customer-cockpit-meta">' +
          '<span>Owner: ' + escapeHtml(customer.success_owner || 'sin owner') + '</span>' +
          '<span>Valor: ' + escapeHtml(customer.value_checkins_completed || 0) + '</span>' +
        '</div>' +
        '<p>' + escapeHtml(customer.next_action || 'Mantener seguimiento.') + '</p>' +
        '<small>' + escapeHtml(opps.length ? 'Oportunidad: ' + opps.join(' + ') : 'Sin upsell pendiente') + '</small>' +
      '</div>'
    );
  }

  function renderCockpit(payload) {
    var data = payload || {};
    var summary = data.summary || {};
    var customers = data.customers || [];
    var list = byId('customer-cockpit-list');
    var empty = byId('customer-cockpit-empty');
    cache.summary = summary;
    cache.customers = customers;
    cache.privacy = data.privacy || {};

    countValue('customer-cockpit-customer-count', summary.customers || 0);
    countValue('customer-cockpit-renewal-count', summary.renewal_due || 0);
    countValue('customer-cockpit-support-count', summary.support_open || 0);
    countValue('customer-cockpit-opportunity-count', (summary.template_opportunities || 0) + (summary.setup_assist_opportunities || 0));

    if (!list) return data;
    if (!customers.length) {
      list.innerHTML = '';
      if (empty) empty.style.display = '';
      setStatus('Sin clientes Pro registrados. El cockpit esta listo para evidencia real.', 'warn');
      return data;
    }
    if (empty) empty.style.display = 'none';
    list.innerHTML = customers.slice(0, 6).map(customerHtml).join('');
    setStatus('Cockpit actualizado con ' + customers.length + ' clientes redactados.', 'ok');
    return data;
  }

  async function fetchCockpit() {
    var response = await fetch(endpoint('/customer-cockpit'));
    var payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.message || payload.error || 'No se pudo leer customer cockpit.');
    }
    return renderCockpit(payload);
  }

  function bindActions() {
    var refreshBtn = byId('customer-cockpit-refresh-btn');
    if (!refreshBtn) return;
    refreshBtn.addEventListener('click', function() {
      fetchCockpit().catch(function(err) {
        setStatus('No se pudo actualizar cockpit: ' + err.message, 'error');
      });
    });
  }

  function init() {
    bindActions();
    fetchCockpit().catch(function(err) {
      setStatus('Cockpit pendiente de API: ' + err.message, 'error');
    });
  }

  SQX.customerCockpit = SQX.customerCockpit || {
    apiBase: apiBase,
    endpoint: endpoint,
    fetchCockpit: fetchCockpit,
    init: init,
    renderCockpit: renderCockpit,
    riskClass: riskClass,
    riskLabel: riskLabel,
    setStatus: setStatus,
  };

  if (SQX.registerModule) {
    SQX.registerModule('customer-cockpit', SQX.customerCockpit);
  }
})(window);

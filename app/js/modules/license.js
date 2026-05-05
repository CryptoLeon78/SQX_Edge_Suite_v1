(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var config = SQX.config || {};
  var storage = SQX.storage || {};
  var raw = config.raw || global.SQX_CONFIG || {};
  var product = raw.product || (raw.manifest && raw.manifest.product) || {};
  var licensing = product.licensing || {};
  var accessLevels = product.accessLevels || {};
  var features = product.features || {};
  var storageKey = licensing.storageKey || 'sqx_license_state_v1';
  var backendStatus = null;

  function byId(id) {
    return global.document.getElementById(id);
  }

  function apiBase() {
    if (raw.apiBase) return raw.apiBase().replace(/\/$/, '');
    return 'http://127.0.0.1:5050/api';
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
      return {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      }[ch];
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

  function remove(key) {
    if (storage.remove) return storage.remove(key);
    global.localStorage.removeItem(key);
    return true;
  }

  function featureList(level) {
    var item = accessLevels[level] || {};
    return item.features || [];
  }

  function levelLabel(level, fallback) {
    var item = accessLevels[level] || {};
    return item.label || fallback || level;
  }

  function parseDate(value) {
    if (!value) return null;
    var date = new Date(value);
    return isNaN(date.getTime()) ? null : date;
  }

  function daysUntil(value) {
    var date = parseDate(value);
    if (!date) return null;
    var today = new Date();
    return Math.ceil((date.getTime() - today.getTime()) / 86400000);
  }

  function buildStatus() {
    var build = product.build || {};
    if (build.channel === 'internal') {
      return {
        active: true,
        state: 'internal',
        plan: 'internal',
        label: levelLabel('internal', 'SQX Edge Internal'),
        source: 'build_profile',
        features: featureList('internal'),
        message: 'Build interno con todas las capacidades habilitadas para desarrollo.'
      };
    }
    return {
      active: false,
      state: 'free',
      plan: 'free',
      label: levelLabel('free', 'SQX Edge Free'),
      source: 'build_profile',
      features: featureList('free'),
      message: 'Modo Free. Las funciones Pro requieren licencia.'
    };
  }

  function statusFromLicense(payload) {
    var plan = String(payload.plan || 'free');
    var level = plan.indexOf('pro') === 0 ? 'pro' : 'free';
    var signature = String(payload.signature || '').trim();
    var remaining = daysUntil(payload.expires_at);
    if (!signature) {
      return {
        active: false,
        state: 'invalid',
        plan: plan,
        label: 'Licencia no valida',
        source: 'local_license',
        features: featureList('free'),
        message: 'Licencia cargada sin firma verificable.'
      };
    }
    if (remaining !== null && remaining < 0) {
      return {
        active: false,
        state: 'expired',
        plan: plan,
        label: 'Licencia expirada',
        source: 'local_license',
        features: featureList('free'),
        expires_at: payload.expires_at,
        days_remaining: remaining,
        message: 'Tu licencia ha expirado. Tus datos siguen disponibles en modo Free.'
      };
    }
    return {
      active: false,
      state: level === 'pro' ? 'pro_pending' : 'free',
      plan: plan,
      label: level === 'pro' ? 'SQX Edge Pro pendiente' : levelLabel('free', 'SQX Edge Free'),
      source: 'local_license',
      features: featureList('free'),
      expires_at: payload.expires_at,
      days_remaining: remaining,
      customer: payload.customer_name || '',
      license_id: payload.license_id || '',
      message: level === 'pro'
        ? 'Licencia Pro cargada. Falta verificacion criptografica en una fase posterior.'
        : 'Licencia Free cargada.'
    };
  }

  function currentStatus() {
    if (backendStatus && typeof backendStatus === 'object') return backendStatus;
    var build = product.build || {};
    if (build.channel === 'internal') return buildStatus();
    var payload = getJson(storageKey, null);
    if (payload && typeof payload === 'object') return statusFromLicense(payload);
    return buildStatus();
  }

  async function fetchJson(path, options) {
    var response = await fetch(apiBase() + path, options);
    var payload = await response.json();
    if (!response.ok || payload.ok === false) {
      throw new Error(payload.message || payload.error || 'license request failed');
    }
    return payload;
  }

  async function refreshBackendStatus() {
    try {
      backendStatus = await fetchJson('/license/status');
    } catch (_err) {
      backendStatus = null;
    }
    return renderPanel();
  }

  function hasFeature(feature) {
    var list = currentStatus().features || [];
    return list.indexOf('*') >= 0 || list.indexOf(feature) >= 0;
  }

  function featureRows(status) {
    var list = status.features || [];
    if (list.indexOf('*') >= 0) {
      list = Object.keys(features);
    }
    return list.map(function(key) {
      var meta = features[key] || {};
      return '<span class="license-feature">' + escapeHtml(meta.label || key) + '</span>';
    }).join('');
  }

  function upgradeBullets(upgrade) {
    return (upgrade.bullets || []).slice(0, 4).map(function(item) {
      return '<li>' + escapeHtml(item) + '</li>';
    }).join('');
  }

  function planStrip(upgrade) {
    return (upgrade.plans || []).slice(0, 3).map(function(plan) {
      return '<span><strong>' + escapeHtml(plan.label) + '</strong>' + escapeHtml(plan.price) + '</span>';
    }).join('');
  }

  function stateClass(state) {
    if (state === 'internal' || state === 'pro_active') return 'is-active';
    if (state === 'pro_pending') return 'is-pending';
    if (state === 'expired' || state === 'invalid') return 'is-blocked';
    return 'is-free';
  }

  function applyDocumentState(status) {
    if (!global.document || !global.document.documentElement) return;
    global.document.documentElement.dataset.licenseState = status.state;
    global.document.documentElement.dataset.licensePlan = status.plan;
  }

  function renderPanel() {
    var panel = byId('license-panel');
    if (!panel) return null;
    var status = currentStatus();
    applyDocumentState(status);

    var badge = byId('license-state-badge');
    var plan = byId('license-plan-label');
    var detail = byId('license-status-detail');
    var commercialCopy = byId('license-commercial-copy');
    var upgradeList = byId('license-upgrade-list');
    var planStripEl = byId('license-plan-strip');
    var featureListEl = byId('license-feature-list');
    var note = byId('license-upgrade-note');
    var upgrade = product.upgrade || {};

    if (badge) {
      badge.className = 'license-badge ' + stateClass(status.state);
      badge.textContent = status.state === 'internal' ? 'Internal' : (status.state === 'free' ? 'Free' : status.state);
    }
    if (plan) plan.textContent = status.label;
    if (detail) detail.textContent = status.message;
    if (commercialCopy) {
      commercialCopy.innerHTML = '<strong>' + escapeHtml(upgrade.headline || 'SQX Edge Pro') + '</strong><span>' + escapeHtml(upgrade.primaryMessage || '') + '</span>';
    }
    if (upgradeList) {
      upgradeList.innerHTML = '<ul>' + upgradeBullets(upgrade) + '</ul>';
    }
    if (planStripEl) {
      planStripEl.innerHTML = planStrip(upgrade);
    }
    if (featureListEl) featureListEl.innerHTML = featureRows(status);
    if (note) {
      note.textContent = status.active
        ? 'Capacidades habilitadas para esta licencia.'
        : (upgrade.primaryMessage || 'Esta funcion forma parte de SQX Edge Pro.');
    }
    return status;
  }

  async function importLicenseText(text) {
    var payload = JSON.parse(text);
    if (!payload || typeof payload !== 'object') {
      throw new Error('license payload must be an object');
    }
    var result = await fetchJson('/license/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    backendStatus = result.status || result.import_status || null;
    setJson(storageKey, payload);
    return renderPanel();
  }

  async function clearLicense() {
    remove(storageKey);
    try {
      var result = await fetchJson('/license/clear', { method: 'POST' });
      backendStatus = result.status || null;
    } catch (_err) {
      backendStatus = null;
    }
    return renderPanel();
  }

  function bindPanel() {
    var input = byId('license-key-input');
    var importBtn = byId('license-import-btn');
    var clearBtn = byId('license-clear-btn');
    var feedback = byId('license-feedback');

    if (importBtn && input) {
      importBtn.addEventListener('click', async function() {
        try {
          await importLicenseText(input.value || '{}');
          if (feedback) feedback.textContent = 'Licencia firmada cargada y verificada.';
        } catch (err) {
          if (feedback) feedback.textContent = 'No se pudo leer la licencia: ' + err.message;
        }
      });
    }
    if (clearBtn) {
      clearBtn.addEventListener('click', async function() {
        await clearLicense();
        if (feedback) feedback.textContent = 'Licencia local eliminada.';
      });
    }
  }

  function init() {
    renderPanel();
    bindPanel();
    refreshBackendStatus();
  }

  SQX.license = SQX.license || {
    apiBase: apiBase,
    bindPanel: bindPanel,
    clearLicense: clearLicense,
    currentStatus: currentStatus,
    fetchJson: fetchJson,
    hasFeature: hasFeature,
    importLicenseText: importLicenseText,
    renderPanel: renderPanel,
    refreshBackendStatus: refreshBackendStatus,
    storageKey: storageKey,
    init: init
  };

  if (SQX.registerModule) {
    SQX.registerModule('license', SQX.license);
  }
})(window);

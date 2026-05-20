// ============================================================
// SQX Dashboard - runtime configuration helpers
// ============================================================

(function initSqxAppConfig(global) {
  const CONFIG_VERSION = 'remote-api-same-origin-v2';
  const manifest = global.SQX_MANIFEST || {};
  const ui = manifest.ui || {};
  const product = manifest.product || {};
  const filters = ui.filters || {};
  const storageKeys = ui.storageKeys || {};

  function esc(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, ch => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    }[ch]));
  }

  function dataAttrName(datasetKey) {
    return 'data-' + datasetKey.replace(/[A-Z]/g, ch => '-' + ch.toLowerCase());
  }

  function optionHtml(option) {
    const value = typeof option === 'object' ? option.value : option;
    const label = typeof option === 'object' ? option.label : option;
    const selected = option && option.selected ? ' selected' : '';
    return '<option value="' + esc(value) + '"' + selected + '>' + esc(label) + '</option>';
  }

  function fillSelect(id, options, selectedValue) {
    const select = document.getElementById(id);
    if (!select || !Array.isArray(options)) return;
    select.innerHTML = options.map(option => {
      const value = typeof option === 'object' ? option.value : option;
      const selected = selectedValue != null
        ? String(value) === String(selectedValue)
        : Boolean(option && option.selected);
      const normalized = typeof option === 'object' ? { ...option, selected } : { value, label: value, selected };
      return optionHtml(normalized);
    }).join('');
  }

  function navCollapsedKey() {
    return storageKeys.navCollapsed || 'sqx_nav_collapsed_v1';
  }

  function readNavCollapsed() {
    try {
      return localStorage.getItem(navCollapsedKey()) === '1';
    } catch (e) {
      return false;
    }
  }

  function writeNavCollapsed(collapsed) {
    try {
      localStorage.setItem(navCollapsedKey(), collapsed ? '1' : '0');
    } catch (e) {}
  }

  function applyNavCollapsed(collapsed) {
    if (document.body) document.body.classList.toggle('nav-collapsed', collapsed);
    const toggle = document.getElementById('tabs-collapse-toggle');
    if (!toggle) return;
    toggle.setAttribute('aria-pressed', collapsed ? 'true' : 'false');
    toggle.setAttribute('aria-label', collapsed ? 'Expandir navegación' : 'Ocultar navegación');
    toggle.setAttribute('title', collapsed ? 'Expandir navegación' : 'Ocultar navegación');
    const label = toggle.querySelector('.tabs-toggle-label');
    if (label) label.textContent = collapsed ? 'Expandir' : 'Ocultar';
  }

  function fallbackTabIcon(tab) {
    const label = String((tab && tab.label) || '').trim();
    return label ? label.slice(0, 1).toUpperCase() : '';
  }

  function renderButtonGroup(id, label, datasetKey, options) {
    const group = document.getElementById(id);
    if (!group || !Array.isArray(options)) return;
    const attr = dataAttrName(datasetKey);
    group.innerHTML = '<label>' + esc(label) + ':</label>' + options.map(option => {
      const cls = option.active ? 'filter-btn active' : 'filter-btn';
      const title = option.title ? ' title="' + esc(option.title) + '"' : '';
      return '<button class="' + cls + '" ' + attr + '="' + esc(option.value) + '"' + title + '>' + esc(option.label) + '</button>';
    }).join('');
  }

  function renderTabs() {
    const tabs = document.getElementById('main-tabs') || document.querySelector('.tabs');
    if (!tabs || !Array.isArray(ui.tabs)) return;
    const toggleHtml =
      '<button class="tabs-toggle" id="tabs-collapse-toggle" type="button" aria-pressed="false">' +
        '<span class="tabs-toggle-icon" aria-hidden="true"></span>' +
        '<span class="tabs-toggle-label">Ocultar</span>' +
      '</button>';
    const primaryTabs = ui.tabs.filter(tab => !tab.hiddenInPrimary);
    tabs.innerHTML = toggleHtml + primaryTabs.map(tab => {
      const cls = tab.active ? 'tab active' : 'tab';
      const icon = tab.icon || fallbackTabIcon(tab);
      return '<div class="' + cls + '" data-tab="' + esc(tab.id) + '" title="' + esc(tab.label) + '">' +
        '<span class="tab-icon" aria-hidden="true">' + esc(icon) + '</span>' +
        '<span class="tab-label">' + esc(tab.label) + '</span>' +
      '</div>';
    }).join('');
    const toggle = document.getElementById('tabs-collapse-toggle');
    if (toggle) {
      toggle.addEventListener('click', function() {
        const collapsed = !document.body.classList.contains('nav-collapsed');
        writeNavCollapsed(collapsed);
        applyNavCollapsed(collapsed);
      });
    }
    applyNavCollapsed(readNavCollapsed());
  }

  function syncHeader() {
    if (!ui.header) return;
    const h1 = document.querySelector('.header h1');
    const subtitle = document.querySelector('.header .subtitle');
    if (h1 && ui.header.titleHtml) h1.innerHTML = ui.header.titleHtml;
    if (subtitle && ui.header.subtitle) subtitle.textContent = ui.header.subtitle;
  }

  function renderConfiguredControls() {
    const blockCatalog = ui.blockSettingsCatalog || {};
    const capa1Options = Array.isArray(blockCatalog.capa1Options)
      ? blockCatalog.capa1Options.map(o => ({ value: o.value, label: o.label || o.value }))
      : Object.keys(ui.bsToPriorityCat || {}).map(v => ({ value: v, label: v }));
    const capa2Options = [{ value: '', label: 'Auto recomendado por timeframe' }].concat(
      Array.isArray(blockCatalog.capa2Options)
        ? blockCatalog.capa2Options.map(o => ({ value: o.value, label: (o.label || o.value) + (o.timeframes && o.timeframes.length ? ' · ' + o.timeframes.join('/') : '') }))
        : []
    );
    const defaultCapa1Block = (ui.capa1Resolver && ui.capa1Resolver.families && ui.capa1Resolver.families.tendencia && ui.capa1Resolver.families.tendencia.default)
      || (capa1Options[0] && capa1Options[0].value)
      || 'BS_Tendencia_v6';
    renderButtonGroup('asset-type-filter', 'Tipo', 'filterType', filters.assetTypes);
    renderButtonGroup('asset-sqx-filter', 'Config SQX', 'filterSqx', filters.sqxConfigs);
    renderButtonGroup('category-dir-filter', 'Direccion', 'filterDir', filters.directions);
    renderButtonGroup('priority-min-filter', 'Min composite', 'priorityMin', filters.priorityMin);
    renderButtonGroup('priority-type-filter', 'Tipo', 'priorityType', filters.assetTypes);

    fillSelect('asset-sort', filters.assetSort);
    fillSelect('cat-filter-rating', filters.ratings);
    fillSelect('cat-filter-sub', filters.subtypes);
    fillSelect('cat-filter-tf', filters.timeframes);
    fillSelect('priority-cat-filter', filters.categories);
    fillSelect('strat-filter-status', filters.strategyStatus);
    fillSelect('sf-tf', (filters.timeframes || []).filter(o => o.value !== 'all'), 'H1');
    fillSelect('sf-bs', capa1Options, defaultCapa1Block);
    fillSelect('psm-bs', capa1Options, defaultCapa1Block);
    fillSelect('csv-meta-bs', capa1Options, defaultCapa1Block);
    fillSelect('tm-c2-block', capa1Options.concat([{ value: 'BS_Custom', label: 'BS_Custom' }]), defaultCapa1Block);
    fillSelect('pg-capa2-bs', capa2Options, '');
    fillSelect('sf-dir', filters.directionsFull, 'L');
    fillSelect('sf-tier', [
      { value: '1', label: 'TIER 1 - pasa todos los tests' },
      { value: '1.5', label: 'TIER 1.5 - pasa con asterisco' },
      { value: '2', label: 'TIER 2 - solida con numeros optimistas' },
      { value: 'tentativa', label: 'Tentativa - pendiente tests' },
    ], 'tentativa');
    fillSelect('sf-status', (filters.strategyStatus || []).filter(o => o.value !== 'all'), 'CANDIDATA');

    const maxMining = Math.max(0, ...((manifest.plan && manifest.plan.minings) || []).map(m => Number(m.num) || 0));
    const sfMining = document.getElementById('sf-mining');
    if (sfMining && maxMining) sfMining.max = String(maxMining);
  }

  function defaultApiBase() {
    const configured = global.SQX_APP_CONFIG && global.SQX_APP_CONFIG.apiBase;
    if (configured) return configured.replace(/\/$/, '');
    const api = ui.api || {};
    const basePath = api.basePath || '/api';
    const remoteBasePath = api.remoteBasePath || '/dashboard/api';
    const loc = global.location || {};
    const protocol = loc.protocol === 'https:' ? 'https:' : 'http:';
    const host = loc.hostname || api.defaultHost || '127.0.0.1';
    const isLocalHost = host === 'localhost' || host === '::1' || host.indexOf('127.') === 0;
    const isRemoteHost = protocol === 'https:' && host && !isLocalHost;
    const currentOrigin = loc.origin || (protocol + '//' + host);
    function safeRemoteApiBase(value) {
      const normalized = String(value || '').replace(/\/$/, '');
      if (!normalized) return '';
      if (!isRemoteHost) return normalized;
      let parsedProtocol = '';
      let parsedHost = '';
      let parsedOrigin = '';
      let parsedPathname = '';
      if (typeof URL !== 'undefined') {
        const parsed = new URL(normalized, currentOrigin);
        parsedProtocol = parsed.protocol || '';
        parsedHost = parsed.hostname || '';
        parsedOrigin = parsed.origin || '';
        parsedPathname = parsed.pathname || '';
      }
      const isLocal = parsedHost
        ? parsedHost === 'localhost' || parsedHost === '::1' || parsedHost.indexOf('127.') === 0
        : /^https?:\/\/(?:localhost|127\.|\[?::1\]?)/i.test(normalized);
      const isInsecure = parsedProtocol ? parsedProtocol !== 'https:' : /^http:\/\//i.test(normalized);
      const sameOrigin = parsedOrigin
        ? parsedOrigin === currentOrigin
        : (
            normalized.indexOf(currentOrigin + remoteBasePath) === 0
            || normalized.indexOf(remoteBasePath) === 0
            || normalized.indexOf(currentOrigin + basePath) === 0
            || normalized.indexOf(basePath) === 0
          );
      const remotePathOk = parsedPathname
        ? parsedPathname.indexOf(remoteBasePath) === 0
        : (normalized.indexOf(currentOrigin + remoteBasePath) === 0 || normalized.indexOf(remoteBasePath) === 0);
      return !isLocal && !isInsecure && sameOrigin && remotePathOk ? normalized : '';
    }
    const meta = document.querySelector('meta[name="sqx-api-base"]');
    if (meta && meta.content) {
      const safeMeta = safeRemoteApiBase(meta.content);
      if (safeMeta) return safeMeta;
    }
    try {
      const stored = localStorage.getItem(storageKeys.apiBase || 'sqx_pg_api_base_v1');
      if (stored) {
        const safeStored = safeRemoteApiBase(stored);
        if (safeStored) return safeStored;
        try {
          localStorage.removeItem(storageKeys.apiBase || 'sqx_pg_api_base_v1');
        } catch (cleanupErr) {}
      }
    } catch (e) {}
    if (isRemoteHost) {
      return currentOrigin + remoteBasePath;
    }
    const port = api.defaultPort || 5050;
    return protocol + '//' + host + ':' + port + basePath;
  }

  function configValue(path, fallback) {
    const parts = path.split('.');
    let cur = ui;
    for (const part of parts) {
      if (!cur || typeof cur !== 'object' || !(part in cur)) return fallback;
      cur = cur[part];
    }
    return cur;
  }

  function diagnostics() {
    const loc = global.location || {};
    const base = defaultApiBase();
    let apiOrigin = '';
    try {
      apiOrigin = (new URL(base, loc.origin || 'http://127.0.0.1')).origin;
    } catch (_err) {}
    return {
      configVersion: CONFIG_VERSION,
      apiBase: base,
      apiOrigin,
      pageOrigin: loc.origin || '',
      host: loc.host || loc.hostname || '',
      protocol: loc.protocol || '',
    };
  }

  global.SQX_CONFIG = {
    version: CONFIG_VERSION,
    manifest,
    ui,
    product,
    storageKeys,
    apiBase: defaultApiBase,
    diagnostics,
    value: configValue,
    fillSelect,
  };

  syncHeader();
  renderTabs();
  renderConfiguredControls();
})(typeof window !== 'undefined' ? window : globalThis);

// ============================================================
// SQX Dashboard - runtime configuration helpers
// ============================================================

(function initSqxAppConfig(global) {
  const manifest = global.SQX_MANIFEST || {};
  const ui = manifest.ui || {};
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
    tabs.innerHTML = ui.tabs.map(tab => {
      const cls = tab.active ? 'tab active' : 'tab';
      return '<div class="' + cls + '" data-tab="' + esc(tab.id) + '">' + esc(tab.label) + '</div>';
    }).join('');
  }

  function syncHeader() {
    if (!ui.header) return;
    const h1 = document.querySelector('.header h1');
    const subtitle = document.querySelector('.header .subtitle');
    if (h1 && ui.header.titleHtml) h1.innerHTML = ui.header.titleHtml;
    if (subtitle && ui.header.subtitle) subtitle.textContent = ui.header.subtitle;
  }

  function renderConfiguredControls() {
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
    fillSelect('sf-bs', Object.keys(ui.bsToPriorityCat || {}).map(v => ({ value: v, label: v })), 'BS_Tendencia');
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
    try {
      const stored = localStorage.getItem(storageKeys.apiBase || 'sqx_pg_api_base_v1');
      if (stored) return stored.replace(/\/$/, '');
    } catch (e) {}
    const meta = document.querySelector('meta[name="sqx-api-base"]');
    if (meta && meta.content) return meta.content.replace(/\/$/, '');
    const api = ui.api || {};
    const protocol = location.protocol === 'https:' ? 'https:' : 'http:';
    const host = location.hostname || api.defaultHost || '127.0.0.1';
    const port = api.defaultPort || 5050;
    const basePath = api.basePath || '/api';
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

  global.SQX_CONFIG = {
    manifest,
    ui,
    storageKeys,
    apiBase: defaultApiBase,
    value: configValue,
    fillSelect,
  };

  syncHeader();
  renderTabs();
  renderConfiguredControls();
})(typeof window !== 'undefined' ? window : globalThis);

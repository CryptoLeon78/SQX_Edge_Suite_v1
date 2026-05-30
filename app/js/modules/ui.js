(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  function byId(id) {
    return global.document.getElementById(id);
  }

  function all(selector, root) {
    return Array.from((root || global.document).querySelectorAll(selector));
  }

  function setDisplay(node, value) {
    if (node) node.style.display = value;
  }

  function show(node, display) {
    setDisplay(node, display || '');
  }

  function hide(node) {
    setDisplay(node, 'none');
  }

  function setText(node, value) {
    if (node) node.textContent = value == null ? '' : String(value);
  }

  function bindClick(id, handler) {
    var node = typeof id === 'string' ? byId(id) : id;
    if (!node || typeof handler !== 'function') return false;
    node.addEventListener('click', handler);
    return true;
  }

  function bindChange(id, handler) {
    var node = typeof id === 'string' ? byId(id) : id;
    if (!node || typeof handler !== 'function') return false;
    node.addEventListener('change', handler);
    return true;
  }

  function bindInput(id, handler) {
    var node = typeof id === 'string' ? byId(id) : id;
    if (!node || typeof handler !== 'function') return false;
    node.addEventListener('input', handler);
    return true;
  }

  function activateTabById(id, doc) {
    var target = doc || global.document;
    var tab = target.querySelector('.tab[data-tab="' + id + '"]');
    var panel = target.getElementById('tab-' + id);
    if (!panel) return false;
    all('.tab', target).forEach(function(node) { node.classList.remove('active'); });
    if (tab) tab.classList.add('active');
    all('.tab-content', target).forEach(function(content) { content.style.display = 'none'; });
    panel.style.display = 'block';
    if (typeof updateGlobalStepNavigation === 'function') {
      setTimeout(updateGlobalStepNavigation, 0);
    }
    return true;
  }

  function bindTabs(selector, handler, doc) {
    var target = doc || global.document;
    all(selector || '.tab', target).forEach(function(tab) {
      tab.addEventListener('click', function() {
        var id = tab.dataset.tab;
        if (handler) handler(id, tab);
        else activateTabById(id, target);
      });
    });
  }

  function bindHomeTabButtons(selector, handler, doc) {
    var target = doc || global.document;
    all(selector || '[data-home-tab]', target).forEach(function(button) {
      button.addEventListener('click', function() {
        if (handler) handler(button.dataset.homeTab, button);
        else activateTabById(button.dataset.homeTab, target);
      });
    });
  }

  function bindButtonGroup(selector, datasetKey, varSetter, callback, doc) {
    var target = doc || global.document;
    all(selector, target).forEach(function(button) {
      button.addEventListener('click', function() {
        all(selector, target).forEach(function(node) { node.classList.remove('active'); });
        button.classList.add('active');
        if (varSetter) varSetter(button.dataset[datasetKey]);
        if (callback) callback();
      });
    });
  }

  function activeTabId() {
    var active = global.document.querySelector('.tab.active[data-tab], .tab-btn.active[data-tab]');
    if (active) return active.dataset.tab;
    var visiblePanel = all('.tab-content', global.document).find(function(panel) {
      return panel.style.display !== 'none';
    });
    return visiblePanel && visiblePanel.id ? visiblePanel.id.replace(/^tab-/, '') : null;
  }

  function edgeExperienceMode() {
    try {
      var state = SQX.edgeFactory && SQX.edgeFactory.getState ? SQX.edgeFactory.getState() : null;
      return state && state.experienceMode === 'advanced' ? 'advanced' : 'basic';
    } catch (_err) {
      return 'basic';
    }
  }

  function tabLabel(tabId) {
    var tabs = global.SQX_MANIFEST && global.SQX_MANIFEST.ui && global.SQX_MANIFEST.ui.tabs || [];
    var found = tabs.find(function(tab) { return tab.id === tabId; });
    return found ? found.label : tabId;
  }

  function basicNextTab(current, state) {
    state = state || {};
    if (current === 'workflow') return 'activos';
    if (current === 'activos') return 'projectgen';
    if (current === 'projectgen') return state.c2Template ? 'cvc' : 'templatemaker';
    if (current === 'templatemaker') return 'projectgen';
    if (current === 'cvc') return 'inicio';
    if (current === 'inicio') return 'workflow';
    return 'workflow';
  }

  function basicPrevTab(current, state) {
    state = state || {};
    if (current === 'workflow') return 'inicio';
    if (current === 'activos') return 'workflow';
    if (current === 'projectgen') return state.c2Template ? 'templatemaker' : 'activos';
    if (current === 'templatemaker') return 'projectgen';
    if (current === 'cvc') return 'projectgen';
    if (current === 'inicio') return 'cvc';
    return 'workflow';
  }

  function advancedOrder() {
    var tabs = global.SQX_MANIFEST && global.SQX_MANIFEST.ui && global.SQX_MANIFEST.ui.tabs || [];
    return tabs.map(function(tab) { return tab.id; }).filter(Boolean);
  }

  function resolveStepNavTarget(direction) {
    var current = activeTabId() || 'workflow';
    var mode = edgeExperienceMode();
    var state = SQX.edgeFactory && SQX.edgeFactory.getState ? SQX.edgeFactory.getState() : {};
    if (mode === 'advanced') {
      var order = advancedOrder();
      if (!order.length) return 'workflow';
      var index = Math.max(0, order.indexOf(current));
      var nextIndex = direction === 'prev'
        ? (index - 1 + order.length) % order.length
        : (index + 1) % order.length;
      return order[nextIndex] || 'workflow';
    }
    return direction === 'prev' ? basicPrevTab(current, state) : basicNextTab(current, state);
  }

  function updateGlobalStepNavigation() {
    var current = activeTabId() || 'workflow';
    var previous = resolveStepNavTarget('prev');
    var next = resolveStepNavTarget('next');
    all('[data-global-step-nav="prev"]').forEach(function(button) {
      button.dataset.targetTab = previous;
      var label = button.querySelector('[data-step-nav-label]');
      if (label) label.textContent = tabLabel(previous);
    });
    all('[data-global-step-nav="next"]').forEach(function(button) {
      button.dataset.targetTab = next;
      var label = button.querySelector('[data-step-nav-label]');
      if (label) label.textContent = tabLabel(next);
    });
    all('[data-global-step-current]').forEach(function(node) {
      node.textContent = tabLabel(current);
    });
  }

  function bindGlobalStepNavigation() {
    all('[data-global-step-nav]').forEach(function(button) {
      if (button.__globalStepNavBound) return;
      button.__globalStepNavBound = true;
      button.addEventListener('click', function() {
        var target = button.dataset.targetTab || resolveStepNavTarget(button.dataset.globalStepNav);
        activateTabById(target, global.document);
      });
    });
    if (!bindGlobalStepNavigation.__stateBound && typeof global.addEventListener === 'function') {
      bindGlobalStepNavigation.__stateBound = true;
      global.addEventListener('sqx:edge-factory-state', updateGlobalStepNavigation);
    }
    updateGlobalStepNavigation();
  }

  SQX.ui = SQX.ui || {
    activateTabById: activateTabById,
    activeTabId: activeTabId,
    all: all,
    bindButtonGroup: bindButtonGroup,
    bindGlobalStepNavigation: bindGlobalStepNavigation,
    bindChange: bindChange,
    bindClick: bindClick,
    bindHomeTabButtons: bindHomeTabButtons,
    bindInput: bindInput,
    bindTabs: bindTabs,
    byId: byId,
    hide: hide,
    setDisplay: setDisplay,
    setText: setText,
    show: show,
    updateGlobalStepNavigation: updateGlobalStepNavigation
  };

  bindGlobalStepNavigation();

  if (SQX.registerModule) {
    SQX.registerModule('ui', SQX.ui);
  }
})(window);

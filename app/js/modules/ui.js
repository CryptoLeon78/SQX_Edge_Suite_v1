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
    if (!tab || !panel) return false;
    all('.tab', target).forEach(function(node) { node.classList.remove('active'); });
    tab.classList.add('active');
    all('.tab-content', target).forEach(function(content) { content.style.display = 'none'; });
    panel.style.display = 'block';
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
    return active ? active.dataset.tab : null;
  }

  SQX.ui = SQX.ui || {
    activateTabById: activateTabById,
    activeTabId: activeTabId,
    all: all,
    bindButtonGroup: bindButtonGroup,
    bindChange: bindChange,
    bindClick: bindClick,
    bindHomeTabButtons: bindHomeTabButtons,
    bindInput: bindInput,
    bindTabs: bindTabs,
    byId: byId,
    hide: hide,
    setDisplay: setDisplay,
    setText: setText,
    show: show
  };

  if (SQX.registerModule) {
    SQX.registerModule('ui', SQX.ui);
  }
})(window);

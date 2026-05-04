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

  function activeTabId() {
    var active = global.document.querySelector('.tab-btn.active[data-tab]');
    return active ? active.dataset.tab : null;
  }

  SQX.ui = SQX.ui || {
    activeTabId: activeTabId,
    all: all,
    bindClick: bindClick,
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

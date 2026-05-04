(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  SQX.version = SQX.version || 'modularization-phase-1';
  SQX.modules = SQX.modules || {};
  SQX.readyQueue = SQX.readyQueue || [];

  function registerModule(name, api) {
    if (!name) return null;
    SQX.modules[name] = api || {};
    return SQX.modules[name];
  }

  function getModule(name) {
    return SQX.modules[name] || null;
  }

  function onReady(fn) {
    if (typeof fn !== 'function') return;
    if (SQX.booted) {
      fn(SQX);
      return;
    }
    SQX.readyQueue.push(fn);
  }

  function flushReady() {
    var queue = SQX.readyQueue.splice(0);
    queue.forEach(function(fn) {
      fn(SQX);
    });
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function toArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function uniq(values) {
    return Array.from(new Set(toArray(values)));
  }

  function safeJsonParse(raw, fallback) {
    try {
      return JSON.parse(raw);
    } catch (_err) {
      return fallback;
    }
  }

  SQX.registerModule = SQX.registerModule || registerModule;
  SQX.getModule = SQX.getModule || getModule;
  SQX.onReady = SQX.onReady || onReady;
  SQX.flushReady = SQX.flushReady || flushReady;
  SQX.utils = SQX.utils || {
    escapeHtml: escapeHtml,
    escapeAttr: escapeHtml,
    safeJsonParse: safeJsonParse,
    toArray: toArray,
    uniq: uniq
  };

  SQX.registerModule('core', {
    utils: SQX.utils,
    onReady: SQX.onReady,
    flushReady: SQX.flushReady
  });
})(window);

(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var WORKER_VERSION = 'tm-perf2-worker-v1';
  var worker = null;
  var workerFailed = false;
  var nextJobId = 1;
  var pending = {};

  function canUseWorker() {
    if (workerFailed || !global.Worker) return false;
    if (global.location && global.location.protocol === 'file:') return false;
    return true;
  }

  function workerScriptUrl() {
    return 'js/workers/template-maker-worker.js';
  }

  function ensureWorker() {
    if (!canUseWorker()) return null;
    if (worker) return worker;
    try {
      worker = new global.Worker(workerScriptUrl());
      worker.onmessage = handleMessage;
      worker.onerror = function(error) {
        workerFailed = true;
        rejectAll(error && error.message ? error.message : 'template_maker_worker_failed');
        try { worker.terminate(); } catch (_err) {}
        worker = null;
      };
      return worker;
    } catch (_err) {
      workerFailed = true;
      worker = null;
      return null;
    }
  }

  function rejectAll(message) {
    Object.keys(pending).forEach(function(id) {
      pending[id].reject(new Error(message || 'template_maker_worker_failed'));
      delete pending[id];
    });
  }

  function handleMessage(event) {
    var message = event && event.data || {};
    var job = pending[message.jobId];
    if (!job) return;
    if (message.type === 'progress') {
      if (typeof job.onProgress === 'function') {
        job.onProgress(Object.assign({ workerVersion: WORKER_VERSION }, message.progress || {}));
      }
      return;
    }
    delete pending[message.jobId];
    if (message.type === 'result') {
      job.resolve(message.result);
      return;
    }
    job.reject(new Error(message.error || 'template_maker_worker_error'));
  }

  function run(action, payload, onProgress) {
    var activeWorker = ensureWorker();
    if (!activeWorker) return Promise.reject(new Error('template_maker_worker_unavailable'));
    var jobId = 'tmw-' + nextJobId++;
    return new Promise(function(resolve, reject) {
      pending[jobId] = { resolve: resolve, reject: reject, onProgress: onProgress };
      try {
        activeWorker.postMessage({
          version: WORKER_VERSION,
          jobId: jobId,
          action: action,
          payload: payload || {}
        });
      } catch (err) {
        delete pending[jobId];
        reject(err);
      }
    });
  }

  function parseCSV(text, options, onProgress) {
    return run('parseCSV', { text: String(text || ''), options: options || {} }, onProgress);
  }

  function parseSQX(file, options, onProgress) {
    return run('parseSQX', { file: file, options: options || {} }, onProgress);
  }

  function buildDiversityClusters(strategies, settings, onProgress) {
    return run('buildDiversityClusters', {
      strategies: strategies || [],
      settings: settings || {}
    }, onProgress);
  }

  function reset() {
    rejectAll('template_maker_worker_reset');
    if (worker) {
      try { worker.terminate(); } catch (_err) {}
    }
    worker = null;
    workerFailed = false;
  }

  SQX.templateMakerWorker = SQX.templateMakerWorker || {
    version: WORKER_VERSION,
    canUseWorker: canUseWorker,
    parseCSV: parseCSV,
    parseSQX: parseSQX,
    buildDiversityClusters: buildDiversityClusters,
    reset: reset
  };
  if (SQX.registerModule) SQX.registerModule('template-maker-worker-client', SQX.templateMakerWorker);
})(window);

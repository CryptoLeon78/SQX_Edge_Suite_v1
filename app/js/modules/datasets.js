(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  function readJsonScript(id, fallback) {
    try {
      var node = global.document && global.document.getElementById(id);
      var text = node && node.textContent && node.textContent.trim();
      if (!text || text.startsWith('__')) return fallback;
      return JSON.parse(text);
    } catch (err) {
      return fallback;
    }
  }

  function historical() {
    return global.SQX_HISTORICAL_DATA || readJsonScript('historical-data', {});
  }

  function scores() {
    return global.SQX_SCORES_DATA || readJsonScript('scores-data', {});
  }

  function manifest() {
    return global.SQX_MANIFEST || {};
  }

  SQX.datasets = SQX.datasets || {
    historical: historical,
    manifest: manifest,
    readJsonScript: readJsonScript,
    scores: scores
  };

  if (SQX.registerModule) {
    SQX.registerModule('datasets', SQX.datasets);
  }
})(window);

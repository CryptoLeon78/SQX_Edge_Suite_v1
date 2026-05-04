(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var utils = SQX.utils || {};
  var emptyMetric = '—';

  function ratingLabel(rating) {
    if (rating === '++') return { text: 'Estrella', cls: 'rating-pp' };
    if (rating === '+') return { text: 'Bueno', cls: 'rating-p' };
    if (rating === '~') return { text: 'Precauc.', cls: 'rating-t' };
    return { text: 'No recom.', cls: 'rating-m' };
  }

  function heatmapClass(rating) {
    if (rating === '++') return 'hm-pp';
    if (rating === '+') return 'hm-p';
    if (rating === '~') return 'hm-t';
    if (rating === '-') return 'hm-m';
    return '';
  }

  function assetDirectionClass(direction) {
    return direction === 'L' ? 'dir-long' : direction === 'S' ? 'dir-short' : 'dir-both';
  }

  function strategyDirectionClass(direction) {
    if (direction === 'L') return 'dir-L';
    if (direction === 'S') return 'dir-S';
    return 'dir-LS';
  }

  function tierClass(tier) {
    if (tier === '1') return 'tier-1';
    if (tier === '1.5') return 'tier-15';
    if (tier === '2') return 'tier-2';
    return 'tier-tentativa';
  }

  function tierLabel(tier) {
    if (tier === '1') return 'TIER 1';
    if (tier === '1.5') return 'TIER 1.5';
    if (tier === '2') return 'TIER 2';
    return 'TENTATIVA';
  }

  function metricClass(label, value) {
    if (value == null) return '';
    if (label === 'PF') return value >= 1.5 ? 'pos' : value >= 1.2 ? 'warn' : 'neg';
    if (label === 'Ret/DD') return value >= 5 ? 'pos' : value >= 3 ? 'warn' : 'neg';
    if (label === 'R Exp') return value >= 0.30 ? 'pos' : value >= 0.15 ? 'warn' : 'neg';
    if (label === 'DD %') return value < 2 ? 'pos' : value < 5 ? 'warn' : 'neg';
    if (label === 'Sharpe') return value >= 1.3 ? 'pos' : value >= 1.0 ? 'warn' : 'neg';
    if (label === 'SQN') return value >= 1.6 ? 'pos' : value >= 1.0 ? 'warn' : 'neg';
    if (label === 'Stagn d') return value < 180 ? 'pos' : value < 365 ? 'warn' : 'neg';
    return '';
  }

  function formatNumber(value, decimals) {
    var dec = decimals == null ? 2 : decimals;
    var parsed = value;
    if (parsed == null || parsed === '') return emptyMetric;
    if (typeof parsed !== 'number') parsed = parseFloat(parsed);
    if (isNaN(parsed)) return emptyMetric;
    return parsed.toLocaleString('en-US', {
      minimumFractionDigits: dec,
      maximumFractionDigits: dec
    });
  }

  function formatInteger(value) {
    if (value == null || value === '') return emptyMetric;
    return parseInt(value, 10).toLocaleString('en-US');
  }

  function escapeHtml(value) {
    if (utils.escapeHtml) return utils.escapeHtml(value);
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  SQX.formatters = SQX.formatters || {
    assetDirectionClass: assetDirectionClass,
    escapeHtml: escapeHtml,
    formatInteger: formatInteger,
    formatNumber: formatNumber,
    heatmapClass: heatmapClass,
    metricClass: metricClass,
    ratingLabel: ratingLabel,
    strategyDirectionClass: strategyDirectionClass,
    tierClass: tierClass,
    tierLabel: tierLabel
  };

  if (SQX.registerModule) {
    SQX.registerModule('formatters', SQX.formatters);
  }
})(window);

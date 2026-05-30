(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var DEFAULT_SQX_SELECTION_POLICY = {
    forexSelectableConfigs: ['A', 'B', 'C', 'D'],
    shortBlockedTypes: ['index', 'oro'],
    scoreRole: 'hypothesis_prior_not_final_selector'
  };

  function sqxSelectionPolicy() {
    var manifestPolicy = global.SQX_MANIFEST && global.SQX_MANIFEST.ui && global.SQX_MANIFEST.ui.sqxSelectionPolicy;
    var policy = Object.assign({}, DEFAULT_SQX_SELECTION_POLICY, manifestPolicy || {});
    policy.forexSelectableConfigs = Array.isArray(policy.forexSelectableConfigs) ? policy.forexSelectableConfigs : DEFAULT_SQX_SELECTION_POLICY.forexSelectableConfigs;
    policy.shortBlockedTypes = Array.isArray(policy.shortBlockedTypes) ? policy.shortBlockedTypes : DEFAULT_SQX_SELECTION_POLICY.shortBlockedTypes;
    return policy;
  }

  function assetType(asset) {
    return String(asset && asset.type || '').trim().toLowerCase();
  }

  function isShortBlockedAsset(asset) {
    var blocked = sqxSelectionPolicy().shortBlockedTypes.map(function(item) { return String(item).toLowerCase(); });
    return blocked.indexOf(assetType(asset)) !== -1;
  }

  function calcScore(asset, dirFilter, ratingOrder) {
    var total = 0;
    var count = 0;
    var cats = asset && asset.cats ? asset.cats : {};
    Object.keys(cats).forEach(function(_key) {
      var val = cats[_key];
      if (dirFilter === 'L' && val.dir === 'S') return;
      if (dirFilter === 'S' && val.dir === 'L') return;
      total += ratingOrder[val.rating] != null ? ratingOrder[val.rating] : 0;
      count += 1;
    });
    return { raw: total, count: count, norm: count ? Math.round((total / (count * 3)) * 100) : 0 };
  }

  function getSqxConfig(asset) {
    var cats = asset && asset.cats ? asset.cats : {};
    var keys = Object.keys(cats);
    var hasL = false;
    var hasS = false;
    var hasLS = false;
    var hasPair = false;

    keys.forEach(function(key) {
      var val = cats[key];
      if (val.dir === 'L/S') hasLS = true;
      else if (val.dir === 'L') hasL = true;
      else if (val.dir === 'S') hasS = true;
      if (key.endsWith('_S')) hasPair = true;
    });

    if (hasLS && !hasPair && !hasL && !hasS) {
      return { code:'A', label:'Both + Entry Sym', desc:'Both (Long & Short) con Entry Symmetry ON. Hipótesis L/S espejada.' };
    }
    if (hasPair) {
      return { code:'B', label:'Both sin Symmetry', desc:'Both (Long & Short) con Symmetry OFF. SQX optimiza L y S por separado.' };
    }
    if (hasL && !hasS) {
      return { code:'C', label:'Only Long', desc:'Only Long. Solo se buscan estrategias en lado Long.' };
    }
    if (hasS && !hasL) {
      return { code:'D', label:'Only Short', desc:'Only Short. Solo se buscan estrategias en lado Short.' };
    }
    return { code:'B', label:'Both sin Symmetry', desc:'Both (Long & Short) con Symmetry OFF. SQX optimiza L y S por separado.' };
  }

  function assetCanUseSqxConfig(asset, code) {
    var cfg = String(code || 'all').toUpperCase();
    if (cfg === 'ALL') return true;
    if (assetType(asset) === 'forex') {
      return sqxSelectionPolicy().forexSelectableConfigs.indexOf(cfg) !== -1;
    }
    if (cfg === 'D' && isShortBlockedAsset(asset)) return false;
    if (cfg === 'A' || cfg === 'B') return getSqxConfig(asset).code === cfg;
    if (cfg === 'C') return Object.values(asset && asset.cats || {}).some(function(value) { return value.dir === 'L' || value.dir === 'L/S'; });
    if (cfg === 'D') return Object.values(asset && asset.cats || {}).some(function(value) { return value.dir === 'S' || value.dir === 'L/S'; });
    return true;
  }

  function resolveSqxDirection(selectedConfig, entryDirection) {
    var cfg = String(selectedConfig || '').toUpperCase();
    if (cfg === 'C') return 'L';
    if (cfg === 'D') return 'S';
    if (cfg === 'A' || cfg === 'B') return 'L/S';
    return entryDirection || 'L/S';
  }

  function scoreFromScores(scores, assetId, catKey) {
    var base = catKey.endsWith('_S') ? catKey.slice(0, -2) : catKey;
    var assetScores = scores[assetId];
    if (!assetScores || !assetScores[base]) return null;
    var entry = assetScores[base];
    return {
      base: base,
      objective: entry.objective,
      composite: entry.composite_score,
      metrics: assetScores.metrics && assetScores.metrics[base] || {}
    };
  }

  function applyObjectiveRatings(assets, scores, getScore) {
    if (!scores || !Object.keys(scores).length) return;
    assets.forEach(function(asset) {
      Object.keys(asset.cats).forEach(function(catKey) {
        var entry = asset.cats[catKey];
        var score = getScore(asset.id, catKey);
        if (score && score.objective) {
          entry.rating = score.objective;
          entry._composite = score.composite;
          entry._metrics = score.metrics;
        }
      });
    });
  }

  function tfMatch(tf, filter) {
    return filter === 'all' || String(tf || '').includes(filter);
  }

  function assetMatchesSqxFilter(asset, code) {
    if (code === 'all') return true;
    return assetCanUseSqxConfig(asset, code);
  }

  function sortRows(rows, col, dir, ratingOrder) {
    if (!col || !dir) return rows;
    return rows.slice().sort(function(a, b) {
      var va;
      var vb;
      if (col === 'asset') { va = a.asset && a.asset.id || ''; vb = b.asset && b.asset.id || ''; }
      else if (col === 'sub') { va = a.asset && a.asset.sub || ''; vb = b.asset && b.asset.sub || ''; }
      else if (col === 'dir') { va = a.dir || ''; vb = b.dir || ''; }
      else if (col === 'tf') { va = a.tf || ''; vb = b.tf || ''; }
      else if (col === 'rating') {
        va = ratingOrder[a.rating] != null ? ratingOrder[a.rating] : -1;
        vb = ratingOrder[b.rating] != null ? ratingOrder[b.rating] : -1;
      } else {
        va = '';
        vb = '';
      }
      if (typeof va === 'number') return dir === 'asc' ? va - vb : vb - va;
      return dir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
    });
  }

  SQX.domain = SQX.domain || {
    applyObjectiveRatings: applyObjectiveRatings,
    assetMatchesSqxFilter: assetMatchesSqxFilter,
    assetCanUseSqxConfig: assetCanUseSqxConfig,
    calcScore: calcScore,
    getSqxConfig: getSqxConfig,
    isShortBlockedAsset: isShortBlockedAsset,
    resolveSqxDirection: resolveSqxDirection,
    sqxSelectionPolicy: sqxSelectionPolicy,
    scoreFromScores: scoreFromScores,
    sortRows: sortRows,
    tfMatch: tfMatch
  };

  if (SQX.registerModule) {
    SQX.registerModule('domain', SQX.domain);
  }
})(window);

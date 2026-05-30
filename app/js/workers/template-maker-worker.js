(function(global) {
  'use strict';

  var WORKER_VERSION = 'tm-perf2-worker-v1';

  try {
    importScripts('../../vendor/jszip.min.js');
  } catch (_err) {
    try { importScripts('../vendor/jszip.min.js'); } catch (_err2) {}
  }

  function post(jobId, type, payload) {
    global.postMessage(Object.assign({ jobId: jobId, type: type }, payload || {}));
  }

  function progress(jobId, stage, payload) {
    post(jobId, 'progress', {
      progress: Object.assign({
        stage: stage,
        workerVersion: WORKER_VERSION
      }, payload || {})
    });
  }

  function cleanHeaderName(value) {
    return String(value || '').replace(/^\uFEFF/, '').trim();
  }

  function parseCsvLine(line, separator) {
    var out = [];
    var current = '';
    var inQuote = false;
    var csvSeparator = separator || (line.indexOf(';') >= 0 ? ';' : ',');
    for (var i = 0; i < line.length; i += 1) {
      var ch = line[i];
      if (ch === '"') {
        if (inQuote && line[i + 1] === '"') {
          current += '"';
          i += 1;
        } else {
          inQuote = !inQuote;
        }
        continue;
      }
      if (ch === csvSeparator && !inQuote) {
        out.push(current.trim());
        current = '';
        continue;
      }
      current += ch;
    }
    out.push(current.trim());
    return out;
  }

  function detectSeparator(line) {
    var candidates = [';', ',', '\t'];
    return candidates.map(function(separator) {
      return {
        separator: separator,
        count: parseCsvLine(line, separator).length
      };
    }).sort(function(a, b) {
      return b.count - a.count;
    })[0].separator;
  }

  function parseCSV(jobId, payload) {
    progress(jobId, 'parsing_csv', { fileName: payload.options && payload.options.fileName || '' });
    var csvText = String(payload.text || '').replace(/^\uFEFF/, '');
    var lines = csvText.split(/\r?\n/).filter(function(line) { return line.trim(); });
    if (lines.length < 2) {
      return { rows: [], headers: [], separator: '', lineCount: lines.length };
    }
    var separator = detectSeparator(lines[0]);
    var headers = parseCsvLine(lines[0], separator).map(cleanHeaderName);
    var rows = [];
    lines.slice(1).forEach(function(line, index) {
      var values = parseCsvLine(line, separator);
      if (values.length < 2) return;
      var row = {};
      headers.forEach(function(header, valueIndex) {
        row[header] = values[valueIndex] || '';
      });
      rows.push(row);
      if ((index + 1) % 100 === 0) {
        progress(jobId, 'parsing_csv', {
          fileName: payload.options && payload.options.fileName || '',
          current: index + 1,
          total: lines.length - 1
        });
      }
    });
    return { rows: rows, headers: headers, separator: separator, lineCount: lines.length };
  }

  function bytesToHex(buffer) {
    return Array.prototype.map.call(new Uint8Array(buffer), function(byte) {
      return byte.toString(16).padStart(2, '0');
    }).join('');
  }

  function fallbackHash(value) {
    var text = typeof value === 'string' ? value : JSON.stringify(value || '');
    var h1 = 2166136261;
    var h2 = 16777619;
    for (var i = 0; i < text.length; i += 1) {
      h1 ^= text.charCodeAt(i);
      h1 = Math.imul(h1, 16777619);
      h2 ^= text.charCodeAt(i) << (i % 8);
      h2 = Math.imul(h2, 1099511627);
    }
    return ('00000000' + (h1 >>> 0).toString(16)).slice(-8) + ('00000000' + (h2 >>> 0).toString(16)).slice(-8);
  }

  function computeHash(file) {
    return file.arrayBuffer().then(function(buffer) {
      if (global.crypto && global.crypto.subtle && global.crypto.subtle.digest) {
        return global.crypto.subtle.digest('SHA-256', buffer).then(bytesToHex);
      }
      return fallbackHash(Array.prototype.join.call(new Uint8Array(buffer), ','));
    });
  }

  function parseSQX(jobId, payload) {
    var file = payload.file;
    if (!file) throw new Error('missing_sqx_file');
    if (!global.JSZip) throw new Error('JSZip no esta cargado en Worker');
    var fileName = file.name || 'strategy.sqx';
    progress(jobId, 'hashing', { fileName: fileName });
    return computeHash(file).then(function(hash) {
      progress(jobId, 'unzipping', { fileName: fileName });
      return global.JSZip.loadAsync(file).then(function(zip) {
        var strategyFile = zip.file('strategy_Portfolio.xml');
        var settingsFile = zip.file('settings.xml');
        progress(jobId, 'parsing_sqx', { fileName: fileName });
        return Promise.all([
          strategyFile ? strategyFile.async('string') : Promise.resolve(''),
          settingsFile ? settingsFile.async('string') : Promise.resolve('')
        ]).then(function(parts) {
          return {
            fileName: fileName,
            hash: hash,
            strategyXml: parts[0] || '',
            settingsXml: parts[1] || '',
            strategyXmlPresent: !!parts[0],
            settingsXmlPresent: !!parts[1]
          };
        });
      });
    });
  }

  function uniqueSorted(values) {
    var out = {};
    (values || []).forEach(function(value) {
      var normalized = String(value || '').trim();
      if (normalized) out[normalized] = true;
    });
    return Object.keys(out).sort();
  }

  function jaccard(a, b) {
    var left = uniqueSorted(a);
    var right = uniqueSorted(b);
    if (!left.length && !right.length) return 0;
    var rightMap = {};
    right.forEach(function(value) { rightMap[value] = true; });
    var intersection = left.filter(function(value) { return rightMap[value]; }).length;
    var unionMap = {};
    left.concat(right).forEach(function(value) { unionMap[value] = true; });
    return intersection / Object.keys(unionMap).length;
  }

  function roundSimilarity(value) {
    return Math.max(0, Math.min(1, Math.round((Number(value) || 0) * 1000) / 1000));
  }

  function getNumeric(value) {
    if (value === '' || value === 'N/A' || value === 'null' || value === undefined || value === null) return null;
    var normalized = String(value).replace(/%/g, '').replace(/\s/g, '').trim();
    if (normalized.indexOf(',') >= 0 && normalized.indexOf('.') >= 0) {
      normalized = normalized.lastIndexOf(',') > normalized.lastIndexOf('.')
        ? normalized.replace(/\./g, '').replace(',', '.')
        : normalized.replace(/,/g, '');
    } else if (normalized.indexOf(',') >= 0) {
      normalized = /,\d{1,4}$/.test(normalized) ? normalized.replace(',', '.') : normalized.replace(/,/g, '');
    }
    var parsed = parseFloat(normalized);
    return Number.isNaN(parsed) ? null : parsed;
  }

  function metricValue(strategy, metric) {
    if (!strategy) return '';
    if (strategy.metrics && strategy.metrics[metric] !== undefined) return strategy.metrics[metric];
    return strategy[metric];
  }

  function logicFeatures(strategy) {
    var features = strategy && strategy.logic && strategy.logic.features || {};
    return {
      indicators: features.indicators || [],
      operators: features.operators || [],
      params: features.params || [],
      rules: features.rules || []
    };
  }

  function computeStructuralSimilarity(aFeatures, bFeatures) {
    var indicators = jaccard(aFeatures.indicators, bFeatures.indicators);
    var operators = jaccard(aFeatures.operators, bFeatures.operators);
    var params = jaccard(aFeatures.params, bFeatures.params);
    var rules = jaccard(aFeatures.rules, bFeatures.rules);
    return roundSimilarity((indicators * 0.55) + (operators * 0.20) + (params * 0.20) + (rules * 0.05));
  }

  function computeMetricSimilarity(a, b, settings) {
    var sims = [];
    (settings.metrics || ['Ret/DD Ratio', 'Profit factor', 'Max DD %', '# of trades', 'Winning Percent', 'Stability']).forEach(function(metric) {
      var av = getNumeric(metricValue(a, metric));
      var bv = getNumeric(metricValue(b, metric));
      if (av === null || bv === null) return;
      var denom = Math.max(Math.abs(av), Math.abs(bv), 1);
      sims.push(Math.max(0, 1 - (Math.abs(av - bv) / denom)));
    });
    if (!sims.length) return 0;
    return roundSimilarity(sims.reduce(function(sum, value) { return sum + value; }, 0) / sims.length);
  }

  function normalizedDiversityWeights(settings) {
    var structural = Number(settings.structuralWeight);
    var metric = Number(settings.metricWeight);
    var total = (structural || 0) + (metric || 0);
    if (!total) return { structural: 0.65, metric: 0.35 };
    return { structural: structural / total, metric: metric / total };
  }

  function comparableDiversityGroup(strategy) {
    return [
      String(strategy && strategy.Symbol || '').toLowerCase().trim(),
      String(strategy && strategy.TimeFrame || '').toLowerCase().trim()
    ].join('|');
  }

  function computeTemplateSimilarity(a, b, settings) {
    if (comparableDiversityGroup(a) !== comparableDiversityGroup(b)) {
      return { comparable: false, structuralSimilarity: 0, metricSimilarity: 0, hybridSimilarity: 0, clusterMatch: false, reason: 'asset/timeframe distinto' };
    }
    var structural = computeStructuralSimilarity(logicFeatures(a), logicFeatures(b));
    var metric = computeMetricSimilarity(a, b, settings);
    var weights = normalizedDiversityWeights(settings);
    var hybrid = roundSimilarity((structural * weights.structural) + (metric * weights.metric));
    var clusterMatch = structural >= settings.structuralThreshold
      || (structural >= settings.bridgeStructuralThreshold && metric >= settings.metricThreshold)
      || hybrid >= settings.hybridThreshold;
    return {
      comparable: true,
      structuralSimilarity: structural,
      metricSimilarity: metric,
      hybridSimilarity: hybrid,
      clusterMatch: clusterMatch,
      reason: clusterMatch ? 'similitud hibrida' : 'diverso'
    };
  }

  function diversityStatus(strategy, status, clusterId, similarity, reason, canGenerate, relation) {
    return {
      strategyId: strategy && strategy._id,
      strategyName: strategy && strategy['Strategy Name'] || '',
      status: status,
      clusterId: clusterId,
      similarity: roundSimilarity(similarity || 0),
      structuralSimilarity: roundSimilarity(relation && relation.structuralSimilarity || 0),
      metricSimilarity: roundSimilarity(relation && relation.metricSimilarity || 0),
      reason: reason || '',
      canGenerateC2: !!canGenerate,
      version: 'template-maker-diversity-v1'
    };
  }

  function chooseDiversityWinner(strategies) {
    return (strategies || []).slice().sort(function(a, b) {
      var scoreDiff = (Number(b.__tmPerfScorePct) || 0) - (Number(a.__tmPerfScorePct) || 0);
      if (scoreDiff) return scoreDiff;
      var pfDiff = (getNumeric(metricValue(b, 'Profit factor')) || 0) - (getNumeric(metricValue(a, 'Profit factor')) || 0);
      if (pfDiff) return pfDiff;
      var cagrDiff = (getNumeric(metricValue(b, 'Ret/DD Ratio') || metricValue(b, 'CAGR/Max DD %')) || 0) - (getNumeric(metricValue(a, 'Ret/DD Ratio') || metricValue(a, 'CAGR/Max DD %')) || 0);
      if (cagrDiff) return cagrDiff;
      var ddDiff = (getNumeric(metricValue(a, 'Max DD %')) || 0) - (getNumeric(metricValue(b, 'Max DD %')) || 0);
      if (ddDiff) return ddDiff;
      var tradesDiff = (getNumeric(metricValue(b, '# of trades')) || 0) - (getNumeric(metricValue(a, '# of trades')) || 0);
      if (tradesDiff) return tradesDiff;
      return (Number(a.__tmPerfOrder) || 0) - (Number(b.__tmPerfOrder) || 0);
    })[0];
  }

  function similarityBetweenIndexes(a, b, pairEvidence) {
    return pairEvidence[Math.min(a, b) + ':' + Math.max(a, b)] || { hybridSimilarity: 0, structuralSimilarity: 0, metricSimilarity: 0 };
  }

  function buildGroupClusters(group, groupKey, report, settings) {
    var parent = group.map(function(_item, index) { return index; });
    var pairEvidence = {};
    function find(index) {
      while (parent[index] !== index) {
        parent[index] = parent[parent[index]];
        index = parent[index];
      }
      return index;
    }
    function union(a, b) {
      var rootA = find(a);
      var rootB = find(b);
      if (rootA !== rootB) parent[rootB] = rootA;
    }
    for (var i = 0; i < group.length; i += 1) {
      for (var j = i + 1; j < group.length; j += 1) {
        var similarity = computeTemplateSimilarity(group[i], group[j], settings);
        pairEvidence[i + ':' + j] = similarity;
        if (similarity.clusterMatch) union(i, j);
      }
    }
    var buckets = {};
    group.forEach(function(strategy, index) {
      var root = find(index);
      buckets[root] = buckets[root] || [];
      buckets[root].push({ strategy: strategy, index: index });
    });
    Object.keys(buckets).forEach(function(root) {
      var members = buckets[root];
      var winner = chooseDiversityWinner(members.map(function(item) { return item.strategy; }));
      var clusterId = 'CL' + String(report.clusters.length + 1).padStart(2, '0');
      report.clusters.push({
        id: clusterId,
        group: groupKey,
        size: members.length,
        winnerId: winner && winner._id,
        members: members.map(function(item) { return item.strategy._id; })
      });
      members.forEach(function(item) {
        var strategy = item.strategy;
        var winnerItem = members.find(function(candidate) { return String(candidate.strategy._id) === String(winner._id); });
        var relation = winner && String(strategy._id) !== String(winner._id)
          ? similarityBetweenIndexes(item.index, winnerItem.index, pairEvidence)
          : { hybridSimilarity: 0, structuralSimilarity: 0, metricSimilarity: 0 };
        var status = members.length === 1 ? 'Diverso' : String(strategy._id) === String(winner._id) ? 'Ganador cluster' : 'Similar descartada';
        var canGenerate = status === 'Diverso' || status === 'Ganador cluster';
        var reason = status === 'Similar descartada'
          ? 'similar a ' + (winner['Strategy Name'] || winner._id)
          : members.length === 1 ? 'sin similares detectados' : 'mejor score del cluster';
        var payload = diversityStatus(strategy, status, clusterId, relation.hybridSimilarity || 0, reason, canGenerate, relation);
        report.byId[String(strategy._id)] = payload;
        report.statuses.push(payload);
        if (canGenerate) report.winners += 1;
        else report.discarded += 1;
      });
    });
  }

  function buildDiversityClusters(jobId, payload) {
    var settings = Object.assign({
      structuralThreshold: 0.70,
      metricThreshold: 0.88,
      hybridThreshold: 0.78,
      structuralWeight: 0.65,
      metricWeight: 0.35,
      bridgeStructuralThreshold: 0.45
    }, payload.settings || {});
    var list = (payload.strategies || []).slice();
    var report = {
      version: 'template-maker-diversity-v1',
      settings: settings,
      total: list.length,
      candidates: 0,
      clusters: [],
      winners: 0,
      discarded: 0,
      byId: {},
      statuses: []
    };
    var groups = {};
    list.forEach(function(strategy, index) {
      strategy.__tmPerfOrder = index;
      if (!strategy.__tmPerfContractValid) {
        report.byId[String(strategy._id)] = diversityStatus(strategy, 'No evaluable', '-', 0, 'contrato CSV pendiente', false);
        report.statuses.push(report.byId[String(strategy._id)]);
        return;
      }
      if (!strategy.__tmPerfHasSQX) {
        report.byId[String(strategy._id)] = diversityStatus(strategy, 'No evaluable', '-', 0, 'falta .sqx', false);
        report.statuses.push(report.byId[String(strategy._id)]);
        return;
      }
      if (strategy.__tmPerfScoreClassification !== 'PASSED') {
        report.byId[String(strategy._id)] = diversityStatus(strategy, 'No evaluable', '-', 0, 'scoring no PASSED', false);
        report.statuses.push(report.byId[String(strategy._id)]);
        return;
      }
      report.candidates += 1;
      var key = comparableDiversityGroup(strategy);
      groups[key] = groups[key] || [];
      groups[key].push(strategy);
    });
    Object.keys(groups).forEach(function(groupKey, index) {
      progress(jobId, 'diversity', { current: index + 1, total: Object.keys(groups).length });
      buildGroupClusters(groups[groupKey], groupKey, report, settings);
    });
    return report;
  }

  global.onmessage = function(event) {
    var message = event && event.data || {};
    var jobId = message.jobId;
    Promise.resolve().then(function() {
      if (message.action === 'parseCSV') return parseCSV(jobId, message.payload || {});
      if (message.action === 'parseSQX') return parseSQX(jobId, message.payload || {});
      if (message.action === 'buildDiversityClusters') return buildDiversityClusters(jobId, message.payload || {});
      throw new Error('unknown_template_maker_worker_action');
    }).then(function(result) {
      progress(jobId, 'done', {});
      post(jobId, 'result', { result: result });
    }).catch(function(err) {
      post(jobId, 'error', { error: err && err.message ? err.message : String(err) });
    });
  };
})(self);

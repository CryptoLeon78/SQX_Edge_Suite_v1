(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  function strategyKey(strategy) {
    return [strategy.id, strategy.mining, strategy.template, strategy.asset, strategy.tf]
      .map(function(value) { return String(value == null ? '' : value); })
      .join('|');
  }

  function getAllStrategies(baseStrategies, userStrategies, deletedKeys) {
    var deleted = new Set(deletedKeys || []);
    return (baseStrategies || []).filter(function(strategy) {
      return !deleted.has(strategyKey(strategy));
    }).concat(userStrategies || []);
  }

  function filterStrategies(strategies, filters) {
    var f = filters || {};
    return (strategies || []).filter(function(strategy) {
      if (f.mining !== 'all' && String(strategy.mining) !== f.mining) return false;
      if (f.template !== 'all' && strategy.template !== f.template) return false;
      if (f.tier !== 'all' && strategy.tier !== f.tier) return false;
      if (f.status !== 'all' && strategy.status !== f.status) return false;
      return true;
    });
  }

  function summarize(strategies) {
    var all = strategies || [];
    return {
      total: all.length,
      tier1: all.filter(function(strategy) { return strategy.tier === '1'; }).length,
      tier15: all.filter(function(strategy) { return strategy.tier === '1.5'; }).length,
      tier2: all.filter(function(strategy) { return strategy.tier === '2'; }).length,
      tentative: all.filter(function(strategy) { return strategy.tier === 'tentativa'; }).length,
      deployed: all.filter(function(strategy) { return strategy.status === 'DEPLOYED'; }).length,
      totalProfit: all.reduce(function(acc, strategy) {
        return acc + ((strategy.metrics && strategy.metrics.net_profit) || 0);
      }, 0)
    };
  }

  function autoDetectTemplate(indicators, rules) {
    if (!indicators) return null;
    var ind = indicators.toUpperCase();
    for (var i = 0; i < (rules || []).length; i++) {
      var rule = rules[i];
      if ((rule.keywords || []).some(function(keyword) { return ind.includes(keyword); })) {
        return rule.template;
      }
    }
    return null;
  }

  function parseCSV(text, sep) {
    var rows = [];
    var cur = '';
    var inQuotes = false;
    var row = [];
    for (var i = 0; i < text.length; i++) {
      var c = text[i];
      var n = text[i + 1];
      if (inQuotes) {
        if (c === '"' && n === '"') { cur += '"'; i++; }
        else if (c === '"') { inQuotes = false; }
        else { cur += c; }
      } else {
        if (c === '"') { inQuotes = true; }
        else if (c === sep) { row.push(cur); cur = ''; }
        else if (c === '\n') { row.push(cur); rows.push(row); row = []; cur = ''; }
        else if (c !== '\r') { cur += c; }
      }
    }
    if (cur !== '' || row.length) { row.push(cur); rows.push(row); }
    return rows.filter(function(csvRow) {
      return csvRow.length > 1 || (csvRow.length === 1 && csvRow[0].trim() !== '');
    });
  }

  function detectSeparator(text) {
    var sample = text.split('\n')[0] || '';
    var semis = (sample.match(/;/g) || []).length;
    var commas = (sample.match(/,/g) || []).length;
    return semis > commas ? ';' : ',';
  }

  function filterCsvRows(rows, options) {
    var opts = options || {};
    var q = String(opts.filter || '').toLowerCase().trim();
    var filtered = (rows || []).map(function(row, index) {
      return Object.assign({ _idx: index }, row);
    });

    if (q) {
      filtered = filtered.filter(function(row) {
        return String(row['Strategy Name'] || '').toLowerCase().includes(q)
          || String(row['Entry indicators'] || '').toLowerCase().includes(q);
      });
    }

    if (opts.sortCol) {
      var col = opts.sortCol;
      var dir = opts.sortDir === 'asc' ? 1 : -1;
      filtered.sort(function(a, b) {
        var va = parseFloat(a[col]);
        var vb = parseFloat(b[col]);
        var na = isNaN(va);
        var nb = isNaN(vb);
        if (na && nb) return String(a[col] || '').localeCompare(String(b[col] || '')) * dir;
        if (na) return 1;
        if (nb) return -1;
        return (va - vb) * dir;
      });
    }

    return filtered;
  }

  function rowToStrategy(row, meta, options) {
    var opts = options || {};
    var columnMap = opts.columnMap || {};
    var sn = String(row['Strategy Name'] || '').trim();
    var id = sn.replace(/^Strategy\s+/i, '') || sn;
    var indicators = row['Entry indicators'] || '';
    var template = meta.template || 'UNKNOWN';
    if (meta.autoTemplate) {
      var auto = autoDetectTemplate(indicators, opts.templateRules || []);
      if (auto) template = auto;
    }

    var numFields = ['m.net_profit','m.fitness','m.net_profit_pct','m.dd','m.dd_pct','m.open_dd_pct','m.max_intraday_dd','m.ret_dd','m.annual_pct_return','m.sharpe','m.pf','m.win_pct','m.trades_per_month','m.exit_quality','m.equity_angle','m.exposure','m.recovery_factor','m.z_score','m.sqn','m.r_exp','m.std_dev','m.payout_ratio','m.avg_bars_in_trade'];
    var intFields = ['m.trades','m.wins','m.losses','m.max_consec_wins','m.max_consec_losses','m.longest_trade_days','m.complexity','m.stagnation_days'];
    var metrics = {};
    Object.entries(columnMap).forEach(function(entry) {
      var col = entry[0];
      var target = entry[1];
      if (!target.startsWith('m.')) return;
      var key = target.slice(2);
      var raw = row[col];
      if (raw == null || raw === '') return;
      if (intFields.includes(target)) {
        var intValue = parseInt(raw, 10);
        if (!isNaN(intValue)) metrics[key] = intValue;
      } else if (numFields.includes(target)) {
        var numValue = parseFloat(raw);
        if (!isNaN(numValue)) metrics[key] = numValue;
      } else {
        metrics[key] = raw;
      }
    });

    var asset = String(row['Symbol'] || '').replace(/_darwinex$/i, '').replace(/_[a-z]+$/i, '').toUpperCase() || 'XAUUSD';
    var tf = String(row['TimeFrame'] || '').toUpperCase() || 'H1';
    var noteParts = [];
    if (meta.phase) noteParts.push('Fase: ' + meta.phase);
    if (meta.notes) noteParts.push(meta.notes);

    return {
      id: id,
      name: indicators ? indicators.split(',').slice(0, 3).join(' + ') : 'Sin nombre',
      mining: meta.mining,
      asset: asset,
      tf: tf,
      blocksetting: meta.bs,
      template: template,
      direction: meta.dir,
      indicators: indicators,
      exits: '— (no en CSV)',
      metrics: metrics,
      tier: meta.tier,
      status: meta.status,
      tests_passed: [],
      tests_failed: [],
      notes: noteParts.join(' · '),
      added: new Date().toISOString().slice(0, 10),
      _imported: true,
      _import_id: 'imp_' + Date.now() + '_' + id
    };
  }

  SQX.strategies = SQX.strategies || {
    autoDetectTemplate: autoDetectTemplate,
    detectSeparator: detectSeparator,
    filterCsvRows: filterCsvRows,
    filterStrategies: filterStrategies,
    getAllStrategies: getAllStrategies,
    parseCSV: parseCSV,
    rowToStrategy: rowToStrategy,
    strategyKey: strategyKey,
    summarize: summarize
  };

  if (SQX.registerModule) {
    SQX.registerModule('strategies', SQX.strategies);
  }
})(window);

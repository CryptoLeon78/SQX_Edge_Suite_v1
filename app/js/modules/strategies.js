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

  function summaryHtml(summary, formatInteger) {
    var fmtInt = formatInteger || function(value) { return String(value); };
    return '<div class="strat-summary-card"><div class="ss-count">' + summary.total + '</div><div class="ss-label">Total</div></div>' +
      '<div class="strat-summary-card t1"><div class="ss-count">' + summary.tier1 + '</div><div class="ss-label">TIER 1</div></div>' +
      '<div class="strat-summary-card t15"><div class="ss-count">' + summary.tier15 + '</div><div class="ss-label">TIER 1.5</div></div>' +
      '<div class="strat-summary-card t2"><div class="ss-count">' + summary.tier2 + '</div><div class="ss-label">TIER 2</div></div>' +
      '<div class="strat-summary-card tt"><div class="ss-count">' + summary.tentative + '</div><div class="ss-label">Tentativas</div></div>' +
      '<div class="strat-summary-card"><div class="ss-count">' + summary.deployed + '</div><div class="ss-label">Deployed</div></div>' +
      '<div class="strat-summary-card"><div class="ss-count" style="font-size:18px;">$' + fmtInt(Math.round(summary.totalProfit)) + '</div><div class="ss-label">Σ Net Profit (BT)</div></div>';
  }

  function filterOptionsHtml(strategies, field, labelFn) {
    var values = Array.from(new Set((strategies || []).map(function(strategy) { return strategy[field]; })));
    values.sort(function(a, b) {
      if (typeof a === 'number' && typeof b === 'number') return a - b;
      return String(a).localeCompare(String(b));
    });
    return '<option value="all">Todos</option>' + values.map(function(value) {
      var label = labelFn ? labelFn(value) : value;
      return '<option value="' + value + '">' + label + '</option>';
    }).join('');
  }

  function strategyCard(strategy, options) {
    var opts = options || {};
    var m = strategy.metrics || {};
    var tierClass = opts.tierClass || function() { return ''; };
    var tierLabel = opts.tierLabel || function(tier) { return tier; };
    var dirClass = opts.dirClass || function() { return ''; };
    var metricClass = opts.metricClass || function() { return ''; };
    var fmtNum = opts.formatNumber || function(value) { return value == null ? '—' : String(value); };
    var fmtInt = opts.formatInteger || function(value) { return value == null ? '—' : String(value); };
    var escapeHtml = opts.escapeHtml || function(value) { return String(value == null ? '' : value); };
    var strategyKeyFn = opts.strategyKey || strategyKey;
    var dirCls = dirClass(strategy.direction);
    var dirTxt = strategy.direction === 'L' ? 'LONG' : strategy.direction === 'S' ? 'SHORT' : 'L+S';
    var key = strategyKeyFn(strategy);
    var sourceLabel = strategy._imported ? 'importada' : 'base';

    var metricsRow = [
      ['Net Profit', m.net_profit != null ? '$' + fmtNum(m.net_profit, 0) : '—', m.net_profit > 0 ? 'pos' : ''],
      ['PF', fmtNum(m.pf), metricClass('PF', m.pf)],
      ['Ret/DD', fmtNum(m.ret_dd), metricClass('Ret/DD', m.ret_dd)],
      ['DD %', m.dd_pct != null ? fmtNum(m.dd_pct) + '%' : '—', metricClass('DD %', m.dd_pct)],
      ['Sharpe', fmtNum(m.sharpe), metricClass('Sharpe', m.sharpe)],
      ['R Exp', fmtNum(m.r_exp), metricClass('R Exp', m.r_exp)],
      ['# Trades', fmtInt(m.trades), ''],
      ['Win %', m.win_pct != null ? fmtNum(m.win_pct) + '%' : '—', ''],
      [
        m.sqn != null ? 'SQN' : (m.stagnation_days != null ? 'Stagn d' : 'WFM $'),
        m.sqn != null ? fmtNum(m.sqn) : (m.stagnation_days != null ? fmtInt(m.stagnation_days) : (m.wfm_profit != null ? '$' + fmtInt(m.wfm_profit) : '—')),
        m.sqn != null ? metricClass('SQN', m.sqn) : (m.stagnation_days != null ? metricClass('Stagn d', m.stagnation_days) : '')
      ]
    ];

    var metricsHtml = metricsRow.map(function(row) {
      return '<div class="sc-metric"><div class="m-label">' + row[0] + '</div><div class="m-val ' + row[2] + '">' + row[1] + '</div></div>';
    }).join('');
    var testsOk = (strategy.tests_passed || []).map(function(test) { return '<span class="sc-test-ok">' + test + '</span>'; }).join('');
    var testsKo = (strategy.tests_failed || []).map(function(test) { return '<span class="sc-test-ko">' + test + '</span>'; }).join('');
    var importedCls = strategy._imported ? ' user-imported' : '';

    return '<div class="strat-card ' + tierClass(strategy.tier) + importedCls + '">' +
      '<div class="sc-head">' +
        '<span class="sc-id">' + strategy.id + '</span>' +
        '<span class="sc-name">' + strategy.name + '</span>' +
        '<span class="strat-tier-badge ' + tierClass(strategy.tier) + '">' + tierLabel(strategy.tier) + '</span>' +
        '<span class="strat-status-badge ' + strategy.status + '">' + strategy.status.replace('_', ' ') + '</span>' +
      '</div>' +
      '<div class="sc-meta">' +
        '<span class="sc-meta-pill">M' + strategy.mining + '</span>' +
        '<span class="sc-meta-pill">' + strategy.asset + '</span>' +
        '<span class="sc-meta-pill">' + strategy.tf + '</span>' +
        '<span class="sc-meta-pill">' + strategy.blocksetting + '</span>' +
        '<span class="sc-meta-pill template">' + strategy.template + '</span>' +
        '<span class="sc-meta-pill ' + dirCls + '">' + dirTxt + '</span>' +
      '</div>' +
      '<div class="sc-indicators"><strong>Señal</strong>' + strategy.indicators + '</div>' +
      '<div class="sc-indicators"><strong>Exits</strong>' + strategy.exits + '</div>' +
      '<div class="sc-metrics">' + metricsHtml + '</div>' +
      (testsOk || testsKo ? '<div class="sc-tests">' + testsOk + testsKo + '</div>' : '') +
      (strategy.notes ? '<div class="sc-notes">' + strategy.notes + '</div>' : '') +
      '<div class="sc-footer"><span class="sc-date">' + (strategy.added || '—') + '</span>' +
        '<button class="strat-remove-btn" data-strategy-key="' + escapeHtml(key) + '" title="Eliminar estrategia ' + sourceLabel + '">Eliminar</button>' +
      '</div>' +
    '</div>';
  }

  function sortForDisplay(strategies) {
    var tierRank = { '1': 0, '1.5': 1, '2': 2, 'tentativa': 3 };
    return (strategies || []).slice().sort(function(a, b) {
      var ta = tierRank[a.tier] == null ? 99 : tierRank[a.tier];
      var tb = tierRank[b.tier] == null ? 99 : tierRank[b.tier];
      if (ta !== tb) return ta - tb;
      return ((b.metrics && b.metrics.net_profit) || 0) - ((a.metrics && a.metrics.net_profit) || 0);
    });
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

  function csvMetricClass(col, value) {
    var num = parseFloat(value);
    if (isNaN(num)) return '';
    if (col === 'Profit factor') return num >= 1.5 ? 'pos' : num >= 1.2 ? 'warn' : 'neg';
    if (col === 'Sharpe Ratio') return num >= 1.3 ? 'pos' : num >= 1.0 ? 'warn' : 'neg';
    if (col === 'Ret/DD Ratio') return num >= 5 ? 'pos' : num >= 3 ? 'warn' : 'neg';
    if (col === 'Max DD %') return num < 2 ? 'pos' : num < 5 ? 'warn' : 'neg';
    if (col === 'R Expectancy') return num >= 0.30 ? 'pos' : num >= 0.15 ? 'warn' : 'neg';
    if (col === 'SQN Score') return num >= 1.6 ? 'pos' : num >= 1.0 ? 'warn' : 'neg';
    if (col === 'Stagnation') return num < 180 ? 'pos' : num < 365 ? 'warn' : 'neg';
    if (col === 'Net profit') return num > 0 ? 'pos' : 'neg';
    return '';
  }

  function csvPreviewTable(rows, state, options) {
    var opts = options || {};
    var selected = state.selected || new Set();
    var cols = opts.columns || ['Strategy Name','Net profit','Profit factor','Sharpe Ratio','Ret/DD Ratio','Max DD %','# of trades','Winning Percent','SQN Score','R Expectancy','Stagnation','Entry indicators'];
    var autoTemplate = opts.autoDetectTemplate || function() { return null; };
    var head = '<thead><tr><th style="width:30px;"><input type="checkbox" id="csv-th-check"></th>' +
      cols.map(function(col) {
        var arrow = state.sortCol === col ? (state.sortDir === 'asc' ? ' ▲' : ' ▼') : '';
        return '<th class="sortable" data-col="' + col + '">' + col + arrow + '</th>';
      }).join('') + '<th>TPL</th></tr></thead>';

    var body = '<tbody>' + (rows || []).map(function(row) {
      var idx = row._idx;
      var checked = selected.has(idx) ? 'checked' : '';
      var tpl = autoTemplate(row['Entry indicators']) || '—';
      var cells = cols.map(function(col) {
        var value = row[col] || '';
        if (col === 'Strategy Name') return '<td class="cv-id">' + value + '</td>';
        if (col === 'Entry indicators') return '<td style="font-size:11px; color:var(--text2); max-width:280px; white-space:normal;">' + value + '</td>';
        return '<td class="cv-num ' + csvMetricClass(col, value) + '">' + value + '</td>';
      }).join('');
      return '<tr><td><input type="checkbox" class="cv-row-check" data-idx="' + idx + '" ' + checked + '></td>' + cells + '<td><span class="cv-tpl">' + tpl + '</span></td></tr>';
    }).join('') + '</tbody>';

    return head + body;
  }

  function csvConfirmHtml(meta, selected, rows) {
    var sel = selected.size;
    var sample = Array.from(selected).slice(0, 5).map(function(index) {
      return 'Strategy ' + String((rows[index] && rows[index]['Strategy Name']) || '').replace(/^Strategy /, '');
    }).join(', ');
    return '<div><strong>' + sel + '</strong> estrategia(s) se importarán.</div>' +
      '<div style="margin-top:6px;">Mining <strong>' + meta.mining + '</strong> · ' + meta.bs + ' · Template default <strong>' + (meta.template || '(auto-detect)') + '</strong> · Dirección <strong>' + meta.dir + '</strong> · TIER <strong>' + meta.tier + '</strong> · Status <strong>' + meta.status + '</strong></div>' +
      (sample ? '<div style="margin-top:6px; font-size:12px; color:var(--text2);">Primeras: ' + sample + (sel > 5 ? '…' : '') + '</div>' : '');
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

  function csvQuote(value) {
    return '"' + String(value == null ? '' : value).replace(/"/g, '""') + '"';
  }

  function exportCsvRows(strategies) {
    var headers = ['ID','Name','Mining','Asset','TF','Blocksetting','Template','Direction','Tier','Status','NetProfit','PF','Sharpe','RetDD','DDpct','Trades','WinPct','RExp','SQN','StagnationDays','TestsPassed','TestsFailed','Indicators','Exits','Notes','Added','Source'];
    var rows = (strategies || []).map(function(strategy) {
      var m = strategy.metrics || {};
      return [
        strategy.id, strategy.name, strategy.mining, strategy.asset, strategy.tf, strategy.blocksetting, strategy.template, strategy.direction, strategy.tier, strategy.status,
        m.net_profit == null ? '' : m.net_profit,
        m.pf == null ? '' : m.pf,
        m.sharpe == null ? '' : m.sharpe,
        m.ret_dd == null ? '' : m.ret_dd,
        m.dd_pct == null ? '' : m.dd_pct,
        m.trades == null ? '' : m.trades,
        m.win_pct == null ? '' : m.win_pct,
        m.r_exp == null ? '' : m.r_exp,
        m.sqn == null ? '' : m.sqn,
        m.stagnation_days == null ? '' : m.stagnation_days,
        (strategy.tests_passed || []).join('|'),
        (strategy.tests_failed || []).join('|'),
        (strategy.indicators || '').replace(/[\r\n]+/g, ' '),
        (strategy.exits || '').replace(/[\r\n]+/g, ' '),
        (strategy.notes || '').replace(/[\r\n]+/g, ' '),
        strategy.added || '',
        strategy._imported ? 'IMPORTED' : 'DEFAULT'
      ].map(csvQuote).join(';');
    });
    return [headers.map(csvQuote).join(';')].concat(rows);
  }

  function dedupeImportedStrategies(baseStrategies, userStrategies, newStrategies) {
    var existingKeys = new Set((baseStrategies || []).concat(userStrategies || []).map(function(strategy) {
      return strategy.id + '|' + strategy.mining + '|' + strategy.template;
    }));
    var fresh = (newStrategies || []).filter(function(strategy) {
      return !existingKeys.has(strategy.id + '|' + strategy.mining + '|' + strategy.template);
    });
    return {
      fresh: fresh,
      duplicates: (newStrategies || []).length - fresh.length
    };
  }

  function cleanedStrategies(strategies) {
    return (strategies || []).map(function(strategy) {
      var clone = JSON.parse(JSON.stringify(strategy));
      delete clone._imported;
      delete clone._import_id;
      return clone;
    });
  }

  function consolidateJson(strategies) {
    return JSON.stringify({ version: 1, strategies: cleanedStrategies(strategies) }, null, 2);
  }

  function escapePre(value) {
    return String(value).replace(/[<>&]/g, function(ch) {
      return { '<': '&lt;', '>': '&gt;', '&': '&amp;' }[ch];
    });
  }

  function consolidatedPopupHtml(jsonText, total) {
    return '<html><head><title>SQX Strategies — Consolidado</title><style>body{background:#0f1117;color:#e4e4e7;font-family:Segoe UI,sans-serif;padding:20px;}h1{font-size:16px;margin-bottom:10px;}p{color:#9ca3af;font-size:12px;margin-bottom:14px;}pre{background:#0a0c12;border:1px solid #2e3348;border-radius:8px;padding:14px;font-family:Consolas,monospace;font-size:12px;color:#9eb1d3;line-height:1.5;overflow:auto;max-height:80vh;white-space:pre-wrap;}button{margin-bottom:10px;padding:8px 16px;background:#22c55e;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:700;}</style></head><body>' +
      '<h1>Consolidado: ' + total + ' estrategias</h1>' +
      '<p>JSON compatible con <code>backend/sqx-edge-tool/config/strategies.json</code>.</p>' +
      '<button onclick="navigator.clipboard.writeText(document.getElementById(\'cn\').textContent).then(()=>this.textContent=\'Copiado\')">Copiar al portapapeles</button>' +
      '<pre id="cn">' + escapePre(jsonText) + '</pre>' +
      '</body></html>';
  }

  SQX.strategies = SQX.strategies || {
    autoDetectTemplate: autoDetectTemplate,
    consolidateJson: consolidateJson,
    consolidatedPopupHtml: consolidatedPopupHtml,
    csvConfirmHtml: csvConfirmHtml,
    csvPreviewTable: csvPreviewTable,
    dedupeImportedStrategies: dedupeImportedStrategies,
    detectSeparator: detectSeparator,
    exportCsvRows: exportCsvRows,
    filterOptionsHtml: filterOptionsHtml,
    filterCsvRows: filterCsvRows,
    filterStrategies: filterStrategies,
    getAllStrategies: getAllStrategies,
    parseCSV: parseCSV,
    rowToStrategy: rowToStrategy,
    sortForDisplay: sortForDisplay,
    strategyCard: strategyCard,
    strategyKey: strategyKey,
    summarize: summarize,
    summaryHtml: summaryHtml
  };

  if (SQX.registerModule) {
    SQX.registerModule('strategies', SQX.strategies);
  }
})(window);

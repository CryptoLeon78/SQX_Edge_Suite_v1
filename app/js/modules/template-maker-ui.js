(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var page = 1;
  var query = '';
  var pageSize = 50;
  var initialized = false;

  function byId(id) {
    return global.document.getElementById(id);
  }

  function init() {
    var tm = SQX.templateMaker;
    if (!tm) return;
    bindOnce();
    return tm.init().then(function() {
      initialized = true;
      renderAll();
    }).catch(function(err) {
      setStatus('No se pudo iniciar Template Maker: ' + (err && err.message ? err.message : err), true);
    });
  }

  function bindOnce() {
    var root = byId('tab-templatemaker');
    if (!root || root.dataset.tmBound === '1') return;
    root.dataset.tmBound = '1';

    bindUpload('tm-csv-zone', 'tm-csv-input', handleCSVFiles);
    bindUpload('tm-sqx-zone', 'tm-sqx-input', handleSQXFiles);

    Array.prototype.forEach.call(root.querySelectorAll('[data-tm-capa]'), function(button) {
      button.addEventListener('click', function() {
        SQX.templateMaker.setCapa(Number(button.dataset.tmCapa)).then(function() {
          page = 1;
          renderAll();
        });
      });
    });

    var preset = byId('tm-preset-select');
    if (preset) {
      preset.addEventListener('change', function() {
        SQX.templateMaker.setPreset(preset.value).then(function() {
          page = 1;
          renderAll();
        });
      });
    }

    var autoPreset = byId('tm-auto-preset');
    if (autoPreset) {
      autoPreset.addEventListener('click', function() {
        SQX.templateMaker.autoDetectPreset().then(function(best) {
          setStatus('Perfil detectado: ' + best);
          renderAll();
        });
      });
    }

    var search = byId('tm-search');
    if (search) {
      search.addEventListener('input', function() {
        query = search.value.toLowerCase();
        page = 1;
        renderResults();
      });
    }

    bindClick('tm-prev', function() {
      page = Math.max(1, page - 1);
      renderResults();
    });
    bindClick('tm-next', function() {
      page += 1;
      renderResults();
    });
    bindClick('tm-reset-btn', function() {
      if (!global.confirm || global.confirm('Resetear estrategias y configuracion de Template Maker?')) {
        SQX.templateMaker.reset().then(function() {
          setStatus('Template Maker limpio.');
          renderAll();
        });
      }
    });
    bindClick('tm-audit-btn', openAudit);
    bindClick('tm-audit-close', closeAudit);
    bindClick('tm-c2-cancel', closeC2);
    bindClick('tm-c2-confirm', confirmC2);
    bindClick('tm-thresholds-toggle', function() {
      var body = byId('tm-thresholds-content');
      if (body) body.hidden = !body.hidden;
    });
  }

  function bindClick(id, handler) {
    var el = byId(id);
    if (el) el.addEventListener('click', handler);
  }

  function bindUpload(zoneId, inputId, handler) {
    var zone = byId(zoneId);
    var input = byId(inputId);
    if (!zone || !input) return;
    zone.addEventListener('click', function() { input.click(); });
    input.addEventListener('change', function(event) { handler(event.target.files); });
    zone.addEventListener('dragover', function(event) {
      event.preventDefault();
      zone.classList.add('is-drag');
    });
    zone.addEventListener('dragleave', function() {
      zone.classList.remove('is-drag');
    });
    zone.addEventListener('drop', function(event) {
      event.preventDefault();
      zone.classList.remove('is-drag');
      handler(event.dataTransfer.files);
    });
  }

  function handleCSVFiles(files) {
    var file = files && files[0];
    if (!file) return;
    file.text().then(function(text) {
      return SQX.templateMaker.loadFromCSV(text);
    }).then(function(rows) {
      setStatus(rows.length + ' estrategias cargadas desde CSV.');
      renderAll();
    }).catch(function(err) {
      setStatus('Error CSV: ' + (err && err.message ? err.message : err), true);
    });
  }

  function handleSQXFiles(files) {
    var list = Array.prototype.slice.call(files || []).filter(function(file) {
      return /\.sqx$/i.test(file.name);
    });
    if (!list.length) return;
    setStatus('Procesando ' + list.length + ' archivos .sqx...');
    SQX.templateMaker.loadFromSQX(list).then(function(rows) {
      setStatus(rows.length + ' estrategias disponibles.');
      renderAll();
    }).catch(function(err) {
      setStatus('Error SQX: ' + (err && err.message ? err.message : err), true);
    });
  }

  function renderAll() {
    renderPreset();
    renderCapa();
    renderThresholds();
    renderStats();
    renderResults();
  }

  function renderPreset() {
    var select = byId('tm-preset-select');
    if (!select) return;
    var current = SQX.templateMaker.getCurrentPreset();
    select.innerHTML = SQX.templateMaker.getPresets().map(function(name) {
      return '<option value="' + esc(name) + '">' + esc(name) + '</option>';
    }).join('');
    select.value = current;
  }

  function renderCapa() {
    var capa = SQX.templateMaker.getCapa();
    Array.prototype.forEach.call(global.document.querySelectorAll('[data-tm-capa]'), function(button) {
      button.classList.toggle('active', Number(button.dataset.tmCapa) === capa);
    });
    var label = byId('tm-capa-label');
    if (label) label.textContent = capa === 1 ? 'Capa 1 - Mining Edge' : 'Capa 2 - Validacion operable';
  }

  function renderStats() {
    var report = SQX.templateMaker.getAuditReport();
    setText('tm-stat-total', report.total);
    setText('tm-stat-passed', report.passed);
    setText('tm-stat-review', report.review);
    setText('tm-stat-failed', report.failed);
  }

  function setText(id, value) {
    var el = byId(id);
    if (el) el.textContent = String(value);
  }

  function renderThresholds() {
    var grid = byId('tm-thresholds-grid');
    if (!grid) return;
    var thresholds = SQX.templateMaker.getThresholds();
    grid.innerHTML = Object.keys(thresholds).map(function(kpi) {
      var item = thresholds[kpi];
      return '<label class="tm-threshold-item">' +
        '<span>' + esc(kpi) + '</span>' +
        '<select data-tm-threshold-op="' + esc(kpi) + '">' +
          ['>', '>=', '<', '<='].map(function(op) {
            return '<option value="' + op + '"' + (op === item.op ? ' selected' : '') + '>' + op + '</option>';
          }).join('') +
        '</select>' +
        '<input type="number" step="0.01" data-tm-threshold-val="' + esc(kpi) + '" value="' + esc(item.val) + '">' +
      '</label>';
    }).join('');

    Array.prototype.forEach.call(grid.querySelectorAll('[data-tm-threshold-op]'), function(select) {
      select.addEventListener('change', function() {
        SQX.templateMaker.setThreshold(select.dataset.tmThresholdOp, 'op', select.value).then(renderResults);
      });
    });
    Array.prototype.forEach.call(grid.querySelectorAll('[data-tm-threshold-val]'), function(input) {
      input.addEventListener('change', function() {
        SQX.templateMaker.setThreshold(input.dataset.tmThresholdVal, 'val', input.value).then(function() {
          renderStats();
          renderResults();
        });
      });
    });
  }

  function renderResults() {
    var all = SQX.templateMaker.scoreAll();
    if (query) {
      all = all.filter(function(item) {
        var strategy = item.strategy;
        return ['Strategy Name', 'Symbol', 'Asset', 'TimeFrame'].some(function(key) {
          return String(strategy[key] || '').toLowerCase().indexOf(query) >= 0;
        });
      });
    }
    var totalPages = Math.max(1, Math.ceil(all.length / pageSize));
    page = Math.min(page, totalPages);
    var visible = all.slice((page - 1) * pageSize, page * pageSize);
    var table = byId('tm-results-table');
    var empty = byId('tm-empty-state');
    var pageInfo = byId('tm-page-info');
    if (pageInfo) pageInfo.textContent = page + ' / ' + totalPages;
    if (!table) return;
    if (empty) empty.hidden = all.length !== 0;
    table.hidden = all.length === 0;
    if (!all.length) return;

    var infoCols = SQX.templateMaker.getInfoColumns();
    var kpiCols = SQX.templateMaker.getKPIColumns();
    byId('tm-results-thead').innerHTML = '<tr><th>#</th><th>Score</th><th>Estado</th>' +
      infoCols.map(function(col) { return '<th>' + esc(col) + '</th>'; }).join('') +
      kpiCols.map(function(col) { return '<th>' + esc(col) + '</th>'; }).join('') +
      '<th>Accion</th></tr>';

    byId('tm-results-tbody').innerHTML = visible.map(function(item, index) {
      var globalIndex = (page - 1) * pageSize + index + 1;
      var score = item.score;
      var strategy = item.strategy;
      var badge = score.classification === 'PASSED' ? 'tm-badge-pass' : score.classification === 'REVIEW' ? 'tm-badge-review' : 'tm-badge-fail';
      return '<tr>' +
        '<td>' + globalIndex + '</td>' +
        '<td><div class="tm-score"><span style="width:' + score.pct + '%"></span></div><strong>' + score.pct + '%</strong></td>' +
        '<td><span class="tm-badge ' + badge + '">' + score.classification + '</span></td>' +
        infoCols.map(function(col) { return '<td>' + esc(strategy[col] || '-') + '</td>'; }).join('') +
        kpiCols.map(function(col) {
          var detail = score.details[col] || {};
          return '<td class="tm-kpi-' + (detail.result || 'na') + '">' + esc(detail.value === undefined || detail.value === '' ? '-' : detail.value) + '</td>';
        }).join('') +
        '<td><button class="filter-btn" type="button" data-tm-export="' + esc(strategy._id) + '"' + (score.classification !== 'PASSED' || !strategy._fileData ? ' disabled' : '') + '>C2</button></td>' +
      '</tr>';
    }).join('');

    Array.prototype.forEach.call(global.document.querySelectorAll('[data-tm-export]'), function(button) {
      button.addEventListener('click', function() {
        openC2(button.dataset.tmExport);
      });
    });
  }

  function openAudit() {
    var report = SQX.templateMaker.getAuditReport();
    var content = byId('tm-audit-content');
    var modal = byId('tm-modal-audit');
    if (!content || !modal) return;
    content.innerHTML = '<div class="tm-audit-grid">' +
      auditTile('Total', report.total) +
      auditTile('Passed', report.passed + ' (' + report.passedPct + '%)') +
      auditTile('Review', report.review) +
      auditTile('Failed', report.failed) +
      auditTile('Certificadas', report.certified + ' (' + report.certifiedPct + '%)') +
      auditTile('Perfil', report.preset + ' / Capa ' + report.capa) +
      '</div>';
    modal.hidden = false;
  }

  function auditTile(label, value) {
    return '<div class="tm-audit-tile"><span>' + esc(label) + '</span><strong>' + esc(value) + '</strong></div>';
  }

  function closeAudit() {
    var modal = byId('tm-modal-audit');
    if (modal) modal.hidden = true;
  }

  function openC2(id) {
    var strategy = SQX.templateMaker.getStrategies().find(function(item) {
      return String(item._id) === String(id);
    });
    var modal = byId('tm-modal-c2');
    if (!strategy || !modal) return;
    modal.dataset.strategyId = strategy._id;
    byId('tm-c2-asset').value = strategy.Symbol || '';
    byId('tm-c2-tf').value = strategy.TimeFrame || '';
    modal.hidden = false;
  }

  function closeC2() {
    var modal = byId('tm-modal-c2');
    if (modal) modal.hidden = true;
  }

  function confirmC2() {
    var modal = byId('tm-modal-c2');
    if (!modal) return;
    var strategy = SQX.templateMaker.getStrategies().find(function(item) {
      return String(item._id) === String(modal.dataset.strategyId);
    });
    if (!strategy) return;
    var options = {
      asset: byId('tm-c2-asset').value.trim() || strategy.Symbol || 'Asset',
      direction: byId('tm-c2-direction').value,
      timeframe: byId('tm-c2-tf').value.trim() || strategy.TimeFrame || 'TF',
      indicator: byId('tm-c2-indicator').value.trim() || 'IND',
      block: byId('tm-c2-block').value
    };
    SQX.templateMaker.generateC2Template(strategy, options).then(function(blob) {
      downloadBlob(blob, 'template_' + options.asset + '_' + options.direction + '_' + options.timeframe + '.sqx');
      closeC2();
    }).catch(function(err) {
      setStatus('No se pudo generar C2: ' + (err && err.message ? err.message : err), true);
    });
  }

  function downloadBlob(blob, name) {
    var a = global.document.createElement('a');
    a.href = global.URL.createObjectURL(blob);
    a.download = name;
    global.document.body.appendChild(a);
    a.click();
    global.document.body.removeChild(a);
    global.URL.revokeObjectURL(a.href);
  }

  function setStatus(message, isError) {
    var el = byId('tm-status');
    if (!el) return;
    el.textContent = message;
    el.classList.toggle('is-error', !!isError);
  }

  function esc(value) {
    var div = global.document.createElement('div');
    div.textContent = String(value === undefined || value === null ? '' : value);
    return div.innerHTML;
  }

  var api = { init: init, renderAll: renderAll, initialized: function() { return initialized; } };
  SQX.templateMakerUI = SQX.templateMakerUI || api;
  if (SQX.registerModule) SQX.registerModule('template-maker-ui', SQX.templateMakerUI);
})(window);

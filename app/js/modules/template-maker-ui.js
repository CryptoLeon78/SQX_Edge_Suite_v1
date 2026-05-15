(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var page = 1;
  var query = '';
  var pageSize = 50;
  var initialized = false;
  var selectedStrategyIds = {};

  function byId(id) {
    return global.document.getElementById(id);
  }

  function init() {
    var tm = SQX.templateMaker;
    if (!tm) return;
    bindOnce();
    return tm.init().then(function() {
      return tm.setCapa(1);
    }).then(function() {
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

    bindUpload('tm-unified-zone', 'tm-files-input', handleUnifiedFiles);
    bindUpload('tm-csv-zone', 'tm-csv-input', handleCSVFiles);
    bindUpload('tm-sqx-zone', 'tm-sqx-input', handleSQXFiles);
    bindClick('tm-open-cert-view', openCertView);

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
    bindClick('tm-reset-results-btn', function() {
      if (!SQX.templateMaker.clearResultStrategies) return;
      if (!global.confirm || global.confirm('Resetear todos los resultados cargados en Template Maker? Perfil y umbrales se conservan.')) {
        SQX.templateMaker.clearResultStrategies().then(function(summary) {
          page = 1;
          selectedStrategyIds = {};
          clearFileInput('tm-files-input');
          clearFileInput('tm-csv-input');
          clearFileInput('tm-sqx-input');
          setStatus('Resultados limpiados: ' + summary.removed + ' estrategias eliminadas.');
          renderAll();
        });
      }
    });
    bindClick('tm-delete-selected-btn', function() {
      if (!SQX.templateMaker.deleteResultStrategies) return;
      var selected = getSelectedStrategyIds();
      if (!selected.length) {
        setStatus('Selecciona una o varias estrategias antes de borrar.', true);
        return;
      }
      if (!global.confirm || global.confirm('Borrar ' + selected.length + ' estrategias seleccionadas de Template Maker?')) {
        SQX.templateMaker.deleteResultStrategies(selected).then(function(summary) {
          page = 1;
          selectedStrategyIds = {};
          setStatus('Estrategias seleccionadas eliminadas: ' + summary.removed + '.');
          renderAll();
        });
      }
    });
    bindClick('tm-reset-btn', function() {
      if (!global.confirm || global.confirm('Resetear estrategias y configuracion de Template Maker?')) {
        SQX.templateMaker.reset().then(function() {
          selectedStrategyIds = {};
          setStatus('Template Maker limpio.');
          renderAll();
        });
      }
    });
    bindClick('tm-audit-btn', openAudit);
    bindClick('tm-audit-close', closeAudit);
    bindClick('tm-c2-cancel', closeC2);
    bindClick('tm-c2-confirm', confirmC2);
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

  function clearFileInput(id) {
    var input = byId(id);
    if (input) input.value = '';
  }

  function handleCSVFiles(files) {
    var file = files && files[0];
    if (!file) return;
    file.text().then(function(text) {
      return SQX.templateMaker.loadFromCSV(text, { fileName: file.name || '' });
    }).then(function(rows) {
      setStatus(rows.length + ' estrategias cargadas desde CSV.');
      renderAll();
    }).catch(function(err) {
      setStatus('Error CSV: ' + (err && err.message ? err.message : err), true);
    });
  }

  function handleUnifiedFiles(files) {
    var list = Array.prototype.slice.call(files || []);
    if (!list.length) return;
    setStatus('Procesando ' + list.length + ' archivos CSV/SQX...');
    SQX.templateMaker.ingestFiles(list).then(function(rows) {
      setStatus(rows.length + ' estrategias reconciliadas con contrato Template Maker Cert.');
      renderAll();
    }).catch(function(err) {
      setStatus('Error de carga: ' + (err && err.message ? err.message : err), true);
    });
  }

  function handleSQXFiles(files) {
    var list = Array.prototype.slice.call(files || []).filter(function(file) {
      return /\.(sqx|zip)$/i.test(file.name);
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
    renderContractSummary();
    renderContractDiagnostics();
    renderResultsResetAction();
    renderDeleteSelectedAction();
    renderResults();
  }

  function renderResultsResetAction() {
    var button = byId('tm-reset-results-btn');
    if (!button) return;
    var total = SQX.templateMaker.getStrategies().length;
    button.disabled = total === 0;
    button.title = total
      ? 'Borra todas las estrategias cargadas en la tabla de resultados.'
      : 'Carga estrategias para habilitar este reset.';
  }

  function cleanupSelectedStrategies() {
    var existing = {};
    SQX.templateMaker.getStrategies().forEach(function(strategy) {
      existing[String(strategy._id)] = true;
    });
    Object.keys(selectedStrategyIds).forEach(function(id) {
      if (!existing[id]) delete selectedStrategyIds[id];
    });
  }

  function getSelectedStrategyIds() {
    cleanupSelectedStrategies();
    return Object.keys(selectedStrategyIds).filter(function(id) {
      return selectedStrategyIds[id];
    });
  }

  function renderDeleteSelectedAction() {
    var button = byId('tm-delete-selected-btn');
    if (!button) return;
    var count = getSelectedStrategyIds().length;
    button.disabled = count === 0;
    button.textContent = count ? 'Borrar seleccionadas (' + count + ')' : 'Borrar seleccionadas';
    button.title = count
      ? 'Borra solo las estrategias marcadas en la tabla.'
      : 'Marca estrategias en la tabla para habilitar este borrado.';
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
    var label = byId('tm-capa-label');
    if (label) label.textContent = 'Capa 1 - Mining Edge';
  }

  function renderStats() {
    var report = SQX.templateMaker.getAuditReport();
    setText('tm-stat-total', report.total);
    setText('tm-stat-passed', report.passed);
    setText('tm-stat-review', report.review);
    setText('tm-stat-failed', report.failed);
  }

  function openCertView() {
    var tab = global.document.querySelector('.tab[data-tab="views"]');
    if (tab && typeof tab.click === 'function') tab.click();
    if (SQX.viewCreator && SQX.viewCreator.loadBuyerReadyTemplate) {
      SQX.viewCreator.loadBuyerReadyTemplate('template-maker-cert');
    }
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

  function renderContractSummary() {
    var mount = byId('tm-contract-summary');
    if (!mount) return;
    var scored = SQX.templateMaker.scoreAll();
    var labels = [
      {
        status: 'Lista para C2',
        className: 'is-ready',
        action: 'Ya puede generar C2 si el candidato es el elegido.'
      },
      {
        status: 'Completa',
        className: 'is-complete',
        action: 'Tiene CSV y .sqx; revisa scoring antes de C2.'
      },
      {
        status: 'Falta SQX',
        className: 'is-warning',
        action: 'Añade el .sqx original para habilitar C2.'
      },
      {
        status: 'Faltan métricas',
        className: 'is-danger',
        action: 'Exporta CSV con Template Maker Cert desde SQX.'
      },
      {
        status: 'Métricas no compatibles',
        className: 'is-danger',
        action: 'Regenera el Databank CSV con la view obligatoria.'
      }
    ];
    var counts = labels.reduce(function(acc, item) {
      acc[item.status] = 0;
      return acc;
    }, {});
    scored.forEach(function(item) {
      var status = SQX.templateMaker.getStrategyStatus(item.strategy, item.score);
      counts[status] = (counts[status] || 0) + 1;
    });
    mount.innerHTML = labels.map(function(item) {
      return '<div class="tm-contract-card ' + item.className + '">' +
        '<span>' + esc(item.status) + '</span>' +
        '<strong>' + esc(counts[item.status] || 0) + '</strong>' +
        '<small>' + esc(item.action) + '</small>' +
      '</div>';
    }).join('');
  }

  function renderContractDiagnostics() {
    var mount = byId('tm-contract-diagnostics');
    if (!mount || !SQX.templateMaker.getContractDiagnostics) return;
    var diagnostics = SQX.templateMaker.getContractDiagnostics();
    var missing = diagnostics.missingRequired || [];
    var recognized = diagnostics.recognizedColumns || [];
    var derived = diagnostics.derivedMetrics || [];
    var required = diagnostics.requiredColumns || [];
    mount.innerHTML = '<div class="tm-diagnostic-grid">' +
      diagnosticCard('Contrato', diagnostics.schemaVersion || 'template-maker-cert-v2', 'Regla activa de certificacion. Si cambia, Template Maker limpia estado antiguo.') +
      diagnosticCard('Perfil CSV', diagnostics.detectedCsvProfile || 'Sin datos', 'Lectura inferida desde las columnas detectadas.') +
      diagnosticCard('Columnas', recognized.length + ' / ' + required.length, 'Reconocidas frente a las obligatorias de Template Maker Cert.') +
      diagnosticCard('Derivadas', derived.length ? derived.join(', ') : 'Ninguna', 'Metricas calculadas por alias controlado, no bloqueantes.') +
      '</div>' +
      '<div class="tm-diagnostic-tags">' +
        '<span><strong>Faltantes reales:</strong> ' + esc(missing.length ? missing.join(', ') : 'ninguna') + '</span>' +
        '<span><strong>Reconocidas:</strong> ' + esc(recognized.length ? recognized.slice(0, 12).join(', ') + (recognized.length > 12 ? '...' : '') : 'pendiente de CSV') + '</span>' +
      '</div>';
  }

  function diagnosticCard(label, value, help) {
    return '<div class="tm-diagnostic-card">' +
      '<span>' + esc(label) + '</span>' +
      '<strong>' + esc(value) + '</strong>' +
      '<small>' + esc(help) + '</small>' +
    '</div>';
  }

  function renderResults() {
    cleanupSelectedStrategies();
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
    renderProblems();
    if (!all.length) {
      byId('tm-results-thead').innerHTML = '';
      byId('tm-results-tbody').innerHTML = '';
      renderDeleteSelectedAction();
      return;
    }

    var infoCols = SQX.templateMaker.getInfoColumns();
    var kpiCols = SQX.templateMaker.getKPIColumns();
    byId('tm-results-thead').innerHTML = '<tr><th class="tm-col-select"><input id="tm-select-visible" class="tm-select-visible" type="checkbox" aria-label="Seleccionar estrategias visibles"></th><th class="tm-col-index">#</th><th class="tm-col-score">Score</th><th class="tm-col-state">Estado</th><th class="tm-col-contract">Contrato</th>' +
      infoCols.map(function(col) { return '<th class="tm-col-info">' + esc(col) + '</th>'; }).join('') +
      kpiCols.map(function(col) { return '<th class="tm-col-kpi">' + esc(col) + '</th>'; }).join('') +
      '<th class="tm-col-action">Accion</th></tr>';

    byId('tm-results-tbody').innerHTML = visible.map(function(item, index) {
      var globalIndex = (page - 1) * pageSize + index + 1;
      var score = item.score;
      var strategy = item.strategy;
      var badge = score.classification === 'PASSED' ? 'tm-badge-pass' : score.classification === 'REVIEW' ? 'tm-badge-review' : 'tm-badge-fail';
      var contractStatus = SQX.templateMaker.getStrategyStatus(strategy, score);
      var contractBadge = contractStatus === 'Lista para C2' ? 'tm-badge-ready' :
        contractStatus === 'Completa' ? 'tm-badge-pass' :
        contractStatus === 'Falta SQX' ? 'tm-badge-review' : 'tm-badge-fail';
      var canC2 = SQX.templateMaker.canGenerateC2(strategy);
      var strategyId = String(strategy._id);
      return '<tr>' +
        '<td class="tm-col-select"><input class="tm-row-check" type="checkbox" data-tm-select="' + esc(strategyId) + '" aria-label="Seleccionar estrategia ' + globalIndex + '"' + (selectedStrategyIds[strategyId] ? ' checked' : '') + '></td>' +
        '<td class="tm-col-index">' + globalIndex + '</td>' +
        '<td class="tm-col-score"><div class="tm-score"><span style="width:' + score.pct + '%"></span></div><strong>' + score.pct + '%</strong></td>' +
        '<td class="tm-col-state"><span class="tm-badge ' + badge + '">' + score.classification + '</span></td>' +
        '<td class="tm-col-contract"><span class="tm-badge ' + contractBadge + '">' + esc(contractStatus) + '</span></td>' +
        infoCols.map(function(col) { return '<td class="tm-col-info" title="' + esc(strategy[col] || '-') + '">' + esc(strategy[col] || '-') + '</td>'; }).join('') +
        kpiCols.map(function(col) {
          var detail = score.details[col] || {};
          return '<td class="tm-col-kpi tm-kpi-' + (detail.result || 'na') + '">' + esc(detail.value === undefined || detail.value === '' ? '-' : detail.value) + '</td>';
        }).join('') +
        '<td class="tm-col-action"><button class="filter-btn tm-c2-action" type="button" data-tm-export="' + esc(strategy._id) + '"' + (!canC2 ? ' disabled' : '') + '>C2</button></td>' +
      '</tr>';
    }).join('');

    Array.prototype.forEach.call(global.document.querySelectorAll('[data-tm-export]'), function(button) {
      button.addEventListener('click', function() {
        openC2(button.dataset.tmExport);
      });
    });
    Array.prototype.forEach.call(global.document.querySelectorAll('[data-tm-select]'), function(checkbox) {
      checkbox.addEventListener('change', function() {
        selectedStrategyIds[String(checkbox.dataset.tmSelect)] = checkbox.checked;
        if (!checkbox.checked) delete selectedStrategyIds[String(checkbox.dataset.tmSelect)];
        updateVisibleSelectionState(visible);
        renderDeleteSelectedAction();
      });
    });
    var selectVisible = byId('tm-select-visible');
    if (selectVisible) {
      selectVisible.addEventListener('change', function() {
        visible.forEach(function(item) {
          var id = String(item.strategy._id);
          if (selectVisible.checked) {
            selectedStrategyIds[id] = true;
          } else {
            delete selectedStrategyIds[id];
          }
        });
        renderResults();
      });
      updateVisibleSelectionState(visible);
    }
    renderDeleteSelectedAction();
  }

  function updateVisibleSelectionState(visible) {
    var selectVisible = byId('tm-select-visible');
    if (!selectVisible) return;
    var ids = (visible || []).map(function(item) {
      return String(item.strategy._id);
    });
    var selectedCount = ids.filter(function(id) {
      return selectedStrategyIds[id];
    }).length;
    selectVisible.checked = ids.length > 0 && selectedCount === ids.length;
    selectVisible.indeterminate = selectedCount > 0 && selectedCount < ids.length;
  }

  function renderProblems() {
    var panel = byId('tm-problem-panel');
    if (!panel) return;
    var total = SQX.templateMaker.getStrategies().length;
    if (!total) {
      panel.innerHTML = '<strong>Contrato pendiente</strong><span>Carga CSV Template Maker Cert y/o archivos .sqx para iniciar la certificacion.</span>';
      panel.classList.remove('is-ok');
      return;
    }
    var incomplete = SQX.templateMaker.getIncompleteRecords();
    if (!incomplete.length) {
      panel.innerHTML = '<strong>Contrato completo</strong><span>Todas las estrategias tienen CSV Template Maker Cert, .sqx y estado operativo coherente.</span>';
      panel.classList.add('is-ok');
      return;
    }
    panel.classList.remove('is-ok');
    var groups = incomplete.reduce(function(acc, strategy) {
      var status = strategy.certification && strategy.certification.status || 'Pendiente';
      acc[status] = (acc[status] || 0) + 1;
      return acc;
    }, {});
    panel.innerHTML = '<strong>Accion requerida antes de C2</strong>' +
      '<span>Template Maker solo habilita C2 cuando existe .sqx, CSV exportado con Template Maker Cert y scoring PASSED.</span>' +
      '<div class="tm-problem-tags">' + Object.keys(groups).map(function(status) {
        return '<span>' + esc(status) + ': ' + groups[status] + ' · ' + esc(problemHint(status)) + '</span>';
      }).join('') + '</div>';
  }

  function problemHint(status) {
    if (status === 'Falta SQX') return 'añade el .sqx original';
    if (status === 'Faltan métricas') return 'exporta CSV con Template Maker Cert';
    if (status === 'Métricas no compatibles') return 'CSV de otra view: reexporta con Template Maker Cert';
    if (status === 'Completa') return 'necesita scoring PASSED para C2';
    return 'revisa fuentes';
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
      auditTile('Pendientes', SQX.templateMaker.getIncompleteRecords().length) +
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

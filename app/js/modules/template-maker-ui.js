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

  function confirmTrace(options, fallbackMessage) {
    if (SQX.modalRegistry && SQX.modalRegistry.confirm) {
      return SQX.modalRegistry.confirm(options || {});
    }
    return Promise.resolve(!global.confirm || global.confirm(fallbackMessage || (options && options.message) || 'Confirmar accion'));
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
      confirmTrace({
        title: 'Reset resultados Template Maker',
        message: 'Resetear todos los resultados cargados en Template Maker. Perfil y umbrales se conservan.',
        confirmLabel: 'Reset resultados',
        trace: ['Destino: IndexedDB SQXTemplateMakerDB', 'Borra: estrategias cargadas', 'Conserva: perfil, umbrales y ajustes']
      }, 'Resetear todos los resultados cargados en Template Maker? Perfil y umbrales se conservan.').then(function(ok) {
        if (!ok) return;
        SQX.templateMaker.clearResultStrategies().then(function(summary) {
          page = 1;
          selectedStrategyIds = {};
          clearFileInput('tm-files-input');
          clearFileInput('tm-csv-input');
          clearFileInput('tm-sqx-input');
          setStatus('Resultados limpiados: ' + summary.removed + ' estrategias eliminadas.');
          renderAll();
        });
      });
    });
    bindClick('tm-delete-selected-btn', function() {
      if (!SQX.templateMaker.deleteResultStrategies) return;
      var selected = getSelectedStrategyIds();
      if (!selected.length) {
        setStatus('Selecciona una o varias estrategias antes de borrar.', true);
        return;
      }
      confirmTrace({
        title: 'Borrar seleccionadas',
        message: 'Borrar ' + selected.length + ' estrategias seleccionadas de Template Maker.',
        confirmLabel: 'Borrar seleccionadas',
        trace: ['Destino: IndexedDB SQXTemplateMakerDB', 'Impacto: se recalculan contrato, diversidad y acciones C2', 'Recuperacion: recargar CSV/SQX']
      }, 'Borrar ' + selected.length + ' estrategias seleccionadas de Template Maker?').then(function(ok) {
        if (!ok) return;
        SQX.templateMaker.deleteResultStrategies(selected).then(function(summary) {
          page = 1;
          selectedStrategyIds = {};
          setStatus('Estrategias seleccionadas eliminadas: ' + summary.removed + '.');
          renderAll();
        });
      });
    });
    bindClick('tm-c2-selected-btn', function() {
      var selected = getSelectedStrategyIds();
      if (selected.length !== 1) {
        setStatus('Selecciona una sola estrategia lista para C2.', true);
        return;
      }
      var strategy = SQX.templateMaker.getStrategies().find(function(item) {
        return String(item._id) === String(selected[0]);
      });
      if (!strategy || !SQX.templateMaker.canGenerateC2(strategy)) {
        setStatus('La estrategia seleccionada no supera contrato, scoring y diversidad.', true);
        return;
      }
      openC2(strategy._id);
    });
    bindClick('tm-reset-btn', function() {
      confirmTrace({
        title: 'Reset completo Template Maker',
        message: 'Resetear estrategias y configuracion de Template Maker.',
        confirmLabel: 'Reset Template Maker',
        trace: ['Destino: IndexedDB SQXTemplateMakerDB', 'Borra: estrategias y configuracion interna', 'Recuperacion: recargar fuentes y view obligatoria']
      }, 'Resetear estrategias y configuracion de Template Maker?').then(function(ok) {
        if (!ok) return;
        SQX.templateMaker.reset().then(function() {
          selectedStrategyIds = {};
          setStatus('Template Maker limpio.');
          renderAll();
        });
      });
    });
    bindClick('tm-audit-btn', openAudit);
    bindClick('tm-audit-close', closeAudit);
    bindClick('tm-c2-cancel', closeC2);
    bindClick('tm-c2-confirm', confirmC2);
    ['tm-c2-asset', 'tm-c2-direction', 'tm-c2-tf', 'tm-c2-indicator', 'tm-c2-cluster', 'tm-c2-block'].forEach(function(id) {
      var el = byId(id);
      if (el) el.addEventListener(el.tagName === 'SELECT' ? 'change' : 'input', renderC2TracePreview);
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
    renderDiversitySettings();
    renderStats();
    renderContractSummary();
    renderContractDiagnostics();
    renderResultsResetAction();
    renderDeleteSelectedAction();
    renderC2SelectedAction();
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

  function renderC2SelectedAction() {
    var button = byId('tm-c2-selected-btn');
    if (!button) return;
    var selected = getSelectedStrategyIds();
    var strategy = selected.length === 1 ? SQX.templateMaker.getStrategies().find(function(item) {
      return String(item._id) === String(selected[0]);
    }) : null;
    var ready = !!(strategy && SQX.templateMaker.canGenerateC2(strategy));
    button.disabled = !ready;
    button.textContent = selected.length === 1 ? 'Generar C2 seleccionada' : 'Generar C2 seleccionada';
    button.title = ready
      ? 'Abre la generacion C2 para la estrategia marcada.'
      : selected.length === 1
        ? 'La estrategia marcada no es ganadora/diversa o no esta lista para C2.'
        : 'Marca una unica estrategia lista para C2.';
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

  function renderDiversitySettings() {
    var grid = byId('tm-diversity-settings-grid');
    var reportMount = byId('tm-diversity-report');
    if (!grid || !SQX.templateMaker.getDiversitySettings) return;
    var settings = SQX.templateMaker.getDiversitySettings();
    var fields = [
      ['structuralThreshold', 'Estructura', 'Similitud minima por indicadores .sqx'],
      ['metricThreshold', 'Metricas', 'Confirmacion secundaria por KPIs'],
      ['hybridThreshold', 'Hibrido', 'Umbral final estructura + metricas'],
      ['structuralWeight', 'Peso estructura', 'Peso de indicadores/reglas'],
      ['metricWeight', 'Peso metricas', 'Peso de KPIs CSV']
    ];
    grid.innerHTML = fields.map(function(field) {
      return '<label class="tm-threshold-item tm-diversity-setting-item">' +
        '<span>' + esc(field[1]) + '<small>' + esc(field[2]) + '</small></span>' +
        '<input type="number" min="0" max="1" step="0.01" data-tm-diversity-setting="' + esc(field[0]) + '" value="' + esc(settings[field[0]]) + '">' +
      '</label>';
    }).join('');
    Array.prototype.forEach.call(grid.querySelectorAll('[data-tm-diversity-setting]'), function(input) {
      input.addEventListener('change', function() {
        SQX.templateMaker.setDiversitySetting(input.dataset.tmDiversitySetting, input.value).then(function() {
          renderStats();
          renderContractSummary();
          renderDiversitySettings();
          renderResults();
        });
      });
    });
    if (reportMount && SQX.templateMaker.getDiversityReport) {
      var report = SQX.templateMaker.getDiversityReport();
      reportMount.innerHTML = '<span>Candidatos: <strong>' + esc(report.candidates) + '</strong></span>' +
        '<span>Clusters: <strong>' + esc(report.clusters.length) + '</strong></span>' +
        '<span>Ganadores C2: <strong>' + esc(report.winners) + '</strong></span>' +
        '<span>Descartadas por similitud: <strong>' + esc(report.discarded) + '</strong></span>';
    }
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
        status: 'Similar descartada',
        className: 'is-warning',
        action: 'Pertenece a un cluster; usa el ganador diverso.'
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
    byId('tm-results-thead').innerHTML = '<tr><th class="tm-col-select"><input id="tm-select-visible" class="tm-select-visible" type="checkbox" aria-label="Seleccionar estrategias visibles"></th><th class="tm-col-index">#</th><th class="tm-col-score">Score</th><th class="tm-col-state">Estado</th><th class="tm-col-contract">Contrato</th><th class="tm-col-diversity">Div.</th><th class="tm-col-cluster">Cluster</th><th class="tm-col-similarity">Sim.</th><th class="tm-col-reason">Motivo</th>' +
      infoCols.map(function(col) { return '<th class="tm-col-info" title="' + esc(col) + '">' + esc(columnLabel(col)) + '</th>'; }).join('') +
      kpiCols.map(function(col) { return '<th class="tm-col-kpi" title="' + esc(col) + '">' + esc(columnLabel(col)) + '</th>'; }).join('') +
      '</tr>';

    byId('tm-results-tbody').innerHTML = visible.map(function(item, index) {
      var globalIndex = (page - 1) * pageSize + index + 1;
      var score = item.score;
      var strategy = item.strategy;
      var badge = score.classification === 'PASSED' ? 'tm-badge-pass' : score.classification === 'REVIEW' ? 'tm-badge-review' : 'tm-badge-fail';
      var contractStatus = SQX.templateMaker.getStrategyStatus(strategy, score);
      var contractBadge = contractStatus === 'Lista para C2' ? 'tm-badge-ready' :
        contractStatus === 'Completa' ? 'tm-badge-pass' :
        contractStatus === 'Falta SQX' || contractStatus === 'Similar descartada' ? 'tm-badge-review' : 'tm-badge-fail';
      var diversity = SQX.templateMaker.getDiversityStatus ? SQX.templateMaker.getDiversityStatus(strategy) : { status: 'No evaluable', clusterId: '-', similarity: 0, reason: '-' };
      var diversityBadge = diversity.status === 'Diverso' || diversity.status === 'Ganador cluster' ? 'tm-badge-ready' :
        diversity.status === 'Similar descartada' ? 'tm-badge-review' : 'tm-badge-fail';
      var strategyId = String(strategy._id);
      return '<tr>' +
        '<td class="tm-col-select"><input class="tm-row-check" type="checkbox" data-tm-select="' + esc(strategyId) + '" aria-label="Seleccionar estrategia ' + globalIndex + '"' + (selectedStrategyIds[strategyId] ? ' checked' : '') + '></td>' +
        '<td class="tm-col-index">' + globalIndex + '</td>' +
        '<td class="tm-col-score"><div class="tm-score"><span style="width:' + score.pct + '%"></span></div><strong>' + score.pct + '%</strong></td>' +
        '<td class="tm-col-state"><span class="tm-badge ' + badge + '">' + score.classification + '</span></td>' +
        '<td class="tm-col-contract"><span class="tm-badge ' + contractBadge + '">' + esc(contractStatus) + '</span></td>' +
        '<td class="tm-col-diversity"><span class="tm-badge ' + diversityBadge + '">' + esc(diversity.status) + '</span></td>' +
        '<td class="tm-col-cluster">' + esc(diversity.clusterId || '-') + '</td>' +
        '<td class="tm-col-similarity">' + esc(Math.round((diversity.similarity || 0) * 100)) + '%</td>' +
        '<td class="tm-col-reason" title="' + esc(diversity.reason || '-') + '">' + esc(diversity.reason || '-') + '</td>' +
        infoCols.map(function(col) { return '<td class="tm-col-info" title="' + esc(strategy[col] || '-') + '">' + esc(strategy[col] || '-') + '</td>'; }).join('') +
        kpiCols.map(function(col) {
          var detail = score.details[col] || {};
          return '<td class="tm-col-kpi tm-kpi-' + (detail.result || 'na') + '" title="' + esc(detail.value === undefined || detail.value === '' ? '-' : detail.value) + '">' + esc(displayMetricValue(col, detail.value)) + '</td>';
        }).join('') +
      '</tr>';
    }).join('');

    Array.prototype.forEach.call(global.document.querySelectorAll('[data-tm-select]'), function(checkbox) {
      checkbox.addEventListener('change', function() {
        selectedStrategyIds[String(checkbox.dataset.tmSelect)] = checkbox.checked;
        if (!checkbox.checked) delete selectedStrategyIds[String(checkbox.dataset.tmSelect)];
        updateVisibleSelectionState(visible);
        renderDeleteSelectedAction();
        renderC2SelectedAction();
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
    renderC2SelectedAction();
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
    if (status === 'Similar descartada') return 'usa el ganador diverso del cluster';
    return 'revisa fuentes';
  }

  function columnLabel(column) {
    var labels = {
      'Strategy Name': 'Name',
      Asset: 'Asset',
      Symbol: 'Symbol',
      TimeFrame: 'TF',
      Fitness: 'Fit',
      'Net profit': 'Net',
      '# of trades': 'Trades',
      'Profit factor': 'PF',
      'Max DD %': 'DD%',
      'Sharpe Ratio': 'Sharpe',
      Stability: 'Stab',
      'CAGR/Max DD %': 'C/DD',
      'Winning Percent': 'Win%',
      SQN: 'SQN',
      'Recovery Factor': 'Recov'
    };
    return labels[column] || column;
  }

  function displayMetricValue(column, value) {
    if (value === undefined || value === '') return '-';
    var normalized = String(value).replace(',', '.');
    var number = Number(normalized);
    if (Number.isNaN(number)) return String(value);
    if (column === 'Net profit') {
      if (Math.abs(number) >= 1000) return (number / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
      return String(Math.round(number));
    }
    if (column === '# of trades') return String(Math.round(number));
    if (column === 'Max DD %' || column === 'Winning Percent') return number.toFixed(1).replace(/\.0$/, '');
    return number.toFixed(2).replace(/0$/, '').replace(/\.$/, '');
  }

  function openAudit() {
    var report = SQX.templateMaker.getAuditReport();
    var content = byId('tm-audit-content');
    var modal = byId('tm-modal-audit');
    if (!content || !modal) return;
    var records = SQX.templateMaker.getStrategyRecords ? SQX.templateMaker.getStrategyRecords() : SQX.templateMaker.getStrategies();
    var firstCsv = (records || []).find(function(item) { return item && item.sources && item.sources.csv; }) || {};
    var firstProvenance = firstCsv.provenance || {};
    var firstSource = firstCsv.sources && firstCsv.sources.csv || {};
    var traceItems = [
      'Contrato: ' + (firstProvenance.schemaVersion || firstProvenance.certVersion || 'template-maker-cert-v2'),
      'View: ' + (firstProvenance.viewName || firstSource.viewName || 'no detectada'),
      'CSV: ' + (firstSource.filename || 'no cargado'),
      'Registros: ' + (records || []).length,
      'Pendientes: ' + SQX.templateMaker.getIncompleteRecords().length
    ];
    var traceHtml = SQX.modalRegistry && SQX.modalRegistry.tracePanelHtml
      ? SQX.modalRegistry.tracePanelHtml('Origen y contrato de auditoria', traceItems)
      : '';
    content.innerHTML = traceHtml + '<div class="tm-audit-grid">' +
      auditTile('Total', report.total) +
      auditTile('Passed', report.passed + ' (' + report.passedPct + '%)') +
      auditTile('Review', report.review) +
      auditTile('Failed', report.failed) +
      auditTile('Pendientes', SQX.templateMaker.getIncompleteRecords().length) +
      auditTile('Certificadas', report.certified + ' (' + report.certifiedPct + '%)') +
      auditTile('Clusters diversidad', report.diversity ? report.diversity.clusters : 0) +
      auditTile('Ganadores C2', report.diversity ? report.diversity.winners : 0) +
      auditTile('Descartadas similitud', report.diversity ? report.diversity.discarded : 0) +
      auditTile('Salidas detectadas', report.exitPolicy ? report.exitPolicy.detected : 0) +
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
    var trace = SQX.templateMaker.resolveC2Trace(strategy, {
      direction: byId('tm-c2-direction') && byId('tm-c2-direction').value || '',
      blockSetting: byId('tm-c2-block') && byId('tm-c2-block').value || 'BS_Tendencia_v6'
    });
    modal.dataset.strategyId = strategy._id;
    byId('tm-c2-asset').value = trace.asset || strategy.Symbol || '';
    byId('tm-c2-tf').value = trace.timeframe || strategy.TimeFrame || '';
    byId('tm-c2-indicator').value = trace.indicatorBase || 'SIN_INDICADOR';
    byId('tm-c2-cluster').value = trace.clusterId || 'CL00';
    setSelectValue('tm-c2-direction', trace.direction || 'BOTH');
    setSelectValue('tm-c2-block', trace.blockSetting || 'BS_Tendencia_v6');
    modal.hidden = false;
    renderC2TracePreview();
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
    var options = readC2Options(strategy);
    var trace = SQX.templateMaker.resolveC2Trace(strategy, options);
    SQX.templateMaker.generateC2Template(strategy, options).then(function(blob) {
      downloadBlob(blob, trace.name + '.sqx');
      setStatus('Template C2 generado: ' + trace.name + ' · ' + trace.blockSetting + ' · ' + trace.indicatorBase + ' · ' + trace.clusterId);
      closeC2();
    }).catch(function(err) {
      setStatus('No se pudo generar C2: ' + (err && err.message ? err.message : err), true);
    });
  }

  function readC2Options(strategy) {
    return {
      asset: (byId('tm-c2-asset') && byId('tm-c2-asset').value.trim()) || strategy.Symbol || 'Asset',
      direction: byId('tm-c2-direction') && byId('tm-c2-direction').value || 'BOTH',
      timeframe: (byId('tm-c2-tf') && byId('tm-c2-tf').value.trim()) || strategy.TimeFrame || 'TF',
      indicatorBase: (byId('tm-c2-indicator') && byId('tm-c2-indicator').value.trim()) || 'SIN_INDICADOR',
      clusterId: (byId('tm-c2-cluster') && byId('tm-c2-cluster').value.trim()) || 'CL00',
      blockSetting: byId('tm-c2-block') && byId('tm-c2-block').value || 'BS_Tendencia_v6'
    };
    options.exitOverrides = readExitOverrides();
    return options;
  }

  function readExitOverrides() {
    var overrides = {};
    var modal = byId('tm-modal-c2');
    if (!modal) return overrides;
    Array.prototype.forEach.call(modal.querySelectorAll('[data-tm-exit-action]'), function(select) {
      var id = select.getAttribute('data-tm-exit-action');
      if (!id) return;
      overrides[id] = { action: select.value };
    });
    return overrides;
  }

  function renderC2TracePreview() {
    var modal = byId('tm-modal-c2');
    if (!modal || modal.hidden) return;
    var strategy = SQX.templateMaker.getStrategies().find(function(item) {
      return String(item._id) === String(modal.dataset.strategyId);
    });
    if (!strategy) return;
    var trace = SQX.templateMaker.resolveC2Trace(strategy, readC2Options(strategy));
    var indicators = byId('tm-c2-indicators-detected');
    var preview = byId('tm-c2-name-preview');
    var warning = byId('tm-c2-trace-warning');
    if (indicators) indicators.textContent = trace.indicatorDisplay || 'SIN_INDICADOR';
    if (preview) preview.textContent = trace.name + '.sqx';
    if (warning) {
      warning.hidden = !trace.missing.length;
      warning.textContent = trace.missing.length
        ? 'Completa o confirma estos campos antes de generar: ' + trace.missing.join(', ') + '.'
        : '';
    }
    if (SQX.templateMaker.getC2GenerationPreview) {
      SQX.templateMaker.getC2GenerationPreview(strategy, readC2Options(strategy)).then(function(result) {
        renderC2ExitPolicy(result);
      }).catch(function(err) {
        renderC2ExitPolicy({
          blocked: true,
          exitPolicyVersion: 'sqx-exit-policy-v1',
          exitPlan: { components: [] },
          exitSummary: { detected: [], blocked: [err && err.message ? err.message : 'error'] }
        });
      });
    }
  }

  function renderC2ExitPolicy(result) {
    var summary = result && result.exitSummary || {};
    var plan = result && result.exitPlan || { components: [] };
    var summaryEl = byId('tm-c2-exit-summary');
    var versionEl = byId('tm-c2-exit-version');
    var listEl = byId('tm-c2-exit-list');
    var overridesEl = byId('tm-c2-exit-overrides');
    var warningEl = byId('tm-c2-exit-warning');
    var confirm = byId('tm-c2-confirm');
    var components = plan.components || [];
    if (versionEl) versionEl.textContent = result && result.exitPolicyVersion || summary.version || 'sqx-exit-policy-v1';
    if (summaryEl) {
      summaryEl.textContent = components.length
        ? components.length + ' salidas detectadas · ' + (summary.randomized || []).length + ' randomizadas · ' + (summary.disabled || []).length + ' desactivadas'
        : 'Sin salidas detectadas en strategy_Portfolio.xml';
    }
    if (listEl) {
      listEl.innerHTML = components.length ? components.map(function(component) {
        return '<span class="tm-c2-exit-chip" data-action="' + esc(component.action) + '">' +
          esc(component.label) + ' · ' + esc(actionLabel(component.action)) +
          '</span>';
      }).join('') : '<span class="tm-c2-exit-chip">No hay salidas configuradas</span>';
    }
    if (overridesEl) {
      overridesEl.innerHTML = components.map(function(component) {
        return '<div class="tm-c2-exit-row">' +
          '<div><strong>' + esc(component.label) + '</strong><small>' + esc(component.key || component.kind) + ' · valor original: ' + esc(component.value || '-') + '</small></div>' +
          '<select class="filter-select" data-tm-exit-action="' + esc(component.id) + '">' +
            optionHtml('keep', 'Mantener', component.action) +
            optionHtml('disable', 'Desactivar', component.action) +
            optionHtml('randomize', 'Randomizar', component.action) +
            optionHtml('block', 'Bloquear', component.action) +
          '</select>' +
          '<small>' + esc(component.reason || '') + '</small>' +
        '</div>';
      }).join('');
      Array.prototype.forEach.call(overridesEl.querySelectorAll('[data-tm-exit-action]'), function(select) {
        select.addEventListener('change', renderC2TracePreview);
      });
    }
    var blocked = !!(summary.blocked && summary.blocked.length);
    if (warningEl) {
      warningEl.hidden = !blocked;
      warningEl.textContent = blocked
        ? 'Hay salidas activas sin decisión metodológica: ' + summary.blocked.join(', ') + '. Revísalas en avanzado antes de generar.'
        : '';
    }
    if (confirm) confirm.disabled = blocked;
  }

  function optionHtml(value, label, selected) {
    return '<option value="' + esc(value) + '"' + (value === selected ? ' selected' : '') + '>' + esc(label) + '</option>';
  }

  function actionLabel(action) {
    if (action === 'randomize') return 'random';
    if (action === 'disable') return 'off';
    if (action === 'keep') return 'mantener';
    if (action === 'block') return 'requiere decisión';
    return action || '-';
  }

  function setSelectValue(id, value) {
    var select = byId(id);
    if (!select) return;
    select.value = value;
    if (select.value !== value && select.options && select.options.length) {
      select.value = select.options[0].value;
    }
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

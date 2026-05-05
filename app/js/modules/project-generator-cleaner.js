(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var PG = SQX.projectGenerator = SQX.projectGenerator || {};
  var escapeHtml = PG.escapeHtml;

function cleanerTableHtml(files, selectedPaths) {
    var selected = selectedPaths || {};
    if (!files || !files.length) return '';
    return ''
      + '<div class="matrix-wrap" style="max-height:380px;">'
      +   '<table class="cat-table" style="font-size:11px;">'
      +     '<thead><tr>'
      +       '<th style="width:30px;"><input type="checkbox" id="cln-th-check"></th>'
      +       '<th>Archivo</th><th>Asset</th><th>TF</th><th>Dir</th>'
      +       '<th>EAB</th><th>ID</th><th>KB</th>'
      +     '</tr></thead><tbody>'
      +     files.map(function(file) {
              var checked = selected[file.path] ? 'checked' : '';
              var eabClass = file.exit_after_bars_count > 0 ? 'cv-num warn' : 'cv-num pos';
              return ''
                + '<tr>'
                +   '<td><input type="checkbox" class="cln-row-check" data-path="' + escapeHtml(file.path) + '" ' + checked + '></td>'
                +   '<td style="font-family:Consolas,monospace;">' + escapeHtml(file.name) + '</td>'
                +   '<td><strong>' + escapeHtml(file.asset) + '</strong></td>'
                +   '<td>' + escapeHtml(file.timeframe) + '</td>'
                +   '<td>' + escapeHtml(file.direction) + '</td>'
                +   '<td class="' + eabClass + '">' + escapeHtml(file.exit_after_bars_count) + '</td>'
                +   '<td>' + escapeHtml(file.fitness_id) + '</td>'
                +   '<td style="color:var(--text2);">' + escapeHtml(file.size_kb) + '</td>'
                + '</tr>';
            }).join('')
      +     '</tbody></table>'
      + '</div>';
  }

function cleanerSelectedMap(selectedPaths) {
    var selected = {};
    (selectedPaths || []).forEach(function(path) {
      selected[path] = true;
    });
    return selected;
  }

function cleanerSelectedLabel(count) {
    return (count || 0) + ' seleccionadas';
  }

function cleanerScanMessage(result) {
    var data = result || {};
    if (data.ok === false) {
      return {
        text: '✗ ' + (data.error || 'Error escaneando .sqx'),
        color: 'var(--red)',
        actionsDisplay: 'none'
      };
    }
    var count = data.count || 0;
    return {
      text: '✓ ' + count + ' archivos .sqx encontrados',
      color: 'var(--green)',
      actionsDisplay: count > 0 ? 'block' : 'none'
    };
  }

function cleanerMissingDirStatus() {
    return { text: 'Pon una carpeta primero.', color: 'var(--yellow)' };
  }

function cleanerScanningStatus() {
    return { text: '🔍 Escaneando...', color: 'var(--text2)' };
  }

function cleanerErrorStatus(message) {
    return { text: '✗ ' + message, color: 'var(--red)' };
  }

function cleanerNoSelectionStatus() {
    return { text: 'No hay nada seleccionado', level: 'err' };
  }

function cleanerNoActionStatus() {
    return { text: 'Selecciona al menos una acción', level: 'err' };
  }

function cleanerProcessingStatus(count) {
    return { text: 'Procesando ' + (count || 0) + ' archivos...', level: 'info' };
  }

function cleanerPreviewPattern(value) {
    var pattern = String(value || '').trim();
    return pattern || '{asset}_{tf}_{dir}_{id}';
  }

function cleanerPreviewHeader(previews) {
    return 'Preview rename para ' + ((previews || []).length) + ' archivos:';
  }

function cleanerPreviewLines(previews) {
    return (previews || []).map(function(preview) {
      if (preview.error) {
        return {
          text: '  ✗ ' + preview.path + ': ' + preview.error,
          level: 'err'
        };
      }
      return {
        text: '  ' + preview.current + ' → ' + preview.new_name,
        level: 'info'
      };
    });
  }

function cleanerOptions(input) {
    var data = input || {};
    return {
      remove_exit_bars: !!data.removeExitBars,
      rename_institutional: !!data.renameInstitutional,
      rename_pattern: data.renamePattern || '{asset}_{tf}_{dir}_{id}'
    };
  }

function cleanerHasAction(options) {
    return !!(options && (options.remove_exit_bars || options.rename_institutional));
  }

function cleanerConfirmMessage(selectedCount, options) {
    var opts = options || {};
    return 'Procesar ' + selectedCount + ' archivos?\n\n'
      + (opts.remove_exit_bars ? '- Eliminar ExitAfterBars (set 0)\n' : '')
      + (opts.rename_institutional ? '- Renombrar a: ' + opts.rename_pattern + '\n' : '')
      + '\nSe crea backup automatico antes de modificar cada .sqx.';
  }

function cleanerResultSummary(result) {
    var data = result || {};
    return 'Resultado: ' + (data.ok_count || 0) + ' OK · ' + (data.fail_count || 0) + ' FAIL';
  }

function cleanerResultLevel(result) {
    return result && result.fail_count === 0 ? 'ok' : 'err';
  }

function basename(filePath) {
    return String(filePath || '').split(/[\\/]/).pop();
  }

function cleanerResultLines(results) {
    return (results || []).map(function(result) {
      var status = result.ok ? 'OK' : 'FAIL';
      return status + ' ' + basename(result.path) + ' - ' + (result.actions || []).join(', ');
    });
  }

function cleanerResultTrace(selectedCount, result) {
    var data = result || {};
    return {
      title: 'Limpieza SQX completada',
      detail: (selectedCount || 0) + ' archivos · OK ' + (data.ok_count || 0) + ' · FAIL ' + (data.fail_count || 0),
      level: cleanerResultLevel(data)
    };
  }

function cleanerProcessErrorTrace(message) {
    return {
      logText: 'Error procesando: ' + message,
      logLevel: 'err',
      traceTitle: 'Error en limpieza SQX',
      traceDetail: message,
      traceLevel: 'err'
    };
  }

  Object.assign(PG, {
    basename: basename,
    cleanerConfirmMessage: cleanerConfirmMessage,
    cleanerErrorStatus: cleanerErrorStatus,
    cleanerHasAction: cleanerHasAction,
    cleanerMissingDirStatus: cleanerMissingDirStatus,
    cleanerNoActionStatus: cleanerNoActionStatus,
    cleanerNoSelectionStatus: cleanerNoSelectionStatus,
    cleanerOptions: cleanerOptions,
    cleanerPreviewHeader: cleanerPreviewHeader,
    cleanerPreviewLines: cleanerPreviewLines,
    cleanerPreviewPattern: cleanerPreviewPattern,
    cleanerProcessingStatus: cleanerProcessingStatus,
    cleanerProcessErrorTrace: cleanerProcessErrorTrace,
    cleanerResultLevel: cleanerResultLevel,
    cleanerResultLines: cleanerResultLines,
    cleanerResultSummary: cleanerResultSummary,
    cleanerResultTrace: cleanerResultTrace,
    cleanerScanMessage: cleanerScanMessage,
    cleanerScanningStatus: cleanerScanningStatus,
    cleanerSelectedLabel: cleanerSelectedLabel,
    cleanerSelectedMap: cleanerSelectedMap,
    cleanerTableHtml: cleanerTableHtml
  });
})(window);

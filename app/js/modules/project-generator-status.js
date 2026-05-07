(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var PG = SQX.projectGenerator = SQX.projectGenerator || {};

function openOutputDisconnectedStatus() {
    return { logText: 'Backend desconectado', logLevel: 'err' };
  }

function openOutputSuccessStatus(outputDir) {
    return {
      logText: 'Carpeta output abierta',
      logLevel: 'info',
      traceTitle: 'Carpeta output abierta',
      traceDetail: outputDir || '',
      traceLevel: 'info'
    };
  }

function openOutputErrorStatus(message) {
    return {
      logText: 'Error abrir carpeta: ' + message,
      logLevel: 'err',
      traceTitle: 'Error abriendo output',
      traceDetail: message,
      traceLevel: 'err'
    };
  }

function generateOneStartMessage(mining, capa) {
    return 'Generando Mining ' + mining + ' · Capa ' + capa + '…';
  }

function generateOneResult(result, mining, capa) {
    var data = result || {};
    if (data.ok) {
      return {
        logText: '✓ ' + data.filename,
        logLevel: 'ok',
        traceTitle: 'Proyecto generado',
        traceDetail: 'Mining ' + mining + ' · Capa ' + capa + ' · ' + data.filename,
        traceLevel: 'ok'
      };
    }
    var error = data.error || 'fallo';
    return {
      logText: '✗ ' + error,
      logLevel: 'err',
      traceTitle: 'Error generando proyecto',
      traceDetail: 'Mining ' + mining + ' · ' + error,
      traceLevel: 'err'
    };
  }

function generateCustomStartMessage(payload) {
    var data = payload || {};
    var asset = data.asset || 'custom';
    var tf = data.tf || '';
    return 'Generando custom ' + asset + (tf ? ' ' + tf : '') + ' · Capa ' + (data.capa || 1) + '…';
  }

function generateCustomMissingStatus() {
    return {
      text: 'Completa al menos Asset y Timeframe.',
      level: 'err',
      logText: 'Custom libre incompleto: faltan Asset o Timeframe',
      logLevel: 'err'
    };
  }

function generateCustomResult(result, payload) {
    var data = result || {};
    var request = payload || {};
    if (data.ok) {
      return {
        text: 'Generado: ' + data.filename,
        level: 'ok',
        logText: '✓ Custom libre → ' + data.filename,
        logLevel: 'ok',
        traceTitle: 'Custom libre generado',
        traceDetail: (data.project_name || request.name || request.asset || 'custom') + ' · Capa ' + (data.capa || request.capa || 1),
        traceLevel: 'ok'
      };
    }
    var error = data.error || 'fallo';
    return {
      text: 'Error: ' + error,
      level: 'err',
      logText: '✗ Custom libre → ' + error,
      logLevel: 'err',
      traceTitle: 'Error generando custom libre',
      traceDetail: error,
      traceLevel: 'err'
    };
  }

function generateErrorResult(message, title) {
    return {
      logText: '✗ Error: ' + message,
      logLevel: 'err',
      traceTitle: title || 'Error generando proyecto',
      traceDetail: message,
      traceLevel: 'err'
    };
  }

function generateAllConfirmMessage(capa, planCount) {
    var countLabel = planCount || 'todos los';
    return '¿Generar ' + countLabel + ' minings en Capa ' + capa + '? Sobrescribe los existentes en output/.';
  }

function generateAllStartMessage(capa) {
    return 'Generando TODOS · Capa ' + capa + '…';
  }

function generateAllResultSummary(result) {
    var data = result || {};
    var failCount = data.fail_count || 0;
    return {
      text: 'OK: ' + (data.ok_count || 0) + ' · FAIL: ' + failCount,
      level: failCount === 0 ? 'ok' : 'err'
    };
  }

function generateAllTrace(capa, result) {
    var data = result || {};
    var failCount = data.fail_count || 0;
    return {
      title: 'Generacion masiva completada',
      detail: 'Capa ' + capa + ' · OK ' + (data.ok_count || 0) + ' · FAIL ' + failCount,
      level: failCount === 0 ? 'ok' : 'err'
    };
  }

function generateAllResultLines(results) {
    return (results || []).map(function(result) {
      var mining = String(result.mining).padStart(2, '0');
      if (result.ok) {
        return {
          text: '  ✓ M' + mining + ' → ' + result.filename,
          level: 'ok'
        };
      }
      return {
        text: '  ✗ M' + mining + ' → ' + result.error,
        level: 'err'
      };
    });
  }

  Object.assign(PG, {
    generateAllConfirmMessage: generateAllConfirmMessage,
    generateAllResultLines: generateAllResultLines,
    generateAllResultSummary: generateAllResultSummary,
    generateAllStartMessage: generateAllStartMessage,
    generateAllTrace: generateAllTrace,
    generateCustomMissingStatus: generateCustomMissingStatus,
    generateCustomResult: generateCustomResult,
    generateCustomStartMessage: generateCustomStartMessage,
    generateErrorResult: generateErrorResult,
    generateOneResult: generateOneResult,
    generateOneStartMessage: generateOneStartMessage,
    openOutputDisconnectedStatus: openOutputDisconnectedStatus,
    openOutputErrorStatus: openOutputErrorStatus,
    openOutputSuccessStatus: openOutputSuccessStatus
  });
})(window);

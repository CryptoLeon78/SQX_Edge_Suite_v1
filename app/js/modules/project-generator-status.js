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
    generateErrorResult: generateErrorResult,
    generateOneResult: generateOneResult,
    generateOneStartMessage: generateOneStartMessage,
    openOutputDisconnectedStatus: openOutputDisconnectedStatus,
    openOutputErrorStatus: openOutputErrorStatus,
    openOutputSuccessStatus: openOutputSuccessStatus
  });
})(window);

(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[<>&"']/g, function(ch) {
      return ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&#39;' })[ch];
    });
  }

  function trimAction(value, maxLength) {
    var text = value || 'Plan operativo';
    var limit = maxLength || 82;
    return text.length > limit ? text.slice(0, limit - 3).trim() + '...' : text;
  }

  function createTraceItem(title, detail, level, now) {
    var date = now || new Date();
    return {
      title: title || 'Evento',
      detail: detail || '',
      level: level || 'info',
      timeLabel: date.toLocaleString(),
      ts: date.getTime()
    };
  }

  function addTrace(trace, item, maxItems) {
    return [item].concat(trace || []).slice(0, maxItems || 12);
  }

  function traceHtml(trace, escapeFn) {
    var esc = escapeFn || escapeHtml;
    return (trace || []).map(function(item) {
      return (
        '<div class="home-history-item ' + esc(item.level || 'info') + '">' +
          '<span class="home-history-dot"></span>' +
          '<div>' +
            '<div class="home-history-title">' + esc(item.title || 'Evento') + '</div>' +
            '<div class="home-history-meta">' + esc(item.timeLabel || '') + ' · ' + esc(item.detail || '') + '</div>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  function assetCounts(assets) {
    return (assets || []).reduce(function(acc, asset) {
      acc[asset.type] = (acc[asset.type] || 0) + 1;
      return acc;
    }, {});
  }

  function computeHomeModel(input) {
    var data = input || {};
    var assets = data.assets || [];
    var planMinings = data.planMinings || [];
    var strategies = data.strategies || [];
    var strategiesUser = data.strategiesUser || [];
    var priorityProgress = data.priorityProgress || {};
    var pipelineState = data.pipelineState || {};
    var phaseMeta = data.phaseMeta || {};
    var backendState = data.backendState || {};
    var backendMeta = backendState.meta || {};
    var counts = assetCounts(assets);
    var strategyUserCount = Array.isArray(strategiesUser) ? strategiesUser.length : 0;
    var marked = Object.keys(priorityProgress).length;
    var phaseCount = Object.keys(phaseMeta).length;
    var manifestOk = !!(assets.length && planMinings.length && strategies.length);
    var planOk = planMinings.length > 0;
    var strategiesOk = (strategies.length + strategyUserCount) > 0;
    var backendOk = backendState.state === 'up';
    var templatesOk = backendOk && !!(backendMeta.templates_capa1_exists && backendMeta.templates_capa2_exists);
    var sqxPathOk = backendOk && !!backendMeta.sqx_path_set;
    var outputOk = backendOk && !!(backendMeta.output_dir && backendMeta.output_dir_exists);
    var auditItems = [manifestOk, planOk, backendOk, templatesOk, sqxPathOk, outputOk];
    var readiness = Math.round(([manifestOk, planOk, strategiesOk, backendOk].filter(Boolean).length / 4) * 100);

    return {
      assetCount: assets.length,
      assetsSub: (counts.forex || 0) + ' Forex · ' + (counts.index || 0) + ' Indices · ' + (counts.oro || 0) + ' Oro',
      planCount: planMinings.length,
      planSub: phaseCount + ' fases · minings configurados',
      strategyCount: strategies.length + strategyUserCount,
      strategiesSub: strategies.length + ' base · ' + strategyUserCount + ' importadas',
      priorityCount: marked,
      nextAction: trimAction(pipelineState.nextAction),
      backendTitle: backendState.title,
      dataStatus: manifestOk ? 'Manifest v' + (data.manifestVersion || 1) : 'Manifest incompleto',
      readiness: readiness,
      heroStatus: backendOk
        ? (sqxPathOk ? 'API conectada. Plan, manifiestos y generador listos para operar.' : 'API conectada. Falta completar la ruta SQX para generar con seguridad.')
        : 'Manifest activo. Arranca la API local para habilitar generacion, validacion de rutas y limpieza SQX.',
      auditScore: auditItems.filter(Boolean).length + '/' + auditItems.length,
      checks: {
        manifest: manifestOk,
        plan: planOk,
        strategies: strategiesOk,
        backend: backendOk
      },
      states: {
        backend: backendOk ? 'ok' : 'warn',
        data: manifestOk ? 'ok' : 'warn'
      },
      audit: {
        manifest: { ok: manifestOk, detail: assets.length + ' activos · ' + (data.catKeys || []).length + ' categorias' },
        plan: { ok: planOk, detail: phaseCount + ' fases · ' + planMinings.length + ' minings' },
        backend: { ok: backendOk, detail: backendOk ? 'API v' + (backendMeta.version || '?') : 'API no conectada' },
        templates: { ok: templatesOk, detail: backendOk ? (templatesOk ? 'Capa 1 + Capa 2 OK' : 'revisar templates') : 'requiere API' },
        sqx: { ok: sqxPathOk, detail: backendOk ? (sqxPathOk ? 'ruta configurada' : 'ruta pendiente') : 'requiere API' },
        output: { ok: outputOk, detail: backendOk ? (outputOk ? 'carpeta accesible' : 'output pendiente') : 'requiere API' }
      }
    };
  }

  SQX.home = SQX.home || {
    addTrace: addTrace,
    computeHomeModel: computeHomeModel,
    createTraceItem: createTraceItem,
    escapeHtml: escapeHtml,
    traceHtml: traceHtml,
    trimAction: trimAction
  };

  if (SQX.registerModule) {
    SQX.registerModule('home', SQX.home);
  }
})(window);

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

  function setText(doc, id, value) {
    var el = doc.getElementById(id);
    if (el) el.textContent = value;
  }

  function setStateClass(doc, id, state) {
    var el = doc.getElementById(id);
    if (!el) return;
    el.classList.remove('is-ok', 'is-warn');
    el.classList.add(state === 'ok' ? 'is-ok' : 'is-warn');
  }

  function setCheck(doc, id, ok) {
    var el = doc.getElementById(id);
    if (!el) return;
    el.classList.remove('is-ok', 'is-warn');
    el.classList.add(ok ? 'is-ok' : 'is-warn');
  }

  function setAudit(doc, id, item) {
    var row = doc.getElementById(id);
    var detailEl = doc.getElementById(id + '-detail');
    if (row) {
      row.classList.remove('is-ok', 'is-warn');
      row.classList.add(item.ok ? 'is-ok' : 'is-warn');
    }
    if (detailEl) detailEl.textContent = item.detail;
  }

  function applyHomeModel(model, doc) {
    var target = doc || global.document;
    if (!target || !model) return;
    setText(target, 'home-assets-count', model.assetCount);
    setText(target, 'home-assets-sub', model.assetsSub);
    setText(target, 'home-minings-count', model.planCount);
    setText(target, 'home-plan-sub', model.planSub);
    setText(target, 'home-strategies-count', model.strategyCount);
    setText(target, 'home-strategies-sub', model.strategiesSub);
    setText(target, 'home-priority-count', model.priorityCount);
    setText(target, 'home-next-action', model.nextAction);
    setText(target, 'home-backend-status', model.backendTitle);
    setText(target, 'home-data-status', model.dataStatus);
    setText(target, 'home-readiness-score', model.readiness + '%');
    setText(target, 'home-hero-status', model.heroStatus);
    setText(target, 'home-audit-score', model.auditScore);

    var bar = target.getElementById('home-readiness-bar');
    if (bar) bar.style.width = model.readiness + '%';
    setCheck(target, 'home-check-manifest', model.checks.manifest);
    setCheck(target, 'home-check-plan', model.checks.plan);
    setCheck(target, 'home-check-strategies', model.checks.strategies);
    setCheck(target, 'home-check-backend', model.checks.backend);
    setStateClass(target, 'home-backend-status', model.states.backend);
    setStateClass(target, 'home-data-status', model.states.data);
    setAudit(target, 'home-audit-manifest', model.audit.manifest);
    setAudit(target, 'home-audit-plan', model.audit.plan);
    setAudit(target, 'home-audit-backend', model.audit.backend);
    setAudit(target, 'home-audit-templates', model.audit.templates);
    setAudit(target, 'home-audit-sqx', model.audit.sqx);
    setAudit(target, 'home-audit-output', model.audit.output);
  }

  SQX.home = SQX.home || {
    addTrace: addTrace,
    applyHomeModel: applyHomeModel,
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

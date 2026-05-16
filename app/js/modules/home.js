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

  function apiBase() {
    var config = SQX.config || {};
    var raw = config.raw || global.SQX_CONFIG || {};
    if (raw.apiBase) return raw.apiBase().replace(/\/$/, '');
    return 'http://127.0.0.1:5050/api';
  }

  function fetchJson(path, options) {
    if (!global.fetch) {
      return Promise.resolve({ ok: false, error: 'fetch_unavailable', _httpStatus: 0 });
    }
    return global.fetch(apiBase() + path, Object.assign({ credentials: 'include' }, options || {}))
      .then(function(response) {
        return response.json()
          .catch(function() { return {}; })
          .then(function(payload) {
            var data = payload && typeof payload === 'object' ? payload : {};
            data._httpStatus = response.status;
            data._httpOk = response.ok;
            return data;
          });
      })
      .catch(function(err) {
        return { ok: false, error: err && err.message ? err.message : 'request_failed', _httpStatus: 0 };
      });
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

  function remoteReasonLabel(reason) {
    var labels = {
      access_allowed: 'Permiso activo',
      session_access_allowed: 'Sesion remota validada',
      session_created: 'Sesion creada',
      active_entitlement: 'Permiso activo',
      identity_missing: 'Email remoto no detectado',
      entitlement_missing: 'Permiso no encontrado',
      entitlement_expired: 'Permiso expirado',
      entitlement_pending: 'Permiso pendiente',
      entitlement_denied: 'Permiso denegado',
      entitlement_blocked: 'Permiso bloqueado',
      tester_grant_key_required: 'Clave tester pendiente',
      session_missing: 'Sesion de app pendiente',
      session_expired: 'Sesion expirada',
      remote_session_required: 'Sesion remota requerida'
    };
    return labels[reason] || String(reason || 'Pendiente');
  }

  function shortWorkspaceId(id) {
    var value = String(id || '').trim();
    if (!value) return '';
    return value.length > 14 ? value.slice(0, 14) + '...' : value;
  }

  function computeRemoteServiceModel(input) {
    var data = input || {};
    var accessPayload = data.access || {};
    var sessionPayload = data.session || {};
    var workspacePayload = data.workspace || {};
    var healthPayload = data.health || {};
    var access = accessPayload.access || {};
    var sessionAccess = sessionPayload.access || accessPayload.session_access || {};
    var session = sessionPayload.session || accessPayload.session || {};
    var entitlement = sessionPayload.entitlement || accessPayload.entitlement || {};
    var workspace = workspacePayload.workspace || {};
    var accessAllowed = !!(sessionAccess.allowed || access.allowed);
    var authenticated = !!(accessPayload.authenticated || session.active || accessAllowed);
    var workspaceOk = !!(workspacePayload.ok && workspace.id);
    var serverOk = !!healthPayload.ok;
    var serverReady = !!(serverOk && healthPayload.sqx_path_set && healthPayload.data_db_exists && healthPayload.templates_capa1_exists && healthPayload.templates_capa2_exists);
    var reason = (sessionAccess.reason || access.reason || entitlement.reason || accessPayload.error || sessionPayload.error || 'identity_missing');
    var mode = accessPayload.mode || 'local_only';
    var state = accessAllowed && workspaceOk && serverOk ? 'active' : (authenticated || serverOk ? 'pending' : 'warn');
    if (String(reason).indexOf('blocked') >= 0 || String(reason).indexOf('denied') >= 0) state = 'blocked';
    var entitlementKind = entitlement.kind || session.entitlement_kind || '';
    var featureScope = (sessionAccess.feature_scope || access.feature_scope || entitlement.feature_scope || 'none');
    var accessStatus = accessAllowed ? 'Acceso completo activo' : (authenticated ? 'Identidad detectada' : 'Sin sesion remota');
    var accessDetail = accessAllowed
      ? ((entitlementKind ? entitlementKind + ' · ' : '') + featureScope + ' · ' + remoteReasonLabel(reason))
      : (mode === 'local_only' ? 'Modo local interno; el enlace remoto activara email y permiso.' : remoteReasonLabel(reason));
    var workspaceStatus = workspaceOk ? shortWorkspaceId(workspace.id) : 'Pendiente';
    var workspaceDetail = workspaceOk
      ? 'Workspace aislado gestionado por servidor; rutas locales no expuestas.'
      : 'Se crea solo con sesion remota valida y permiso activo.';
    var serverStatus = serverOk ? (serverReady ? 'Recursos listos' : 'Backend disponible') : 'No conectado';
    var serverDetail = serverOk
      ? (serverReady ? 'SQX, data.db y templates verificados en servidor.' : 'API responde; completar recursos servidor antes de operar.')
      : 'Sin conexion con la API del gateway remoto o local.';

    return {
      state: state,
      badgeClass: 'is-' + state,
      badge: state === 'active' ? 'Remote Pro' : (state === 'blocked' ? 'Bloqueado' : (mode === 'local_only' ? 'Local' : 'Pendiente')),
      title: state === 'active' ? 'Acceso remoto listo' : (state === 'blocked' ? 'Acceso bloqueado' : 'Preparado para acceso remoto'),
      detail: state === 'active'
        ? 'Sesion, permiso, workspace y backend estan coordinados para operar desde enlace protegido.'
        : 'El acceso final se valida con email, permiso activo, sesion de app y workspace aislado.',
      items: {
        access: { state: accessAllowed ? 'ok' : (authenticated ? 'pending' : 'warn'), status: accessStatus, detail: accessDetail },
        workspace: { state: workspaceOk ? 'ok' : 'pending', status: workspaceStatus, detail: workspaceDetail },
        server: { state: serverReady ? 'ok' : (serverOk ? 'pending' : 'warn'), status: serverStatus, detail: serverDetail },
        privacy: {
          state: 'ok',
          status: 'Sin instalacion local',
          detail: 'El usuario trabaja por enlace; no se muestran rutas internas, tokens, claves ni carpetas del servidor.'
        }
      },
      raw: {
        accessVersion: accessPayload.version,
        workspaceVersion: workspacePayload.version || workspace.version,
        serverVersion: healthPayload.version
      }
    };
  }

  function setRemoteItem(doc, key, item) {
    var target = doc || global.document;
    var box = target.getElementById('remote-pro-' + key + '-item');
    var status = target.getElementById('remote-pro-' + key + '-status');
    var detail = target.getElementById('remote-pro-' + key + '-detail');
    if (box) {
      box.classList.remove('is-ok', 'is-warn', 'is-pending', 'is-blocked');
      box.classList.add('is-' + (item.state || 'pending'));
    }
    if (status) status.textContent = item.status || 'Pendiente';
    if (detail) detail.textContent = item.detail || '';
  }

  function applyRemoteServiceModel(model, doc) {
    var target = doc || global.document;
    if (!target || !model) return;
    var panel = target.getElementById('remote-pro-panel');
    var badge = target.getElementById('remote-pro-badge');
    setText(target, 'remote-pro-title', model.title);
    setText(target, 'remote-pro-detail', model.detail);
    if (panel) {
      panel.classList.remove('is-active', 'is-warn', 'is-pending', 'is-blocked');
      panel.classList.add('is-' + (model.state || 'pending'));
    }
    if (badge) {
      badge.className = 'remote-pro-badge ' + (model.badgeClass || 'is-pending');
      badge.textContent = model.badge || 'Pendiente';
    }
    setRemoteItem(target, 'access', model.items.access);
    setRemoteItem(target, 'workspace', model.items.workspace);
    setRemoteItem(target, 'server', model.items.server);
    setRemoteItem(target, 'privacy', model.items.privacy);
  }

  function refreshRemoteServiceStatus(doc) {
    var target = doc || global.document;
    applyRemoteServiceModel(computeRemoteServiceModel({}), target);
    return Promise.all([
      fetchJson('/remote/access/status'),
      fetchJson('/remote/session/status'),
      fetchJson('/remote/workspace/status'),
      fetchJson('/health')
    ]).then(function(results) {
      var model = computeRemoteServiceModel({
        access: results[0],
        session: results[1],
        workspace: results[2],
        health: results[3]
      });
      applyRemoteServiceModel(model, target);
      return model;
    });
  }

  function bindRemoteServicePanel(doc) {
    var target = doc || global.document;
    var btn = target && target.getElementById('remote-pro-refresh');
    if (!btn || btn.dataset.boundRemotePro) return false;
    btn.dataset.boundRemotePro = '1';
    btn.addEventListener('click', function() { refreshRemoteServiceStatus(target); });
    return true;
  }

  function initRemoteServicePanel(doc) {
    var target = doc || global.document;
    if (!target || !target.getElementById('remote-pro-panel')) return null;
    bindRemoteServicePanel(target);
    return refreshRemoteServiceStatus(target);
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
    applyRemoteServiceModel: applyRemoteServiceModel,
    apiBase: apiBase,
    bindRemoteServicePanel: bindRemoteServicePanel,
    computeRemoteServiceModel: computeRemoteServiceModel,
    computeHomeModel: computeHomeModel,
    createTraceItem: createTraceItem,
    fetchJson: fetchJson,
    initRemoteServicePanel: initRemoteServicePanel,
    refreshRemoteServiceStatus: refreshRemoteServiceStatus,
    remoteReasonLabel: remoteReasonLabel,
    shortWorkspaceId: shortWorkspaceId,
    escapeHtml: escapeHtml,
    traceHtml: traceHtml,
    trimAction: trimAction
  };

  if (SQX.registerModule) {
    SQX.registerModule('home', SQX.home);
  }
})(window);

(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var REMOTE_WELCOME_DISMISSED_KEY = 'sqx_remote_welcome_dismissed_v1';

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

  function sessionStore() {
    try {
      return global.sessionStorage || null;
    } catch (_err) {
      return null;
    }
  }

  function remoteWelcomeDismissed() {
    var store = sessionStore();
    return !!(store && store.getItem(REMOTE_WELCOME_DISMISSED_KEY) === '1');
  }

  function setRemoteWelcomeDismissed(value) {
    var store = sessionStore();
    if (!store) return;
    if (value) store.setItem(REMOTE_WELCOME_DISMISSED_KEY, '1');
    else store.removeItem(REMOTE_WELCOME_DISMISSED_KEY);
  }

  function computeRemoteServiceModel(input) {
    var data = input || {};
    var accessPayload = data.access || {};
    var sessionPayload = data.session || {};
    var workspacePayload = data.workspace || {};
    var healthPayload = data.health || {};
    var securityPayload = data.security || {};
    var access = accessPayload.access || {};
    var sessionAccess = sessionPayload.access || accessPayload.session_access || {};
    var session = sessionPayload.session || accessPayload.session || {};
    var entitlement = sessionPayload.entitlement || accessPayload.entitlement || {};
    var workspace = workspacePayload.workspace || {};
    var sessionAllowed = !!(sessionAccess.allowed || session.active);
    var accessAllowed = !!(sessionAllowed || access.allowed);
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
    var grantKeyRequired = !!(entitlement.grant_key_required && entitlementKind === 'tester_free' && !sessionAllowed);
    var canCreateSession = !!(authenticated && !sessionAllowed && entitlement.status === 'active');
    var accessStatus = sessionAllowed ? 'Sesion remota activa' : (access.allowed ? 'Permiso detectado' : (authenticated ? 'Identidad detectada' : 'Sin sesion remota'));
    var accessDetail = sessionAllowed
      ? ((entitlementKind ? entitlementKind + ' · ' : '') + featureScope + ' · ' + remoteReasonLabel(reason))
      : (access.allowed ? 'Email y permiso validados; falta crear la sesion de app para abrir workspace.' : null);
    accessDetail = accessDetail
      ? accessDetail
      : (mode === 'local_only' ? 'Modo local interno; el enlace remoto activara email y permiso.' : remoteReasonLabel(reason));
    var workspaceStatus = workspaceOk ? shortWorkspaceId(workspace.id) : 'Pendiente';
    var workspaceDetail = workspaceOk
      ? 'Workspace aislado gestionado por servidor; rutas locales no expuestas.'
      : 'Se crea solo con sesion remota valida y permiso activo.';
    var serverStatus = serverOk ? (serverReady ? 'Recursos listos' : 'Backend disponible') : 'No conectado';
    var serverDetail = serverOk
      ? (serverReady ? 'SQX, data.db y templates verificados en servidor.' : 'API responde; completar recursos servidor antes de operar.')
      : 'Sin conexion con la API del gateway remoto o local.';
    var killSwitch = securityPayload.killSwitch || {};
    var securityOk = !!securityPayload.ok;
    var securityBlocked = !!(killSwitch.active || (securityPayload.revocation || {}).currentSessionRevoked || (securityPayload.blocking || {}).currentIdentityBlocked);
    if (securityBlocked) state = 'blocked';
    var securityStatus = securityBlocked ? 'Control remoto activo' : (securityOk ? 'Protecciones activas' : 'Pendiente');
    var securityDetail = securityBlocked
      ? 'Kill switch, revocacion o bloqueo requieren revision del operador.'
      : (securityOk ? 'Rate limits, revocacion, bloqueo y watermark preparados.' : 'Esperando politica REMOTE-6 del gateway.');
    var watermark = securityPayload.watermark || {};
    var watermarkText = watermark.enabled
      ? ((watermark.label || 'SQX REMOTE PRO') + ' · ' + (watermark.marker || workspaceStatus || 'session'))
      : '';
    var isRemoteMode = mode !== 'local_only';
    var welcomeVisible = !!(isRemoteMode || authenticated || sessionAllowed);
    var welcomePrimaryAction = state === 'active' ? 'enter' : (canCreateSession ? 'login' : 'refresh');
    var welcomePrimaryLabel = state === 'active'
      ? 'Acceso DASHBOARD'
      : (canCreateSession ? 'Acceso DASHBOARD' : 'Actualizar estado');
    var welcomeVerdict = state === 'active'
      ? 'OK todo validado'
      : (canCreateSession ? 'OK identidad validada' : (state === 'blocked' ? 'Acceso bloqueado' : 'Validando acceso'));

    return {
      state: state,
      mode: mode,
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
        security: { state: securityBlocked ? 'blocked' : (securityOk ? 'ok' : 'pending'), status: securityStatus, detail: securityDetail },
        privacy: {
          state: 'ok',
          status: 'Sin instalacion local',
          detail: 'El usuario trabaja por enlace; no se muestran rutas internas, tokens, claves ni carpetas del servidor.'
        }
      },
      raw: {
        accessVersion: accessPayload.version,
        workspaceVersion: workspacePayload.version || workspace.version,
        serverVersion: healthPayload.version,
        securityVersion: securityPayload.version
      },
      sessionLogin: {
        visible: canCreateSession,
        requiresGrantKey: grantKeyRequired,
        disabled: !canCreateSession,
        title: grantKeyRequired ? 'Clave tester requerida' : 'OK identidad validada',
        detail: grantKeyRequired
          ? 'Introduce la clave tester privada para activar la sesion de app y crear el workspace aislado.'
          : (canCreateSession
            ? 'Cloudflare Access y el entitlement estan validados. No necesitas clave tester adicional para abrir la sesion de app.'
            : 'Cuando haya email y permiso activo, aqui aparecera la accion de sesion.'),
        buttonLabel: grantKeyRequired ? 'Validar tester' : 'Acceso DASHBOARD'
      },
      watermark: {
        enabled: !!watermark.enabled,
        text: watermarkText,
        state: securityBlocked ? 'blocked' : 'active'
      },
      welcome: {
        visible: welcomeVisible,
        dismissed: remoteWelcomeDismissed(),
        verdict: welcomeVerdict,
        detail: state === 'active'
          ? 'OK todo validado. Sesion, permiso, workspace y protecciones estan activos. Puedes entrar al dashboard y continuar la metodologia.'
          : (canCreateSession
            ? 'OK identidad validada. Pulsa Acceso DASHBOARD para crear tu sesion de app y abrir el workspace aislado.'
            : 'Antes de operar, SQX Edge valida identidad, permiso activo, sesion de app y workspace aislado.'),
        primaryAction: welcomePrimaryAction,
        primaryLabel: welcomePrimaryLabel,
        trustLabel: 'Ver Trust Center',
        enterLabel: 'Acceso DASHBOARD'
      }
    };
  }

  function setRemoteItem(doc, key, item) {
    var target = doc || global.document;
    var box = target.getElementById('remote-pro-' + key + '-item');
    var status = target.getElementById('remote-pro-' + key + '-status');
    var detail = target.getElementById('remote-pro-' + key + '-detail');
    item = item || {};
    if (box) {
      box.classList.remove('is-ok', 'is-warn', 'is-pending', 'is-blocked');
      box.classList.add('is-' + (item.state || 'pending'));
    }
    if (status) status.textContent = item.status || 'Pendiente';
    if (detail) detail.textContent = item.detail || '';
  }

  function setRemoteSessionLoginState(model, doc) {
    var target = doc || global.document;
    var sessionLogin = (model && model.sessionLogin) || {};
    var box = target.getElementById('remote-session-actions');
    var title = target.getElementById('remote-session-title');
    var detail = target.getElementById('remote-session-login-detail');
    var keyWrap = target.getElementById('remote-session-key-wrap');
    var btn = target.getElementById('remote-session-login');
    if (box) box.hidden = !sessionLogin.visible;
    if (title) title.textContent = sessionLogin.title || 'Crear sesion de app';
    if (detail) detail.textContent = sessionLogin.detail || '';
    if (keyWrap) keyWrap.hidden = !sessionLogin.requiresGrantKey;
    if (btn) {
      btn.disabled = !!sessionLogin.disabled;
      btn.textContent = sessionLogin.buttonLabel || 'Crear sesion remota';
    }
  }

  function setRemoteWelcomeItem(doc, key, item) {
    var target = doc || global.document;
    var box = target.getElementById('remote-welcome-' + key + '-item');
    var status = target.getElementById('remote-welcome-' + key + '-status');
    var detail = target.getElementById('remote-welcome-' + key + '-detail');
    item = item || {};
    if (box) {
      box.classList.remove('is-ok', 'is-warn', 'is-pending', 'is-blocked');
      box.classList.add('is-' + (item.state || 'pending'));
    }
    if (status) status.textContent = item.status || 'Pendiente';
    if (detail) detail.textContent = item.detail || '';
  }

  function applyRemoteWelcomeModel(model, doc) {
    var target = doc || global.document;
    if (!target || !model) return;
    var welcome = model.welcome || {};
    var gate = target.getElementById('remote-welcome-gate');
    var primary = target.getElementById('remote-welcome-primary');
    var enter = target.getElementById('remote-welcome-enter');
    var trust = target.getElementById('remote-welcome-trust-toggle');
    var shouldShow = !!(welcome.visible && !welcome.dismissed);
    if (gate) gate.hidden = !shouldShow;
    setText(target, 'remote-welcome-verdict', welcome.verdict || '');
    setText(target, 'remote-welcome-detail', welcome.detail || '');
    setRemoteWelcomeItem(target, 'access', model.items.access);
    setRemoteWelcomeItem(target, 'workspace', model.items.workspace);
    setRemoteWelcomeItem(target, 'security', model.items.security);
    setRemoteWelcomeItem(target, 'privacy', model.items.privacy);
    if (primary) {
      primary.textContent = welcome.primaryLabel || 'Actualizar estado';
      primary.dataset.remoteWelcomeAction = welcome.primaryAction || 'refresh';
      primary.disabled = model.state === 'blocked';
    }
    if (enter) enter.hidden = true;
    if (trust) trust.textContent = welcome.trustLabel || 'Ver Trust Center';
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
    setRemoteItem(target, 'security', model.items.security);
    setRemoteItem(target, 'privacy', model.items.privacy);
    setRemoteSessionLoginState(model, target);
    applyRemoteWelcomeModel(model, target);
    var watermark = target.getElementById('remote-session-watermark');
    if (watermark) {
      if (model.watermark && model.watermark.enabled && model.watermark.text) {
        watermark.hidden = false;
        watermark.textContent = model.watermark.text;
        watermark.classList.toggle('is-blocked', model.watermark.state === 'blocked');
      } else {
        watermark.hidden = true;
      }
    }
  }

  function refreshRemoteServiceStatus(doc) {
    var target = doc || global.document;
    applyRemoteServiceModel(computeRemoteServiceModel({}), target);
    return Promise.all([
      fetchJson('/remote/access/status'),
      fetchJson('/remote/session/status'),
      fetchJson('/remote/security/status'),
      fetchJson('/health')
    ]).then(function(results) {
      var accessPayload = results[0] || {};
      var sessionPayload = results[1] || {};
      var sessionAccess = sessionPayload.access || {};
      var session = sessionPayload.session || {};
      var canRequestWorkspace = !!(sessionAccess.allowed || session.active);
      var workspacePromise = canRequestWorkspace
        ? fetchJson('/remote/workspace/status')
        : Promise.resolve({
            ok: false,
            error: 'remote_session_pending',
            reason: 'workspace_requires_valid_remote_session',
            _httpStatus: 0
          });
      return workspacePromise.then(function(workspacePayload) {
        var model = computeRemoteServiceModel({
          access: accessPayload,
          session: sessionPayload,
          workspace: workspacePayload,
          security: results[2],
          health: results[3]
        });
        applyRemoteServiceModel(model, target);
        return model;
      });
    });
  }

  function loginRemoteSession(doc, refreshFn) {
    var target = doc || global.document;
    var btn = target && target.getElementById('remote-session-login');
    var detail = target && target.getElementById('remote-session-login-detail');
    var keyInput = target && target.getElementById('remote-session-grant-key');
    var body = {};
    if (keyInput && String(keyInput.value || '').trim()) {
      body.grant_key = String(keyInput.value || '').trim();
    }
    if (btn) btn.disabled = true;
    if (detail) detail.textContent = 'Validando permiso y creando sesion segura...';
    return fetchJson('/remote/session/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    }).then(function(payload) {
      var access = payload && payload.access ? payload.access : {};
      if (payload && payload.ok && access.allowed) {
        if (keyInput) keyInput.value = '';
        if (detail) detail.textContent = 'Sesion remota creada. Preparando workspace aislado...';
        var refresher = typeof refreshFn === 'function' ? refreshFn : refreshRemoteServiceStatus;
        return refresher(target).then(function(model) {
          return { ok: true, login: payload, model: model };
        });
      }
      var reason = (payload && (payload.error || (payload.access || {}).reason || (payload.entitlement || {}).reason)) || 'session_login_failed';
      if (detail) detail.textContent = remoteReasonLabel(reason) + '. Revisa permiso, sesion Cloudflare o entitlement activo.';
      if (btn) btn.disabled = false;
      return { ok: false, login: payload, error: reason };
    });
  }

  function bindRemoteServicePanel(doc) {
    var target = doc || global.document;
    var btn = target && target.getElementById('remote-pro-refresh');
    var loginBtn = target && target.getElementById('remote-session-login');
    var bound = false;
    if (btn && !btn.dataset.boundRemotePro) {
      btn.dataset.boundRemotePro = '1';
      btn.addEventListener('click', function() { refreshRemoteServiceStatus(target); });
      bound = true;
    }
    if (loginBtn && !loginBtn.dataset.boundRemoteLogin) {
      loginBtn.dataset.boundRemoteLogin = '1';
      loginBtn.addEventListener('click', function() { loginRemoteSession(target); });
      bound = true;
    }
    return bound;
  }

  function dismissRemoteWelcomeGate(doc) {
    var target = doc || global.document;
    setRemoteWelcomeDismissed(true);
    var gate = target && target.getElementById('remote-welcome-gate');
    if (gate) gate.hidden = true;
  }

  function bindRemoteWelcomeGate(doc) {
    var target = doc || global.document;
    var primary = target && target.getElementById('remote-welcome-primary');
    var enter = target && target.getElementById('remote-welcome-enter');
    var trust = target && target.getElementById('remote-welcome-trust-toggle');
    var trustPanel = target && target.getElementById('remote-trust-center');
    var bound = false;
    if (primary && !primary.dataset.boundRemoteWelcomePrimary) {
      primary.dataset.boundRemoteWelcomePrimary = '1';
      primary.addEventListener('click', function() {
        var action = primary.dataset.remoteWelcomeAction || 'refresh';
        if (action === 'enter') {
          dismissRemoteWelcomeGate(target);
        } else if (action === 'login') {
          primary.disabled = true;
          loginRemoteSession(target).then(function(result) {
            var model = result && result.model;
            if (result && result.ok && model && model.state === 'active') {
              dismissRemoteWelcomeGate(target);
            } else if (primary) {
              primary.disabled = false;
            }
            return result;
          }).catch(function() {
            if (primary) primary.disabled = false;
          });
        } else {
          refreshRemoteServiceStatus(target);
        }
      });
      bound = true;
    }
    if (enter && !enter.dataset.boundRemoteWelcomeEnter) {
      enter.dataset.boundRemoteWelcomeEnter = '1';
      enter.addEventListener('click', function() { dismissRemoteWelcomeGate(target); });
      bound = true;
    }
    if (trust && trustPanel && !trust.dataset.boundRemoteWelcomeTrust) {
      trust.dataset.boundRemoteWelcomeTrust = '1';
      trust.addEventListener('click', function() {
        trustPanel.hidden = !trustPanel.hidden;
        trust.textContent = trustPanel.hidden ? 'Ver Trust Center' : 'Ocultar Trust Center';
      });
      bound = true;
    }
    return bound;
  }

  function initRemoteServicePanel(doc) {
    var target = doc || global.document;
    if (!target || !target.getElementById('remote-pro-panel')) return null;
    bindRemoteServicePanel(target);
    bindRemoteWelcomeGate(target);
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
    applyRemoteWelcomeModel: applyRemoteWelcomeModel,
    apiBase: apiBase,
    bindRemoteServicePanel: bindRemoteServicePanel,
    bindRemoteWelcomeGate: bindRemoteWelcomeGate,
    computeRemoteServiceModel: computeRemoteServiceModel,
    computeHomeModel: computeHomeModel,
    createTraceItem: createTraceItem,
    dismissRemoteWelcomeGate: dismissRemoteWelcomeGate,
    fetchJson: fetchJson,
    initRemoteServicePanel: initRemoteServicePanel,
    loginRemoteSession: loginRemoteSession,
    refreshRemoteServiceStatus: refreshRemoteServiceStatus,
    remoteReasonLabel: remoteReasonLabel,
    setRemoteSessionLoginState: setRemoteSessionLoginState,
    shortWorkspaceId: shortWorkspaceId,
    escapeHtml: escapeHtml,
    traceHtml: traceHtml,
    trimAction: trimAction
  };

  if (SQX.registerModule) {
    SQX.registerModule('home', SQX.home);
  }
})(window);

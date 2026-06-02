(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var REGISTRY_DATABANK_ORDER = ['Results', 'RETEST 0', 'retest 1', 'TICK', 'MC', 'MC2', 'Sequential', 'Monkey Test', 'Synthetic', 'Syntetic', 'SPP', 'WFM', 'Forward', 'Foward', 'SQX EDGE CORR1 STABILITY', 'SQX EDGE CORR1 TAGGED'];
  var registryReadback = null;
  var basicSelectedFiles = [];

  function byId(id) {
    return global.document.getElementById(id);
  }

  function all(selector, root) {
    return Array.from((root || global.document).querySelectorAll(selector));
  }

  function setText(id, value) {
    var node = byId(id);
    if (node) node.textContent = value == null ? '' : String(value);
  }

  function edgeMode() {
    try {
      var state = SQX.edgeFactory && SQX.edgeFactory.getState ? SQX.edgeFactory.getState() : {};
      return state && state.experienceMode === 'advanced' ? 'advanced' : 'basic';
    } catch (_err) {
      return 'basic';
    }
  }

  function setBasicStatus(message, level) {
    var node = byId('edge-basic-status');
    if (!node) return;
    node.textContent = message || '';
    node.dataset.state = level || 'info';
  }

  function openTool(toolId) {
    if (!toolId) return false;
    if (edgeMode() === 'basic') {
      var flow = byId('edge-basic-flow');
      if (flow && flow.scrollIntoView) flow.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setBasicStatus('Modo básico cerrado: usa la ruta única de selección, descarga, análisis y export C2.', 'warn');
      return false;
    }
    if (SQX.ui && SQX.ui.activateTabById) return SQX.ui.activateTabById(toolId, global.document);
    var panel = byId('tab-' + toolId);
    if (!panel) return false;
    all('.tab-content').forEach(function(content) { content.style.display = 'none'; });
    panel.style.display = 'block';
    return true;
  }

  function renderState() {
    if (!SQX.edgeFactory) return null;
    var state = SQX.edgeFactory.getState();
    var mode = state && state.experienceMode === 'advanced' ? 'advanced' : 'basic';
    var steps = SQX.edgeFactory.visibleStepsForMode ? SQX.edgeFactory.visibleStepsForMode(mode) : SQX.edgeFactory.steps();
    var completed = mode === 'basic' && SQX.edgeFactory.basicCompletedSteps
      ? SQX.edgeFactory.basicCompletedSteps(state)
      : (Array.isArray(state.completedSteps) ? state.completedSteps : []);
    var stageCompleted = Array.isArray(state.completedSteps) ? state.completedSteps : [];
    var next = steps.find(function(step) { return completed.indexOf(step.id) === -1; }) || steps[steps.length - 1];
    var activeStep = state.activeStep || (next && next.id);
    var activeBasicStep = state.activeBasicStep || (next && next.id);
    if (mode === 'basic' && completed.indexOf(activeBasicStep) !== -1 && next) activeBasicStep = next.id;
    var contexts = SQX.edgeFactory.contextSummary ? SQX.edgeFactory.contextSummary(state) : {};
    renderExperienceMode(state);
    all('[data-edge-stage]').forEach(function(card) {
      var id = card.dataset.edgeStage;
      card.classList.toggle('is-complete', stageCompleted.indexOf(id) !== -1);
      card.classList.toggle('is-current', mode === 'advanced' && id === activeStep);
      var box = card.querySelector('input[data-edge-complete]');
      if (box) box.checked = stageCompleted.indexOf(id) !== -1;
      var context = card.querySelector('[data-edge-context]');
      if (context) {
        context.textContent = contexts[id] || 'Sin contexto registrado todavía.';
        context.classList.toggle('is-empty', !contexts[id]);
      }
    });
    all('[data-edge-basic-step]').forEach(function(card) {
      var id = card.dataset.edgeBasicStep;
      card.classList.toggle('is-complete', completed.indexOf(id) !== -1);
      card.classList.toggle('is-current', mode === 'basic' && activeBasicStep === id);
    });
    setText('edge-factory-progress-label', completed.length + ' de ' + steps.length + ' etapas');
    setText('edge-factory-next', completed.length === steps.length ? (mode === 'basic' ? 'Modo básico terminado' : 'Listo para portfolio o nueva iteración') : 'Siguiente: ' + (next ? next.label : 'Punto de partida'));
    var meter = byId('edge-factory-meter-bar');
    if (meter) meter.style.width = Math.round((completed.length / steps.length) * 100) + '%';
    renderSignals(state);
    renderBasicFlowState(state);
    renderBasicTemplateStatus();
    return state;
  }

  function latest(list) {
    return Array.isArray(list) && list.length ? list[0] : null;
  }

  function renderExperienceMode(state) {
    var mode = state && state.experienceMode === 'advanced' ? 'advanced' : 'basic';
    var shell = byId('edge-factory-shell');
    if (shell) {
      shell.classList.toggle('edge-mode-basic', mode === 'basic');
      shell.classList.toggle('edge-mode-advanced', mode === 'advanced');
    }
    if (global.document && global.document.body) {
      global.document.body.classList.toggle('sqx-basic-mode', mode === 'basic');
      global.document.body.classList.toggle('sqx-advanced-mode', mode === 'advanced');
    }
    all('[data-edge-mode]').forEach(function(button) {
      var active = button.dataset.edgeMode === mode;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    setText('edge-factory-mode-label', mode === 'advanced' ? 'Modo avanzado' : 'Modo básico');
    setText(
      'edge-factory-mode-copy',
      mode === 'advanced'
        ? 'Herramientas internas, checks manuales y custom libre visibles.'
        : 'Ruta cerrada: selección, descarga C1+C2, análisis C1 y export C2.'
    );
    if (mode === 'basic' && SQX.ui && SQX.ui.activeTabId && SQX.ui.activateTabById) {
      var activeTab = SQX.ui.activeTabId();
      if (activeTab && activeTab !== 'workflow') {
        setTimeout(function() { SQX.ui.activateTabById('workflow', global.document); }, 0);
      }
    }
    var drawer = byId('edge-tool-drawer');
    var toggle = byId('edge-tools-toggle');
    all('[data-edge-advanced-only]').forEach(function(node) {
      if (mode === 'basic') {
        node.setAttribute('aria-hidden', 'true');
        if (!node.hasAttribute('hidden')) {
          node.dataset.edgeBasicHidden = 'true';
          node.hidden = true;
        }
        try { node.inert = true; } catch (_err) {}
      } else {
        node.removeAttribute('aria-hidden');
        if (node.dataset.edgeBasicHidden === 'true') {
          node.hidden = false;
          delete node.dataset.edgeBasicHidden;
        }
        try { node.inert = false; } catch (_err) {}
      }
    });
    if (mode === 'basic' && drawer && !drawer.hidden) {
      drawer.hidden = true;
      if (toggle) {
        toggle.setAttribute('aria-expanded', 'false');
        toggle.classList.remove('active');
      }
    }
  }

  function setSignal(id, title, detail, ready) {
    var node = global.document.querySelector('[data-edge-signal="' + id + '"]');
    if (!node) return;
    var strong = node.querySelector('strong');
    var small = node.querySelector('small');
    if (strong) strong.textContent = title || 'Pendiente';
    if (small) small.textContent = detail || '';
    node.classList.toggle('is-ready', !!ready);
    node.classList.toggle('is-waiting', !ready);
  }

  function renderSignals(state) {
    state = state || {};
    var card = state.selectedCard || {};
    var c1 = latest(state.capa1Outputs);
    var c1Registry = state.capa1Analysis && state.capa1Analysis.projectKey ? state.capa1Analysis : null;
    var c2Template = state.c2Template || null;
    var portfolio = state.portfolioLab || null;
    var master = state.portfolioMasterContract || null;
    setSignal(
      'asset',
      state.selectedCard ? [card.asset, card.timeframe, card.direction].filter(Boolean).join(' · ') : 'Sin tarjeta',
      state.selectedCard ? (card.blockSetting || 'BlockSetting trazable') : 'Asset · TF · direccion · BlockSetting',
      !!state.selectedCard
    );
    setSignal(
      'capa1',
      c1Registry ? ((c1Registry.forwardCount || c1Registry.passed || 0) + ' Forward · ' + (c1Registry.total || 0) + ' Results') : (c1 ? ((c1.results ? ((c1.results.ok || 0) + '/' + (c1.results.total || 0) + ' OK') : 'Generada')) : 'Pendiente'),
      c1Registry ? c1Registry.projectKey : (c1 && c1.files && c1.files.length ? c1.files.length + ' archivo(s) listos para descarga' : '.cfx y descarga del navegador'),
      !!(c1Registry || c1)
    );
    setSignal(
      'template',
      c2Template ? (c2Template.name || 'Template C2 listo') : 'Pendiente',
      c2Template ? [c2Template.indicatorBase, c2Template.clusterId].filter(Boolean).join(' · ') : 'Indicador · cluster · exit policy',
      !!c2Template
    );
    setSignal(
      'portfolio',
      portfolio && portfolio.total ? (portfolio.winners || 0) + ' ganadores diversos' : 'Pendiente',
      portfolio && portfolio.total
        ? (portfolio.version || 'portfolio-lab-governed-v1') + ' · Master ' + (master ? master.status : 'blocked')
        : 'Shortlist diversa Capa 2',
      !!(portfolio && portfolio.total)
    );
  }

  function cleanToken(value) {
    var text = String(value == null ? '' : value).trim();
    if (text.normalize) text = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    return text.replace(/[^A-Za-z0-9_.-]+/g, '_').replace(/^_+|_+$/g, '').replace(/_{2,}/g, '_');
  }

  function basicDirection(value) {
    var raw = String(value || '').trim().toLowerCase();
    if (raw === 'long' || raw === 'l') return 'long';
    if (raw === 'short' || raw === 's') return 'short';
    return 'both';
  }

  function basicC2Direction(value) {
    var dir = basicDirection(value);
    if (dir === 'long') return 'LONG';
    if (dir === 'short') return 'SHORT';
    return 'BOTH';
  }

  function basicAssets() {
    var manifestAssets = global.SQX_MANIFEST && global.SQX_MANIFEST.assets && global.SQX_MANIFEST.assets.assets;
    return Array.isArray(global.ASSETS) && global.ASSETS.length ? global.ASSETS : (Array.isArray(manifestAssets) ? manifestAssets : []);
  }

  function assetById(assetId) {
    var target = String(assetId || '').trim().toUpperCase();
    return basicAssets().find(function(asset) { return String(asset.id || '').toUpperCase() === target; }) || null;
  }

  function parseTimeframes(value) {
    var seen = {};
    return String(value || '').split(',')
      .map(function(item) { return item.trim().toUpperCase(); })
      .filter(function(item) {
        if (!item || seen[item]) return false;
        seen[item] = true;
        return true;
      });
  }

  function timeframesForAsset(assetId) {
    var asset = assetById(assetId);
    var cats = asset && asset.cats || {};
    var values = [];
    Object.keys(cats).forEach(function(cat) {
      values = values.concat(parseTimeframes(cats[cat] && cats[cat].tf));
    });
    var seen = {};
    values = values.filter(function(tf) {
      if (seen[tf]) return false;
      seen[tf] = true;
      return true;
    });
    return values.length ? values : ['M15', 'M30', 'H1', 'H4', 'D1'];
  }

  function ratingWeight(value) {
    var text = String(value || '');
    return (text.match(/\+/g) || []).length - (text.match(/-/g) || []).length;
  }

  function categoryForSelection(assetId, timeframe) {
    var asset = assetById(assetId);
    var cats = asset && asset.cats || {};
    var tf = String(timeframe || '').toUpperCase();
    var ranked = Object.keys(cats).map(function(cat) {
      var data = cats[cat] || {};
      var tfs = parseTimeframes(data.tf);
      return {
        cat: cat,
        tfMatch: tfs.indexOf(tf) !== -1,
        rating: ratingWeight(data.rating)
      };
    }).sort(function(a, b) {
      return (b.tfMatch ? 1 : 0) - (a.tfMatch ? 1 : 0) || b.rating - a.rating;
    });
    return ranked[0] ? ranked[0].cat : 'tendencia';
  }

  function blocksettingTraceForBasic(assetId, timeframe) {
    var category = categoryForSelection(assetId, timeframe);
    if (typeof global.blockSettingTraceForSelection === 'function') {
      return Object.assign({ family: category }, global.blockSettingTraceForSelection(category, timeframe));
    }
    var resolver = global.SQX_UI && global.SQX_UI.capa1Resolver || {};
    var rules = resolver.families && resolver.families[category] || {};
    var intraday = resolver.intradayTimeframes || ['M5', 'M15', 'M30', 'H1'];
    var blockSetting = intraday.indexOf(String(timeframe || '').toUpperCase()) !== -1 && rules.intraday
      ? rules.intraday
      : (rules.default || 'BS_Tendencia_v6');
    return {
      family: category,
      blocksetting: blockSetting,
      blocksettingTrace: { canonicalId: blockSetting, family: category }
    };
  }

  function populateBasicAssetOptions() {
    var select = byId('edge-basic-asset');
    if (!select || select.__edgeBasicAssetsPopulated) return;
    var assets = basicAssets();
    if (!assets.length) return;
    var current = select.value;
    select.innerHTML = '<option value="">Seleccionar</option>' + assets.map(function(asset) {
      var id = String(asset.id || '').toUpperCase();
      return '<option value="' + escapeHtml(id) + '">' + escapeHtml(id) + '</option>';
    }).join('');
    if (current) select.value = current;
    select.__edgeBasicAssetsPopulated = true;
  }

  function populateBasicTimeframeOptions(assetId, preferred) {
    var select = byId('edge-basic-timeframe');
    if (!select) return;
    var values = timeframesForAsset(assetId);
    var current = preferred || select.value;
    select.innerHTML = '<option value="">Seleccionar</option>' + values.map(function(tf) {
      return '<option value="' + escapeHtml(tf) + '">' + escapeHtml(tf) + '</option>';
    }).join('');
    if (current && values.indexOf(String(current).toUpperCase()) !== -1) select.value = String(current).toUpperCase();
    else if (values.length) select.value = values[0];
  }

  function syncBasicBlockSetting() {
    var asset = String((byId('edge-basic-asset') || {}).value || '').trim().toUpperCase();
    var tf = String((byId('edge-basic-timeframe') || {}).value || '').trim().toUpperCase();
    var trace = blocksettingTraceForBasic(asset, tf);
    var input = byId('edge-basic-blocksetting');
    if (input) input.value = trace.blocksetting || 'BS_Tendencia_v6';
    return trace;
  }

  function renderBasicFlowState(state) {
    var selection = state && (state.basicSelection || state.selectedCard) || {};
    var selectedText = selection.asset && selection.timeframe
      ? [selection.asset, selection.timeframe, selection.direction || selection.dir || 'both', selection.blockSetting].filter(Boolean).join(' · ')
      : 'Sin contexto seleccionado.';
    setText('edge-basic-selection-summary', selectedText);
    var batch = state && state.basicDownloadBatch;
    setText('edge-basic-download-summary', batch && batch.files && batch.files.length
      ? batch.files.map(function(file) { return file.name || file; }).join(' + ')
      : 'Esperando contexto.');
    var files = Array.isArray(state && state.basicFinalFiles) ? state.basicFinalFiles : [];
    setText('edge-basic-file-list', files.length ? files.map(function(file) { return file.name || file; }).join(' · ') : 'Sin archivos seleccionados.');
    setText('edge-basic-finish-summary', state && state.basicFinishedAt ? ('Ruta finalizada: ' + state.basicFinishedAt) : 'La ruta queda lista cuando los templates C2 estan exportados.');
  }

  function readBasicSelection() {
    var state = SQX.edgeFactory && SQX.edgeFactory.getState ? SQX.edgeFactory.getState() : {};
    var card = state.selectedCard || {};
    var asset = String((byId('edge-basic-asset') || {}).value || card.asset || '').trim().toUpperCase();
    var tf = String((byId('edge-basic-timeframe') || {}).value || card.timeframe || '').trim().toUpperCase();
    var dir = basicDirection((byId('edge-basic-direction') || {}).value || card.direction || 'both');
    var trace = syncBasicBlockSetting();
    var bs = String((byId('edge-basic-blocksetting') || {}).value || card.blockSetting || trace.blocksetting || 'BS_Tendencia_v6').trim() || 'BS_Tendencia_v6';
    var name = ['Project', cleanToken(asset || 'ASSET'), cleanToken(tf || 'TF'), cleanToken(bs || 'BS_Custom')].join('_');
    return {
      asset: asset,
      tf: tf,
      dir: dir,
      bs: bs,
      name: name,
      family: trace.family || 'tendencia',
      blocksettingTrace: trace.blocksettingTrace || { canonicalId: bs }
    };
  }

  function confirmBasicSelection() {
    var selection = readBasicSelection();
    if (!selection.asset || !selection.tf) {
      setBasicStatus('Selecciona activo y timeframe.', 'error');
      return false;
    }
    if (SQX.edgeFactory && SQX.edgeFactory.recordBasicSelection) {
      SQX.edgeFactory.recordBasicSelection({
        asset: selection.asset,
        timeframe: selection.tf,
        direction: selection.dir,
        blockSetting: selection.bs,
        blocksettingTrace: selection.blocksettingTrace,
        family: selection.family,
        source: 'edge-basic-flow'
      });
    }
    setText('edge-basic-selection-summary', [selection.asset, selection.tf, selection.dir, selection.bs].join(' · '));
    setBasicStatus('Contexto confirmado: ' + selection.asset + ' ' + selection.tf + ' ' + selection.dir + '.', 'ok');
    renderState();
    return true;
  }

  function stageBasicFiles(files) {
    basicSelectedFiles = Array.prototype.slice.call(files || []);
    var records = basicSelectedFiles.map(function(file) {
      return {
        name: file.name || '',
        size: file.size || 0,
        modified: file.lastModified ? new Date(file.lastModified).toISOString() : ''
      };
    }).filter(function(file) { return file.name; });
    if (SQX.edgeFactory && SQX.edgeFactory.recordBasicFinalFiles) SQX.edgeFactory.recordBasicFinalFiles(records);
    setText('edge-basic-file-list', records.length ? records.map(function(file) { return file.name; }).join(' · ') : 'Sin archivos seleccionados.');
    setBasicStatus(records.length ? (records.length + ' archivo(s) final Capa1 seleccionados.') : 'Selecciona CSV + .sqx finales de Capa1.', records.length ? 'ok' : 'warn');
    renderState();
    return records;
  }

  function basicFetchJson(path, options) {
    var request = options || {};
    return global.fetch(apiBase() + path, {
      method: request.method || 'GET',
      credentials: 'include',
      headers: Object.assign({ 'Content-Type': 'application/json' }, request.headers || {}),
      body: request.body ? JSON.stringify(request.body) : undefined
    }).then(function(response) {
      return response.text().then(function(text) {
        var data = {};
        try { data = text ? JSON.parse(text) : {}; } catch (_err) { data = { error: text || 'invalid_json' }; }
        if (!response.ok || data.ok === false) {
          var error = new Error(data.message || data.error || ('HTTP ' + response.status));
          error.status = response.status;
          error.data = data;
          throw error;
        }
        return data;
      });
    });
  }

  function filenameFromDisposition(headerValue, fallback) {
    var header = String(headerValue || '');
    var utf = header.match(/filename\*=UTF-8''([^;]+)/i);
    if (utf && utf[1]) return decodeURIComponent(utf[1].replace(/"/g, ''));
    var plain = header.match(/filename="?([^";]+)"?/i);
    return plain && plain[1] ? plain[1] : fallback;
  }

  function downloadBlob(blob, filename) {
    var url = URL.createObjectURL(blob);
    var link = global.document.createElement('a');
    link.href = url;
    link.download = filename || 'sqx-edge-download.bin';
    global.document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function downloadBasicFiles(files) {
    var names = (files || []).map(function(file) {
      if (typeof file === 'string') return file;
      return file && (file.name || file.filename || file.file);
    }).map(function(name) { return String(name || '').trim(); }).filter(Boolean);
    if (!names.length) return Promise.resolve(false);
    if (typeof global.pgDownloadOutputBundle === 'function') {
      return Promise.resolve(global.pgDownloadOutputBundle(names)).then(function() { return true; });
    }
    return global.fetch(apiBase() + '/output/download-selected', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ files: names })
    }).then(function(response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.blob().then(function(blob) {
        downloadBlob(blob, filenameFromDisposition(response.headers.get('Content-Disposition'), names.length === 1 ? names[0] : 'sqx-edge-suite-cfx-basic.zip'));
        return true;
      });
    });
  }

  function recordBasicPair(selection, results, files) {
    if (!SQX.edgeFactory) return;
    if (SQX.edgeFactory.recordBasicSelection) {
      SQX.edgeFactory.recordBasicSelection({
        asset: selection.asset,
        timeframe: selection.tf,
        direction: selection.dir,
        blockSetting: selection.bs,
        blocksettingTrace: selection.blocksettingTrace,
        family: selection.family,
        source: 'edge-basic-flow'
      });
    }
    if (SQX.edgeFactory.recordProjectGeneration) {
      var c1 = results && results.capa1;
      var c2 = results && results.capa2;
      if (c1 && c1.ok) {
        SQX.edgeFactory.recordProjectGeneration({
          capa: 1,
          mode: 'basic-pair',
          minings: [],
          results: [c1],
          outputFiles: files || [],
          custom: { name: c1.project_name || selection.name, asset: selection.asset, tf: selection.tf, dir: selection.dir, bs: selection.bs },
          generatedAt: new Date().toISOString()
        });
      }
      if (c2 && c2.ok) {
        SQX.edgeFactory.recordProjectGeneration({
          capa: 2,
          mode: 'basic-pair',
          minings: [],
          results: [c2],
          outputFiles: files || [],
          custom: { name: c2.project_name || selection.name, asset: selection.asset, tf: selection.tf, dir: selection.dir, bs: selection.bs },
          generatedAt: new Date().toISOString()
        });
      }
    }
    if (SQX.edgeFactory.recordBasicDownloadBatch) {
      SQX.edgeFactory.recordBasicDownloadBatch({
        selection: selection,
        files: files || [],
        results: [results && results.capa1, results && results.capa2].filter(Boolean),
        status: files && files.length ? 'ready' : 'pending'
      });
    }
  }

  function generateBasicCustom(selection, capa) {
    return basicFetchJson('/generate-custom', {
      method: 'POST',
      body: {
        name: selection.name,
        asset: selection.asset,
        tf: selection.tf,
        bs: selection.bs,
        dir: selection.dir,
        capa: capa
      }
    });
  }

  function generateBasicPair() {
    var selection = readBasicSelection();
    if (!selection.asset || !selection.tf) {
      setBasicStatus('Selecciona activo y timeframe antes de descargar el par.', 'error');
      return Promise.resolve(false);
    }
    var button = byId('edge-basic-generate-pair');
    if (button) button.disabled = true;
    setBasicStatus('Generando Capa 1 + Capa 2 para ' + selection.asset + ' ' + selection.tf + '...', 'info');
    return basicFetchJson('/generate-pair', {
      method: 'POST',
      body: {
        name: selection.name,
        asset: selection.asset,
        tf: selection.tf,
        bs: selection.bs,
        blocksetting_capa2: selection.bs,
        dir: selection.dir
      }
    }).then(function(response) {
      var results = response.results || {};
      var files = response.files || [];
      recordBasicPair(selection, results, files);
      if (typeof global.pgLoadOutput === 'function') global.pgLoadOutput();
      renderState();
      if (!response.ok) {
        var c1Error = results.capa1 && results.capa1.error;
        var c2Error = results.capa2 && results.capa2.error;
        setBasicStatus('Generación incompleta: ' + (c1Error || c2Error || 'revisa el backend antes de continuar.'), 'error');
        return response;
      }
      return downloadBasicFiles(files).then(function() {
        var names = files.map(function(file) {
          return typeof file === 'string' ? file : (file && (file.name || file.filename || file.file));
        }).filter(Boolean);
        setText('edge-basic-download-summary', names.join(' + '));
        setBasicStatus('Par descargado: ' + names.join(' + '), 'ok');
        renderState();
        return response;
      });
    }).catch(function(error) {
      var payload = error && error.data;
      if (payload && payload.partial) {
        var partialResults = payload.results || {};
        var partialFiles = (payload.files || []).filter(Boolean);
        recordBasicPair(selection, partialResults, partialFiles);
        renderState();
        setBasicStatus('Generación parcial: revisa Capa 2 antes de continuar. ' + (payload.results && payload.results.capa2 && payload.results.capa2.error || error.message), 'error');
        return payload;
      }
      setBasicStatus('No se pudo generar el par: ' + (error && error.message ? error.message : error), 'error');
      return false;
    }).finally(function() {
      if (button) button.disabled = false;
    });
  }

  function templateStrategies() {
    return SQX.templateMaker && SQX.templateMaker.getStrategies ? SQX.templateMaker.getStrategies() : [];
  }

  function basicReadyStrategies() {
    if (!SQX.templateMaker || !SQX.templateMaker.canGenerateC2) return [];
    return templateStrategies().filter(function(strategy) { return SQX.templateMaker.canGenerateC2(strategy); });
  }

  function renderBasicTemplateStatus() {
    var totalNode = byId('edge-basic-total-count');
    var csvNode = byId('edge-basic-csv-count');
    var sqxNode = byId('edge-basic-sqx-count');
    var readyNode = byId('edge-basic-ready-count');
    var select = byId('edge-basic-winner');
    var exportBtn = byId('edge-basic-export-template');
    if (!totalNode && !csvNode && !sqxNode && !readyNode && !select && !exportBtn) return;
    var strategies = templateStrategies();
    var ready = basicReadyStrategies();
    var csvCount = strategies.filter(function(strategy) { return !!(strategy.sources && strategy.sources.csv); }).length;
    var sqxCount = strategies.filter(function(strategy) { return !!(strategy._fileData || strategy.sources && strategy.sources.sqx); }).length;
    setText('edge-basic-total-count', strategies.length);
    setText('edge-basic-csv-count', csvCount);
    setText('edge-basic-sqx-count', sqxCount);
    setText('edge-basic-ready-count', ready.length);
    if (select) {
      var previous = select.value;
      select.innerHTML = '';
      if (!ready.length) {
        var empty = global.document.createElement('option');
        empty.value = '';
        empty.textContent = strategies.length ? 'Sin candidatos listos' : 'Carga resultados Capa 1';
        select.appendChild(empty);
      } else {
        ready.forEach(function(strategy) {
          var option = global.document.createElement('option');
          option.value = String(strategy._id);
          option.textContent = String(strategy['Strategy Name'] || strategy.name || strategy._id);
          select.appendChild(option);
        });
        if (previous && ready.some(function(strategy) { return String(strategy._id) === String(previous); })) {
          select.value = previous;
        }
      }
    }
    if (exportBtn) exportBtn.disabled = ready.length === 0;
  }

  function recordBasicTemplateAnalysis(source) {
    try {
      if (!SQX.edgeFactory || !SQX.edgeFactory.recordTemplateMakerAnalysis) return;
      SQX.edgeFactory.recordTemplateMakerAnalysis({
        source: source || 'edge-basic-flow',
        report: SQX.templateMaker && SQX.templateMaker.getAuditReport ? SQX.templateMaker.getAuditReport() : {},
        diversity: SQX.templateMaker && SQX.templateMaker.getDiversityReport ? SQX.templateMaker.getDiversityReport() : null,
        readyForC2: basicReadyStrategies().length
      });
      if (SQX.edgeFactory.savePatch) SQX.edgeFactory.savePatch({ activeBasicStep: 'basic-export' }, 'edge-factory-basic-analysis');
    } catch (_err) {}
  }

  function ensureTemplateMakerReady() {
    if (!SQX.templateMaker) return Promise.reject(new Error('Template Maker no esta cargado.'));
    if (typeof SQX.templateMaker.init === 'function') return SQX.templateMaker.init();
    return Promise.resolve();
  }

  function handleBasicFiles(files) {
    var list = Array.prototype.slice.call(files || []);
    if (!list.length) list = basicSelectedFiles.slice();
    if (!list.length) {
      setBasicStatus('Selecciona CSV + .sqx finales de Capa1 antes de analizar.', 'warn');
      return Promise.resolve([]);
    }
    setBasicStatus('Analizando ' + list.length + ' archivo(s) de Capa 1...', 'info');
    return ensureTemplateMakerReady().then(function() {
      if (!SQX.templateMaker.ingestFiles) throw new Error('TemplateMaker.ingestFiles no esta disponible.');
      return SQX.templateMaker.ingestFiles(list);
    }).then(function(rows) {
      recordBasicTemplateAnalysis('edge-basic-flow-files');
      renderBasicTemplateStatus();
      renderState();
      setBasicStatus((rows || []).length + ' estrategias reconciliadas. Listas C2: ' + basicReadyStrategies().length + '.', 'ok');
      return rows;
    }).catch(function(error) {
      setBasicStatus('No se pudieron analizar los archivos: ' + (error && error.message ? error.message : error), 'error');
      return [];
    });
  }

  function exportBasicTemplate() {
    var ready = basicReadyStrategies();
    if (!ready.length) {
      setBasicStatus('No hay candidatos listos para exportar templates C2.', 'error');
      return Promise.resolve(false);
    }
    var selection = readBasicSelection();
    setBasicStatus('Exportando ' + ready.length + ' template(s) C2...', 'info');
    var traces = [];
    var jobs = ready.map(function(strategy) {
      var options = {
        asset: selection.asset || strategy.Symbol || strategy.Asset || 'Asset',
        timeframe: selection.tf || strategy.TimeFrame || 'TF',
        direction: basicC2Direction(selection.dir),
        blockSetting: selection.bs || strategy.BlockSetting || 'BS_Custom'
      };
      var trace = SQX.templateMaker.resolveC2Trace ? SQX.templateMaker.resolveC2Trace(strategy, options) : { name: 'template_c2_basic' };
      traces.push(trace);
      return SQX.templateMaker.generateC2Template(strategy, options).then(function(blob) {
        return { blob: blob, trace: trace };
      });
    });
    return Promise.all(jobs).then(function(items) {
      var filenames = [];
      if (items.length === 1 || !global.JSZip) {
        items.forEach(function(item) {
          var itemName = item.trace.name + '.sqx';
          filenames.push(itemName);
          downloadBlob(item.blob, itemName);
        });
      } else {
        var zip = new global.JSZip();
        items.forEach(function(item) {
          var itemName = item.trace.name + '.sqx';
          filenames.push(itemName);
          zip.file(itemName, item.blob);
        });
        zip.file('edge-basic-template-export.json', JSON.stringify({
          version: 'edge-basic-template-export-v1',
          exportedAt: new Date().toISOString(),
          templates: traces
        }, null, 2));
        filenames = ['sqx-edge-basic-c2-templates-' + new Date().toISOString().slice(0, 10) + '.zip'];
        return zip.generateAsync({ type: 'blob' }).then(function(blob) {
          downloadBlob(blob, filenames[0]);
          return filenames;
        });
      }
      return filenames;
    }).then(function(exportFiles) {
      exportFiles = exportFiles && exportFiles.length ? exportFiles : (ready.length === 1
        ? [traces[0].name + '.sqx']
        : ['sqx-edge-basic-c2-templates-' + new Date().toISOString().slice(0, 10) + '.zip']);
      if (SQX.edgeFactory && SQX.edgeFactory.recordC2Template && traces[0]) SQX.edgeFactory.recordC2Template(traces[0]);
      if (SQX.edgeFactory && SQX.edgeFactory.recordBasicTemplateExports) {
        SQX.edgeFactory.recordBasicTemplateExports({ files: exportFiles, templates: traces });
      }
      renderState();
      setBasicStatus('Templates C2 exportados: ' + traces.length + '. Pulsa Finalizar para cerrar.', 'ok');
      return true;
    }).catch(function(error) {
      setBasicStatus('No se pudieron exportar templates C2: ' + (error && error.message ? error.message : error), 'error');
      return false;
    });
  }

  function bindTools() {
    all('[data-edge-tool]').forEach(function(button) {
      if (button.__edgeToolBound) return;
      button.__edgeToolBound = true;
      button.addEventListener('click', function() {
        openTool(button.dataset.edgeTool);
      });
    });
  }

  function bindDrawer() {
    var toggle = byId('edge-tools-toggle');
    var drawer = byId('edge-tool-drawer');
    if (!toggle || !drawer || toggle.__edgeDrawerBound) return;
    toggle.__edgeDrawerBound = true;
    toggle.addEventListener('click', function() {
      var open = drawer.hidden;
      drawer.hidden = !open;
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.classList.toggle('active', open);
    });
  }

  function bindExperienceMode() {
    all('[data-edge-mode]').forEach(function(button) {
      if (button.__edgeModeBound) return;
      button.__edgeModeBound = true;
      button.addEventListener('click', function() {
        if (SQX.edgeFactory && SQX.edgeFactory.setExperienceMode) {
          SQX.edgeFactory.setExperienceMode(button.dataset.edgeMode);
        }
        renderState();
      });
    });
  }

  function bindStepControls() {
    all('[data-edge-step-open]').forEach(function(button) {
      if (button.__edgeStepBound) return;
      button.__edgeStepBound = true;
      button.addEventListener('click', function() {
        if (edgeMode() === 'basic') {
          var flow = byId('edge-basic-flow');
          if (flow && flow.scrollIntoView) flow.scrollIntoView({ behavior: 'smooth', block: 'start' });
          setBasicStatus('Modo básico cerrado: la navegación avanzada queda bloqueada.', 'warn');
          return;
        }
        if (SQX.edgeFactory) SQX.edgeFactory.setActiveStep(button.dataset.edgeStepOpen);
        renderState();
        var target = global.document.querySelector('[data-edge-stage="' + button.dataset.edgeStepOpen + '"]');
        if (target && target.scrollIntoView) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
    });
    all('input[data-edge-complete]').forEach(function(box) {
      if (box.__edgeCompleteBound) return;
      box.__edgeCompleteBound = true;
      box.addEventListener('change', function() {
        if (SQX.edgeFactory) SQX.edgeFactory.completeStep(box.dataset.edgeComplete, box.checked);
        renderState();
      });
    });
  }

  function portfolioSample() {
    return [
      'Strategy Name;Symbol;TimeFrame;Profit factor;Ret/DD Ratio;Max DD %;# of trades;Stability;Winning Percent;SQN;BlockSetting;Indicator;Cluster;Forward Source;Forward Status;Pass Source',
      'AUDCAD_H4_LINEAR_CL01;AUDCAD;H4;1,68;6,2;18;245;0,72;51;2,1;BS_Volatilidad_v6;LinearRegression;CL01;Foward;PASSED;natural',
      'AUDCAD_H1_MACD_CL02;AUDCAD;H1;1,58;5,6;20;260;0,69;50;2,0;BS_Tendencia_v6;MACD;CL02;FOWARD;PASSED;natural',
      'AUDCAD_H4_LINEAR_CL03;AUDCAD;H4;1,61;5,8;19;238;0,68;49;1,9;BS_Volatilidad_v6;LinearRegression;CL03;Forward;PASSED;natural',
      'XAUUSD_H1_KER_CL04;XAUUSD;H1;1,51;4,8;22;318;0,64;48;1,8;BS_Tendencia_v6;KER;CL04;Foward;PASSED;natural',
      'US500_M15_ATR_CL05;US500;M15;1,42;4,1;24;420;0,61;46;1,6;BS_Volumen_v6_intraday_v6;ATR;CL05;Foward;PASSED;natural',
      'EURUSD_M30_RSI_CL06;EURUSD;M30;1,47;4,4;21;310;0,66;52;1,7;BS_MeanReversion_v6;RSI;CL06;Forward;PASSED;natural',
      'GBPJPY_H4_SUPER_CL07;GBPJPY;H4;1,55;5,1;26;205;0,62;49;1,8;BS_Tendencia_v6;SUPER;CL07;Foward;PASSED;natural',
      'USDJPY_H1_ADX_CL08;USDJPY;H1;1,49;4,6;23;286;0,65;51;1,7;BS_Volatilidad_v6;ADX;CL08;Foward;PASSED;natural',
      'NAS100_M15_CHOP_CL09;NAS100;M15;1,44;4,3;25;398;0,63;48;1,6;BS_Volumen_v6_intraday_v6;CHOPPINESS;CL09;Forward;PASSED;natural',
      'GER40_H1_HURST_CL10;GER40;H1;1,46;4,5;24;274;0,67;50;1,7;BS_Tendencia_v6;HURST;CL10;Foward;PASSED;natural',
      'GBPUSD_M30_MACD_CL11;GBPUSD;M30;1,43;4,2;22;302;0,64;49;1,6;BS_Tendencia_v6;MACD;CL11;Foward;PASSED;natural',
      'XAGUSD_H4_LINEAR_CL12;XAGUSD;H4;1,7;6,4;18;250;0,7;52;2,1;BS_Volatilidad_v6;LinearRegression;CL12;Synthetic;FORCED PASS;forced'
    ].join('\n');
  }

  function correlationStabilitySample() {
    var candidates = [
      'strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,blockSetting',
      'AUDCAD_H1_A,AUDCAD,H1,1.55,5.4,18,160,BS_Momentum_v6',
      'AUDCAD_H1_B,AUDCAD,H1,1.48,4.9,20,150,BS_Momentum_v6',
      'AUDCAD_H1_C,AUDCAD,H1,1.42,4.6,21,140,BS_Momentum_v6'
    ].join('\n');
    var isRows = [
      'strategy,isReturnSeries',
      'AUDCAD_H1_A,"0.01|-0.004|0.012|0.006|-0.003|0.009|0.004|-0.002|0.011|0.005|0.003|0.007"',
      'AUDCAD_H1_B,"-0.003|0.008|-0.002|0.010|0.004|-0.001|0.006|0.003|-0.002|0.009|0.004|0.002"',
      'AUDCAD_H1_C,"0.009|-0.003|0.011|0.005|-0.002|0.008|0.003|-0.001|0.010|0.004|0.002|0.006"'
    ].join('\n');
    var oos3Rows = [
      'strategy,oos3ReturnSeries',
      'AUDCAD_H1_A,"0.006|0.004|-0.003|0.009|0.002|-0.001|0.008|0.004|-0.002|0.007|0.003|0.005"',
      'AUDCAD_H1_B,"-0.002|0.006|0.003|-0.001|0.008|0.002|0.004|-0.003|0.006|0.003|-0.001|0.005"',
      'AUDCAD_H1_C,"0.006|0.004|-0.002|0.008|0.002|-0.001|0.007|0.004|-0.002|0.006|0.003|0.005"'
    ].join('\n');
    return { candidates: candidates, isRows: isRows, oos3Rows: oos3Rows };
  }

  function statusLabel(status) {
    return status === 'portfolio' ? 'Portfolio' : (status === 'similar' ? 'Similar' : 'Revisar');
  }

  function readPortfolioSettings() {
    function numberFrom(id, fallback) {
      var node = byId(id);
      var value = node ? Number(String(node.value || '').replace(',', '.')) : NaN;
      return Number.isFinite(value) ? value : fallback;
    }
    return {
      similarityThreshold: numberFrom('edge-portfolio-threshold', 0.78),
      maxWinners: numberFrom('edge-portfolio-max-winners', 12),
      maxPerAsset: numberFrom('edge-portfolio-max-asset', 2),
      maxPerTimeframe: numberFrom('edge-portfolio-max-timeframe', 4),
      maxPerBlockSetting: numberFrom('edge-portfolio-max-blocksetting', 3),
      maxPerIndicator: numberFrom('edge-portfolio-max-indicator', 3),
      maxPerCluster: numberFrom('edge-portfolio-max-cluster', 1)
    };
  }

  function readCorrelationStabilitySettings() {
    function numberFrom(id, fallback) {
      var node = byId(id);
      var value = node ? Number(String(node.value || '').replace(',', '.')) : NaN;
      return Number.isFinite(value) ? value : fallback;
    }
    return {
      maxIsCorrelation: numberFrom('edge-corr-max-is', 0.50),
      maxOos3Correlation: numberFrom('edge-corr-max-oos3', 0.60),
      warnOos3Correlation: numberFrom('edge-corr-warn-oos3', 0.45),
      maxCorrelationDrift: numberFrom('edge-corr-max-drift', 0.25),
      minComparablePoints: numberFrom('edge-corr-min-points', 12)
    };
  }

  function renderCorrelationStability(report) {
    var output = byId('edge-corr-results');
    if (!output) return;
    if (!report) {
      output.innerHTML = '<div class="edge-portfolio-empty"><strong>Sin auditoria CORR1.</strong><span>Aporta candidatos, series IS y series OOS3 comparables.</span></div>';
      return;
    }
    var summary = report.summary || {};
    var methodology = report.methodology || {};
    var labels = report.decisionLabels || {};
    var isCapa1C2 = report.decisionDomain === 'capa1_c2_template_selection';
    var primaryLabel = labels.selected || (isCapa1C2 ? 'C2 template' : 'Portfolio');
    var similarLabel = labels.similar || (isCapa1C2 ? 'Template similar' : 'Similar');
    var heading = isCapa1C2 ? 'Seleccion Capa1 -> Template C2' : 'Portfolio Capa2';
    var pairs = Array.isArray(report.selectedPairAudit) ? report.selectedPairAudit : [];
    output.innerHTML =
      '<div class="edge-portfolio-summary edge-corr-summary">' +
        '<div class="edge-portfolio-stat ' + escapeHtml(summary.status && summary.status.indexOf('blocked') === 0 ? 'review' : 'portfolio') + '"><span>Estado</span><strong>' + escapeHtml(summary.status || 'n/a') + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Input</span><strong>' + escapeHtml(summary.inputRows || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat portfolio"><span>' + escapeHtml(primaryLabel) + '</span><strong>' + escapeHtml(summary.selectedByIs || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat similar"><span>' + escapeHtml(similarLabel) + '</span><strong>' + escapeHtml(summary.similarByIs || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat review"><span>OOS3 break</span><strong>' + escapeHtml(summary.oos3CorrelationBreaks || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat review"><span>Warnings</span><strong>' + escapeHtml(summary.oos3Warnings || 0) + '</strong></div>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>' + escapeHtml(heading) + '</strong>' +
        '<span>' + escapeHtml(methodology.selectionBasis || 'IS_CORR only') + ' · ' + escapeHtml(methodology.auditBasis || 'OOS3_CORR stability confirmation only') + ' · OOS3 elige sustitutos=' + escapeHtml(methodology.oos3MaySelectAlternates === true ? 'true' : 'false') + '.</span>' +
      '</div>' +
      '<table><thead><tr><th>Par</th><th>Corr IS</th><th>Corr OOS3</th><th>Drift</th><th>Estado IS</th><th>Estado OOS3</th><th>Flags</th></tr></thead><tbody>' +
      pairs.map(function(pair) {
        return '<tr>' +
          '<td>' + escapeHtml(pair.leftCandidateId) + ' / ' + escapeHtml(pair.rightCandidateId) + '</td>' +
          '<td>' + escapeHtml(pair.isCorrelation == null ? '' : pair.isCorrelation) + '</td>' +
          '<td>' + escapeHtml(pair.oos3Correlation == null ? '' : pair.oos3Correlation) + '</td>' +
          '<td>' + escapeHtml(pair.correlationDrift == null ? '' : pair.correlationDrift) + '</td>' +
          '<td>' + escapeHtml(pair.isStatus || '') + '</td>' +
          '<td>' + escapeHtml(pair.oos3Status || '') + '</td>' +
          '<td>' + escapeHtml((pair.flags || []).join(' · ')) + '</td>' +
        '</tr>';
      }).join('') +
      '</tbody></table>';
  }

  function renderPortfolioReport(report) {
    var output = byId('edge-portfolio-results');
    if (!output || !report) return;
    if (!report.rows || !report.rows.length) {
      output.innerHTML = '<div class="edge-portfolio-empty"><strong>No hay candidatos Capa 2 para analizar.</strong><span>Carga CSV, pega datos o usa la muestra.</span></div>';
      return;
    }
    var risk = report.riskPlan || {};
    var correlation = report.correlationStatus || {};
    var steps = Array.isArray(report.deploymentSteps) ? report.deploymentSteps : [];
    output.innerHTML =
      '<div class="edge-portfolio-summary">' +
        '<div class="edge-portfolio-stat"><span>Version</span><strong>governed-v1</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Total</span><strong>' + escapeHtml(report.total) + '</strong></div>' +
        '<div class="edge-portfolio-stat portfolio"><span>Portfolio</span><strong>' + escapeHtml(report.winners) + '</strong></div>' +
        '<div class="edge-portfolio-stat similar"><span>Similares</span><strong>' + escapeHtml(report.similar || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat review"><span>Revisar</span><strong>' + escapeHtml(report.review || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat review"><span>Rechazados</span><strong>' + escapeHtml(report.rejected || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Assets</span><strong>' + escapeHtml(report.uniqueAssets || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Rango</span><strong>' + escapeHtml(risk.targetRange || '8-12') + '</strong></div>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Plan de riesgo: ' + escapeHtml(risk.statusLabel || 'riesgo pendiente') + '</strong>' +
        '<span>' + escapeHtml(risk.objective || '8-12 ganadores naturales de Forward/Foward antes de MT5 real') + ' · riesgo base ' + escapeHtml(risk.baseRiskPct || 0.2) + '% · cap inicial ' + escapeHtml(risk.maxInitialRiskPct || 0.3) + '% · agregado ' + escapeHtml(risk.aggregateRisk || 'not_computable') + '.</span>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Correlacion: ' + escapeHtml(correlation.label || 'Similitud operativa, no correlacion de retornos') + '</strong>' +
        '<span>' + escapeHtml(correlation.detail || '') + ' · umbral similitud ' + escapeHtml(correlation.similarityThreshold || (report.settings && report.settings.similarityThreshold)) + '.</span>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Despliegue gradual</strong>' +
        '<span>' + steps.map(function(step) { return escapeHtml(step.label) + ' [' + escapeHtml(step.status) + ']'; }).join(' · ') + '</span>' +
      '</div>' +
      '<table><thead><tr><th>Estado</th><th>Estrategia</th><th>Forward/Foward</th><th>Asset</th><th>TF</th><th>BlockSetting</th><th>Indicador</th><th>PF</th><th>Ret/DD</th><th>DD</th><th>Trades</th><th>Score</th><th>Riesgo</th><th>Relación</th><th>Cluster</th><th>Motivo</th></tr></thead><tbody>' +
      report.rows.map(function(row) {
        return '<tr data-status="' + escapeHtml(row.diversityStatus) + '">' +
          '<td><span class="edge-portfolio-badge ' + escapeHtml(row.diversityStatus) + '">' + escapeHtml(statusLabel(row.diversityStatus)) + '</span></td>' +
          '<td>' + escapeHtml(row.strategy) + '</td>' +
          '<td>' + escapeHtml(row.forwardSource || '') + ' · ' + escapeHtml(row.forwardStatus || '') + '</td>' +
          '<td>' + escapeHtml(row.asset) + '</td>' +
          '<td>' + escapeHtml(row.timeframe) + '</td>' +
          '<td>' + escapeHtml(row.blockSetting) + '</td>' +
          '<td>' + escapeHtml(row.indicator) + '</td>' +
          '<td>' + escapeHtml(row.profitFactor) + '</td>' +
          '<td>' + escapeHtml(row.retDd) + '</td>' +
          '<td>' + escapeHtml(row.maxDd) + '%</td>' +
          '<td>' + escapeHtml(row.trades) + '</td>' +
          '<td>' + escapeHtml(row.score) + '</td>' +
          '<td>' + escapeHtml(row.riskPct == null ? '' : row.riskPct + '%') + '</td>' +
          '<td>' + escapeHtml(row.correlationStatus === 'available' ? ('corr ' + row.correlation) : ('sim ' + row.similarity)) + '</td>' +
          '<td>' + escapeHtml(row.clusterRef) + '</td>' +
          '<td class="edge-portfolio-reason">' + escapeHtml(row.reason || '') + (row.closestStrategy ? ' · ' + escapeHtml(row.closestStrategy) : '') + '</td>' +
        '</tr>';
      }).join('') +
      '</tbody></table>';
  }

  function portfolioMasterSeriesSample(report) {
    var winners = report && Array.isArray(report.rows)
      ? report.rows.filter(function(row) { return row.diversityStatus === 'portfolio'; })
      : [];
    var header = 'strategy,Returns';
    var rows = winners.map(function(row, index) {
      var offset = (index + 1) / 1000;
      var series = [
        0.010 + offset,
        -0.004 + offset,
        0.012 - offset,
        0.006 + offset,
        -0.003 + offset,
        0.009 - offset
      ].map(function(value) { return Math.round(value * 10000) / 10000; }).join('|');
      return '"' + String(row.strategy || row.id || '').replace(/"/g, '""') + '","' + series + '"';
    });
    return [header].concat(rows).join('\n');
  }

  function portfolioMasterForwardSample(report) {
    var winners = report && Array.isArray(report.rows)
      ? report.rows.filter(function(row) { return row.diversityStatus === 'portfolio'; })
      : [];
    var header = 'strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,Source Databank,Forward Status,Pass Source,Example Only';
    var rows = winners.map(function(row) {
      return [
        row.strategy || row.id || '',
        row.asset || '',
        row.timeframe || '',
        row.profitFactor || '',
        row.retDd || '',
        row.maxDd || '',
        row.trades || '',
        row.forwardSource || 'Foward',
        row.forwardStatus || 'PASSED',
        row.passSource || 'natural',
        'true'
      ].map(function(value) {
        return '"' + String(value == null ? '' : value).replace(/"/g, '""') + '"';
      }).join(',');
    });
    return [header].concat(rows).join('\n');
  }

  function portfolioMasterAccountSample() {
    return 'accountModel=demo-forward-review; environment=demo-first; baseCurrency=USD; riskBudgetMode=0.2 pct base, 0.30 pct cap';
  }

  function portfolioMasterBrokerSample() {
    return 'brokerProfile=ECN/low-spread; executionModel=hedging-netting reviewed; leverageMode=broker-context-known; notes=symbol specs reviewed outside browser';
  }

  function statusClass(status) {
    return status === 'ready' || status === 'ready_for_master_review' ? 'portfolio' : 'review';
  }

  function masterDisplayStatus(status) {
    if (status === 'ready_for_master_review') return 'ready';
    if (status === 'blocked_pending_operator_inputs') return 'blocked';
    return status || 'blocked';
  }

  function renderPortfolioMasterContract(contract) {
    var output = byId('edge-master-results');
    if (!output) return;
    if (!contract) {
      output.innerHTML = '<div class="edge-portfolio-empty"><strong>Sin contrato Portfolio Master.</strong><span>Primero calcula Portfolio Lab; despues aporta Forward CSV, equity/returns comparables y contexto publico cuenta/broker.</span></div>';
      return;
    }
    var risk = contract.outputReadback && contract.outputReadback.aggregateRisk ? contract.outputReadback.aggregateRisk : {};
    var intake = contract.inputIntake || {};
    var inputs = Array.isArray(contract.requiredInputs) ? contract.requiredInputs : [];
    var blocked = Array.isArray(contract.blockedReasons) ? contract.blockedReasons : [];
    output.innerHTML =
      '<div class="edge-portfolio-summary">' +
        '<div class="edge-portfolio-stat ' + escapeHtml(statusClass(contract.status)) + '"><span>Estado</span><strong>' + escapeHtml(masterDisplayStatus(contract.status)) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Shortlist</span><strong>' + escapeHtml((contract.outputReadback && contract.outputReadback.shortlistSize) || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Forward</span><strong>' + escapeHtml((contract.inputReadback && contract.inputReadback.forwardCsv && contract.inputReadback.forwardCsv.matchedPortfolioWinners) || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Series</span><strong>' + escapeHtml((contract.inputReadback && contract.inputReadback.comparableSeries && contract.inputReadback.comparableSeries.matchedPortfolioWinners) || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Pares</span><strong>' + escapeHtml(risk.comparablePairs || 0) + '</strong></div>' +
        '<div class="edge-portfolio-stat review"><span>Live</span><strong>' + escapeHtml(contract.liveDeploymentAllowed ? 'SI' : 'NO') + '</strong></div>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Readback: ' + escapeHtml(contract.statusLabel || contract.status) + '</strong>' +
        '<span>' + escapeHtml(intake.version || 'portfolio-master-inputs-pending-v1') + ' · ' + escapeHtml(risk.status || 'unavailable') + ' · no autoriza despliegue real.</span>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Prerrequisitos</strong>' +
        '<span>' + inputs.map(function(item) { return escapeHtml(item.label) + ' [' + escapeHtml(item.status) + ']'; }).join(' · ') + '</span>' +
      '</div>' +
      (blocked.length
        ? '<div class="edge-portfolio-empty"><strong>Bloqueos</strong><span>' + blocked.map(escapeHtml).join(' · ') + '</span></div>'
        : '<div class="edge-portfolio-empty"><strong>Bloqueos</strong><span>Sin bloqueos de contrato. Portfolio Master aun debe recalcular y confirmar antes de operar.</span></div>');
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function(ch) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch];
    });
  }

  function currentPortfolioLab() {
    if (!SQX.edgeFactory) return null;
    var state = SQX.edgeFactory.getState();
    return state.portfolioLab || null;
  }

  function runPortfolioLab() {
    if (!SQX.edgeFactory) return null;
    var input = byId('edge-portfolio-input');
    var report = SQX.edgeFactory.buildPortfolioShortlist(input ? input.value : '', readPortfolioSettings());
    if (SQX.edgeFactory.recordPortfolioLab) {
      SQX.edgeFactory.recordPortfolioLab(report);
    } else {
      SQX.edgeFactory.savePatch({ portfolioLab: report, activeStep: 'portfolio' }, 'portfolio-lab-run');
    }
    renderPortfolioReport(report);
    renderPortfolioMasterContract(SQX.edgeFactory.getState().portfolioMasterContract);
    renderState();
    return report;
  }

  function currentCorrelationStability() {
    if (!SQX.edgeFactory) return null;
    var state = SQX.edgeFactory.getState();
    return state.portfolioCorrelationStability || null;
  }

  function fillCorrelationFromLab() {
    var candidates = byId('edge-corr-candidates-input');
    var portfolioInput = byId('edge-portfolio-input');
    if (candidates && portfolioInput && portfolioInput.value) candidates.value = portfolioInput.value;
    var lab = currentPortfolioLab();
    if (lab && lab.rows && candidates && !candidates.value) {
      candidates.value = [
        'strategy,asset,timeframe,profitFactor,retDd,maxDd,trades,blockSetting'
      ].concat(lab.rows.map(function(row) {
        return [row.strategy, row.asset, row.timeframe, row.profitFactor, row.retDd, row.maxDd, row.trades, row.blockSetting].map(function(value) {
          return '"' + String(value == null ? '' : value).replace(/"/g, '""') + '"';
        }).join(',');
      })).join('\n');
    }
  }

  function runCorrelationStability() {
    var candidates = byId('edge-corr-candidates-input');
    var portfolioInput = byId('edge-portfolio-input');
    var isInput = byId('edge-corr-is-input');
    var oos3Input = byId('edge-corr-oos3-input');
    var output = byId('edge-corr-results');
    var csv = candidates && candidates.value ? candidates.value : (portfolioInput ? portfolioInput.value : '');
    if (output) output.innerHTML = '<div class="edge-portfolio-empty"><strong>Auditando estabilidad.</strong><span>POST /sqx142/portfolio-correlation/stability-audit</span></div>';
    if (!global.fetch) {
      renderCorrelationStability({ ok: false, summary: { status: 'fetch_unavailable' }, selectedPairAudit: [] });
      return Promise.resolve(null);
    }
    return global.fetch(apiBase() + '/sqx142/portfolio-correlation/stability-audit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        csv: csv,
        isSeriesCsv: isInput ? isInput.value : '',
        oos3SeriesCsv: oos3Input ? oos3Input.value : '',
        settings: readCorrelationStabilitySettings(),
        includeCsvExport: true
      })
    })
      .then(function(response) {
        return response.json().catch(function() {
          return { ok: false, version: 'sqx142-portfolio-corr1-stability-audit-v1', summary: { status: 'invalid_json_response' }, selectedPairAudit: [] };
        }).then(function(json) {
          if (!response.ok && !json.error) json.error = 'http_' + response.status;
          return json;
        });
      })
      .then(function(report) {
        if (SQX.edgeFactory && SQX.edgeFactory.recordPortfolioCorrelationStability) {
          SQX.edgeFactory.recordPortfolioCorrelationStability(report);
        } else if (SQX.edgeFactory) {
          SQX.edgeFactory.savePatch({ portfolioCorrelationStability: report }, 'portfolio-corr1-stability');
        }
        renderCorrelationStability(report);
        renderState();
        return report;
      })
      .catch(function(err) {
        var report = { ok: false, version: 'sqx142-portfolio-corr1-stability-audit-v1', summary: { status: err && err.name ? err.name : 'network_error' }, selectedPairAudit: [] };
        renderCorrelationStability(report);
        return report;
      });
  }

  function runRegisteredCorrelationDecision() {
    var key = String(registryProjectKey() || '').trim();
    var output = byId('edge-corr-results');
    syncRegistryInputs(key);
    if (output) output.innerHTML = '<div class="edge-portfolio-empty"><strong>Analizando Capa1 C2 CORR1 registrado.</strong><span>Leyendo SQX local cerrado y series dailyEquity de SQX EDGE CORR1 TAGGED para seleccionar Template C2.</span></div>';
    if (!key || !global.fetch) {
      renderCorrelationStability({ ok: false, summary: { status: key ? 'fetch_unavailable' : 'project_key_missing' }, selectedPairAudit: [] });
      return Promise.resolve(null);
    }
    return global.fetch(apiBase() + '/sqx142/capa1-c2-corr1/registered-decision', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'analyze',
        projectKey: key,
        databank: 'SQX EDGE CORR1 TAGGED',
        settings: readCorrelationStabilitySettings()
      })
    })
      .then(function(response) {
        return response.json().catch(function() {
          return { ok: false, version: 'sqx142-capa1-c2-corr1-registered-decision-v1', report: { summary: { status: 'invalid_json_response' }, selectedPairAudit: [] } };
        }).then(function(json) {
          if (!response.ok && !json.error) json.error = 'http_' + response.status;
          return json;
        });
      })
      .then(function(json) {
        var report = json && json.report ? json.report : { ok: false, summary: { status: json && json.error ? json.error : 'missing_report' }, selectedPairAudit: [] };
        if (SQX.edgeFactory && SQX.edgeFactory.recordC2TemplateSelection) {
          SQX.edgeFactory.recordC2TemplateSelection(report);
        } else if (SQX.edgeFactory) {
          SQX.edgeFactory.savePatch({ c2TemplateSelection: report }, 'capa1-c2-corr1-registered-decision');
        }
        renderCorrelationStability(report);
        renderState();
        return fetchRegistryFunnel(key).then(function() { return json; });
      })
      .catch(function(err) {
        var report = { ok: false, version: 'sqx142-capa1-c2-corr1-registered-decision-v1', decisionDomain: 'capa1_c2_template_selection', summary: { status: err && err.name ? err.name : 'network_error' }, selectedPairAudit: [] };
        renderCorrelationStability(report);
        return report;
      });
  }

  function sampleCorrelationStability() {
    var sample = correlationStabilitySample();
    var candidates = byId('edge-corr-candidates-input');
    var isInput = byId('edge-corr-is-input');
    var oos3Input = byId('edge-corr-oos3-input');
    if (candidates) candidates.value = sample.candidates;
    if (isInput) isInput.value = sample.isRows;
    if (oos3Input) oos3Input.value = sample.oos3Rows;
    return runCorrelationStability();
  }

  function downloadCorrelationStability() {
    var report = currentCorrelationStability();
    if (!report) return;
    var filename = 'sqx-edge-correlation-stability-audit.json';
    try {
      var blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      var link = global.document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
      if (SQX.edgeFactory.recordDownloadRequest) {
        SQX.edgeFactory.recordDownloadRequest({ kind: 'portfolio-correlation-stability', files: [filename] });
      }
    } catch (_err) {
      var output = byId('edge-corr-results');
      if (output) output.textContent = JSON.stringify(report, null, 2);
    }
  }

  function readPortfolioMasterInputs() {
    return {
      forwardCsv: (byId('edge-master-forward-input') || {}).value || '',
      comparableSeriesCsv: (byId('edge-master-series-input') || {}).value || '',
      accountContext: (byId('edge-master-account-input') || {}).value || '',
      brokerContext: (byId('edge-master-broker-input') || {}).value || ''
    };
  }

  function runPortfolioMasterContract() {
    if (!SQX.edgeFactory) return null;
    var payload = Object.assign({
      labReport: currentPortfolioLab()
    }, readPortfolioMasterInputs());
    var state = SQX.edgeFactory.recordPortfolioMasterContract
      ? SQX.edgeFactory.recordPortfolioMasterContract(payload)
      : SQX.edgeFactory.savePatch({ portfolioMasterContract: SQX.edgeFactory.buildPortfolioMasterContract(payload) }, 'portfolio-master-contract-run');
    var contract = state.portfolioMasterContract;
    renderPortfolioMasterContract(contract);
    renderState();
    return contract;
  }

  function samplePortfolioMasterContract() {
    if (!SQX.edgeFactory) return;
    var lab = currentPortfolioLab();
    var portfolioInput = byId('edge-portfolio-input');
    if (!lab || !lab.total) {
      if (portfolioInput && !portfolioInput.value) portfolioInput.value = portfolioSample();
      lab = runPortfolioLab();
    }
    var forward = byId('edge-master-forward-input');
    var series = byId('edge-master-series-input');
    var account = byId('edge-master-account-input');
    var broker = byId('edge-master-broker-input');
    if (forward) forward.value = portfolioMasterForwardSample(lab);
    if (series) series.value = portfolioMasterSeriesSample(lab);
    if (account) account.value = portfolioMasterAccountSample();
    if (broker) broker.value = portfolioMasterBrokerSample();
    runPortfolioMasterContract();
  }

  function downloadPortfolioMasterContract() {
    if (!SQX.edgeFactory) return;
    var state = SQX.edgeFactory.getState();
    var contract = state.portfolioMasterContract || runPortfolioMasterContract();
    if (!contract) return;
    var filename = 'sqx-edge-portfolio-master-contract.json';
    try {
      var blob = new Blob([JSON.stringify(contract, null, 2)], { type: 'application/json' });
      var link = global.document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
      if (SQX.edgeFactory.recordDownloadRequest) {
        SQX.edgeFactory.recordDownloadRequest({ kind: 'portfolio-master-contract', files: [filename] });
      }
    } catch (_err) {
      var output = byId('edge-master-results');
      if (output) output.textContent = JSON.stringify(contract, null, 2);
    }
  }

  function downloadPortfolioReport() {
    if (!SQX.edgeFactory) return;
    var state = SQX.edgeFactory.getState();
    var report = state.portfolioLab || runPortfolioLab();
    if (!report) return;
    if (SQX.edgeFactory.sanitizePortfolioReport) report = SQX.edgeFactory.sanitizePortfolioReport(report);
    var filename = 'sqx-edge-portfolio-lab-summary.json';
    try {
      var blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      var link = global.document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
      if (SQX.edgeFactory.recordDownloadRequest) {
        SQX.edgeFactory.recordDownloadRequest({ kind: 'portfolio-summary', files: [filename] });
      }
    } catch (_err) {
      var output = byId('edge-portfolio-results');
      if (output) output.textContent = JSON.stringify(report, null, 2);
    }
  }

  function downloadPortfolioCsv() {
    if (!SQX.edgeFactory) return;
    var state = SQX.edgeFactory.getState();
    var report = state.portfolioLab || runPortfolioLab();
    if (!report || !report.rows) return;
    if (SQX.edgeFactory.sanitizePortfolioReport) report = SQX.edgeFactory.sanitizePortfolioReport(report);
    var rows = ['decision,strategy,asset,timeframe,forwardSource,forwardStatus,blockSetting,indicator,cluster,score,similarityLabel,reason'];
    report.rows.filter(function(row) { return row.diversityStatus === 'portfolio'; }).forEach(function(row) {
      rows.push([
        row.decision,
        row.strategy,
        row.asset,
        row.timeframe,
        row.forwardSource,
        row.forwardStatus,
        row.blockSetting,
        row.indicator,
        row.clusterRef,
        row.score,
        row.similarityLabel,
        row.reason
      ].map(function(value) {
        return '"' + String(value == null ? '' : value).replace(/"/g, '""') + '"';
      }).join(','));
    });
    var filename = 'sqx-edge-portfolio-shortlist.csv';
    try {
      var blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8' });
      var link = global.document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
      if (SQX.edgeFactory.recordDownloadRequest) {
        SQX.edgeFactory.recordDownloadRequest({ kind: 'portfolio-shortlist-csv', files: [filename] });
      }
    } catch (_err) {
      var output = byId('edge-portfolio-results');
      if (output) output.textContent = rows.join('\n');
    }
  }

  function resetPortfolioLab() {
    var input = byId('edge-portfolio-input');
    var output = byId('edge-portfolio-results');
    var file = byId('edge-portfolio-file');
    var masterForward = byId('edge-master-forward-input');
    var masterSeries = byId('edge-master-series-input');
    var masterAccount = byId('edge-master-account-input');
    var masterBroker = byId('edge-master-broker-input');
    if (input) input.value = '';
    if (file) file.value = '';
    if (masterForward) masterForward.value = '';
    if (masterSeries) masterSeries.value = '';
    if (masterAccount) masterAccount.value = '';
    if (masterBroker) masterBroker.value = '';
    if (output) output.innerHTML = '<div class="edge-portfolio-empty"><strong>Sin lote Capa 2 cargado.</strong><span>Carga CSV, pega datos o usa la muestra para calcular ranking y diversidad.</span></div>';
    renderPortfolioMasterContract(null);
    if (SQX.edgeFactory) SQX.edgeFactory.savePatch({ portfolioLab: null, portfolioMasterContract: null }, 'portfolio-lab-reset');
    renderState();
  }

  function bindPortfolioMaster() {
    var run = byId('edge-master-run');
    var sample = byId('edge-master-sample');
    var exportBtn = byId('edge-master-export');
    var reset = byId('edge-master-reset');
    if (run && !run.__edgeMasterBound) {
      run.__edgeMasterBound = true;
      run.addEventListener('click', runPortfolioMasterContract);
    }
    if (sample && !sample.__edgeMasterBound) {
      sample.__edgeMasterBound = true;
      sample.addEventListener('click', samplePortfolioMasterContract);
    }
    if (exportBtn && !exportBtn.__edgeMasterBound) {
      exportBtn.__edgeMasterBound = true;
      exportBtn.addEventListener('click', downloadPortfolioMasterContract);
    }
    if (reset && !reset.__edgeMasterBound) {
      reset.__edgeMasterBound = true;
      reset.addEventListener('click', function() {
        ['edge-master-forward-input', 'edge-master-series-input', 'edge-master-account-input', 'edge-master-broker-input'].forEach(function(id) {
          var node = byId(id);
          if (node) node.value = '';
        });
        renderPortfolioMasterContract(null);
        if (SQX.edgeFactory) SQX.edgeFactory.savePatch({ portfolioMasterContract: null }, 'portfolio-master-reset');
        renderState();
      });
    }
  }

  function bindPortfolioLab() {
    var sample = byId('edge-portfolio-sample');
    var run = byId('edge-portfolio-run');
    var exportBtn = byId('edge-portfolio-export');
    var exportCsv = byId('edge-portfolio-export-csv');
    var reset = byId('edge-portfolio-reset');
    var file = byId('edge-portfolio-file');
    var input = byId('edge-portfolio-input');
    if (sample && !sample.__edgePortfolioBound) {
      sample.__edgePortfolioBound = true;
      sample.addEventListener('click', function() {
        if (input) input.value = portfolioSample();
        runPortfolioLab();
      });
    }
    if (run && !run.__edgePortfolioBound) {
      run.__edgePortfolioBound = true;
      run.addEventListener('click', runPortfolioLab);
    }
    if (exportBtn && !exportBtn.__edgePortfolioBound) {
      exportBtn.__edgePortfolioBound = true;
      exportBtn.addEventListener('click', downloadPortfolioReport);
    }
    if (exportCsv && !exportCsv.__edgePortfolioBound) {
      exportCsv.__edgePortfolioBound = true;
      exportCsv.addEventListener('click', downloadPortfolioCsv);
    }
    if (reset && !reset.__edgePortfolioBound) {
      reset.__edgePortfolioBound = true;
      reset.addEventListener('click', resetPortfolioLab);
    }
    if (file && !file.__edgePortfolioBound) {
      file.__edgePortfolioBound = true;
      file.addEventListener('change', function() {
        var selected = file.files && file.files[0];
        if (!selected || !input) return;
        var reader = new FileReader();
        reader.onload = function() {
          input.value = String(reader.result || '');
          runPortfolioLab();
        };
        reader.readAsText(selected);
      });
    }
  }

  function bindCorrelationStability() {
    var fromLab = byId('edge-corr-from-lab');
    var registered = byId('edge-corr-registered');
    var sample = byId('edge-corr-sample');
    var run = byId('edge-corr-run');
    var exportBtn = byId('edge-corr-export');
    if (fromLab && !fromLab.__edgeCorrBound) {
      fromLab.__edgeCorrBound = true;
      fromLab.addEventListener('click', fillCorrelationFromLab);
    }
    if (registered && !registered.__edgeCorrBound) {
      registered.__edgeCorrBound = true;
      registered.addEventListener('click', runRegisteredCorrelationDecision);
    }
    if (sample && !sample.__edgeCorrBound) {
      sample.__edgeCorrBound = true;
      sample.addEventListener('click', sampleCorrelationStability);
    }
    if (run && !run.__edgeCorrBound) {
      run.__edgeCorrBound = true;
      run.addEventListener('click', runCorrelationStability);
    }
    if (exportBtn && !exportBtn.__edgeCorrBound) {
      exportBtn.__edgeCorrBound = true;
      exportBtn.addEventListener('click', downloadCorrelationStability);
    }
    renderCorrelationStability(currentCorrelationStability());
  }

  function backportOperationSelect() {
    return byId('edge-backport-operation');
  }

  function currentBackportOperation() {
    if (!SQX.edgeFactory || !SQX.edgeFactory.backportOperatorOperation) return null;
    var select = backportOperationSelect();
    return SQX.edgeFactory.backportOperatorOperation(select ? select.value : 'mcp-status');
  }

  function readBackportOptions() {
    return {
      asset: (byId('edge-backport-asset') || {}).value || '',
      timeframe: (byId('edge-backport-timeframe') || {}).value || '',
      maxCorrelation: (byId('edge-backport-max-correlation') || {}).value || '',
      simulations: (byId('edge-backport-simulations') || {}).value || '',
      minBars: (byId('edge-backport-min-bars') || {}).value || ''
    };
  }

  function apiBase() {
    try {
      if (global.SQX_CONFIG && typeof global.SQX_CONFIG.apiBase === 'function') {
        return String(global.SQX_CONFIG.apiBase() || '/api').replace(/\/$/, '');
      }
    } catch (_err) {}
    return '/api';
  }

  function registryProjectKey() {
    var input = byId('edge-registry-project-key') || byId('ps-registry-project-key');
    if (input && input.value) return String(input.value).trim();
    var state = SQX.edgeFactory && SQX.edgeFactory.getState ? SQX.edgeFactory.getState() : {};
    return state && state.capa1Analysis ? String(state.capa1Analysis.projectKey || '').trim() : '';
  }

  function syncRegistryInputs(value) {
    ['edge-registry-project-key', 'ps-registry-project-key'].forEach(function(id) {
      var input = byId(id);
      if (input && value && input.value !== value) input.value = value;
    });
  }

  function registryProjectFromPayload(payload) {
    var projects = payload && Array.isArray(payload.projects) ? payload.projects : [];
    return projects[0] || null;
  }

  function registryDatabanks(project) {
    var rows = Array.isArray(project && project.databanks) ? project.databanks : [];
    var byName = {};
    rows.forEach(function(row) { byName[String(row.databank || '').toLowerCase()] = row; });
    var ordered = REGISTRY_DATABANK_ORDER.map(function(name) {
      return byName[name.toLowerCase()] || { databank: name, row_count: 0, source_kind: 'pending' };
    });
    rows.forEach(function(row) {
      var key = String(row.databank || '').toLowerCase();
      if (!REGISTRY_DATABANK_ORDER.some(function(name) { return name.toLowerCase() === key; })) ordered.push(row);
    });
    return ordered;
  }

  function registrySummaryText(project) {
    if (!project) return 'Esperando custom project registrado.';
    var rows = registryDatabanks(project);
    var byName = {};
    rows.forEach(function(row) { byName[String(row.databank || '').toLowerCase()] = row; });
    var results = byName.results ? Number(byName.results.row_count || 0) : 0;
    var forward = byName.foward || byName.forward;
    var spp = byName.spp;
    var wfm = byName.wfm;
    return [
      project.projectKey,
      [project.asset, project.timeframe, project.direction, project.blocksettingFamily].filter(Boolean).join(' · '),
      'Results ' + results,
      'Forward ' + (forward ? Number(forward.row_count || 0) : 0),
      'SPP ' + (spp ? Number(spp.row_count || 0) : 0),
      'WFM ' + (wfm ? Number(wfm.row_count || 0) : 0)
    ].filter(Boolean).join(' · ');
  }

  function corr2BackupId() {
    var input = byId('edge-corr2-backup-id') || byId('ps-corr2-backup-id');
    return input && input.value ? String(input.value).trim() : '';
  }

  function syncCorr2BackupId(value) {
    ['edge-corr2-backup-id', 'ps-corr2-backup-id'].forEach(function(id) {
      var input = byId(id);
      if (input && value && input.value !== value) input.value = value;
    });
  }

  function renderCorr2Status(report, message) {
    report = report || null;
    var cfx = report && (report.after || report.cfx || (report.status && report.status.cfx) || {});
    var expected = report && (report.expected || (report.status && report.status.expected) || {});
    var integrated = cfx && cfx.corr2Integrated;
    var backup = report && report.backupId;
    if (backup) syncCorr2BackupId(backup);
    var state = report && report.ok === false ? (report.error || 'Error') : (message || (integrated ? 'Integrado' : 'Pendiente'));
    var summary = report
      ? [
          'Capa1 C2 CORR2 ' + (integrated ? 'integrado' : 'no integrado'),
          ((report.actual || {}).sourceDatabank || expected.sourceDatabank) ? ('Input ' + ((report.actual || {}).sourceDatabank || expected.sourceDatabank)) : 'Input Forward',
          expected.stabilityDatabank ? ('Output ' + expected.stabilityDatabank) : 'Output stability',
          backup ? ('Backup ' + backup) : ''
        ].filter(Boolean).join(' · ')
      : 'Capa1 C2 CORR2 pendiente de preflight.';
    ['edge-corr2-status', 'ps-corr2-status'].forEach(function(id) { setText(id, state); });
    ['edge-corr2-summary', 'ps-corr2-summary'].forEach(function(id) { setText(id, summary); });
  }

  function renderRegistryPanel(payload, message) {
    var project = registryProjectFromPayload(payload);
    var summary = registrySummaryText(project);
    var status = project ? 'Registrado' : (message || 'Sin lectura');
    syncRegistryInputs(project ? project.projectKey : registryProjectKey());
    ['edge-registry-status', 'ps-registry-status'].forEach(function(id) { setText(id, status); });
    ['edge-registry-summary', 'ps-registry-summary'].forEach(function(id) { setText(id, summary); });
    ['edge-registry-funnel', 'ps-registry-funnel'].forEach(function(id) {
      var target = byId(id);
      if (!target) return;
      if (!project) {
        target.innerHTML = '<div class="edge-registry-empty">No hay embudo registrado para este custom.</div>';
        return;
      }
      var rows = registryDatabanks(project);
      var max = rows.reduce(function(acc, row) { return Math.max(acc, Number(row.row_count || 0)); }, 0) || 1;
      target.innerHTML = rows.map(function(row, index) {
        var count = Number(row.row_count || 0);
        var pct = Math.max(2, Math.round((count / max) * 100));
        var finalNode = String(row.databank || '').toLowerCase() === 'foward' || String(row.databank || '').toLowerCase() === 'forward';
        return '<div class="edge-registry-node ' + (count ? 'is-recorded' : 'is-empty') + (finalNode ? ' is-final' : '') + '">' +
          '<span class="edge-registry-order">' + escapeHtml(index + 1) + '</span>' +
          '<strong>' + escapeHtml(row.databank || '') + '</strong>' +
          '<div class="edge-registry-bar"><i style="width:' + escapeHtml(pct) + '%"></i></div>' +
          '<em>' + escapeHtml(count) + '</em>' +
        '</div>';
      }).join('');
    });
  }

  function corr2LocalProject(action) {
    var key = String(registryProjectKey() || '').trim();
    syncRegistryInputs(key);
    if (!key || !global.fetch) {
      renderCorr2Status(null, key ? 'Fetch no disponible' : 'Sin custom');
      return Promise.resolve(null);
    }
    var payload = { action: action || 'status', projectKey: key };
    if (payload.action === 'rollback') payload.backupId = corr2BackupId();
    renderCorr2Status(null, payload.action === 'apply' ? 'Parcheando' : 'Consultando');
    return global.fetch(apiBase() + '/sqx142/capa1-c2-corr2/local-project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function(response) { return response.json().then(function(json) { if (!response.ok) json.ok = false; return json; }); })
      .then(function(json) {
        renderCorr2Status(json, json && json.ok === false ? (json.error || 'Error') : (payload.action === 'apply' ? 'Integrado' : payload.action === 'record' ? 'Registrado' : payload.action));
        if (payload.action === 'apply' || payload.action === 'rollback' || payload.action === 'record') {
          return scanRegistryProject().then(function() { return json; });
        }
        return json;
      })
      .catch(function(err) {
        renderCorr2Status({ ok: false, error: err && err.name ? err.name : 'network_error' }, 'Error');
        return null;
      });
  }

  function fetchRegistryFunnel(projectKey) {
    var key = String(projectKey || registryProjectKey() || '').trim();
    syncRegistryInputs(key);
    if (!key) {
      renderRegistryPanel(null, 'Sin custom');
      return Promise.resolve(null);
    }
    renderRegistryPanel(null, 'Consultando');
    if (!global.fetch) {
      renderRegistryPanel(null, 'Fetch no disponible');
      return Promise.resolve(null);
    }
    return global.fetch(apiBase() + '/sqx142/mining-registry/funnel?projectKey=' + encodeURIComponent(key))
      .then(function(response) { return response.json().then(function(json) { if (!response.ok) json.ok = false; return json; }); })
      .then(function(json) {
        registryReadback = json;
        renderRegistryPanel(json, json && json.ok === false ? (json.error || 'Error') : 'Registrado');
        return json;
      })
      .catch(function(err) {
        renderRegistryPanel(null, err && err.name ? err.name : 'Error de red');
        return null;
      });
  }

  function scanRegistryProject() {
    var key = String(registryProjectKey() || '').trim();
    syncRegistryInputs(key);
    if (!key || !global.fetch) return fetchRegistryFunnel(key);
    renderRegistryPanel(null, 'Actualizando');
    return global.fetch(apiBase() + '/sqx142/mining-registry/scan-project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ projectKey: key, maxSqxParse: 300 })
    })
      .then(function(response) { return response.json().then(function(json) { if (!response.ok) json.ok = false; return json; }); })
      .then(function(json) {
        registryReadback = json && json.funnel ? json.funnel : json;
        renderRegistryPanel(registryReadback, json && json.ok === false ? (json.error || 'Error') : 'Actualizado');
        return registryReadback;
      })
      .catch(function(err) {
        renderRegistryPanel(null, err && err.name ? err.name : 'Error de red');
        return null;
      });
  }

  function applyRegistryProject(skipFetch) {
    var payload = registryReadback;
    var project = registryProjectFromPayload(payload);
    if (!project && !skipFetch) return fetchRegistryFunnel(registryProjectKey()).then(function() { return applyRegistryProject(true); });
    if (!project) {
      renderRegistryPanel(null, 'Sin embudo');
      return null;
    }
    if (SQX.edgeFactory && SQX.edgeFactory.recordMiningRegistryFunnel) {
      SQX.edgeFactory.recordMiningRegistryFunnel(project);
      renderState();
    }
    renderRegistryPanel(payload, 'Aplicado');
    return project;
  }

  function bindMiningRegistryPanel() {
    [
      ['edge-registry-load', fetchRegistryFunnel],
      ['ps-registry-load', fetchRegistryFunnel],
      ['edge-registry-scan', scanRegistryProject],
      ['ps-registry-scan', scanRegistryProject],
      ['edge-registry-apply', applyRegistryProject],
      ['ps-registry-apply', applyRegistryProject],
      ['edge-corr2-status-btn', function() { return corr2LocalProject('status'); }],
      ['ps-corr2-status-btn', function() { return corr2LocalProject('status'); }],
      ['edge-corr2-record', function() { return corr2LocalProject('record'); }],
      ['ps-corr2-record', function() { return corr2LocalProject('record'); }],
      ['edge-corr1-analyze', runRegisteredCorrelationDecision],
      ['ps-corr1-analyze', runRegisteredCorrelationDecision],
      ['edge-corr2-plan', function() { return corr2LocalProject('plan'); }],
      ['ps-corr2-plan', function() { return corr2LocalProject('plan'); }],
      ['edge-corr2-apply', function() { return corr2LocalProject('apply'); }],
      ['ps-corr2-apply', function() { return corr2LocalProject('apply'); }],
      ['edge-corr2-rollback', function() { return corr2LocalProject('rollback'); }],
      ['ps-corr2-rollback', function() { return corr2LocalProject('rollback'); }]
    ].forEach(function(pair) {
      var button = byId(pair[0]);
      if (!button || button.__edgeRegistryBound) return;
      button.__edgeRegistryBound = true;
      button.addEventListener('click', function() { pair[1](); });
    });
    ['edge-registry-project-key', 'ps-registry-project-key'].forEach(function(id) {
      var input = byId(id);
      if (!input || input.__edgeRegistryBound) return;
      input.__edgeRegistryBound = true;
      input.addEventListener('change', function() { syncRegistryInputs(input.value); });
    });
    var state = SQX.edgeFactory && SQX.edgeFactory.getState ? SQX.edgeFactory.getState() : {};
    registryReadback = state && state.miningRegistryFunnel ? { ok: true, projects: [state.miningRegistryFunnel] } : registryReadback;
    renderRegistryPanel(registryReadback, registryReadback ? 'Registrado' : 'Sin lectura');
    renderCorr2Status(null, 'Sin preflight C2 CORR1');
  }

  function renderBackportOperationMode() {
    var operation = currentBackportOperation();
    var input = byId('edge-backport-input');
    var run = byId('edge-backport-run');
    var sample = byId('edge-backport-sample');
    var sqxTag = byId('edge-backport-export-sqx-tags');
    var payloadBox = byId('edge-backport-payload-mode');
    if (!operation) return;
    if (input) {
      input.disabled = operation.method === 'GET';
      input.placeholder = operation.method === 'GET'
        ? 'Este modo consulta estado local read-only y no necesita payload.'
        : (operation.id === 'mt5-data-probe'
          ? 'time,open,high,low,close,volume'
          : (operation.id === 'migration-checklist'
            ? 'kind,label,relativePath,operation'
            : 'strategy,asset,timeframe,Source Databank,Forward Status,returnSeries,equitySeries'));
    }
    if (sample) sample.disabled = operation.method === 'GET';
    if (sqxTag) sqxTag.disabled = operation.id !== 'correlation-filter';
    if (run) run.textContent = operation.method === 'GET' ? 'Consultar API' : 'Ejecutar probe';
    if (payloadBox) {
      payloadBox.textContent = operation.method + ' ' + operation.endpoint + ' · ' + operation.expectedVersion;
    }
  }

  function renderBackportResult(summary) {
    var output = byId('edge-backport-results');
    if (!output) return;
    if (!summary) {
      output.innerHTML = '<div class="edge-portfolio-empty"><strong>Sin readback BACKPORT.</strong><span>Selecciona un contrato y ejecuta una consulta local.</span></div>';
      return;
    }
    var raw = summary.raw || {};
    var guards = raw.guards || {};
    var privacy = raw.privacy || {};
    var warnings = Array.isArray(raw.warnings) ? raw.warnings : [];
    var blockers = Array.isArray(raw.blockers) ? raw.blockers : [];
    output.innerHTML =
      '<div class="edge-portfolio-summary edge-backport-summary">' +
        '<div class="edge-portfolio-stat ' + escapeHtml(summary.ok ? 'portfolio' : 'review') + '"><span>Estado</span><strong>' + escapeHtml(summary.status) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Contrato</span><strong>' + escapeHtml(summary.expectedVersion) + '</strong></div>' +
        '<div class="edge-portfolio-stat"><span>Total</span><strong>' + escapeHtml(summary.total) + '</strong></div>' +
        '<div class="edge-portfolio-stat portfolio"><span>OK</span><strong>' + escapeHtml(summary.primaryCount) + '</strong></div>' +
        '<div class="edge-portfolio-stat similar"><span>Review</span><strong>' + escapeHtml(summary.reviewCount) + '</strong></div>' +
        '<div class="edge-portfolio-stat review"><span>Block</span><strong>' + escapeHtml(summary.blockCount) + '</strong></div>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>' + escapeHtml(summary.label) + '</strong>' +
        '<span>' + escapeHtml(summary.method + ' ' + summary.endpoint) + ' · response ' + escapeHtml(summary.responseVersion || 'n/a') + ' · CSV ' + escapeHtml(summary.csvExportAvailable ? 'available' : 'n/a') + ' · SQX Tag ' + escapeHtml(summary.sqxTagCsvAvailable ? 'available' : 'n/a') + '.</span>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Guards</strong>' +
        '<span>SQX runtime started=' + escapeHtml(guards.sqx_runtime_started === true ? 'true' : 'false') +
          ' · data.db write=' + escapeHtml(guards.data_db_write_allowed === true ? 'true' : 'false') +
          ' · user/projects write=' + escapeHtml(guards.user_projects_write_allowed === true ? 'true' : 'false') +
          ' · remote/tester=' + escapeHtml(guards.remote_tester_access === true ? 'true' : 'false') + '</span>' +
      '</div>' +
      '<div class="edge-portfolio-empty">' +
        '<strong>Privacidad</strong>' +
        '<span>local_paths_returned=' + escapeHtml(privacy.local_paths_returned === true ? 'true' : 'false') +
          ' · tokens_returned=' + escapeHtml(privacy.tokens_returned === true ? 'true' : 'false') +
          ' · private_fields_returned=' + escapeHtml(privacy.private_fields_returned === true ? 'true' : 'false') + '</span>' +
      '</div>' +
      (warnings.length || blockers.length
        ? '<div class="edge-portfolio-empty"><strong>Avisos</strong><span>' + warnings.concat(blockers).map(escapeHtml).join(' · ') + '</span></div>'
        : '<div class="edge-portfolio-empty"><strong>Avisos</strong><span>Sin avisos devueltos por el contrato.</span></div>');
  }

  function currentBackportSummary() {
    if (!SQX.edgeFactory) return null;
    var state = SQX.edgeFactory.getState();
    return state.backportOperatorPanel && state.backportOperatorPanel.lastOperation;
  }

  function storeAndRenderBackportResult(operationId, report) {
    var state = SQX.edgeFactory && SQX.edgeFactory.recordBackportOperatorResult
      ? SQX.edgeFactory.recordBackportOperatorResult(operationId, report)
      : null;
    var summary = state && state.backportOperatorPanel
      ? state.backportOperatorPanel.lastOperation
      : (SQX.edgeFactory && SQX.edgeFactory.summarizeBackportOperatorResult ? SQX.edgeFactory.summarizeBackportOperatorResult(operationId, report) : null);
    renderBackportResult(summary);
    renderState();
    return summary;
  }

  function runBackportOperatorPanel() {
    if (!SQX.edgeFactory) return Promise.resolve(null);
    var operation = currentBackportOperation();
    if (!operation) return Promise.resolve(null);
    var output = byId('edge-backport-results');
    var input = byId('edge-backport-input');
    if (output) {
      output.innerHTML = '<div class="edge-portfolio-empty"><strong>Consultando contrato local.</strong><span>' + escapeHtml(operation.method + ' ' + operation.endpoint) + '</span></div>';
    }
    var url = apiBase() + operation.endpoint;
    var request = { method: operation.method, headers: { 'Content-Type': 'application/json' } };
    if (operation.method !== 'GET') {
      request.body = JSON.stringify(SQX.edgeFactory.buildBackportOperatorPayload(operation.id, input ? input.value : '', readBackportOptions()));
    }
    if (!global.fetch) {
      return Promise.resolve(storeAndRenderBackportResult(operation.id, {
        ok: false,
        version: operation.expectedVersion,
        error: 'fetch_unavailable',
        privacy: { local_paths_returned: false, tokens_returned: false, private_fields_returned: false },
        guards: { sqx_runtime_started: false, data_db_write_allowed: false, user_projects_write_allowed: false, remote_tester_access: false }
      }));
    }
    return global.fetch(url, request)
      .then(function(response) {
        return response.json().catch(function() {
          return { ok: false, version: operation.expectedVersion, error: 'invalid_json_response' };
        }).then(function(json) {
          if (!response.ok && !json.error) json.error = 'http_' + response.status;
          return storeAndRenderBackportResult(operation.id, json);
        });
      })
      .catch(function(err) {
        return storeAndRenderBackportResult(operation.id, {
          ok: false,
          version: operation.expectedVersion,
          error: err && err.name ? err.name : 'network_error',
          privacy: { local_paths_returned: false, tokens_returned: false, private_fields_returned: false },
          guards: { sqx_runtime_started: false, data_db_write_allowed: false, user_projects_write_allowed: false, remote_tester_access: false }
        });
      });
  }

  function sampleBackportOperatorPanel() {
    if (!SQX.edgeFactory) return;
    var operation = currentBackportOperation();
    var input = byId('edge-backport-input');
    if (input && operation && operation.method !== 'GET') {
      input.value = SQX.edgeFactory.backportOperatorSample(operation.id);
    }
  }

  function downloadBackportJson() {
    var summary = currentBackportSummary();
    if (!summary) summary = runBackportOperatorPanel();
    if (!summary || summary.then) return;
    var filename = 'sqx-edge-backport-operator-readback.json';
    try {
      var blob = new Blob([JSON.stringify(summary.raw || summary, null, 2)], { type: 'application/json' });
      var link = global.document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
      if (SQX.edgeFactory.recordDownloadRequest) {
        SQX.edgeFactory.recordDownloadRequest({ kind: 'backport-operator-readback', files: [filename] });
      }
    } catch (_err) {
      var output = byId('edge-backport-results');
      if (output) output.textContent = JSON.stringify(summary.raw || summary, null, 2);
    }
  }

  function downloadBackportCsv() {
    var summary = currentBackportSummary();
    if (!summary || !summary.raw || !summary.raw.csvExport) return;
    var filename = 'sqx-edge-backport-operator-export.csv';
    try {
      var blob = new Blob([String(summary.raw.csvExport || '')], { type: 'text/csv;charset=utf-8' });
      var link = global.document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
      if (SQX.edgeFactory.recordDownloadRequest) {
        SQX.edgeFactory.recordDownloadRequest({ kind: 'backport-operator-csv', files: [filename] });
      }
    } catch (_err) {
      var output = byId('edge-backport-results');
      if (output) output.textContent = String(summary.raw.csvExport || '');
    }
  }

  function downloadBackportSqxTagCsv() {
    var summary = currentBackportSummary();
    if (!summary || summary.operationId !== 'correlation-filter' || !summary.raw || !summary.raw.sqxTagCsv) return;
    var filename = 'sqx-edge-correlation-tags.csv';
    try {
      var blob = new Blob([String(summary.raw.sqxTagCsv || '')], { type: 'text/csv;charset=utf-8' });
      var link = global.document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
      if (SQX.edgeFactory.recordDownloadRequest) {
        SQX.edgeFactory.recordDownloadRequest({ kind: 'backport-operator-sqx-tag-csv', files: [filename] });
      }
    } catch (_err) {
      var output = byId('edge-backport-results');
      if (output) output.textContent = String(summary.raw.sqxTagCsv || '');
    }
  }

  function bindBackportOperatorPanel() {
    var select = backportOperationSelect();
    var run = byId('edge-backport-run');
    var sample = byId('edge-backport-sample');
    var exportJson = byId('edge-backport-export-json');
    var exportCsv = byId('edge-backport-export-csv');
    var exportSqxTags = byId('edge-backport-export-sqx-tags');
    var reset = byId('edge-backport-reset');
    if (select && !select.__edgeBackportBound) {
      select.__edgeBackportBound = true;
      select.addEventListener('change', renderBackportOperationMode);
    }
    if (run && !run.__edgeBackportBound) {
      run.__edgeBackportBound = true;
      run.addEventListener('click', runBackportOperatorPanel);
    }
    if (sample && !sample.__edgeBackportBound) {
      sample.__edgeBackportBound = true;
      sample.addEventListener('click', sampleBackportOperatorPanel);
    }
    if (exportJson && !exportJson.__edgeBackportBound) {
      exportJson.__edgeBackportBound = true;
      exportJson.addEventListener('click', downloadBackportJson);
    }
    if (exportCsv && !exportCsv.__edgeBackportBound) {
      exportCsv.__edgeBackportBound = true;
      exportCsv.addEventListener('click', downloadBackportCsv);
    }
    if (exportSqxTags && !exportSqxTags.__edgeBackportBound) {
      exportSqxTags.__edgeBackportBound = true;
      exportSqxTags.addEventListener('click', downloadBackportSqxTagCsv);
    }
    if (reset && !reset.__edgeBackportBound) {
      reset.__edgeBackportBound = true;
      reset.addEventListener('click', function() {
        var input = byId('edge-backport-input');
        if (input) input.value = '';
        if (SQX.edgeFactory) SQX.edgeFactory.savePatch({ backportOperatorPanel: null }, 'ui-integration1-backport-reset');
        renderBackportResult(null);
        renderState();
      });
    }
    renderBackportOperationMode();
    renderBackportResult(currentBackportSummary());
  }

  function bindBasicFlow() {
    populateBasicAssetOptions();
    var generate = byId('edge-basic-generate-pair');
    var saveSelection = byId('edge-basic-save-selection');
    var files = byId('edge-basic-files');
    var analyze = byId('edge-basic-analyze-files');
    var exportBtn = byId('edge-basic-export-template');
    var finish = byId('edge-basic-finish');
    var state = SQX.edgeFactory && SQX.edgeFactory.getState ? SQX.edgeFactory.getState() : {};
    var card = state.basicSelection || state.selectedCard || {};
    var assetInput = byId('edge-basic-asset');
    var tfInput = byId('edge-basic-timeframe');
    var dirInput = byId('edge-basic-direction');
    var bsInput = byId('edge-basic-blocksetting');
    if (assetInput && !assetInput.value && card.asset) assetInput.value = card.asset;
    populateBasicTimeframeOptions(assetInput && assetInput.value, card.timeframe);
    if (tfInput && card.timeframe) tfInput.value = card.timeframe;
    if (dirInput && card.direction) dirInput.value = basicDirection(card.direction);
    if (bsInput && !bsInput.value && card.blockSetting) bsInput.value = card.blockSetting;
    syncBasicBlockSetting();
    renderBasicFlowState(state);
    if (saveSelection && !saveSelection.__edgeBasicBound) {
      saveSelection.__edgeBasicBound = true;
      saveSelection.addEventListener('click', confirmBasicSelection);
    }
    if (generate && !generate.__edgeBasicBound) {
      generate.__edgeBasicBound = true;
      generate.addEventListener('click', generateBasicPair);
    }
    if (files && !files.__edgeBasicBound) {
      files.__edgeBasicBound = true;
      files.addEventListener('change', function(event) {
        stageBasicFiles(event.target.files);
      });
    }
    if (analyze && !analyze.__edgeBasicBound) {
      analyze.__edgeBasicBound = true;
      analyze.addEventListener('click', function() {
        handleBasicFiles(basicSelectedFiles);
      });
    }
    if (exportBtn && !exportBtn.__edgeBasicBound) {
      exportBtn.__edgeBasicBound = true;
      exportBtn.addEventListener('click', exportBasicTemplate);
    }
    if (finish && !finish.__edgeBasicBound) {
      finish.__edgeBasicBound = true;
      finish.addEventListener('click', function() {
        var current = SQX.edgeFactory && SQX.edgeFactory.getState ? SQX.edgeFactory.getState() : {};
        var exported = (Array.isArray(current.basicTemplateExports) && current.basicTemplateExports.length) || current.c2Template;
        if (!exported) {
          setBasicStatus('Exporta templates C2 antes de finalizar la ruta básica.', 'warn');
          renderState();
          return;
        }
        if (SQX.edgeFactory && SQX.edgeFactory.finishBasicFlow) SQX.edgeFactory.finishBasicFlow();
        setBasicStatus('Ruta basica finalizada.', 'ok');
        renderState();
      });
    }
    ['edge-basic-asset', 'edge-basic-timeframe', 'edge-basic-direction'].forEach(function(id) {
      var input = byId(id);
      if (!input || input.__edgeBasicSelectionBound) return;
      input.__edgeBasicSelectionBound = true;
      input.addEventListener('change', function() {
        if (id === 'edge-basic-asset') {
          populateBasicTimeframeOptions(input.value);
        }
        var selection = readBasicSelection();
        setText('edge-basic-selection-summary', selection.asset && selection.tf
          ? [selection.asset, selection.tf, selection.dir, selection.bs].join(' · ')
          : 'Sin contexto seleccionado.');
        renderState();
      });
    });
    renderBasicTemplateStatus();
  }

  function init() {
    if (!byId('edge-factory-shell')) return false;
    bindTools();
    bindDrawer();
    bindExperienceMode();
    bindStepControls();
    bindBasicFlow();
    bindPortfolioLab();
    bindCorrelationStability();
    bindPortfolioMaster();
    bindBackportOperatorPanel();
    bindMiningRegistryPanel();
    if (SQX.edgeFactory) renderPortfolioMasterContract(SQX.edgeFactory.getState().portfolioMasterContract);
    renderState();
    return true;
  }

  SQX.edgeFactoryUI = {
    init: init,
    renderState: renderState,
    openTool: openTool,
    generateBasicPair: generateBasicPair,
    handleBasicFiles: handleBasicFiles,
    exportBasicTemplate: exportBasicTemplate,
    renderBasicTemplateStatus: renderBasicTemplateStatus,
    runPortfolioLab: runPortfolioLab,
    runPortfolioMasterContract: runPortfolioMasterContract,
    renderPortfolioReport: renderPortfolioReport,
    renderPortfolioMasterContract: renderPortfolioMasterContract,
    runCorrelationStability: runCorrelationStability,
    runRegisteredCorrelationDecision: runRegisteredCorrelationDecision,
    renderCorrelationStability: renderCorrelationStability,
    runBackportOperatorPanel: runBackportOperatorPanel,
    renderBackportResult: renderBackportResult,
    fetchRegistryFunnel: fetchRegistryFunnel,
    scanRegistryProject: scanRegistryProject,
    applyRegistryProject: applyRegistryProject,
    renderRegistryPanel: renderRegistryPanel
  };

  if (SQX.registerModule) SQX.registerModule('edge-factory-ui', SQX.edgeFactoryUI);
})(window);

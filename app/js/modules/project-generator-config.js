(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};
  var PG = SQX.projectGenerator = SQX.projectGenerator || {};
  var escapeHtml = PG.escapeHtml;
  var storageKeys = (global.SQX_CONFIG && global.SQX_CONFIG.storageKeys) || {};
  var CUSTOM_PRESETS_STORAGE_KEY = storageKeys.projectGeneratorCustomPresets || 'sqx_pg_custom_presets_v1';
  var CUSTOM_PRESET_PACKAGE_TYPE = 'sqx-edge.project-generator-custom-presets';
  var CUSTOM_PRESET_PACKAGE_VERSION = 1;
  var CUSTOM_STARTER_PROFILES = [
    {
      id: 'forex-h1-balanced',
      name: 'Forex H1 Balanced',
      tag: 'Forex',
      description: 'Punto de partida equilibrado para pares major en H1.',
      guidance: 'Usalo como primer .cfx de validacion para compradores que quieren algo estable y facil de auditar.',
      config: { name: 'Custom_EURUSD_H1_Balanced', asset: 'EURUSD', tf: 'H1', bs: 'BS_Forex_H1_Balanced', dir: 'both', capa: 1, template: '' }
    },
    {
      id: 'forex-m15-scalp',
      name: 'Forex M15 Scalp',
      tag: 'Scalp',
      description: 'Perfil rapido para explorar intradia con control por Capa 1.',
      guidance: 'Buen candidato para demos cortas, siempre con filtro de robustez posterior.',
      config: { name: 'Custom_GBPUSD_M15_Scalp', asset: 'GBPUSD', tf: 'M15', bs: 'BS_Forex_M15_Scalp', dir: 'both', capa: 1, template: '' }
    },
    {
      id: 'index-h1-trend',
      name: 'Index H1 Trend',
      tag: 'Index',
      description: 'Base direccional para indices con sesgo long y timeframe H1.',
      guidance: 'Ideal para mostrar una linea de investigacion direccional sin saturar al comprador.',
      config: { name: 'Custom_US500_H1_Trend', asset: 'US500', tf: 'H1', bs: 'BS_Index_H1_Trend', dir: 'long', capa: 1, template: '' }
    },
    {
      id: 'gold-h1-risk',
      name: 'Gold H1 Risk',
      tag: 'Gold',
      description: 'Arranque prudente para oro con Capa 2 y direccion dual.',
      guidance: 'Conviene presentarlo como perfil de riesgo controlado, no como promesa de resultado.',
      config: { name: 'Custom_XAUUSD_H1_Risk', asset: 'XAUUSD', tf: 'H1', bs: 'BS_Gold_H1_Risk', dir: 'both', capa: 2, template: '' }
    },
    {
      id: 'forex-h4-swing',
      name: 'Forex H4 Swing',
      tag: 'Swing',
      description: 'Perfil calmado para swing en EURJPY con menos ruido intradia.',
      guidance: 'Util para compradores que prefieren menos operaciones y una lectura mas tranquila.',
      config: { name: 'Custom_EURJPY_H4_Swing', asset: 'EURJPY', tf: 'H4', bs: 'BS_Forex_H4_Swing', dir: 'both', capa: 2, template: '' }
    },
    {
      id: 'index-m15-breakout',
      name: 'Index M15 Breakout',
      tag: 'Breakout',
      description: 'Exploracion de rupturas para US100 en M15 con sesgo long.',
      guidance: 'Perfil de validacion agresiva: debe pasar por comparativas fuera de muestra.',
      config: { name: 'Custom_US100_M15_Breakout', asset: 'US100', tf: 'M15', bs: 'BS_Index_M15_Breakout', dir: 'long', capa: 1, template: '' }
    },
    {
      id: 'gold-m30-volatility',
      name: 'Gold M30 Volatility',
      tag: 'Volatility',
      description: 'Perfil de oro para sesiones activas y validacion de volatilidad.',
      guidance: 'Buen complemento al perfil Gold H1 para explicar sensibilidad por timeframe.',
      config: { name: 'Custom_XAUUSD_M30_Volatility', asset: 'XAUUSD', tf: 'M30', bs: 'BS_Gold_M30_Volatility', dir: 'both', capa: 2, template: '' }
    },
    {
      id: 'index-h1-meanrevert',
      name: 'Index H1 Mean Revert',
      tag: 'MeanRev',
      description: 'Perfil alternativo para DE40 H1 orientado a reversion.',
      guidance: 'Sirve para contrastar tendencia vs reversion dentro de un mismo paquete comprador.',
      config: { name: 'Custom_DE40_H1_MeanRevert', asset: 'DE40', tf: 'H1', bs: 'BS_Index_H1_MeanRevert', dir: 'both', capa: 2, template: '' }
    }
  ];
  var CUSTOM_PROFILE_FAMILY_DEFINITIONS = [
    {
      id: 'buyer-first-setup',
      name: 'Buyer First Setup',
      tag: 'Buyer',
      description: 'Pack minimo para entregar una primera propuesta Pro con Forex, indice y oro.',
      profileIds: ['forex-h1-balanced', 'index-h1-trend', 'gold-h1-risk']
    },
    {
      id: 'intraday-validation',
      name: 'Intraday Validation',
      tag: 'Validation',
      description: 'Perfiles intradia para comparar scalp, breakout y volatilidad sin tocar el plan mining.',
      profileIds: ['forex-m15-scalp', 'index-m15-breakout', 'gold-m30-volatility']
    },
    {
      id: 'swing-risk-review',
      name: 'Swing Risk Review',
      tag: 'Risk',
      description: 'Familia tranquila para revisar H1/H4, capa 2 y sensibilidad direccional.',
      profileIds: ['forex-h4-swing', 'gold-h1-risk', 'index-h1-meanrevert']
    },
    {
      id: 'full-buyer-sample',
      name: 'Full Buyer Sample',
      tag: 'Pro',
      description: 'Muestra completa para compradores Pro: ocho perfiles base con narrativa de validacion.',
      profileIds: [
        'forex-h1-balanced',
        'forex-m15-scalp',
        'forex-h4-swing',
        'index-h1-trend',
        'index-m15-breakout',
        'index-h1-meanrevert',
        'gold-h1-risk',
        'gold-m30-volatility'
      ]
    }
  ];

function safeJsonParse(raw, fallback) {
    try {
      return JSON.parse(raw);
    } catch (_err) {
      return fallback;
    }
  }

function customPresetIdFromName(name) {
    return String(name || '')
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 48) || 'custom';
  }

function normalizeCustomProjectConfig(input) {
    var data = input || {};
    return {
      name: String(data.name || '').trim(),
      asset: String(data.asset || '').trim().toUpperCase(),
      tf: String(data.tf || '').trim().toUpperCase(),
      bs: String(data.bs || 'BS_Custom').trim() || 'BS_Custom',
      dir: ['long', 'short', 'both'].indexOf(data.dir) >= 0 ? data.dir : 'long',
      capa: parseInt(data.capa || 1, 10) === 2 ? 2 : 1,
      template: String(data.template || '').trim()
    };
  }

function normalizeCustomPreset(item) {
    if (!item || typeof item !== 'object') return null;
    var config = normalizeCustomProjectConfig(item.config || item);
    if (!config.asset || !config.tf) return null;
    var defaultName = config.name || (config.asset + ' ' + config.tf + ' ' + config.dir);
    var name = String(item.name || defaultName).trim() || defaultName;
    return {
      id: customPresetIdFromName(item.id || name),
      name: name,
      savedAt: String(item.savedAt || new Date().toISOString()),
      config: config
    };
  }

function getCustomStarterProfiles() {
    return CUSTOM_STARTER_PROFILES.map(function(profile) {
      return {
        id: profile.id,
        name: profile.name,
        tag: profile.tag,
        description: profile.description,
        guidance: profile.guidance,
        config: normalizeCustomProjectConfig(profile.config)
      };
    });
  }

function findCustomStarterProfile(id) {
    var profileId = String(id || '').trim();
    return getCustomStarterProfiles().find(function(profile) { return profile.id === profileId; }) || null;
  }

function customStarterProfileToPreset(profile) {
    var starter = typeof profile === 'string' ? findCustomStarterProfile(profile) : profile;
    if (!starter) return null;
    return normalizeCustomPreset({
      id: 'starter-' + starter.id,
      name: starter.name,
      savedAt: new Date().toISOString(),
      config: starter.config
    });
  }

function buildCustomStarterProfilePack() {
    return buildCustomProjectPresetPackage(getCustomStarterProfiles().map(customStarterProfileToPreset));
  }

function getCustomProfileFamilies() {
    return CUSTOM_PROFILE_FAMILY_DEFINITIONS.map(function(family) {
      var profiles = (family.profileIds || []).map(findCustomStarterProfile).filter(Boolean);
      return {
        id: family.id,
        name: family.name,
        tag: family.tag,
        description: family.description,
        profileIds: profiles.map(function(profile) { return profile.id; }),
        profiles: profiles
      };
    });
  }

function findCustomProfileFamily(id) {
    var familyId = String(id || '').trim();
    return getCustomProfileFamilies().find(function(family) { return family.id === familyId; }) || null;
  }

function buildCustomProfileFamilyPack(id) {
    var family = findCustomProfileFamily(id);
    if (!family) return null;
    return buildCustomProjectPresetPackage(family.profiles.map(function(profile) {
      var preset = customStarterProfileToPreset(profile);
      if (preset) preset.id = 'family-' + family.id + '-' + profile.id;
      return preset;
    }).filter(Boolean));
  }

function buildAllCustomProfileFamilyPack() {
    var seen = {};
    var presets = [];
    getCustomProfileFamilies().forEach(function(family) {
      var pack = buildCustomProfileFamilyPack(family.id);
      (pack && pack.presets || []).forEach(function(preset) {
        if (seen[preset.id]) return;
        seen[preset.id] = true;
        presets.push(preset);
      });
    });
    return buildCustomProjectPresetPackage(presets);
  }

function customProfileFamilyCountLabel(count) {
    var n = count || 0;
    return n + (n === 1 ? ' familia lista' : ' familias listas');
  }

function customProfileFamilyCardsHtml(families) {
    var list = families || getCustomProfileFamilies();
    if (!list.length) return messageHtml('No hay familias de perfiles disponibles.', 'warning');
    return list.map(function(family) {
      var id = escapeHtml(family.id);
      var profiles = family.profiles || [];
      return ''
        + '<article class="pg-custom-family-card">'
        +   '<div class="pg-custom-starter-title">'
        +     '<strong>' + escapeHtml(family.name) + '</strong>'
        +     '<span class="pg-custom-starter-tag">' + escapeHtml(family.tag || 'Pack') + '</span>'
        +   '</div>'
        +   '<div class="pg-custom-starter-desc">' + escapeHtml(family.description || '') + '</div>'
        +   '<div class="pg-custom-family-flow">'
        +     profiles.map(function(profile) {
                var cfg = normalizeCustomProjectConfig(profile.config);
                return '<span>' + escapeHtml(cfg.asset + ' ' + cfg.tf) + '</span>';
              }).join('')
        +   '</div>'
        +   '<div class="pg-custom-starter-actions">'
        +     '<button class="export-btn pg-ghost-btn" data-pg-family-load="' + id + '">Cargar primero</button>'
        +     '<button class="export-btn pg-ghost-btn" data-pg-family-save="' + id + '">Guardar pack</button>'
        +     '<button class="export-btn pg-ghost-btn" data-pg-family-export="' + id + '">Exportar</button>'
        +   '</div>'
        + '</article>';
    }).join('');
  }

function customStarterProfileCountLabel(count) {
    var n = count || 0;
    return n + (n === 1 ? ' perfil listo' : ' perfiles listos');
  }

function customStarterProfileCardsHtml(profiles) {
    var list = profiles || getCustomStarterProfiles();
    if (!list.length) return messageHtml('No hay perfiles starter disponibles.', 'warning');
    return list.map(function(profile) {
      var config = normalizeCustomProjectConfig(profile.config);
      var title = escapeHtml(profile.name);
      var id = escapeHtml(profile.id);
      return ''
        + '<article class="pg-custom-starter-card">'
        +   '<div class="pg-custom-starter-title">'
        +     '<strong>' + title + '</strong>'
        +     '<span class="pg-custom-starter-tag">' + escapeHtml(profile.tag || 'Starter') + '</span>'
        +   '</div>'
        +   '<div class="pg-custom-starter-desc">' + escapeHtml(profile.description || '') + '</div>'
        +   '<div class="pg-custom-starter-guidance">' + escapeHtml(profile.guidance || '') + '</div>'
        +   '<div class="pg-custom-starter-meta">'
        +     '<span>' + escapeHtml(config.asset) + '</span>'
        +     '<span>' + escapeHtml(config.tf) + '</span>'
        +     '<span>' + escapeHtml(config.dir.toUpperCase()) + '</span>'
        +     '<span>C' + escapeHtml(config.capa) + '</span>'
        +   '</div>'
        +   '<div class="pg-custom-starter-actions">'
        +     '<button class="export-btn pg-ghost-btn" data-pg-starter-load="' + id + '">Cargar</button>'
        +     '<button class="export-btn pg-ghost-btn" data-pg-starter-save="' + id + '">Guardar</button>'
        +   '</div>'
        + '</article>';
    }).join('');
  }

function getCustomProjectPresets(storage) {
    var store = storage || global.localStorage;
    var payload = safeJsonParse(store.getItem(CUSTOM_PRESETS_STORAGE_KEY), []);
    return Array.isArray(payload) ? payload.map(normalizeCustomPreset).filter(Boolean) : [];
  }

function setCustomProjectPresets(presets, storage) {
    var store = storage || global.localStorage;
    var clean = (presets || []).map(normalizeCustomPreset).filter(Boolean).slice(0, 30);
    store.setItem(CUSTOM_PRESETS_STORAGE_KEY, JSON.stringify(clean));
    return getCustomProjectPresets(store);
  }

function buildCustomProjectPresetPackage(presets, storage) {
    return {
      type: CUSTOM_PRESET_PACKAGE_TYPE,
      version: CUSTOM_PRESET_PACKAGE_VERSION,
      app: 'SQX Edge',
      exportedAt: new Date().toISOString(),
      presets: (presets || getCustomProjectPresets(storage)).map(normalizeCustomPreset).filter(Boolean)
    };
  }

function parseCustomProjectPresetPackage(payload) {
    var data = typeof payload === 'string' ? safeJsonParse(payload, null) : payload;
    if (!data) return [];
    if (Array.isArray(data)) return data.map(normalizeCustomPreset).filter(Boolean);
    if (Array.isArray(data.presets)) return data.presets.map(normalizeCustomPreset).filter(Boolean);
    if (data.config || data.asset || data.tf) return [normalizeCustomPreset(data)].filter(Boolean);
    return [];
  }

function importCustomProjectPresetPackage(payload, storage) {
    var incoming = parseCustomProjectPresetPackage(payload);
    if (!incoming.length) {
      return { imported: 0, presets: getCustomProjectPresets(storage) };
    }
    var incomingIds = incoming.reduce(function(acc, preset) {
      acc[preset.id] = true;
      return acc;
    }, {});
    var merged = incoming.concat(getCustomProjectPresets(storage).filter(function(preset) {
      return !incomingIds[preset.id];
    }));
    return { imported: incoming.length, presets: setCustomProjectPresets(merged, storage) };
  }

function importCustomProjectPresetPackageFromText(text, storage) {
    return importCustomProjectPresetPackage(String(text || ''), storage);
  }

function upsertCustomProjectPreset(input, presetName, storage) {
    var config = normalizeCustomProjectConfig(input);
    if (!config.asset || !config.tf) {
      return { ok: false, error: 'Completa Asset y Timeframe antes de guardar.' };
    }
    var name = String(presetName || config.name || (config.asset + ' ' + config.tf + ' ' + config.dir)).trim();
    var preset = normalizeCustomPreset({
      id: customPresetIdFromName(name),
      name: name,
      savedAt: new Date().toISOString(),
      config: config
    });
    var presets = getCustomProjectPresets(storage).filter(function(existing) { return existing.id !== preset.id; });
    presets.unshift(preset);
    return { ok: true, preset: preset, presets: setCustomProjectPresets(presets, storage) };
  }

function findCustomProjectPreset(id, storage) {
    return getCustomProjectPresets(storage).find(function(preset) { return preset.id === id; }) || null;
  }

function deleteCustomProjectPreset(id, storage) {
    var current = getCustomProjectPresets(storage);
    var next = current.filter(function(preset) { return preset.id !== id; });
    return {
      deleted: next.length !== current.length,
      presets: setCustomProjectPresets(next, storage)
    };
  }

function customProjectPresetCountLabel(count) {
    var n = count || 0;
    return n + (n === 1 ? ' guardado' : ' guardados');
  }

function customProjectPresetOptionsHtml(presets) {
    var list = presets || [];
    if (!list.length) return '<option value="">Sin presets guardados</option>';
    return '<option value="">Selecciona preset</option>' + list.map(function(preset) {
      return '<option value="' + escapeHtml(preset.id) + '">' + escapeHtml(preset.name) + '</option>';
    }).join('');
  }

function uniqueAssets(minings) {
    var seen = {};
    return (minings || [])
      .map(function(mining) { return mining.asset; })
      .filter(function(asset) {
        if (!asset || seen[asset]) return false;
        seen[asset] = true;
        return true;
      })
      .sort();
  }

function aliasTableHtml(minings, aliases) {
    var assets = uniqueAssets(minings);
    if (!assets.length) return '<div style="color:var(--text2);font-size:12px;">(esperando minings...)</div>';
    return ''
      + '<table class="cat-table" style="font-size:12px;">'
      +   '<thead><tr><th>Asset (plan)</th><th>Instrument SQX (alias)</th><th></th></tr></thead>'
      +   '<tbody>'
      +   assets.map(function(asset) {
            var current = (aliases || {})[asset] || '';
            return ''
              + '<tr>'
              +   '<td style="font-weight:700;">' + escapeHtml(asset) + '</td>'
              +   '<td><input type="text" class="search-input" style="width:200px;font-size:12px;padding:4px 8px;" data-pg-alias="' + escapeHtml(asset) + '" value="' + escapeHtml(current) + '" placeholder="(default)"></td>'
              +   '<td><button class="export-btn" style="padding:3px 10px;font-size:11px;" data-pg-suggest-asset="' + escapeHtml(asset) + '">&#128269;</button></td>'
              + '</tr>';
          }).join('')
      +   '</tbody>'
      + '</table>';
  }

function aliasTopSuggestions(suggestions, limit) {
    return (suggestions || []).slice(0, limit || 5);
  }

function aliasSuggestionPrompt(asset, suggestions) {
    var top = aliasTopSuggestions(suggestions, 5);
    var options = top.map(function(suggestion, index) {
      return (index + 1) + '. ' + suggestion.instrument + ' [' + suggestion.score + '%] — '
        + (suggestion.description || '') + ' (broker_id=' + suggestion.broker_id + ')';
    }).join('\n');
    return 'Sugerencias para "' + asset + '":\n\n'
      + options
      + '\n\nElige número (1-' + top.length + ') o escribe el ticker manualmente:';
  }

function aliasChoiceValue(choice, suggestions) {
    var raw = String(choice || '').trim();
    if (!raw) return '';
    var top = aliasTopSuggestions(suggestions, 5);
    var index = parseInt(raw, 10);
    if (index >= 1 && index <= top.length) return top[index - 1].instrument;
    return raw;
  }

function aliasProposedMessage(asset, instrument) {
    return 'Alias propuesto: ' + asset + ' → ' + instrument + ' (pulsa Guardar config)';
  }

function aliasSuggestionEmptyMessage(asset) {
    return 'Sin sugerencias para ' + asset + ' en data.db';
  }

function aliasAutoSuggestStartMessage(count) {
    return 'Auto-sugiriendo para ' + (count || 0) + ' assets…';
  }

function aliasAutoSuggestResult(found) {
    var count = found || 0;
    return {
      text: 'Auto-suggest: ' + count + ' aliases nuevos propuestos (pulsa Guardar config)',
      level: count > 0 ? 'ok' : 'info'
    };
  }

function configSaveBody(input) {
    var data = input || {};
    return {
      sqx_path: data.sqxPath || '',
      sqx_data_db: data.sqxDataDb || '',
      sqx_projects_dir: data.sqxProjectsDir || '',
      output_dir: data.outputDir || '',
      template_capa1: data.templateCapa1 || '',
      template_capa2: data.templateCapa2 || '',
      asset_aliases: data.assetAliases || {}
    };
  }

function configSaveStatus(result) {
    var keys = result && result.updated_keys || [];
    return {
      message: '✓ Guardado: ' + keys.join(', '),
      color: 'var(--green)',
      logText: 'Config actualizada (' + keys.length + ' keys)',
      logLevel: 'ok',
      traceTitle: 'Configuracion guardada',
      traceDetail: keys.join(', '),
      traceLevel: 'ok'
    };
  }

function configSaveError(message) {
    return {
      message: '✗ Error: ' + message,
      color: 'var(--red)',
      traceTitle: 'Error guardando configuracion',
      traceDetail: message,
      traceLevel: 'err'
    };
  }

function sqxCandidateFields(candidate) {
    var data = candidate || {};
    return {
      sqxPath: data.sqx_path || '',
      dataDb: data.data_db || '',
      projectsDir: data.projects_dir || ''
    };
  }

function sqxCandidateSelectedStatus(candidate) {
    var fields = sqxCandidateFields(candidate);
    return {
      logText: 'Path SQX seleccionado: ' + fields.sqxPath + ' (pulsa Guardar config)',
      logLevel: 'info',
      traceTitle: 'Ruta SQX detectada',
      traceDetail: fields.sqxPath,
      traceLevel: 'info'
    };
  }

function validateSqxMissingPathHtml() {
    return messageHtml('Pon primero un SQX install path.', 'warning');
  }

function validateSqxResolvedFields(result) {
    var resolved = result && result.resolved || {};
    return {
      dataDb: resolved.data_db || '',
      projectsDir: resolved.projects_dir || ''
    };
  }

function validateSqxShouldApply(result) {
    return !!(result && result.valid && result.resolved && result.resolved.data_db);
  }

function validateSqxTrace(path) {
    return {
      title: 'Validacion SQX correcta',
      detail: path,
      level: 'ok'
    };
  }

function messageHtml(message, tone) {
    var color = tone === 'error' ? 'var(--red)' : tone === 'warning' ? 'var(--yellow)' : 'var(--text2)';
    return '<div style="color:' + color + ';font-size:12px;">' + escapeHtml(message) + '</div>';
  }

function sqxNotFoundHtml() {
    return '<div class="alert warning"><div class="alert-icon">!</div><div class="alert-content"><strong>No se encontro ninguna instalacion de SQX.</strong>Edita los campos manualmente con la ruta donde este StrategyQuantX.exe.</div></div>';
  }

function sqxAppliedHtml() {
    return '<div class="alert success"><div class="alert-icon">&#10003;</div><div class="alert-content"><strong>Aplicado.</strong> Pulsa "Guardar config" para persistir.</div></div>';
  }

function autodetectCandidatesHtml(result) {
    var candidates = (result && result.candidates) || [];
    if (!result || !result.found) return sqxNotFoundHtml();
    return '<div style="font-size:12px;color:var(--text2);margin-bottom:6px;">' + result.found + ' instalacion(es) detectada(s):</div>'
      + candidates.map(function(candidate, index) {
        return ''
          + '<div class="pg-autodetect-row">'
          +   '<div style="flex:1;">'
          +     '<div style="font-weight:700;font-size:13px;">SQX v' + escapeHtml(candidate.version) + (candidate.has_exe ? ' &#10003;' : ' ! sin .exe') + '</div>'
          +     '<div style="font-family:Consolas,monospace;font-size:11px;color:var(--text2);">' + escapeHtml(candidate.sqx_path) + '</div>'
          +     '<div style="font-family:Consolas,monospace;font-size:10px;color:var(--text2);">-&gt; data.db: ' + escapeHtml(candidate.data_db) + '</div>'
          +   '</div>'
          +   '<button class="export-btn pg-use-btn" data-idx="' + index + '" style="border-color:var(--green);color:var(--green);">Usar esta</button>'
          + '</div>';
      }).join('');
  }

function validationItemHtml(label, ok) {
    return '<li style="color:' + (ok ? 'var(--green)' : 'var(--red)') + ';">' + (ok ? 'OK' : 'X') + ' ' + escapeHtml(label) + '</li>';
  }

function validateSqxPathHtml(result) {
    var checks = result.checks || {};
    return '<div class="alert ' + (result.valid ? 'success' : 'warning') + '"><div class="alert-icon">' + (result.valid ? 'OK' : '!') + '</div><div class="alert-content"><strong>' + (result.valid ? 'Path valido' : 'Path con problemas') + '</strong>'
      + '<ul style="margin-top:6px;padding-left:20px;font-size:12px;">'
      + validationItemHtml('Directorio base existe', checks.base_exists)
      + validationItemHtml('user/data/data.db existe', checks.data_db_exists)
      + validationItemHtml('user/projects existe', checks.projects_exists)
      + validationItemHtml('StrategyQuantX.exe existe', checks.exe_exists)
      + '</ul></div></div>';
  }

  Object.assign(PG, {
    aliasTableHtml: aliasTableHtml,
    aliasAutoSuggestResult: aliasAutoSuggestResult,
    aliasAutoSuggestStartMessage: aliasAutoSuggestStartMessage,
    aliasChoiceValue: aliasChoiceValue,
    aliasProposedMessage: aliasProposedMessage,
    aliasSuggestionEmptyMessage: aliasSuggestionEmptyMessage,
    aliasSuggestionPrompt: aliasSuggestionPrompt,
    aliasTopSuggestions: aliasTopSuggestions,
    autodetectCandidatesHtml: autodetectCandidatesHtml,
    configSaveBody: configSaveBody,
    configSaveError: configSaveError,
    configSaveStatus: configSaveStatus,
    customPresetPackageType: CUSTOM_PRESET_PACKAGE_TYPE,
    customPresetPackageVersion: CUSTOM_PRESET_PACKAGE_VERSION,
    customPresetIdFromName: customPresetIdFromName,
    customProfileFamilyCardsHtml: customProfileFamilyCardsHtml,
    customProfileFamilyCountLabel: customProfileFamilyCountLabel,
    customProjectPresetCountLabel: customProjectPresetCountLabel,
    customProjectPresetOptionsHtml: customProjectPresetOptionsHtml,
    customStarterProfileCardsHtml: customStarterProfileCardsHtml,
    customStarterProfileCountLabel: customStarterProfileCountLabel,
    customStarterProfileToPreset: customStarterProfileToPreset,
    deleteCustomProjectPreset: deleteCustomProjectPreset,
    findCustomStarterProfile: findCustomStarterProfile,
    findCustomProfileFamily: findCustomProfileFamily,
    findCustomProjectPreset: findCustomProjectPreset,
    getCustomProfileFamilies: getCustomProfileFamilies,
    getCustomStarterProfiles: getCustomStarterProfiles,
    getCustomProjectPresets: getCustomProjectPresets,
    buildAllCustomProfileFamilyPack: buildAllCustomProfileFamilyPack,
    buildCustomProfileFamilyPack: buildCustomProfileFamilyPack,
    buildCustomStarterProfilePack: buildCustomStarterProfilePack,
    buildCustomProjectPresetPackage: buildCustomProjectPresetPackage,
    importCustomProjectPresetPackage: importCustomProjectPresetPackage,
    importCustomProjectPresetPackageFromText: importCustomProjectPresetPackageFromText,
    messageHtml: messageHtml,
    normalizeCustomPreset: normalizeCustomPreset,
    normalizeCustomProjectConfig: normalizeCustomProjectConfig,
    setCustomProjectPresets: setCustomProjectPresets,
    sqxAppliedHtml: sqxAppliedHtml,
    sqxCandidateFields: sqxCandidateFields,
    sqxCandidateSelectedStatus: sqxCandidateSelectedStatus,
    sqxNotFoundHtml: sqxNotFoundHtml,
    uniqueAssets: uniqueAssets,
    upsertCustomProjectPreset: upsertCustomProjectPreset,
    validateSqxMissingPathHtml: validateSqxMissingPathHtml,
    validateSqxPathHtml: validateSqxPathHtml,
    validateSqxResolvedFields: validateSqxResolvedFields,
    validateSqxShouldApply: validateSqxShouldApply,
    validateSqxTrace: validateSqxTrace
  });
})(window);

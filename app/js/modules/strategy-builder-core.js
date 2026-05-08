(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  var WORKFLOW_STATES = [
    'source_selected',
    'context_resolved',
    'idea_framed',
    'validation_planned',
    'handoff_prepared',
    'operator_reviewed',
    'package_exportable'
  ];

  var BLOCKED_STATES = [
    'blocked_missing_source',
    'blocked_unsupported_asset',
    'blocked_missing_timeframe',
    'blocked_claims_boundary',
    'blocked_validation_pack_missing',
    'blocked_operator_review'
  ];

  var SOURCE_MODES = ['blank', 'cvc_handoff', 'project_generator_profile', 'views_workflow'];
  var PACKAGE_TYPE = 'sqx-edge.strategy-builder-package';
  var HANDOFF_TYPE = 'sqx-edge.strategy-builder-handoff';
  var IMPORT_BLOCKED_KEYS = {
    raw_csv: true,
    rawCsv: true,
    rawCSV: true,
    csv_payload: true,
    csvPayload: true,
    raw_payload: true,
    rawPayload: true,
    raw_data: true,
    rawData: true
  };
  var PG_BLOCKSETTINGS = {
    trend_following: 'BS_Tendencia',
    mean_reversion: 'BS_Reversion',
    breakout: 'BS_Breakout',
    pullback: 'BS_Pullback',
    volatility_filter: 'BS_Volatility',
    regime_filter: 'BS_Regime'
  };

  var ARCHETYPES = {
    trend_following: {
      label: 'Trend following',
      indicators: ['EMA', 'MACD', 'SuperTrend', 'SMA persistence'],
      validation: ['Trend persistence', 'Drawdown', 'Walk-forward'],
      risk: { stop_logic: 'ATR or swing stop', exposure: 'single-symbol controlled', review: 'trend decay and drawdown clustering' }
    },
    mean_reversion: {
      label: 'Mean reversion',
      indicators: ['RSI', 'Stochastic', 'Bollinger', 'PercentRank'],
      validation: ['Recovery profile', 'Adverse excursion', 'OOS decay'],
      risk: { stop_logic: 'volatility stop', exposure: 'lower burst exposure', review: 'tail loss and recovery speed' }
    },
    breakout: {
      label: 'Breakout',
      indicators: ['Donchian', 'Keltner', 'ATR', 'Volume filters'],
      validation: ['False breakout rate', 'Volatility expansion', 'Trade count'],
      risk: { stop_logic: 'range or ATR stop', exposure: 'event-sensitive', review: 'false breakout clusters' }
    },
    pullback: {
      label: 'Pullback',
      indicators: ['EMA', 'RSI', 'CCI', 'Support/resistance'],
      validation: ['Entry timing', 'Retracement depth', 'Regime fit'],
      risk: { stop_logic: 'structure stop', exposure: 'trend-conditioned', review: 'entry timing drift' }
    },
    volatility_filter: {
      label: 'Volatility filter',
      indicators: ['ATR', 'StdDev', 'Keltner', 'Bollinger width'],
      validation: ['Volatility clustering', 'Risk envelope', 'Stop behavior'],
      risk: { stop_logic: 'volatility envelope', exposure: 'filter-gated', review: 'volatility regime transitions' }
    },
    regime_filter: {
      label: 'Regime filter',
      indicators: ['CSSA/Regime', 'SMA200 persistence', 'EGT score'],
      validation: ['Regime compatibility', 'Blocked market states', 'Evidence quality'],
      risk: { stop_logic: 'regime exit or volatility stop', exposure: 'regime-gated', review: 'false regime positives' }
    }
  };

  var DEFAULT_CHECKLIST = [
    'asset and timeframe are correct',
    'source evidence has been reviewed',
    'idea archetype is appropriate for the asset/regime',
    'validation pack is selected',
    'StrategyQuant settings will be reviewed manually',
    'no profitability claim is inferred from the package',
    'export is local and reviewable'
  ];

  function nowIso(options) {
    return options && options.createdAt ? options.createdAt : new Date().toISOString();
  }

  function normalizeText(value, fallback) {
    var text = String(value == null ? '' : value).trim();
    return text || fallback || '';
  }

  function normalizeAsset(value) {
    return normalizeText(value).toUpperCase().replace(/[^A-Z0-9._-]/g, '');
  }

  function normalizeTimeframe(value) {
    return normalizeText(value, 'H1').toUpperCase();
  }

  function parseJsonPayload(input) {
    if (input && typeof input === 'object') return { payload: input, errors: [] };
    try {
      return { payload: JSON.parse(String(input == null ? '' : input)), errors: [] };
    } catch (_err) {
      return { payload: null, errors: ['invalid_json'] };
    }
  }

  function collectForbiddenKeys(value, path, hits) {
    if (!value || typeof value !== 'object') return hits;
    Object.keys(value).forEach(function(key) {
      var nextPath = path ? path + '.' + key : key;
      if (IMPORT_BLOCKED_KEYS[key]) hits.push(nextPath);
      collectForbiddenKeys(value[key], nextPath, hits);
    });
    return hits;
  }

  function manifestAssets(manifest) {
    var source = manifest || global.SQX_MANIFEST || {};
    return source.assets && Array.isArray(source.assets.assets) ? source.assets.assets : [];
  }

  function findAsset(assetId, manifest) {
    var normalized = normalizeAsset(assetId);
    var assets = manifestAssets(manifest);
    for (var i = 0; i < assets.length; i += 1) {
      if (normalizeAsset(assets[i].id) === normalized) return assets[i];
    }
    return null;
  }

  function supportedAsset(assetId, manifest) {
    if (!manifestAssets(manifest).length) return !!normalizeAsset(assetId);
    return !!findAsset(assetId, manifest);
  }

  function marketFamily(assetId, manifest) {
    var asset = findAsset(assetId, manifest);
    if (!asset) return 'unknown';
    if (asset.type === 'forex') return 'forex';
    if (asset.type === 'index') return 'index';
    if (asset.type === 'oro') return 'gold';
    return asset.type || 'unknown';
  }

  function safeProjectName(asset, timeframe, archetype) {
    return ['SB', normalizeAsset(asset), normalizeTimeframe(timeframe), normalizeText(archetype, 'idea')]
      .join('_')
      .replace(/[^A-Za-z0-9_-]/g, '_')
      .slice(0, 80);
  }

  function normalizeDirection(value) {
    var text = normalizeText(value, '').toLowerCase();
    if (text === 'long' || text === 'short' || text === 'both') return text;
    return 'both';
  }

  function defaultValidationPack(archetype) {
    if (archetype === 'mean_reversion') return 'risk-capital-review';
    if (archetype === 'breakout') return 'asset-family-review';
    if (archetype === 'regime_filter') return 'pro-setup-assist';
    return 'robustness';
  }

  function sourceSummary(input) {
    var mode = input.source_mode || input.sourceMode || 'blank';
    var handoff = input.source_handoff || input.sourceHandoff || null;
    if (mode === 'cvc_handoff' && handoff && handoff.type === HANDOFF_TYPE) {
      var candidate = handoff.recommended_candidate || {};
      return {
        type: handoff.type,
        candidate: candidate.strategy_name || '',
        rank: candidate.rank || null,
        decision: candidate.decision || 'review_required',
        oos: candidate.oos || null,
        regime: candidate.regime || null
      };
    }
    if (input.source_summary && typeof input.source_summary === 'object') {
      return {
        type: normalizeText(input.source_summary.type, mode),
        candidate: normalizeText(input.source_summary.candidate),
        rank: input.source_summary.rank || null,
        decision: normalizeText(input.source_summary.decision, 'review_required'),
        oos: input.source_summary.oos || null,
        regime: input.source_summary.regime || null,
        note: normalizeText(input.source_summary.note)
      };
    }
    if (mode === 'project_generator_profile') {
      return { type: mode, profile_id: normalizeText(input.project_profile_id || input.projectProfileId, 'starter-forex-h1-balanced') };
    }
    if (mode === 'views_workflow') {
      return { type: mode, validation_pack_id: normalizeText(input.validation_pack_id || input.validationPackId, 'asset-family-review') };
    }
    return { type: 'blank', note: 'operator_defined_context' };
  }

  function resolveAsset(input) {
    var handoff = input.source_handoff || input.sourceHandoff || null;
    if ((input.source_mode || input.sourceMode) === 'cvc_handoff' && handoff && handoff.recommended_candidate) {
      return normalizeAsset(handoff.recommended_candidate.symbol || input.asset);
    }
    return normalizeAsset(input.asset);
  }

  function resolveWorkflowState(context, input, manifest) {
    if (SOURCE_MODES.indexOf(context.source_mode) === -1) return 'blocked_missing_source';
    if (!supportedAsset(context.asset, manifest)) return 'blocked_unsupported_asset';
    if (!context.timeframe) return 'blocked_missing_timeframe';
    if (!ARCHETYPES[context.idea_archetype]) return 'blocked_claims_boundary';
    if (!context.validation_pack_id) return 'blocked_validation_pack_missing';
    if (!input.operator_reviewed && !input.operatorReviewed) return 'blocked_operator_review';
    return 'package_exportable';
  }

  function buildContext(input, options) {
    var data = input || {};
    var manifest = options && options.manifest ? options.manifest : global.SQX_MANIFEST;
    var mode = normalizeText(data.source_mode || data.sourceMode, 'blank');
    var archetype = normalizeText(data.idea_archetype || data.ideaArchetype, 'trend_following');
    var asset = resolveAsset(data);
    var timeframe = normalizeTimeframe(data.timeframe);
    var summary = sourceSummary(data);
    var regime = summary.regime || {};
    return {
      asset: asset,
      timeframe: timeframe,
      market_family: normalizeText(data.market_family || data.marketFamily, marketFamily(asset, manifest)),
      direction_bias: normalizeText(data.direction_bias || data.directionBias, 'review_required'),
      source_mode: mode,
      source_summary: summary,
      regime_label: regime.label || data.regime_label || data.regimeLabel || 'unknown',
      oos_summary: summary.oos || data.oos_summary || data.oosSummary || { status: 'unknown' },
      mtf_summary: data.mtf_summary || data.mtfSummary || { status: 'not_attached' },
      project_profile_id: normalizeText(data.project_profile_id || data.projectProfileId, 'starter-forex-h1-balanced'),
      validation_pack_id: normalizeText(data.validation_pack_id || data.validationPackId, defaultValidationPack(archetype)),
      risk_profile: normalizeText(data.risk_profile || data.riskProfile, 'review_required'),
      idea_archetype: archetype,
      traceability: data.traceability || ['SB3 read-only package prototype']
    };
  }

  function checklist(input) {
    var reviewed = !!(input.operator_reviewed || input.operatorReviewed);
    return DEFAULT_CHECKLIST.map(function(label) {
      return { label: label, confirmed: reviewed };
    });
  }

  function buildPackage(input, options) {
    var data = input || {};
    var context = buildContext(data, options);
    var manifest = options && options.manifest ? options.manifest : global.SQX_MANIFEST;
    var archetype = ARCHETYPES[context.idea_archetype] || null;
    var state = resolveWorkflowState(context, data, manifest);
    var validationEmphasis = archetype ? archetype.validation.slice() : [];
    return {
      type: PACKAGE_TYPE,
      version: 1,
      created_at: nowIso(options),
      workflow_state: state,
      source_mode: context.source_mode,
      source_summary: context.source_summary,
      asset_profile: {
        asset: context.asset,
        timeframe: context.timeframe,
        market_family: context.market_family,
        direction_bias: context.direction_bias,
        regime_label: context.regime_label,
        oos_summary: context.oos_summary,
        mtf_summary: context.mtf_summary
      },
      idea_archetype: {
        id: context.idea_archetype,
        label: archetype ? archetype.label : 'Review required'
      },
      indicator_family_candidates: archetype ? archetype.indicators.slice() : [],
      risk_envelope: archetype ? archetype.risk : { review: 'operator review required' },
      validation_requirements: {
        validation_pack_id: context.validation_pack_id,
        emphasis: validationEmphasis,
        note: 'validation is a review gate, not a marketing proof'
      },
      project_generator_handoff: {
        profile_id: context.project_profile_id,
        suggested_project_name: safeProjectName(context.asset, context.timeframe, context.idea_archetype),
        auto_run_bulk_generation: false,
        custom_project_allowed: true
      },
      views_handoff: {
        validation_pack_id: context.validation_pack_id,
        required_review: true
      },
      operator_checklist: checklist(data),
      traceability: context.traceability.concat([
        'No raw CSV payloads',
        'No remote calls',
        'No generated trading logic'
      ]),
      blocked_claims: [
        'No profitability claim is inferred from this package.',
        'No auto-trading or broker integration is included.',
        'StrategyQuant settings must be reviewed manually.'
      ]
    };
  }

  function sampleCvcHandoff() {
    return {
      type: HANDOFF_TYPE,
      version: 1,
      generated_at: '2026-05-09T00:00:00.000Z',
      source_review: {
        type: 'sqx-edge.champion-challenger-review',
        candidate_count: 3,
        formal_ready_count: 1,
        oos_stable_count: 1,
        regime_compliant_count: 3
      },
      recommended_candidate: {
        rank: 1,
        strategy_name: 'Challenger A',
        symbol: 'EURUSD',
        decision: 'builder_candidate',
        metrics: { profit_factor: 1.62, return_drawdown: 3.95, trades: 180 },
        oos: { block_count: 3, positive_block_ratio: 1, stable_enough: true },
        regime: { symbol: 'EURUSD', label: 'COMPLIANT', reason: 'sample evidence' }
      },
      candidates: [],
      builder_status: 'planned_contract',
      guardrails: ['No raw CSV payloads are included.', 'No remote calls are required.']
    };
  }

  function modelFromPackage(payload) {
    var assetProfile = payload.asset_profile || {};
    var idea = payload.idea_archetype || {};
    var validation = payload.validation_requirements || {};
    var project = payload.project_generator_handoff || {};
    return {
      source_mode: normalizeText(payload.source_mode, 'blank'),
      source_summary: payload.source_summary || null,
      asset: normalizeAsset(assetProfile.asset),
      timeframe: normalizeTimeframe(assetProfile.timeframe),
      idea_archetype: normalizeText(idea.id, 'trend_following'),
      validation_pack_id: normalizeText(validation.validation_pack_id, defaultValidationPack(idea.id)),
      project_profile_id: normalizeText(project.profile_id, 'starter-forex-h1-balanced'),
      operator_reviewed: false,
      traceability: (payload.traceability || []).concat(['SB4 imported package re-review'])
    };
  }

  function modelFromHandoff(payload) {
    var candidate = payload.recommended_candidate || {};
    return {
      source_mode: 'cvc_handoff',
      source_handoff: payload,
      asset: normalizeAsset(candidate.symbol || 'EURUSD'),
      timeframe: normalizeTimeframe(candidate.timeframe || 'H1'),
      idea_archetype: 'trend_following',
      validation_pack_id: 'robustness',
      project_profile_id: 'starter-forex-h1-balanced',
      operator_reviewed: false,
      traceability: ['SB4 imported CVC handoff re-review']
    };
  }

  function validateImportPayload(input, options) {
    var parsed = parseJsonPayload(input);
    var errors = parsed.errors.slice();
    var warnings = [];
    var payload = parsed.payload;
    var manifest = options && options.manifest ? options.manifest : global.SQX_MANIFEST;
    if (!payload || typeof payload !== 'object') {
      errors.push('payload_must_be_object');
      return { ok: false, errors: errors, warnings: warnings, payload: null };
    }
    var forbidden = collectForbiddenKeys(payload, '', []);
    if (forbidden.length) errors.push('forbidden_raw_payload_keys:' + forbidden.join(','));
    if (payload.type !== PACKAGE_TYPE && payload.type !== HANDOFF_TYPE) errors.push('unsupported_type:' + normalizeText(payload.type, 'missing'));
    if (payload.type === PACKAGE_TYPE) {
      if (payload.version !== 1) errors.push('unsupported_package_version');
      if (!payload.asset_profile || !payload.asset_profile.asset) errors.push('missing_asset_profile');
      if (!payload.asset_profile || !payload.asset_profile.timeframe) errors.push('missing_timeframe');
      if (!payload.idea_archetype || !payload.idea_archetype.id) errors.push('missing_idea_archetype');
      if (!payload.validation_requirements || !payload.validation_requirements.validation_pack_id) errors.push('missing_validation_pack');
      if (payload.asset_profile && payload.asset_profile.asset && !supportedAsset(payload.asset_profile.asset, manifest)) errors.push('unsupported_asset');
      if (payload.workflow_state && WORKFLOW_STATES.concat(BLOCKED_STATES).indexOf(payload.workflow_state) === -1) {
        warnings.push('unknown_workflow_state:' + payload.workflow_state);
      }
    }
    if (payload.type === HANDOFF_TYPE) {
      if (!payload.recommended_candidate) errors.push('missing_recommended_candidate');
      if (payload.recommended_candidate && payload.recommended_candidate.symbol && !supportedAsset(payload.recommended_candidate.symbol, manifest)) {
        errors.push('unsupported_asset');
      }
    }
    return { ok: errors.length === 0, errors: errors, warnings: warnings, payload: payload };
  }

  function importPayload(input, options) {
    var validation = validateImportPayload(input, options);
    if (!validation.ok) {
      return {
        ok: false,
        errors: validation.errors,
        warnings: validation.warnings,
        model: null,
        package: null,
        source_handoff: null
      };
    }
    var opts = options || {};
    var model = validation.payload.type === HANDOFF_TYPE ? modelFromHandoff(validation.payload) : modelFromPackage(validation.payload);
    if (opts.operatorReviewed === true || opts.operator_reviewed === true) model.operator_reviewed = true;
    var built = buildPackage(model, opts);
    built.import_metadata = {
      source_type: validation.payload.type,
      imported_at: nowIso(opts),
      re_review_required: !model.operator_reviewed,
      warnings: validation.warnings.slice()
    };
    return {
      ok: true,
      errors: [],
      warnings: validation.warnings,
      model: model,
      package: built,
      source_handoff: validation.payload.type === HANDOFF_TYPE ? validation.payload : null
    };
  }

  function projectGeneratorPrefillFromPackage(input, options) {
    var payload = input && input.type === PACKAGE_TYPE ? input : buildPackage(input || {}, options);
    var errors = [];
    if (!payload || payload.type !== PACKAGE_TYPE) errors.push('invalid_strategy_builder_package');
    if (payload && payload.workflow_state !== 'package_exportable' && !(options && options.allowBlocked)) {
      errors.push('package_not_exportable');
    }
    var assetProfile = payload && payload.asset_profile || {};
    var idea = payload && payload.idea_archetype || {};
    var handoff = payload && payload.project_generator_handoff || {};
    var asset = normalizeAsset(assetProfile.asset);
    var timeframe = normalizeTimeframe(assetProfile.timeframe);
    if (!asset) errors.push('missing_asset');
    if (!timeframe) errors.push('missing_timeframe');
    if (errors.length) {
      return { ok: false, errors: errors, config: null };
    }
    return {
      ok: true,
      errors: [],
      config: {
        name: normalizeText(handoff.suggested_project_name, safeProjectName(asset, timeframe, idea.id)),
        asset: asset,
        tf: timeframe,
        bs: PG_BLOCKSETTINGS[idea.id] || 'BS_Custom',
        dir: normalizeDirection(assetProfile.direction_bias),
        capa: 1,
        template: ''
      },
      source: {
        package_type: payload.type,
        package_version: payload.version,
        workflow_state: payload.workflow_state,
        archetype: idea.id || 'unknown',
        validation_pack_id: payload.validation_requirements && payload.validation_requirements.validation_pack_id || ''
      },
      guardrails: [
        'prefill_only',
        'no_generation_triggered',
        'operator_must_press_generate_custom'
      ]
    };
  }

  SQX.strategyBuilderCore = SQX.strategyBuilderCore || {
    archetypes: ARCHETYPES,
    blockedStates: BLOCKED_STATES,
    buildContext: buildContext,
    buildPackage: buildPackage,
    defaultValidationPack: defaultValidationPack,
    importPayload: importPayload,
    projectGeneratorPrefillFromPackage: projectGeneratorPrefillFromPackage,
    sampleCvcHandoff: sampleCvcHandoff,
    sourceModes: SOURCE_MODES,
    states: WORKFLOW_STATES,
    supportedAsset: supportedAsset,
    validateImportPayload: validateImportPayload
  };

  if (SQX.registerModule) {
    SQX.registerModule('strategy-builder-core', SQX.strategyBuilderCore);
  }
})(window);

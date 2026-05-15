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
  var BUYER_HANDOFF_PACK_TYPE = 'sqx-edge.strategy-builder-buyer-handoff-pack';
  var BUYER_HANDOFF_PACK_REVIEW_TYPE = 'sqx-edge.strategy-builder-buyer-handoff-pack-review';
  var BUYER_SESSION_CHECKLIST_TYPE = 'sqx-edge.strategy-builder-buyer-session-checklist';
  var BUYER_SESSION_SUMMARY_TYPE = 'sqx-edge.strategy-builder-buyer-session-summary';
  var BUYER_SESSION_NOTES_TYPE = 'sqx-edge.strategy-builder-buyer-session-notes';
  var BUYER_SESSION_SUPPORT_CASE_TYPE = 'sqx-edge.strategy-builder-buyer-session-support-case-bundle';
  var BUYER_SESSION_RESOLUTION_TYPE = 'sqx-edge.strategy-builder-buyer-session-support-resolution-checklist';
  var EVIDENCE_HANDOFF_INDEX_TYPE = 'sqx-edge.strategy-builder-evidence-handoff-index';
  var REQUIRED_BUYER_HANDOFFS = [
    'project_generator_prefill',
    'project_generator_preset_draft',
    'sqx_views',
    'strategy_cleaner'
  ];
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
    trend_following: 'BS_Tendencia_v4',
    mean_reversion: 'BS_Regimen_v4',
    breakout: 'BS_Volatilidad_v4',
    pullback: 'BS_Momentum_v4',
    volatility_filter: 'BS_Volatilidad_v4',
    regime_filter: 'BS_Regimen_v4'
  };
  var VIEWS_HANDOFF_PACKS = {
    robustness: {
      label: 'Robustness',
      preset: 'robustness',
      yearCount: 9,
      sampleStart: 21,
      groupMode: 'by_year'
    },
    'risk-capital-review': {
      label: 'Risk Review',
      preset: 'risk',
      yearCount: 5,
      sampleStart: 21,
      groupMode: 'by_metric'
    },
    'asset-family-review': {
      label: 'Asset Family Review',
      preset: 'robustness',
      yearCount: 9,
      sampleStart: 21,
      groupMode: 'by_year'
    },
    'pro-setup-assist': {
      label: 'Pro Setup Review',
      preset: 'risk',
      yearCount: 7,
      sampleStart: 21,
      groupMode: 'by_year'
    },
    'free-core-validation': {
      label: 'Core Validation',
      preset: 'egt-core',
      yearCount: 9,
      sampleStart: 21,
      groupMode: 'by_year'
    }
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
  var BUYER_WORKFLOW_STEPS = [
    { id: 'source', label: 'Evidence source selected', blocked: 'Select or import a source.' },
    { id: 'review', label: 'Manual review confirmed', blocked: 'Confirm manual review.' },
    { id: 'package', label: 'Package exportable', blocked: 'Resolve package gate.' },
    { id: 'project_generator', label: 'Project Generator handoff available', blocked: 'Package must be exportable.' },
    { id: 'sqx_views', label: 'SQX Views validation available', blocked: 'Package must be exportable.' },
    { id: 'operator', label: 'Operator runs StrategyQuant manually', blocked: 'Use the prepared handoffs manually.' }
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
        regime: candidate.regime || null,
        temporal_health: candidate.temporal_health || null,
        egt_v2: candidate.egt_v2 || null,
        direction: candidate.direction || null,
        directional_coherence: candidate.directional_coherence || null,
        consolidated_score: candidate.consolidated_score || null,
        evidence_review: candidate.evidence_review || null,
        source_review: handoff.source_review || null
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
        temporal_health: input.source_summary.temporal_health || null,
        egt_v2: input.source_summary.egt_v2 || null,
        direction: input.source_summary.direction || null,
        directional_coherence: input.source_summary.directional_coherence || null,
        consolidated_score: input.source_summary.consolidated_score || null,
        evidence_review: input.source_summary.evidence_review || null,
        source_review: input.source_summary.source_review || null,
        note: normalizeText(input.source_summary.note)
      };
    }
    if (mode === 'project_generator_profile') {
      return { type: mode, profile_id: normalizeText(input.project_profile_id || input.projectProfileId, 'custom-forex-h1-balanced') };
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
      cvc_evidence_summary: {
        temporal_health: summary.temporal_health || null,
        egt_v2: summary.egt_v2 || null,
        direction: summary.direction || null,
        directional_coherence: summary.directional_coherence || null,
        consolidated_score: summary.consolidated_score || null,
        evidence_review: summary.evidence_review || null
      },
      mtf_summary: data.mtf_summary || data.mtfSummary || { status: 'not_attached' },
      project_profile_id: normalizeText(data.project_profile_id || data.projectProfileId, 'custom-forex-h1-balanced'),
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
        cvc_evidence_summary: context.cvc_evidence_summary,
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
        regime: { symbol: 'EURUSD', label: 'COMPLIANT', reason: 'sample evidence' },
        temporal_health: {
          status: 'fresh',
          pass_all: true,
          peak_block: 3,
          block_count: 3,
          dd_at_close: 0,
          recovery_index: 1
        },
        egt_v2: {
          verdict: 'STRONG',
          label: 'COMPLIANT',
          direction: 'long_only',
          dominant_regime: 'BULL',
          failed_regimes: [],
          insufficient_regimes: [],
          regime_block_counts: { BULL: 3, BEAR: 0, RANGE: 0 }
        },
        direction: {
          direction: 'long_only',
          source: 'trades_split',
          confidence: 'high',
          imbalance: 1
        },
        directional_coherence: {
          verdict: 'OK',
          direction: 'long_only',
          metric: 'Net Profit',
          avg_net_profit: 100,
          bull_check: 'OK',
          bear_check: null,
          flags: []
        },
        consolidated_score: {
          score: 88,
          base_score: 76,
          bonus: 12,
          passed_hard: true,
          hard_fails: []
        },
        evidence_review: {
          formal_ok: true,
          oos_stable: true,
          temporal_health_ok: true,
          egt_v2_ok: true,
          directional_coherence_ok: true,
          score_pro_ok: true,
          operator_review_required: true
        }
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
      project_profile_id: normalizeText(project.profile_id, 'custom-forex-h1-balanced'),
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
      project_profile_id: 'custom-forex-h1-balanced',
      operator_reviewed: false,
      traceability: ['SB4 imported CVC handoff re-review']
    };
  }

  function validatePackageShape(payload, errors, warnings, manifest, prefix) {
    var label = prefix || '';
    if (!payload || payload.type !== PACKAGE_TYPE) {
      errors.push(label + 'invalid_strategy_builder_package');
      return;
    }
    if (payload.version !== 1) errors.push(label + 'unsupported_package_version');
    if (!payload.asset_profile || !payload.asset_profile.asset) errors.push(label + 'missing_asset_profile');
    if (!payload.asset_profile || !payload.asset_profile.timeframe) errors.push(label + 'missing_timeframe');
    if (!payload.idea_archetype || !payload.idea_archetype.id) errors.push(label + 'missing_idea_archetype');
    if (!payload.validation_requirements || !payload.validation_requirements.validation_pack_id) errors.push(label + 'missing_validation_pack');
    if (payload.asset_profile && payload.asset_profile.asset && !supportedAsset(payload.asset_profile.asset, manifest)) errors.push(label + 'unsupported_asset');
    if (payload.workflow_state && WORKFLOW_STATES.concat(BLOCKED_STATES).indexOf(payload.workflow_state) === -1) {
      warnings.push(label + 'unknown_workflow_state:' + payload.workflow_state);
    }
  }

  function validateBuyerHandoffPackShape(payload, errors, warnings, manifest) {
    if (payload.version !== 1) errors.push('unsupported_buyer_pack_version');
    if (!payload.strategy_builder_package) {
      errors.push('missing_strategy_builder_package');
    } else {
      validatePackageShape(payload.strategy_builder_package, errors, warnings, manifest, 'nested_');
    }
    var handoffs = payload.handoffs || {};
    REQUIRED_BUYER_HANDOFFS.forEach(function(id) {
      if (!handoffs[id]) errors.push('missing_buyer_pack_handoff:' + id);
    });
    if (payload.workflow && payload.workflow.ready !== true) warnings.push('buyer_pack_workflow_not_ready');
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
    if (payload.type !== PACKAGE_TYPE && payload.type !== HANDOFF_TYPE && payload.type !== BUYER_HANDOFF_PACK_TYPE) errors.push('unsupported_type:' + normalizeText(payload.type, 'missing'));
    if (payload.type === PACKAGE_TYPE) {
      validatePackageShape(payload, errors, warnings, manifest, '');
    }
    if (payload.type === HANDOFF_TYPE) {
      if (!payload.recommended_candidate) errors.push('missing_recommended_candidate');
      if (payload.recommended_candidate && payload.recommended_candidate.symbol && !supportedAsset(payload.recommended_candidate.symbol, manifest)) {
        errors.push('unsupported_asset');
      }
    }
    if (payload.type === BUYER_HANDOFF_PACK_TYPE) {
      validateBuyerHandoffPackShape(payload, errors, warnings, manifest);
    }
    return { ok: errors.length === 0, errors: errors, warnings: warnings, payload: payload };
  }

  function buyerHandoffPackReview(input, options) {
    var validation = validateImportPayload(input, options);
    if (!validation.ok || !validation.payload || validation.payload.type !== BUYER_HANDOFF_PACK_TYPE) {
      return {
        ok: false,
        errors: validation.errors.length ? validation.errors : ['unsupported_buyer_handoff_pack'],
        warnings: validation.warnings,
        review: null,
        package: null,
        guardrails: ['review_only', 'no_destination_action_triggered']
      };
    }
    var opts = options || {};
    var pack = validation.payload;
    var sourcePackage = pack.strategy_builder_package;
    var model = modelFromPackage(sourcePackage);
    if (opts.operatorReviewed === true || opts.operator_reviewed === true) model.operator_reviewed = true;
    var rebuilt = buildPackage(model, opts);
    var handoffs = pack.handoffs || {};
    var included = REQUIRED_BUYER_HANDOFFS.map(function(id) {
      return {
        id: id,
        present: !!handoffs[id],
        ok: !!(handoffs[id] && handoffs[id].ok !== false)
      };
    });
    var missing = included.filter(function(item) { return !item.present; }).map(function(item) { return item.id; });
    return {
      ok: true,
      errors: [],
      warnings: validation.warnings,
      package: rebuilt,
      review: {
        type: BUYER_HANDOFF_PACK_REVIEW_TYPE,
        version: 1,
        imported_at: nowIso(opts),
        source_created_at: normalizeText(pack.created_at),
        source_type: pack.type,
        asset: rebuilt.asset_profile.asset,
        timeframe: rebuilt.asset_profile.timeframe,
        original_workflow_state: normalizeText(sourcePackage.workflow_state, 'unknown'),
        rebuilt_workflow_state: rebuilt.workflow_state,
        re_review_required: !model.operator_reviewed,
        included_handoffs: included,
        missing_handoffs: missing,
        manual_next_steps: (pack.manual_next_steps || []).concat([
          'Confirm manual review before exporting or preparing handoffs from the imported pack.'
        ]),
        guardrails: [
          'review_only',
          'no_destination_action_triggered',
          'no_local_storage_write',
          'no_backend_endpoint',
          'operator_must_confirm_manual_review'
        ]
      },
      guardrails: [
        'buyer_pack_import_review_only',
        'no_destination_action_triggered',
        'operator_must_confirm_manual_review'
      ]
    };
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
    var sourcePayload = validation.payload.type === BUYER_HANDOFF_PACK_TYPE ? validation.payload.strategy_builder_package : validation.payload;
    var model = validation.payload.type === HANDOFF_TYPE ? modelFromHandoff(validation.payload) : modelFromPackage(sourcePayload);
    if (opts.operatorReviewed === true || opts.operator_reviewed === true) model.operator_reviewed = true;
    var built = buildPackage(model, opts);
    var buyerReviewResult = validation.payload.type === BUYER_HANDOFF_PACK_TYPE ? buyerHandoffPackReview(validation.payload, opts) : null;
    built.import_metadata = {
      source_type: validation.payload.type,
      imported_at: nowIso(opts),
      re_review_required: !model.operator_reviewed,
      warnings: validation.warnings.slice(),
      buyer_pack_review: !!buyerReviewResult
    };
    return {
      ok: true,
      errors: [],
      warnings: validation.warnings,
      model: model,
      package: built,
      source_handoff: validation.payload.type === HANDOFF_TYPE ? validation.payload : null,
      buyer_pack_review: buyerReviewResult ? buyerReviewResult.review : null
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

  function reviewChecklistSummary(input) {
    var payload = input && input.type === PACKAGE_TYPE ? input : buildPackage(input || {});
    var items = payload && payload.operator_checklist || [];
    var confirmed = items.filter(function(item) { return !!item.confirmed; }).length;
    return {
      total: items.length,
      confirmed: confirmed,
      ready: !!items.length && confirmed === items.length,
      items: items.map(function(item) {
        return {
          label: normalizeText(item.label, 'review item'),
          confirmed: !!item.confirmed
        };
      })
    };
  }

  function presetNameFromConfig(config, source) {
    var data = config || {};
    var sourceData = source || {};
    var archetype = normalizeText(sourceData.archetype, 'idea').replace(/_/g, ' ');
    return ['SB', data.asset, data.tf, archetype]
      .filter(Boolean)
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim()
      .slice(0, 80);
  }

  function projectGeneratorPresetDraftFromPackage(input, options) {
    var prefill = projectGeneratorPrefillFromPackage(input, options);
    if (!prefill.ok) {
      return {
        ok: false,
        errors: prefill.errors,
        config: null,
        preset_name: '',
        guardrails: ['no_auto_save']
      };
    }
    return {
      ok: true,
      errors: [],
      config: prefill.config,
      preset_name: presetNameFromConfig(prefill.config, prefill.source),
      source: prefill.source,
      guardrails: prefill.guardrails.concat([
        'preset_name_prefill_only',
        'no_auto_save',
        'operator_must_press_save_preset'
      ])
    };
  }

  function sqxViewsHandoffFromPackage(input, options) {
    var payload = input && input.type === PACKAGE_TYPE ? input : buildPackage(input || {}, options);
    var errors = [];
    var warnings = [];
    if (!payload || payload.type !== PACKAGE_TYPE) errors.push('invalid_strategy_builder_package');
    if (payload && payload.workflow_state !== 'package_exportable' && !(options && options.allowBlocked)) {
      errors.push('package_not_exportable');
    }
    var assetProfile = payload && payload.asset_profile || {};
    var validation = payload && payload.validation_requirements || {};
    var viewSource = payload && payload.views_handoff || {};
    var asset = normalizeAsset(assetProfile.asset);
    var timeframe = normalizeTimeframe(assetProfile.timeframe);
    var validationPackId = normalizeText(viewSource.validation_pack_id || validation.validation_pack_id, 'robustness');
    var pack = VIEWS_HANDOFF_PACKS[validationPackId] || VIEWS_HANDOFF_PACKS.robustness;
    if (!VIEWS_HANDOFF_PACKS[validationPackId]) warnings.push('unknown_validation_pack:' + validationPackId);
    if (!asset) errors.push('missing_asset');
    if (!timeframe) errors.push('missing_timeframe');
    if (errors.length) {
      return { ok: false, errors: errors, warnings: warnings, handoff: null };
    }
    return {
      ok: true,
      errors: [],
      warnings: warnings,
      handoff: {
        preset: pack.preset,
        viewName: ['SB', asset, timeframe, pack.label].join(' '),
        yearCount: pack.yearCount,
        sampleStart: pack.sampleStart,
        groupMode: pack.groupMode,
        validation_pack_id: validationPackId,
        asset: asset,
        timeframe: timeframe,
        required_review: true
      },
      source: {
        package_type: payload.type,
        package_version: payload.version,
        workflow_state: payload.workflow_state,
        validation_pack_id: validationPackId
      },
      guardrails: [
        'views_handoff_only',
        'no_template_saved',
        'no_download_triggered',
        'operator_must_press_download_or_save_template'
      ]
    };
  }

  function strategyCleanerDraftFromPackage(input, options) {
    var payload = input && input.type === PACKAGE_TYPE ? input : buildPackage(input || {}, options);
    var errors = [];
    if (!payload || payload.type !== PACKAGE_TYPE) errors.push('invalid_strategy_builder_package');
    if (payload && payload.workflow_state !== 'package_exportable' && !(options && options.allowBlocked)) {
      errors.push('package_not_exportable');
    }
    var assetProfile = payload && payload.asset_profile || {};
    var asset = normalizeAsset(assetProfile.asset);
    var timeframe = normalizeTimeframe(assetProfile.timeframe);
    if (!asset) errors.push('missing_asset');
    if (!timeframe) errors.push('missing_timeframe');
    if (errors.length) {
      return { ok: false, errors: errors, draft: null, guardrails: ['no_cleaning_triggered'] };
    }
    return {
      ok: true,
      errors: [],
      draft: {
        asset: asset,
        timeframe: timeframe,
        recursive: true,
        remove_exit_bars: true,
        rename_institutional: true,
        rename_pattern: '{asset}_{tf}_{dir}_{id}',
        directory_hint: 'Select the StrategyQuant databank or generated .sqx folder manually.'
      },
      source: {
        package_type: payload.type,
        package_version: payload.version,
        workflow_state: payload.workflow_state,
        validation_pack_id: payload.validation_requirements && payload.validation_requirements.validation_pack_id || ''
      },
      guardrails: [
        'draft_only',
        'no_scan_triggered',
        'no_cleaning_triggered',
        'no_file_mutation',
        'operator_must_press_scan_and_process'
      ]
    };
  }

  function unifiedBuyerHandoffPackFromPackage(input, options) {
    var payload = input && input.type === PACKAGE_TYPE ? input : buildPackage(input || {}, options);
    var errors = [];
    if (!payload || payload.type !== PACKAGE_TYPE) errors.push('invalid_strategy_builder_package');
    if (payload && payload.workflow_state !== 'package_exportable' && !(options && options.allowBlocked)) {
      errors.push('package_not_exportable');
    }
    var pgPrefill = errors.length ? null : projectGeneratorPrefillFromPackage(payload, options);
    var pgPreset = errors.length ? null : projectGeneratorPresetDraftFromPackage(payload, options);
    var views = errors.length ? null : sqxViewsHandoffFromPackage(payload, options);
    var cleaner = errors.length ? null : strategyCleanerDraftFromPackage(payload, options);
    [pgPrefill, pgPreset, views, cleaner].forEach(function(result) {
      if (result && result.ok === false) errors = errors.concat(result.errors || []);
    });
    if (errors.length) {
      return {
        ok: false,
        errors: errors,
        pack: null,
        guardrails: ['no_destination_action_triggered']
      };
    }
    return {
      ok: true,
      errors: [],
      pack: {
        type: BUYER_HANDOFF_PACK_TYPE,
        version: 1,
        created_at: nowIso(options),
        strategy_builder_package: payload,
        workflow: buyerWorkflowSummary(payload),
        handoffs: {
          project_generator_prefill: pgPrefill,
          project_generator_preset_draft: pgPreset,
          sqx_views: views,
          strategy_cleaner: cleaner
        },
        manual_next_steps: [
          'Review Project Generator fields before pressing Generar custom.',
          'Review preset name before pressing Guardar preset.',
          'Review SQX Views columns before pressing Descargar .vw or Guardar preset.',
          'Choose a .sqx folder before pressing Escanear and Procesar seleccion in Strategy Cleaner.',
          'Run StrategyQuant validation manually before making any trading claim.'
        ],
        guardrails: [
          'local_review_pack_only',
          'no_backend_endpoint',
          'no_api_call',
          'no_generation_triggered',
          'no_template_saved',
          'no_scan_triggered',
          'no_cleaning_triggered',
          'no_profitability_claim'
        ]
      },
      guardrails: [
        'pack_prepared_only',
        'no_destination_action_triggered',
        'operator_must_execute_each_destination_manually'
      ]
    };
  }

  function includedHandoffMap(input) {
    var data = input || {};
    var map = {};
    if (data.type === BUYER_HANDOFF_PACK_TYPE) {
      var handoffs = data.handoffs || {};
      REQUIRED_BUYER_HANDOFFS.forEach(function(id) {
        map[id] = !!handoffs[id];
      });
      return map;
    }
    if (data.type === BUYER_HANDOFF_PACK_REVIEW_TYPE) {
      (data.included_handoffs || []).forEach(function(item) {
        map[item.id] = !!item.present;
      });
      return map;
    }
    REQUIRED_BUYER_HANDOFFS.forEach(function(id) {
      map[id] = true;
    });
    return map;
  }

  function guidedBuyerSessionChecklist(input, options) {
    var source = input || {};
    var review = source.type === BUYER_HANDOFF_PACK_REVIEW_TYPE ? source : null;
    var pack = source.type === BUYER_HANDOFF_PACK_TYPE ? source : null;
    var payload = pack ? pack.strategy_builder_package : (source.type === PACKAGE_TYPE ? source : null);
    if (!payload && !review) payload = buildPackage(source, options);
    var assetProfile = payload && payload.asset_profile || {};
    var workflowState = review
      ? normalizeText(review.rebuilt_workflow_state || review.original_workflow_state, 'blocked_operator_review')
      : normalizeText(payload && payload.workflow_state, 'blocked_operator_review');
    var asset = normalizeAsset(review && review.asset || assetProfile.asset);
    var timeframe = normalizeTimeframe(review && review.timeframe || assetProfile.timeframe);
    var reviewConfirmed = workflowState === 'package_exportable' && !(review && review.re_review_required);
    var handoffMap = includedHandoffMap(review || pack || payload);
    var destinationReady = reviewConfirmed ? 'pending' : 'blocked';
    var destinationNote = reviewConfirmed ? 'Ready for manual operator action.' : 'Confirm manual review first.';
    var steps = [
      {
        id: 'manual_review_gate',
        label: 'Confirm manual review gate',
        status: reviewConfirmed ? 'done' : 'pending',
        owner: 'operator',
        action: 'Check the source evidence, asset, timeframe, validation pack and safe-claims boundary.'
      },
      {
        id: 'project_generator_prefill',
        label: 'Prepare Project Generator fields',
        status: handoffMap.project_generator_prefill ? destinationReady : 'blocked',
        owner: 'operator',
        action: 'Press Enviar a Project Generator, review fields and do not generate until they are correct.',
        note: handoffMap.project_generator_prefill ? destinationNote : 'Project Generator prefill handoff missing.'
      },
      {
        id: 'project_generator_generate',
        label: 'Generate custom project manually',
        status: destinationReady,
        owner: 'operator',
        action: 'In Project Generator, press Generar custom manually only after reviewing the prefilled fields.',
        note: destinationNote
      },
      {
        id: 'project_generator_preset',
        label: 'Prepare and save preset manually',
        status: handoffMap.project_generator_preset_draft ? destinationReady : 'blocked',
        owner: 'operator',
        action: 'Press Preparar preset PG, review the preset name and press Guardar preset manually if desired.',
        note: handoffMap.project_generator_preset_draft ? destinationNote : 'Project Generator preset draft missing.'
      },
      {
        id: 'sqx_views_review',
        label: 'Open SQX Views validation review',
        status: handoffMap.sqx_views ? destinationReady : 'blocked',
        owner: 'operator',
        action: 'Press Enviar a SQX Views, review columns and download or save the template manually.',
        note: handoffMap.sqx_views ? destinationNote : 'SQX Views handoff missing.'
      },
      {
        id: 'strategy_cleaner_review',
        label: 'Prepare Strategy Cleaner draft',
        status: handoffMap.strategy_cleaner ? destinationReady : 'blocked',
        owner: 'operator',
        action: 'Press Preparar Cleaner, select the .sqx folder manually, then scan and process manually.',
        note: handoffMap.strategy_cleaner ? destinationNote : 'Strategy Cleaner draft missing.'
      },
      {
        id: 'strategyquant_validation',
        label: 'Run StrategyQuant validation manually',
        status: destinationReady,
        owner: 'operator',
        action: 'Run StrategyQuant validation before making any trading or performance claim.',
        note: destinationNote
      }
    ];
    return {
      ok: true,
      errors: [],
      checklist: {
        type: BUYER_SESSION_CHECKLIST_TYPE,
        version: 1,
        created_at: nowIso(options),
        asset: asset,
        timeframe: timeframe,
        source_type: normalizeText(source.type || (payload && payload.type), 'sqx-edge.strategy-builder-package'),
        workflow_state: workflowState,
        review_required: !reviewConfirmed,
        steps: steps,
        guardrails: [
          'guided_session_only',
          'no_destination_action_triggered',
          'no_local_storage_write',
          'no_backend_endpoint',
          'operator_executes_every_step_manually',
          'no_profitability_claim'
        ]
      },
      guardrails: [
        'checklist_preview_only',
        'no_destination_action_triggered',
        'operator_executes_every_step_manually'
      ]
    };
  }

  function buyerSessionHandoffSummary(input, options) {
    var source = input || {};
    var checklistResult = source.type === BUYER_SESSION_CHECKLIST_TYPE
      ? { ok: true, errors: [], checklist: source }
      : guidedBuyerSessionChecklist(source, options);
    if (!checklistResult.ok) {
      return {
        ok: false,
        errors: checklistResult.errors || ['buyer_session_checklist_failed'],
        summary: null,
        guardrails: ['summary_export_only', 'no_destination_action_triggered']
      };
    }
    var checklist = checklistResult.checklist;
    var steps = checklist.steps || [];
    var counts = steps.reduce(function(acc, step) {
      var status = normalizeText(step.status, 'pending');
      acc[status] = (acc[status] || 0) + 1;
      return acc;
    }, {});
    var nextStep = steps.filter(function(step) { return step.status !== 'done'; })[0] || null;
    return {
      ok: true,
      errors: [],
      summary: {
        type: BUYER_SESSION_SUMMARY_TYPE,
        version: 1,
        created_at: nowIso(options),
        source_type: normalizeText(checklist.type, BUYER_SESSION_CHECKLIST_TYPE),
        asset: normalizeAsset(checklist.asset),
        timeframe: normalizeTimeframe(checklist.timeframe),
        workflow_state: normalizeText(checklist.workflow_state, 'blocked_operator_review'),
        review_required: !!checklist.review_required,
        step_counts: {
          done: counts.done || 0,
          pending: counts.pending || 0,
          blocked: counts.blocked || 0
        },
        next_manual_action: nextStep ? {
          id: nextStep.id,
          label: normalizeText(nextStep.label),
          action: normalizeText(nextStep.action),
          note: normalizeText(nextStep.note)
        } : {
          id: 'operator_validation',
          label: 'Run StrategyQuant validation manually',
          action: 'Validate manually before making any trading claim.',
          note: 'No automatic destination action was triggered.'
        },
        handoff_targets: steps.filter(function(step) { return step.id !== 'manual_review_gate'; }).map(function(step) {
          return {
            id: step.id,
            label: normalizeText(step.label),
            status: normalizeText(step.status, 'pending'),
            owner: normalizeText(step.owner, 'operator')
          };
        }),
        redaction: [
          'no_raw_csv_payloads',
          'no_license_payloads',
          'no_private_keys',
          'no_buyer_identity',
          'no_checkout_payload'
        ],
        guardrails: [
          'summary_export_only',
          'no_destination_action_triggered',
          'no_local_storage_write',
          'no_backend_endpoint',
          'operator_executes_every_step_manually',
          'no_profitability_claim'
        ]
      },
      guardrails: [
        'summary_export_only',
        'no_destination_action_triggered',
        'operator_executes_every_step_manually'
      ]
    };
  }

  function buyerSessionOperatorNotes(input, options) {
    var source = input || {};
    var summaryResult = source.type === BUYER_SESSION_SUMMARY_TYPE
      ? { ok: true, errors: [], summary: source }
      : buyerSessionHandoffSummary(source, options);
    if (!summaryResult.ok) {
      return {
        ok: false,
        errors: summaryResult.errors || ['buyer_session_summary_failed'],
        notes: null,
        guardrails: ['printable_notes_preview_only', 'no_destination_action_triggered']
      };
    }
    var summary = summaryResult.summary || {};
    var asset = normalizeAsset(summary.asset);
    var timeframe = normalizeTimeframe(summary.timeframe);
    var next = summary.next_manual_action || {};
    var handoffLines = (summary.handoff_targets || []).map(function(target) {
      return '[' + normalizeText(target.status, 'pending').toUpperCase() + '] '
        + normalizeText(target.label, target.id || 'manual handoff')
        + ' - owner: ' + normalizeText(target.owner, 'operator');
    });
    if (!handoffLines.length) handoffLines.push('[PENDING] Manual handoff review - owner: operator');
    var redactionLines = (summary.redaction || []).map(function(item) { return '- ' + normalizeText(item); });
    var guardrailLines = (summary.guardrails || []).map(function(item) { return '- ' + normalizeText(item); });
    var sections = [
      {
        id: 'session_scope',
        title: 'Session scope',
        lines: [
          'Asset/timeframe: ' + asset + ' ' + timeframe,
          'Workflow state: ' + normalizeText(summary.workflow_state, 'blocked_operator_review'),
          'Review required: ' + (summary.review_required ? 'yes' : 'no'),
          'Step counts: done ' + ((summary.step_counts && summary.step_counts.done) || 0)
            + ', pending ' + ((summary.step_counts && summary.step_counts.pending) || 0)
            + ', blocked ' + ((summary.step_counts && summary.step_counts.blocked) || 0)
        ]
      },
      {
        id: 'next_manual_action',
        title: 'Next manual action',
        lines: [
          normalizeText(next.label, 'Run StrategyQuant validation manually'),
          normalizeText(next.action, 'Validate manually before making any trading claim.'),
          normalizeText(next.note, 'No automatic destination action was triggered.'),
          'No automatic destination action was triggered.'
        ]
      },
      {
        id: 'handoff_targets',
        title: 'Handoff targets',
        lines: handoffLines
      },
      {
        id: 'redaction_boundary',
        title: 'Redaction boundary',
        lines: redactionLines.length ? redactionLines : ['- no_sensitive_payloads']
      },
      {
        id: 'operator_guardrails',
        title: 'Operator guardrails',
        lines: guardrailLines.length ? guardrailLines : ['- operator_executes_every_step_manually']
      }
    ];
    var printLines = ['SQX Edge buyer session notes - ' + asset + ' ' + timeframe, ''];
    sections.forEach(function(section) {
      printLines.push(section.title);
      section.lines.forEach(function(line) { printLines.push(line); });
      printLines.push('');
    });
    return {
      ok: true,
      errors: [],
      notes: {
        type: BUYER_SESSION_NOTES_TYPE,
        version: 1,
        created_at: nowIso(options),
        source_type: normalizeText(summary.type, BUYER_SESSION_SUMMARY_TYPE),
        asset: asset,
        timeframe: timeframe,
        workflow_state: normalizeText(summary.workflow_state, 'blocked_operator_review'),
        review_required: !!summary.review_required,
        print_ready: true,
        format: 'plain_text',
        sections: sections,
        print_text: printLines.join('\n').trim(),
        redaction: (summary.redaction || []).slice(0),
        guardrails: [
          'printable_notes_only',
          'no_destination_action_triggered',
          'no_local_storage_write',
          'no_backend_endpoint',
          'operator_executes_every_step_manually',
          'no_profitability_claim'
        ]
      },
      guardrails: [
        'printable_notes_preview_only',
        'no_destination_action_triggered',
        'operator_executes_every_step_manually'
      ]
    };
  }

  function supportCaseId(asset, timeframe, createdAt) {
    var stamp = normalizeText(createdAt, nowIso()).replace(/[^0-9A-Za-z]/g, '').slice(0, 14);
    return ['SB', normalizeAsset(asset), normalizeTimeframe(timeframe), stamp].join('-');
  }

  function buyerSessionSupportCaseBundle(input, options) {
    var source = input || {};
    var notesResult = source.type === BUYER_SESSION_NOTES_TYPE
      ? { ok: true, errors: [], notes: source }
      : buyerSessionOperatorNotes(source, options);
    if (!notesResult.ok) {
      return {
        ok: false,
        errors: notesResult.errors || ['buyer_session_notes_failed'],
        bundle: null,
        guardrails: ['support_case_bundle_only', 'no_destination_action_triggered']
      };
    }
    var notes = notesResult.notes || {};
    var createdAt = nowIso(options);
    var asset = normalizeAsset(notes.asset);
    var timeframe = normalizeTimeframe(notes.timeframe);
    var sections = (notes.sections || []).map(function(section) {
      return {
        id: normalizeText(section.id),
        title: normalizeText(section.title),
        line_count: (section.lines || []).length
      };
    });
    return {
      ok: true,
      errors: [],
      bundle: {
        type: BUYER_SESSION_SUPPORT_CASE_TYPE,
        version: 1,
        created_at: createdAt,
        case_id: supportCaseId(asset, timeframe, createdAt),
        source_type: normalizeText(notes.type, BUYER_SESSION_NOTES_TYPE),
        asset: asset,
        timeframe: timeframe,
        workflow_state: normalizeText(notes.workflow_state, 'blocked_operator_review'),
        review_required: !!notes.review_required,
        support_priority: notes.review_required ? 'manual_review_required' : 'standard_setup',
        operator_notes: {
          format: 'plain_text',
          print_ready: !!notes.print_ready,
          text: normalizeText(notes.print_text)
        },
        section_manifest: sections,
        support_questions: [
          'Has the operator confirmed the manual review gate?',
          'Which destination step is blocked or pending?',
          'Were Project Generator, SQX Views and Strategy Cleaner actions executed manually?',
          'Has StrategyQuant validation been run before any trading or performance claim?'
        ],
        attachment_manifest: [
          {
            id: 'printable_operator_notes',
            format: 'txt',
            included: true,
            sensitive_payload: false
          },
          {
            id: 'buyer_session_summary',
            format: 'json',
            included: false,
            sensitive_payload: false,
            note: 'Regenerate locally from Strategy Builder if the support case needs structured fields.'
          },
          {
            id: 'full_strategy_builder_package',
            format: 'json',
            included: false,
            sensitive_payload: true,
            note: 'Do not attach full package unless the operator explicitly redacts it first.'
          }
        ],
        redaction: (notes.redaction || []).concat([
          'no_full_strategy_builder_package',
          'no_support_customer_identity',
          'no_private_commercial_payload'
        ]),
        guardrails: [
          'support_case_bundle_only',
          'no_destination_action_triggered',
          'no_local_storage_write',
          'no_backend_endpoint',
          'no_remote_ticket_created',
          'operator_executes_every_step_manually',
          'no_profitability_claim'
        ]
      },
      guardrails: [
        'support_case_bundle_only',
        'no_destination_action_triggered',
        'no_remote_ticket_created'
      ]
    };
  }

  function buyerSessionSupportResolutionChecklist(input, options) {
    var source = input || {};
    var caseResult = source.type === BUYER_SESSION_SUPPORT_CASE_TYPE
      ? { ok: true, errors: [], bundle: source }
      : buyerSessionSupportCaseBundle(source, options);
    if (!caseResult.ok) {
      return {
        ok: false,
        errors: caseResult.errors || ['buyer_support_case_failed'],
        checklist: null,
        guardrails: ['support_resolution_checklist_only', 'no_destination_action_triggered']
      };
    }
    var bundle = caseResult.bundle || {};
    var reviewRequired = !!bundle.review_required;
    var blockedDestination = normalizeText(bundle.workflow_state, 'blocked_operator_review') !== 'package_exportable';
    var steps = [
      {
        id: 'case_identity_confirmed',
        label: 'Confirm support case identity',
        status: 'pending',
        owner: 'operator',
        action: 'Match case id, asset, timeframe and buyer session context before taking any action.'
      },
      {
        id: 'manual_review_gate_resolved',
        label: 'Resolve manual review gate',
        status: reviewRequired ? 'blocked' : 'pending',
        owner: 'operator',
        action: 'Confirm the operator has reviewed the source evidence, package state and safe-claims boundary.',
        note: reviewRequired ? 'Manual review is still required before support can close the case.' : 'Review gate is not marked as required in the bundle.'
      },
      {
        id: 'blocked_step_identified',
        label: 'Identify blocked or pending destination step',
        status: blockedDestination ? 'pending' : 'done',
        owner: 'operator',
        action: 'Use support questions and section manifest to locate the pending Project Generator, SQX Views, Cleaner or StrategyQuant step.'
      },
      {
        id: 'safe_attachments_checked',
        label: 'Check safe attachment boundary',
        status: 'pending',
        owner: 'operator',
        action: 'Attach only printable notes or redacted summary unless the full package is explicitly reviewed and redacted.'
      },
      {
        id: 'buyer_response_prepared',
        label: 'Prepare buyer response',
        status: 'pending',
        owner: 'operator',
        action: 'Explain the next manual step without profitability, trading or automation claims.'
      },
      {
        id: 'strategyquant_validation_confirmed',
        label: 'Confirm StrategyQuant validation boundary',
        status: 'pending',
        owner: 'operator',
        action: 'Do not close as validated unless StrategyQuant validation has been run manually.'
      },
      {
        id: 'case_close_or_escalate',
        label: 'Close or escalate support case',
        status: reviewRequired ? 'blocked' : 'pending',
        owner: 'operator',
        action: 'Close only after manual resolution evidence exists; otherwise escalate internally with redacted artifacts.'
      }
    ];
    var counts = steps.reduce(function(acc, step) {
      acc[step.status] = (acc[step.status] || 0) + 1;
      return acc;
    }, {});
    return {
      ok: true,
      errors: [],
      checklist: {
        type: BUYER_SESSION_RESOLUTION_TYPE,
        version: 1,
        created_at: nowIso(options),
        case_id: normalizeText(bundle.case_id, supportCaseId(bundle.asset, bundle.timeframe)),
        source_type: normalizeText(bundle.type, BUYER_SESSION_SUPPORT_CASE_TYPE),
        asset: normalizeAsset(bundle.asset),
        timeframe: normalizeTimeframe(bundle.timeframe),
        workflow_state: normalizeText(bundle.workflow_state, 'blocked_operator_review'),
        support_priority: normalizeText(bundle.support_priority, reviewRequired ? 'manual_review_required' : 'standard_setup'),
        review_required: reviewRequired,
        resolution_ready: !reviewRequired && !blockedDestination,
        step_counts: {
          done: counts.done || 0,
          pending: counts.pending || 0,
          blocked: counts.blocked || 0
        },
        steps: steps,
        close_conditions: [
          'manual_review_gate_confirmed',
          'support_question_answered',
          'safe_attachment_boundary_respected',
          'buyer_response_has_no_profitability_claim',
          'strategyquant_validation_boundary_confirmed'
        ],
        escalation_conditions: [
          'manual_review_required',
          'destination_step_still_blocked',
          'full_package_requested_without_redaction',
          'buyer_requests_profitability_or_trading_claim'
        ],
        guardrails: [
          'support_resolution_checklist_only',
          'no_destination_action_triggered',
          'no_local_storage_write',
          'no_backend_endpoint',
          'no_remote_ticket_created',
          'operator_executes_every_step_manually',
          'no_profitability_claim'
        ]
      },
      guardrails: [
        'support_resolution_checklist_only',
        'no_destination_action_triggered',
        'no_remote_ticket_created'
      ]
    };
  }

  function artifactTimestamp(value) {
    var data = value || {};
    return normalizeText(data.created_at || data.imported_at || data.generated_at || data.exported_at || '');
  }

  function artifactTimeframe(value) {
    var text = normalizeText(value, '');
    return text ? normalizeTimeframe(text) : '';
  }

  function artifactAsset(data) {
    var value = data || {};
    var profile = value.asset_profile || {};
    return normalizeAsset(value.asset || profile.asset || '');
  }

  function artifactTf(data) {
    var value = data || {};
    var profile = value.asset_profile || {};
    return artifactTimeframe(value.timeframe || profile.timeframe || '');
  }

  function evidenceEntry(id, label, payload, required) {
    var data = payload || null;
    var state = data ? normalizeText(data.workflow_state || data.rebuilt_workflow_state || data.original_workflow_state || '') : '';
    return {
      id: id,
      label: label,
      required: !!required,
      present: !!data,
      type: data ? normalizeText(data.type || '') : '',
      workflow_state: state,
      asset: data ? artifactAsset(data) : '',
      timeframe: data ? artifactTf(data) : '',
      created_at: data ? artifactTimestamp(data) : '',
      redaction: 'reduced_metadata_only'
    };
  }

  function directArtifactByType(source, type) {
    return source && source.type === type ? source : null;
  }

  function sourcePackageFromArtifacts(artifacts, source) {
    var direct = directArtifactByType(source, PACKAGE_TYPE);
    var pack = artifacts.buyer_handoff_pack || artifacts.buyerHandoffPack || directArtifactByType(source, BUYER_HANDOFF_PACK_TYPE);
    return artifacts.package
      || artifacts.strategy_builder_package
      || artifacts.strategyBuilderPackage
      || direct
      || (pack && pack.strategy_builder_package)
      || null;
  }

  function handoffEvidenceIndex(input, options) {
    var source = input || {};
    var artifacts = source.artifacts || source;
    var pack = artifacts.buyer_handoff_pack
      || artifacts.buyerHandoffPack
      || directArtifactByType(source, BUYER_HANDOFF_PACK_TYPE);
    var handoffs = pack && pack.handoffs || {};
    var payload = sourcePackageFromArtifacts(artifacts, source);
    var review = artifacts.buyer_pack_review
      || artifacts.buyerPackReview
      || directArtifactByType(source, BUYER_HANDOFF_PACK_REVIEW_TYPE);
    var checklist = artifacts.buyer_session_checklist
      || artifacts.buyerSessionChecklist
      || directArtifactByType(source, BUYER_SESSION_CHECKLIST_TYPE);
    var summary = artifacts.buyer_session_summary
      || artifacts.buyerSessionSummary
      || directArtifactByType(source, BUYER_SESSION_SUMMARY_TYPE);
    var notes = artifacts.buyer_session_notes
      || artifacts.buyerSessionNotes
      || directArtifactByType(source, BUYER_SESSION_NOTES_TYPE);
    var supportCase = artifacts.buyer_support_case
      || artifacts.buyerSupportCase
      || directArtifactByType(source, BUYER_SESSION_SUPPORT_CASE_TYPE);
    var resolution = artifacts.buyer_resolution_checklist
      || artifacts.buyerResolutionChecklist
      || directArtifactByType(source, BUYER_SESSION_RESOLUTION_TYPE);
    var entries = [
      evidenceEntry('strategy_builder_package', 'Strategy Builder package', payload, true),
      evidenceEntry('project_generator_prefill', 'Project Generator prefill', handoffs.project_generator_prefill, true),
      evidenceEntry('project_generator_preset_draft', 'Project Generator preset draft', handoffs.project_generator_preset_draft, true),
      evidenceEntry('sqx_views', 'SQX Views validation handoff', handoffs.sqx_views, true),
      evidenceEntry('strategy_cleaner', 'Strategy Cleaner draft', handoffs.strategy_cleaner, true),
      evidenceEntry('buyer_handoff_pack', 'Buyer handoff pack', pack, true),
      evidenceEntry('buyer_pack_import_review', 'Buyer pack import review', review, false),
      evidenceEntry('buyer_session_checklist', 'Buyer session checklist', checklist, true),
      evidenceEntry('buyer_session_summary', 'Buyer session summary', summary, false),
      evidenceEntry('buyer_session_notes', 'Buyer session printable notes', notes, false),
      evidenceEntry('buyer_support_case', 'Buyer support case bundle', supportCase, false),
      evidenceEntry('buyer_resolution_checklist', 'Buyer support resolution checklist', resolution, false)
    ];
    var missingRequired = entries.filter(function(entry) {
      return entry.required && !entry.present;
    }).map(function(entry) { return entry.id; });
    var presentCount = entries.filter(function(entry) { return entry.present; }).length;
    var asset = artifactAsset(payload || pack || checklist || summary || notes || supportCase || resolution);
    var timeframe = artifactTf(payload || pack || checklist || summary || notes || supportCase || resolution);
    return {
      ok: missingRequired.length === 0,
      errors: missingRequired.map(function(id) { return 'missing_required_evidence:' + id; }),
      index: {
        type: EVIDENCE_HANDOFF_INDEX_TYPE,
        version: 1,
        created_at: nowIso(options),
        asset: asset,
        timeframe: timeframe,
        source_type: normalizeText(source.type || artifacts.source_type || 'strategy_builder_session'),
        workflow_state: normalizeText(
          (payload && payload.workflow_state)
            || (review && review.rebuilt_workflow_state)
            || (checklist && checklist.workflow_state)
            || 'unknown'
        ),
        summary: {
          total_entries: entries.length,
          present_entries: presentCount,
          required_entries: entries.filter(function(entry) { return entry.required; }).length,
          missing_required_entries: missingRequired.length,
          ready_for_buyer_handoff: missingRequired.length === 0
        },
        missing_required_handoffs: missingRequired,
        entries: entries,
        privacy_boundary: [
          'reduced_metadata_only',
          'no_buyer_identity',
          'no_raw_csv_payloads',
          'no_local_storage_write',
          'no_backend_endpoint',
          'no_remote_ticket_created',
          'no_profitability_claim'
        ],
        guardrails: [
          'evidence_index_only',
          'no_destination_action_triggered',
          'no_local_storage_write',
          'no_backend_endpoint',
          'operator_executes_every_step_manually'
        ]
      },
      guardrails: [
        'evidence_index_only',
        'no_destination_action_triggered',
        'no_remote_call'
      ]
    };
  }

  function buyerWorkflowSummary(input, options) {
    var payload = input && input.type === PACKAGE_TYPE ? input : buildPackage(input || {}, options);
    var review = reviewChecklistSummary(payload);
    var exportable = payload && payload.workflow_state === 'package_exportable';
    var hasSource = payload && payload.source_mode && payload.source_mode !== 'blank';
    var states = {
      source: hasSource,
      review: review.ready,
      package: exportable,
      project_generator: exportable,
      sqx_views: exportable,
      operator: false
    };
    return {
      ready: exportable,
      workflow_state: payload ? payload.workflow_state : 'blocked_missing_source',
      next_action: exportable
        ? 'Prepare a handoff, then run StrategyQuant actions manually.'
        : 'Complete the manual review gate before preparing buyer handoffs.',
      steps: BUYER_WORKFLOW_STEPS.map(function(step) {
        return {
          id: step.id,
          label: step.label,
          status: states[step.id] ? 'done' : 'pending',
          note: states[step.id] ? 'Ready' : step.blocked
        };
      })
    };
  }

  function handoffAuditEntry(target, input, result, options) {
    var payload = input && input.type === PACKAGE_TYPE ? input : buildPackage(input || {}, options);
    var assetProfile = payload && payload.asset_profile || {};
    var handoffResult = result || {};
    return {
      type: 'sqx-edge.strategy-builder-audit-entry',
      version: 1,
      created_at: nowIso(options),
      target: normalizeText(target, 'unknown'),
      ok: handoffResult.ok !== false,
      workflow_state: payload ? payload.workflow_state : 'unknown',
      asset: normalizeAsset(assetProfile.asset),
      timeframe: normalizeTimeframe(assetProfile.timeframe),
      guardrails: (handoffResult.guardrails || []).concat([
        'visible_session_trace',
        'no_local_storage_write',
        'no_remote_call',
        'operator_manual_next_step'
      ]),
      manual_next_action: 'Review the destination screen and press the final action manually.'
    };
  }

  SQX.strategyBuilderCore = SQX.strategyBuilderCore || {
    archetypes: ARCHETYPES,
    blockedStates: BLOCKED_STATES,
    buildContext: buildContext,
    buildPackage: buildPackage,
    buyerHandoffPackReview: buyerHandoffPackReview,
    buyerSessionSupportResolutionChecklist: buyerSessionSupportResolutionChecklist,
    buyerSessionSupportCaseBundle: buyerSessionSupportCaseBundle,
    buyerSessionOperatorNotes: buyerSessionOperatorNotes,
    buyerSessionHandoffSummary: buyerSessionHandoffSummary,
    buyerWorkflowSummary: buyerWorkflowSummary,
    defaultValidationPack: defaultValidationPack,
    guidedBuyerSessionChecklist: guidedBuyerSessionChecklist,
    handoffEvidenceIndex: handoffEvidenceIndex,
    handoffAuditEntry: handoffAuditEntry,
    importPayload: importPayload,
    projectGeneratorPrefillFromPackage: projectGeneratorPrefillFromPackage,
    projectGeneratorPresetDraftFromPackage: projectGeneratorPresetDraftFromPackage,
    reviewChecklistSummary: reviewChecklistSummary,
    sampleCvcHandoff: sampleCvcHandoff,
    sourceModes: SOURCE_MODES,
    sqxViewsHandoffFromPackage: sqxViewsHandoffFromPackage,
    states: WORKFLOW_STATES,
    strategyCleanerDraftFromPackage: strategyCleanerDraftFromPackage,
    supportedAsset: supportedAsset,
    validateImportPayload: validateImportPayload,
    unifiedBuyerHandoffPackFromPackage: unifiedBuyerHandoffPackFromPackage
  };

  if (SQX.registerModule) {
    SQX.registerModule('strategy-builder-core', SQX.strategyBuilderCore);
  }
})(window);

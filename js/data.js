// ============================================================
// SQX Dashboard - compatibility data layer
// Source of truth lives in js/manifest-data.js and sqx-edge-tool/config/*.json.
// This file keeps the existing dashboard code working with global names.
// ============================================================

var SQX_GLOBAL = typeof window !== 'undefined' ? window : globalThis;
var SQX_MANIFEST = SQX_GLOBAL.SQX_MANIFEST || {};
var SQX_UI = SQX_MANIFEST.ui || {};
var SQX_PLAN = SQX_MANIFEST.plan || {};
var SQX_ASSET_MANIFEST = SQX_MANIFEST.assets || {};
var SQX_STRATEGY_MANIFEST = SQX_MANIFEST.strategies || {};

var CAT_META = SQX_UI.categories || {};
var ASSETS = SQX_ASSET_MANIFEST.assets || [];
var FILTROS = SQX_UI.filtros || [];
var RATING_ORDER = SQX_UI.ratingOrder || {};
var CAT_KEYS = Object.keys(CAT_META);
var SQX_CONFIG_DESC = SQX_UI.sqxConfigDesc || {};
var MACRO_EVENTS = SQX_UI.macroEvents || [];
var APPROACH_HINTS = SQX_UI.approachHints || {};
var CAT_TO_BS = SQX_UI.catToBs || {};
var STRATEGIES = SQX_STRATEGY_MANIFEST.strategies || [];
var PLAN_MININGS = SQX_PLAN.minings || [];
var PHASE_META = SQX_PLAN.phases || {};
var FUNNEL_STAGES_DEFAULT = (SQX_UI.pipeline && SQX_UI.pipeline.funnelStagesDefault) || [];
var FUNNEL_PRELOAD = (SQX_UI.pipeline && SQX_UI.pipeline.funnelPreload) || {};
var BS_TO_PRIORITY_CAT = SQX_UI.bsToPriorityCat || {};
var PRIORITY_CAT_TO_BS = SQX_UI.priorityCatToBs || {};

Object.assign(SQX_GLOBAL, {
  CAT_META,
  ASSETS,
  FILTROS,
  RATING_ORDER,
  CAT_KEYS,
  SQX_CONFIG_DESC,
  MACRO_EVENTS,
  APPROACH_HINTS,
  CAT_TO_BS,
  STRATEGIES,
  PLAN_MININGS,
  PHASE_META,
  FUNNEL_STAGES_DEFAULT,
  FUNNEL_PRELOAD,
  BS_TO_PRIORITY_CAT,
  PRIORITY_CAT_TO_BS,
});

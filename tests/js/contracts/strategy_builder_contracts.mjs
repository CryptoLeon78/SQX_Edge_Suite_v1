import { assert, Element, createLoadedSandbox } from './harness.mjs';

const { SQX, document, sandbox } = createLoadedSandbox([
  'app/js/modules/ui.js',
  'app/js/modules/strategy-builder-core.js',
  'app/js/modules/strategy-builder.js',
]);

sandbox.SQX_MANIFEST = {
  assets: {
    assets: [
      { id: 'EURUSD', type: 'forex', sub: 'Major' },
      { id: 'US500', type: 'index', sub: 'SP500' },
    ],
  },
};

const core = SQX.strategyBuilderCore;
assert.ok(core, 'strategy builder core should register');
assert.equal(core.states[core.states.length - 1], 'package_exportable');
assert.ok(core.sourceModes.includes('cvc_handoff'));
assert.ok(core.archetypes.trend_following.indicators.includes('EMA'));

const blocked = core.buildPackage({
  source_mode: 'blank',
  asset: 'EURUSD',
  timeframe: 'H1',
  idea_archetype: 'trend_following',
  validation_pack_id: 'robustness',
  project_profile_id: 'starter-forex-h1-balanced',
});
assert.equal(blocked.type, 'sqx-edge.strategy-builder-package');
assert.equal(blocked.workflow_state, 'blocked_operator_review');
assert.equal(blocked.project_generator_handoff.auto_run_bulk_generation, false);
assert.match(blocked.blocked_claims.join(' '), /No profitability claim/);

const unsupported = core.buildPackage({
  source_mode: 'blank',
  asset: 'FAKEPAIR',
  timeframe: 'H1',
  idea_archetype: 'trend_following',
  validation_pack_id: 'robustness',
  operator_reviewed: true,
});
assert.equal(unsupported.workflow_state, 'blocked_unsupported_asset');

const cvcHandoff = core.sampleCvcHandoff();
const ready = core.buildPackage({
  source_mode: 'cvc_handoff',
  source_handoff: cvcHandoff,
  timeframe: 'H1',
  idea_archetype: 'trend_following',
  validation_pack_id: 'robustness',
  project_profile_id: 'starter-forex-h1-balanced',
  operator_reviewed: true,
}, { createdAt: '2026-05-09T00:00:00.000Z' });
assert.equal(ready.workflow_state, 'package_exportable');
assert.equal(ready.asset_profile.asset, 'EURUSD');
assert.equal(ready.source_summary.candidate, 'Challenger A');
assert.equal(ready.views_handoff.validation_pack_id, 'robustness');
assert.equal(JSON.stringify(ready).includes('raw_csv'), false);

[
  'sb-source-mode',
  'sb-asset',
  'sb-timeframe',
  'sb-archetype',
  'sb-validation-pack',
  'sb-project-profile',
  'sb-reviewed',
  'sb-build-btn',
  'sb-sample-cvc-btn',
  'sb-clear-btn',
  'sb-export-btn',
  'sb-status',
  'sb-package-preview',
  'sb-state',
  'sb-source',
  'sb-asset-out',
  'sb-check-count',
].forEach(id => document.add(new Element(id)));

const selectDefaults = {
  'sb-source-mode': 'blank',
  'sb-asset': 'EURUSD',
  'sb-timeframe': 'H1',
  'sb-archetype': 'trend_following',
  'sb-validation-pack': 'robustness',
  'sb-project-profile': 'starter-forex-h1-balanced',
};
Object.entries(selectDefaults).forEach(([id, value]) => {
  document.getElementById(id).value = value;
});

const ui = SQX.strategyBuilder;
assert.ok(ui, 'strategy builder UI should register');
assert.equal(ui.init({ document }), true);
assert.equal(document.getElementById('sb-state').textContent, 'blocked_operator_review');

document.getElementById('sb-sample-cvc-btn').click();
assert.equal(document.getElementById('sb-state').textContent, 'package_exportable');
assert.equal(document.getElementById('sb-source').textContent, 'cvc_handoff');
assert.match(document.getElementById('sb-package-preview').textContent, /sqx-edge\.strategy-builder-package/);
assert.match(document.getElementById('sb-status').textContent, /Package ready/);

document.getElementById('sb-clear-btn').click();
assert.equal(document.getElementById('sb-state').textContent, 'blocked_operator_review');

console.log('strategy builder contracts ok');

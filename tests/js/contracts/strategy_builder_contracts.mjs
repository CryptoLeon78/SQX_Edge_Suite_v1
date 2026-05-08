import { assert, Element, createLoadedSandbox } from './harness.mjs';

const { SQX, document, sandbox } = createLoadedSandbox([
  'app/js/modules/ui.js',
  'app/js/modules/project-generator-core.js',
  'app/js/modules/project-generator-config.js',
  'app/js/modules/project-generator-dom.js',
  'app/js/modules/strategy-builder-core.js',
  'app/js/modules/strategy-builder.js',
  'app/js/modules/view-creator.js',
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
assert.equal(typeof core.importPayload, 'function');
assert.equal(typeof core.projectGeneratorPrefillFromPackage, 'function');
assert.equal(typeof core.projectGeneratorPresetDraftFromPackage, 'function');
assert.equal(typeof core.reviewChecklistSummary, 'function');
assert.equal(typeof core.sqxViewsHandoffFromPackage, 'function');
assert.equal(typeof core.buyerWorkflowSummary, 'function');
assert.equal(typeof core.handoffAuditEntry, 'function');
assert.equal(typeof core.strategyCleanerDraftFromPackage, 'function');
assert.equal(typeof core.validateImportPayload, 'function');

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
const pgPrefill = core.projectGeneratorPrefillFromPackage(ready);
assert.equal(pgPrefill.ok, true);
assert.equal(pgPrefill.config.asset, 'EURUSD');
assert.equal(pgPrefill.config.tf, 'H1');
assert.equal(pgPrefill.config.bs, 'BS_Tendencia');
assert.equal(pgPrefill.config.dir, 'both');
assert.equal(pgPrefill.guardrails.includes('no_generation_triggered'), true);
assert.equal(core.projectGeneratorPrefillFromPackage(blocked).ok, false);
const reviewSummary = core.reviewChecklistSummary(ready);
assert.equal(reviewSummary.ready, true);
assert.equal(reviewSummary.confirmed, 7);
const presetDraft = core.projectGeneratorPresetDraftFromPackage(ready);
assert.equal(presetDraft.ok, true);
assert.equal(presetDraft.preset_name, 'SB EURUSD H1 trend following');
assert.equal(presetDraft.guardrails.includes('no_auto_save'), true);
const viewsHandoff = core.sqxViewsHandoffFromPackage(ready);
assert.equal(viewsHandoff.ok, true);
assert.equal(viewsHandoff.handoff.preset, 'robustness');
assert.equal(viewsHandoff.handoff.viewName, 'SB EURUSD H1 Robustness');
assert.equal(viewsHandoff.handoff.validation_pack_id, 'robustness');
assert.equal(viewsHandoff.guardrails.includes('no_template_saved'), true);
assert.equal(core.sqxViewsHandoffFromPackage(blocked).ok, false);
const workflowSummary = core.buyerWorkflowSummary(ready);
assert.equal(workflowSummary.ready, true);
assert.equal(workflowSummary.steps.filter(step => step.status === 'done').length, 5);
assert.match(workflowSummary.next_action, /Prepare a handoff/);
const auditEntry = core.handoffAuditEntry('SQX Views', ready, viewsHandoff, { createdAt: '2026-05-09T01:15:00.000Z' });
assert.equal(auditEntry.type, 'sqx-edge.strategy-builder-audit-entry');
assert.equal(auditEntry.target, 'SQX Views');
assert.equal(auditEntry.asset, 'EURUSD');
assert.equal(auditEntry.guardrails.includes('no_local_storage_write'), true);
const cleanerDraft = core.strategyCleanerDraftFromPackage(ready);
assert.equal(cleanerDraft.ok, true);
assert.equal(cleanerDraft.draft.remove_exit_bars, true);
assert.equal(cleanerDraft.draft.rename_institutional, true);
assert.equal(cleanerDraft.draft.rename_pattern, '{asset}_{tf}_{dir}_{id}');
assert.equal(cleanerDraft.guardrails.includes('no_cleaning_triggered'), true);
assert.equal(core.strategyCleanerDraftFromPackage(blocked).ok, false);

const importedPackage = core.importPayload(JSON.stringify(ready), { createdAt: '2026-05-09T01:00:00.000Z' });
assert.equal(importedPackage.ok, true);
assert.equal(importedPackage.package.type, 'sqx-edge.strategy-builder-package');
assert.equal(importedPackage.package.workflow_state, 'blocked_operator_review');
assert.equal(importedPackage.package.source_summary.candidate, 'Challenger A');
assert.equal(importedPackage.package.import_metadata.re_review_required, true);
assert.equal(importedPackage.model.operator_reviewed, false);

const reviewedImport = core.importPayload(ready, { operatorReviewed: true, createdAt: '2026-05-09T01:05:00.000Z' });
assert.equal(reviewedImport.ok, true);
assert.equal(reviewedImport.package.workflow_state, 'package_exportable');
assert.equal(reviewedImport.package.import_metadata.re_review_required, false);

const importedHandoff = core.importPayload(cvcHandoff, { createdAt: '2026-05-09T01:10:00.000Z' });
assert.equal(importedHandoff.ok, true);
assert.equal(importedHandoff.model.source_mode, 'cvc_handoff');
assert.equal(importedHandoff.package.asset_profile.asset, 'EURUSD');
assert.equal(importedHandoff.package.workflow_state, 'blocked_operator_review');

const blockedImport = core.importPayload({
  type: 'sqx-edge.strategy-builder-package',
  version: 1,
  raw_csv: 'forbidden',
});
assert.equal(blockedImport.ok, false);
assert.match(blockedImport.errors.join(' '), /forbidden_raw_payload_keys/);

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
  'sb-import-btn',
  'sb-import-file',
  'sb-send-pg-btn',
  'sb-prepare-preset-btn',
  'sb-send-views-btn',
  'sb-prepare-cleaner-btn',
  'sb-clear-btn',
  'sb-export-btn',
  'sb-status',
  'sb-package-preview',
  'sb-review-list',
  'sb-workflow-steps',
  'sb-audit-list',
  'sb-state',
  'sb-source',
  'sb-asset-out',
  'sb-check-count',
].forEach(id => document.add(new Element(id)));
document.addTab('strategybuilder', true);
document.addTab('projectgen', false);
document.addTab('views', false);
[
  'pg-custom-name',
  'pg-custom-asset',
  'pg-custom-tf',
  'pg-custom-bs',
  'pg-custom-dir',
  'pg-custom-capa',
  'pg-custom-template',
  'pg-custom-preset-name',
  'pg-custom-status',
  'pg-log',
  'cln-dir',
  'cln-recursive',
  'cln-opt-eab',
  'cln-opt-rename',
  'cln-pattern',
  'cln-pattern-wrap',
  'cln-info',
].forEach(id => document.add(new Element(id)));
[
  'vc-view-name',
  'vc-year-count',
  'vc-sample-start',
  'vc-group-mode',
  'vc-include-total',
  'vc-preview',
  'vc-selected-count',
  'vc-column-count',
  'vc-year-range',
  'vc-preview-title',
  'vc-mode-label',
  'vc-status',
].forEach(id => document.add(new Element(id)));
document.getElementById('vc-include-total').checked = true;
document.getElementById('vc-group-mode').value = 'by_year';

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
assert.match(document.getElementById('sb-workflow-steps').innerHTML, /Manual review confirmed/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Sin handoffs preparados/);

document.getElementById('sb-sample-cvc-btn').click();
assert.equal(document.getElementById('sb-state').textContent, 'package_exportable');
assert.equal(document.getElementById('sb-source').textContent, 'cvc_handoff');
assert.match(document.getElementById('sb-package-preview').textContent, /sqx-edge\.strategy-builder-package/);
assert.match(document.getElementById('sb-status').textContent, /Package ready/);
assert.match(document.getElementById('sb-workflow-steps').innerHTML, /SQX Views validation available/);
const viewPresetCountBefore = SQX.viewCreator.getSavedPresets().length;
document.getElementById('sb-send-views-btn').click();
assert.equal(document.getElementById('tab-views').style.display, 'block');
assert.equal(document.getElementById('vc-view-name').value, 'SB EURUSD H1 Robustness');
assert.ok(Number(document.getElementById('vc-column-count').textContent) > 104);
assert.match(document.getElementById('vc-status').textContent, /Handoff cargado/);
assert.equal(SQX.viewCreator.getSavedPresets().length, viewPresetCountBefore);
assert.match(document.getElementById('sb-status').textContent, /No template was saved/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /SQX Views/);
document.getElementById('sb-send-pg-btn').click();
assert.equal(document.getElementById('tab-projectgen').style.display, 'block');
assert.equal(document.getElementById('pg-custom-name').value, 'SB_EURUSD_H1_trend_following');
assert.equal(document.getElementById('pg-custom-asset').value, 'EURUSD');
assert.equal(document.getElementById('pg-custom-tf').value, 'H1');
assert.equal(document.getElementById('pg-custom-bs').value, 'BS_Tendencia');
assert.equal(document.getElementById('pg-custom-status').textContent, 'Prefill desde Strategy Builder. Revisa y pulsa Generar custom manualmente.');
assert.match(document.getElementById('sb-review-list').innerHTML, /source evidence has been reviewed/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Project Generator/);
document.getElementById('sb-prepare-preset-btn').click();
assert.equal(document.getElementById('pg-custom-preset-name').value, 'SB EURUSD H1 trend following');
assert.equal(document.getElementById('pg-custom-status').textContent, 'Preset preparado desde Strategy Builder. Revisa y pulsa Guardar preset manualmente.');
assert.match(document.getElementById('pg-log').textContent, /Guardado manual pendiente/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /PG Preset Draft/);
document.getElementById('sb-prepare-cleaner-btn').click();
assert.equal(document.getElementById('tab-projectgen').style.display, 'block');
assert.equal(document.getElementById('cln-recursive').checked, true);
assert.equal(document.getElementById('cln-opt-eab').checked, true);
assert.equal(document.getElementById('cln-opt-rename').checked, true);
assert.equal(document.getElementById('cln-pattern').value, '{asset}_{tf}_{dir}_{id}');
assert.equal(document.getElementById('cln-info').textContent, 'Draft desde Strategy Builder: elige carpeta .sqx, pulsa Escanear y procesa manualmente.');
assert.match(document.getElementById('pg-log').textContent, /limpieza manual pendientes/);
assert.match(document.getElementById('sb-status').textContent, /No scan or cleanup/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Strategy Cleaner/);

const importedUiResult = ui.importText(JSON.stringify(ready), { document });
assert.equal(importedUiResult.ok, true);
assert.equal(document.getElementById('sb-state').textContent, 'blocked_operator_review');
assert.match(document.getElementById('sb-status').textContent, /Confirm manual review/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Import JSON/);
document.getElementById('sb-reviewed').checked = true;
document.getElementById('sb-reviewed').dispatch('change');
assert.equal(document.getElementById('sb-state').textContent, 'package_exportable');
assert.match(document.getElementById('sb-package-preview').textContent, /Challenger A/);

document.getElementById('sb-clear-btn').click();
assert.equal(document.getElementById('sb-state').textContent, 'blocked_operator_review');

console.log('strategy builder contracts ok');

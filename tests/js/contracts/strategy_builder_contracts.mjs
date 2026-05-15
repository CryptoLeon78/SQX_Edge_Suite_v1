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
assert.equal(typeof core.buyerHandoffPackReview, 'function');
assert.equal(typeof core.buyerSessionHandoffSummary, 'function');
assert.equal(typeof core.buyerSessionOperatorNotes, 'function');
assert.equal(typeof core.buyerSessionSupportCaseBundle, 'function');
assert.equal(typeof core.buyerSessionSupportResolutionChecklist, 'function');
assert.equal(typeof core.handoffEvidenceIndex, 'function');
assert.equal(typeof core.handoffAuditEntry, 'function');
assert.equal(typeof core.guidedBuyerSessionChecklist, 'function');
assert.equal(typeof core.strategyCleanerDraftFromPackage, 'function');
assert.equal(typeof core.unifiedBuyerHandoffPackFromPackage, 'function');
assert.equal(typeof core.validateImportPayload, 'function');

const blocked = core.buildPackage({
  source_mode: 'blank',
  asset: 'EURUSD',
  timeframe: 'H1',
  idea_archetype: 'trend_following',
  validation_pack_id: 'robustness',
  project_profile_id: 'custom-forex-h1-balanced',
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
  project_profile_id: 'custom-forex-h1-balanced',
  operator_reviewed: true,
}, { createdAt: '2026-05-09T00:00:00.000Z' });
assert.equal(ready.workflow_state, 'package_exportable');
assert.equal(ready.asset_profile.asset, 'EURUSD');
assert.equal(ready.source_summary.candidate, 'Challenger A');
assert.equal(ready.source_summary.temporal_health.status, 'fresh');
assert.equal(ready.source_summary.egt_v2.verdict, 'STRONG');
assert.equal(ready.source_summary.direction.direction, 'long_only');
assert.equal(ready.source_summary.directional_coherence.verdict, 'OK');
assert.equal(ready.source_summary.consolidated_score.score, 88);
assert.equal(ready.source_summary.evidence_review.operator_review_required, true);
assert.equal(ready.source_summary.evidence_review.directional_coherence_ok, true);
assert.equal(ready.source_summary.evidence_review.score_pro_ok, true);
assert.equal(ready.asset_profile.cvc_evidence_summary.temporal_health.status, 'fresh');
assert.equal(ready.asset_profile.cvc_evidence_summary.egt_v2.verdict, 'STRONG');
assert.equal(ready.asset_profile.cvc_evidence_summary.directional_coherence.verdict, 'OK');
assert.equal(ready.asset_profile.cvc_evidence_summary.consolidated_score.passed_hard, true);
assert.equal(ready.views_handoff.validation_pack_id, 'robustness');
assert.equal(JSON.stringify(ready).includes('raw_csv'), false);
assert.equal(JSON.stringify(ready).includes('metrics_by_block'), false);
const pgPrefill = core.projectGeneratorPrefillFromPackage(ready);
assert.equal(pgPrefill.ok, true);
assert.equal(pgPrefill.config.asset, 'EURUSD');
assert.equal(pgPrefill.config.tf, 'H1');
assert.equal(pgPrefill.config.bs, 'BS_Tendencia_v6');
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
const buyerPack = core.unifiedBuyerHandoffPackFromPackage(ready, { createdAt: '2026-05-09T01:20:00.000Z' });
assert.equal(buyerPack.ok, true);
assert.equal(buyerPack.pack.type, 'sqx-edge.strategy-builder-buyer-handoff-pack');
assert.equal(buyerPack.pack.created_at, '2026-05-09T01:20:00.000Z');
assert.equal(buyerPack.pack.workflow.ready, true);
assert.equal(buyerPack.pack.handoffs.project_generator_prefill.ok, true);
assert.equal(buyerPack.pack.handoffs.project_generator_preset_draft.ok, true);
assert.equal(buyerPack.pack.handoffs.sqx_views.ok, true);
assert.equal(buyerPack.pack.handoffs.strategy_cleaner.ok, true);
assert.equal(buyerPack.guardrails.includes('no_destination_action_triggered'), true);
assert.equal(buyerPack.pack.guardrails.includes('no_backend_endpoint'), true);
assert.equal(buyerPack.pack.guardrails.includes('no_api_call'), true);
assert.match(buyerPack.pack.manual_next_steps.join(' '), /StrategyQuant validation/);
assert.equal(core.unifiedBuyerHandoffPackFromPackage(blocked).ok, false);
const buyerPackReview = core.buyerHandoffPackReview(buyerPack.pack, { createdAt: '2026-05-09T01:25:00.000Z' });
assert.equal(buyerPackReview.ok, true);
assert.equal(buyerPackReview.review.type, 'sqx-edge.strategy-builder-buyer-handoff-pack-review');
assert.equal(buyerPackReview.review.re_review_required, true);
assert.equal(buyerPackReview.review.rebuilt_workflow_state, 'blocked_operator_review');
assert.equal(buyerPackReview.review.included_handoffs.length, 4);
assert.equal(buyerPackReview.review.missing_handoffs.length, 0);
assert.equal(buyerPackReview.guardrails.includes('no_destination_action_triggered'), true);
const buyerSessionChecklist = core.guidedBuyerSessionChecklist(buyerPack.pack, { createdAt: '2026-05-09T01:35:00.000Z' });
assert.equal(buyerSessionChecklist.ok, true);
assert.equal(buyerSessionChecklist.checklist.type, 'sqx-edge.strategy-builder-buyer-session-checklist');
assert.equal(buyerSessionChecklist.checklist.review_required, false);
assert.equal(buyerSessionChecklist.checklist.steps.length, 7);
assert.equal(buyerSessionChecklist.checklist.steps[0].status, 'done');
assert.match(buyerSessionChecklist.checklist.steps.map(step => step.action).join(' '), /Generar custom/);
assert.equal(buyerSessionChecklist.checklist.guardrails.includes('operator_executes_every_step_manually'), true);
const importedBuyerSessionChecklist = core.guidedBuyerSessionChecklist(buyerPackReview.review);
assert.equal(importedBuyerSessionChecklist.ok, true);
assert.equal(importedBuyerSessionChecklist.checklist.review_required, true);
assert.equal(importedBuyerSessionChecklist.checklist.steps[0].status, 'pending');
assert.equal(importedBuyerSessionChecklist.checklist.steps[1].status, 'blocked');
const buyerSessionSummary = core.buyerSessionHandoffSummary(buyerSessionChecklist.checklist, { createdAt: '2026-05-09T01:40:00.000Z' });
assert.equal(buyerSessionSummary.ok, true);
assert.equal(buyerSessionSummary.summary.type, 'sqx-edge.strategy-builder-buyer-session-summary');
assert.equal(buyerSessionSummary.summary.created_at, '2026-05-09T01:40:00.000Z');
assert.equal(buyerSessionSummary.summary.step_counts.done, 1);
assert.equal(buyerSessionSummary.summary.step_counts.pending, 6);
assert.equal(buyerSessionSummary.summary.handoff_targets.length, 6);
assert.equal(buyerSessionSummary.summary.redaction.includes('no_buyer_identity'), true);
assert.equal(buyerSessionSummary.summary.guardrails.includes('no_destination_action_triggered'), true);
assert.equal(JSON.stringify(buyerSessionSummary.summary).includes('"raw_csv"'), false);
assert.equal(JSON.stringify(buyerSessionSummary.summary).includes('"buyer_email"'), false);
const buyerSessionNotes = core.buyerSessionOperatorNotes(buyerSessionSummary.summary, { createdAt: '2026-05-09T01:45:00.000Z' });
assert.equal(buyerSessionNotes.ok, true);
assert.equal(buyerSessionNotes.notes.type, 'sqx-edge.strategy-builder-buyer-session-notes');
assert.equal(buyerSessionNotes.notes.created_at, '2026-05-09T01:45:00.000Z');
assert.equal(buyerSessionNotes.notes.print_ready, true);
assert.equal(buyerSessionNotes.notes.format, 'plain_text');
assert.equal(buyerSessionNotes.notes.sections.length, 5);
assert.match(buyerSessionNotes.notes.print_text, /SQX Edge buyer session notes - EURUSD H1/);
assert.match(buyerSessionNotes.notes.print_text, /Handoff targets/);
assert.match(buyerSessionNotes.notes.print_text, /No automatic destination action was triggered/);
assert.equal(buyerSessionNotes.notes.guardrails.includes('no_local_storage_write'), true);
assert.equal(JSON.stringify(buyerSessionNotes.notes).includes('"buyer_email"'), false);
const buyerSupportCase = core.buyerSessionSupportCaseBundle(buyerSessionNotes.notes, { createdAt: '2026-05-09T01:50:00.000Z' });
assert.equal(buyerSupportCase.ok, true);
assert.equal(buyerSupportCase.bundle.type, 'sqx-edge.strategy-builder-buyer-session-support-case-bundle');
assert.equal(buyerSupportCase.bundle.created_at, '2026-05-09T01:50:00.000Z');
assert.match(buyerSupportCase.bundle.case_id, /^SB-EURUSD-H1-20260509T0150/);
assert.equal(buyerSupportCase.bundle.attachment_manifest.length, 3);
assert.equal(buyerSupportCase.bundle.attachment_manifest.some(item => item.id === 'full_strategy_builder_package' && item.included === false && item.sensitive_payload === true), true);
assert.equal(buyerSupportCase.bundle.support_questions.length, 4);
assert.equal(buyerSupportCase.bundle.guardrails.includes('no_remote_ticket_created'), true);
assert.equal(JSON.stringify(buyerSupportCase.bundle).includes('"buyer_email"'), false);
const buyerResolution = core.buyerSessionSupportResolutionChecklist(buyerSupportCase.bundle, { createdAt: '2026-05-09T01:55:00.000Z' });
assert.equal(buyerResolution.ok, true);
assert.equal(buyerResolution.checklist.type, 'sqx-edge.strategy-builder-buyer-session-support-resolution-checklist');
assert.equal(buyerResolution.checklist.created_at, '2026-05-09T01:55:00.000Z');
assert.equal(buyerResolution.checklist.steps.length, 7);
assert.equal(buyerResolution.checklist.step_counts.blocked, 0);
assert.equal(buyerResolution.checklist.step_counts.done, 1);
assert.equal(buyerResolution.checklist.close_conditions.includes('strategyquant_validation_boundary_confirmed'), true);
assert.equal(buyerResolution.checklist.escalation_conditions.includes('manual_review_required'), true);
assert.equal(buyerResolution.checklist.guardrails.includes('no_remote_ticket_created'), true);
assert.equal(JSON.stringify(buyerResolution.checklist).includes('"buyer_email"'), false);
const evidenceIndex = core.handoffEvidenceIndex({
  package: ready,
  buyer_handoff_pack: buyerPack.pack,
  buyer_pack_review: buyerPackReview.review,
  buyer_session_checklist: buyerSessionChecklist.checklist,
  buyer_session_summary: buyerSessionSummary.summary,
  buyer_session_notes: buyerSessionNotes.notes,
  buyer_support_case: buyerSupportCase.bundle,
  buyer_resolution_checklist: buyerResolution.checklist,
}, { createdAt: '2026-05-09T02:00:00.000Z' });
assert.equal(evidenceIndex.ok, true);
assert.equal(evidenceIndex.index.type, 'sqx-edge.strategy-builder-evidence-handoff-index');
assert.equal(evidenceIndex.index.created_at, '2026-05-09T02:00:00.000Z');
assert.equal(evidenceIndex.index.asset, 'EURUSD');
assert.equal(evidenceIndex.index.timeframe, 'H1');
assert.equal(evidenceIndex.index.summary.ready_for_buyer_handoff, true);
assert.equal(evidenceIndex.index.summary.missing_required_entries, 0);
assert.equal(evidenceIndex.index.entries.some(entry => entry.id === 'buyer_resolution_checklist' && entry.present), true);
assert.equal(evidenceIndex.index.privacy_boundary.includes('no_buyer_identity'), true);
assert.equal(evidenceIndex.index.guardrails.includes('no_destination_action_triggered'), true);
assert.equal(JSON.stringify(evidenceIndex.index).includes('"raw_csv"'), false);
assert.equal(JSON.stringify(evidenceIndex.index).includes('"buyer_email"'), false);
const partialEvidenceIndex = core.handoffEvidenceIndex({ package: ready }, { createdAt: '2026-05-09T02:05:00.000Z' });
assert.equal(partialEvidenceIndex.ok, false);
assert.equal(partialEvidenceIndex.index.missing_required_handoffs.includes('buyer_handoff_pack'), true);
assert.equal(partialEvidenceIndex.errors.some(error => error.includes('missing_required_evidence')), true);

const importedPackage = core.importPayload(JSON.stringify(ready), { createdAt: '2026-05-09T01:00:00.000Z' });
assert.equal(importedPackage.ok, true);
assert.equal(importedPackage.package.type, 'sqx-edge.strategy-builder-package');
assert.equal(importedPackage.package.workflow_state, 'blocked_operator_review');
assert.equal(importedPackage.package.source_summary.candidate, 'Challenger A');
assert.equal(importedPackage.package.import_metadata.re_review_required, true);
assert.equal(importedPackage.model.operator_reviewed, false);

const importedBuyerPack = core.importPayload(JSON.stringify(buyerPack.pack), { createdAt: '2026-05-09T01:30:00.000Z' });
assert.equal(importedBuyerPack.ok, true);
assert.equal(importedBuyerPack.package.workflow_state, 'blocked_operator_review');
assert.equal(importedBuyerPack.package.import_metadata.source_type, 'sqx-edge.strategy-builder-buyer-handoff-pack');
assert.equal(importedBuyerPack.package.import_metadata.buyer_pack_review, true);
assert.equal(importedBuyerPack.buyer_pack_review.type, 'sqx-edge.strategy-builder-buyer-handoff-pack-review');
assert.equal(importedBuyerPack.buyer_pack_review.included_handoffs.every(item => item.present), true);
assert.equal(importedBuyerPack.model.operator_reviewed, false);

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
  'sb-prepare-buyer-pack-btn',
  'sb-buyer-session-btn',
  'sb-buyer-summary-btn',
  'sb-buyer-notes-btn',
  'sb-buyer-support-case-btn',
  'sb-buyer-resolution-btn',
  'sb-evidence-index-btn',
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
  'sb-project-profile': 'custom-forex-h1-balanced',
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
assert.equal(document.getElementById('pg-custom-bs').value, 'BS_Tendencia_v6');
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
document.getElementById('sb-prepare-buyer-pack-btn').click();
assert.match(document.getElementById('sb-package-preview').textContent, /sqx-edge\.strategy-builder-buyer-handoff-pack/);
assert.match(document.getElementById('sb-package-preview').textContent, /project_generator_prefill/);
assert.match(document.getElementById('sb-package-preview').textContent, /strategy_cleaner/);
assert.match(document.getElementById('sb-status').textContent, /No destination action/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Buyer Handoff Pack/);
assert.equal(SQX.viewCreator.getSavedPresets().length, viewPresetCountBefore);
assert.equal(sandbox.localStorage.getItem('sqx_strategy_builder_buyer_pack_v1'), null);
document.getElementById('sb-buyer-session-btn').click();
assert.match(document.getElementById('sb-package-preview').textContent, /sqx-edge\.strategy-builder-buyer-session-checklist/);
assert.match(document.getElementById('sb-package-preview').textContent, /operator_executes_every_step_manually/);
assert.match(document.getElementById('sb-status').textContent, /Buyer session checklist prepared/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Buyer Session Checklist/);
document.getElementById('sb-buyer-summary-btn').click();
assert.match(document.getElementById('sb-package-preview').textContent, /sqx-edge\.strategy-builder-buyer-session-summary/);
assert.match(document.getElementById('sb-package-preview').textContent, /no_buyer_identity/);
assert.match(document.getElementById('sb-package-preview').textContent, /no_destination_action_triggered/);
assert.match(document.getElementById('sb-status').textContent, /Buyer session summary prepared|Buyer session summary exported/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Buyer Session Summary/);
assert.equal(sandbox.localStorage.getItem('sqx_strategy_builder_buyer_session_summary_v1'), null);
document.getElementById('sb-buyer-notes-btn').click();
assert.match(document.getElementById('sb-package-preview').textContent, /SQX Edge buyer session notes - EURUSD H1/);
assert.match(document.getElementById('sb-package-preview').textContent, /Handoff targets/);
assert.match(document.getElementById('sb-package-preview').textContent, /Operator guardrails/);
assert.match(document.getElementById('sb-status').textContent, /Buyer session printable notes prepared|Buyer session printable notes exported/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Buyer Session Notes/);
assert.equal(sandbox.localStorage.getItem('sqx_strategy_builder_buyer_session_notes_v1'), null);
document.getElementById('sb-buyer-support-case-btn').click();
assert.match(document.getElementById('sb-package-preview').textContent, /sqx-edge\.strategy-builder-buyer-session-support-case-bundle/);
assert.match(document.getElementById('sb-package-preview').textContent, /no_remote_ticket_created/);
assert.match(document.getElementById('sb-package-preview').textContent, /full_strategy_builder_package/);
assert.match(document.getElementById('sb-status').textContent, /Buyer support case bundle prepared|Buyer support case bundle exported/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Buyer Support Case/);
assert.equal(sandbox.localStorage.getItem('sqx_strategy_builder_buyer_support_case_v1'), null);
document.getElementById('sb-buyer-resolution-btn').click();
assert.match(document.getElementById('sb-package-preview').textContent, /sqx-edge\.strategy-builder-buyer-session-support-resolution-checklist/);
assert.match(document.getElementById('sb-package-preview').textContent, /case_close_or_escalate/);
assert.match(document.getElementById('sb-package-preview').textContent, /strategyquant_validation_boundary_confirmed/);
assert.match(document.getElementById('sb-status').textContent, /Buyer support resolution checklist prepared|Buyer support resolution checklist exported/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Buyer Resolution Checklist/);
assert.equal(sandbox.localStorage.getItem('sqx_strategy_builder_buyer_resolution_v1'), null);
document.getElementById('sb-evidence-index-btn').click();
assert.match(document.getElementById('sb-package-preview').textContent, /sqx-edge\.strategy-builder-evidence-handoff-index/);
assert.match(document.getElementById('sb-package-preview').textContent, /buyer_resolution_checklist/);
assert.match(document.getElementById('sb-package-preview').textContent, /ready_for_buyer_handoff/);
assert.match(document.getElementById('sb-status').textContent, /Evidence handoff index prepared/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Evidence Index/);
assert.equal(sandbox.localStorage.getItem('sqx_strategy_builder_evidence_index_v1'), null);
const importedBuyerPackUiResult = ui.importText(JSON.stringify(buyerPack.pack), { document });
assert.equal(importedBuyerPackUiResult.ok, true);
assert.equal(document.getElementById('sb-state').textContent, 'blocked_operator_review');
assert.match(document.getElementById('sb-package-preview').textContent, /sqx-edge\.strategy-builder-buyer-handoff-pack-review/);
assert.match(document.getElementById('sb-package-preview').textContent, /included_handoffs/);
assert.match(document.getElementById('sb-status').textContent, /Buyer pack imported for local review/);
assert.match(document.getElementById('sb-audit-list').innerHTML, /Buyer Pack Import Review/);
assert.equal(sandbox.localStorage.getItem('sqx_strategy_builder_buyer_pack_v1'), null);
document.getElementById('sb-buyer-session-btn').click();
assert.match(document.getElementById('sb-package-preview').textContent, /sqx-edge\.strategy-builder-buyer-session-checklist/);
assert.match(document.getElementById('sb-package-preview').textContent, /Confirm manual review first/);
assert.match(document.getElementById('sb-status').textContent, /Buyer session checklist prepared/);

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

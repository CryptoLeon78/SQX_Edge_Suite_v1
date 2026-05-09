import { assert, Element, createLoadedSandbox } from './harness.mjs';

const { SQX, document, sandbox } = createLoadedSandbox([
  'app/js/modules/formatters.js',
  'app/js/modules/ui.js',
  'app/js/modules/datasets.js',
  'app/js/modules/champion-challenger-core.js',
  'app/js/modules/champion-challenger-regime.js',
  'app/js/modules/champion-challenger.js',
]);

sandbox.SQX_HISTORICAL_DATA = {
  EURUSD: { start: '2020-01', v: Array.from({ length: 72 }, (_value, index) => 100 + index * 1.2) },
};
sandbox.SQX_SCORES_DATA = {
  EURUSD: { regimen: { objective: '+', composite_score: 0.67, scope: 'global' }, metrics: { regimen: { sma200_persistence_bars: 32 } } },
};

[
  'cvc-champion-input',
  'cvc-challenger-input',
  'cvc-oos-input',
  'cvc-run-btn',
  'cvc-sample-btn',
  'cvc-clear-btn',
  'cvc-export-btn',
  'cvc-handoff-btn',
  'cvc-status',
  'cvc-summary',
  'cvc-ranking',
  'cvc-empty',
  'cvc-oos-summary',
  'cvc-handoff-preview',
  'cvc-candidate-count',
  'cvc-ready-count',
  'cvc-oos-ready-count',
  'cvc-regime-ready-count',
  'cvc-filter-health-ok',
  'cvc-filter-egt-v2-ok',
  'cvc-filter-coherence-ok',
].forEach(id => document.add(new Element(id)));

const cvc = SQX.championChallenger;
assert.ok(cvc, 'champion challenger UI module should register');
assert.equal(cvc.init({ document }), true);

document.getElementById('cvc-sample-btn').click();
assert.equal(document.getElementById('cvc-candidate-count').textContent, '3');
assert.equal(document.getElementById('cvc-ready-count').textContent, '1');
assert.equal(document.getElementById('cvc-oos-ready-count').textContent, '1');
assert.equal(document.getElementById('cvc-regime-ready-count').textContent, '3');
assert.match(document.getElementById('cvc-status').textContent, /Comparacion lista/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /Challenger A Long/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /OOS 100% positivo/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /EGT/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /COMPLIANT/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /Health fresh/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /EGT v2 STRONG/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /Dir long_only/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /Coherencia OK/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /Score Pro/);
assert.match(document.getElementById('cvc-summary').innerHTML, /Health OK/);
assert.match(document.getElementById('cvc-summary').innerHTML, /EGT v2 OK/);
assert.match(document.getElementById('cvc-summary').innerHTML, /Coherencia OK/);
assert.match(document.getElementById('cvc-summary').innerHTML, /Score Pro OK/);

document.getElementById('cvc-filter-health-ok').checked = true;
document.getElementById('cvc-filter-health-ok').dispatch('change');
assert.match(document.getElementById('cvc-status').textContent, /Filtro activo: 2\/3 visibles/);
assert.match(document.getElementById('cvc-ranking').innerHTML, /Challenger A Long/);
assert.doesNotMatch(document.getElementById('cvc-ranking').innerHTML, /Challenger C/);

document.getElementById('cvc-filter-egt-v2-ok').checked = true;
document.getElementById('cvc-filter-egt-v2-ok').dispatch('change');
assert.match(document.getElementById('cvc-status').textContent, /Filtro activo: 1\/3 visibles/);
document.getElementById('cvc-filter-health-ok').checked = false;
document.getElementById('cvc-filter-egt-v2-ok').checked = false;
document.getElementById('cvc-filter-health-ok').dispatch('change');

document.getElementById('cvc-filter-coherence-ok').checked = true;
document.getElementById('cvc-filter-coherence-ok').dispatch('change');
assert.match(document.getElementById('cvc-ranking').innerHTML, /Coherencia OK/);
document.getElementById('cvc-filter-coherence-ok').checked = false;
document.getElementById('cvc-filter-coherence-ok').dispatch('change');

const reviewExport = cvc.buildReviewExport(cvc.evaluate({ document }), { generatedAt: '2026-05-08T00:00:00.000Z' });
assert.equal(reviewExport.type, 'sqx-edge.champion-challenger-review');
assert.equal(reviewExport.summary.candidate_count, 3);
assert.equal(reviewExport.summary.oos_stable_count, 1);
assert.equal(reviewExport.summary.temporal_health_ok_count, 2);
assert.equal(reviewExport.summary.egt_v2_ok_count, 1);
assert.equal(reviewExport.summary.directional_coherence_ok_count, 3);
assert.ok(reviewExport.summary.score_pro_ok_count >= 1);
assert.equal(reviewExport.redaction.raw_csv, 'excluded');
assert.equal(reviewExport.redaction.remote_calls, 'none');
assert.equal(reviewExport.candidates[0].strategy_name, 'Challenger A Long');
assert.equal(reviewExport.candidates[0].temporal_health.status, 'fresh');
assert.equal(reviewExport.candidates[0].temporal_health.pass_all, true);
assert.equal(reviewExport.candidates[0].egt_v2.verdict, 'STRONG');
assert.equal(reviewExport.candidates[0].direction.direction, 'long_only');
assert.equal(reviewExport.candidates[0].directional_coherence.verdict, 'OK');
assert.equal(reviewExport.candidates[0].consolidated_score.passed_hard, true);
assert.equal(Array.isArray(reviewExport.candidates[0].egt_v2.failed_regimes), true);
assert.equal(Object.prototype.hasOwnProperty.call(reviewExport.candidates[0], 'raw'), false);
assert.equal(JSON.stringify(reviewExport).includes('metrics_by_block'), false);

const handoff = cvc.buildStrategyBuilderHandoff(reviewExport, { generatedAt: '2026-05-08T00:01:00.000Z' });
assert.equal(handoff.type, 'sqx-edge.strategy-builder-handoff');
assert.equal(handoff.source_review.candidate_count, 3);
assert.equal(handoff.source_review.temporal_health_ok_count, 2);
assert.equal(handoff.source_review.egt_v2_ok_count, 1);
assert.equal(handoff.source_review.directional_coherence_ok_count, 3);
assert.ok(handoff.source_review.score_pro_ok_count >= 1);
assert.equal(handoff.recommended_candidate.strategy_name, 'Challenger A Long');
assert.equal(handoff.recommended_candidate.decision, 'builder_candidate');
assert.equal(handoff.recommended_candidate.temporal_health.status, 'fresh');
assert.equal(handoff.recommended_candidate.egt_v2.verdict, 'STRONG');
assert.equal(handoff.recommended_candidate.directional_coherence.verdict, 'OK');
assert.equal(handoff.recommended_candidate.evidence_review.directional_coherence_ok, true);
assert.equal(handoff.recommended_candidate.evidence_review.score_pro_ok, true);
assert.equal(handoff.recommended_candidate.evidence_review.operator_review_required, true);
assert.equal(handoff.recommended_candidate.evidence_review.egt_v2_ok, true);
assert.match(handoff.guardrails.join(' '), /No raw CSV payloads/);
assert.equal(JSON.stringify(handoff).includes('Top Picks'), false);

document.getElementById('cvc-handoff-btn').click();
assert.match(document.getElementById('cvc-status').textContent, /Handoff Strategy Builder/);
assert.match(document.getElementById('cvc-handoff-preview').innerHTML, /Strategy Builder handoff/);
document.getElementById('cvc-export-btn').click();
assert.match(document.getElementById('cvc-status').textContent, /Resumen CVC/);

document.getElementById('cvc-champion-input').value = [
  'Strategy Name,Symbol,Profit factor,Return/Drawdown,# trades',
  'Champion,EURUSD,1.50,4.00,200',
].join('\n');
document.getElementById('cvc-challenger-input').value = [
  'Strategy Name,Symbol,Profit factor,Return/Drawdown,# trades,Filters Result',
  '<script>alert(1)</script>,EURUSD,1.80,4.20,220,PASSED',
].join('\n');
document.getElementById('cvc-oos-input').value = '';

const model = cvc.evaluate({ document });
assert.equal(model.ok, true);
assert.equal(model.rankings.length, 1);
assert.match(document.getElementById('cvc-ranking').innerHTML, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
assert.doesNotMatch(document.getElementById('cvc-ranking').innerHTML, /<script>/);

document.getElementById('cvc-clear-btn').click();
assert.equal(document.getElementById('cvc-champion-input').value, '');
assert.equal(document.getElementById('cvc-ranking').innerHTML, '');
assert.equal(document.getElementById('cvc-candidate-count').textContent, '0');
assert.equal(document.getElementById('cvc-regime-ready-count').textContent, '0');
assert.equal(document.getElementById('cvc-handoff-preview').innerHTML, '');

document.getElementById('cvc-run-btn').click();
assert.match(document.getElementById('cvc-status').textContent, /Revisa los datos/);

console.log('champion challenger UI contracts ok');

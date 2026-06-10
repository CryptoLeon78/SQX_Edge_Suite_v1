import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const overlayRoot = path.join(repoRoot, 'integrations/sqx144/blocksettings_ai_overlay');
const js = fs.readFileSync(path.join(overlayRoot, 'sqx-edge-bsai.js'), 'utf8');
const css = fs.readFileSync(path.join(overlayRoot, 'sqx-edge-bsai.css'), 'utf8');

[
  'formSignature',
  'markFormDirty',
  'resetSession',
  'candidateIsCurrent',
  'projectIsCurrent',
  'lastPlannedSignature',
  'lastCandidateSignature',
  'lastProjectSignature',
  'state.sessionId = "";',
  'state.candidate = null;',
  'state.project = null;',
  'plan_required_for_current_form',
  'candidate_required_for_current_form',
  'responseStillCurrent(signature)',
].forEach((marker) => {
  assert.ok(js.includes(marker), `BS-AI7 hardening marker missing: ${marker}`);
});

[
  'sqx-edge-bsai-reset',
  'Nueva sesion / Limpiar',
  'Cambios pendientes',
  'Pulsa Plan para validar esta demanda antes de guardar/generar.',
  'Candidato activo',
  'Base usada',
  'Politica',
  'v7 explicito',
  'D1 default v6_D1',
  'default v6/v6_D1',
  'Capa1',
  'Capa2',
  'Descarga manual Capa1/Capa2. No se importa nada en SQX.',
].forEach((marker) => {
  assert.ok(js.includes(marker), `BS-AI7 UI marker missing: ${marker}`);
});

assert.ok(
  js.includes('if (saveButton) saveButton.disabled = state.busy || state.formDirty || state.lastPlannedSignature !== signature;'),
  'Guardar .sqb should require a current plan'
);
assert.ok(
  js.includes('if (generateButton) generateButton.disabled = state.busy || !candidateIsCurrent();'),
  'Generar .cfx should require a current candidate'
);
assert.ok(
  js.includes('node.addEventListener("input", markFormDirty);') && js.includes('node.addEventListener("change", markFormDirty);'),
  'form controls should clear stale results on input and change'
);
assert.ok(
  js.includes('state.candidate = Object.assign({}, state.candidate || {}, result.candidate || {});'),
  'project generation should preserve candidate download context while adding project context'
);
assert.ok(
  js.includes('var v7Selected = base.indexOf("_v7") >= 0 || requestedBase.indexOf("_v7") >= 0;'),
  'policy trace should identify v7 only from an explicit/selected v7 base'
);
assert.ok(
  js.includes('policy.indexOf("v6_d1") >= 0'),
  'policy trace should classify D1 default v6_D1 policies explicitly'
);
assert.ok(
  !js.includes('policy.indexOf("explicit") >= 0'),
  'policy trace must not treat no_explicit/default policy names as v7 explicit'
);

assert.ok(css.includes('.sqx-edge-bsai-trace'), 'trace block should be styled');
assert.ok(css.includes('.sqx-edge-bsai-downloads'), 'download group should be styled');
assert.ok(css.includes('.sqx-edge-bsai-output a.sqx-edge-bsai-download'), 'download links should use labeled blocks');
assert.ok(css.includes('overflow-wrap: anywhere'), 'long candidate/project filenames should wrap');

assert.ok(!js.includes('C:\\') && !js.includes('C:/'), 'overlay must not expose local Windows paths');
assert.ok(!js.toLowerCase().includes('token='), 'overlay must not expose tokens');
assert.ok(!js.toLowerCase().includes('secret'), 'overlay must not expose protected material strings');
assert.ok(!js.includes('localhost:11434') && !js.includes('127.0.0.1:11434'), 'overlay must not call Ollama directly');
assert.ok(!js.includes('data.db'), 'overlay must not reference data.db');
assert.ok(!js.includes('user/projects'), 'overlay must not reference user/projects');

console.log('blocksettings ai overlay hardening contracts ok');

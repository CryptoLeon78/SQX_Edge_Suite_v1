import fs from 'node:fs';
import path from 'node:path';
import { assert, repoRoot } from './harness.mjs';

const overlayRoot = path.join(repoRoot, 'integrations/sqx144/blocksettings_ai_overlay');
const js = fs.readFileSync(path.join(overlayRoot, 'sqx-edge-bsai.js'), 'utf8');
const css = fs.readFileSync(path.join(overlayRoot, 'sqx-edge-bsai.css'), 'utf8');

[
  'sqx-edge-bsai-launcher',
  'sqx-edge-bsai-panel',
  'sqx-edge-bsai-close',
  'sqx-edge-bsai-prompt',
  'sqx-edge-bsai-asset',
  'sqx-edge-bsai-timeframe',
  'sqx-edge-bsai-direction',
  'sqx-edge-bsai-base',
  'sqx-edge-bsai-reset',
  'sqx-edge-bsai-plan',
  'sqx-edge-bsai-save',
  'sqx-edge-bsai-generate',
  'sqx-edge-bsai-output',
].forEach((id) => {
  assert.ok(js.includes(id), `overlay should expose manual smoke control ${id}`);
});

[
  '<option>H1</option>',
  '<option>D1</option>',
  '<option value=\\"long\\">Long</option>',
  'placeholder=\\"solo para v7/manual\\"',
  'Nueva sesion / Limpiar</button>',
  'Plan</button>',
  'Guardar .sqb</button>',
  'Generar .cfx</button>',
  'Cambios pendientes',
  'Plan validado',
  'Proyecto BSAI listo',
  'Candidato guardado',
  'Candidato activo',
  'Base usada',
  'Politica',
  'Capa1',
  'Capa2',
  'Descargar .sqb candidato',
].forEach((marker) => {
  assert.ok(js.includes(marker), `overlay should keep expected manual smoke marker: ${marker}`);
});

assert.ok(js.includes('apiUrl(item.downloadUrl)'), 'project download links should be built through apiUrl');
assert.ok(js.includes('apiUrl(state.candidate.downloadUrl)'), 'candidate download link should be built through apiUrl');
assert.ok(js.includes('if (raw.indexOf("/api/") === 0) return API_ORIGIN + raw;'), 'apiUrl should preserve backend /api downloads');
assert.ok(js.includes('safeApiBase'), 'overlay should constrain the local API base');
assert.ok(js.includes('/blocksettings/ai/sessions/'), 'overlay should use the BS-AI session API');
assert.ok(js.includes('/generate-project'), 'overlay should use the local project-generation API');

assert.ok(css.includes('.sqx-edge-bsai-launcher'), 'manual smoke should have launcher styling');
assert.ok(css.includes('.sqx-edge-bsai-panel'), 'manual smoke should have panel styling');
assert.ok(css.includes('.sqx-edge-bsai-actions'), 'manual smoke should have action styling');
assert.ok(css.includes('.sqx-edge-bsai-output a'), 'manual smoke should style download links');
assert.ok(css.includes('.sqx-edge-bsai-trace'), 'manual smoke should style active candidate trace');
assert.ok(css.includes('.sqx-edge-bsai-downloads'), 'manual smoke should style complete download labels');
assert.ok(css.includes('overflow-wrap: anywhere'), 'manual smoke should wrap long artifact names');

assert.ok(!js.includes('C:\\') && !js.includes('C:/'), 'overlay must not expose local Windows paths');
assert.ok(!js.toLowerCase().includes('token='), 'overlay must not expose tokens');
assert.ok(!js.toLowerCase().includes('secret'), 'overlay must not expose secrets');
assert.ok(!js.includes('localhost:11434') && !js.includes('127.0.0.1:11434'), 'overlay must not call Ollama directly');
assert.ok(!js.includes('data.db'), 'overlay must not reference data.db');
assert.ok(!js.includes('user/projects'), 'overlay must not reference user/projects');

console.log('blocksettings ai overlay manual smoke contracts ok');

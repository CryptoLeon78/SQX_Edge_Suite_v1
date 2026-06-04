import { assert } from './harness.mjs';
import fs from 'fs';
import path from 'path';

const repoRoot = process.cwd();
const overlayJs = fs.readFileSync(path.join(repoRoot, 'integrations/sqx142/ai_wizard_overlay/sqx-edge-aiwizard.js'), 'utf8');
const overlayCss = fs.readFileSync(path.join(repoRoot, 'integrations/sqx142/ai_wizard_overlay/sqx-edge-aiwizard.css'), 'utf8');
const installer = fs.readFileSync(path.join(repoRoot, 'tools/sqx142_ai_wizard_overlay.ps1'), 'utf8');
const server = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/api/server.py'), 'utf8');
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx142_ai_wizard.py'), 'utf8');
const doc = fs.readFileSync(path.join(repoRoot, 'docs/SQX142_AW_AI1_AI_WIZARD.md'), 'utf8');

assert.match(core, /AI_WIZARD_VERSION = "sqx142-ai-wizard-v1"/);
assert.match(core, /SPEC_TYPE = "sqx-edge\.ai-wizard-strategy-spec"/);
assert.match(core, /PACKAGE_TYPE = "sqx-edge\.strategy-builder-package"/);
assert.match(core, /blocked_unsupported_rule/);
assert.match(core, /no_sqx_runtime_launch/);
assert.match(core, /no_data_db_write/);
assert.match(core, /SQX_AI_WIZARD_OPENAI_ENABLED/);

assert.match(server, /\/api\/sqx142\/ai-wizard\/status/);
assert.match(server, /\/api\/sqx142\/ai-wizard\/plan/);
assert.match(server, /\/api\/sqx142\/ai-wizard\/draft-sqx/);
assert.match(server, /_require_sqx142_local_operator\(AI_WIZARD_VERSION\)/);

assert.match(overlayJs, /sqx142-ai-wizard-overlay-v2/);
assert.match(overlayJs, /http:\/\/127\.0\.0\.1:5050\/api/);
assert.match(overlayJs, /safeApiBase/);
assert.match(overlayJs, /localhost-only/);
assert.match(overlayJs, /host === "127\.0\.0\.1"/);
assert.match(overlayJs, /Provider directo desde navegador: blocked/);
assert.match(overlayJs, /draftButton\.disabled = state\.busy \|\| !hasValidSession\(\)/);
assert.match(overlayJs, /blocked/);
assert.doesNotMatch(overlayJs, /OPENAI_API_KEY|api_key|token=/i);
assert.match(overlayCss, /\.sqx-edge-aiwizard-shell/);

assert.match(installer, /ValidateSet\('status', 'install', 'rollback'\)/);
assert.doesNotMatch(installer, /Crack/);
assert.match(installer, /SQX142_ROOT/);
assert.match(installer, /sqx_process_running/);
assert.match(installer, /New-Backup/);
assert.match(installer, /localPathsReturned = \$false/);
assert.doesNotMatch(installer, /StrategyQuantX\.exe.*start|Start-Process.*StrategyQuant/i);

assert.match(doc, /implemented_v1_pending_manual_sqx_roundtrip/);
assert.match(doc, /No SQX runtime launch/);
assert.match(doc, /No `run_project`/);
assert.match(doc, /OpenAI queda preparado/);

console.log('sqx142 aw ai1 contracts ok');

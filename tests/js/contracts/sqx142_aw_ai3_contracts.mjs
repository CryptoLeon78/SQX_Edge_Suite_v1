import { assert } from './harness.mjs';
import fs from 'fs';
import path from 'path';

const repoRoot = process.cwd();
const core = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/core/sqx142_ai_wizard.py'), 'utf8');
const studioTest = fs.readFileSync(path.join(repoRoot, 'backend/sqx-edge-tool/test_sqx142_ai_wizard_studio.py'), 'utf8');
const overlayJs = fs.readFileSync(path.join(repoRoot, 'integrations/sqx142/ai_wizard_overlay/sqx-edge-aiwizard.js'), 'utf8');
const doc = fs.existsSync(path.join(repoRoot, 'docs/SQX142_AW_AI3_UNIVERSAL_PROMPT_COMPILER.md'))
  ? fs.readFileSync(path.join(repoRoot, 'docs/SQX142_AW_AI3_UNIVERSAL_PROMPT_COMPILER.md'), 'utf8')
  : '';

assert.match(core, /AI_WIZARD_AI3_COMPILER_VERSION = "sqx142-aw-ai3-universal-prompt-compiler-v1"/);
assert.match(core, /AI_WIZARD_INTERPRETER_SCHEMA/);
assert.match(core, /_try_local_model_interpretation/);
assert.match(core, /OllamaClient\(OllamaConfig/);
assert.match(core, /auto_start=False/);
assert.match(core, /rawPromptPersisted": False/);
assert.match(core, /rawResponsePersisted": False/);
assert.match(core, /externalApiCalled": False/);
assert.match(core, /universalPromptIntake": True/);
assert.match(core, /universalSqxGeneration": False/);

assert.match(core, /"candle_atr_sequence"/);
assert.match(core, /generate_ai_wizard_draft_from_ast/);
assert.match(core, /_patch_candle_atr_strategy_xml/);
assert.match(core, /_copy_sqx_with_patched_xml/);
assert.match(core, /"zip_entries_preserved"/);
assert.match(core, /"no_sqx_user_projects_write"/);
assert.match(core, /"no_data_db_write"/);
assert.match(core, /"no_runtime_launch"/);
assert.match(core, /"manual_algowizard_review_required"/);
assert.match(core, /"key": "talib_ATR"/);
assert.match(core, /_xml_price_value\("Close", shift\)/);
assert.match(core, /_xml_price_value\("Open", shift\)/);

assert.match(studioTest, /test_ai3_spanish_candle_prompt_compiles_traceable_draft/);
assert.match(studioTest, /test_ai3_local_model_interpreter_feeds_ast_without_persisting_raw/);
assert.match(studioTest, /SQX Edge AI3 Universal Prompt Compiler draft/);
assert.match(studioTest, /fake-local-model/);

assert.doesNotMatch(overlayJs, /127\.0\.0\.1:11434|localhost:11434|ollama\/api/i);
assert.doesNotMatch(overlayJs, /OPENAI_API_KEY|Authorization|Bearer|token=/i);

if (doc) {
  assert.match(doc, /SQX142-AW-AI3 Universal Prompt Compiler/);
  assert.match(doc, /sqx142-aw-ai3-universal-prompt-compiler-v1/);
  assert.match(doc, /universal_prompt_intake_not_universal_sqx_generation/);
  assert.match(doc, /allowlisted_catalog_only/);
  assert.match(doc, /candle_atr_sequence/);
  assert.match(doc, /raw_prompt_persisted=false/);
  assert.match(doc, /raw_provider_response_persisted=false/);
  assert.match(doc, /no provider calls from browser/);
}

console.log('sqx142 aw ai3 contracts ok');

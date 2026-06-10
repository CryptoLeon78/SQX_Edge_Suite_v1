import fs from 'node:fs';
import path from 'node:path';
import { assert, createLoadedSandbox, repoRoot } from './harness.mjs';

const { SQX } = createLoadedSandbox([
  'app/js/modules/exit-policy.js',
]);

const exitPolicy = SQX.exitPolicy;
assert.ok(exitPolicy, 'exit policy module should register globally');
assert.equal(exitPolicy.version, 'sqx-exit-policy-v1', 'exit policy should expose v1 version');
['detectExitComponentsFromXml', 'buildDefaultExitPlan', 'applyExitPlanToStrategyXml', 'summarizeExitPlan', 'getPolicy', 'setUserOverride'].forEach(method => {
  assert.equal(typeof exitPolicy[method], 'function', `exit policy API ${method} should exist`);
});

const lacityXml = fs.readFileSync(path.join(repoRoot, 'resources/template-maker-tool/exit_policy_lacity_strategy.xml'), 'utf8');
const components = exitPolicy.detectExitComponentsFromXml(lacityXml);
assert.ok(components.length >= 7, 'LaCity fixture should expose all exit method params');
assert.ok(components.some(component => component.kind === 'exit_after_days'), 'ExitAfterDays should be classified');
assert.ok(components.some(component => component.kind === 'exit_after_trading_days'), 'ExitAfterTradingDays/TDays should be classified');
assert.ok(components.some(component => component.kind === 'exit_after_bars'), 'ExitAfterBars should be classified');
assert.ok(components.some(component => component.kind === 'profit_target'), 'Profit Target should be classified');
assert.ok(components.some(component => component.kind === 'stop_loss'), 'Stop Loss should be classified');
assert.ok(components.some(component => component.kind === 'trailing_stop'), 'Trailing Stop should be classified');
assert.ok(components.some(component => component.kind === 'break_even'), 'Move SL to BE should be classified');

const plan = exitPolicy.buildDefaultExitPlan(lacityXml);
const summary = exitPolicy.summarizeExitPlan(plan);
assert.equal(summary.version, 'sqx-exit-policy-v1', 'exit summary should carry policy version');
assert.ok(summary.disabled.includes('Exit After Days LaCity'), 'ExitAfterDays should be disabled by default');
assert.ok(summary.disabled.includes('Exit After TDays LaCity'), 'ExitAfterTDays should be disabled by default');
assert.ok(summary.disabled.includes('Exit After Bars'), 'ExitAfterBars should be disabled by default');
assert.ok(summary.disabled.includes('Move SL to BE'), 'Move SL to BE should be disabled by default');
assert.ok(summary.randomized.includes('Profit Target'), 'Profit Target should be randomized by default');
assert.ok(summary.randomized.includes('Stop Loss'), 'Stop Loss should be randomized by default');
assert.ok(summary.randomized.includes('Trailing Stop'), 'Trailing Stop should be randomized by default');

const patched = exitPolicy.applyExitPlanToStrategyXml(lacityXml, plan);
assert.match(patched, /#ExitAfterDays\.ExitAfterDays#"[^>]*>0<\/Param>/, 'ExitAfterDays should be set to zero');
assert.match(patched, /#ExitAfterTradingDays\.ExitAfterTradingDays#"[^>]*>0<\/Param>/, 'ExitAfterTradingDays should be set to zero');
assert.match(patched, /#ExitAfterBars\.ExitAfterBars#"[^>]*>0<\/Param>/, 'ExitAfterBars should be set to zero');
assert.match(patched, /#MoveSL2BE\.MoveSL2BE#"[^>]*>0<\/Param>/, 'Move SL to BE should be set to zero');
assert.match(patched, /#ProfitTarget\.ProfitTarget#"[^>]*generate="random" randomValue="default"/, 'Profit Target should be random');
assert.match(patched, /#StopLoss\.StopLoss#"[^>]*generate="random" randomValue="default"/, 'Stop Loss should be random');
assert.match(patched, /#TrailingStop\.TrailingStop#"[^>]*generate="random" randomValue="default"/, 'Trailing Stop should be random');

const unknownXml = '<Strategy><Rule name="Long entry"><Then><Item key="EnterAtMarket"><Param key="#UnknownExit.Custom#" name="Mystery Exit" exitMethod="true">9</Param></Item></Then></Rule></Strategy>';
const unknownPlan = exitPolicy.buildDefaultExitPlan(unknownXml);
assert.ok(exitPolicy.summarizeExitPlan(unknownPlan).blocked.includes('Mystery Exit'), 'unknown active exits should block by default');
assert.throws(() => exitPolicy.applyExitPlanToStrategyXml(unknownXml, unknownPlan), /Mystery Exit/, 'unknown active exits should require an override before mutation');
const overridePlan = exitPolicy.buildDefaultExitPlan(unknownXml, { unknown: { action: 'disable' } });
const overridePatched = exitPolicy.applyExitPlanToStrategyXml(unknownXml, overridePlan);
assert.match(overridePatched, /#UnknownExit\.Custom#"[^>]*>0<\/Param>/, 'explicit override should allow disabling unknown exits');

exitPolicy.setUserOverride('exit_after_days', { action: 'keep' });
assert.equal(exitPolicy.getPolicy().overrides.exit_after_days.action, 'keep', 'user overrides should persist in policy state');
exitPolicy.setUserOverride('exit_after_days', null);
assert.equal(exitPolicy.getPolicy().overrides.exit_after_days, undefined, 'empty override should clear policy state');

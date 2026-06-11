import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { assert, repoRoot } from './harness.mjs';

const pluginIndex = path.join(repoRoot, 'integrations', 'sqx144', 'results_plugins', 'Regime Edge Analyzer', 'index.html');
const url = pathToFileURL(pluginIndex).href;

const browser = await chromium.launch({ headless: true });
try {
  for (const [label, viewport] of Object.entries({
    desktop: { width: 1440, height: 960 },
    mobile: { width: 390, height: 820 },
  })) {
    const page = await browser.newPage({ viewport });
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto(url);
    await page.waitForSelector('[data-regime-label]');
    await page.waitForFunction(() => window.__SQX_REGIME_EDGE__ && window.__SQX_REGIME_EDGE__.evaluate().label !== 'REGIME_UNKNOWN');
    const regimeLabel = await page.locator('[data-regime-label]').textContent();
    assert.ok(regimeLabel.trim().startsWith('REGIME_'), `${label} should render regime label`);
    const score = await page.locator('[data-regime-score]').textContent();
    assert.ok(/^\d+\/100$/.test(score.trim()), `${label} should render Regime Score`);
    assert.ok(await page.locator('[data-year-timeline] .year-card').count() >= 2, `${label} should render annual cards`);
    assert.ok(await page.locator('[data-detail-rows] tr').count() >= 2, `${label} should render detail rows`);
    assert.ok(await page.locator('.guard').count() >= 4, `${label} should render methodology notes`);
    const beforeOrders = await page.evaluate(() => window.__SQX_REGIME_EDGE__.state.messagesSent.map(item => item.type));
    assert.equal(beforeOrders.includes('GET_ORDERS'), false, `${label} should not auto-request GET_ORDERS`);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
    assert.equal(overflow, false, `${label} should not horizontally overflow`);

    await page.evaluate(() => window.__SQX_REGIME_EDGE__.loadFixture('longBullMismatch'));
    await page.waitForFunction(() => window.__SQX_REGIME_EDGE__.evaluate().label === 'REGIME_MISMATCH_REVIEW');
    await page.evaluate(() => window.__SQX_REGIME_EDGE__.loadFixture('missingSeries'));
    await page.waitForFunction(() => window.__SQX_REGIME_EDGE__.evaluate().label === 'REGIME_UNKNOWN');
    await page.evaluate(() => window.__SQX_REGIME_EDGE__.loadFixture('sidewaysMeanRevert'));
    await page.waitForFunction(() => window.__SQX_REGIME_EDGE__.evaluate().label === 'REGIME_MEAN_REVERT');
    const summary = await page.evaluate(() => window.__SQX_REGIME_EDGE__.buildSummary());
    assert.ok(summary.includes('Regime Score'), `${label} summary should include Regime Score`);

    await page.locator('[data-copy-summary]').click();
    await page.waitForFunction(() => ['copied', 'selectable fallback'].includes(document.querySelector('[data-copy-state]').textContent.trim()));
    await page.locator('[data-language-toggle]').click();
    await page.waitForFunction(() => document.documentElement.lang === 'es');
    await page.locator('[data-theme-toggle]').click();
    await page.waitForFunction(() => document.documentElement.getAttribute('data-theme') === 'dark');

    await page.evaluate(() => {
      window.__SQX_REGIME_EDGE__.state.strategy = { id: 'realish', resultKey: 'Portfolio', name: 'Realish AUDCAD H1 L' };
      window.__SQX_REGIME_EDGE__.state.messagesSent = [];
    });
    await page.locator('[data-orders-button]').click();
    const sent = await page.evaluate(() => window.__SQX_REGIME_EDGE__.state.messagesSent.map(item => item.type));
    assert.ok(sent.includes('GET_ORDERS'), `${label} should send GET_ORDERS after opt-in`);
    assert.equal(errors.length, 0, `${label} browser errors: ${errors.join('\n')}`);
    await page.close();
  }
} finally {
  await browser.close();
}

console.log('sqx144 custom results8 regime edge analyzer render smoke ok');

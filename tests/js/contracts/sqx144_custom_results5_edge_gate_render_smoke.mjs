import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { assert, repoRoot } from './harness.mjs';

const pluginIndex = path.join(repoRoot, 'integrations', 'sqx144', 'results_plugins', 'SQX Edge Gate', 'index.html');
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
    await page.waitForSelector('[data-verdict]');
    await page.waitForFunction(() => window.__SQX_EDGE_GATE__ && window.__SQX_EDGE_GATE__.evaluate().verdict === 'PASS');
    const verdict = await page.locator('[data-verdict]').textContent();
    assert.equal(verdict.trim(), 'PASS', `${label} should render PASS fixture`);
    await page.waitForSelector('[data-pipeline-select]');
    const pipeline = await page.locator('[data-pipeline-select]').inputValue();
    assert.equal(pipeline, 'build', `${label} should render Build pipeline context`);
    const gateScore = await page.locator('[data-gate-score]').textContent();
    assert.ok(/^\d+\/100$/.test(gateScore.trim()), `${label} should render Gate Score`);
    assert.ok(await page.locator('[data-decision-matrix] .matrix-row').count() >= 5, `${label} should render decision matrix rows`);
    assert.equal(await page.locator('[data-order-panel]').isHidden(), true, `${label} should keep Order Radar collapsed before opt-in`);
    assert.equal(await page.locator('text=Methodology Guardrails').count(), 0, `${label} should not render the old guardrails panel`);
    assert.equal(await page.locator('text=Official Tabs').count(), 0, `${label} should not render the old official-tabs panel`);
    assert.equal(await page.locator('text=Manual Export').count(), 0, `${label} should not render the old manual export panel`);
    const beforeOrders = await page.evaluate(() => window.__SQX_EDGE_GATE__.state.messagesSent.map(item => item.type));
    assert.equal(beforeOrders.includes('GET_ORDERS'), false, `${label} should not auto-request GET_ORDERS`);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
    assert.equal(overflow, false, `${label} should not horizontally overflow`);
    const radarBox = await page.locator('.radar-svg').boundingBox();
    assert.ok(radarBox && radarBox.width > 100 && radarBox.height > 100, `${label} radar should be visible`);
    await page.evaluate(() => {
      window.__SQX_EDGE_GATE__.loadFixture('tickRealRetentionBlock');
      window.__SQX_EDGE_GATE__.setPreviousTrades(140);
    });
    await page.waitForFunction(() => window.__SQX_EDGE_GATE__.evaluate().verdict === 'BLOCK');
    await page.evaluate(() => window.__SQX_EDGE_GATE__.loadFixture('ordersLateDegradation'));
    await page.waitForFunction(() => window.__SQX_EDGE_GATE__.evaluate().verdict === 'REVIEW');
    const summary = await page.evaluate(() => window.__SQX_EDGE_GATE__.buildSummary());
    assert.ok(summary.includes('Gate Score'), `${label} summary should include Gate Score`);
    await page.locator('[data-copy-summary]').click();
    await page.waitForFunction(() => ['copied', 'selectable fallback'].includes(document.querySelector('[data-copy-state]').textContent.trim()));
    await page.locator('[data-language-toggle]').click();
    await page.waitForFunction(() => document.documentElement.lang === 'es');
    await page.locator('[data-theme-toggle]').click();
    await page.waitForFunction(() => document.documentElement.getAttribute('data-theme') === 'dark');
    await page.locator('[data-orders-button]').click();
    const sent = await page.evaluate(() => window.__SQX_EDGE_GATE__.state.messagesSent.map(item => item.type));
    assert.ok(sent.includes('GET_ORDERS'), `${label} should send GET_ORDERS after opt-in`);
    assert.equal(await page.locator('[data-order-panel]').isVisible(), true, `${label} should show Order Radar after opt-in`);
    assert.equal(errors.length, 0, `${label} browser errors: ${errors.join('\n')}`);
    await page.close();
  }
} finally {
  await browser.close();
}

console.log('sqx144 custom results5 edge gate render smoke ok');

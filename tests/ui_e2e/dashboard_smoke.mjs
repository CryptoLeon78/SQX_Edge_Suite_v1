import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const dashboardUrl = 'file:///' + path.join(repoRoot, 'app', 'SQX_Dashboard_v6.html').replace(/\\/g, '/');
const screenshotsEnabled = process.env.SQX_E2E_SCREENSHOTS === '1';
const screenshotDir = path.join(repoRoot, 'output', 'playwright');

async function assertNoMobileOverflow(page) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 8);
  if (overflow) throw new Error('Mobile viewport has horizontal overflow');
}

function collectBrowserErrors(page, bucket) {
  page.on('pageerror', error => bucket.push(`pageerror: ${error.message}`));
  page.on('console', message => {
    if (message.type() !== 'error') return;
    const text = message.text();
    if (text.includes('net::ERR_CONNECTION_REFUSED')) return;
    bucket.push(`console error: ${text}`);
  });
}

function assertNoBrowserErrors(bucket, label) {
  if (bucket.length) throw new Error(`${label} browser errors:\n${bucket.join('\n')}`);
}

async function saveShot(page, name) {
  if (!screenshotsEnabled) return;
  await mkdir(screenshotDir, { recursive: true });
  await page.screenshot({ path: path.join(screenshotDir, name), fullPage: true });
}

async function run() {
  const browser = await chromium.launch({ headless: true });
  try {
    const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const desktopErrors = [];
    collectBrowserErrors(desktop, desktopErrors);
    await desktop.goto(dashboardUrl, { waitUntil: 'load' });
    await desktop.waitForSelector('.tab[data-tab="inicio"].active');
    await desktop.waitForSelector('#home-readiness-score');
    await desktop.locator('[data-home-tab="pipeline"]').first().click();
    await desktop.waitForSelector('.tab[data-tab="pipeline"].active');
    await desktop.locator('.tab[data-tab="activos"]').click();
    await desktop.waitForSelector('.tab[data-tab="activos"].active');
    await desktop.locator('[data-filter-type="forex"]').click();
    await desktop.waitForSelector('[data-filter-type="forex"].active');
    await desktop.fill('#search-asset', 'EUR');
    await desktop.waitForSelector('#asset-grid .asset-card');
    await desktop.evaluate(() => navToAsset('EURUSD'));
    await desktop.waitForSelector('#detail-panel.visible');
    await desktop.locator('.tab[data-tab="estrategias"]').click();
    await desktop.waitForSelector('#tab-estrategias .strat-card');
    const cards = await desktop.locator('#tab-estrategias .strat-card').count();
    const deleteButtons = await desktop.locator('#tab-estrategias .strat-remove-btn').count();
    if (cards < 1) throw new Error('Strategies tab rendered without strategy cards');
    if (cards !== deleteButtons) throw new Error(`Expected one delete button per card, got ${cards} cards and ${deleteButtons} buttons`);

    desktop.on('dialog', dialog => dialog.accept());
    await desktop.locator('#tab-estrategias .strat-remove-btn').first().click();
    await desktop.waitForFunction(() => localStorage.getItem('sqx_strategies_deleted_v1') !== null);
    const afterDelete = await desktop.locator('#tab-estrategias .strat-card').count();
    if (afterDelete !== cards - 1) throw new Error(`Deleting a base strategy should hide exactly one card, got ${afterDelete} from ${cards}`);
    await desktop.locator('#strat-restore-hidden-btn').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_strategies_deleted_v1') || '[]').length === 0);
    const afterRestore = await desktop.locator('#tab-estrategias .strat-card').count();
    if (afterRestore !== cards) throw new Error(`Restoring hidden strategies should recover cards, got ${afterRestore} from ${cards}`);
    await saveShot(desktop, 'e2e-strategies-desktop.png');
    assertNoBrowserErrors(desktopErrors, 'desktop');
    await desktop.close();

    const mobile = await browser.newPage({ viewport: { width: 390, height: 920 } });
    const mobileErrors = [];
    collectBrowserErrors(mobile, mobileErrors);
    await mobile.goto(dashboardUrl, { waitUntil: 'load' });
    await mobile.waitForSelector('.tab[data-tab="inicio"].active');
    await mobile.locator('.tab[data-tab="estrategias"]').click();
    await mobile.waitForSelector('#tab-estrategias .strat-card');
    const activeTabBox = await mobile.locator('.tab.active').boundingBox();
    const tabsBox = await mobile.locator('.tabs').boundingBox();
    if (activeTabBox && activeTabBox.height > 80) throw new Error('Mobile active tab is too tall');
    if (tabsBox && tabsBox.height > 90) throw new Error('Mobile tabs bar is too tall');
    await assertNoMobileOverflow(mobile);
    await saveShot(mobile, 'e2e-strategies-mobile.png');
    assertNoBrowserErrors(mobileErrors, 'mobile');
    await mobile.close();
  } finally {
    await browser.close();
  }
}

run().catch(error => {
  console.error(error);
  process.exit(1);
});

import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
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
    desktop.on('dialog', dialog => dialog.accept());
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
    await desktop.locator('.tab[data-tab="workflow"]').click();
    await desktop.waitForSelector('.tab[data-tab="workflow"].active');
    await desktop.evaluate(() => localStorage.removeItem('sqx_workflow_checklist_v1'));
    await desktop.locator('.subtab[data-subtab="wf-capa1"]').click();
    await desktop.waitForSelector('#wf-capa1.active');
    await desktop.locator('input[data-check="capa1-pre-mm"]').check();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_workflow_checklist_v1') || '{}')['capa1-pre-mm'] === true);
    await desktop.locator('button[data-checklist-clear="capa1"]').click();
    await desktop.waitForFunction(() => !JSON.parse(localStorage.getItem('sqx_workflow_checklist_v1') || '{}')['capa1-pre-mm']);
    const workflowChecked = await desktop.locator('input[data-check="capa1-pre-mm"]').isChecked();
    if (workflowChecked) throw new Error('Workflow checklist clear should uncheck capa1 items');
    await saveShot(desktop, 'e2e-workflow-desktop.png');
    await desktop.locator('.subtab[data-subtab="wf-overview"]').click();
    await desktop.waitForSelector('#wf-overview.active');
    await saveShot(desktop, 'e2e-workflow-handoff-desktop.png');
    await desktop.locator('#workflow-views-handoff [data-vc-handoff="robustness"]').click();
    await desktop.waitForSelector('.tab[data-tab="views"].active');
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'SQX Robustez');
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 104);
    await desktop.locator('.tab[data-tab="projectgen"]').click();
    await desktop.waitForSelector('.tab[data-tab="projectgen"].active');
    await desktop.waitForSelector('#pg-onboarding-title');
    await desktop.waitForFunction(() => document.getElementById('pg-onboarding-progress')?.textContent.trim() === '0/4');
    await desktop.waitForFunction(() => document.getElementById('pg-onboarding-steps')?.querySelectorAll('.pg-step').length === 4);
    await desktop.waitForSelector('#pg-custom-generate');
    await desktop.locator('#pg-custom-asset').fill('EURUSD');
    await desktop.locator('#pg-custom-tf').fill('H1');
    await desktop.locator('#pg-custom-name').fill('Custom_EURUSD_H1');
    await desktop.locator('#pg-custom-capa').selectOption('1');
    await desktop.locator('#pg-custom-preset-name').fill('EURUSD H1 Smoke');
    await desktop.locator('#pg-custom-save-preset').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_pg_custom_presets_v1') || '[]').length === 1);
    await desktop.locator('#pg-custom-asset').fill('GBPUSD');
    await desktop.locator('#pg-custom-load-preset').click();
    await desktop.waitForFunction(() => document.getElementById('pg-custom-asset')?.value === 'EURUSD');
    await desktop.locator('#pg-custom-delete-preset').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_pg_custom_presets_v1') || '[]').length === 0);
    await desktop.waitForFunction(() => document.getElementById('pg-custom-status')?.textContent.includes('Preset eliminado'));
    await saveShot(desktop, 'e2e-projectgen-desktop.png');
    await desktop.locator('.tab[data-tab="views"]').click();
    await desktop.waitForSelector('.tab[data-tab="views"].active');
    await desktop.waitForSelector('#vc-metric-list .views-metric-row');
    await desktop.locator('[data-vc-preset="egt-core"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-column-count')?.textContent.trim() === '104');
    await desktop.locator('#vc-year-count').fill('5');
    await desktop.waitForFunction(() => document.getElementById('vc-column-count')?.textContent.trim() === '64');
    await desktop.locator('[data-vc-preset="risk"]').click();
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    await desktop.waitForSelector('#vc-template-list .views-template-card');
    const templateCount = await desktop.locator('#vc-template-list .views-template-card').count();
    if (templateCount < 4) throw new Error(`Expected buyer-ready SQX Views examples, got ${templateCount}`);
    await desktop.locator('[data-vc-template-load="risk-capital-review"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'Risk Capital Review');
    await desktop.locator('[data-vc-template-save="risk-capital-review"]').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_view_creator_presets_v1') || '[]').some(preset => preset.id === 'buyer-risk-capital-review'));
    const buyerPack = await desktop.evaluate(() => window.SQX.viewCreator.buildBuyerReadyTemplatePack());
    if (buyerPack.type !== 'sqx-edge.view-presets' || buyerPack.presets.length < 4) throw new Error('SQX Views buyer-ready pack contract failed');
    await desktop.evaluate(() => localStorage.removeItem('sqx_view_creator_presets_v1'));
    await desktop.locator('#vc-year-count').fill('5');
    await desktop.locator('[data-vc-preset="risk"]').click();
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    await desktop.locator('#vc-preset-name').fill('Risk V2 Smoke');
    await desktop.locator('#vc-save-preset-btn').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_view_creator_presets_v1') || '[]').length === 1);
    const exportedPack = await desktop.evaluate(() => window.SQX.viewCreator.buildPresetPackage());
    if (exportedPack.type !== 'sqx-edge.view-presets' || exportedPack.presets.length !== 1) throw new Error('SQX Views export pack contract failed');
    await desktop.locator('[data-vc-preset="egt-core"]').click();
    await desktop.waitForFunction(() => document.getElementById('vc-column-count')?.textContent.trim() === '64');
    await desktop.locator('#vc-load-preset-btn').click();
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    await desktop.locator('#vc-delete-preset-btn').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_view_creator_presets_v1') || '[]').length === 0);
    await mkdir(screenshotDir, { recursive: true });
    const importPackPath = path.join(screenshotDir, 'view-preset-pack-smoke.json');
    await writeFile(importPackPath, JSON.stringify(exportedPack, null, 2), 'utf8');
    await desktop.locator('#vc-import-presets-file').setInputFiles(importPackPath);
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_view_creator_presets_v1') || '[]').length === 1);
    await desktop.locator('#vc-load-preset-btn').click();
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    await saveShot(desktop, 'e2e-view-creator-desktop.png');
    await desktop.locator('.tab[data-tab="estrategias"]').click();
    await desktop.waitForSelector('#tab-estrategias .strat-card');
    const cards = await desktop.locator('#tab-estrategias .strat-card').count();
    const deleteButtons = await desktop.locator('#tab-estrategias .strat-remove-btn').count();
    if (cards < 1) throw new Error('Strategies tab rendered without strategy cards');
    if (cards !== deleteButtons) throw new Error(`Expected one delete button per card, got ${cards} cards and ${deleteButtons} buttons`);

    await desktop.locator('#tab-estrategias .strat-remove-btn').first().click();
    await desktop.waitForFunction(() => localStorage.getItem('sqx_strategies_deleted_v1') !== null);
    const afterDelete = await desktop.locator('#tab-estrategias .strat-card').count();
    if (afterDelete !== cards - 1) throw new Error(`Deleting a base strategy should hide exactly one card, got ${afterDelete} from ${cards}`);
    await desktop.locator('#strat-restore-hidden-btn').click();
    await desktop.waitForFunction(() => JSON.parse(localStorage.getItem('sqx_strategies_deleted_v1') || '[]').length === 0);
    const afterRestore = await desktop.locator('#tab-estrategias .strat-card').count();
    if (afterRestore !== cards) throw new Error(`Restoring hidden strategies should recover cards, got ${afterRestore} from ${cards}`);
    await saveShot(desktop, 'e2e-strategies-desktop.png');
    await desktop.locator('#strat-views-handoff [data-vc-handoff="risk"]').click();
    await desktop.waitForSelector('.tab[data-tab="views"].active');
    await desktop.waitForFunction(() => document.getElementById('vc-view-name')?.value === 'SQX Risk Review');
    await desktop.waitForFunction(() => Number(document.getElementById('vc-column-count')?.textContent.trim() || 0) > 64);
    assertNoBrowserErrors(desktopErrors, 'desktop');
    await desktop.close();

    const mobile = await browser.newPage({ viewport: { width: 390, height: 920 } });
    const mobileErrors = [];
    collectBrowserErrors(mobile, mobileErrors);
    await mobile.goto(dashboardUrl, { waitUntil: 'load' });
    await mobile.waitForSelector('.tab[data-tab="inicio"].active');
    await mobile.locator('.tab[data-tab="views"]').click();
    await mobile.waitForSelector('#vc-preview');
    await assertNoMobileOverflow(mobile);
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

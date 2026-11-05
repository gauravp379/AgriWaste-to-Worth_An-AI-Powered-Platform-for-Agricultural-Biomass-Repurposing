// @ts-check
const { test, expect } = require('@playwright/test');
const { AnalyzerPage } = require('./pages/analyzer.page');

test.describe('AI Residue Analyzer E2E Tests', () => {
  let analyzer;

  test.beforeEach(async ({ page }) => {
    analyzer = new AnalyzerPage(page);
    await analyzer.goto();
  });

  test('TC-AI-01: Page renders drag-and-drop zone and 1-click sample crop pills', async ({ page }) => {
    await expect(analyzer.dropZone).toBeVisible();
    await expect(page.locator('.sample-crops-bar')).toBeVisible();
  });

  test('TC-AI-02: Clicking sample crop runs 5-stage neural pipeline and displays results', async ({ page }) => {
    await analyzer.loadSampleCrop('rice');
    await analyzer.waitForScanCompletion();
    
    await expect(analyzer.resultsSection).toBeVisible();
    await expect(analyzer.classifiedCropName).toContainText(/Rice/i);
    await expect(analyzer.confidencePill).toBeVisible();
  });

  test('TC-AI-03: Industrial buyers and seasonality price chart render in results', async ({ page }) => {
    await analyzer.loadSampleCrop('sugarcane');
    await analyzer.waitForScanCompletion();

    await expect(page.locator('#matchedBuyersList')).toBeVisible();
    await expect(page.locator('#priceTrendChart')).toBeVisible();
  });

  test('TC-AI-04: One-click "List this waste in Marketplace" bridges prefill data', async ({ page }) => {
    await analyzer.loadSampleCrop('rice');
    await analyzer.waitForScanCompletion();

    await analyzer.clickListThisWaste();
    await expect(page).toHaveURL(/marketplace\.html/);

    // Verify Add Listing modal was opened automatically
    const modal = page.locator('#addListingModal');
    await expect(modal).toBeVisible();
    
    // Check prefilled crop selection
    const cropVal = await page.locator('#wizCropSelect').inputValue();
    expect(cropVal).toBe('rice');
  });

  test('TC-AI-05: AES-GCM 256-bit report vault encrypts lab ledger', async ({ page }) => {
    await analyzer.loadSampleCrop('wheat');
    await analyzer.waitForScanCompletion();

    await analyzer.encryptReport();
    await expect(page.locator('#encryptedVaultStatus')).toBeVisible();
    const vaultText = await page.locator('#vaultCipherPreview').textContent();
    expect(vaultText).toBeTruthy();
  });
});


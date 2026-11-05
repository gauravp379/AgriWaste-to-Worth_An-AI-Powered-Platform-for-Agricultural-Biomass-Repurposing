// @ts-check

/**
 * Page Object Model for AI Residue Analyzer
 */
class AnalyzerPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
    this.dropZone = page.locator('#dropZone');
    this.steppedProgress = page.locator('#steppedProgress');
    this.resultsSection = page.locator('#resultsSection');
    this.classifiedCropName = page.locator('#classifiedCropName');
    this.confidencePill = page.locator('#confidencePill');
    this.exportPdfBtn = page.locator('#exportPdfBtn');
    this.listThisWasteBtn = page.locator('#listThisWasteBtn');
    this.encryptReportBtn = page.locator('#encryptReportBtn');
    this.encryptedVaultStatus = page.locator('#encryptedVaultStatus');
    this.sampleRiceBtn = page.locator('button[onclick*="rice"]');
    this.sampleWheatBtn = page.locator('button[onclick*="wheat"]');
    this.sampleBagasseBtn = page.locator('button[onclick*="sugarcane"]');
  }

  async goto() {
    await this.page.goto('/ai-analyzer.html');
    await this.page.waitForLoadState('domcontentloaded');
  }

  async loadSampleCrop(cropKey = 'rice') {
    const btn = this.page.locator(`button[onclick*="'${cropKey}'"]`);
    await btn.click();
  }

  async waitForScanCompletion() {
    // Wait for stepped progress to complete or resultsSection to be visible
    await this.resultsSection.waitFor({ state: 'visible', timeout: 15000 });
  }

  async clickListThisWaste() {
    await this.listThisWasteBtn.click();
    // Navigates to marketplace.html with prefill modal open
    await this.page.waitForURL(/marketplace\.html/);
  }

  async encryptReport() {
    await this.encryptReportBtn.click();
    await this.encryptedVaultStatus.waitFor({ state: 'visible', timeout: 5000 });
  }
}

module.exports = { AnalyzerPage };


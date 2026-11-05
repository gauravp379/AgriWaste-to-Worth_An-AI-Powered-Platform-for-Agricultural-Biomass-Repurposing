// @ts-check

/**
 * Page Object Model for Multi-Role Dashboard Command Portals
 */
class DashboardPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
    this.switcherBar = page.locator('#portalSwitcherBar');
    this.btnFarmer = page.locator('#btnSwitchFarmer');
    this.btnBuyer = page.locator('#btnSwitchBuyer');
    this.btnAdmin = page.locator('#btnSwitchAdmin');
    this.farmerPortal = page.locator('#farmerPortalView');
    this.buyerPortal = page.locator('#buyerPortalView');
    this.adminPortal = page.locator('#adminPortalView');
    this.farmerListingsTable = page.locator('#farmerListingsTableBody');
    this.farmerWasteSold = page.locator('#farmerWasteSold');
    this.farmerEarnings = page.locator('#farmerTotalEarnings');
    this.buyerSpend = page.locator('#buyerTotalSpend');
    this.adminGmv = page.locator('#adminGmv');
    this.adminKycTable = page.locator('#adminKycTableBody');
    this.themeToggleBtn = page.locator('#themeToggleBtn');
    this.sunlightContrastBtn = page.locator('#sunlightContrastBtn');
  }

  async goto() {
    await this.page.goto('/dashboard.html');
    await this.page.waitForLoadState('domcontentloaded');
  }

  async switchToFarmer() {
    await this.btnFarmer.click();
    await this.farmerPortal.waitFor({ state: 'visible' });
  }

  async switchToBuyer() {
    await this.btnBuyer.click();
    await this.buyerPortal.waitFor({ state: 'visible' });
  }

  async switchToAdmin() {
    await this.btnAdmin.click();
    await this.adminPortal.waitFor({ state: 'visible' });
  }

  async approveFirstKyc() {
    const firstApproveBtn = this.adminKycTable.locator('.btn-approve').first();
    await firstApproveBtn.click();
  }
}

module.exports = { DashboardPage };


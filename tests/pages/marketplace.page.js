// @ts-check

/**
 * Page Object Model for Marketplace (Residue Exchange)
 */
class MarketplacePage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
    this.searchInput = page.locator('#searchInput');
    this.voiceSearchBtn = page.locator('#voiceSearchBtn');
    this.categorySelect = page.locator('#categoryFilter');
    this.stateSelect = page.locator('#stateFilter');
    this.minPriceInput = page.locator('#minPrice');
    this.maxPriceInput = page.locator('#maxPrice');
    this.applyPriceBtn = page.locator('#applyPriceFilter');
    this.clearFiltersBtn = page.locator('#clearFiltersBtn');
    this.activeFilterChips = page.locator('#activeFilterChips');
    this.listingsGrid = page.locator('#listingsGrid');
    this.listingCards = page.locator('#listingsGrid .listing-card');
    this.filterSheetToggleBtn = page.locator('#filterSheetToggleBtn');
    this.sidebar = page.locator('.marketplace-sidebar');
    this.quickViewModal = page.locator('#quickViewModal');
    this.addListingModal = page.locator('#addListingModal');
    this.cartBtn = page.locator('#cartBtn');
    this.cartSidebar = page.locator('#cartSidebar');
    this.checkoutModal = page.locator('#checkoutModal');
    this.openAddListingBtn = page.locator('#openAddListingBtn');
  }

  async goto() {
    await this.page.goto('/marketplace.html');
    await this.page.waitForLoadState('domcontentloaded');
  }

  async searchCrop(query) {
    await this.searchInput.fill(query);
    await this.searchInput.dispatchEvent('input');
    await this.page.waitForTimeout(350);
  }

  async filterByCategory(category) {
    await this.categorySelect.selectOption(category);
    await this.page.waitForTimeout(300);
  }

  async setPriceRange(min, max) {
    await this.minPriceInput.fill(String(min));
    await this.maxPriceInput.fill(String(max));
    await this.applyPriceBtn.click();
    await this.page.waitForTimeout(300);
  }

  async openFirstQuickView() {
    const firstQuickBtn = this.listingCards.first().locator('.btn-quick-view');
    await firstQuickBtn.click();
    await this.quickViewModal.waitFor({ state: 'visible' });
  }

  async closeQuickView() {
    await this.quickViewModal.locator('#closeQuickViewModal').click();
    await this.quickViewModal.waitFor({ state: 'hidden' });
  }

  async addFirstItemToCart() {
    const firstCartBtn = this.listingCards.first().locator('.btn-add-cart');
    await firstCartBtn.click();
  }

  async openAddListingWizard() {
    await this.openAddListingBtn.click();
    await this.addListingModal.waitFor({ state: 'visible' });
  }

  async completeAddListingWizard(crop, title, qty, price, moisture = '12') {
    await this.openAddListingWizard();
    // Step 1: Residue Classification
    await this.page.locator('#wizCropSelect').selectOption(crop);
    await this.page.locator('#wizTitle').fill(title);
    await this.page.locator('.btn-wiz-next').click();
    await this.page.waitForTimeout(200);

    // Step 2: Quality & Metrics
    await this.page.locator('#wizMoisture').fill(moisture);
    await this.page.locator('.btn-wiz-next').click();
    await this.page.waitForTimeout(200);

    // Step 3: Logistics & Pricing
    await this.page.locator('#wizQuantity').fill(String(qty));
    await this.page.locator('#wizPrice').fill(String(price));
    await this.page.locator('#wizLocation').fill('Ludhiana, Punjab');
    await this.page.locator('#btnPublishListing').click();
    await this.page.waitForTimeout(500);
  }
}

module.exports = { MarketplacePage };


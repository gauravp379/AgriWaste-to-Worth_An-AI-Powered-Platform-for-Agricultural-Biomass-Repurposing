// @ts-check
const { test, expect } = require('@playwright/test');
const { MarketplacePage } = require('./pages/marketplace.page');

test.describe('Marketplace (Residue Exchange) E2E Tests', () => {
  let marketplace;

  test.beforeEach(async ({ page }) => {
    marketplace = new MarketplacePage(page);
    await marketplace.goto();
  });

  test('TC-MKT-01: Page loads with Mandi Intelligence bar and listing cards', async ({ page }) => {
    await expect(page.locator('.market-intelligence-bar')).toBeVisible();
    await expect(marketplace.listingsGrid).toBeVisible();
    const count = await marketplace.listingCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('TC-MKT-02: Search filters listings in real-time', async ({ page }) => {
    await marketplace.searchCrop('rice');
    const count = await marketplace.listingCards.count();
    expect(count).toBeGreaterThan(0);
    const firstTitle = await marketplace.listingCards.first().locator('.card-title').textContent();
    expect(firstTitle?.toLowerCase()).toContain('rice');
  });

  test('TC-MKT-03: Quick-view modal displays verified laboratory metrics', async ({ page }) => {
    await marketplace.openFirstQuickView();
    await expect(marketplace.quickViewModal).toBeVisible();
    await expect(page.locator('#qvMoisture')).toBeVisible();
    await expect(page.locator('#qvCalorific')).toBeVisible();
    await expect(page.locator('#qvCo2Offset')).toBeVisible();
    await marketplace.closeQuickView();
    await expect(marketplace.quickViewModal).toBeHidden();
  });

  test('TC-MKT-04: Adding item to cart updates cart counter badge', async ({ page }) => {
    const initialBadge = await page.locator('#cartBadge').textContent();
    await marketplace.addFirstItemToCart();
    const updatedBadge = await page.locator('#cartBadge').textContent();
    expect(Number(updatedBadge)).toBeGreaterThanOrEqual(1);
  });

  test('TC-MKT-05: 3-step listing wizard publishes new crop residue lot', async ({ page }) => {
    const lotTitle = 'High-Density Rice Stubble Bales - Batch #99';
    await marketplace.completeAddListingWizard('rice', lotTitle, 65, 5300, '11.5');
    
    // Verify lot is now at top of listings grid
    const firstCardTitle = await marketplace.listingCards.first().locator('.card-title').textContent();
    expect(firstCardTitle).toContain(lotTitle);
  });

  test('TC-MKT-06: Mobile responsive bottom sheet filter drawer opens on mobile', async ({ page, viewport }) => {
    if (viewport && viewport.width < 768) {
      await expect(marketplace.filterSheetToggleBtn).toBeVisible();
      await marketplace.filterSheetToggleBtn.click();
      await expect(page.locator('.marketplace-sidebar')).toHaveClass(/sheet-open/);
    }
  });
});


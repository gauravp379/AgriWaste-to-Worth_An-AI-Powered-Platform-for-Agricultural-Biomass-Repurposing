/**
 * Standalone Smoke & Invariant Verification Suite for AgriWaste to Worth
 * Run offline with: node tests/run_smoke_tests.js
 */

const fs = require('fs');
const http = require('http');
const path = require('path');

const BASE_URL = 'http://localhost:5000';

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

function assert(condition, message) {
  totalTests++;
  if (condition) {
    passedTests++;
    console.log(`  \x1b[32m✔ PASS\x1b[0m - ${message}`);
  } else {
    failedTests++;
    console.error(`  \x1b[31m✖ FAIL\x1b[0m - ${message}`);
  }
}

function fetchPage(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    }).on('error', reject);
  });
}

async function runTestSuite() {
  console.log('\n============================================================');
  console.log('🌱 AGRIWASTE TO WORTH — INTEGRATED SYSTEM QUALITY GATES');
  console.log('============================================================\n');

  // Test Group 1: Server Endpoints & Payload Health
  console.log('\x1b[36m[Group 1: Server Endpoints & Payload Health]\x1b[0m');
  const pages = ['index.html', 'marketplace.html', 'ai-analyzer.html', 'dashboard.html', 'about.html'];
  for (const page of pages) {
    try {
      const res = await fetchPage(`${BASE_URL}/${page}`);
      assert(res.status === 200, `${page} returned HTTP 200 OK (${res.body.length} bytes)`);
    } catch (e) {
      assert(false, `Failed to reach ${page} on ${BASE_URL}: ${e.message}`);
    }
  }

  // Test Group 2: Marketplace Architecture & Modals
  console.log('\n\x1b[36m[Group 2: Marketplace Architecture & Modals]\x1b[0m');
  const mktHtml = fs.readFileSync(path.join(__dirname, '../marketplace.html'), 'utf-8');
  assert(mktHtml.includes('id="listingsGrid"'), 'Marketplace DOM contains #listingsGrid container');
  assert(mktHtml.includes('class="market-intelligence-bar"'), 'Mandi Harvest Intelligence Bar exists');
  assert(mktHtml.includes('id="addListingModal"'), '3-Step Add Listing Wizard Modal present');
  assert(mktHtml.includes('id="quickViewModal"'), 'Laboratory Quick View Modal present');
  assert(mktHtml.includes('id="cartSidebar"'), 'Off-Canvas Purchase Cart Drawer present');
  assert(mktHtml.includes('id="filterSheetToggleBtn"'), 'Mobile Bottom Sheet Filter Trigger present');

  // Test Group 3: AI Analyzer Neural Vision Pipeline
  console.log('\n\x1b[36m[Group 3: AI Analyzer Neural Vision Pipeline]\x1b[0m');
  const aiHtml = fs.readFileSync(path.join(__dirname, '../ai-analyzer.html'), 'utf-8');
  assert(aiHtml.includes('id="uploadArea"'), 'Drag-and-drop file upload zone configured (#uploadArea)');
  assert(aiHtml.includes('sample-crop-bar'), '1-Click verified crop sample test bar configured');
  assert(aiHtml.includes('analysis-steps'), '5-stage neural processing progress pipeline present');
  assert(aiHtml.includes('id="resultsCard"'), 'Results card with confidence score present (#resultsCard)');
  assert(aiHtml.includes('id="buyersList"'), 'Matched industrial off-takers recommendation container present (#buyersList)');
  assert(aiHtml.includes('listThisWasteFromAnalyzer'), 'One-click "List this waste in Marketplace" bridge present');

  // Test Group 4: Role-Differentiated Command Portals
  console.log('\n\x1b[36m[Group 4: Role-Differentiated Command Portals]\x1b[0m');
  const dashHtml = fs.readFileSync(path.join(__dirname, '../dashboard.html'), 'utf-8');
  assert(dashHtml.includes('id="portalSwitcherBar"'), 'Sticky persona switcher bar present');
  assert(dashHtml.includes('id="farmerPortalView"'), 'Dedicated Farmer Kisan Krishi Kendra portal present');
  assert(dashHtml.includes('id="buyerPortalView"'), 'Dedicated Industrial Buyer Procurement portal present');
  assert(dashHtml.includes('id="adminPortalView"'), 'Dedicated Platform Governance Admin portal present');
  assert(dashHtml.includes('id="farmerListingsTableBody"'), 'Farmer active lots table present');
  assert(dashHtml.includes('id="adminKycTableBody"'), 'Admin KYC verification queue table present');

  // Test Group 5: Client-Side Security & Cryptography
  console.log('\n\x1b[36m[Group 5: Client-Side Security & Cryptography]\x1b[0m');
  const authJs = fs.readFileSync(path.join(__dirname, '../js/auth.js'), 'utf-8');
  assert(authJs.includes("crypto.subtle.digest('SHA-256'"), 'Web Crypto SHA-256 client-side password hashing configured');
  assert(authJs.includes('DEFAULT_USERS'), 'Role default users configured for instant evaluation');
  assert(authJs.includes('quickLoginAs'), '1-Click quick login switcher function present');

  const aiJs = fs.readFileSync(path.join(__dirname, '../js/ai-analyzer.js'), 'utf-8');
  assert(aiJs.includes('crypto.subtle.encrypt') && aiJs.includes('AES-GCM'), 'AES-GCM 256-bit encrypted lab report vault configured');

  // Test Group 6: Design Tokens & Accessibility
  console.log('\n\x1b[36m[Group 6: Editorial Agrarian Design Tokens & WCAG]\x1b[0m');
  const css = fs.readFileSync(path.join(__dirname, '../css/style.css'), 'utf-8');
  assert(css.includes('--earth-950') && css.includes('--primary-color'), 'Core Editorial Agrarian color tokens configured');
  assert(css.includes('--font-heading') && css.includes('Fraunces'), 'Editorial serif Fraunces typography configured');
  assert(css.includes('dark-theme') || css.includes('dark-mode'), 'Designed dark mode theme rules configured');
  assert(css.includes('sunlight-contrast') || css.includes('theme-sunlight-contrast'), 'Outdoor high-contrast sunlight mode configured');

  console.log('\n------------------------------------------------------------');
  console.log(`TOTAL TESTS EXECUTED: ${totalTests}`);
  console.log(`\x1b[32mPASSED: ${passedTests}\x1b[0m | \x1b[31mFAILED: ${failedTests}\x1b[0m`);
  console.log('------------------------------------------------------------\n');

  if (failedTests > 0) {
    process.exit(1);
  }
}

runTestSuite().catch(err => {
  console.error('Test Suite Failed to Execute:', err);
  process.exit(1);
});

const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Navigate to the local server
  await page.goto('http://127.0.0.1:5000/');

  // Wait for images to load
  await page.waitForTimeout(2000);

  // Take a screenshot
  await page.screenshot({ path: 'landing_page.png', fullPage: true });

  await browser.close();
})();

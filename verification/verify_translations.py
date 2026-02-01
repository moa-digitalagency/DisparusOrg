
import asyncio
from playwright.async_api import async_playwright
import os

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 3000})

        # 1. Login to admin
        await page.goto("http://localhost:3000/admin/login")
        await page.fill("input[name='username']", "admin")
        await page.fill("input[name='password']", "admin123")
        await page.click("button[type='submit']")

        # 2. Check Admin Reports List
        await page.goto("http://localhost:3000/admin/reports")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path="/home/jules/verification/admin_list_v2.png")
        print("Captured admin list v2")

        # 3. Check Admin Edit Person
        # Find first edit link
        await page.click("a:has-text('Modifier')")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path="/home/jules/verification/admin_edit_person_v2.png")
        print("Captured admin edit person v2")

        # 4. Check Public Detail Contribution
        await page.goto("http://localhost:3000/")
        await page.wait_for_selector("text=Voir tout")
        await page.click("text=Voir tout")
        await page.wait_for_load_state("networkidle")
        # Click first report
        await page.locator(".grid > div").first.click()
        await page.wait_for_load_state("networkidle")

        # Select contribution type 'found' to show proof fields
        # Try to find the select by testid if available, or just name
        await page.select_option("select[name='contribution_type']", "found")
        await page.wait_for_timeout(500)

        await page.screenshot(path="/home/jules/verification/public_detail_contribution_v2.png")
        print("Captured public detail contribution v2")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify())

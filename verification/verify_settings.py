from playwright.sync_api import sync_playwright, expect
import os

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 800})
    page = context.new_page()

    # 1. Login
    print("Logging in...")
    page.goto("http://localhost:5000/admin/login")
    page.fill("input[name='username']", "admin")
    page.fill("input[name='password']", "admin")
    page.click("button[type='submit']")
    # Wait for navigation
    page.wait_for_url("http://localhost:5000/admin/")
    print("Logged in.")

    # 2. Go to Settings
    print("Going to settings...")
    page.goto("http://localhost:5000/admin/settings")

    # 3. Take screenshot of initial state
    page.screenshot(path="/home/jules/verification/initial_settings.png")

    # 4. Change Settings
    print("Changing settings...")
    # Change Site Name
    page.fill("input[name='setting_site_name']", "DISPARUS TEST SITE")

    # Uncheck "Enable rate limiting" (it defaults to checked)
    checkbox = page.locator("input[name='setting_enable_rate_limiting']")
    if checkbox.is_checked():
        # Force uncheck because input is sr-only
        checkbox.uncheck(force=True)

    # Change Select "Default Search Filter"
    page.select_option("select[name='setting_default_search_filter']", "person")

    # 5. Save
    print("Saving...")
    page.click("button[type='submit']")
    page.wait_for_load_state('networkidle')

    # 6. Verify Persistence (it redirects to same page)
    # Reload to be sure
    print("Reloading...")
    page.reload()
    page.wait_for_load_state('networkidle')

    # Check Site Name
    print("Verifying values...")
    expect(page.locator("input[name='setting_site_name']")).to_have_value("DISPARUS TEST SITE")

    # Check Checkbox (should be unchecked)
    expect(page.locator("input[name='setting_enable_rate_limiting']")).not_to_be_checked()

    # Check Select (should be 'person')
    expect(page.locator("select[name='setting_default_search_filter']")).to_have_value("person")

    print("Success. Taking screenshot.")
    page.screenshot(path="/home/jules/verification/verification.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)

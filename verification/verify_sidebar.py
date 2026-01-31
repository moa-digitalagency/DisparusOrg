import re
import sys
from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 800})
    page = context.new_page()

    try:
        # Login
        print("Navigating to login...")
        page.goto("http://localhost:5000/admin/login")

        # Check if we are already logged in (redirected to dashboard)
        if "/admin/login" in page.url:
            print("Filling login form...")
            page.fill("input[name='username']", "admin")
            page.fill("input[name='password']", "secret")
            page.click("button[type='submit']")
            print("Submitted login form.")

        # Wait for dashboard
        print("Waiting for dashboard...")
        page.wait_for_url("http://localhost:5000/admin/", timeout=10000)
        print("Dashboard loaded.")

        # Verify classes
        print("Verifying classes...")
        # Select desktop sidebar explicitly
        sidebar = page.locator("aside.w-64:not(#mobile-sidebar-content)")

        try:
            expect(sidebar).to_have_class(re.compile(r"md:flex"))
            print("PASS: Sidebar has md:flex")
        except Exception as e:
            print(f"FAIL: Sidebar missing md:flex. Classes: {sidebar.get_attribute('class')}")

        try:
            expect(sidebar).to_have_class(re.compile(r"md:flex-col"))
            print("PASS: Sidebar has md:flex-col")
        except Exception as e:
             print(f"FAIL: Sidebar missing md:flex-col. Classes: {sidebar.get_attribute('class')}")

        menu_container = sidebar.locator("div.flex-1.overflow-y-auto")
        if menu_container.count() > 0:
             print("PASS: Menu container found with flex-1 and overflow-y-auto")
        else:
             print("FAIL: Menu container NOT found")

        # Take screenshot
        print("Taking screenshot...")
        page.screenshot(path="/home/jules/verification/verification.png")
        print("Screenshot saved.")

    except Exception as e:
        print(f"Error: {e}")
        page.screenshot(path="/home/jules/verification/error.png")
        sys.exit(1)
    finally:
        browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)

from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Login
        print("Navigating to login...")
        page.goto("http://localhost:3000/admin/login")
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin")
        page.click('button[type="submit"]')
        page.wait_for_url("**/admin/")
        print("Logged in.")

        # Go to settings
        print("Navigating to settings...")
        page.goto("http://localhost:3000/admin/settings")
        # Wait for content to load
        page.wait_for_selector("text=Parametres generaux")

        # Capture
        output_path = "/home/jules/verification/admin_settings_v4.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        page.screenshot(path=output_path, full_page=True)
        print(f"Screenshot saved to {output_path}")

        browser.close()

if __name__ == "__main__":
    run()

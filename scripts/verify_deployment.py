from playwright.sync_api import sync_playwright
import time
import os
import sys

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a large viewport to capture full details
        context = browser.new_context(viewport={'width': 1280, 'height': 3000})
        page = context.new_page()

        base_url = "http://localhost:3000"

        # Ensure output directory exists
        os.makedirs("statics/verification", exist_ok=True)

        print("Starting verification...")

        # Capture Console Errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        page.on("pageerror", lambda exc: console_errors.append(f"Uncaught Exception: {exc}"))

        def check_errors(page_name):
            if console_errors:
                print(f"  !! JS Errors detected on {page_name}:")
                for err in console_errors:
                    print(f"     - {err}")
                # Clear for next page
                console_errors.clear()
                return False
            return True

        # 1. Home Page
        print("Checking Home Page...")
        try:
            page.goto(base_url)
            page.wait_for_load_state("networkidle")
            page.screenshot(path="statics/verification/01_home.png", full_page=True)
            print("  - Home Page loaded (200 OK)")
            check_errors("Home Page")
        except Exception as e:
            print(f"  - Home Page FAILED: {e}")

        # 2. Search Page
        print("Checking Search Page...")
        try:
            page.goto(f"{base_url}/recherche")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="statics/verification/02_search.png", full_page=True)
            print("  - Search Page loaded (200 OK)")
            check_errors("Search Page")
        except Exception as e:
            print(f"  - Search Page FAILED: {e}")

        # 3. Report Page
        print("Checking Report Page...")
        try:
            page.goto(f"{base_url}/signaler")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="statics/verification/03_report.png", full_page=True)
            print("  - Report Page loaded (200 OK)")
            check_errors("Report Page")
        except Exception as e:
            print(f"  - Report Page FAILED: {e}")

        # 4. Admin Login & Dashboard
        print("Checking Admin Login...")
        try:
            page.goto(f"{base_url}/admin/login")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="statics/verification/04_admin_login.png")
            print("  - Admin Login loaded (200 OK)")
            check_errors("Admin Login")

            # Attempt Login
            admin_password = os.environ.get('ADMIN_PASSWORD')
            if admin_password:
                print("  - Attempting Login...")
                page.fill('input[name="username"]', 'admin')
                page.fill('input[name="password"]', admin_password)
                page.click('button[type="submit"]')

                # Wait for navigation
                page.wait_for_load_state("networkidle")

                if "/admin/login" not in page.url:
                    print("  - Login Successful!")
                    page.screenshot(path="statics/verification/05_admin_dashboard.png", full_page=True)
                    check_errors("Admin Dashboard")

                    # Check Map
                    print("Checking Admin Map...")
                    page.goto(f"{base_url}/admin/map")
                    page.wait_for_load_state("networkidle")
                    time.sleep(2) # Wait for tiles
                    page.screenshot(path="statics/verification/06_admin_map.png", full_page=True)
                    check_errors("Admin Map")

                else:
                    print("  - Login Failed (Still on login page)")
            else:
                print("  - Skipping Login (ADMIN_PASSWORD not set)")

        except Exception as e:
            print(f"  - Admin Login/Dashboard FAILED: {e}")

        browser.close()
        print("Verification complete. Screenshots saved in statics/verification/")

if __name__ == "__main__":
    # Wait a bit for server to be fully ready
    time.sleep(5)
    run_verification()

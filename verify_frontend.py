from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Test Report Page (Tabs)
        print("Testing Report Page...")
        try:
            page.goto("http://localhost:3000/signaler", timeout=10000)
            time.sleep(2) # Wait for load
            page.screenshot(path="verification_report_person.png")

            # Click Animal Tab
            page.click("#tab-animal")
            time.sleep(1)
            page.screenshot(path="verification_report_animal.png")
        except Exception as e:
            print(f"Report page failed: {e}")

        # Test Home Page (Filters)
        print("Testing Home Page...")
        try:
            page.goto("http://localhost:3000/", timeout=10000)
            time.sleep(2)
            page.screenshot(path="verification_home.png")
        except Exception as e:
            print(f"Home page failed: {e}")

        # Test Search Page
        print("Testing Search Page...")
        try:
            page.goto("http://localhost:3000/recherche", timeout=10000)
            time.sleep(2)
            page.screenshot(path="verification_search.png")
        except Exception as e:
            print(f"Search page failed: {e}")

        browser.close()

if __name__ == "__main__":
    run()

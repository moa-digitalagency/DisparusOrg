
from playwright.sync_api import sync_playwright
import time

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Report Form - Animal Tab
        print("Navigating to /signaler...")
        page.goto("http://localhost:5000/signaler")
        page.wait_for_selector("#tab-animal")

        # Click Animal Tab
        print("Clicking Animal Tab...")
        page.click("#tab-animal")
        time.sleep(1) # Wait for transition

        # Check for Animal Fields
        print("Checking Animal Fields...")
        if page.is_visible("#block-animal-type") and page.is_visible("#block-breed"):
            print("SUCCESS: Animal fields visible")
        else:
            print("FAILURE: Animal fields not visible")

        page.screenshot(path="verification_report_animal.png")

        # Check Person Tab switch back
        print("Clicking Person Tab...")
        page.click("#tab-person")
        time.sleep(1)
        if page.is_visible("#block-person-type") and not page.is_visible("#block-animal-type"):
             print("SUCCESS: Person fields visible, Animal hidden")
        else:
             print("FAILURE: Switching back failed")

        page.screenshot(path="verification_report_person.png")

        # 2. Homepage Filters
        print("Navigating to Homepage...")
        page.goto("http://localhost:5000/")
        page.wait_for_selector("#type-filter")

        # Check options
        options = page.eval_on_selector("#type-filter", "el => Array.from(el.options).map(o => o.value)")
        if 'person' in options and 'animal' in options:
            print(f"SUCCESS: Filters present: {options}")
        else:
            print(f"FAILURE: Filters missing: {options}")

        page.screenshot(path="verification_home.png")

        # 3. Search Page
        print("Navigating to Search...")
        page.goto("http://localhost:5000/recherche")
        page.wait_for_selector("select[name='type']")

        page.screenshot(path="verification_search.png")

        browser.close()

if __name__ == "__main__":
    verify_frontend()

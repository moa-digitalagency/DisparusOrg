from playwright.sync_api import sync_playwright, expect
import os

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # 1. Verify Report Page (Mic Button)
        try:
            print("Navigating to report page...")
            response = page.goto("http://127.0.0.1:5000/signaler")
            print(f"Status: {response.status}")

            content = page.content()
            if "btn-speech-toggle" in content:
                print("Button found in HTML source")
            else:
                print("Button NOT found in HTML source")

            if page.locator("#btn-speech-toggle").count() > 0:
                print("Microphone button exists in DOM.")

                if not page.locator("#btn-speech-toggle").is_visible():
                    print("Microphone button is hidden (likely no Speech API). Forcing visible for screenshot.")
                    page.evaluate("document.getElementById('btn-speech-toggle').style.display = 'block'")
                else:
                    print("Microphone button is visible.")
            else:
                print("Microphone button NOT found in DOM!")

            os.makedirs("/home/jules/verification", exist_ok=True)
            page.screenshot(path="/home/jules/verification/report_page.png")
        except Exception as e:
            print(f"Error verifying report page: {e}")

        # 2. Verify Detail Page (Share Button)
        try:
            print("Navigating to detail page...")
            page.goto("http://127.0.0.1:5000/disparu/DEMO01")
            page.wait_for_selector("#btn-generate-story", timeout=5000)

            if page.locator("#btn-generate-story").is_visible():
                print("Share Story button found!")
            else:
                print("Share Story button NOT visible!")

            page.screenshot(path="/home/jules/verification/detail_page.png")
        except Exception as e:
            print(f"Error verifying detail page: {e}")

        browser.close()

if __name__ == "__main__":
    verify()

import sys
import os
import threading
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# Add the root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Disparu

# Set up environment variables
os.environ['DATABASE_URL'] = 'sqlite:///test.db'
os.environ['WTF_CSRF_ENABLED'] = 'False'

app = create_app()

def run_server():
    app.run(port=5001)

def setup_data():
    with app.app_context():
        db.create_all()

        # Clear existing data
        Disparu.query.delete()

        # Create 'Found' record (Green overlay)
        found = Disparu(
            public_id='FOUND1',
            first_name='Green',
            last_name='Overlay',
            age=25,
            sex='female',
            person_type='adult',
            country='TestCountry',
            city='TestCity',
            physical_description='Test',
            circumstances='Test',
            disappearance_date=datetime.now(),
            status='found',
            photo_url='/static/img/logo.png' # Use dummy photo
        )

        # Create 'Deceased' record (Gray overlay)
        deceased = Disparu(
            public_id='DEAD01',
            first_name='Gray',
            last_name='Overlay',
            age=50,
            sex='male',
            person_type='adult',
            country='TestCountry',
            city='TestCity',
            physical_description='Test',
            circumstances='Test',
            disappearance_date=datetime.now(),
            status='deceased',
            photo_url='/static/img/logo.png' # Use dummy photo
        )

        # Create 'Missing' record (No overlay / red badge)
        missing = Disparu(
            public_id='MISS01',
            first_name='No',
            last_name='Overlay',
            age=10,
            sex='child',
            person_type='child',
            country='TestCountry',
            city='TestCity',
            physical_description='Test',
            circumstances='Test',
            disappearance_date=datetime.now(),
            status='missing',
            photo_url='/static/img/logo.png'
        )

        db.session.add(found)
        db.session.add(deceased)
        db.session.add(missing)
        db.session.commit()
        print("Test data created.")

def capture_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            print("Navigating to index page...")
            page.goto("http://127.0.0.1:5001/")

            # Wait for cards to load
            page.wait_for_selector(".disparu-card")

            # Take screenshot of the cards grid
            # We target the grid container
            # Use a more specific selector or just take full page if simple selector fails
            # The error showed multiple matches for .grid.grid-cols-1
            # We want the one containing the cards

            # Use the first match which seemed to be the cards container in the error log
            # Or better, target by ID or structure if possible.
            # In index.html: <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

            grid = page.locator(".grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-3").first

            screenshot_path = "tests/verification/overlays_screenshot.png"
            grid.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"Error during screenshot: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    # Start server in background thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Give server time to start
    time.sleep(2)

    # Setup data
    setup_data()

    # Run playwright
    capture_screenshot()

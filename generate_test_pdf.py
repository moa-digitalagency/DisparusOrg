import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

# Import real i18n
from utils.i18n import get_translation, load_translations

# Load translations first
load_translations()

# Define t function to use real translations
def t(key, **kwargs):
    text = get_translation(key, 'fr') # Use French for the test
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            return text
    return text

# Mock Disparu Class with missing data
class MockDisparu:
    def __init__(self):
        self.public_id = "TEST01"
        self.first_name = "John"
        self.last_name = "Doe"
        # Edge cases: None or missing fields
        self.age = None
        self.sex = None
        self.person_type = "adult"
        self.country = None
        self.city = None
        self.physical_description = None
        self.clothing = None
        self.circumstances = None
        self.photo_url = "http://invalid-url/broken.jpg"
        self.disappearance_date = "invalid-date" # Test the invalid-date logic
        self.contacts = None # or {} or []
        # Missing attributes entirely (simulated by not setting them here)
        # getattr will handle this in the fixed code

try:
    from utils.pdf_gen import generate_missing_person_pdf

    print("Generating PDF with missing data and REAL translations...")
    disparu = MockDisparu()

    # Generate PDF
    pdf_buffer = generate_missing_person_pdf(disparu, t=t, locale='fr')

    if pdf_buffer:
        output_filename = "test_missing_data.pdf"
        with open(output_filename, "wb") as f:
            f.write(pdf_buffer.getvalue())
        print(f"Success! PDF generated: {output_filename}")
        print("Expected output:")
        print(f"- pdf.missing_person -> {t('pdf.missing_person')}")
        print(f"- common.invalid_date -> {t('common.invalid_date')}")
    else:
        print("Failed: PDF buffer is None.")

except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()

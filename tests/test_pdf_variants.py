import os
import sys
import unittest
from unittest.mock import MagicMock
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock get_translation for tests
import utils.i18n as i18n
# Just ensure it doesn't fail if files are missing in test env
# The real get_translation function handles missing files gracefully

from utils.pdf_gen import generate_missing_person_pdf

class TestPDFVariants(unittest.TestCase):
    def setUp(self):
        self.output_dir = 'test_output'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def create_mock_disparu(self, status='missing', person_type='adult', sex='male'):
        d = MagicMock()
        d.public_id = f"TEST-{status}-{person_type}-{sex}"
        d.first_name = "Jean"
        d.last_name = "Dupont"
        d.status = status
        d.person_type = person_type
        d.sex = sex
        d.age = 30
        d.city = "Paris"
        d.country = "France"
        d.disappearance_date = datetime.now()
        d.updated_at = datetime.now()
        d.physical_description = "Description physique test."
        d.clothing = "Vêtements test."
        d.circumstances = "Circonstances test."
        d.contacts = [{"name": "Contact Test", "phone": "0123456789"}]
        d.photo_url = None # Test without photo for simplicity
        return d

    def generate_pdf(self, d):
        pdf_buffer = generate_missing_person_pdf(d)
        if pdf_buffer:
            filepath = os.path.join(self.output_dir, f"{d.public_id}.pdf")
            with open(filepath, "wb") as f:
                f.write(pdf_buffer.read())
            print(f"Generated {filepath}")
        else:
            print(f"Failed to generate {d.public_id}.pdf")

    def test_all_variants(self):
        # Statuses: missing, found, deceased, injured
        # Types: adult, child, teenager, elderly, animal
        # Sex: male, female

        scenarios = [
            ('missing', 'adult', 'male'),
            ('found', 'adult', 'female'),
            ('deceased', 'adult', 'male'),
            ('injured', 'adult', 'female'),

            ('missing', 'child', 'female'),
            ('missing', 'teenager', 'male'),
            ('missing', 'elderly', 'female'),

            ('missing', 'animal', 'male'),
            ('found', 'animal', 'female'),
            ('deceased', 'animal', 'male'),
            ('injured', 'animal', 'female'),
        ]

        for status, p_type, sex in scenarios:
            d = self.create_mock_disparu(status=status, person_type=p_type, sex=sex)
            self.generate_pdf(d)

if __name__ == '__main__':
    unittest.main()

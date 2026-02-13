import os
import sys
import unittest
from unittest.mock import MagicMock
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

    def test_generate_missing_adult(self):
        d = self.create_mock_disparu(status='missing', person_type='adult', sex='male')
        pdf_buffer = generate_missing_person_pdf(d)
        self.assertIsNotNone(pdf_buffer, "PDF buffer should not be None")
        with open(os.path.join(self.output_dir, f"{d.public_id}.pdf"), "wb") as f:
            f.write(pdf_buffer.read())
        print(f"Generated {d.public_id}.pdf")

    def test_generate_found_adult(self):
        d = self.create_mock_disparu(status='found', person_type='adult', sex='female')
        pdf_buffer = generate_missing_person_pdf(d)
        self.assertIsNotNone(pdf_buffer, "PDF buffer should not be None")
        with open(os.path.join(self.output_dir, f"{d.public_id}.pdf"), "wb") as f:
            f.write(pdf_buffer.read())
        print(f"Generated {d.public_id}.pdf")

    def test_generate_deceased_adult(self):
        d = self.create_mock_disparu(status='deceased', person_type='adult', sex='male')
        pdf_buffer = generate_missing_person_pdf(d)
        self.assertIsNotNone(pdf_buffer, "PDF buffer should not be None")
        with open(os.path.join(self.output_dir, f"{d.public_id}.pdf"), "wb") as f:
            f.write(pdf_buffer.read())
        print(f"Generated {d.public_id}.pdf")

    def test_generate_missing_animal(self):
        d = self.create_mock_disparu(status='missing', person_type='animal', sex='male')
        d.first_name = "Rex"
        pdf_buffer = generate_missing_person_pdf(d)
        self.assertIsNotNone(pdf_buffer, "PDF buffer should not be None")
        with open(os.path.join(self.output_dir, f"{d.public_id}.pdf"), "wb") as f:
            f.write(pdf_buffer.read())
        print(f"Generated {d.public_id}.pdf")

    def test_generate_found_animal(self):
        d = self.create_mock_disparu(status='found', person_type='animal', sex='female')
        d.first_name = "Luna"
        pdf_buffer = generate_missing_person_pdf(d)
        self.assertIsNotNone(pdf_buffer, "PDF buffer should not be None")
        with open(os.path.join(self.output_dir, f"{d.public_id}.pdf"), "wb") as f:
            f.write(pdf_buffer.read())
        print(f"Generated {d.public_id}.pdf")

if __name__ == '__main__':
    unittest.main()

import os
import unittest
# Set DATABASE_URL before importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import create_app, db
from models import Disparu
from datetime import datetime

class TestPDFDownload(unittest.TestCase):
    def setUp(self):
        # Use in-memory DB for speed
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['PROPAGATE_EXCEPTIONS'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Add sample data
        d1 = Disparu(
            public_id='TEST01',
            first_name='John',
            last_name='Doe',
            person_type='adult',
            status='missing',
            country='Gabon',
            city='Libreville',
            disappearance_date=datetime.now(),
            physical_description='Desc',
            circumstances='Circumstances',
            age=30,
            sex='male',
        )
        # Add a record with minimal data but valid schema
        d2 = Disparu(
            public_id='TEST02',
            first_name='Jane',
            last_name='Doe',
            person_type='adult',
            status='missing',
            country='France',
            city='Paris',
            disappearance_date=datetime.now(),
            physical_description='Desc',
            circumstances='Circumstances',
            age=-1,     # Unknown age convention
            sex='female',
            contacts=None # JSON field can be None
        )
        db.session.add_all([d1, d2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_pdf_download_success(self):
        response = self.client.get('/disparu/TEST01/pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')

    def test_pdf_download_robustness(self):
        # Should generate PDF even with missing optional fields
        response = self.client.get('/disparu/TEST02/pdf')
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}")
        self.assertEqual(response.mimetype, 'application/pdf')

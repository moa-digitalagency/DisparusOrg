import unittest
import os
from app import create_app, db
from models import Disparu, Download
from datetime import datetime

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

class TestShareImage(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

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
            contacts=None
        )
        db.session.add(d1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_share_image_download(self):
        # Calls the async route via sync test client
        response = self.client.get('/disparu/TEST01/share-image')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/png')

        download = Download.query.filter_by(disparu_public_id='TEST01').first()
        self.assertIsNotNone(download)

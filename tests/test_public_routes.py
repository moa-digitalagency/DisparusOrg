import os
# Set DATABASE_URL before importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import unittest
from app import create_app
from models import db, Disparu, Contribution
from datetime import datetime

class TestPublicRoutes(unittest.TestCase):
    def setUp(self):
        # Use in-memory DB for speed
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
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
        d2 = Disparu(
            public_id='TEST02',
            first_name='Jane',
            last_name='Doe',
            person_type='adult',
            status='found',
            country='France',
            city='Paris',
            disappearance_date=datetime.now(),
            physical_description='Desc',
            circumstances='Circumstances',
            age=30,
            sex='female',
        )
        db.session.add_all([d1, d2])

        c1 = Contribution(
            disparu_id=1,
            contribution_type='sighting',
            details='Seen here'
        )
        db.session.add(c1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_index_stats(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # Verify basic presence of stats elements
        self.assertIn('data-testid="stat-total"', content)
        self.assertIn('data-testid="stat-found"', content)
        self.assertIn('data-testid="stat-contributions"', content)

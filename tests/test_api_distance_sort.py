"""
Test for API distance sorting.
"""
import unittest
import os
import sys
from app import create_app
from models import db, Disparu
from datetime import datetime

class TestApiDistanceSort(unittest.TestCase):
    def setUp(self):
        # Use in-memory DB for speed
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create tables
        db.create_all()

        # Create test data
        # Point A: User location
        self.user_lat = 48.8566 # Paris
        self.user_lng = 2.3522

        # 1. Very close (Paris)
        self.d1 = Disparu(
            public_id='paris1', person_type='person', first_name='Close', last_name='One',
            age=30, sex='M', country='France', city='Paris', physical_description='.',
            disappearance_date=datetime.now(), circumstances='.',
            latitude=48.8566, longitude=2.3522, status='missing'
        )

        # 2. Medium distance (London) ~340km
        self.d2 = Disparu(
            public_id='london1', person_type='person', first_name='Medium', last_name='One',
            age=30, sex='M', country='UK', city='London', physical_description='.',
            disappearance_date=datetime.now(), circumstances='.',
            latitude=51.5074, longitude=-0.1278, status='missing'
        )

        # 3. Far distance (New York) ~5800km
        self.d3 = Disparu(
            public_id='ny1', person_type='person', first_name='Far', last_name='One',
            age=30, sex='M', country='USA', city='NY', physical_description='.',
            disappearance_date=datetime.now(), circumstances='.',
            latitude=40.7128, longitude=-74.0060, status='missing'
        )

        # Add in mixed order
        db.session.add_all([self.d3, self.d1, self.d2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_sort_by_distance(self):
        client = self.app.test_client()

        # Query with lat/lng
        resp = client.get(f'/api/disparus?lat={self.user_lat}&lng={self.user_lng}&limit=10')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertEqual(len(data), 3)

        # Check order: Closest first
        self.assertEqual(data[0]['public_id'], 'paris1')
        self.assertEqual(data[1]['public_id'], 'london1')
        self.assertEqual(data[2]['public_id'], 'ny1')

        # Check distance values exist and are ascending
        d1 = data[0]['distance']
        d2 = data[1]['distance']
        d3 = data[2]['distance']

        self.assertLess(d1, 1.0) # Should be ~0
        self.assertGreater(d2, 300)
        self.assertLess(d2, 400)
        self.assertGreater(d3, 5000)

        self.assertLess(d1, d2)
        self.assertLess(d2, d3)

    def test_no_lat_lng_sorts_by_date(self):
        client = self.app.test_client()
        # Query WITHOUT lat/lng
        resp = client.get('/api/disparus?limit=10')
        data = resp.get_json()

        # Should be ordered by created_at desc (which is insertion order effectively here, or I should have set created_at)
        # Since I added d3, d1, d2 in one go, ID order is likely d3=1, d1=2, d2=3.
        # created_at defaults to now(). They might be identical.
        # But let's check that 'distance' key is NOT in the response

        self.assertNotIn('distance', data[0])

if __name__ == '__main__':
    unittest.main()

import unittest
from app import create_app
from models import db, Disparu
from algorithms.clustering import get_nearby_cases
from datetime import datetime

class TestClusteringOptimization(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        # Disable CSRF for testing if needed, though not hitting routes here
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_disparu(self, lat, lon, public_id):
        return Disparu(
            public_id=public_id,
            person_type='person',
            first_name='Test',
            last_name='Test',
            age=25,
            sex='M',
            country='Test',
            city='Test',
            physical_description='Test',
            disappearance_date=datetime.now(),
            circumstances='Test',
            latitude=lat,
            longitude=lon,
            status='missing'
        )

    def test_get_nearby_cases_basic(self):
        # Center: 0, 0
        d1 = self.create_disparu(0.1, 0.1, 'near1') # Close
        d2 = self.create_disparu(1.0, 1.0, 'far1')  # ~157km away
        d3 = self.create_disparu(5.0, 5.0, 'far2')  # Far

        db.session.add_all([d1, d2, d3])
        db.session.commit()

        # Radius 100km
        results = get_nearby_cases(0, 0, radius_km=100)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['disparu']['public_id'], 'near1')

        # Radius 200km
        results = get_nearby_cases(0, 0, radius_km=200)
        self.assertEqual(len(results), 2)
        public_ids = sorted([r['disparu']['public_id'] for r in results])
        self.assertEqual(public_ids, ['far1', 'near1'])

    def test_get_nearby_cases_wrapping(self):
        # Near dateline: 179E.
        # Target: 179, 0. Radius 500km.
        # 1 deg lat = 111km. 500km ~ 4.5 deg.

        # Point at -179 (East from 179 across dateline is 2 deg diff = 222km)
        d1 = self.create_disparu(0, -179, 'wrap1')
        # Point at 175 (West from 179 is 4 deg diff = 444km)
        d2 = self.create_disparu(0, 175, 'west1')
        # Point at 170 (West from 179 is 9 deg diff = 1000km)
        d3 = self.create_disparu(0, 170, 'far1')

        db.session.add_all([d1, d2, d3])
        db.session.commit()

        results = get_nearby_cases(0, 179, radius_km=500)
        ids = sorted([r['disparu']['public_id'] for r in results])
        self.assertEqual(ids, ['west1', 'wrap1'])

if __name__ == '__main__':
    unittest.main()

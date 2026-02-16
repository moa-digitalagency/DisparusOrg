import unittest
from app import create_app
from models import db, Disparu
from datetime import datetime

class TestApiGeoFallback(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_fallback_logic(self):
        # Create 1 "near" record (within 5 degrees)
        d_near = Disparu(
            public_id='near1', person_type='person', first_name='Near', last_name='One',
            age=30, sex='M', country='France', city='Paris', physical_description='.',
            disappearance_date=datetime.now(), circumstances='.',
            latitude=48.8566, longitude=2.3522, status='missing'
        )

        # Create 2 "far" records (outside 5 degrees)
        d_far1 = Disparu(
            public_id='far1', person_type='person', first_name='Far', last_name='One',
            age=30, sex='M', country='USA', city='NY', physical_description='.',
            disappearance_date=datetime.now(), circumstances='.',
            latitude=40.7128, longitude=-74.0060, status='missing'
        ) # Dist ~ 5800 km

        d_far2 = Disparu(
            public_id='far2', person_type='person', first_name='Far', last_name='Two',
            age=30, sex='M', country='Australia', city='Sydney', physical_description='.',
            disappearance_date=datetime.now(), circumstances='.',
            latitude=-33.8688, longitude=151.2093, status='missing'
        ) # Dist ~ 17000 km

        db.session.add_all([d_near, d_far1, d_far2])
        db.session.commit()

        client = self.app.test_client()

        # Request limit=2.
        # Initial box (5 deg) finds 'near1' (1 record).
        # 1 < 2, so fallback triggers.
        # Fallback should find all 3, sort by distance, and return top 2.
        # Top 2 should be 'near1' and 'far1'.

        resp = client.get('/api/disparus/nearby?lat=48.8566&lng=2.3522&limit=2&status=missing')
        data = resp.get_json()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['public_id'], 'near1')
        self.assertEqual(data[1]['public_id'], 'far1')

        # Verify distances are roughly correct
        self.assertLess(data[0]['distance'], 10)
        self.assertGreater(data[1]['distance'], 5000)

if __name__ == '__main__':
    unittest.main()

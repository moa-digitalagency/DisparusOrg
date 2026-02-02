import unittest
from app import create_app
from models import db, Disparu
from algorithms.clustering import find_hotspots
from datetime import datetime

class TestHotspots(unittest.TestCase):
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

    def test_find_hotspots_basic(self):
        # Create a cluster of 3 points near 0,0
        d1 = self.create_disparu(0.1, 0.1, 'p1')
        d2 = self.create_disparu(0.12, 0.12, 'p2')
        d3 = self.create_disparu(0.08, 0.08, 'p3')

        # Create isolated points
        d4 = self.create_disparu(10, 10, 'p4')
        d5 = self.create_disparu(-10, -10, 'p5')

        db.session.add_all([d1, d2, d3, d4, d5])
        db.session.commit()

        # Search with min_cases=3, radius=50km
        hotspots = find_hotspots(min_cases=3, radius_km=50)

        self.assertEqual(len(hotspots), 1)
        self.assertEqual(hotspots[0]['count'], 3)
        self.assertCountEqual(hotspots[0]['disparus'], ['p1', 'p2', 'p3'])

    def test_find_hotspots_wrapping(self):
        # Create points across the date line
        # 0 lat, 179.9 lon and -179.9 lon. Distance ~ 22km.
        d1 = self.create_disparu(0, 179.9, 'east')
        d2 = self.create_disparu(0, -179.9, 'west')
        d3 = self.create_disparu(0, 180, 'line')

        db.session.add_all([d1, d2, d3])
        db.session.commit()

        hotspots = find_hotspots(min_cases=3, radius_km=50)

        self.assertEqual(len(hotspots), 1)
        self.assertEqual(hotspots[0]['count'], 3)
        self.assertCountEqual(hotspots[0]['disparus'], ['east', 'west', 'line'])

    def test_find_hotspots_grid_boundary(self):
        # Test points that might fall into different grid cells but are close
        # Grid size is 0.5.
        # Point at 0.49, 0.49.
        # Point at 0.51, 0.51.
        # They are in different cells: (0,0) and (1,1).
        # Distance is small (sqrt(0.02^2 + 0.02^2) deg ~ 0.028 deg ~ 3km).

        d1 = self.create_disparu(0.49, 0.49, 'p1')
        d2 = self.create_disparu(0.51, 0.51, 'p2')
        d3 = self.create_disparu(0.50, 0.50, 'p3')

        db.session.add_all([d1, d2, d3])
        db.session.commit()

        hotspots = find_hotspots(min_cases=3, radius_km=50)

        self.assertEqual(len(hotspots), 1)
        self.assertEqual(hotspots[0]['count'], 3)

if __name__ == '__main__':
    unittest.main()

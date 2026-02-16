"""
Benchmark script for API distance calculation performance.
"""
import time
import os
import sys
import unittest
import random
from datetime import datetime

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set DATABASE_URL before importing app or calling create_app
os.environ['DATABASE_URL'] = 'sqlite:///benchmark.db'

from app import create_app
from models import db, Disparu

class BenchmarkDistance(unittest.TestCase):
    def setUp(self):
        self.db_path = 'benchmark.db'

        # Ensure clean state
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create tables
        db.create_all()

        # Seed Data
        print("Seeding 2000 records...")
        disparus = []
        for i in range(2000):
            # Random coordinates
            lat = random.uniform(-90, 90)
            lng = random.uniform(-180, 180)

            d = Disparu(
                public_id=f'bench{i}',
                person_type='person',
                first_name=f'Name{i}',
                last_name=f'Last{i}',
                age=random.randint(1, 90),
                sex='M',
                country='Test',
                city='TestCity',
                physical_description='.',
                disappearance_date=datetime.now(),
                circumstances='.',
                latitude=lat,
                longitude=lng,
                status='missing'
            )
            disparus.append(d)

        db.session.add_all(disparus)
        db.session.commit()
        print("Seeding complete.")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_benchmark(self):
        client = self.app.test_client()

        print("\nRunning benchmark (limit=2000)...")
        start_time = time.time()

        # Request with non-zero lat/lng to trigger distance calculation
        resp = client.get('/api/disparus?lat=48.8566&lng=2.3522&limit=2000')

        end_time = time.time()
        duration = end_time - start_time

        print(f"Request took: {duration:.4f} seconds")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(len(data), 2000)

        if data:
            # Ensure distance key is present
            if 'distance' in data[0]:
                print(f"First result distance: {data[0].get('distance')}")
            else:
                print("Distance key missing!")

if __name__ == '__main__':
    unittest.main()

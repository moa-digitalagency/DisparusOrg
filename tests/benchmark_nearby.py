import os
import time
import unittest
from app import create_app
from models import db, Disparu
from datetime import datetime

class BenchmarkNearby(unittest.TestCase):
    def setUp(self):
        self.db_path = 'benchmark.db'
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Add many disparus inside the bounding box
        disparus = []
        for i in range(1000):
            d = Disparu(
                public_id=f'TEST{i:04d}',
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
                latitude=10.0 + (i / 1000.0),
                longitude=10.0 + (i / 1000.0)
            )
            disparus.append(d)
        db.session.add_all(disparus)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_benchmark_nearby(self):
        iterations = 50
        start_time = time.time()
        for _ in range(iterations):
            response = self.client.get('/api/disparus/nearby?lat=48.8566&lng=2.3522')
            self.assertEqual(response.status_code, 200)
        end_time = time.time()

        duration = end_time - start_time
        print(f"\nNearby benchmark duration for {iterations} requests: {duration:.4f}s")
        print(f"Average time per request: {duration/iterations:.4f}s")

if __name__ == '__main__':
    unittest.main()

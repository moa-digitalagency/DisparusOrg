import os
import time
import unittest
from app import create_app
from models import db, Disparu
from datetime import datetime

class BenchmarkDetailView(unittest.TestCase):
    def setUp(self):
        # Use a real file for SQLite to simulate disk I/O more realistically than :memory:
        # although in production it's likely Postgres.
        # Still, the goal is to see relative improvement.
        self.db_path = 'benchmark.db'
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Add a sample disparu
        self.disparu = Disparu(
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
        db.session.add(self.disparu)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_benchmark_detail_view(self):
        iterations = 100
        start_time = time.time()
        for _ in range(iterations):
            response = self.client.get('/disparu/TEST01')
            self.assertEqual(response.status_code, 200)
        end_time = time.time()

        duration = end_time - start_time
        print(f"\nBaseline duration for {iterations} requests: {duration:.4f}s")
        print(f"Average time per request: {duration/iterations:.4f}s")

if __name__ == '__main__':
    unittest.main()

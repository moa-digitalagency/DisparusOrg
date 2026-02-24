import os
import time
import unittest
from app import create_app
from models import db, Disparu, Contribution
from datetime import datetime
import random

class BenchmarkStats(unittest.TestCase):
    def setUp(self):
        # Use :memory: to avoid file locking issues and ensure clean state
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Add sample disparus and contributions
        disparus = []
        for i in range(500):
            d = Disparu(
                public_id=f'TEST{i:03d}',
                first_name=f'Name{i}',
                last_name=f'Last{i}',
                person_type=random.choice(['adult', 'child', 'elderly', 'animal']),
                status=random.choice(['missing', 'found', 'found_alive', 'deceased']),
                country=random.choice(['Gabon', 'Congo', 'France']),
                city='City',
                disappearance_date=datetime.now(),
                physical_description='Desc',
                circumstances='Circumstances',
                age=random.randint(1, 90),
                sex=random.choice(['male', 'female']),
            )
            disparus.append(d)

        db.session.add_all(disparus)
        db.session.commit()

        # Add contributions
        contributions = []
        for i in range(200):
            c = Contribution(
                disparu_id=random.choice(disparus).id,
                contribution_type='sighting',
                details=f'Details {i}',
                contributor_name=f'Contributor{i}',
                content=f'Content {i}',
                is_approved=True
            )
            contributions.append(c)

        db.session.add_all(contributions)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_benchmark_stats(self):
        # Warmup
        self.client.get('/api/stats')

        iterations = 1000
        start_time = time.time()
        for _ in range(iterations):
            response = self.client.get('/api/stats')
            self.assertEqual(response.status_code, 200)
        end_time = time.time()

        duration = end_time - start_time
        print(f"\nBaseline duration for {iterations} requests: {duration:.4f}s")
        print(f"Average time per request: {duration/iterations:.6f}s")

if __name__ == '__main__':
    unittest.main()
